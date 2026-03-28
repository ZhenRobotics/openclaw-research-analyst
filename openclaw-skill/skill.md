---
name: research-analyst
description: Local stock/crypto analysis using Python scripts. Uses public APIs only. No credentials required. All code included and reviewed by ClawHub.
version: 1.4.0
homepage: https://github.com/ZhenRobotics/openclaw-research-analyst
commands:
  - /stock - Analyze stock/crypto
  - /cn_market - China market report
  - /portfolio - Portfolio management (local storage)
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3","pip"]}}}
---

# Research Analyst v1.4.0

**Local financial analysis tool** - Analyze stocks, cryptocurrencies, and China markets using public APIs.

## What This Skill Does

Runs Python analysis scripts locally to analyze:
- 📈 **US Stocks** - AAPL, MSFT, GOOGL, etc.
- 🪙 **Crypto** - BTC, ETH, and major cryptocurrencies
- 🇨🇳 **China Markets** - A-shares, Hong Kong stocks
- 💰 **Dividends** - Yield analysis and income ratings
- 📊 **Portfolio** - Local portfolio tracking
- 👀 **Watchlist** - Price alerts (local storage)

**Zero credentials required.** All data from public APIs:
- Yahoo Finance (stocks/crypto quotes)
- CoinGecko (crypto data)
- Google News (financial news)
- China market data sources (东方财富, 新浪财经, etc.)

---

## 🔒 Security Model

### Bundled Code Architecture

**v1.4.0+ uses bundled code** instead of downloading from GitHub:

✅ **All code included** - Python scripts packaged with this skill
✅ **ClawHub reviewed** - Code reviewed during skill submission
✅ **No external downloads** - No git clone or runtime code fetching
✅ **Faster installation** - Code already present, just install dependencies
✅ **Lower risk** - No execution of external/unreviewed code

**Previous versions (v1.3.x)** downloaded code from GitHub at runtime. **v1.4.0** eliminates this by bundling all code in the skill package.

### What Gets Installed

When you install this skill, you get:

1. **Python scripts** (~50KB, 26 files)
   - All in `scripts/` directory
   - Reviewed by ClawHub during submission
   - Source: https://github.com/ZhenRobotics/openclaw-research-analyst

2. **Dependencies from PyPI** (installed separately)
   - `yfinance`, `requests`, `beautifulsoup4`, `lxml`, etc.
   - See requirements.txt for full list with SHA256 hashes
   - Standard, widely-used packages (~50M+ downloads each)

3. **Verification script**
   - `verify_install.sh` - Optional security checks
   - Scans for suspicious patterns
   - Validates dependencies

---

## Installation

### Requirements

- **Python 3.10+**
- **pip** (Python package installer)

### Installation Steps

**1. Install the skill** (if using OpenClaw/ClawHub)
```bash
claw install research-analyst
```

**2. Navigate to skill directory**
```bash
cd ~/.clawdbot/skills/research-analyst/
# Or wherever your skill installation directory is
```

**3. (Optional) Run verification script**
```bash
bash verify_install.sh
# Checks:
# - Python scripts for suspicious patterns
# - Dependencies in requirements.txt
# - File integrity
```

**4. Install Python dependencies**
```bash
# With hash verification (recommended)
pip install --require-hashes -r requirements.txt

# Or standard install
pip install -r requirements.txt
```

**5. Test installation**
```bash
python3 scripts/stock_analyzer.py --help
```

That's it! No git clone, no GPG verification, no external downloads.

---

## Quick Start

### US Stocks
```bash
python3 scripts/stock_analyzer.py AAPL
python3 scripts/stock_analyzer.py AAPL MSFT GOOGL
```

### Crypto
```bash
python3 scripts/stock_analyzer.py BTC-USD ETH-USD
```

### China Markets
```bash
# A-shares (Shenzhen)
python3 scripts/stock_analyzer.py 002168.SZ

# A-shares (Shanghai)
python3 scripts/stock_analyzer.py 600519.SS

# Hong Kong
python3 scripts/stock_analyzer.py 0700.HK

# Market report
python3 scripts/cn_market_report.py --async
```

### Dividends
```bash
python3 scripts/dividend_analyzer.py JNJ PG KO
```

### Portfolio Management
```bash
# View portfolio
python3 scripts/portfolio_manager.py show

# Add position
python3 scripts/portfolio_manager.py add AAPL --quantity 100 --cost 150

# Remove position
python3 scripts/portfolio_manager.py remove AAPL
```

### Watchlist
```bash
# Add alert
python3 scripts/watchlist_manager.py add AAPL --target 200 --stop 150

# Check alerts
python3 scripts/watchlist_manager.py check

# List all
python3 scripts/watchlist_manager.py list
```

