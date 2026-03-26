---
name: research-analyst
description: AI-powered US/China/HK stock & crypto research with 8-dimension analysis, China market reports (东方财富/新浪/财联社/腾讯/同花顺), portfolio tracking, and trend detection
version: 1.3.0
homepage: https://finance.yahoo.com
commands:
  - /stock - Analyze a stock or crypto (e.g., /stock AAPL)
  - /stock_compare - Compare multiple tickers
  - /stock_dividend - Analyze dividend metrics
  - /stock_watch - Add/remove from watchlist
  - /stock_alerts - Check triggered alerts
  - /stock_hot - Find trending stocks & crypto (Hot Scanner)
  - /stock_rumors - Find early signals, M&A rumors, insider activity (Rumor Scanner)
  - /cn_market - China A-share & Hong Kong market report (中国市场报告)
  - /cn_rankings - Market rankings from 东方财富 (榜单数据)
  - /cn_quotes - Stock quotes from 新浪财经 (实时行情)
  - /cn_news - Financial news from 财联社 (财经快讯)
  - /cn_moneyflow - Money flow analysis from 腾讯财经 (资金流向)
  - /cn_diagnosis - Stock diagnosis from 同花顺 (个股诊断)
  - /portfolio - Show portfolio summary
  - /portfolio_add - Add asset to portfolio
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3","uv"],"env":["AUTH_TOKEN","CT0"]},"install":[{"id":"python3-check","kind":"shell","command":"python3 --version","bins":["python3"],"label":"Verify Python 3.10+ installed"},{"id":"uv-brew","kind":"brew","formula":"uv","bins":["uv"],"label":"Install uv package manager"},{"id":"bird-npm","kind":"shell","command":"npm install -g @steipete/bird","bins":["bird"],"label":"Install bird CLI (optional, for Twitter/X)"}]}}
---

# OpenClaw Research Analyst v1.3.0

**⚠️ Installation Required**: This skill requires Python 3.10+, uv package manager, and optional dependencies. See installation instructions below.

**🔒 SECURITY NOTICE**: Core features require NO API keys (uses public data). Optional Twitter/Feishu integration requires credentials - **Review [SECURITY.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/SECURITY.md) before supplying any credentials.**

**📦 Source Code**: https://github.com/ZhenRobotics/openclaw-research-analyst

Analyze **US stocks, China A-shares, Hong Kong stocks**, and **cryptocurrencies** with 8-dimension analysis, **China market multi-source reports** (东方财富/新浪/财联社/腾讯/同花顺), portfolio management, watchlists, alerts, dividend analysis, and **viral trend detection**.

## 📦 Installation & Dependencies

