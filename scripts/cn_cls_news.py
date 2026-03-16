#!/usr/bin/env python3
"""
财联社快讯 (CLS.cn) - 获取实时财经快讯
数据源: https://www.cls.cn/telegraph
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

HEADERS = {
    'Referer': 'https://www.cls.cn/telegraph',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

def fetch_cls_telegraph(count=20):
    """
    获取财联社电报快讯

    Args:
        count: 获取数量，默认20条

    Returns:
        list: 快讯列表
    """
    try:
        # 财联社API（可能需要根据实际情况调整）
        # 注意：实际API可能有反爬虫，这里使用通用接口格式
        url = f'https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&category=&lastTime=&os=web&refresh_type=1&rn={count}&sv=7.7.5'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))

        items = []
        rolldata = data.get('data', {}).get('roll_data', [])

        for item in rolldata[:count]:
            # 提取股票代码（简单正则匹配）
            content = item.get('content', '')
            brief = item.get('brief', '')

            # 提取可能的股票代码
            import re
            codes = re.findall(r'[0-9]{6}|HK\.[0-9]{5}', content + brief)

            items.append({
                'id': item.get('id'),
                'title': item.get('title', ''),
                'brief': brief[:200] if brief else '',  # 限制长度
                'content': content[:500] if content else '',  # 限制长度
                'ctime': item.get('ctime', ''),
                'level': item.get('level', 0),  # 重要性等级
                'related_codes': list(set(codes)),  # 去重
                'source': 'cls_telegraph'
            })

        return items

    except Exception as e:
        print(f"财联社数据获取失败: {e}", file=__import__('sys').stderr)
        return []


def fetch_cls_depth(count=10):
    """
    获取财联社深度文章

    Args:
        count: 获取数量，默认10条

    Returns:
        list: 深度文章列表
    """
    try:
        # 深度文章接口
        url = f'https://www.cls.cn/nodeapi/updateTelegraphList?app=CailianpressWeb&category=depth&lastTime=&os=web&refresh_type=1&rn={count}&sv=7.7.5'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))

        items = []
        rolldata = data.get('data', {}).get('roll_data', [])

        for item in rolldata[:count]:
            items.append({
                'id': item.get('id'),
                'title': item.get('title', ''),
                'brief': item.get('brief', '')[:300],
                'ctime': item.get('ctime', ''),
                'source': 'cls_depth'
            })

        return items

    except Exception as e:
        print(f"财联社深度数据获取失败: {e}", file=__import__('sys').stderr)
        return []


def main():
    """主函数：获取财联社数据并输出JSON"""
    telegraph = fetch_cls_telegraph(count=30)
    depth = fetch_cls_depth(count=10)

    result = {
        'timestamp': datetime.now().isoformat(),
        'telegraph': telegraph,
        'depth': depth,
        'total_count': len(telegraph) + len(depth)
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
