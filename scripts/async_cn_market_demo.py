#!/usr/bin/env python3
"""
Async China Market Report - Phase 1 Implementation Demo

This demonstrates how to migrate the existing cn_market_report.py to
use async parallel data fetching.

Expected Performance:
- Current: 38.98s (sequential)
- Target: <22s (parallel with optimization)
- Improvement: 43%

Usage:
    # Enable async mode
    export CN_MARKET_USE_ASYNC=true

    # Run report
    python3 scripts/async_cn_market_demo.py
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional

# Import the async architecture core
from async_architecture_core import (
    AsyncDataOrchestrator,
    SimpleCacheManager,
    DataSource,
    FetchResult,
    FetchStatus,
    validate_fetch_results,
    get_performance_summary
)


# =============================================================================
# Async Data Source Implementations
# =============================================================================

async def fetch_sina_quotes_async(
    session: aiohttp.ClientSession,
    params: Optional[dict]
) -> dict:
    """
    Async version of Sina Finance stock quotes

    Performance:
    - Original: 1.11s (sync)
    - Async: ~1.0s (minimal overhead)
    """
    tickers = params.get('tickers', []) if params else []

    if not tickers:
        return {'quotes': []}

    # Convert to Sina format
    def to_sina_code(t: str) -> str:
        t = t.strip().upper()
        if t.startswith('HK.'):
            return 'hk' + t.split('.', 1)[1].zfill(5)
        if t.isdigit() and len(t) == 6:
            return ('sh' if t.startswith(('5', '6')) else 'sz') + t
        return t

    sina_codes = [to_sina_code(t) for t in tickers]
    url = 'https://hq.sinajs.cn/list=' + ','.join(sina_codes)

    headers = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        async with session.get(url, headers=headers, timeout=30) as response:
            data = await response.read()

        # Parse response
        text = data.decode('gbk', errors='ignore')
        quotes = []

        for line in text.strip().split('\n'):
            if '="' not in line:
                continue

            head, rest = line.split('="', 1)
            fields = rest.rstrip('";').split(',')

            if len(fields) < 4:
                continue

            symbol = head.split('str_')[-1]
            quotes.append({
                'symbol': symbol,
                'name': fields[0],
                'price': float(fields[3]) if fields[3] else 0.0,
                'pct': float(fields[32]) if len(fields) > 32 and fields[32] else 0.0
            })

        return {'quotes': quotes}

    except Exception as e:
        print(f"Sina quotes error: {e}", file=sys.stderr)
        raise


async def fetch_eastmoney_rankings_async(
    session: aiohttp.ClientSession,
    params: Optional[dict]
) -> dict:
    """
    Async version of Eastmoney market rankings

    Performance:
    - Original: 2.49s (sync)
    - Async: ~2.3s
    """
    base_url = 'https://push2.eastmoney.com/api/qt/clist/get'

    headers = {
        'Referer': 'https://quote.eastmoney.com/center/gridlist.html',
        'User-Agent': 'Mozilla/5.0'
    }

    # Common fields
    fields = 'f12,f14,f2,f3,f6'

    async def fetch_list(fs: str, fid: str, pz: int = 20) -> List[dict]:
        """Fetch a single list"""
        params = {
            'pn': 1,
            'pz': pz,
            'po': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': fid,
            'fs': fs,
            'fields': fields
        }

        try:
            async with session.get(base_url, params=params, headers=headers, timeout=30) as response:
                data = await response.json()

            items = (data.get('data') or {}).get('diff') or []
            return [
                {
                    'code': it.get('f12'),
                    'name': it.get('f14'),
                    'price': it.get('f2'),
                    'pct': it.get('f3'),
                    'amount': it.get('f6'),
                }
                for it in items
            ]

        except Exception as e:
            print(f"Eastmoney fetch error for {fid}: {e}", file=sys.stderr)
            return []

    # Fetch A-share and HK in parallel
    a_fs = 'm:1 t:2,m:1 t:23'
    hk_fs = 'm:116 t:3,m:116 t:4'

    a_gainers, a_amount, hk_gainers, hk_amount = await asyncio.gather(
        fetch_list(a_fs, 'f3', 20),  # A-share top gainers
        fetch_list(a_fs, 'f6', 20),  # A-share top amount
        fetch_list(hk_fs, 'f3', 20),  # HK top gainers
        fetch_list(hk_fs, 'f6', 20),  # HK top amount
        return_exceptions=True
    )

    return {
        'a_share': {
            'top_gainers': a_gainers if not isinstance(a_gainers, Exception) else [],
            'top_amount': a_amount if not isinstance(a_amount, Exception) else []
        },
        'hong_kong': {
            'top_gainers': hk_gainers if not isinstance(hk_gainers, Exception) else [],
            'top_amount': hk_amount if not isinstance(hk_amount, Exception) else []
        }
    }


async def fetch_cls_telegraph_async(
    session: aiohttp.ClientSession,
    params: Optional[dict]
) -> dict:
    """
    Async version of CLS Telegraph (财联社快讯)

    Performance:
    - Original: 2.06s (sync)
    - Async: ~1.8s
    - With anti-scraping: may add 0.5-1s delay
    """
    import re

    count = params.get('count', 30) if params else 30

    url = f'https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&category=&lastTime=&os=web&refresh_type=1&rn={count}&sv=7.7.5'

    headers = {
        'Referer': 'https://www.cls.cn/telegraph',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        async with session.get(url, headers=headers, timeout=15) as response:
            data = await response.json()

        items = []
        rolldata = data.get('data', {}).get('roll_data', [])

        for item in rolldata[:count]:
            content = item.get('content', '')
            brief = item.get('brief', '')

            # Extract stock codes
            codes = re.findall(r'[0-9]{6}|HK\.[0-9]{5}', content + brief)

            items.append({
                'id': item.get('id'),
                'title': item.get('title', ''),
                'brief': brief[:200] if brief else '',
                'content': content[:500] if content else '',
                'ctime': item.get('ctime', ''),
                'level': item.get('level', 0),
                'related_codes': list(set(codes)),
                'source': 'cls_telegraph'
            })

        return {
            'timestamp': datetime.now().isoformat(),
            'telegraph': items,
            'depth': [],  # Simplified for demo
            'total_count': len(items)
        }

    except Exception as e:
        print(f"CLS telegraph error: {e}", file=sys.stderr)
        raise


async def fetch_tencent_moneyflow_async(
    session: aiohttp.ClientSession,
    params: Optional[dict]
) -> dict:
    """
    Async version of Tencent Finance money flow

    Performance:
    - Original: 7.06s (sync)
    - Async: ~6.5s
    - With auth optimization (Phase 3): <4s

    Note: Currently returns empty data due to auth issues
    """
    import re

    url = 'https://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/chr&i=0&v=dd&d=d&p=1&l=40'

    headers = {
        'Referer': 'https://stockapp.finance.qq.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            data = await response.read()

        text = data.decode('gbk', errors='ignore')

        # Parse response
        match = re.search(r'data:"([^"]+)"', text)
        if not match:
            return {
                'timestamp': datetime.now().isoformat(),
                'hot_stocks': [],
                'concept_plates': [],
                'money_flow': {'top_inflow': [], 'top_outflow': []},
                'total_count': 0
            }

        lines = match.group(1).split(';')
        inflow = []
        outflow = []

        for line in lines[:20]:
            if not line.strip():
                continue

            fields = line.split('~')
            if len(fields) < 6:
                continue

            try:
                net_inflow = float(fields[5]) if len(fields) > 5 else None
            except:
                net_inflow = None

            item = {
                'code': fields[0],
                'name': fields[1],
                'price': float(fields[2]) if fields[2] else None,
                'pct': float(fields[3]) if fields[3] else None,
                'net_inflow': net_inflow,
            }

            if net_inflow and net_inflow > 0:
                inflow.append(item)
            elif net_inflow and net_inflow < 0:
                outflow.append(item)

        return {
            'timestamp': datetime.now().isoformat(),
            'hot_stocks': [],
            'concept_plates': [],
            'money_flow': {
                'top_inflow': sorted(inflow, key=lambda x: x.get('net_inflow', 0), reverse=True)[:10],
                'top_outflow': sorted(outflow, key=lambda x: x.get('net_inflow', 0))[:10],
            },
            'total_count': len(inflow) + len(outflow)
        }

    except Exception as e:
        print(f"Tencent money flow error: {e}", file=sys.stderr)
        raise


async def fetch_ths_diagnosis_async(
    session: aiohttp.ClientSession,
    params: Optional[dict]
) -> dict:
    """
    Async version of 10jqka (THS) diagnosis

    Performance:
    - Original: 10.56s (sync with regex)
    - Async: ~10.0s (still slow due to HTML parsing)
    - With BeautifulSoup optimization (Phase 2): <5s

    TODO: Migrate to BeautifulSoup + lxml for 50% speedup
    """
    import re

    url = 'http://q.10jqka.com.cn/thshy/'

    headers = {
        'Referer': 'https://www.10jqka.com.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            html = await response.text(encoding='gbk', errors='ignore')

        items = []

        # Simplified HTML parsing with regex (slow but works)
        # TODO: Replace with BeautifulSoup in Phase 2
        pattern = r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*class="[^"]*">([^<]+)</td>'
        matches = re.findall(pattern, html)

        for match in matches[:20]:
            name, price, pct = match
            if not name or not price:
                continue

            try:
                price_float = float(price)
                pct_float = float(pct.replace('%', '').replace('+', ''))
            except:
                continue

            items.append({
                'name': name.strip(),
                'price': price_float,
                'pct': pct_float,
                'source': '10jqka_industry'
            })

        return {
            'timestamp': datetime.now().isoformat(),
            'hot_stocks': [],
            'industry_ranking': items,
            'total_count': len(items)
        }

    except Exception as e:
        print(f"THS diagnosis error: {e}", file=sys.stderr)
        raise


# =============================================================================
# Report Generation
# =============================================================================

async def generate_async_report(
    tickers: List[str] = None,
    cache_enabled: bool = True
) -> dict:
    """
    Generate China market report using async architecture

    Args:
        tickers: List of stock tickers for watchlist
        cache_enabled: Whether to use caching

    Returns:
        Report data dictionary
    """
    if tickers is None:
        tickers = ['510300', '600519', '000001', 'HK.00700']

    # Initialize cache
    cache = SimpleCacheManager(max_size_mb=100)

    # Define data sources
    sources = [
        DataSource(
            name='stock_quotes',
            fetch_func=fetch_sina_quotes_async,
            timeout=30,
            max_retries=3,
            cache_ttl=15,  # 15 seconds - near real-time
            required=True  # Critical data
        ),
        DataSource(
            name='market_rankings',
            fetch_func=fetch_eastmoney_rankings_async,
            timeout=30,
            max_retries=3,
            cache_ttl=300,  # 5 minutes
            required=False
        ),
        DataSource(
            name='cls_telegraph',
            fetch_func=fetch_cls_telegraph_async,
            timeout=15,
            max_retries=3,
            cache_ttl=60,  # 1 minute
            required=False
        ),
        DataSource(
            name='tencent_moneyflow',
            fetch_func=fetch_tencent_moneyflow_async,
            timeout=10,
            max_retries=3,
            cache_ttl=300,  # 5 minutes
            required=False
        ),
        DataSource(
            name='ths_diagnosis',
            fetch_func=fetch_ths_diagnosis_async,
            timeout=10,
            max_retries=3,
            cache_ttl=600,  # 10 minutes
            required=False
        )
    ]

    # Fetch all data in parallel
    params = {'tickers': tickers, 'count': 30}

    async with AsyncDataOrchestrator(cache) as orchestrator:
        print("🚀 Starting parallel data fetch...", file=sys.stderr)
        start_time = asyncio.get_event_loop().time()

        results = await orchestrator.fetch_all_sources(sources, params)

        end_time = asyncio.get_event_loop().time()
        duration_ms = (end_time - start_time) * 1000

        print(f"✅ Data fetch completed in {duration_ms:.0f}ms", file=sys.stderr)

    # Validate required sources
    is_valid, error = validate_fetch_results(results, ['stock_quotes'])

    if not is_valid:
        return {
            'error': error,
            'results': {k: v.to_dict() for k, v in results.items()}
        }

    # Extract data from results
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'tickers': tickers,
        'quotes': results['stock_quotes'].data.get('quotes', []) if results['stock_quotes'].data else [],
        'market_rankings': results['market_rankings'].data if results['market_rankings'].data else {},
        'cls_telegraph': results['cls_telegraph'].data if results['cls_telegraph'].data else {},
        'tencent_moneyflow': results['tencent_moneyflow'].data if results['tencent_moneyflow'].data else {},
        'ths_diagnosis': results['ths_diagnosis'].data if results['ths_diagnosis'].data else {},
        'performance': get_performance_summary(results)
    }

    return report_data


def format_markdown_report(report_data: dict) -> str:
    """
    Format report data as markdown (same as original)

    Args:
        report_data: Report data dictionary

    Returns:
        Markdown formatted string
    """
    lines = []
    stamp = datetime.now().strftime('%F')

    lines.append(f'# 每日中文市场简报（A/HK） - {stamp}')
    lines.append('')
    lines.append('生成时间：' + datetime.now().strftime('%F %T'))

    # Watchlist quotes
    lines.append('')
    lines.append('## 观察清单（实时快照）')
    for q in report_data.get('quotes', []):
        name = q.get('name') or q.get('symbol')
        price = q.get('price')
        pct = q.get('pct')
        lines.append(f'- {name}: {price} ({pct}%)')

    # A-share rankings
    rankings = report_data.get('market_rankings', {})
    a_share = rankings.get('a_share', {})

    lines.append('')
    lines.append('## A 股榜单')

    if a_share.get('top_gainers'):
        lines.append('### 涨幅榜（Top 20）')
        for it in a_share['top_gainers'][:20]:
            lines.append(f"- {it['name']}({it['code']}): {it['pct']}%  现价:{it['price']} 成交额:{it['amount']}")

    if a_share.get('top_amount'):
        lines.append('### 成交额榜（Top 20）')
        for it in a_share['top_amount'][:20]:
            lines.append(f"- {it['name']}({it['code']}): 成交额:{it['amount']}  涨幅:{it['pct']}% 现价:{it['price']}")

    # Hong Kong rankings
    hk = rankings.get('hong_kong', {})
    lines.append('')
    lines.append('## 港股榜单（若接口异常将留空）')

    if hk.get('top_gainers'):
        lines.append('### 涨幅榜（Top 20）')
        for it in hk['top_gainers'][:20]:
            lines.append(f"- {it['name']}({it['code']}): {it['pct']}%  现价:{it['price']} 成交额:{it['amount']}")

    # CLS telegraph
    cls = report_data.get('cls_telegraph', {})
    lines.append('')
    lines.append('## 财联社快讯 (实时)')

    if cls.get('telegraph'):
        for item in cls['telegraph'][:10]:
            title = item.get('title') or item.get('brief', '')[:50]
            codes = ','.join(item.get('related_codes', [])[:3])
            codes_str = f" [{codes}]" if codes else ""
            lines.append(f"- {item.get('ctime', '')} {title}{codes_str}")
    else:
        lines.append('- 财联社数据获取失败或无数据')

    # Tencent money flow
    tencent = report_data.get('tencent_moneyflow', {})
    money_flow = tencent.get('money_flow', {})

    lines.append('')
    lines.append('## 资金流向 (腾讯财经)')

    if money_flow.get('top_inflow'):
        lines.append('### 主力净流入 Top 5')
        for item in money_flow['top_inflow'][:5]:
            lines.append(f"- {item.get('name')}({item.get('code')}): 净流入 {item.get('net_inflow', 0):.2f}万 涨幅:{item.get('pct', 0):.2f}%")

    if money_flow.get('top_outflow'):
        lines.append('### 主力净流出 Top 5')
        for item in money_flow['top_outflow'][:5]:
            lines.append(f"- {item.get('name')}({item.get('code')}): 净流出 {abs(item.get('net_inflow', 0)):.2f}万 涨幅:{item.get('pct', 0):.2f}%")

    # THS industry ranking
    ths = report_data.get('ths_diagnosis', {})
    lines.append('')
    lines.append('## 行业板块 (同花顺)')

    if ths.get('industry_ranking'):
        for item in ths['industry_ranking'][:10]:
            lines.append(f"- {item.get('name')}: {item.get('pct', 0):.2f}%")
    else:
        lines.append('- 同花顺数据获取失败或无数据')

    # Performance metrics
    perf = report_data.get('performance', {})
    lines.append('')
    lines.append('---')
    lines.append('## 性能指标')
    lines.append(f"- 总耗时: {perf.get('total_time_parallel_ms', 0):.0f}ms")
    lines.append(f"- 成功率: {perf.get('success_rate', 0):.1%}")
    lines.append(f"- 缓存命中率: {perf.get('cache_hit_rate', 0):.1%}")

    return '\n'.join(lines) + '\n'


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Main entry point for async report generation"""
    print("=" * 70, file=sys.stderr)
    print("🚀 China Market Async Report - Phase 1 Demo", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    # Generate report
    report_data = await generate_async_report()

    if 'error' in report_data:
        print(f"❌ Report generation failed: {report_data['error']}", file=sys.stderr)
        sys.exit(1)

    # Format as markdown
    markdown = format_markdown_report(report_data)

    # Save files
    stamp = datetime.now().strftime('%F')
    report_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
    os.makedirs(report_dir, exist_ok=True)

    md_path = os.path.join(report_dir, f'cn_daily_digest_async_{stamp}.md')
    json_path = os.path.join(report_dir, f'cn_market_data_async_{stamp}.json')

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print("", file=sys.stderr)
    print("✅ Report generation complete!", file=sys.stderr)
    print(f"📄 Markdown: {md_path}", file=sys.stderr)
    print(f"📊 JSON: {json_path}", file=sys.stderr)

    # Print performance summary
    perf = report_data.get('performance', {})
    print("", file=sys.stderr)
    print("📈 Performance Summary:", file=sys.stderr)
    print(f"   Total time: {perf.get('total_time_parallel_ms', 0):.0f}ms", file=sys.stderr)
    print(f"   Success rate: {perf.get('success_rate', 0):.1%}", file=sys.stderr)
    print(f"   Cache hit rate: {perf.get('cache_hit_rate', 0):.1%}", file=sys.stderr)
    print(f"   Sources: {perf.get('successful', 0)}/{perf.get('total_sources', 0)}", file=sys.stderr)

    # Output result paths as JSON for integration
    print(json.dumps({
        'markdown': md_path,
        'json': json_path,
        'performance': perf
    }, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
