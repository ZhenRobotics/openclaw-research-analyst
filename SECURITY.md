# Security Policy - Research Analyst v1.3.3

**Last Updated**: 2026-03-27
**Status**: Active Development

---

## 🔒 Security Overview

This skill downloads Python scripts from GitHub and runs them locally to analyze stocks and cryptocurrencies using **public APIs only**. All analysis runs on your machine, not on external servers.

**Zero credentials required** for core features.

---

## 🌐 Network Endpoints Called

### Core Functionality (No Credentials Required)

**Stock Data**:
- `https://query1.finance.yahoo.com/*` - Yahoo Finance API (public)
- `http://hq.sinajs.cn/*` - Sina Finance quotes (public)
- `http://query.sse.com.cn/*` - Shanghai Stock Exchange (public)
- `http://www.szse.cn/*` - Shenzhen Stock Exchange (public)

**China Market Data**:
- `http://quote.eastmoney.com/*` - 东方财富 rankings (public web scraping)
- `https://www.cls.cn/*` - 财联社 news (public RSS feeds)
- `http://qt.gtimg.cn/*` - 腾讯财经 money flow (public API)
- `http://basic.10jqka.com.cn/*` - 同花顺 diagnosis (public web scraping)

**Crypto & Market Data**:
- `https://api.coingecko.com/*` - CoinGecko API (public, no auth)
- `https://www.google.com/search?*` - Google News (public web scraping)

**What Gets Sent**:
- ✅ Read-only HTTP GET requests to public APIs
- ✅ Stock/crypto ticker symbols (e.g., "AAPL", "BTC-USD")
- ❌ No authentication headers
- ❌ No personal data
- ❌ No API keys

**What Stays Local**:
- ✅ All analysis results
- ✅ Portfolio data (`~/.clawdbot/skills/stock-analysis/portfolios.json`)
- ✅ Watchlist data (`~/.clawdbot/skills/stock-analysis/watchlist.json`)
- ✅ All computations

---

## 🔑 Credential Management

### Core Features: NO CREDENTIALS NEEDED ✅

The following features work **without any API keys or credentials**:
- Stock analysis (US, China, Hong Kong)
- Crypto analysis (top 20 cryptocurrencies)
- China market report
- Portfolio management (local storage)
- Watchlist management (local storage)
- Dividend analysis
- Hot scanner (trending assets)
- Rumor detector (public news sources)

### Data Sources

All data sources are **public and require no authentication**:
- Yahoo Finance - stock quotes, fundamentals
- CoinGecko - crypto market data
- Google News - breaking news headlines
- China market sources - A-share and Hong Kong data

---

## 📦 What Gets Downloaded

When you install this skill, you download:
- **~50KB of Python source code** (26 scripts)
- **Dependencies**: yfinance, requests, beautifulsoup4, lxml
- **No executables** - only Python source code
- **No telemetry or tracking**
- **No external credential collection**

**Installation uses version pinning**:
```bash
git clone --branch v1.3.3 --depth 1 \
  https://github.com/ZhenRobotics/openclaw-research-analyst.git
```

**Integrity verification**:
```bash
git verify-tag v1.3.3  # Verify code hasn't been tampered with
```

---

## 🔍 Code Review

Before running, you can review the code:

```bash
# Review main analysis script
cat scripts/stock_analyzer.py

# Check for network calls
grep -r "requests\." scripts/

# Check for data transmission (should only see GET requests)
grep -r "post\|POST" scripts/

# Verify no credentials hardcoded
grep -ri "api.key\|secret\|token\|password" scripts/
```

**What to look for**:
- ✅ Only GET requests to known public APIs
- ✅ No POST requests (no data upload)
- ✅ No authentication/API keys in code
- ✅ Local file I/O only for storage

---

## 🛡️ Security Best Practices

### For Users

1. **Review Before Installing**: Read the source code at GitHub
2. **Use Version Pinning**: Install specific tagged releases (v1.3.3)
3. **Verify Integrity**: Run `git verify-tag v1.3.3` after cloning
4. **Monitor Network**: Use firewall/network monitor to verify only public APIs called
5. **Local Storage**: Portfolio and watchlist data stored in `~/.clawdbot/skills/stock-analysis/`

### Isolation

- ✅ Skill runs as your user (no elevated privileges)
- ✅ Data stored in user directory (not system-wide)
- ✅ No background processes or daemons
- ✅ No system modifications

---

## 📊 Data Privacy

### What This Skill Does NOT Do

- ❌ Collect personal information
- ❌ Send data to external servers (beyond read-only API queries)
- ❌ Track your usage or analytics
- ❌ Require account creation
- ❌ Access your credentials or tokens
- ❌ Modify system settings
- ❌ Create persistent background processes

### What Gets Stored Locally

- Portfolio holdings (if you use portfolio features)
- Watchlist entries (if you use watchlist features)
- Temporary cache files (API responses, 1-hour TTL)

**Storage Location**: `~/.clawdbot/skills/stock-analysis/`

---

## 🚨 Reporting Security Issues

Found a security vulnerability? Please report it:

- **Email**: security@openclaw.ai (if available)
- **GitHub**: https://github.com/ZhenRobotics/openclaw-research-analyst/security/advisories/new
- **Private Disclosure**: Do not open public issues for security vulnerabilities

We take security seriously and will respond within 48 hours.

---

## 📜 License & Audit Trail

- **License**: MIT-0 (Public Domain equivalent)
- **Source Code**: https://github.com/ZhenRobotics/openclaw-research-analyst
- **Release**: v1.3.3 (tagged)
- **Commits**: All changes tracked in git history

---

## ✅ Security Checklist

Before installation:
- [ ] Read this security policy
- [ ] Review source code on GitHub
- [ ] Verify tagged release matches version
- [ ] Check git commit history for suspicious changes
- [ ] Understand what data sources are accessed

After installation:
- [ ] Monitor network traffic (should only see public API calls)
- [ ] Verify no unexpected processes running
- [ ] Check `~/.clawdbot/skills/stock-analysis/` for stored data
- [ ] Review permissions on local storage files

---

**Remember**: This skill requires downloading and executing external code. Only install if you trust the source and have reviewed the code.
