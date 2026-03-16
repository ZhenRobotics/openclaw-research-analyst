# Installation Guide - OpenClaw Research Analyst v1.0.0

**⚠️ Security Notice**: This package contains **13 Python scripts** with **6063 lines of verified source code**. All code is open source and available at: https://github.com/ZhenRobotics/openclaw-research-analyst

---

## 📦 What's Included

This package contains:
- ✅ **13 Python scripts** (6063 lines)
- ✅ **Full source code** (not obfuscated)
- ✅ **MIT License** (open source)
- ✅ **No telemetry or tracking**
- ✅ **No external credential collection**

## 🔒 Security Verification

Before installing, you can verify the package contents:

```bash
# Clone and inspect
git clone https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst

# View all scripts
ls -la scripts/

# Read any script
cat scripts/stock_analyzer.py

# Check dependencies
cat pyproject.toml
```

---

## 📋 Prerequisites

### Required
1. **Python 3.10 or higher**
   ```bash
   python3 --version  # Should be 3.10+
   ```

2. **uv package manager**
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Or via Homebrew
   brew install uv

   # Or via pip
   pip install uv
   ```

3. **Git**
   ```bash
   git --version
   ```

### Optional (for advanced features)

4. **bird CLI** (Twitter/X integration)
   ```bash
   npm install -g @steipete/bird
   ```

5. **Environment variables** (Twitter/X only)
   - `AUTH_TOKEN` - Your X.com auth token
   - `CT0` - Your X.com CT0 token

   Get these from browser DevTools → Application → Cookies → x.com

---

## 🚀 Installation

### Method 1: Git Clone (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst

# 2. Install Python dependencies
uv sync

# 3. Verify installation
uv run scripts/stock_analyzer.py --help
```

### Method 2: npm (if published)

```bash
# Install globally
npm install -g openclaw-research-analyst

# Or install locally
npm install openclaw-research-analyst
```

---

## ✅ Verification

Run these commands to verify everything works:

```bash
# Test stock analysis
uv run scripts/stock_analyzer.py AAPL --fast

# Test dividend analysis
uv run scripts/dividend_analyzer.py JNJ

# Test hot scanner (no credentials needed)
python3 scripts/trend_scanner.py --no-social

# Run unit tests
uv run pytest scripts/tests.py -v
```

---

## 🔐 Required Credentials

### None Required for Core Features!

The following features work **without any credentials**:
- ✅ Stock analysis (Yahoo Finance - public API)
- ✅ Crypto analysis (CoinGecko - public API)
- ✅ Dividend analysis
- ✅ Portfolio management (local storage)
- ✅ Watchlist & alerts (local storage)
- ✅ China market data (public APIs)
- ✅ Google News scanning

### Optional Credentials

**Twitter/X Integration** (Optional):
- Only needed for social sentiment analysis
- Create `.env` file:
  ```env
  AUTH_TOKEN=your_auth_token_here
  CT0=your_ct0_token_here
  ```
- Get tokens from browser: DevTools → Application → Cookies → x.com
- Never share these tokens!

---

## 📊 Data Sources & APIs

All data sources used are **public APIs** that do NOT require authentication:

| Service | Purpose | Credentials |
|---------|---------|-------------|
| Yahoo Finance | Stock prices, fundamentals | ❌ None |
| CoinGecko | Crypto data | ❌ None |
| Google News | News articles | ❌ None |
| SEC EDGAR | Insider trading | ❌ None |
| 东方财富 | China A-shares | ❌ None |
| 新浪财经 | China quotes | ❌ None |
| 财联社 | China news | ❌ None |
| 腾讯财经 | Money flow | ❌ None |
| 同花顺 | Stock diagnosis | ❌ None |
| Twitter/X | Social sentiment | ✅ Optional |

---

## 🗂️ File Structure

```
openclaw-research-analyst/
├── scripts/
│   ├── stock_analyzer.py          # Main analysis (2537 lines)
│   ├── dividend_analyzer.py        # Dividend analysis
│   ├── portfolio_manager.py        # Portfolio tracking
│   ├── watchlist_manager.py        # Alerts system
│   ├── trend_scanner.py            # Hot scanner
│   ├── rumor_detector.py           # Rumor detection
│   ├── cn_market_report.py         # China market report
│   ├── cn_market_rankings.py       # 东方财富
│   ├── cn_stock_quotes.py          # 新浪财经
│   ├── cn_cls_telegraph.py         # 财联社
│   ├── cn_tencent_moneyflow.py     # 腾讯财经
│   ├── cn_ths_diagnosis.py         # 同花顺
│   └── tests.py                    # Unit tests
├── docs/
│   ├── README.md                   # Documentation index
│   ├── USAGE.md                    # Usage guide
│   ├── ARCHITECTURE.md             # Technical details
│   └── CN_DATA_SOURCES.md          # China data sources
├── README.md                       # Project overview
├── SKILL.md                        # OpenClaw skill definition
├── INSTALL.md                      # This file
├── package.json                    # npm configuration
├── pyproject.toml                  # Python dependencies
└── .env.example                    # Environment template
```

---

## 🆘 Troubleshooting

### "uv: command not found"
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Then restart terminal
```

### "Python 3.10+ required"
```bash
# Install Python 3.10+
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# Verify
python3 --version
```

### "Module not found" errors
```bash
# Reinstall dependencies
uv sync --reinstall
```

### Twitter/X integration not working
- This is **optional**
- All core features work without it
- Check `.env` file format
- Verify AUTH_TOKEN and CT0 values

---

## 📞 Support

- **GitHub Issues**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues
- **Documentation**: https://github.com/ZhenRobotics/openclaw-research-analyst/tree/main/docs
- **Source Code**: https://github.com/ZhenRobotics/openclaw-research-analyst

---

## ⚖️ License

MIT License - See LICENSE file for details.

## ⚠️ Disclaimer

**NOT FINANCIAL ADVICE.** This tool is for informational and educational purposes only. Always do your own research and consult a licensed financial advisor before making investment decisions.

---

**Generated**: 2026-03-16
**Version**: 1.0.0
**Verified Lines of Code**: 6063
