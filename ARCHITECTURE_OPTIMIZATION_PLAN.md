# OpenClaw Research Analyst - China Market Architecture Optimization Plan
## Version 1.1 - Performance & Reliability Enhancement

**Document Date**: 2026-03-18
**Author**: Backend Architect
**Target Version**: v1.1.0 - v1.2.0
**Status**: Design Phase

---

## Executive Summary

This document provides a comprehensive architecture optimization plan to reduce China market report generation time from **38.98s to <20s** (49% improvement) while maintaining 100% network reliability and adding intelligent caching, anti-scraping countermeasures, and graceful degradation capabilities.

### Key Performance Targets

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| Total Report Time | 38.98s | <20s | Async parallel fetching |
| Sina Finance | 1.11s | <1s | Already optimal |
| Eastmoney | 2.49s | <2s | Already optimal |
| CLS Telegraph | 2.06s | <2s | Anti-scraping + retry |
| Tencent Finance | 7.06s | <4s | Auth automation + cache |
| 10jqka (THS) | 10.56s | <5s | Parser optimization + cache |
| Cache Hit Rate | 0% | 60-80% | Redis/diskcache |
| Network Success | 100% | 100% | Enhanced retry + fallback |

---

## Part 1: Current Architecture Analysis

### 1.1 Architecture Pattern Assessment

**Current State**: Synchronous Sequential Architecture

```
Main Process (cn_market_report.py)
    ├── subprocess.run(cn_market_rankings.py)      [2.49s] ✅
    ├── subprocess.run(cn_stock_quotes.py)         [1.11s] ✅
    ├── subprocess.run(cn_cls_telegraph.py)        [2.06s] ⚠️
    ├── subprocess.run(cn_tencent_moneyflow.py)    [7.06s] ⚠️
    └── subprocess.run(cn_ths_diagnosis.py)        [10.56s] ⚠️

Total Sequential Time: 23.28s (data fetch only)
Additional Time: ~15.7s (JSON I/O, parsing, markdown generation)
```

**Critical Bottlenecks Identified**:

1. **Sequential Execution**: All 5 data sources called serially with blocking I/O
2. **No Caching**: Every request hits external APIs, even for static data
3. **HTML Parsing Inefficiency**: 10jqka uses regex on raw HTML (10.56s)
4. **Authentication Gaps**: Tencent Finance returns empty data (missing auth)
5. **Anti-Scraping Exposure**: CLS Telegraph being blocked intermittently

### 1.2 Data Source Performance Profile

```python
# Performance Breakdown Analysis

Data Source Performance:
┌─────────────────┬──────────┬──────────────┬─────────────────────────┐
│ Source          │ Response │ Reliability  │ Primary Bottleneck      │
├─────────────────┼──────────┼──────────────┼─────────────────────────┤
│ Sina Finance    │ 1.11s ✅ │ 100% (15/15) │ None - Optimal          │
│ Eastmoney       │ 2.49s ✅ │ 100% (15/15) │ None - Acceptable       │
│ CLS Telegraph   │ 2.06s ⚠️ │  93% (14/15) │ Anti-scraping detection │
│ Tencent Finance │ 7.06s ⚠️ │  60% ( 9/15) │ Auth required + parsing │
│ 10jqka (THS)    │ 10.56s ⚠️│  73% (11/15) │ Regex HTML parsing      │
└─────────────────┴──────────┴──────────────┴─────────────────────────┘

Cache Opportunity Analysis:
- Market Rankings: 5min cache (盘中), 2h cache (盘后)
- Stock Quotes: 15sec cache (盘中), 30min cache (盘后)
- News/Telegraph: 1min cache (盘中), 10min cache (盘后)
- Money Flow: 5min cache (盘中), 1h cache (盘后)
- Industry Ranking: 10min cache (盘中), 4h cache (盘后)
```

### 1.3 Current Error Handling

**Strengths**:
- 30s timeout prevents indefinite hangs
- Exponential backoff retry (1s, 2s, 4s)
- Graceful degradation with try-except blocks
- Empty fallback data structures

**Weaknesses**:
- No logging/alerting for repeated failures
- No circuit breaker pattern
- No health check before data fetch
- No multi-source fallback strategy

---

## Part 2: Optimized Architecture Design

### 2.1 High-Level Architecture

**Target State**: Async Concurrent Architecture with Intelligent Caching

```
┌─────────────────────────────────────────────────────────────────┐
│                  cn_market_report.py (Main)                     │
│                   Async Orchestrator Layer                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │  Cache Manager  │ (Redis/DiskCache)
                    │  - Market hours │
                    │  - TTL strategy │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │   Async Data Fetcher Pool    │
              │   (asyncio + aiohttp)        │
              └──────────────┬──────────────┘
                             │
        ┏━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━┓
        ┃     Parallel Async Data Sources        ┃
        ┣━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━┫
        ┃ Sina   ┃ East  ┃ CLS   ┃ Tence ┃ THS  ┃
        ┃ 1.11s  ┃ 2.49s ┃ 2.06s ┃ 7.06s ┃10.56s┃
        ┗━━━━━━━━┻━━━━━━━┻━━━━━━━┻━━━━━━━┻━━━━━━┛
                     │
              Parallel Execution
         Max Time = max(1.11, 2.49, 2.06, 7.06, 10.56)
                  = 10.56s (72% faster!)
                     │
        ┌────────────┴────────────┐
        │   Data Aggregator       │
        │   - Merge results       │
        │   - Handle partial data │
        │   - Quality validation  │
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        │  Report Generator       │
        │  - Markdown formatting  │
        │  - JSON serialization   │
        └─────────────────────────┘
```

### 2.2 Caching Strategy Design

**Cache Architecture**:

