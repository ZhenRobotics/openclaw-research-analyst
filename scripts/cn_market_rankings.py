#!/usr/bin/env python3
import json, urllib.request, urllib.parse

BASE = 'https://push2.eastmoney.com/api/qt/clist/get'
HEADERS = {
    'Referer': 'https://quote.eastmoney.com/center/gridlist.html',
    'User-Agent': 'Mozilla/5.0'
}

# Common fields: f12=代码 f14=名称 f2=最新价 f3=涨跌幅% f6=成交额
FIELDS = 'f12,f14,f2,f3,f6'

def fetch_list(fs, fid='f3', pn=1, pz=20):
    params = {
        'pn': pn,
        'pz': pz,
        'po': 1,
        'np': 1,
        'fltt': 2,
        'invt': 2,
        'fid': fid,  # sort field
        'fs': fs,
        'fields': FIELDS
    }
    url = BASE + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode('utf-8', 'ignore'))
    items = (data.get('data') or {}).get('diff') or []
    out = []
    for it in items:
        out.append({
            'code': it.get('f12'),
            'name': it.get('f14'),
            'price': it.get('f2'),
            'pct': it.get('f3'),
            'amount': it.get('f6'),
        })
    return out


def main():
    # A股：沪深A（上/深）：fs=m:1 t:2,m:1 t:23
    a_fs = 'm:1 t:2,m:1 t:23'
    a_top_gainers = fetch_list(a_fs, fid='f3', pz=20)
    a_top_amount = fetch_list(a_fs, fid='f6', pz=20)

    # 港股（主板）：常用 fs=m:116 t:3（主板），创业板 t:4；这里聚合主板+创业板
    hk_fs = 'm:116 t:3,m:116 t:4'
    try:
        hk_top_gainers = fetch_list(hk_fs, fid='f3', pz=20)
        hk_top_amount = fetch_list(hk_fs, fid='f6', pz=20)
    except Exception:
        hk_top_gainers, hk_top_amount = [], []

    print(json.dumps({
        'a_share': {
            'top_gainers': a_top_gainers,
            'top_amount': a_top_amount,
        },
        'hong_kong': {
            'top_gainers': hk_top_gainers,
            'top_amount': hk_top_amount,
        }
    }, ensure_ascii=False))

if __name__ == '__main__':
    main()
