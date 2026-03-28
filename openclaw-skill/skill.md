---
name: research-analyst
description: Downloads Python scripts from GitHub for local stock/crypto analysis using public APIs. No credentials required.
version: 1.3.3
homepage: https://github.com/ZhenRobotics/openclaw-research-analyst
commands:
  - /stock - Analyze stock/crypto (requires git clone first)
  - /cn_market - China market report
  - /portfolio - Portfolio management (local storage)
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3","uv","git"]}}}
---

# Research Analyst v1.3.3

## What This Skill Does

Downloads Python analysis scripts from GitHub and runs them locally to analyze stocks, cryptocurrencies, and China markets using **public APIs only**.

**Zero credentials required for analysis.** All data fetched from public APIs.

---

## ⚠️ Important

- **External Code:** This skill instructs you to download code from GitHub
- **Local Execution:** Analysis runs on your machine, not on servers
- **Public APIs:** Fetches data from Yahoo Finance, CoinGecko, Google News
- **No Authentication:** Core features need no API keys or credentials

**Review the code before running:** https://github.com/ZhenRobotics/openclaw-research-analyst

---

## Installation

### Requirements
- Python 3.10+
- `uv` package manager
- `git`

### Steps

```bash
# 1. Install uv
brew install uv  # macOS
# or: pip install uv

# 2. Clone repository (use tagged release)
git clone --branch v1.3.3 --depth 1 \
  https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst

# 3. Verify integrity (optional but recommended)
git verify-tag v1.3.3

# 4. Install dependencies
uv sync

# 5. Test
python3 scripts/stock_analyzer.py --help
```

**What you downloaded:**
- ~50KB Python scripts
- Dependencies: yfinance, requests, beautifulsoup4
- No executables, only Python source code

---

## Core Features

### Stock Analysis

```bash
# US stocks
python3 scripts/stock_analyzer.py AAPL

# Multiple stocks
python3 scripts/stock_analyzer.py AAPL MSFT GOOGL

# Fast mode
python3 scripts/stock_analyzer.py AAPL --fast
```

**What it does:**
- Fetches data from `query1.finance.yahoo.com` (public)
- Runs 8-dimension analysis locally
- Prints results to terminal
- No data sent to external servers

**Metrics:**
- Earnings (30%), Fundamentals (20%), Analysts (20%)
- Historical (10%), Market (10%), Sector (15%)
- Momentum (15%), Sentiment (10%)

### Crypto Analysis

```bash
python3 scripts/stock_analyzer.py BTC-USD ETH-USD
```

**What it does:**
- Fetches from `api.coingecko.com` (public)
- Market cap, BTC correlation, momentum
- Local analysis only

### China Markets

```bash
# A-shares
python3 scripts/stock_analyzer.py 002168.SZ
python3 scripts/stock_analyzer.py 600519.SS

# Hong Kong
python3 scripts/stock_analyzer.py 0700.HK

# Market report
python3 scripts/cn_market_report.py --async
```

**Data sources (all public):**
- 东方财富 (East Money)
- 新浪财经 (Sina Finance)
- 财联社 (CLS)
- 腾讯财经 (Tencent Finance)
- 同花顺 (THS)

### Dividends

```bash
python3 scripts/dividend_analyzer.py JNJ PG KO
```

**Metrics:**
- Yield, payout ratio, 5-year growth
- Safety score (0-100), income rating

### Portfolio (Local Storage)

```bash
# View
python3 scripts/portfolio_manager.py show

# Add
python3 scripts/portfolio_manager.py add AAPL --quantity 100 --cost 150
```

**Storage:** `~/.clawdbot/skills/stock-analysis/portfolios.json`

### Watchlist (Local Storage)

```bash
# Add alerts
python3 scripts/watchlist_manager.py add AAPL --target 200 --stop 150

# Check
python3 scripts/watchlist_manager.py check
```

**Storage:** `~/.clawdbot/skills/stock-analysis/watchlist.json`

### Hot Scanner

```bash
python3 scripts/trend_scanner.py
```

**Sources:**
- CoinGecko trending
- Yahoo Finance movers
- Google News RSS

### Rumor Detector

```bash
python3 scripts/rumor_detector.py
```

**Sources:**
- Google News (M&A, insider trades, analyst actions)
- SEC EDGAR (public filings)

---

## Supported Markets

| Market | Format | Example |
|--------|--------|---------|
| US Stocks | `TICKER` | `AAPL`, `MSFT` |
| A-Shares (SZ) | `CODE.SZ` | `002168.SZ` |
| A-Shares (SH) | `CODE.SS` | `600519.SS` |
| Hong Kong | `CODE.HK` | `0700.HK` |
| Crypto | `TICKER-USD` | `BTC-USD`, `ETH-USD` |

---

## Data Flow

### What Gets Fetched
- Stock quotes from `query1.finance.yahoo.com`
- Crypto data from `api.coingecko.com`
- News from `news.google.com`
- China market data from public sources

### What Gets Sent
- **Read-only HTTP requests** to public APIs
- **No authentication headers**
- **No personal data**
- **No API keys**

### What Stays Local
- Analysis results
- Portfolio data
- Watchlist data
- All computations

**No data transmitted to external servers beyond read-only public API queries.**

---

## Security

### Code Review
```bash
# Review main analysis script
cat scripts/stock_analyzer.py

# Check for network calls
grep -r "requests\." scripts/

# Check for data transmission
grep -r "post\|POST" scripts/
```

### What to Look For
- ✅ Only GET requests to known public APIs
- ✅ No POST requests (no data upload)
- ✅ No authentication/API keys in code
- ✅ Local file I/O only for storage

### Source Code
- **Repository:** https://github.com/ZhenRobotics/openclaw-research-analyst
- **License:** MIT-0
- **Release:** v1.3.3 (tagged)

---

## Limitations

- Yahoo Finance may lag 15-20 minutes
- Short interest data lags ~2 weeks
- Breaking news: keyword-based, 1h cache

---

## Support

- **Issues:** https://github.com/ZhenRobotics/openclaw-research-analyst/issues
- **Documentation:** https://github.com/ZhenRobotics/openclaw-research-analyst
- **Security:** https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/SECURITY.md

---

## Disclaimer

⚠️ **NOT FINANCIAL ADVICE.** For informational purposes only.

⚠️ **REVIEW CODE BEFORE RUNNING.** This skill downloads and executes code from GitHub.

---

Built for [OpenClaw](https://openclaw.ai) 🦞