```python
# Cache Strategy Specification

from enum import Enum
from datetime import datetime, time

class MarketSession(Enum):
    PRE_MARKET = "pre_market"      # Before 09:30
    TRADING = "trading"            # 09:30 - 15:00
    POST_MARKET = "post_market"    # After 15:00
    WEEKEND = "weekend"

class CacheConfig:
    """
    Dynamic cache TTL based on market session and data type
    """

    # Cache backends (priority order)
    BACKENDS = ['redis', 'diskcache', 'memory']

    # TTL Matrix (seconds)
    TTL_MATRIX = {
        'market_rankings': {
            MarketSession.TRADING: 300,      # 5 min (high volatility)
            MarketSession.POST_MARKET: 7200, # 2 hours
            MarketSession.PRE_MARKET: 14400, # 4 hours
            MarketSession.WEEKEND: 86400,    # 24 hours
        },
        'stock_quotes': {
            MarketSession.TRADING: 15,       # 15 sec (real-time needed)
            MarketSession.POST_MARKET: 1800, # 30 min
            MarketSession.PRE_MARKET: 3600,  # 1 hour
            MarketSession.WEEKEND: 43200,    # 12 hours
        },
        'news_telegraph': {
            MarketSession.TRADING: 60,       # 1 min (breaking news)
            MarketSession.POST_MARKET: 600,  # 10 min
            MarketSession.PRE_MARKET: 1800,  # 30 min
            MarketSession.WEEKEND: 3600,     # 1 hour
        },
        'money_flow': {
            MarketSession.TRADING: 300,      # 5 min
            MarketSession.POST_MARKET: 3600, # 1 hour
            MarketSession.PRE_MARKET: 7200,  # 2 hours
            MarketSession.WEEKEND: 28800,    # 8 hours
        },
        'industry_ranking': {
            MarketSession.TRADING: 600,      # 10 min (slower changes)
            MarketSession.POST_MARKET: 14400,# 4 hours
            MarketSession.PRE_MARKET: 28800, # 8 hours
            MarketSession.WEEKEND: 86400,    # 24 hours
        }
    }

    @staticmethod
    def get_market_session() -> MarketSession:
        """Determine current market session based on Shanghai time"""
        now = datetime.now()

        # Weekend check
        if now.weekday() >= 5:  # Saturday=5, Sunday=6
            return MarketSession.WEEKEND

        current_time = now.time()
        trading_start = time(9, 30)
        trading_end = time(15, 0)

        if current_time < trading_start:
            return MarketSession.PRE_MARKET
        elif trading_start <= current_time <= trading_end:
            return MarketSession.TRADING
        else:
            return MarketSession.POST_MARKET

    @staticmethod
    def get_ttl(data_type: str) -> int:
        """Get appropriate TTL for data type and market session"""
        session = CacheConfig.get_market_session()
        return CacheConfig.TTL_MATRIX.get(data_type, {}).get(
            session,
            300  # Default 5 min fallback
        )

    @staticmethod
    def generate_cache_key(source: str, params: dict) -> str:
        """Generate consistent cache keys"""
        import hashlib
        import json

        key_data = {
            'source': source,
            'params': params,
            'version': 'v1'  # For cache invalidation on schema changes
        }

        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:8]

        return f"cn_market:{source}:{key_hash}"
```

**Cache Implementation Layers**:

1. **L1 Cache (Memory)**: In-process Python dict for ultra-fast access (<1ms)
2. **L2 Cache (DiskCache)**: Local SQLite for persistent cache (5-10ms)
3. **L3 Cache (Redis)**: Shared cache for distributed systems (10-20ms)

**Cache Warming Strategy**:

```python
# Pre-fetch strategy for predictable access patterns

CACHE_WARMING_SCHEDULE = {
    'market_open': {
        'time': '09:25',  # 5 min before market open
        'targets': [
            'market_rankings',
            'stock_quotes',
            'money_flow'
        ]
    },
    'lunch_break': {
        'time': '11:30',
        'targets': [
            'news_telegraph',
            'industry_ranking'
        ]
    },
    'market_close': {
        'time': '15:05',
        'targets': [
            'market_rankings',
            'money_flow',
            'industry_ranking'
        ]
    }
}
```

### 2.3 Async Parallel Data Fetching Architecture

**Implementation Specification**:

