#!/usr/bin/env python3
import os, json, datetime, subprocess, sys

WS = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
REPORT_DIR = os.path.join(WS, 'reports')
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DEFAULT_TICKERS = ['510300','600519','000001','HK.00700']

def run_json(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    p.check_returncode()
    return json.loads(p.stdout)

def main():
    os.makedirs(REPORT_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%F')

    # Fetch CN hotlists (东方财富)
    hot = run_json([sys.executable, os.path.join(SKILL_DIR,'scripts','cn_market_rankings.py')])

    # Watchlist quotes (新浪财经)
    tickers = DEFAULT_TICKERS
    wl = run_json([sys.executable, os.path.join(SKILL_DIR,'scripts','cn_stock_quotes.py'), *tickers])

    # Fetch CLS news (财联社)
    try:
        cls = run_json([sys.executable, os.path.join(SKILL_DIR,'scripts','cn_cls_telegraph.py')])
    except:
        cls = {'telegraph': [], 'depth': []}

    # Fetch Tencent Finance (腾讯财经)
    try:
        tencent = run_json([sys.executable, os.path.join(SKILL_DIR,'scripts','cn_tencent_moneyflow.py')])
    except:
        tencent = {'hot_stocks': [], 'concept_plates': [], 'money_flow': {'top_inflow': [], 'top_outflow': []}}

    # Fetch 10jqka data (同花顺)
    try:
        jqka = run_json([sys.executable, os.path.join(SKILL_DIR,'scripts','cn_ths_diagnosis.py')])
    except:
        jqka = {'hot_stocks': [], 'industry_ranking': []}

    # Save JSON attachments
    hot_json = os.path.join(REPORT_DIR, f'cn_hot_{stamp}.json')
    wl_json = os.path.join(REPORT_DIR, f'cn_watchlist_{stamp}.json')
    cls_json = os.path.join(REPORT_DIR, f'cn_cls_{stamp}.json')
    tencent_json = os.path.join(REPORT_DIR, f'cn_tencent_{stamp}.json')
    jqka_json = os.path.join(REPORT_DIR, f'cn_10jqka_{stamp}.json')

    with open(hot_json, 'w', encoding='utf-8') as f:
        json.dump(hot, f, ensure_ascii=False, indent=2)
    with open(wl_json, 'w', encoding='utf-8') as f:
        json.dump(wl, f, ensure_ascii=False, indent=2)
    with open(cls_json, 'w', encoding='utf-8') as f:
        json.dump(cls, f, ensure_ascii=False, indent=2)
    with open(tencent_json, 'w', encoding='utf-8') as f:
        json.dump(tencent, f, ensure_ascii=False, indent=2)
    with open(jqka_json, 'w', encoding='utf-8') as f:
        json.dump(jqka, f, ensure_ascii=False, indent=2)

    # Build Chinese markdown digest
    md_path = os.path.join(REPORT_DIR, f'cn_daily_digest_{stamp}.md')
    lines = []
    lines.append(f'# 每日中文市场简报（A/HK） - {stamp}')
    lines.append('')
    lines.append('生成时间：' + datetime.datetime.now().strftime('%F %T %Z'))

    # Watchlist
    lines.append('## 观察清单（实时快照）')
    for q in wl.get('quotes', []):
        name = q.get('name') or q.get('symbol')
        price = q.get('price')
        pct = q.get('pct')
        lines.append(f'- {name}: {price} ({pct}%)')

    # A 股榜单
    lines.append('')
    lines.append('## A 股榜单')
    lines.append('### 涨幅榜（Top 20）')
    for it in hot['a_share']['top_gainers'][:20]:
        lines.append(f"- {it['name']}({it['code']}): {it['pct']}%  现价:{it['price']} 成交额:{it['amount']}")
    lines.append('### 成交额榜（Top 20）')
    for it in hot['a_share']['top_amount'][:20]:
        lines.append(f"- {it['name']}({it['code']}): 成交额:{it['amount']}  涨幅:{it['pct']}% 现价:{it['price']}")

    # 港股榜单
    lines.append('')
    lines.append('## 港股榜单（若接口异常将留空）')
    if hot['hong_kong']['top_gainers']:
        lines.append('### 涨幅榜（Top 20）')
        for it in hot['hong_kong']['top_gainers'][:20]:
            lines.append(f"- {it['name']}({it['code']}): {it['pct']}%  现价:{it['price']} 成交额:{it['amount']}")
    if hot['hong_kong']['top_amount']:
        lines.append('### 成交额榜（Top 20）')
        for it in hot['hong_kong']['top_amount'][:20]:
            lines.append(f"- {it['name']}({it['code']}): 成交额:{it['amount']}  涨幅:{it['pct']}% 现价:{it['price']}")

    # 财联社快讯 (CLS)
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

    # 腾讯财经 - 资金流向
    lines.append('')
    lines.append('## 资金流向 (腾讯财经)')
    if tencent.get('money_flow', {}).get('top_inflow'):
        lines.append('### 主力净流入 Top 5')
        for item in tencent['money_flow']['top_inflow'][:5]:
            lines.append(f"- {item.get('name')}({item.get('code')}): 净流入 {item.get('net_inflow', 0):.2f}万 涨幅:{item.get('pct', 0):.2f}%")

    if tencent.get('money_flow', {}).get('top_outflow'):
        lines.append('### 主力净流出 Top 5')
        for item in tencent['money_flow']['top_outflow'][:5]:
            lines.append(f"- {item.get('name')}({item.get('code')}): 净流出 {abs(item.get('net_inflow', 0)):.2f}万 涨幅:{item.get('pct', 0):.2f}%")

    # 同花顺 - 行业排行
    lines.append('')
    lines.append('## 行业板块 (同花顺)')
    if jqka.get('industry_ranking'):
        for item in jqka['industry_ranking'][:10]:
            lines.append(f"- {item.get('name')}: {item.get('pct', 0):.2f}%")
    else:
        lines.append('- 同花顺数据获取失败或无数据')

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(json.dumps({
        'digest_md': md_path,
        'hot_json': hot_json,
        'watchlist_json': wl_json,
        'cls_json': cls_json,
        'tencent_json': tencent_json,
        'jqka_json': jqka_json,
        'data_sources': {
            'eastmoney': '东方财富 (热榜)',
            'sina': '新浪财经 (行情)',
            'cls': '财联社 (快讯)',
            'tencent': '腾讯财经 (资金流)',
            '10jqka': '同花顺 (行业)'
        }
    }, ensure_ascii=False))

if __name__ == '__main__':
    main()
