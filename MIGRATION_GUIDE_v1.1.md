# Migration Guide: Async Architecture v1.1.0
## From Sequential to Parallel Data Fetching

**Target**: Reduce China market report generation from 38.98s to <22s (43% improvement)

**Risk Level**: Low (backward compatible, feature-flagged)

**Timeline**: 2 weeks for Phase 1 implementation

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Testing Strategy](#testing-strategy)
4. [Deployment Process](#deployment-process)
5. [Rollback Procedure](#rollback-procedure)
6. [Monitoring & Validation](#monitoring--validation)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- Python 3.10+
- Disk space: 100MB for cache
- Memory: 512MB minimum
- Network: Stable connection to China market APIs

### Dependencies

Install new async dependencies:

```bash
# Core async dependencies
pip install aiohttp>=3.9.0
pip install aiodns>=3.1.0  # Optional: faster DNS resolution

# Optional for Phase 2
pip install diskcache>=5.6.0
pip install beautifulsoup4>=4.12.0
pip install lxml>=5.0.0
```

Or use the requirements file:

```bash
pip install -r requirements_async.txt
```

### Code Review Checklist

Before deployment, ensure:

- [ ] All async functions use `async/await` correctly
- [ ] No blocking I/O in async context (no `requests`, use `aiohttp`)
- [ ] Error handling maintains backward compatibility
- [ ] Cache keys are deterministic and versioned
- [ ] Timeout values are appropriate for each source
- [ ] Circuit breaker thresholds are reasonable

---

## Installation

### Step 1: Backup Current System

```bash
# Backup current scripts
cp -r scripts scripts.backup.$(date +%Y%m%d)

# Backup current reports
cp -r reports reports.backup.$(date +%Y%m%d)

# Tag current version in git
git tag -a v1.0.1-stable -m "Stable version before async migration"
git push origin v1.0.1-stable
```

### Step 2: Install New Files

```bash
# Copy new async architecture files
cp scripts/async_architecture_core.py scripts/
cp scripts/async_cn_market_demo.py scripts/

# Make executable
chmod +x scripts/async_architecture_core.py
chmod +x scripts/async_cn_market_demo.py
```

### Step 3: Configuration

Create configuration file `.env.cn_market`:

```bash
cat > .env.cn_market << 'EOF'
# Async mode (default: false for safety)
CN_MARKET_USE_ASYNC=false

# Cache configuration
CACHE_BACKEND=memory
CACHE_DIR=/var/cache/openclaw/cn_market
CACHE_MAX_SIZE_MB=100

# Performance tuning
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT_SEC=30
MAX_RETRIES=3

# Circuit breaker
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT_SEC=60
EOF
```

### Step 4: Verify Installation

```bash
# Test async module imports
python3 -c "from scripts.async_architecture_core import AsyncDataOrchestrator; print('✅ Core module OK')"

# Test demo script syntax
python3 -m py_compile scripts/async_cn_market_demo.py && echo "✅ Demo script syntax OK"

# Run quick test (won't fetch real data)
python3 scripts/async_architecture_core.py
```

---

## Testing Strategy

### Phase 1: Unit Testing (Day 1-2)

Test individual async components:

```bash
# Test 1: Cache manager
python3 << 'EOF'
import asyncio
from scripts.async_architecture_core import SimpleCacheManager

cache = SimpleCacheManager()

# Test basic operations
cache.set('test_key', {'data': 'value'}, ttl=60)
assert cache.get('test_key') == {'data': 'value'}

# Test expiration
import time
cache.set('expire_key', {'data': 'value'}, ttl=1)
time.sleep(2)
assert cache.get('expire_key') is None

print("✅ Cache manager tests passed")
EOF

# Test 2: Circuit breaker
python3 << 'EOF'
from scripts.async_architecture_core import CircuitBreaker

breaker = CircuitBreaker(threshold=3, timeout=60)

# Trigger circuit breaker
for i in range(5):
    breaker.record_failure('test_api')

assert breaker.is_open('test_api') == True

# Test recovery
breaker.record_success('test_api')
assert breaker.is_open('test_api') == False

print("✅ Circuit breaker tests passed")
EOF
```

### Phase 2: Integration Testing (Day 3-5)

Test with real data sources:

```bash
# Test 1: Single source (Sina Finance)
python3 << 'EOF'
import asyncio
from scripts.async_cn_market_demo import fetch_sina_quotes_async
import aiohttp

async def test():
    async with aiohttp.ClientSession() as session:
        params = {'tickers': ['600519', '000001']}
        result = await fetch_sina_quotes_async(session, params)
        assert 'quotes' in result
        assert len(result['quotes']) > 0
        print(f"✅ Fetched {len(result['quotes'])} quotes")

asyncio.run(test())
EOF

# Test 2: All sources in parallel
python3 scripts/async_cn_market_demo.py 2>&1 | tee test_output.log

# Verify output
if grep -q "✅ Report generation complete" test_output.log; then
    echo "✅ Integration test passed"
else
    echo "❌ Integration test failed"
    exit 1
fi
```

### Phase 3: Performance Testing (Day 6-7)

Compare sync vs async performance:

```bash
# Benchmark script
cat > benchmark_async.sh << 'EOF'
#!/bin/bash

echo "=== Performance Benchmark ==="
echo ""

# Test sync version (original)
echo "Testing SYNC version..."
export CN_MARKET_USE_ASYNC=false
time python3 scripts/cn_market_report.py > /dev/null 2>&1
SYNC_TIME=$?

echo ""
echo "Testing ASYNC version..."
export CN_MARKET_USE_ASYNC=true
time python3 scripts/async_cn_market_demo.py > /dev/null 2>&1
ASYNC_TIME=$?

echo ""
echo "=== Results ==="
echo "Sync time: See above"
echo "Async time: See above"
echo ""
echo "Run this script 5 times and average the results"
EOF

chmod +x benchmark_async.sh
./benchmark_async.sh
```

### Phase 4: Data Consistency Testing (Day 8-10)

Ensure async produces same results as sync:

```bash
# Data consistency checker
python3 << 'EOF'
import json
from datetime import datetime

# Load both outputs
with open('reports/cn_daily_digest_2026-03-18.md') as f:
    sync_report = f.read()

with open('reports/cn_daily_digest_async_2026-03-18.md') as f:
    async_report = f.read()

# Compare key sections (ignoring timestamps)
def extract_stocks(report):
    """Extract stock codes from report"""
    import re
    return set(re.findall(r'[0-9]{6}', report))

sync_stocks = extract_stocks(sync_report)
async_stocks = extract_stocks(async_report)

# Check overlap (should be >90%)
overlap = len(sync_stocks & async_stocks)
total = len(sync_stocks | async_stocks)

consistency = overlap / total if total > 0 else 0

print(f"Data consistency: {consistency:.1%}")

if consistency >= 0.9:
    print("✅ Consistency check passed")
else:
    print(f"❌ Consistency check failed: {consistency:.1%}")
    print(f"Sync only: {sync_stocks - async_stocks}")
    print(f"Async only: {async_stocks - sync_stocks}")
EOF
```

---

## Deployment Process

### Stage 1: Canary Deployment (Week 1)

Deploy to 10% of traffic:

```bash
# Step 1: Deploy to production
git checkout main
git pull origin main

# Copy async files
cp scripts/async_*.py /opt/openclaw/scripts/

# Step 2: Enable for 10% of requests
cat > /opt/openclaw/config/traffic_split.conf << 'EOF'
# Traffic split configuration
ASYNC_TRAFFIC_PERCENTAGE=10
EOF

# Step 3: Monitor for 48 hours
tail -f /var/log/openclaw/cn_market.log | grep -E "async|error|performance"

# Step 4: Check metrics
python3 << 'EOF'
import json
from glob import glob

# Load recent performance logs
logs = sorted(glob('/var/log/openclaw/performance_*.json'))[-100:]

async_times = []
sync_times = []

for log_file in logs:
    with open(log_file) as f:
        data = json.load(f)

    if data.get('mode') == 'async':
        async_times.append(data.get('duration_ms', 0))
    else:
        sync_times.append(data.get('duration_ms', 0))

if async_times and sync_times:
    avg_async = sum(async_times) / len(async_times)
    avg_sync = sum(sync_times) / len(sync_times)
    improvement = (avg_sync - avg_async) / avg_sync * 100

    print(f"Async average: {avg_async:.0f}ms")
    print(f"Sync average: {avg_sync:.0f}ms")
    print(f"Improvement: {improvement:.1f}%")

    if improvement > 30:
        print("✅ Performance target met - proceed to Stage 2")
    else:
        print("⚠️  Performance below target - investigate")
EOF
```

### Stage 2: Gradual Rollout (Week 2)

Increase to 50% traffic:

```bash
# Update traffic split
sed -i 's/ASYNC_TRAFFIC_PERCENTAGE=10/ASYNC_TRAFFIC_PERCENTAGE=50/' \
    /opt/openclaw/config/traffic_split.conf

# Restart service
systemctl restart openclaw-analyst

# Monitor for 24 hours
```

### Stage 3: Full Deployment (Week 2 End)

Switch to 100% async:

```bash
# Update configuration
cat > /opt/openclaw/.env.cn_market << 'EOF'
CN_MARKET_USE_ASYNC=true
EOF

# Restart
systemctl restart openclaw-analyst

# Verify
curl http://localhost/api/cn-market-report | jq '.performance'

# Should show async=true and duration < 25000ms
```

---

## Rollback Procedure

### Emergency Rollback (5 minutes)

If critical issues occur:

```bash
# Step 1: Disable async mode
echo "CN_MARKET_USE_ASYNC=false" > /opt/openclaw/.env.cn_market

# Step 2: Restart service
systemctl restart openclaw-analyst

# Step 3: Verify rollback
curl http://localhost/api/cn-market-report | jq '.mode'
# Should return "sync"

# Step 4: Check logs
tail -n 100 /var/log/openclaw/cn_market.log
```

### Partial Rollback (30 minutes)

Rollback specific data sources:

```python
# scripts/async_cn_market_demo.py

# Disable problematic source
sources = [
    # DataSource('ths_diagnosis', fetch_ths_diagnosis_async, ...),  # DISABLED
    DataSource('stock_quotes', fetch_sina_quotes_async, ...),
    # ... other sources
]
```

### Full Rollback (1 hour)

Revert to previous version:

```bash
# Step 1: Restore from backup
rm -rf scripts
mv scripts.backup.20260318 scripts

# Step 2: Restore git version
git revert HEAD
git push origin main

# Step 3: Deploy previous version
./deploy.sh v1.0.1-stable

# Step 4: Verify
python3 scripts/cn_market_report.py
```

---

## Monitoring & Validation

### Key Metrics to Track

Create monitoring dashboard:

```python
# monitoring_dashboard.py

import json
from datetime import datetime, timedelta
from glob import glob

def generate_dashboard():
    """Generate performance dashboard"""

    # Load last 24 hours of data
    cutoff = datetime.now() - timedelta(hours=24)
    logs = []

    for log_file in sorted(glob('reports/cn_market_data_async_*.json'))[-100:]:
        with open(log_file) as f:
            logs.append(json.load(f))

    # Calculate metrics
    total_runs = len(logs)
    successful_runs = sum(1 for log in logs if 'error' not in log)
    success_rate = successful_runs / total_runs if total_runs > 0 else 0

    durations = [
        log.get('performance', {}).get('total_time_parallel_ms', 0)
        for log in logs
    ]

    avg_duration = sum(durations) / len(durations) if durations else 0
    p95_duration = sorted(durations)[int(len(durations) * 0.95)] if durations else 0

    cache_hits = [
        log.get('performance', {}).get('cache_hit_rate', 0)
        for log in logs
    ]
    avg_cache_hit = sum(cache_hits) / len(cache_hits) if cache_hits else 0

    # Print dashboard
    print("=" * 60)
    print("📊 China Market Async Performance Dashboard")
    print("=" * 60)
    print(f"Period: Last 24 hours ({total_runs} runs)")
    print("")
    print(f"Success Rate:     {success_rate:.1%}")
    print(f"Avg Duration:     {avg_duration:.0f}ms")
    print(f"P95 Duration:     {p95_duration:.0f}ms")
    print(f"Avg Cache Hit:    {avg_cache_hit:.1%}")
    print("")

    # Status indicators
    if avg_duration < 25000 and success_rate > 0.95:
        print("✅ Status: HEALTHY")
    elif avg_duration < 30000 and success_rate > 0.90:
        print("⚠️  Status: DEGRADED")
    else:
        print("❌ Status: CRITICAL")

    print("=" * 60)

if __name__ == '__main__':
    generate_dashboard()
```

Run monitoring:

```bash
# Add to crontab - run every hour
0 * * * * cd /opt/openclaw && python3 monitoring_dashboard.py >> /var/log/openclaw/dashboard.log 2>&1

# View current status
python3 monitoring_dashboard.py
```

### Alert Configuration

Set up alerts for critical metrics:

```bash
# alert_rules.yaml

alerts:
  - name: high_failure_rate
    condition: success_rate < 0.90
    severity: critical
    message: "China market report success rate below 90%"

  - name: slow_performance
    condition: p95_duration > 30000
    severity: warning
    message: "China market report P95 latency above 30s"

  - name: low_cache_hit_rate
    condition: cache_hit_rate < 0.30
    severity: warning
    message: "Cache hit rate below 30%"

  - name: circuit_breaker_open
    condition: circuit_breaker_open == true
    severity: critical
    message: "Circuit breaker triggered for data source"
```

---

## Troubleshooting

### Issue 1: AsyncIO Event Loop Error

**Symptom**: `RuntimeError: no running event loop`

**Solution**:

```python
# Wrong:
data = await fetch_data()

# Correct:
import asyncio
data = asyncio.run(fetch_data())
```

### Issue 2: Timeout Errors

**Symptom**: Frequent timeout errors for specific sources

**Solution**:

```python
# Increase timeout for slow sources
DataSource(
    name='ths_diagnosis',
    fetch_func=fetch_ths_diagnosis_async,
    timeout=60,  # Increase from 30 to 60
    max_retries=5  # More retries
)
```

### Issue 3: Memory Leak

**Symptom**: Memory usage grows over time

**Solution**:

```python
# Ensure session cleanup
async with AsyncDataOrchestrator(cache) as orchestrator:
    results = await orchestrator.fetch_all_sources(sources)
# Session automatically closed here

# Clear cache periodically
cache.clear()
```

### Issue 4: Data Inconsistency

**Symptom**: Async results differ from sync

**Solution**:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Compare outputs
diff reports/cn_daily_digest_2026-03-18.md \
     reports/cn_daily_digest_async_2026-03-18.md

# Check for race conditions in data parsing
```

### Issue 5: Cache Not Working

**Symptom**: Cache hit rate always 0%

**Solution**:

```python
# Verify cache key generation
cache = SimpleCacheManager()
key = cache.generate_key('test_source', {'param': 'value'})
print(f"Generated key: {key}")

# Check cache expiration
cache.set(key, {'data': 'test'}, ttl=300)
print(f"Can retrieve: {cache.get(key) is not None}")

# Verify TTL is not too short
DataSource(
    name='market_rankings',
    cache_ttl=300,  # At least 5 minutes
)
```

---

## Success Criteria

Migration is considered successful when:

- [ ] Average report generation time < 25s (vs 38.98s baseline)
- [ ] Success rate > 95% (same as sync version)
- [ ] Data consistency > 95% match with sync version
- [ ] Cache hit rate > 30% after 1 week
- [ ] Zero critical bugs in production for 1 week
- [ ] Memory usage stable (no leaks)
- [ ] All monitoring alerts configured and working

---

## Post-Migration Checklist

After successful migration:

- [ ] Update documentation
- [ ] Archive sync version code
- [ ] Remove feature flags (after 1 month stable)
- [ ] Schedule Phase 2 implementation (DiskCache, BeautifulSoup)
- [ ] Document lessons learned
- [ ] Share performance improvements with team

---

## Next Steps

After Phase 1 is stable:

1. **Week 3-4**: Implement Phase 2 (DiskCache, anti-scraping)
2. **Week 5-6**: Implement Phase 3 (Tencent auth, monitoring)
3. **Week 7**: Performance audit and optimization
4. **Week 8**: Documentation and knowledge transfer

---

## Support

If you encounter issues during migration:

1. Check logs: `/var/log/openclaw/cn_market.log`
2. Run diagnostics: `python3 scripts/async_architecture_core.py`
3. Review this guide's troubleshooting section
4. Rollback if necessary (see Rollback Procedure)
5. Open GitHub issue with logs and error messages

---

**Document Version**: 1.0
**Last Updated**: 2026-03-18
**Status**: Ready for Implementation