```python
# async_data_fetcher.py - Core async architecture

import asyncio
import aiohttp
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

@dataclass
class DataSource:
    """Data source configuration"""
    name: str
    fetch_func: Callable
    timeout: int = 30
    max_retries: int = 3
    cache_ttl: int = 300
    required: bool = False  # If True, report fails if this source fails
    fallback_sources: List[str] = None  # Alternative sources

class FetchStatus(Enum):
    SUCCESS = "success"
    CACHED = "cached"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CIRCUIT_OPEN = "circuit_open"

@dataclass
class FetchResult:
    """Standardized result container"""
    source: str
    status: FetchStatus
    data: Optional[dict]
    error: Optional[str]
    duration_ms: float
    from_cache: bool = False
    retry_count: int = 0

class AsyncDataOrchestrator:
    """
    Orchestrates parallel data fetching with:
    - Async/await for I/O concurrency
    - Circuit breaker pattern
    - Intelligent retry with exponential backoff
    - Cache integration
    - Graceful degradation
    """

    def __init__(
        self,
        cache_manager,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60
    ):
        self.cache_manager = cache_manager
        self.circuit_breaker = CircuitBreaker(
            threshold=circuit_breaker_threshold,
            timeout=circuit_breaker_timeout
        )
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager for session lifecycle"""
        connector = aiohttp.TCPConnector(
            limit=10,  # Max concurrent connections
            limit_per_host=2,  # Max per host to avoid overwhelming
            ttl_dns_cache=300
        )

        timeout = aiohttp.ClientTimeout(
            total=60,    # Total timeout for entire request
            connect=10,  # Connection timeout
            sock_read=30 # Socket read timeout
        )

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session"""
        if self.session:
            await self.session.close()

    async def fetch_all_sources(
        self,
        sources: List[DataSource],
        tickers: Optional[List[str]] = None
    ) -> Dict[str, FetchResult]:
        """
        Fetch data from all sources in parallel

        Returns:
            Dict mapping source name to FetchResult
        """
        tasks = []

        for source in sources:
            task = self._fetch_with_retry(source, tickers)
            tasks.append(task)

        # Wait for all tasks with timeout
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results back to source names
        result_map = {}
        for source, result in zip(sources, results):
            if isinstance(result, Exception):
                result_map[source.name] = FetchResult(
                    source=source.name,
                    status=FetchStatus.FAILED,
                    data=None,
                    error=str(result),
                    duration_ms=0,
                    from_cache=False
                )
            else:
                result_map[source.name] = result

        return result_map

    async def _fetch_with_retry(
        self,
        source: DataSource,
        tickers: Optional[List[str]]
    ) -> FetchResult:
        """
        Fetch with exponential backoff retry
        """
        import time

        # Check circuit breaker
        if self.circuit_breaker.is_open(source.name):
            return FetchResult(
                source=source.name,
                status=FetchStatus.CIRCUIT_OPEN,
                data=None,
                error="Circuit breaker open",
                duration_ms=0,
                from_cache=False
            )

        # Check cache first
        cache_key = self.cache_manager.generate_key(source.name, tickers)
        cached_data = await self.cache_manager.get(cache_key)

        if cached_data:
            return FetchResult(
                source=source.name,
                status=FetchStatus.CACHED,
                data=cached_data,
                error=None,
                duration_ms=0,
                from_cache=True
            )

        # Retry loop
        last_error = None
        for attempt in range(source.max_retries):
            start_time = time.time()

            try:
                # Call the actual fetch function
                if asyncio.iscoroutinefunction(source.fetch_func):
                    data = await source.fetch_func(self.session, tickers)
                else:
                    # Wrap sync function in executor
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(
                        None,
                        source.fetch_func,
                        tickers
                    )

                duration_ms = (time.time() - start_time) * 1000

                # Cache successful result
                await self.cache_manager.set(
                    cache_key,
                    data,
                    ttl=source.cache_ttl
                )

                # Reset circuit breaker on success
                self.circuit_breaker.record_success(source.name)

                return FetchResult(
                    source=source.name,
                    status=FetchStatus.SUCCESS,
                    data=data,
                    error=None,
                    duration_ms=duration_ms,
                    from_cache=False,
                    retry_count=attempt
                )

            except asyncio.TimeoutError as e:
                last_error = f"Timeout after {source.timeout}s"
                duration_ms = (time.time() - start_time) * 1000

                if attempt < source.max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    await asyncio.sleep(wait_time)

            except Exception as e:
                last_error = str(e)

                if attempt < source.max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)

        # All retries failed - record failure
        self.circuit_breaker.record_failure(source.name)

        return FetchResult(
            source=source.name,
            status=FetchStatus.FAILED,
            data=None,
            error=last_error,
            duration_ms=duration_ms,
            from_cache=False,
            retry_count=source.max_retries
        )


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failures: Dict[str, int] = {}
        self.last_failure_time: Dict[str, float] = {}

    def is_open(self, source: str) -> bool:
        """Check if circuit is open for a source"""
        import time

        if source not in self.failures:
            return False

        # Check if timeout expired (move to HALF_OPEN)
        if time.time() - self.last_failure_time.get(source, 0) > self.timeout:
            self.failures[source] = 0
            return False

        return self.failures.get(source, 0) >= self.threshold

    def record_failure(self, source: str):
        """Record a failure"""
        import time
        self.failures[source] = self.failures.get(source, 0) + 1
        self.last_failure_time[source] = time.time()

    def record_success(self, source: str):
        """Record a success - reset counter"""
        self.failures[source] = 0
```

### 2.4 Enhanced HTML Parsing for 10jqka

**Problem**: Current regex-based parsing is slow (10.56s) and brittle

**Solution**: Migrate to BeautifulSoup with CSS selectors

```python
# cn_ths_diagnosis_v2.py - Optimized parser

from bs4 import BeautifulSoup
import lxml  # Fast C-based parser

def fetch_industry_ranking_optimized(count=20):
    """
    Optimized industry ranking with BeautifulSoup + lxml
    Expected: <5s (50% improvement)
    """
    try:
        url = 'http://q.10jqka.com.cn/thshy/'

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('gbk', errors='ignore')

        # Use lxml parser (5-10x faster than html.parser)
        soup = BeautifulSoup(html, 'lxml')

        items = []

        # CSS selector (much faster than regex)
        # Target table structure: <table class="m-table"><tbody><tr>...
        table = soup.select_one('table.m-table tbody')

        if not table:
            return []

        for row in table.find_all('tr', limit=count):
            cells = row.find_all('td')

            if len(cells) < 3:
                continue

            name = cells[0].get_text(strip=True)
            price = cells[1].get_text(strip=True)
            pct = cells[2].get_text(strip=True)

            items.append({
                'name': name,
                'price': try_float(price),
                'pct': try_float(pct.replace('%', '').replace('+', '')),
                'source': '10jqka_industry'
            })

        return items

    except Exception as e:
        print(f"同花顺行业排行获取失败: {e}", file=sys.stderr)
        return []

# Performance comparison:
# - Old (regex): ~10.56s
# - New (BeautifulSoup + lxml): ~4-5s
# - Improvement: 50-53%
```

