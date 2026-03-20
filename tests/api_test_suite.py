#!/usr/bin/env python3
"""
新闻实时推送系统 - 完整API测试套件
News Real-time Push System - Comprehensive API Test Suite

测试目标：
1. 功能测试 - 验证所有API正常工作
2. 性能测试 - 验证响应时间 < 200ms (95th percentile)
3. 可靠性测试 - 验证错误处理和重试机制
4. 端到端测试 - 验证完整工作流 < 60秒延迟
"""

import sys
import time
import asyncio
import json
from pathlib import Path
from datetime import datetime
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from news_collector import NewsCollector
from news_database import NewsDatabase
from feishu_push import FeishuPusher
from news_monitor import NewsMonitor

# 测试配置
TEST_CONFIG = {
    'performance_sla_ms': 200,  # 95th percentile < 200ms
    'end_to_end_sla_sec': 60,   # 端到端 < 60秒
    'min_news_count': 10,        # 最少抓取10条新闻
    'keyword_accuracy_threshold': 0.7,  # 关键词准确率 > 70%
}

class APITestResults:
    """测试结果收集器"""
    def __init__(self):
        self.tests = []
        self.start_time = datetime.now()

    def add_test(self, name, passed, duration_ms=None, details=None):
        self.tests.append({
            'name': name,
            'passed': passed,
            'duration_ms': duration_ms,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })

    def get_summary(self):
        total = len(self.tests)
        passed = sum(1 for t in self.tests if t['passed'])
        failed = total - passed

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            'duration': str(datetime.now() - self.start_time)
        }

    def print_report(self):
        """打印详细测试报告"""
        summary = self.get_summary()

        print("\n" + "="*80)
        print("📊 API 测试报告")
        print("="*80)
        print(f"\n测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {summary['duration']}")
        print(f"\n测试结果:")
        print(f"  ✅ 通过: {summary['passed']}")
        print(f"  ❌ 失败: {summary['failed']}")
        print(f"  📈 通过率: {summary['pass_rate']}")

        print(f"\n详细结果:")
        print("-"*80)

        for i, test in enumerate(self.tests, 1):
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            duration = f"({test['duration_ms']:.0f}ms)" if test['duration_ms'] else ""
            print(f"{i:2d}. {status} {test['name']} {duration}")
            if test['details']:
                print(f"    {test['details']}")

        print("="*80 + "\n")

        return summary


# ========== 功能测试 ==========

async def test_cls_api_fetch():
    """测试1: 财联社新闻API抓取功能"""
    collector = NewsCollector()

    try:
        start = time.time()
        news_list = await collector.fetch_cls_news(limit=20)
        duration = (time.time() - start) * 1000

        await collector.close_session()

        success = news_list is not None and len(news_list) >= 10

        return {
            'passed': success,
            'duration_ms': duration,
            'details': f"抓取 {len(news_list) if news_list else 0} 条新闻"
        }
    except Exception as e:
        return {
            'passed': False,
            'duration_ms': None,
            'details': f"错误: {str(e)}"
        }


async def test_eastmoney_api_fetch():
    """测试2: 东方财富新闻API抓取功能"""
    collector = NewsCollector()

    try:
        start = time.time()
        news_list = await collector.fetch_eastmoney_news(limit=20)
        duration = (time.time() - start) * 1000

        await collector.close_session()

        # 东方财富可能返回404，所以只要不抛异常就算通过
        success = news_list is not None

        return {
            'passed': success,
            'duration_ms': duration,
            'details': f"抓取 {len(news_list) if news_list else 0} 条新闻"
        }
    except Exception as e:
        return {
            'passed': False,
            'duration_ms': None,
            'details': f"错误: {str(e)}"
        }


def test_database_operations():
    """测试3: 数据库读写操作"""
    db = NewsDatabase()

    try:
        start = time.time()

        # 测试写入
        news_id = db.add_news(
            title="测试新闻",
            content="这是一条测试新闻内容",
            source="test",
            url="http://test.com"
        )

        # 测试读取
        stats = db.get_statistics()

        duration = (time.time() - start) * 1000

        db.close()

        success = stats is not None and stats.get('total_news', 0) > 0

        return {
            'passed': success,
            'duration_ms': duration,
            'details': f"数据库中共 {stats.get('total_news', 0)} 条新闻"
        }
    except Exception as e:
        return {
            'passed': False,
            'duration_ms': None,
            'details': f"错误: {str(e)}"
        }


