#!/usr/bin/env python3
"""
新闻收集器
News Collector

从多个来源收集中国市场新闻，存入数据库
"""
import sys
import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from news_database import NewsDatabase


class NewsCollector:
    """新闻收集器"""

    def __init__(self):
        self.db = NewsDatabase()
        self.session = None

    async def init_session(self):
        """初始化HTTP会话"""
        if self.session is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }
            self.session = aiohttp.ClientSession(headers=headers)

    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()

    async def fetch_eastmoney_news(self, limit=50):
        """
        抓取东方财富新闻

        Returns:
            list: 新闻列表
        """
        await self.init_session()

        url = "https://newsapi.eastmoney.com/api/getcode"
        params = {
            "type": "0",  # 0=全部, 1=公司, 2=行业
            "pageSize": limit,
            "pageIndex": 1,
            "client": "web"
        }

        try:
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    news_list = []

                    for item in data.get('data', {}).get('list', []):
                        news_list.append({
                            'title': item.get('title', ''),
                            'content': item.get('content', ''),
                            'url': item.get('url', ''),
                            'publish_time': datetime.fromtimestamp(item.get('showtime', 0)),
                            'source': 'eastmoney',
                            'raw_data': item
                        })

                    return news_list
                else:
                    print(f"❌ 东方财富新闻响应错误: HTTP {response.status}", file=sys.stderr)
                    return []
        except Exception as e:
            print(f"❌ 东方财富新闻抓取失败: {e}", file=sys.stderr)
            return []

    async def fetch_cls_news(self, limit=50):
        """
        抓取财联社快讯和深度文章

        Returns:
            list: 新闻列表
        """
        await self.init_session()

        headers = {
            'Referer': 'https://www.cls.cn/telegraph'
        }

        news_list = []

        # 尝试抓取快讯
        url_telegraph = "https://www.cls.cn/nodeapi/telegraphList"
        params_telegraph = {
            "app": "CailianpressWeb",
            "category": "",
            "lastTime": "",
            "os": "web",
            "refresh_type": 1,
            "rn": limit,
            "sv": "7.7.5"
        }

        try:
            async with self.session.get(url_telegraph, params=params_telegraph, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get('data', {}).get('roll_data', []):
                        news_list.append({
                            'title': item.get('title', ''),
                            'content': item.get('content', ''),
                            'url': f"https://www.cls.cn/detail/{item.get('id')}",
                            'publish_time': datetime.fromtimestamp(item.get('ctime', 0)),
                            'source': 'cls',
                            'raw_data': item
                        })
        except Exception as e:
            print(f"❌ 财联社快讯抓取失败: {e}", file=sys.stderr)

        # 尝试抓取深度文章（作为补充）
        url_depth = "https://www.cls.cn/nodeapi/updateTelegraphList"
        params_depth = {
            "app": "CailianpressWeb",
            "category": "depth",
            "lastTime": "",
            "os": "web",
            "refresh_type": 1,
            "rn": min(limit, 20),  # 深度文章数量较少
            "sv": "7.7.5"
        }

        try:
            async with self.session.get(url_depth, params=params_depth, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data.get('data', {}).get('roll_data', []):
                        news_list.append({
                            'title': item.get('title', ''),
                            'content': item.get('brief', ''),
                            'url': f"https://www.cls.cn/detail/{item.get('id')}",
                            'publish_time': datetime.fromtimestamp(item.get('ctime', 0)),
                            'source': 'cls',
                            'raw_data': item
                        })
        except Exception as e:
            print(f"❌ 财联社深度文章抓取失败: {e}", file=sys.stderr)

        return news_list

    async def fetch_sina_news(self, limit=50):
        """
        抓取新浪财经新闻

        Returns:
            list: 新闻列表
        """
        await self.init_session()

        url = "https://finance.sina.com.cn/roll/index.d.html"

        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()

                    # 简单解析（需要更复杂的HTML解析）
                    news_list = []

                    # 这里只是占位符，实际需要使用 BeautifulSoup 或正则表达式解析
                    # 暂时返回空列表
                    return news_list
                else:
                    print(f"❌ 新浪财经新闻响应错误: HTTP {response.status}", file=sys.stderr)
                    return []
        except Exception as e:
            print(f"❌ 新浪财经新闻抓取失败: {e}", file=sys.stderr)
            return []

    async def collect_all(self, limit_per_source=50):
        """
        从所有来源收集新闻

        Args:
            limit_per_source: 每个来源抓取的新闻数量

        Returns:
            dict: 收集结果统计
        """
        print("📰 开始收集新闻...\n")

        # 并行抓取
        tasks = [
            self.fetch_eastmoney_news(limit_per_source),
            self.fetch_cls_news(limit_per_source),
            # self.fetch_sina_news(limit_per_source),  # 暂时禁用
        ]

        results = await asyncio.gather(*tasks)

        # 合并结果
        all_news = []
        for news_list in results:
            all_news.extend(news_list)

        # 存入数据库
        stats = {
            'total_fetched': len(all_news),
            'total_saved': 0,
            'duplicates': 0,
            'by_source': {}
        }

        for news in all_news:
            source = news['source']

            # 统计来源
            if source not in stats['by_source']:
                stats['by_source'][source] = {'fetched': 0, 'saved': 0}

            stats['by_source'][source]['fetched'] += 1

            # 存入数据库
            news_id = self.db.add_news(
                title=news['title'],
                content=news['content'],
                source=source,
                url=news['url'],
                publish_time=news['publish_time'],
                raw_data=news.get('raw_data')
            )

            if news_id:
                stats['total_saved'] += 1
                stats['by_source'][source]['saved'] += 1
            else:
                stats['duplicates'] += 1

        return stats

    def close(self):
        """关闭数据库连接"""
        self.db.close()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='新闻收集器')
    parser.add_argument('--limit', type=int, default=50,
                       help='每个来源抓取的新闻数量（默认50）')
    parser.add_argument('--continuous', action='store_true',
                       help='持续运行模式（每5分钟抓取一次）')
    parser.add_argument('--interval', type=int, default=300,
                       help='持续运行时的抓取间隔（秒，默认300）')

    args = parser.parse_args()

    collector = NewsCollector()

    try:
        if args.continuous:
            print(f"🔄 持续运行模式，每 {args.interval} 秒抓取一次\n")

            while True:
                stats = await collector.collect_all(limit_per_source=args.limit)

                print("\n=== 收集完成 ===\n")
                print(f"抓取总数: {stats['total_fetched']}")
                print(f"保存总数: {stats['total_saved']}")
                print(f"重复数量: {stats['duplicates']}")

                print("\n按来源统计:")
                for source, counts in stats['by_source'].items():
                    print(f"  {source}: 抓取 {counts['fetched']}, 保存 {counts['saved']}")

                print(f"\n下次抓取时间: {datetime.now() + timedelta(seconds=args.interval)}")
                print("\n" + "="*60 + "\n")

                await asyncio.sleep(args.interval)
        else:
            stats = await collector.collect_all(limit_per_source=args.limit)

            print("\n=== 收集完成 ===\n")
            print(f"抓取总数: {stats['total_fetched']}")
            print(f"保存总数: {stats['total_saved']}")
            print(f"重复数量: {stats['duplicates']}")

            print("\n按来源统计:")
            for source, counts in stats['by_source'].items():
                print(f"  {source}: 抓取 {counts['fetched']}, 保存 {counts['saved']}")

    finally:
        await collector.close_session()
        collector.close()


if __name__ == '__main__':
    asyncio.run(main())