### 2.5 Tencent Finance Authentication Strategy

**Problem**: Money flow data returns empty due to missing authentication

**Investigation Required**:

```python
# cn_tencent_auth_investigation.py

"""
Authentication Investigation Steps:

1. Browser DevTools Analysis:
   - Open Chrome DevTools → Network tab
   - Visit https://stockapp.finance.qq.com
   - Capture all requests to money flow endpoints
   - Check for:
     * Cookie values (session, token)
     * Authorization headers
     * CSRF tokens
     * Request signatures

2. Cookie Analysis:
   Required cookies (typically):
   - uin: User ID
   - skey: Session key
   - p_skey: Product session key
   - pt4_token: Platform token

3. API Endpoint Analysis:
   Current: https://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/chr

   Might need:
   - Different endpoint for authenticated data
   - Additional query parameters
   - Request signing algorithm

4. Implementation Strategy:

   Option A: Cookie-based auth (recommended)
   - Extract cookies from browser session
   - Store in .env file
   - Include in all requests
   - Auto-refresh when expired

   Option B: API key/token (if available)
   - Register for developer account
   - Use official API with credentials
   - More stable long-term

   Option C: Headless browser (last resort)
   - Use Selenium/Playwright
   - Full browser automation
   - Highest resource cost
"""

import http.cookiejar
import urllib.request

class TencentAuthManager:
    """
    Manages authentication for Tencent Finance API
    """

    def __init__(self, cookie_file: str = '.tencent_cookies.txt'):
        self.cookie_file = cookie_file
        self.cookie_jar = http.cookiejar.MozillaCookieJar(cookie_file)

        # Try to load existing cookies
        try:
            self.cookie_jar.load(ignore_discard=True, ignore_expires=True)
        except FileNotFoundError:
            pass

    def save_cookies_from_browser(self):
        """
        Instructions to manually extract cookies:

        1. Open Chrome
        2. Visit https://stockapp.finance.qq.com
        3. Login if needed
        4. Open DevTools → Application → Cookies
        5. Copy these cookies:
           - uin
           - skey
           - p_skey
           - pt4_token
        6. Save to .env:
           TENCENT_COOKIES="uin=xxx; skey=xxx; p_skey=xxx; pt4_token=xxx"
        """
        pass

    def get_authenticated_opener(self):
        """Create URL opener with cookies"""
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        return opener

    def test_authentication(self):
        """Test if current cookies work"""
        try:
            opener = self.get_authenticated_opener()
            url = 'https://stock.gtimg.cn/data/index.php?appn=rank&t=ranka/chr&i=0&v=dd&d=d&p=1&l=40'

            req = urllib.request.Request(url, headers=HEADERS)
            response = opener.open(req, timeout=10)
            data = response.read().decode('gbk', errors='ignore')

            # Check if we got valid data (not empty)
            if 'data:"' in data and len(data) > 100:
                return True, "Authentication successful"
            else:
                return False, "Got response but data empty - may need auth"

        except Exception as e:
            return False, f"Authentication failed: {e}"
```

**Recommended Implementation**:

1. Create `.env.tencent` file for cookie storage
2. Provide CLI tool for cookie extraction
3. Auto-refresh cookies every 7 days
4. Fallback to alternative data source if auth fails

### 2.6 Anti-Scraping Countermeasures for CLS

**Problem**: CLS Telegraph blocked intermittently (93% success rate)

**Strategy**: Multi-layered anti-detection

```python
# anti_scraping_toolkit.py

import random
import time
from typing import List
from fake_useragent import UserAgent

class AntiScrapingToolkit:
    """
    Comprehensive anti-scraping toolkit
    """

    def __init__(self):
        self.ua = UserAgent()
        self.request_count = 0
        self.last_request_time = 0

    def get_rotating_headers(self) -> dict:
        """Rotate headers to appear more human-like"""

        browsers = ['chrome', 'firefox', 'safari', 'edge']
        browser = random.choice(browsers)

        headers = {
            'User-Agent': self.ua[browser],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

        # Randomly include referer (80% of time)
        if random.random() > 0.2:
            headers['Referer'] = 'https://www.cls.cn/'

        return headers

    def rate_limit(self, min_interval: float = 1.0):
        """
        Enforce rate limiting between requests

        Args:
            min_interval: Minimum seconds between requests
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            # Add random jitter (±20%)
            jitter = random.uniform(-0.2, 0.2) * sleep_time
            time.sleep(sleep_time + jitter)

        self.last_request_time = time.time()
        self.request_count += 1

    def add_human_delay(self):
        """Add realistic human-like delay"""
        # Random delay between 0.5-2.0 seconds
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)

    def should_use_proxy(self) -> bool:
        """
        Determine if proxy should be used
        Based on request count and failure rate
        """
        # Use proxy after 10 consecutive requests from same IP
        return self.request_count % 10 == 0


class ProxyRotator:
    """
    Proxy pool management (optional - for heavy usage)

    Proxy sources:
    1. Free proxy lists (unreliable)
    2. Paid proxy services (recommended)
    3. Self-hosted proxy network
    """

    def __init__(self, proxy_list: List[str] = None):
        self.proxies = proxy_list or []
        self.current_index = 0
        self.failed_proxies = set()

    def get_next_proxy(self) -> str:
        """Get next working proxy"""
        if not self.proxies:
            return None

        for _ in range(len(self.proxies)):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)

            if proxy not in self.failed_proxies:
                return proxy

        # All proxies failed - reset and try again
        self.failed_proxies.clear()
        return self.proxies[0] if self.proxies else None

    def mark_failed(self, proxy: str):
        """Mark proxy as failed"""
        self.failed_proxies.add(proxy)


# Enhanced CLS fetcher with anti-scraping
async def fetch_cls_telegraph_v2(session: aiohttp.ClientSession, count=20):
    """
    Enhanced CLS telegraph fetcher with anti-scraping measures
    """
    toolkit = AntiScrapingToolkit()

    # Rate limiting
    toolkit.rate_limit(min_interval=1.0)

    # Rotating headers
    headers = toolkit.get_rotating_headers()

    try:
        url = f'https://www.cls.cn/nodeapi/telegraphList?app=CailianpressWeb&category=&lastTime=&os=web&refresh_type=1&rn={count}&sv=7.7.5'

        async with session.get(url, headers=headers, timeout=15) as response:
            # Check for rate limiting response
            if response.status == 429:
                # Back off for longer
                await asyncio.sleep(5)
                raise Exception("Rate limited - backing off")

            response.raise_for_status()
            data = await response.json()

        items = []
        rolldata = data.get('data', {}).get('roll_data', [])

        for item in rolldata[:count]:
            content = item.get('content', '')
            brief = item.get('brief', '')

            import re
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

        # Success - add small delay for next request
        toolkit.add_human_delay()

        return items

    except Exception as e:
        print(f"CLS telegraph fetch failed: {e}", file=sys.stderr)
        return []
```

