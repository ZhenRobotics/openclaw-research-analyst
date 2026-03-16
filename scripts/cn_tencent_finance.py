#!/usr/bin/env python3
"""
腾讯财经 - 获取自选股、板块、资金流数据
数据源: https://stockapp.finance.qq.com
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

HEADERS = {
    'Referer': 'https://stockapp.finance.qq.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}


def fetch_concept_plates(count=20):
    """
    获取概念板块涨幅榜

    Args:
        count: 获取数量

    Returns:
        list: 概念板块列表
    """
    try:
        # 腾讯财经概念板块接口
        url = 'https://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/rap&p=1&o=0&l=40&v=list_data'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk', errors='ignore')

        # 解析返回的JS格式数据
        # 格式: var rank_data = {data:"000001~平安银行~..."}
        import re
        match = re.search(r'data:"([^"]+)"', data)
        if not match:
            return []

        items = []
        lines = match.group(1).split(';')

        for line in lines[:count]:
            if not line.strip():
                continue

            fields = line.split('~')
            if len(fields) < 5:
                continue

            items.append({
                'code': fields[0],
                'name': fields[1],
                'price': try_float(fields[2]),
                'pct': try_float(fields[3]),
                'amount': fields[4] if len(fields) > 4 else None,
                'source': 'tencent_concept'
            })

        return items

    except Exception as e:
        print(f"腾讯概念板块获取失败: {e}", file=__import__('sys').stderr)
        return []


def fetch_money_flow(market='sh'):
    """
    获取资金流向数据

    Args:
        market: 市场类型 sh=沪市, sz=深市, cyb=创业板

    Returns:
        dict: 资金流向数据
    """
    try:
        # 腾讯财经资金流向接口
        url = f'https://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/chr&i=0&v=dd&d=d&p=1&l=40'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk', errors='ignore')

        # 简单解析返回数据
        import re
        match = re.search(r'data:"([^"]+)"', data)
        if not match:
            return {}

        lines = match.group(1).split(';')

        inflow = []
        outflow = []

        for line in lines[:20]:
            if not line.strip():
                continue

            fields = line.split('~')
            if len(fields) < 6:
                continue

            item = {
                'code': fields[0],
                'name': fields[1],
                'price': try_float(fields[2]),
                'pct': try_float(fields[3]),
                'net_inflow': try_float(fields[5]) if len(fields) > 5 else None,
            }

            # 根据净流入判断
            if item.get('net_inflow') and item['net_inflow'] > 0:
                inflow.append(item)
            elif item.get('net_inflow') and item['net_inflow'] < 0:
                outflow.append(item)

        return {
            'top_inflow': sorted(inflow, key=lambda x: x.get('net_inflow', 0), reverse=True)[:10],
            'top_outflow': sorted(outflow, key=lambda x: x.get('net_inflow', 0))[:10],
        }

    except Exception as e:
        print(f"腾讯资金流向获取失败: {e}", file=__import__('sys').stderr)
        return {'top_inflow': [], 'top_outflow': []}


def fetch_hot_stocks(count=30):
    """
    获取热门股票（综合腾讯财经数据）

    Returns:
        list: 热门股票列表
    """
    try:
        # 涨幅榜
        url = 'https://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/rap&p=1&o=0&l=40&v=list_data'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk', errors='ignore')

        import re
        match = re.search(r'data:"([^"]+)"', data)
        if not match:
            return []

        items = []
        lines = match.group(1).split(';')

        for line in lines[:count]:
            if not line.strip():
                continue

            fields = line.split('~')
            if len(fields) < 5:
                continue

            items.append({
                'code': fields[0],
                'name': fields[1],
                'price': try_float(fields[2]),
                'pct': try_float(fields[3]),
                'amount': fields[4] if len(fields) > 4 else None,
                'source': 'tencent_hot'
            })

        return items

    except Exception as e:
        print(f"腾讯热门股票获取失败: {e}", file=__import__('sys').stderr)
        return []


def try_float(x):
    """安全转换为float"""
    try:
        return float(x)
    except:
        return None


def main():
    """主函数：获取腾讯财经数据并输出JSON"""
    hot_stocks = fetch_hot_stocks(count=30)
    concept_plates = fetch_concept_plates(count=20)
    money_flow = fetch_money_flow()

    result = {
        'timestamp': datetime.now().isoformat(),
        'hot_stocks': hot_stocks,
        'concept_plates': concept_plates,
        'money_flow': money_flow,
        'total_count': len(hot_stocks) + len(concept_plates)
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
