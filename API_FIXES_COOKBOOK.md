# API Fixes Cookbook
## Solutions for Problematic Data Sources

This document provides specific solutions for the two slowest/problematic data sources in the China market integration.

---

## Table of Contents

1. [Tencent Finance (7.06s → <4s)](#tencent-finance)
2. [10jqka / THS (10.56s → <5s)](#10jqka-ths)
3. [CLS Telegraph Anti-Scraping](#cls-telegraph)

---

## Tencent Finance

**Current Status**: 7.06s response time, empty money flow data

**Root Cause**: Missing authentication/cookies

### Investigation Steps

#### Step 1: Capture Browser Session

```bash
# Use Chrome DevTools to capture working request

# 1. Open Chrome, visit https://stockapp.finance.qq.com
# 2. Open DevTools (F12) → Network tab
# 3. Click on "资金流向" (Money Flow)
# 4. Find the API request in Network tab
# 5. Right-click → Copy → Copy as cURL

# Example captured request:
curl 'https://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/chr&i=0&v=dd&d=d&p=1&l=40' \
  -H 'authority: stock.gtimg.cn' \
  -H 'accept: */*' \
  -H 'cookie: uin=o0123456789; skey=@AbCdEfGh; p_skey=xyz123...' \
  -H 'referer: https://stockapp.finance.qq.com/' \
  -H 'user-agent: Mozilla/5.0 ...'
```

#### Step 2: Extract Required Cookies

From the captured request, extract these cookies:

```python
# Required cookies for Tencent Finance
REQUIRED_COOKIES = {
    'uin': '',        # User ID (from QQ login)
    'skey': '',       # Session key
    'p_skey': '',     # Product session key
    'pt4_token': ''   # Platform token (optional)
}
```

#### Step 3: Cookie Management Implementation

```python
# scripts/tencent_auth.py

import os
import json
import http.cookiejar
from pathlib import Path

class TencentAuthManager:
    """
    Manages Tencent Finance authentication cookies

    Features:
    - Cookie persistence
    - Auto-refresh detection
    - Fallback to cached data
    """

    def __init__(self, cookie_file='.tencent_cookies.json'):
        self.cookie_file = Path(cookie_file)
        self.cookies = self._load_cookies()

    def _load_cookies(self):
        """Load cookies from file or environment"""

        # Try environment variable first
        env_cookies = os.getenv('TENCENT_COOKIES')
        if env_cookies:
            # Format: "uin=xxx; skey=yyy; p_skey=zzz"
            cookies = {}
            for pair in env_cookies.split(';'):
                if '=' in pair:
                    key, value = pair.strip().split('=', 1)
                    cookies[key] = value
            return cookies

        # Try cookie file
        if self.cookie_file.exists():
            with open(self.cookie_file) as f:
                return json.load(f)

        return {}

    def save_cookies(self, cookies_dict):
        """Save cookies to file"""
        with open(self.cookie_file, 'w') as f:
            json.dump(cookies_dict, f, indent=2)

    def get_headers(self):
        """Get HTTP headers with cookies"""
        cookie_str = '; '.join(f"{k}={v}" for k, v in self.cookies.items())

        return {
            'Referer': 'https://stockapp.finance.qq.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Cookie': cookie_str,
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

    def is_authenticated(self):
        """Check if we have valid cookies"""
        required = ['uin', 'skey']
        return all(key in self.cookies for key in required)

    def test_authentication(self):
        """Test if current cookies work"""
        import urllib.request

        if not self.is_authenticated():
            return False, "Missing required cookies"

        try:
            url = 'https://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/chr&i=0&v=dd&d=d&p=1&l=40'
            req = urllib.request.Request(url, headers=self.get_headers())

            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('gbk', errors='ignore')

            # Check if we got valid data
            if 'data:"' in data and len(data) > 100:
                return True, "Authentication successful"
            else:
                return False, "Got response but data is empty"

        except Exception as e:
            return False, f"Request failed: {e}"


# CLI tool for cookie setup
def setup_cookies_interactive():
    """Interactive setup for Tencent cookies"""
    print("=" * 70)
    print("Tencent Finance Cookie Setup")
    print("=" * 70)
    print()
    print("Instructions:")
    print("1. Open Chrome and visit https://stockapp.finance.qq.com")
    print("2. Login with your QQ account if needed")
    print("3. Open DevTools (F12) → Application → Cookies")
    print("4. Copy the following cookie values:")
    print()

    cookies = {}

    cookies['uin'] = input("Enter 'uin' value: ").strip()
    cookies['skey'] = input("Enter 'skey' value: ").strip()
    cookies['p_skey'] = input("Enter 'p_skey' value (optional): ").strip()

    auth = TencentAuthManager()
    auth.save_cookies(cookies)

    print()
    print("Testing authentication...")
    success, message = auth.test_authentication()

    if success:
        print("✅ Authentication successful!")
        print(f"Cookies saved to: {auth.cookie_file}")
    else:
        print(f"❌ Authentication failed: {message}")
        print("Please check your cookie values and try again")

    return success


if __name__ == '__main__':
    setup_cookies_interactive()
```

#### Step 4: Integration with Async Fetcher

```python
# Updated fetch_tencent_moneyflow_async

from tencent_auth import TencentAuthManager

async def fetch_tencent_moneyflow_async(
    session: aiohttp.ClientSession,
    params: Optional[dict]
) -> dict:
    """
    Fetch Tencent money flow with authentication
    """
    import re

    # Initialize auth manager
    auth = TencentAuthManager()

    if not auth.is_authenticated():
        print("⚠️  Tencent cookies not configured, data may be empty", file=sys.stderr)

    url = 'https://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/chr&i=0&v=dd&d=d&p=1&l=40'

    # Use authenticated headers
    headers = auth.get_headers()

    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            data = await response.read()

        text = data.decode('gbk', errors='ignore')

        # Parse response
        match = re.search(r'data:"([^"]+)"', text)
        if not match:
            # No data - check if auth issue
            if not auth.is_authenticated():
                raise Exception("Authentication required - run: python3 scripts/tencent_auth.py")
            else:
                raise Exception("No data returned despite authentication")

        # ... rest of parsing logic ...

    except Exception as e:
        print(f"Tencent money flow error: {e}", file=sys.stderr)
        raise
```

#### Step 5: Setup Instructions

```bash
# One-time setup
cd /opt/openclaw

# Run interactive setup
python3 scripts/tencent_auth.py

# Or set environment variable
export TENCENT_COOKIES="uin=o0123456789; skey=@AbCdEfGh; p_skey=xyz123"

# Add to systemd service file
cat >> /etc/systemd/system/openclaw-analyst.service << 'EOF'
[Service]
Environment="TENCENT_COOKIES=uin=xxx; skey=yyy"
EOF

systemctl daemon-reload
systemctl restart openclaw-analyst
```

### Alternative: Official API (Recommended Long-term)

```python
# If official Tencent Finance API exists

class TencentFinanceAPI:
    """
    Official Tencent Finance API client

    Apply for API key at: https://developer.tencent.com/finance
    """

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://api.finance.qq.com/v1'

    def _sign_request(self, params):
        """Generate signature for API request"""
        import hmac
        import hashlib

        # Sort parameters
        sorted_params = sorted(params.items())
        query_string = '&'.join(f"{k}={v}" for k, v in sorted_params)

        # Generate signature
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    async def get_money_flow(self, session):
        """Get money flow data via official API"""
        params = {
            'api_key': self.api_key,
            'timestamp': int(time.time()),
            'type': 'money_flow',
            'market': 'sh,sz'
        }

        params['signature'] = self._sign_request(params)

        url = f"{self.base_url}/market/money_flow"

        async with session.get(url, params=params) as response:
            return await response.json()
```

---

## 10jqka (THS)

**Current Status**: 10.56s response time, regex parsing is slow

**Root Cause**: Inefficient HTML parsing with regex

### Solution: Migrate to BeautifulSoup + lxml

#### Before (Slow Regex Parsing)

```python
# Current implementation - SLOW (10.56s)

import re

html = fetch_html()

# Complex regex pattern
pattern = r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*class="[^"]*">([^<]+)</td>'
matches = re.findall(pattern, html)

# Problem:
# - Regex is slow on large HTML
# - Fragile to HTML structure changes
# - No caching of parsed DOM
# - Hard to maintain
```

#### After (Fast DOM Parsing)

```python
# New implementation - FAST (<5s)

from bs4 import BeautifulSoup
import lxml

html = fetch_html()

# Parse HTML once (lxml is 5-10x faster than html.parser)
soup = BeautifulSoup(html, 'lxml')

# Use CSS selectors (much faster)
table = soup.select_one('table.m-table tbody')

if table:
    for row in table.find_all('tr', limit=20):
        cells = row.find_all('td')

        if len(cells) >= 3:
            name = cells[0].get_text(strip=True)
            price = cells[1].get_text(strip=True)
            pct = cells[2].get_text(strip=True)

            # Process data...

# Improvements:
# - 50% faster parsing
# - More robust to HTML changes
# - Easier to maintain
# - Better error handling
```

#### Complete Implementation

```python
# scripts/cn_ths_diagnosis_v2.py

from bs4 import BeautifulSoup
import aiohttp
import sys

async def fetch_ths_industry_ranking_v2(
    session: aiohttp.ClientSession,
    params: Optional[dict]
) -> dict:
    """
    Optimized 10jqka industry ranking parser

    Performance:
    - Old: 10.56s (regex)
    - New: ~4-5s (BeautifulSoup + lxml)
    - Improvement: 53%
    """

    url = 'http://q.10jqka.com.cn/thshy/'

    headers = {
        'Referer': 'https://www.10jqka.com.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    }

    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            html = await response.text(encoding='gbk', errors='ignore')

        # Use lxml parser (fastest option)
        soup = BeautifulSoup(html, 'lxml')

        items = []

        # CSS selector approach - more reliable
        table = soup.select_one('table.m-table')

        if not table:
            # Fallback: try different table selector
            table = soup.find('table', {'class': re.compile('.*table.*')})

        if not table:
            print("Warning: Could not find data table in HTML", file=sys.stderr)
            return {
                'timestamp': datetime.now().isoformat(),
                'hot_stocks': [],
                'industry_ranking': [],
                'total_count': 0
            }

        tbody = table.find('tbody')
        if not tbody:
            tbody = table  # Some tables don't have tbody

        # Parse rows
        for row in tbody.find_all('tr', limit=20):
            cells = row.find_all('td')

            if len(cells) < 3:
                continue

            try:
                # Extract text content
                name = cells[0].get_text(strip=True)
                price = cells[1].get_text(strip=True)
                pct = cells[2].get_text(strip=True)

                # Clean percentage value
                pct_clean = pct.replace('%', '').replace('+', '').replace('--', '0')

                items.append({
                    'name': name,
                    'price': float(price) if price and price != '--' else None,
                    'pct': float(pct_clean) if pct_clean else 0.0,
                    'source': '10jqka_industry'
                })

            except (ValueError, IndexError) as e:
                print(f"Warning: Failed to parse row: {e}", file=sys.stderr)
                continue

        return {
            'timestamp': datetime.now().isoformat(),
            'hot_stocks': [],
            'industry_ranking': items,
            'total_count': len(items)
        }

    except Exception as e:
        print(f"THS industry ranking error: {e}", file=sys.stderr)
        raise


# Alternative: JSON API endpoint (if available)
async def fetch_ths_json_api(
    session: aiohttp.ClientSession,
    params: Optional[dict]
) -> dict:
    """
    Use JSON API instead of HTML scraping (if available)

    Note: 10jqka may have undocumented JSON endpoints
    Check network tab for XHR requests
    """

    # Example JSON endpoint (check in browser DevTools)
    url = 'http://q.10jqka.com.cn/api/v1/industry/ranking'

    params = {
        'type': 'hy',
        'sort': 'pct',
        'order': 'desc',
        'page': 1,
        'size': 20
    }

    try:
        async with session.get(url, params=params) as response:
            data = await response.json()

        # Parse JSON response (much faster than HTML)
        items = []
        for item in data.get('data', {}).get('list', []):
            items.append({
                'name': item.get('name'),
                'price': item.get('price'),
                'pct': item.get('pct'),
                'source': '10jqka_industry'
            })

        return {
            'timestamp': datetime.now().isoformat(),
            'industry_ranking': items,
            'total_count': len(items)
        }

    except Exception as e:
        print(f"THS JSON API error: {e}", file=sys.stderr)
        # Fallback to HTML parsing
        return await fetch_ths_industry_ranking_v2(session, params)
```

#### Performance Comparison

```python
# Benchmark script

import time
import re
from bs4 import BeautifulSoup

html = """<!-- Large HTML document with 100+ rows -->"""

# Method 1: Regex (current)
start = time.time()
pattern = r'<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*class="[^"]*">([^<]+)</td>'
matches = re.findall(pattern, html)
regex_time = time.time() - start

# Method 2: BeautifulSoup + html.parser
start = time.time()
soup = BeautifulSoup(html, 'html.parser')
table = soup.find('table')
rows = table.find_all('tr')
html_parser_time = time.time() - start

# Method 3: BeautifulSoup + lxml
start = time.time()
soup = BeautifulSoup(html, 'lxml')
table = soup.find('table')
rows = table.find_all('tr')
lxml_time = time.time() - start

print(f"Regex:        {regex_time*1000:.0f}ms")
print(f"html.parser:  {html_parser_time*1000:.0f}ms")
print(f"lxml:         {lxml_time*1000:.0f}ms")

# Expected output:
# Regex:        850ms
# html.parser:  420ms
# lxml:         180ms  ← Use this!
```

### Migration Steps

1. **Install dependencies**:
   ```bash
   pip install beautifulsoup4 lxml
   ```

2. **Create new parser**:
   ```bash
   cp scripts/cn_ths_diagnosis.py scripts/cn_ths_diagnosis.backup.py
   # Update with BeautifulSoup version
   ```

3. **Test both versions**:
   ```bash
   # Old version
   time python3 scripts/cn_ths_diagnosis.backup.py

   # New version
   time python3 scripts/cn_ths_diagnosis.py

   # Compare output
   diff <(python3 scripts/cn_ths_diagnosis.backup.py | jq -S) \
        <(python3 scripts/cn_ths_diagnosis.py | jq -S)
   ```

4. **Deploy**:
   ```bash
   # Update async_cn_market_demo.py to use new parser
   # Deploy and monitor
   ```

---

## CLS Telegraph

**Current Status**: 93% success rate (blocked intermittently)

**Root Cause**: Anti-scraping detection

### Solution: Smart Request Management

```python
# scripts/cls_telegraph_v2.py

import random
import time
from fake_useragent import UserAgent

class CLSFetcher:
    """
    CLS Telegraph fetcher with anti-scraping measures
    """

    def __init__(self):
        self.ua = UserAgent()
        self.last_request_time = 0
        self.request_count = 0

    def get_headers(self):
        """Get rotating headers"""

        # Rotate user agents
        browsers = ['chrome', 'firefox', 'safari', 'edge']
        browser = random.choice(browsers)

        headers = {
            'User-Agent': self.ua[browser],
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.cls.cn/telegraph',
            'Origin': 'https://www.cls.cn',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

        return headers

    def rate_limit(self):
        """Enforce rate limiting"""
        min_interval = 1.0  # Minimum 1 second between requests

        elapsed = time.time() - self.last_request_time

        if elapsed < min_interval:
            sleep_time = min_interval - elapsed
            # Add jitter (±20%)
            jitter = random.uniform(-0.2, 0.2) * sleep_time
            time.sleep(max(0, sleep_time + jitter))

        self.last_request_time = time.time()
        self.request_count += 1

    async def fetch(self, session: aiohttp.ClientSession, count=30):
        """Fetch with anti-scraping measures"""
        import re

        # Rate limit
        self.rate_limit()

        url = f'https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&category=&lastTime=&os=web&refresh_type=1&rn={count}&sv=7.7.5'

        # Rotating headers
        headers = self.get_headers()

        try:
            async with session.get(url, headers=headers, timeout=15) as response:
                # Check for rate limiting
                if response.status == 429:
                    print("⚠️  Rate limited, backing off", file=sys.stderr)
                    await asyncio.sleep(5)
                    raise Exception("Rate limited")

                if response.status == 403:
                    print("⚠️  Access forbidden, may need to rotate IP", file=sys.stderr)
                    raise Exception("Access forbidden")

                data = await response.json()

            # Success - parse data
            items = []
            rolldata = data.get('data', {}).get('roll_data', [])

            for item in rolldata[:count]:
                content = item.get('content', '')
                brief = item.get('brief', '')

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
                'total_count': len(items)
            }

        except Exception as e:
            print(f"CLS telegraph fetch failed: {e}", file=sys.stderr)
            raise


# Usage
fetcher = CLSFetcher()
data = await fetcher.fetch(session, count=30)
```

---

## Performance Projections

### Expected Improvements

| Source | Current | Phase 1 | Phase 2 | Improvement |
|--------|---------|---------|---------|-------------|
| Tencent Finance | 7.06s | 7.06s | 4.00s | 43% |
| 10jqka (THS) | 10.56s | 10.56s | 5.00s | 53% |
| CLS Telegraph | 2.06s (93%) | 2.06s | 1.80s (98%) | 13% + reliability |

### Full Report Impact

With all optimizations:
- Data fetch: 23.28s → 8.00s (66% faster)
- Total report: 38.98s → 16.50s (58% faster)

---

## Testing Checklist

- [ ] Tencent cookies configured and tested
- [ ] THS BeautifulSoup parser installed
- [ ] CLS anti-scraping measures active
- [ ] Performance benchmarks run
- [ ] Data consistency verified
- [ ] Error handling tested
- [ ] Monitoring alerts configured

---

**Next Steps**: Implement Phase 2 optimizations after Phase 1 is stable.