---

## Part 3: Implementation Roadmap

### 3.1 Phase 1: Quick Wins (v1.1.0) - Week 1-2

**Target**: Achieve <25s report generation (36% improvement)

**Changes**:
1. Implement async parallel data fetching
2. Add basic in-memory caching (L1 only)
3. Optimize 10jqka HTML parser with BeautifulSoup

**Migration Strategy**:
```python
# Step 1: Create new async module alongside existing
# - Keeps existing code working
# - Allows A/B testing

# scripts/async_cn_market_report.py
# New async implementation

# Step 2: Add feature flag
USE_ASYNC = os.getenv('CN_MARKET_USE_ASYNC', 'false').lower() == 'true'

if USE_ASYNC:
    from scripts.async_cn_market_report import generate_report_async
    result = asyncio.run(generate_report_async())
else:
    # Original sync code
    result = generate_report_sync()

# Step 3: Test in production with monitoring
# - Compare results between sync and async
# - Validate data consistency
# - Monitor performance metrics

# Step 4: Gradual rollout
# - Week 1: 10% traffic
# - Week 2: 50% traffic
# - Week 3: 100% traffic (deprecate sync)
```

**Success Metrics**:
- [ ] Report generation: <25s (from 38.98s)
- [ ] Cache hit rate: >30%
- [ ] Data consistency: 100% match with sync version
- [ ] Zero data loss or corruption

### 3.2 Phase 2: Stability & Caching (v1.1.1) - Week 3-4

**Target**: Achieve <20s with caching (49% improvement)

**Changes**:
1. Add DiskCache for persistence (L2)
2. Implement market-hour aware TTL
3. Add cache warming for predictable patterns
4. Enhance anti-scraping for CLS

**Implementation**:
```python
# Cache manager with fallback layers

from diskcache import Cache
import os

class HybridCacheManager:
    """
    Multi-layer cache with automatic fallback

    L1 (Memory): <1ms, 100MB limit, lost on restart
    L2 (Disk): 5-10ms, 1GB limit, persistent
    L3 (Redis): 10-20ms, shared, optional
    """

    def __init__(self, cache_dir: str = '.cache'):
        # L1: In-memory dict
        self.memory_cache: Dict[str, tuple] = {}  # (data, expiry)
        self.memory_max_size = 100 * 1024 * 1024  # 100MB

        # L2: DiskCache
        self.disk_cache = Cache(
            directory=os.path.join(cache_dir, 'cn_market'),
            size_limit=1 * 1024 * 1024 * 1024,  # 1GB
            eviction_policy='least-recently-used'
        )

        # L3: Redis (optional)
        self.redis_client = None
        if os.getenv('REDIS_URL'):
            import redis
            self.redis_client = redis.from_url(os.getenv('REDIS_URL'))

    async def get(self, key: str) -> Optional[dict]:
        """Get from cache with layer fallback"""
        import time

        # Try L1 (memory)
        if key in self.memory_cache:
            data, expiry = self.memory_cache[key]
            if time.time() < expiry:
                return data
            else:
                del self.memory_cache[key]

        # Try L2 (disk)
        data = self.disk_cache.get(key)
        if data:
            # Promote to L1
            ttl = self.disk_cache.get(f"{key}:ttl", 300)
            self.memory_cache[key] = (data, time.time() + ttl)
            return data

        # Try L3 (Redis) if available
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    import json
                    data = json.loads(data)
                    # Promote to L2 and L1
                    await self.set(key, data, ttl=300)
                    return data
            except:
                pass

        return None

    async def set(self, key: str, data: dict, ttl: int):
        """Set in all cache layers"""
        import time

        # L1 (memory)
        self.memory_cache[key] = (data, time.time() + ttl)

        # L2 (disk)
        self.disk_cache.set(key, data, expire=ttl)
        self.disk_cache.set(f"{key}:ttl", ttl)

        # L3 (Redis)
        if self.redis_client:
            try:
                import json
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(data, ensure_ascii=False)
                )
            except:
                pass  # Redis failure shouldn't break the app
```

**Success Metrics**:
- [ ] Report generation: <20s
- [ ] Cache hit rate: >60%
- [ ] CLS success rate: >95% (from 93%)
- [ ] Disk cache: <100MB for 7 days of data

### 3.3 Phase 3: Authentication & Polish (v1.2.0) - Week 5-6

**Target**: Full reliability + monitoring

**Changes**:
1. Implement Tencent Finance authentication
2. Add monitoring and alerting
3. Add data quality validation
4. Implement circuit breaker pattern

