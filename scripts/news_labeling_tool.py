#!/usr/bin/env python3
"""
新闻标注工具
News Labeling Tool

交互式标注工具，用于标注新闻的情绪和重要性
"""
import sys
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from news_database import NewsDatabase


class NewsLabelingTool:
    """新闻标注工具"""

    def __init__(self):
        self.db = NewsDatabase()
        self.labeled_count = 0

    def display_news(self, news):
        """显示新闻详情"""
        print("\n" + "="*80)
        print(f"📰 新闻 ID: {news['id']}")
        print(f"📅 发布时间: {news['publish_time']}")
        print(f"📍 来源: {news['source']}")
        print("="*80)
        print(f"\n标题: {news['title']}\n")

        if news['content']:
            content = news['content'][:500] + "..." if len(news['content']) > 500 else news['content']
            print(f"内容: {content}\n")

        if news['url']:
            print(f"链接: {news['url']}\n")

        print("="*80)

    def label_news_interactive(self, news):
        """交互式标注单条新闻"""
        self.display_news(news)

        # 情绪标注
        print("\n情绪分类:")
        print("  1. BULLISH (利好)")
        print("  2. BEARISH (利空)")
        print("  3. NEUTRAL (中性)")
        print("  s. SKIP (跳过)")
        print("  q. QUIT (退出)")

        while True:
            choice = input("\n请选择 [1/2/3/s/q]: ").strip().lower()

            if choice == 'q':
                return 'quit'
            elif choice == 's':
                return 'skip'
            elif choice == '1':
                sentiment = 'BULLISH'
                break
            elif choice == '2':
                sentiment = 'BEARISH'
                break
            elif choice == '3':
                sentiment = 'NEUTRAL'
                break
            else:
                print("❌ 无效选择，请重新输入")

        # 重要性评分
        print("\n重要性评分:")
        print("  5 - 极其重大（全市场影响，必须立即推送）")
        print("  4 - 非常重要（行业级影响，应该推送）")
        print("  3 - 比较重要（公司级影响）")
        print("  2 - 一般重要（常规新闻）")
        print("  1 - 不太重要（参考信息）")

        while True:
            importance_input = input("\n请输入重要性 [1-5]: ").strip()

            try:
                importance = int(importance_input)
                if 1 <= importance <= 5:
                    break
                else:
                    print("❌ 请输入 1-5 之间的数字")
            except ValueError:
                print("❌ 无效输入，请输入数字")

        # 相关股票（可选）
        print("\n相关股票（可选，用逗号分隔，如: 000001,600000）:")
        stocks_input = input("股票代码: ").strip()
        affected_stocks = [s.strip() for s in stocks_input.split(',') if s.strip()]

        # 标签（可选）
        print("\n标签（可选，用逗号分隔，如: 政策,并购,业绩）:")
        tags_input = input("标签: ").strip()
        tags = [t.strip() for t in tags_input.split(',') if t.strip()]

        # 保存标注
        self.db.label_news(
            news_id=news['id'],
            sentiment=sentiment,
            importance=importance,
            affected_stocks=affected_stocks if affected_stocks else None,
            tags=tags if tags else None,
            labeled_by='human'
        )

        self.labeled_count += 1

        # 显示标注结果
        print(f"\n✅ 标注完成:")
        print(f"   情绪: {sentiment}")
        print(f"   重要性: {importance}/5")
        if affected_stocks:
            print(f"   相关股票: {', '.join(affected_stocks)}")
        if tags:
            print(f"   标签: {', '.join(tags)}")

        if importance >= 4:
            print(f"\n⚠️ 这是重大新闻，将被标记为推送候选！")

        return 'continue'

    def batch_labeling(self, batch_size=10):
        """批量标注"""
        print("\n🏷️  新闻标注工具")
        print("="*80)

        news_list = self.db.get_unlabeled_news(limit=batch_size)

        if not news_list:
            print("\n✅ 没有待标注的新闻！")
            return

        print(f"\n📊 待标注新闻数: {len(news_list)}")
        print(f"📊 本次标注批次: {min(batch_size, len(news_list))}")

        for idx, news in enumerate(news_list, 1):
            print(f"\n进度: {idx}/{len(news_list)}")

            result = self.label_news_interactive(news)

            if result == 'quit':
                print(f"\n👋 退出标注")
                break
            elif result == 'skip':
                print(f"\n⏭️  跳过此条")
                continue

        # 显示统计
        print("\n" + "="*80)
        print(f"✅ 本次标注完成: {self.labeled_count} 条")

        stats = self.db.get_statistics()
        print(f"📊 数据库总计:")
        print(f"   - 总新闻数: {stats['total_news']}")
        print(f"   - 已标注数: {stats['labeled_news']}")
        print(f"   - 标注进度: {stats['labeled_news']/stats['total_news']*100:.1f}%")

    def review_labeled(self, limit=10):
        """查看已标注的新闻"""
        print("\n📋 已标注新闻列表")
        print("="*80)

        news_list = self.db.get_labeled_news(limit=limit)

        if not news_list:
            print("\n⚠️ 暂无已标注的新闻")
            return

        for idx, news in enumerate(news_list, 1):
            print(f"\n[{idx}] {news['title']}")
            print(f"    发布时间: {news['publish_time']}")
            print(f"    情绪: {news['sentiment']}")
            print(f"    重要性: {news['importance']}/5")
            print(f"    标注时间: {news['labeled_at']}")

    def close(self):
        """关闭数据库连接"""
        self.db.close()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='新闻标注工具')
    parser.add_argument('command', choices=['label', 'review', 'stats'],
                       help='命令：label（标注）、review（查看）、stats（统计）')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='批量标注的数量（默认10）')
    parser.add_argument('--limit', type=int, default=10,
                       help='查看数量（默认10）')

    args = parser.parse_args()

    tool = NewsLabelingTool()

    try:
        if args.command == 'label':
            tool.batch_labeling(batch_size=args.batch_size)
        elif args.command == 'review':
            tool.review_labeled(limit=args.limit)
        elif args.command == 'stats':
            db = NewsDatabase()
            stats = db.get_statistics()

            print("\n=== 数据库统计 ===\n")
            print(f"总新闻数: {stats['total_news']}")
            print(f"已标注数: {stats['labeled_news']}")
            print(f"重大新闻: {stats['major_news']}")

            if stats['labeled_news'] > 0:
                print(f"\n标注进度: {stats['labeled_news']/stats['total_news']*100:.1f}%")

                print("\n情绪分布:")
                for sentiment, count in stats['sentiment_distribution'].items():
                    percentage = count / stats['labeled_news'] * 100
                    print(f"  {sentiment}: {count} ({percentage:.1f}%)")

                print("\n重要性分布:")
                for importance, count in sorted(stats['importance_distribution'].items()):
                    percentage = count / stats['labeled_news'] * 100
                    print(f"  {importance}: {count} ({percentage:.1f}%)")

            print("\n来源分布:")
            for source, count in stats['source_distribution'].items():
                print(f"  {source}: {count}")

            db.close()

    finally:
        tool.close()


if __name__ == '__main__':
    main()
