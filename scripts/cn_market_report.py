#!/usr/bin/env python3
import os, json, datetime, subprocess, sys
import argparse

SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPORT_DIR = os.path.join(SKILL_DIR, 'reports')
WS = SKILL_DIR

DEFAULT_TICKERS = ['510300','600519','000001','HK.00700']

# Load environment configuration
from dotenv import load_dotenv
load_dotenv(os.path.join(SKILL_DIR, '.env.cn_market'), override=False)

def run_json(cmd):
    # Validate script exists before running
    if len(cmd) > 1 and not os.path.exists(cmd[1]):
        raise FileNotFoundError(f"Script not found: {cmd[1]}")
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        print(f"Error running {cmd}: stderr={p.stderr}", file=sys.stderr)
    p.check_returncode()
    return json.loads(p.stdout)

def main_async():
    """Async version using parallel data fetching (v1.1.0)"""
    async_demo_script = os.path.join(SKILL_DIR, 'scripts', 'async_cn_market_demo.py')

    if not os.path.exists(async_demo_script):
        print(f"Warning: Async demo script not found, falling back to sync mode", file=sys.stderr)
        return main_sync()

    # Run async demo script
    result = subprocess.run([sys.executable, async_demo_script],
                          capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        print(f"Error running async script: {result.stderr}", file=sys.stderr)
        print("Falling back to sync mode", file=sys.stderr)
        return main_sync()

    # Parse and return result
    try:
        output_lines = result.stdout.strip().split('\n')
        # Last line should be JSON output
        json_output = json.loads(output_lines[-1])
        print(json.dumps(json_output, ensure_ascii=False))
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Error parsing async output: {e}", file=sys.stderr)
        print("Falling back to sync mode", file=sys.stderr)
        return main_sync()

def main_sync():
    """Original synchronous version (v1.0.1)"""
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

def _generate_brief_summary(report_path):
    """生成精简简报"""
    import re
    from datetime import datetime

    if not os.path.exists(report_path):
        return None

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        # 提取A股数据
        a_gainers = re.findall(r'### 涨幅榜（Top 20）\n((?:- .*?\n){20})', content)
        if not a_gainers:
            return None

        a_top3_gain = re.findall(r'- (.*?)\(.*?\): ([-\d.]+)%', a_gainers[0])[:3]

        a_volumes = re.findall(r'### 成交额榜（Top 20）\n((?:- .*?\n){20})', content)
        a_vol_data = re.findall(r'- (.*?)\(.*?\): 成交额:([\d.]+).*?涨幅:([-\d.]+)%', a_volumes[0]) if a_volumes else []
        a_top3_vol = a_vol_data[:3] if a_vol_data else []
        a_losers = sorted([x for x in a_vol_data if float(x[2]) < 0], key=lambda x: float(x[2]))[:3] if a_vol_data else []

        # 提取港股数据
        hk_section = re.findall(r'## 港股榜单.*?### 涨幅榜（Top 20）\n((?:- .*?\n){20})', content, re.DOTALL)
        hk_data = re.findall(r'- (.*?)\(.*?\): ([-\d.]+)%.*?成交额:([\d.]+)', hk_section[0]) if hk_section else []
        hk_top3_gain = hk_data[:3] if hk_data else []
        hk_top3_vol = sorted(hk_data, key=lambda x: float(x[2]), reverse=True)[:3] if hk_data else []

        # 格式化输出
        time_str = datetime.now().strftime("%H:%M")
        brief = f"📊 {time_str} 市场快报\n\n【A股】"

        if a_top3_gain:
            brief += f"涨:{a_top3_gain[0][0][:5]}+{a_top3_gain[0][1]}% "
        if a_losers:
            brief += f"跌:{a_losers[0][0][:5]}{a_losers[0][2]}% "
        if a_top3_vol:
            brief += f"额:{a_top3_vol[0][0][:5]}{float(a_top3_vol[0][1])/1e8:.0f}亿"

        brief += "\n【港股】"
        if hk_top3_gain:
            brief += f"涨:{hk_top3_gain[0][0][:7]}+{hk_top3_gain[0][1]}% "
        if hk_top3_vol:
            brief += f"额:{hk_top3_vol[0][0][:5]}{float(hk_top3_vol[0][2])/1e8:.0f}亿"

        return brief
    except Exception as e:
        print(f"⚠️ Brief summary generation failed: {e}", file=sys.stderr)
        return None


def main():
    """Entry point - selects async or sync mode based on configuration"""
    parser = argparse.ArgumentParser(description='Generate China market daily report')
    parser.add_argument('--async', dest='use_async', action='store_true',
                       help='Use async mode for parallel data fetching (v1.1.0)')
    parser.add_argument('--sync', dest='use_async', action='store_false',
                       help='Use sync mode (legacy v1.0.1)')
    parser.add_argument('--push', action='store_true',
                       help='Push brief summary to Feishu after generation')
    parser.add_argument('--brief', action='store_true',
                       help='Output brief summary (≤120 chars)')
    parser.set_defaults(use_async=None)

    args = parser.parse_args()

    # Determine mode: CLI arg > environment variable > default (false)
    if args.use_async is not None:
        use_async = args.use_async
    else:
        use_async = os.getenv('CN_MARKET_USE_ASYNC', 'false').lower() in ('true', '1', 'yes')

    # Suppress JSON output if only brief mode
    if args.brief and not args.push:
        # Redirect stdout temporarily for report generation
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

    try:
        if use_async:
            print("🚀 Using async mode (v1.1.0)", file=sys.stderr)
            main_async()
        else:
            print("⏱️  Using sync mode (v1.0.1)", file=sys.stderr)
            main_sync()
    finally:
        if args.brief and not args.push:
            # Restore stdout
            sys.stdout = old_stdout

    # Handle push and brief options
    if args.push or args.brief:
        from datetime import datetime
        report_file = os.path.join(SKILL_DIR, "reports",
                                   f"cn_daily_digest_{'async' if use_async else 'sync'}_{datetime.now().strftime('%Y-%m-%d')}.md")

        brief = _generate_brief_summary(report_file)

        if brief:
            # Save brief to file
            if args.brief:
                brief_filename = f"cn_market_brief_{datetime.now().strftime('%Y-%m-%d_%H%M')}.txt"
                brief_path = os.path.join(SKILL_DIR, "reports", brief_filename)

                with open(brief_path, 'w', encoding='utf-8') as f:
                    f.write(brief)
                    f.write(f"\n\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"报告来源: {os.path.basename(report_file)}\n")

                # Print brief (stdout only, no JSON)
                print(f"\n{brief}", file=sys.stdout)
                print(f"\n✅ 精简简报已保存: {brief_path}", file=sys.stderr)

            if args.push:
                try:
                    sys.path.insert(0, os.path.join(SKILL_DIR, 'scripts'))
                    from feishu_push import FeishuPusher

                    pusher = FeishuPusher()
                    pusher.push(brief)
                except ImportError:
                    print("⚠️ feishu_push module not found, skipping push", file=sys.stderr)
                except Exception as e:
                    print(f"⚠️ Feishu push failed: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