**Monitoring Dashboard**:
```python
# monitoring.py - Performance tracking

import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List
from datetime import datetime

@dataclass
class PerformanceMetrics:
    """Track key metrics"""
    timestamp: str
    total_duration_ms: float
    cache_hit_rate: float
    source_durations: Dict[str, float]
    source_success_rates: Dict[str, float]
    errors: List[str]

    def to_dict(self):
        return asdict(self)

    def save(self, filepath: str):
        """Save metrics to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load(filepath: str) -> 'PerformanceMetrics':
        """Load metrics from JSON"""
        with open(filepath) as f:
            data = json.load(f)
        return PerformanceMetrics(**data)


class PerformanceMonitor:
    """Monitor and alert on performance degradation"""

    def __init__(self, alert_threshold_ms: float = 30000):
        self.alert_threshold = alert_threshold_ms
        self.metrics_history: List[PerformanceMetrics] = []

    def record(self, metrics: PerformanceMetrics):
        """Record new metrics"""
        self.metrics_history.append(metrics)

        # Keep only last 100 runs
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)

        # Check for alerts
        self._check_alerts(metrics)

    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check if alerts should be triggered"""

        # Alert 1: Total duration exceeds threshold
        if metrics.total_duration_ms > self.alert_threshold:
            self._send_alert(
                f"Performance degradation: {metrics.total_duration_ms:.0f}ms "
                f"exceeds threshold {self.alert_threshold:.0f}ms"
            )

        # Alert 2: Cache hit rate drops below 40%
        if metrics.cache_hit_rate < 0.4:
            self._send_alert(
                f"Low cache hit rate: {metrics.cache_hit_rate:.1%}"
            )

        # Alert 3: Any source success rate below 80%
        for source, rate in metrics.source_success_rates.items():
            if rate < 0.8:
                self._send_alert(
                    f"Source {source} failing: {rate:.1%} success rate"
                )

    def _send_alert(self, message: str):
        """Send alert (implement notification logic)"""
        print(f"[ALERT] {message}", file=sys.stderr)

        # TODO: Integrate with:
        # - Email (SMTP)
        # - Slack webhook
        # - PagerDuty
        # - Custom webhook

    def get_summary(self) -> dict:
        """Get performance summary"""
        if not self.metrics_history:
            return {}

        recent = self.metrics_history[-10:]  # Last 10 runs

        avg_duration = sum(m.total_duration_ms for m in recent) / len(recent)
        avg_cache_hit = sum(m.cache_hit_rate for m in recent) / len(recent)

        return {
            'avg_duration_ms': avg_duration,
            'avg_cache_hit_rate': avg_cache_hit,
            'total_runs': len(self.metrics_history),
            'last_run': recent[-1].timestamp
        }
```

**Success Metrics**:
- [ ] Tencent Finance: >0 money flow records
- [ ] Monitoring: <5min alert latency
- [ ] Circuit breaker: Prevents cascade failures
- [ ] Data quality: 100% schema validation

---

## Part 4: Answers to Key Questions

### Q1: How to guarantee partial data source failures don't block report?

**Answer**: Multi-level graceful degradation

```python
class ReportGenerator:
    """
    Generate report even with partial data
    """

    REQUIRED_SOURCES = ['stock_quotes']  # Only real-time quotes required
    OPTIONAL_SOURCES = ['market_rankings', 'cls_telegraph',
                        'tencent_moneyflow', 'ths_diagnosis']

    def generate_report(self, fetch_results: Dict[str, FetchResult]) -> dict:
        """
        Generate report with available data

        Strategy:
        1. If required sources fail: abort with error
        2. If optional sources fail: continue with placeholder
        3. Mark sections as "unavailable" with reason
        4. Log all failures for investigation
        """

        # Check required sources
        for source in self.REQUIRED_SOURCES:
            result = fetch_results.get(source)
            if not result or result.status != FetchStatus.SUCCESS:
                raise ReportGenerationError(
                    f"Required source {source} failed: {result.error}"
                )

        # Build report with available data
        report_sections = {}

        for source in self.OPTIONAL_SOURCES:
            result = fetch_results.get(source)

            if result and result.status == FetchStatus.SUCCESS:
                report_sections[source] = self._format_section(
                    source,
                    result.data
                )
            else:
                # Fallback section
                report_sections[source] = self._format_unavailable_section(
                    source,
                    reason=result.error if result else "Unknown"
                )

        return {
            'sections': report_sections,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'success_rate': self._calculate_success_rate(fetch_results),
                'data_sources': list(fetch_results.keys())
            }
        }

    def _format_unavailable_section(self, source: str, reason: str) -> str:
        """Format unavailable data section"""
        return f"## {source}\n\n⚠️ 数据暂时不可用\n\n原因: {reason}\n"
```

### Q2: How to design cache strategy for trading hours vs after-hours?

**Answer**: See Section 2.2 - Dynamic TTL based on market session

Key principles:
1. **Trading hours (09:30-15:00)**: Short TTL for near-real-time data
2. **After hours**: Long TTL since data is static
3. **Pre-market**: Medium TTL for overnight changes
4. **Weekend**: Longest TTL to reduce load

### Q3: How to fight anti-scraping without breaking reliability?

**Answer**: Layered approach with automatic fallback

```python
# Anti-scraping priority:
# 1. Rotating user agents (low risk, high effectiveness)
# 2. Request rate limiting with jitter (required)
# 3. Referer headers (helps with some sites)
# 4. Cookie persistence (for stateful sites)
# 5. Proxy rotation (only if needed, adds latency)

# If all fail: use cached data (even if stale)
# Better stale data than no data
```

### Q4: Microservices vs Monolith?

**Answer**: Stay monolith with modular design (for now)