### Required
- **Python 3.10+** - Core runtime
- **uv** - Python package manager (`brew install uv` or see https://github.com/astral-sh/uv)
- **Git** - To clone the repository

### Optional
- **bird CLI** - Twitter/X integration (`npm install -g @steipete/bird`)
- **Environment Variables** (for Twitter/X only):
  - `AUTH_TOKEN` - X.com auth token
  - `CT0` - X.com CT0 token

### Installation
```bash
# Clone from GitHub
git clone https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst

# Install Python dependencies
uv sync

# Verify installation
uv run scripts/stock_analyzer.py --help
```

### Security Note
- ✅ All source code is available at GitHub (verified)
- ✅ No credentials required for core functionality
- ✅ Twitter/X credentials stored in local .env file only
- ✅ All API calls use public endpoints (Yahoo Finance, CoinGecko, etc.)

## Core Features

- 📊 **8-Dimension Analysis** — Comprehensive stock scoring across earnings, fundamentals, analysts, momentum, sentiment, sector, market, and history
- 💰 **Dividend Analysis** — Yield, payout ratio, 5-year growth, safety score, income rating
- 📈 **Portfolio Management** — Track holdings, P&L, concentration warnings
- ⏰ **Watchlist + Alerts** — Price targets, stop losses, signal change notifications
- 🔥 **Hot Scanner** — Multi-source viral trend detection (CoinGecko, Google News, Twitter/X)
- 🔮 **Rumor Detector** — Early signals for M&A, insider trades, analyst actions
- 🌏 **China Markets** — A-share & Hong Kong data (东方财富, 新浪, 财联社, 腾讯, 同花顺)
- 🪙 **Crypto Support** — Top 20 cryptos with BTC correlation and momentum analysis
- ⚡ **Fast Mode** — Skip slow analyses for quick checks

## Quick Commands

### Stock Analysis
```bash
# Basic analysis
uv run {baseDir}/scripts/stock_analyzer.py AAPL

# Fast mode (skips insider trading & breaking news)
uv run {baseDir}/scripts/stock_analyzer.py AAPL --fast

# Compare multiple
uv run {baseDir}/scripts/stock_analyzer.py AAPL MSFT GOOGL

# Crypto
uv run {baseDir}/scripts/stock_analyzer.py BTC-USD ETH-USD
```

### Dividend Analysis```bash
# Analyze dividends
uv run {baseDir}/scripts/dividend_analyzer.py JNJ

# Compare dividend stocks
uv run {baseDir}/scripts/dividend_analyzer.py JNJ PG KO MCD --output json
```

**Dividend Metrics:**
- Dividend Yield & Annual Payout
- Payout Ratio (safe/moderate/high/unsustainable)
- 5-Year Dividend Growth (CAGR)
- Consecutive Years of Increases
- Safety Score (0-100)
- Income Rating (excellent/good/moderate/poor)

### Watchlist + Alerts```bash
# Add to watchlist
uv run {baseDir}/scripts/watchlist_manager.py add AAPL

# With price target alert
uv run {baseDir}/scripts/watchlist_manager.py add AAPL --target 200

# With stop loss alert
uv run {baseDir}/scripts/watchlist_manager.py add AAPL --stop 150

# Alert on signal change (BUY→SELL)
uv run {baseDir}/scripts/watchlist_manager.py add AAPL --alert-on signal

# View watchlist
uv run {baseDir}/scripts/watchlist_manager.py list

# Check for triggered alerts
uv run {baseDir}/scripts/watchlist_manager.py check
uv run {baseDir}/scripts/watchlist_manager.py check --notify  # Telegram format

# Remove from watchlist
uv run {baseDir}/scripts/watchlist_manager.py remove AAPL
```

**Alert Types:**
- 🎯 **Target Hit** — Price >= target
- 🛑 **Stop Hit** — Price <= stop
- 📊 **Signal Change** — BUY/HOLD/SELL changed

### Portfolio Management
```bash
# Create portfolio
uv run {baseDir}/scripts/portfolio_manager.py create "Tech Portfolio"

# Add assets
uv run {baseDir}/scripts/portfolio_manager.py add AAPL --quantity 100 --cost 150
uv run {baseDir}/scripts/portfolio_manager.py add BTC-USD --quantity 0.5 --cost 40000

# View portfolio
uv run {baseDir}/scripts/portfolio_manager.py show

# Analyze with period returns
uv run {baseDir}/scripts/stock_analyzer.py --portfolio "Tech Portfolio" --period weekly
```

### 🌏 China Market Reports
```bash
# Complete China market report (all sources)
python3 {baseDir}/scripts/cn_market_report.py

# Market rankings from 东方财富
python3 {baseDir}/scripts/cn_market_rankings.py

# Stock quotes from 新浪财经
python3 {baseDir}/scripts/cn_stock_quotes.py 600519  # 贵州茅台

# Financial news from 财联社
python3 {baseDir}/scripts/cn_cls_telegraph.py

# Money flow analysis from 腾讯财经
python3 {baseDir}/scripts/cn_tencent_moneyflow.py

# Stock diagnosis from 同花顺
python3 {baseDir}/scripts/cn_ths_diagnosis.py 600519
```

**China Data Sources (5 Major Platforms):**
- 📊 **东方财富 (East Money)** — Market rankings, sector analysis, hot stocks
- 💹 **新浪财经 (Sina Finance)** — Real-time quotes, A-share & Hong Kong
- 📰 **财联社 (CLS)** — Breaking financial news, market telegraph
- 💰 **腾讯财经 (Tencent Finance)** — Money flow analysis, capital tracking
- 🔍 **同花顺 (THS)** — Stock diagnosis, technical analysis

**What You Get:**
- A-share (沪深) and Hong Kong stock data
- Market hot lists and sector rotations
- Real-time capital flow tracking
- Breaking financial news and announcements
- Individual stock technical diagnosis

### 🔥 Hot Scanner
```bash
# Full scan - find what's trending NOW
python3 {baseDir}/scripts/trend_scanner.py

# Fast scan (skip social media)
python3 {baseDir}/scripts/trend_scanner.py --no-social

# JSON output for automation
python3 {baseDir}/scripts/trend_scanner.py --json
```

**Data Sources:**
- 📊 CoinGecko Trending — Top 15 trending coins
- 📈 CoinGecko Movers — Biggest gainers/losers
- 📰 Google News — Finance & crypto headlines
- 📉 Yahoo Finance — Gainers, losers, most active
- 🐦 Twitter/X — Social sentiment (requires auth)

**Output:**
- Top trending by mention count
- Crypto highlights with 24h changes
- Stock movers by category
- Breaking news with tickers

**Twitter Setup (Optional):**
1. Install bird: `npm install -g @steipete/bird`
2. Login to x.com in Safari/Chrome
3. Create `.env` with `AUTH_TOKEN` and `CT0`

### 🔮 Rumor Scanner```bash
# Find early signals, M&A rumors, insider activity
python3 {baseDir}/scripts/rumor_detector.py
```

**What it finds:**
- 🏢 **M&A Rumors** — Merger, acquisition, takeover bids
- 👔 **Insider Activity** — CEO/Director buying/selling
- 📊 **Analyst Actions** — Upgrades, downgrades, price target changes
- 🐦 **Twitter Whispers** — "hearing that...", "sources say...", "rumor"
- ⚖️ **SEC Activity** — Investigations, filings

**Impact Scoring:**
- Each rumor is scored by potential market impact (1-10)
- M&A/Takeover: +5 points
- Insider buying: +4 points
- Upgrade/Downgrade: +3 points
- "Hearing"/"Sources say": +2 points
- High engagement: +2 bonus

**Best Practice:** Run at 07:00 before US market open to catch pre-market signals.

## Analysis Dimensions (8 for stocks, 3 for crypto)

### Stocks
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Earnings Surprise | 30% | EPS beat/miss |
| Fundamentals | 20% | P/E, margins, growth |
| Analyst Sentiment | 20% | Ratings, price targets |
| Historical | 10% | Past earnings reactions |
| Market Context | 10% | VIX, SPY/QQQ trends |
| Sector | 15% | Relative strength |
| Momentum | 15% | RSI, 52-week range |
| Sentiment | 10% | Fear/Greed, shorts, insiders |

### Crypto
- Market Cap & Category
- BTC Correlation (30-day)
- Momentum (RSI, range)

## Sentiment Sub-Indicators

| Indicator | Source | Signal |
|-----------|--------|--------|
| Fear & Greed | CNN | Contrarian (fear=buy) |
| Short Interest | Yahoo | Squeeze potential |
| VIX Structure | Futures | Stress detection |
| Insider Trades | SEC EDGAR | Smart money |
| Put/Call Ratio | Options | Sentiment extreme |

## Risk Detection

- ⚠️ **Pre-Earnings** — Warns if < 14 days to earnings
- ⚠️ **Post-Spike** — Flags if up >15% in 5 days
- ⚠️ **Overbought** — RSI >70 + near 52w high
- ⚠️ **Risk-Off** — GLD/TLT/UUP rising together
- ⚠️ **Geopolitical** — Taiwan, China, Russia, Middle East keywords
- ⚠️ **Breaking News** — Crisis keywords in last 24h

## Performance Options

| Flag | Effect | Speed |
|------|--------|-------|
| (default) | Full analysis | 60-120s |
| `--no-insider` | Skip SEC EDGAR | 50-90s |
| `--fast` | Skip insider + news | 45-75s |

## Supported Cryptos (Top 20)

BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, DOT, MATIC, LINK, ATOM, UNI, LTC, BCH, XLM, ALGO, VET, FIL, NEAR

(Use `-USD` suffix: `BTC-USD`, `ETH-USD`)

## Data Storage

| File | Location |
|------|----------|
| Portfolios | `~/.clawdbot/skills/stock-analysis/portfolios.json` |
| Watchlist | `~/.clawdbot/skills/stock-analysis/watchlist.json` |

## Limitations

- Yahoo Finance may lag 15-20 minutes
- Short interest lags ~2 weeks (FINRA)
- Insider trades lag 2-3 days (SEC filing)
- US markets only (non-US incomplete)
- Breaking news: 1h cache, keyword-based

## Disclaimer

⚠️ **NOT FINANCIAL ADVICE.** For informational purposes only. Consult a licensed financial advisor before making investment decisions.