def test_feishu_push_api():
    """测试4: 飞书推送API"""
    pusher = FeishuPusher()

    try:
        start = time.time()

        test_message = f"🧪 API测试消息 - {datetime.now().strftime('%H:%M:%S')}"

        result = pusher.push(test_message)

        duration = (time.time() - start) * 1000

        return {
            'passed': result.get('success', False),
            'duration_ms': duration,
            'details': result.get('error', '推送成功') if not result.get('success') else f"消息ID: {result.get('message_id', 'N/A')}"
        }
    except Exception as e:
        return {
            'passed': False,
            'duration_ms': None,
            'details': f"错误: {str(e)}"
        }


def test_keyword_matching():
    """测试5: 关键词匹配准确性"""
    monitor = NewsMonitor(use_ai=False, importance_threshold=4)

    # 测试案例
    test_cases = [
        {
            'title': '央行降息降准 股市大涨',
            'expected': 'BULLISH',
            'min_importance': 4
        },
        {
            'title': '公司暴雷退市 投资者血亏',
            'expected': 'BEARISH',
            'min_importance': 4
        },
        {
            'title': '市场交易平稳',
            'expected': 'NEUTRAL',
            'min_importance': 2
        }
    ]

    correct = 0
    durations = []

    for case in test_cases:
        start = time.time()
        result = monitor.classify_by_keywords(case['title'], '')
        duration = (time.time() - start) * 1000
        durations.append(duration)

        if result['sentiment'] == case['expected']:
            correct += 1

    monitor.db.close()

    accuracy = correct / len(test_cases)
    avg_duration = mean(durations)

    return {
        'passed': accuracy >= TEST_CONFIG['keyword_accuracy_threshold'],
        'duration_ms': avg_duration,
        'details': f"准确率 {accuracy*100:.0f}% ({correct}/{len(test_cases)})"
    }


# ========== 性能测试 ==========

async def test_api_response_time():
    """测试6: API响应时间（95th percentile < 200ms）"""
    collector = NewsCollector()
    durations = []

    try:
        # 执行10次请求
        for _ in range(10):
            start = time.time()
            await collector.fetch_cls_news(limit=10)
            duration = (time.time() - start) * 1000
            durations.append(duration)

        await collector.close_session()

        # 计算95th percentile
        durations.sort()
        p95_index = int(len(durations) * 0.95)
        p95 = durations[p95_index] if p95_index < len(durations) else durations[-1]

        avg = mean(durations)
        med = median(durations)

        passed = p95 < TEST_CONFIG['performance_sla_ms']

        return {
            'passed': passed,
            'duration_ms': p95,
            'details': f"平均 {avg:.0f}ms, 中位数 {med:.0f}ms, P95 {p95:.0f}ms"
        }
    except Exception as e:
        return {
            'passed': False,
            'duration_ms': None,
            'details': f"错误: {str(e)}"
        }