**Reasoning**:
- Current scale: 5 data sources, <5 req/min
- Microservices overhead: Service mesh, inter-service communication, deployment complexity
- Monolith benefits: Simpler deployment, easier debugging, lower latency
- Future migration path: Design modules as if they were microservices

**When to split to microservices**:
- Exceeds 100 req/min
- Need independent scaling per source
- Different teams maintain different sources
- SLA requirements differ by source

### Q5: How to implement progressive optimization?

**Answer**: Feature flags + backward compatibility

```python
# Progressive rollout strategy:

# 1. Add alongside existing (Week 1)
#    - New code in separate module
#    - Old code still runs
#    - No breaking changes

# 2. A/B testing (Week 2)
#    - 10% traffic to new code
#    - Compare results
#    - Monitor for issues

# 3. Gradual increase (Week 3)
#    - 50% traffic if no issues
#    - Continue monitoring

# 4. Full migration (Week 4)
#    - 100% traffic to new code
#    - Deprecate old code
#    - Remove after 1 month

# 5. Rollback plan
#    - Keep old code for 1 month
#    - Single env var to switch back
#    - Document rollback procedure
```

---

## Part 5: Performance Projections

### 5.1 Expected Performance Improvements

```
Baseline (Current):
├── Sequential Data Fetch: 23.28s
│   ├── Sina Finance:      1.11s
│   ├── Eastmoney:         2.49s
│   ├── CLS Telegraph:     2.06s
│   ├── Tencent Finance:   7.06s
│   └── 10jqka:           10.56s
├── JSON I/O:              5.00s (estimated)
├── Parsing/Formatting:    8.00s (estimated)
├── Markdown Generation:   2.70s (estimated)
└── Total:                38.98s

Phase 1 (v1.1.0 - Async + Basic Cache):
├── Parallel Data Fetch:  10.56s (slowest source)
├── JSON I/O:              5.00s
├── Parsing (optimized):   4.00s (-50% via BeautifulSoup)
├── Markdown Generation:   2.70s
├── Total:                22.26s (-43%)
└── Cache Hit (30%):      15.58s (-60% on cache hit)

Phase 2 (v1.1.1 - Full Cache + Anti-scraping):
├── Parallel Data Fetch:   8.00s (10jqka improved to 5s)
├── JSON I/O:              5.00s
├── Parsing:               3.00s
├── Markdown Generation:   2.70s
├── Total:                18.70s (-52%)
└── Cache Hit (60%):       7.48s (-81% on cache hit)

Phase 3 (v1.2.0 - Full Optimization):
├── Parallel Data Fetch:   7.00s (Tencent auth reduces to 4s)
├── JSON I/O:              4.00s (async file I/O)
├── Parsing:               3.00s
├── Markdown Generation:   2.50s
├── Total:                16.50s (-58%)
└── Cache Hit (70%):       6.95s (-82% on cache hit)
```

### 5.2 Cost-Benefit Analysis

| Phase | Dev Time | Performance Gain | Risk | ROI |
|-------|----------|------------------|------|-----|
| Phase 1 | 2 weeks | 43% faster | Low | High - Quick wins |
| Phase 2 | 2 weeks | 52% faster | Medium | High - Caching critical |
| Phase 3 | 2 weeks | 58% faster | Medium | Medium - Diminishing returns |

**Recommendation**: Implement Phase 1 & 2 immediately, defer Phase 3 pending usage metrics

---

## Part 6: Risk Assessment & Mitigation

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Async bugs cause data loss | Medium | High | Extensive testing, feature flags |
| Cache invalidation issues | Medium | Medium | Short TTL initially, monitoring |
| External API changes break parsers | High | Medium | Schema validation, alerts |
| Auth tokens expire | Low | Medium | Auto-refresh, fallback sources |
| Performance regression | Low | High | A/B testing, rollback plan |

### 6.2 Rollback Strategy

```python
# Emergency rollback procedure (5 minutes):

# 1. Set environment variable
export CN_MARKET_USE_ASYNC=false

# 2. Restart application
systemctl restart openclaw-analyst

# 3. Verify rollback
curl http://localhost/api/cn-market-report
# Should see sync version marker

# 4. Investigate issue
tail -f /var/log/openclaw/cn_market.log

# 5. Fix and redeploy
# ... fix code ...
git commit -m "fix: resolve async data corruption"
git push
# CI/CD auto-deploys
```

---

## Part 7: Implementation Checklist

### Phase 1: Async Foundation (v1.1.0)

- [ ] Create `async_cn_market_report.py` module
- [ ] Implement `AsyncDataOrchestrator` class
- [ ] Convert data sources to async functions
  - [ ] `fetch_sina_quotes_async()`
  - [ ] `fetch_eastmoney_rankings_async()`
  - [ ] `fetch_cls_telegraph_async()`
  - [ ] `fetch_tencent_moneyflow_async()`
  - [ ] `fetch_ths_diagnosis_async()`
- [ ] Implement basic in-memory cache (L1)
- [ ] Add feature flag `CN_MARKET_USE_ASYNC`
- [ ] Write integration tests
  - [ ] Test parallel execution
  - [ ] Test partial failure handling
  - [ ] Test data consistency with sync version
- [ ] Performance benchmark suite
- [ ] Update documentation

### Phase 2: Caching & Stability (v1.1.1)

- [ ] Implement `HybridCacheManager`
- [ ] Add DiskCache integration (L2)
- [ ] Implement market-hour aware TTL
- [ ] Add cache warming scheduler
- [ ] Implement `AntiScrapingToolkit`
- [ ] Add rotating user agents
- [ ] Add request rate limiting
- [ ] Optimize 10jqka parser with BeautifulSoup
- [ ] Add monitoring module
- [ ] Cache performance dashboard

### Phase 3: Authentication & Monitoring (v1.2.0)

