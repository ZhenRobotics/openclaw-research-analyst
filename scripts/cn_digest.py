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

    # Fetch CN hotlists
    hot = run_json([sys.executable, os.path.join(SKILL_DIR,'scripts','cn_hotlists.py')])

    # Watchlist quotes
    tickers = DEFAULT_TICKERS
    wl = run_json([sys.executable, os.path.join(SKILL_DIR,'scripts','cn_watchlist.py'), *tickers])

    # Save JSON attachments
    hot_json = os.path.join(REPORT_DIR, f'cn_hot_{stamp}.json')
    wl_json = os.path.join(REPORT_DIR, f'cn_watchlist_{stamp}.json')
    with open(hot_json, 'w', encoding='utf-8') as f:
        json.dump(hot, f, ensure_ascii=False, indent=2)
    with open(wl_json, 'w', encoding='utf-8') as f:
        json.dump(wl, f, ensure_ascii=False, indent=2)

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

    # 占位：公告 / 研报 / 资金流 / 板块概念（后续补充）
    lines.append('')
    lines.append('## 公告 / 研报 / 资金流 / 板块概念')
    lines.append('- 首版占位：将于下一版接入东方财富/新浪接口，输出中文要点与 JSON 附件')

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(json.dumps({
        'digest_md': md_path,
        'hot_json': hot_json,
        'watchlist_json': wl_json
    }, ensure_ascii=False))

if __name__ == '__main__':
    main()