---

## Features

### Stock Analysis (8 Dimensions)

Analyzes stocks across 8 dimensions with weighted scoring:

1. **Earnings** (30%) - Revenue growth, profit margins, earnings quality
2. **Fundamentals** (20%) - P/E, P/B, ROE, debt ratios
3. **Analysts** (20%) - Consensus ratings, target prices, upgrades/downgrades
4. **Historical** (10%) - Long-term performance, volatility
5. **Market** (10%) - Trading volume, liquidity, market conditions
6. **Sector** (15%) - Sector performance, relative strength
7. **Momentum** (15%) - Recent price action, technical indicators
8. **Sentiment** (10%) - News sentiment, social mentions

**Output**: Overall score (0-100), dimension breakdown, recommendation

### Crypto Analysis

- Market cap and dominance
- 24h/7d/30d price changes
- BTC correlation
- Trading volume analysis
- CoinGecko trending rank

### China Market Data Sources

All public, no authentication required:

- **东方财富** (East Money) - Market data, quotes
- **新浪财经** (Sina Finance) - Real-time quotes
- **财联社** (CLS) - Financial news, market telegraph
- **腾讯财经** (Tencent Finance) - Money flow data
- **同花顺** (THS) - Technical diagnosis

### Portfolio Tracking

**Local storage** (~/.clawdbot/skills/research-analyst/portfolios.json):
- Track positions (ticker, quantity, cost basis)
- Calculate unrealized P&L
- Portfolio composition
- Performance metrics

### Watchlist Alerts

**Local storage** (~/.clawdbot/skills/research-analyst/watchlist.json):
- Price targets (upside alerts)
- Stop losses (downside alerts)
- Percentage-based alerts
- Notification on breach

---

## Supported Markets

| Market | Format | Example |
|--------|--------|---------|
| US Stocks | TICKER | AAPL, MSFT, GOOGL |
| Crypto | TICKER-USD | BTC-USD, ETH-USD |
| A-shares (Shenzhen) | CODE.SZ | 002168.SZ |
| A-shares (Shanghai) | CODE.SS | 600519.SS |
| Hong Kong | CODE.HK | 0700.HK, 9988.HK |

---

## Data Flow & Privacy

### What Gets Fetched (Read-Only)

- Stock quotes from `query1.finance.yahoo.com`
- Crypto data from `api.coingecko.com`
- News from `news.google.com`
- China market data from public sources (listed above)

**All requests are HTTP GET** - read-only, no data upload.

### What Gets Sent

- **API queries only** (ticker symbols, date ranges)
- **No authentication** headers or credentials
- **No personal data**
- **No analytics** or tracking

### What Stays Local

- All analysis results (computed locally)
- Portfolio data (`~/.clawdbot/skills/research-analyst/portfolios.json`)
- Watchlist data (`~/.clawdbot/skills/research-analyst/watchlist.json`)
- Cached API responses (optional, local only)

**No data leaves your machine** except for public API queries.

---

## Dependency Trust

### Bundled Code (This Repository)

✅ **Reviewed by ClawHub** during skill submission
✅ **Source available**: https://github.com/ZhenRobotics/openclaw-research-analyst
✅ **Open source**: MIT-0 license, fully inspectable

**Our claim**: "No data sent beyond read-only API queries"
**Verification**: Review `scripts/` directory in skill installation

### PyPI Dependencies

**Installed separately** from PyPI (not controlled by this skill):

- `yfinance` - ~50M downloads, Yahoo Finance API client
- `requests` - ~500M downloads, Python HTTP library
- `beautifulsoup4` - ~100M downloads, HTML parser
- `lxml` - ~60M downloads, XML/HTML processor
- `pandas` - ~100M downloads, data analysis library
- `numpy` - ~200M downloads, numerical computing

**Trust decision**: These packages are widely-used and established, but you must trust the PyPI ecosystem. They can execute code during installation.

**Mitigation**:
- Install in virtual environment
- Review requirements.txt (includes SHA256 hashes)
- Use `pip install --require-hashes` for integrity verification

---

## Security Best Practices

### Recommended Installation

```bash
# 1. Create isolated environment
python3 -m venv venv
source venv/bin/activate

# 2. Run verification (optional)
bash verify_install.sh

# 3. Install with hash verification
pip install --require-hashes -r requirements.txt

# 4. Test
python3 scripts/stock_analyzer.py AAPL
```

### Code Review

**Bundled code is already reviewed by ClawHub**, but you can still inspect:

