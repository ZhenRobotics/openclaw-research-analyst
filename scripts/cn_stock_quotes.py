#!/usr/bin/env python3
import sys, json, urllib.request

# Map plain tickers to Sina format
# A-share: sh/sz + 6-digit; HK: hk + 5-digit zero-padded

def to_sina_code(t):
    t = t.strip().upper()
    if t.startswith('HK.'):
        return 'hk' + t.split('.',1)[1].zfill(5)
    # assume digits => A-share, decide sh/sz by leading digit
    if t.isdigit() and len(t) == 6:
        return ('sh' if t.startswith(('5','6')) else 'sz') + t
    return t  # fallback


def fetch_quotes(codes):
    url = 'https://hq.sinajs.cn/list=' + ','.join(codes)
    req = urllib.request.Request(url, headers={
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0'
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        data = r.read()  # GBK bytes
    text = data.decode('gbk', errors='ignore')
    out = []
    for line in text.strip().split('\n'):
        # var hq_str_sh600519="贵州茅台,1680.00,1679.50,1683.88,1699.88,1663.00, ...";
        if '="' not in line:
            continue
        head, rest = line.split('="', 1)
        name = head.split('_')[-1]
        fields = rest.rstrip('";').split(',')
        if len(fields) < 4:
            continue
        symbol = head.split('str_')[-1]
        out.append({
            'symbol': symbol,
            'name': fields[0],
            'price': try_float(fields[3]),
            'prev_close': try_float(fields[2]),
            'open': try_float(fields[1]),
        })
    return out


def try_float(x):
    try:
        return float(x)
    except Exception:
        return None


def main():
    tickers = sys.argv[1:] or ['510300','600519','000001','HK.00700']
    codes = [to_sina_code(t) for t in tickers]
    quotes = fetch_quotes(codes)
    # enrich with pct
    for q in quotes:
        if q.get('price') and q.get('prev_close') and q['prev_close']:
            q['pct'] = round((q['price'] / q['prev_close'] - 1) * 100, 2)
        else:
            q['pct'] = None
    print(json.dumps({'tickers': tickers, 'quotes': quotes}, ensure_ascii=False))

if __name__ == '__main__':
    main()