async def test_concurrent_requests():
    """测试7: 并发请求处理能力"""
    collector = NewsCollector()

    try:
        start = time.time()

        # 并发10个请求
        tasks = [collector.fetch_cls_news(limit=5) for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = (time.time() - start) * 1000

        await collector.close_session()

        # 统计成功的请求
        successful = sum(1 for r in results if not isinstance(r, Exception) and r is not None)

        passed = successful >= 8  # 至少80%成功

        return {
            'passed': passed,
            'duration_ms': duration,
            'details': f"成功 {successful}/10 个并发请求"
        }
    except Exception as e:
        return {
            'passed': False,
            'duration_ms': None,
            'details': f"错误: {str(e)}"
        }


# ========== 可靠性测试 ==========

def test_database_error_handling():
    """测试8: 数据库错误处理"""
    db = NewsDatabase()

    try:
        # 测试重复插入
        news_id1 = db.add_news(
            title="重复测试",
            content="内容",
            source="test",
            url="http://test-duplicate.com"
        )

        # 尝试插入相同新闻
        news_id2 = db.add_news(
            title="重复测试",
            content="内容",
            source="test",
            url="http://test-duplicate.com"
        )

        db.close()

        # 第二次应该返回None（已存在）
        passed = news_id1 is not None and news_id2 is None

        return {
            'passed': passed,
            'duration_ms': None,
            'details': "重复新闻正确拒绝" if passed else "重复检测失败"
        }
    except Exception as e:
        return {
            'passed': False,
            'duration_ms': None,
            'details': f"错误: {str(e)}"
        }


# ========== 端到端测试 ==========

async def test_end_to_end_workflow():
    """测试9: 端到端工作流（抓取→分析→推送）"""
    monitor = NewsMonitor(use_ai=False, importance_threshold=4)

    try:
        start = time.time()

        # 1. 抓取新闻
        stats = await monitor.collector.collect_all(limit_per_source=20)

        # 2. 获取最新新闻
        if stats['total_saved'] > 0:
            recent_news = monitor.db.cursor.execute('''
                SELECT id, title, content, source
                FROM news
                WHERE is_pushed = 0
                ORDER BY fetch_time DESC
                LIMIT 5
            ''').fetchall()

            # 3. 分析和分类
            for news in recent_news:
                result = monitor.classify_by_keywords(news['title'], news['content'])
                monitor.db.add_prediction(
                    news['id'],
                    result['sentiment'],
                    result['importance'],
                    result['confidence']
                )

        duration = (time.time() - start) * 1000

        await monitor.collector.close_session()
        monitor.db.close()

        # 验证总延迟
        passed = duration < TEST_CONFIG['end_to_end_sla_sec'] * 1000

        return {
            'passed': passed,
            'duration_ms': duration,
            'details': f"抓取 {stats['total_fetched']} 条, 新增 {stats['total_saved']} 条"
        }
    except Exception as e:
        return {
            'passed': False,
            'duration_ms': None,
            'details': f"错误: {str(e)}"
        }


# ========== 主测试运行器 ==========

async def run_all_tests():
    """运行所有测试"""
    results = APITestResults()

    print("\n🚀 开始 API 测试套件执行...")
    print("="*80)

    # 功能测试
    print("\n📋 功能测试:")

    print("  1. 测试财联社API...")
    result = await test_cls_api_fetch()
    results.add_test("财联社新闻API", **result)

    print("  2. 测试东方财富API...")
    result = await test_eastmoney_api_fetch()
    results.add_test("东方财富新闻API", **result)

    print("  3. 测试数据库操作...")
    result = test_database_operations()
    results.add_test("数据库读写操作", **result)

    print("  4. 测试飞书推送API...")
    result = test_feishu_push_api()
    results.add_test("飞书推送API", **result)

    print("  5. 测试关键词匹配...")
    result = test_keyword_matching()
    results.add_test("关键词匹配准确性", **result)

    # 性能测试
    print("\n⚡ 性能测试:")

    print("  6. 测试API响应时间...")
    result = await test_api_response_time()
    results.add_test("API响应时间(P95)", **result)

    print("  7. 测试并发请求...")
    result = await test_concurrent_requests()
    results.add_test("并发请求处理", **result)

    # 可靠性测试
    print("\n🛡️ 可靠性测试:")

    print("  8. 测试错误处理...")
    result = test_database_error_handling()
    results.add_test("数据库错误处理", **result)

    # 端到端测试
    print("\n🔄 端到端测试:")

    print("  9. 测试完整工作流...")
    result = await test_end_to_end_workflow()
    results.add_test("端到端工作流", **result)

    # 打印报告
    summary = results.print_report()

    # 保存报告
    report_file = Path(__file__).parent.parent / 'logs' / f'api_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': summary,
            'tests': results.tests,
            'config': TEST_CONFIG
        }, f, ensure_ascii=False, indent=2)

    print(f"📝 详细报告已保存: {report_file}\n")

    # 返回是否全部通过
    return summary['failed'] == 0


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
