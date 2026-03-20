#!/usr/bin/env python3
"""
实时新闻监控器
Real-time News Monitor

监控新闻源，使用AI模型自动分类，重大消息立即推送到飞书
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from news_database import NewsDatabase
from news_collector import NewsCollector
from feishu_push import FeishuPusher


class NewsMonitor:
    """实时新闻监控器"""

    def __init__(self, use_ai=True, importance_threshold=4):
        """
        初始化

        Args:
            use_ai: 是否使用AI模型（False则使用关键词规则）
            importance_threshold: 重要性阈值（>=此值才推送）
        """
        self.use_ai = use_ai
        self.importance_threshold = importance_threshold

        self.db = NewsDatabase()
        self.collector = NewsCollector()
        self.pusher = FeishuPusher()

        self.sentiment_model = None
        self.importance_model = None
        self.tokenizer = None

        # 关键词规则（AI不可用时使用）
        self.keyword_rules = {
            'BULLISH': {
                'keywords': [
                    '降息', '降准', '刺激', '利好', '并购', '重组', '突破',
                    '上涨', '增长', '盈利', '业绩超预期', '战略合作', '新产品',
                    '技术突破', '政策支持', '订单', '中标'
                ],
                'weight': 1.0
            },
            'BEARISH': {
                'keywords': [
                    '退市', '诉讼', '处罚', '暴雷', '破产', '辞职', '亏损',
                    '下跌', '风险', '警示', '调查', '违规', '造假', '裁员',
                    '债务', '减值', '停牌', '监管'
                ],
                'weight': 1.5  # 利空消息权重更高
            }
        }

    async def load_ai_models(self):
        """加载AI模型"""
        if not self.use_ai:
            print("⏭️  跳过AI模型加载（使用关键词规则）")
            return

        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            models_dir = Path(__file__).parent.parent / 'models'

            sentiment_path = models_dir / 'sentiment_classifier' / 'final_model'
            importance_path = models_dir / 'importance_scorer' / 'final_model'

            if not sentiment_path.exists():
                print(f"⚠️  情绪分类模型不存在: {sentiment_path}")
                print("   请先运行训练: python3 scripts/news_model_trainer.py sentiment")
                self.use_ai = False
                return

            print("📥 加载AI模型...")

            # 加载情绪分类器
            self.tokenizer = AutoTokenizer.from_pretrained(str(sentiment_path))
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                str(sentiment_path)
            )
            self.sentiment_model.eval()
            print("✅ 情绪分类器已加载")

            # 加载重要性评分器（如果存在）
            if importance_path.exists():
                self.importance_model = AutoModelForSequenceClassification.from_pretrained(
                    str(importance_path)
                )
                self.importance_model.eval()
                print("✅ 重要性评分器已加载")
            else:
                print("⚠️  重要性评分器不存在，将使用规则估算")

        except ImportError:
            print("⚠️  transformers库未安装，使用关键词规则")
            self.use_ai = False
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            self.use_ai = False

    def classify_by_keywords(self, title, content):
        """
        基于关键词的分类（AI不可用时使用）

        Returns:
            dict: {
                'sentiment': str,
                'importance': int,
                'confidence': float,
                'matched_keywords': list
            }
        """
        text = f"{title} {content or ''}".lower()

        bullish_score = 0
        bearish_score = 0
        matched_keywords = []

        # 检查利好关键词
        for kw in self.keyword_rules['BULLISH']['keywords']:
            if kw in text:
                bullish_score += self.keyword_rules['BULLISH']['weight']
                matched_keywords.append(('BULLISH', kw))

        # 检查利空关键词
        for kw in self.keyword_rules['BEARISH']['keywords']:
            if kw in text:
                bearish_score += self.keyword_rules['BEARISH']['weight']
                matched_keywords.append(('BEARISH', kw))

        # 判断情绪
        if bullish_score > bearish_score and bullish_score >= 2:
            sentiment = 'BULLISH'
            confidence = min(bullish_score / 5, 1.0)
        elif bearish_score > bullish_score and bearish_score >= 2:
            sentiment = 'BEARISH'
            confidence = min(bearish_score / 5, 1.0)
        else:
            sentiment = 'NEUTRAL'
            confidence = 0.5

        # 估算重要性（基于匹配关键词数量）
        keyword_count = len(matched_keywords)
        if keyword_count >= 3:
            importance = 5
        elif keyword_count >= 2:
            importance = 4
        elif keyword_count == 1:
            importance = 3
        else:
            importance = 2

        return {
            'sentiment': sentiment,
            'importance': importance,
            'confidence': confidence,
            'matched_keywords': matched_keywords
        }

    def classify_by_ai(self, title, content):
        """
        使用AI模型分类

        Returns:
            dict: {
                'sentiment': str,
                'importance': float,
                'confidence': float
            }
        """
        import torch

        text = f"{title}\n{content or ''}"

        # 情绪分类
        inputs = self.tokenizer(
            text,
            max_length=512,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        with torch.no_grad():
            outputs = self.sentiment_model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
            pred_label = torch.argmax(logits, dim=1).item()
            confidence = probs[0][pred_label].item()

        sentiment_map = {0: 'BULLISH', 1: 'BEARISH', 2: 'NEUTRAL'}
        sentiment = sentiment_map[pred_label]

        # 重要性评分
        if self.importance_model:
            with torch.no_grad():
                outputs = self.importance_model(**inputs)
                importance = outputs.logits[0][0].item()
                importance = max(1, min(5, round(importance)))  # 限制在1-5
        else:
            # 如果没有重要性模型，使用简单规则
            importance = 3 if sentiment == 'NEUTRAL' else 4

        return {
            'sentiment': sentiment,
            'importance': importance,
            'confidence': confidence
        }

    async def check_and_push_news(self, news_id, title, content, source):
        """
        检查并推送重大新闻

        Args:
            news_id: 数据库中的新闻ID
            title: 标题
            content: 内容
            source: 来源
        """
        # 分类
        if self.use_ai:
            result = self.classify_by_ai(title, content)
        else:
            result = self.classify_by_keywords(title, content)

        sentiment = result['sentiment']
        importance = result['importance']
        confidence = result['confidence']

        # 保存预测结果
        self.db.add_prediction(news_id, sentiment, importance, confidence)

        # 检查是否需要推送
        if importance >= self.importance_threshold:
            # 构造推送消息
            emoji_map = {
                'BULLISH': '📈',
                'BEARISH': '📉',
                'NEUTRAL': '📊'
            }

            emoji = emoji_map.get(sentiment, '📰')
            importance_stars = '⭐' * int(importance)

            message = f"{emoji} 【重大{sentiment.lower()}消息】 {importance_stars}\n\n"
            message += f"标题: {title}\n\n"

            if content and len(content) < 200:
                message += f"内容: {content}\n\n"

            message += f"来源: {source}\n"
            message += f"重要性: {importance}/5\n"
            message += f"置信度: {confidence:.2f}\n"
            message += f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            if self.use_ai:
                message += "\n\n🤖 AI自动分类"
            else:
                message += "\n\n🔍 关键词匹配"
                if 'matched_keywords' in result:
                    keywords = [kw[1] for kw in result['matched_keywords']]
                    message += f"\n匹配关键词: {', '.join(keywords)}"

            # 推送到飞书
            push_result = self.pusher.push(message)

            if push_result['success']:
                self.db.mark_as_pushed(news_id)
                print(f"✅ 已推送: {title[:50]}...")
                print(f"   情绪: {sentiment}, 重要性: {importance}/5")

                # 记录推送历史到日志
                return True
            else:
                print(f"❌ 推送失败: {title[:50]}...")
                print(f"   错误: {push_result.get('error', 'Unknown')}")
                return False

        return False

    async def monitor_loop(self, interval=300):
        """
        监控循环

        Args:
            interval: 抓取间隔（秒）
        """
        print("\n🔍 新闻监控器启动")
        print("="*80)
        print(f"使用模式: {'AI模型' if self.use_ai else '关键词规则'}")
        print(f"重要性阈值: >= {self.importance_threshold}")
        print(f"抓取间隔: {interval} 秒")
        print(f"飞书推送: {'已配置' if self.pusher.user_open_id or self.pusher.webhook_url else '未配置'}")
        print("="*80 + "\n")

        # 加载AI模型
        await self.load_ai_models()

        iteration = 0

        try:
            while True:
                iteration += 1
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 第 {iteration} 次抓取...")

                # 收集新闻
                stats = await self.collector.collect_all(limit_per_source=30)

                print(f"  抓取: {stats['total_fetched']} 条")
                print(f"  新增: {stats['total_saved']} 条")
                print(f"  重复: {stats['duplicates']} 条")

                # 处理新增的新闻
                if stats['total_saved'] > 0:
                    # 获取最近5分钟的未推送新闻
                    recent_news = self.db.cursor.execute('''
                        SELECT id, title, content, source
                        FROM news
                        WHERE is_pushed = 0
                          AND fetch_time >= datetime('now', '-5 minutes')
                        ORDER BY fetch_time DESC
                    ''').fetchall()

                    push_count = 0
                    for news in recent_news:
                        pushed = await self.check_and_push_news(
                            news['id'],
                            news['title'],
                            news['content'],
                            news['source']
                        )
                        if pushed:
                            push_count += 1

                    if push_count > 0:
                        print(f"  📱 推送: {push_count} 条重大消息")

                print(f"\n下次抓取: {datetime.now() + timedelta(seconds=interval)}")
                print("-"*80)

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n👋 监控器已停止")
        finally:
            await self.collector.close_session()
            self.db.close()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='实时新闻监控器')
    parser.add_argument('--interval', type=int, default=300,
                       help='抓取间隔（秒，默认300）')
    parser.add_argument('--threshold', type=int, default=4,
                       help='重要性阈值（1-5，默认4）')
    parser.add_argument('--no-ai', action='store_true',
                       help='不使用AI模型，只用关键词规则')

    args = parser.parse_args()

    monitor = NewsMonitor(
        use_ai=not args.no_ai,
        importance_threshold=args.threshold
    )

    await monitor.monitor_loop(interval=args.interval)


if __name__ == '__main__':
    asyncio.run(main())