```bash
# View main analysis script
cat scripts/stock_analyzer.py

# Check for network calls (should only see GET requests)
grep -r "requests\." scripts/

# Check for data transmission (should see NO POST)
grep -ri "method.*post\|requests\.post" scripts/

# Check for subprocess calls
grep -r "subprocess\|os\.system" scripts/
```

### Sandboxing (Optional)

For extra security:
```bash
# Run in Docker container
docker run -it -v $(pwd):/app python:3.10 bash
cd /app && pip install -r requirements.txt
python3 scripts/stock_analyzer.py AAPL
```

---

## Verification Script

**verify_install.sh** performs 7 automated checks:

1. ✅ Python environment (version check)
2. ✅ File integrity (no modifications)
3. ✅ SHA256 hashes in requirements.txt
4. ✅ Suspicious pattern scanning (eval, exec, subprocess)
5. ✅ Network pattern scanning (POST requests)
6. ✅ Key files present
7. ✅ No unusual network imports

**Usage**:
```bash
bash verify_install.sh
# Exit code 0: All checks passed
# Exit code 1: Critical errors detected
```

**Results**:
- `✓ ALL CHECKS PASSED` - Safe to use
- `⚠ PASSED WITH WARNINGS` - Review warnings
- `✗ VERIFICATION FAILED` - Do not proceed

---

## Troubleshooting

### Import Errors

```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Verify installation
pip list | grep yfinance
```

### Permission Errors

```bash
# Create data directory
mkdir -p ~/.clawdbot/skills/research-analyst/

# Check permissions
ls -la ~/.clawdbot/skills/research-analyst/
```

### API Rate Limits

Yahoo Finance and CoinGecko have rate limits:
- **Yahoo Finance**: ~2000 requests/hour
- **CoinGecko**: 50 calls/minute (free tier)

**Solution**: Add delays between requests or use caching.

### China Market Data

Some China data sources may be inaccessible outside China:
- Use VPN if needed
- Some features may return empty results

---

## Limitations

- **Yahoo Finance data** may lag 15-20 minutes
- **Short interest data** lags ~2 weeks (exchange reporting delay)
- **Breaking news** uses keyword-based filtering, 1h cache
- **China market data** may require VPN outside China
- **Crypto data** limited to CoinGecko's coverage

---

## Architecture Changes (v1.4.0)

### What Changed

**v1.3.x (Download Model)**:
```
Install skill → git clone repo → verify → install deps → run
Risk: Downloads and executes external code
```

**v1.4.0+ (Bundled Model)**:
```
Install skill (code included) → install deps → run
Risk: Only PyPI dependencies (standard practice)
```

### Why This Change

1. **Remove "Suspicious" flag** - No more external code execution
2. **Faster installation** - No git clone needed
3. **ClawHub review** - Code reviewed during submission
4. **Better UX** - Simpler installation process

### Trade-offs

**Advantages**:
- ✅ Lower security risk
- ✅ Faster installation
- ✅ No git/gpg required
- ✅ Code pre-reviewed

**Disadvantages**:
- ⚠️ Larger skill package (~600KB vs ~20KB)
- ⚠️ Updates require skill re-publishing
- ⚠️ Can't pull latest code from GitHub

**For latest development version**, see: https://github.com/ZhenRobotics/openclaw-research-analyst

---

## Support

- **Issues**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues
- **Documentation**: https://github.com/ZhenRobotics/openclaw-research-analyst
- **Security**: https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/SECURITY.md
- **Source Code**: https://github.com/ZhenRobotics/openclaw-research-analyst

---

## License

**MIT-0** (Public Domain) - Free to use, modify, and redistribute. No attribution required.

https://spdx.org/licenses/MIT-0.html

---

## Disclaimer

⚠️ **NOT FINANCIAL ADVICE**

This tool is for informational and educational purposes only. Not financial, investment, or trading advice. Always do your own research and consult with qualified financial advisors before making investment decisions.

---

## Changelog

### v1.4.0 (2026-03-28)

**Major architecture change**: Bundled code model

- ✅ All Python scripts now bundled with skill
- ✅ No more git clone or external downloads
- ✅ ClawHub reviews code during submission
- ✅ Simpler installation process
- ✅ Removes "Suspicious" flag (no external code execution)
- 📦 Larger package size (~600KB vs ~20KB)

**Migration from v1.3.x**: No action needed for new installs. Existing users can continue using v1.3.x or upgrade to v1.4.0.

### v1.3.3 (2026-03-27)

- Enhanced security warnings and transparency
- Added GPG signature verification
- Technical controls (verify_install.sh, SHA256 hashes)
- Registry metadata alignment

---

Built for OpenClaw 🦞