- [ ] Investigate Tencent Finance auth
- [ ] Implement `TencentAuthManager`
- [ ] Add cookie persistence
- [ ] Implement `CircuitBreaker` pattern
- [ ] Add `PerformanceMonitor`
- [ ] Add alert system (email/Slack)
- [ ] Implement data quality validation
- [ ] Add health check endpoint
- [ ] Create operations runbook
- [ ] Final performance audit

---

## Part 8: Code Migration Examples

### 8.1 Main Report Generator Migration

```python
# BEFORE: cn_market_report.py (sync)
def main():
    # Sequential execution
    hot = run_json([sys.executable, 'cn_market_rankings.py'])
    wl = run_json([sys.executable, 'cn_stock_quotes.py', *tickers])
    cls = run_json([sys.executable, 'cn_cls_telegraph.py'])
    # ... 23.28s total

# AFTER: async_cn_market_report.py (async)
async def main_async():
    # Parallel execution
    async with AsyncDataOrchestrator(cache_manager) as orchestrator:
        sources = [
            DataSource('market_rankings', fetch_rankings_async, cache_ttl=300),
            DataSource('stock_quotes', fetch_quotes_async, cache_ttl=15),
            DataSource('cls_telegraph', fetch_cls_async, cache_ttl=60),
            DataSource('tencent_moneyflow', fetch_tencent_async, cache_ttl=300),
            DataSource('ths_diagnosis', fetch_ths_async, cache_ttl=600),
        ]

        results = await orchestrator.fetch_all_sources(sources, tickers)
        # ... 10.56s total (parallel)

    return generate_report(results)

# Compatibility wrapper
def main():
    if os.getenv('CN_MARKET_USE_ASYNC') == 'true':
        return asyncio.run(main_async())
    else:
        return main_sync()  # Original code
```

### 8.2 Individual Data Source Migration

```python
# BEFORE: cn_stock_quotes.py (sync)
def fetch_quotes(codes, max_retries=3):
    url = 'https://hq.sinajs.cn/list=' + ','.join(codes)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    # ... parse and return

# AFTER: async version
async def fetch_quotes_async(
    session: aiohttp.ClientSession,
    codes: List[str]
) -> dict:
    """
    Async version compatible with AsyncDataOrchestrator
    """
    url = 'https://hq.sinajs.cn/list=' + ','.join(codes)

    async with session.get(url, timeout=30) as response:
        data = await response.read()

    # Parsing logic stays the same
    text = data.decode('gbk', errors='ignore')
    quotes = parse_sina_response(text)

    return {'quotes': quotes}
```

---

## Appendix A: Dependencies Update

```bash
# New dependencies for async architecture

pip install aiohttp          # Async HTTP client
pip install diskcache        # L2 disk cache
pip install fake-useragent   # User agent rotation
pip install beautifulsoup4   # HTML parsing (already have?)
pip install lxml            # Fast XML/HTML parser
pip install redis           # L3 cache (optional)
pip install tenacity        # Advanced retry (optional)

# Update requirements.txt
cat >> requirements.txt << 'EOF'

# Async architecture dependencies (v1.1.0+)
aiohttp>=3.9.0
diskcache>=5.6.0
fake-useragent>=1.4.0
beautifulsoup4>=4.12.0
lxml>=5.0.0

# Optional for distributed caching
redis>=5.0.0

# Optional for advanced retry
tenacity>=8.2.0
EOF
```

## Appendix B: Configuration Template

```bash
# .env.cn_market - Configuration for China market module

# Async mode (set to 'true' to enable)
CN_MARKET_USE_ASYNC=false

# Cache configuration
CACHE_BACKEND=diskcache  # Options: memory, diskcache, redis
CACHE_DIR=/var/cache/openclaw/cn_market
CACHE_MAX_SIZE_MB=1000

# Redis configuration (if using redis backend)
REDIS_URL=redis://localhost:6379/0

# Tencent Finance authentication (Phase 3)
TENCENT_COOKIES="uin=xxx; skey=xxx; p_skey=xxx; pt4_token=xxx"

# Anti-scraping configuration
USE_PROXY=false
PROXY_LIST=/etc/openclaw/proxies.txt
USER_AGENT_ROTATION=true
MIN_REQUEST_INTERVAL_SEC=1.0

# Circuit breaker configuration
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT_SEC=60

# Monitoring configuration
ENABLE_MONITORING=true
ALERT_THRESHOLD_MS=30000
ALERT_EMAIL=ops@example.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

# Performance tuning
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT_SEC=30
MAX_RETRIES=3
```

---

## Conclusion

This architecture optimization plan provides a comprehensive roadmap to improve China market report generation performance by **49-58%** while maintaining 100% reliability and adding enterprise-grade caching, monitoring, and error handling.

The phased approach allows for progressive optimization with minimal risk, ensuring backward compatibility and providing clear rollback procedures at each stage.

**Next Steps**:
1. Review and approve architecture plan
2. Create Phase 1 implementation tickets
3. Set up development environment with async dependencies
4. Begin implementation starting with async data orchestrator
5. Establish performance benchmarking baseline

**Estimated Timeline**:
- Phase 1: 2 weeks (v1.1.0)
- Phase 2: 2 weeks (v1.1.1)
- Phase 3: 2 weeks (v1.2.0)
- Total: 6 weeks to full optimization

**Estimated Performance**:
- Phase 1: 38.98s → 22.26s (43% improvement)
- Phase 2: 38.98s → 18.70s (52% improvement)
- Phase 3: 38.98s → 16.50s (58% improvement)
- With cache hits: 6.95s (82% improvement)

---

**Document Version**: 1.0
**Last Updated**: 2026-03-18
**Status**: Ready for Implementation
