#!/usr/bin/env python3
"""
快速监控模式 - 优化版
采用增量抓取 + 短间隔，提升实时性
"""
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from news_monitor import NewsMonitor

class FastNewsMonitor(NewsMonitor):
    """快速监控器 - 优化实时性"""

    async def monitor_loop_fast(self, interval=60):
        """
        快速监控循环
        - 使用更短的间隔（默认60秒）
        - 只抓取最新的10-20条（减少重复）
        - 更快的响应速度
        """
        print("\n🚀 快速监控模式启动")
        print("="*80)
        print(f"使用模式: {'AI模型' if self.use_ai else '关键词规则'}")
        print(f"重要性阈值: >= {self.importance_threshold}")
        print(f"抓取间隔: {interval} 秒 ⚡")
        print(f"每次抓取: 20 条最新新闻（增量模式）")
        print(f"飞书推送: {'已配置' if self.pusher.user_open_id or self.pusher.webhook_url else '未配置'}")
        print("="*80 + "\n")

        # 加载AI模型
        await self.load_ai_models()

        iteration = 0

        try:
            while True:
                iteration += 1
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 第 {iteration} 次抓取...")

                # 只抓取最新的20条（而不是50条）
                stats = await self.collector.collect_all(limit_per_source=20)

                print(f"  抓取: {stats['total_fetched']} 条")
                print(f"  新增: {stats['total_saved']} 条")
                print(f"  重复: {stats['duplicates']} 条")

                # 只处理新增的新闻（减少计算）
                if stats['total_saved'] > 0:
                    # 获取最近1分钟的未推送新闻
                    recent_news = self.db.cursor.execute('''
                        SELECT id, title, content, source
                        FROM news
                        WHERE is_pushed = 0
                          AND fetch_time >= datetime('now', '-2 minutes')
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

                next_time = datetime.now() + timedelta(seconds=interval)
                print(f"  下次抓取: {next_time.strftime('%H:%M:%S')}")
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

    parser = argparse.ArgumentParser(description='快速新闻监控器')
    parser.add_argument('--interval', type=int, default=60,
                       help='抓取间隔（秒，默认60）')
    parser.add_argument('--threshold', type=int, default=4,
                       help='重要性阈值（1-5，默认4）')
    parser.add_argument('--no-ai', action='store_true',
                       help='不使用AI模型，只用关键词规则')

    args = parser.parse_args()

    monitor = FastNewsMonitor(
        use_ai=not args.no_ai,
        importance_threshold=args.threshold
    )

    await monitor.monitor_loop_fast(interval=args.interval)


if __name__ == '__main__':
    asyncio.run(main())
