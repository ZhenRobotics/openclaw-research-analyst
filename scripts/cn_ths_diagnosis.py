#!/usr/bin/env python3
"""
同花顺 (10jqka.com.cn) - 获取F10资料、诊股、研报数据
数据源: https://www.10jqka.com.cn
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
import re

HEADERS = {
    'Referer': 'https://www.10jqka.com.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Cookie': 'v=xxx'  # 可能需要cookie
}


def fetch_hot_stocks(count=30):
    """
    获取同花顺热门股票

    Returns:
        list: 热门股票列表
    """
    try:
        # 同花顺涨幅榜接口
        url = 'http://data.10jqka.com.cn/rank/cxg/board/all/field/zdf/order/desc/page/1/ajax/1/'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('gbk', errors='ignore')

        # 简单HTML解析（实际应该用BeautifulSoup，但这里保持依赖最小化）
        items = []

        # 提取表格数据（简化版）
        # 实际格式: <td>600519</td><td>贵州茅台</td><td>1680.00</td><td>+2.5%</td>
        pattern = r'<td>(\d{6})</td>\s*<td>([^<]+)</td>\s*<td>([0-9.]+)</td>\s*<td[^>]*>([^<]+)</td>'
        matches = re.findall(pattern, html)

        for match in matches[:count]:
            code, name, price, pct = match
            items.append({
                'code': code,
                'name': name.strip(),
                'price': try_float(price),
                'pct': try_float(pct.replace('%', '').replace('+', '')),
                'source': '10jqka_hot'
            })

        return items

    except Exception as e:
        print(f"同花顺热门股票获取失败: {e}", file=__import__('sys').stderr)
        return []


def fetch_stock_diagnosis(code):
    """
    获取个股诊断（同花顺特色功能）

    Args:
        code: 股票代码

    Returns:
        dict: 诊股结果
    """
    try:
        # 同花顺诊股接口
        url = f'http://basic.10jqka.com.cn/api/stock/diagnose/{code}.json'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get('status_code') != 0:
            return None

        result = data.get('data', {})

        return {
            'code': code,
            'comprehensive_score': result.get('comprehensive_score'),  # 综合评分
            'trend_score': result.get('trend_score'),  # 趋势评分
            'valuation': result.get('valuation'),  # 估值
            'profit_ability': result.get('profit_ability'),  # 盈利能力
            'growth': result.get('growth'),  # 成长性
            'recommendation': result.get('recommendation'),  # 建议
            'source': '10jqka_diagnosis'
        }

    except Exception as e:
        print(f"同花顺诊股失败 {code}: {e}", file=__import__('sys').stderr)
        return None


def fetch_stock_reports(code, count=10):
    """
    获取研报数据

    Args:
        code: 股票代码
        count: 获取数量

    Returns:
        list: 研报列表
    """
    try:
        # 同花顺研报接口
        url = f'http://basic.10jqka.com.cn/{code}/report.html'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('gbk', errors='ignore')

        # 简化HTML解析
        items = []

        # 提取研报信息
        pattern = r'<div class="tit">([^<]+)</div>.*?<div class="time">([^<]+)</div>.*?<div class="org">([^<]+)</div>'
        matches = re.findall(pattern, html, re.DOTALL)

        for match in matches[:count]:
            title, date, org = match
            items.append({
                'title': title.strip(),
                'date': date.strip(),
                'organization': org.strip(),
                'code': code,
                'source': '10jqka_report'
            })

        return items

    except Exception as e:
        print(f"同花顺研报获取失败 {code}: {e}", file=__import__('sys').stderr)
        return []


def fetch_industry_ranking(count=20):
    """
    获取行业排行

    Returns:
        list: 行业排行列表
    """
    try:
        url = 'http://q.10jqka.com.cn/thshy/'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('gbk', errors='ignore')

        items = []

        # 简化解析行业数据
        pattern = r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*class="[^"]*">([^<]+)</td>'
        matches = re.findall(pattern, html)

        for match in matches[:count]:
            name, price, pct = match
            if not name or not price:
                continue

            items.append({
                'name': name.strip(),
                'price': try_float(price),
                'pct': try_float(pct.replace('%', '').replace('+', '')),
                'source': '10jqka_industry'
            })

        return items

    except Exception as e:
        print(f"同花顺行业排行获取失败: {e}", file=__import__('sys').stderr)
        return []


def try_float(x):
    """安全转换为float"""
    try:
        return float(x) if x else None
    except:
        return None


def main():
    """主函数：获取同花顺数据并输出JSON"""
    import sys

    # 如果提供了股票代码，获取个股详细信息
    if len(sys.argv) > 1:
        code = sys.argv[1]
        diagnosis = fetch_stock_diagnosis(code)
        reports = fetch_stock_reports(code, count=10)

        result = {
            'timestamp': datetime.now().isoformat(),
            'code': code,
            'diagnosis': diagnosis,
            'reports': reports
        }
    else:
        # 否则获取市场概览
        hot_stocks = fetch_hot_stocks(count=30)
        industry_ranking = fetch_industry_ranking(count=20)

        result = {
            'timestamp': datetime.now().isoformat(),
            'hot_stocks': hot_stocks,
            'industry_ranking': industry_ranking,
            'total_count': len(hot_stocks) + len(industry_ranking)
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
