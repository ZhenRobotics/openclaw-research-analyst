# Security Policy - Research Analyst v1.3.0

**Last Updated**: 2026-03-26
**Status**: Active Development

---

## 🔒 Security Overview

This skill fetches financial data from public APIs and optionally integrates with third-party services. **Review this document before installation.**

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

### Optional Features (Credentials Required)

**Twitter/X Integration** (scripts/rumor_detector.py, scripts/trend_scanner.py):
- `https://twitter.com/*` - via bird CLI
- **Requires**: Browser session cookies (AUTH_TOKEN, CT0)
- **Risk**: Session hijacking if cookies leaked
- **Recommendation**: Use read-only credentials, rotate frequently

**Feishu/Lark Integration** (scripts/feishu_push.py):
- `https://open.feishu.cn/open-apis/*` - Feishu Open API
- **Requires**: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_WEBHOOK
- **Risk**: Message sending, potential spam if credentials leaked
- **Recommendation**: Create limited-scope bot with message-only permission

---

## 🔑 Credential Management

### Core Features: NO CREDENTIALS NEEDED ✅

The following features work **without any API keys**:
- `/stock` - Stock analysis (Yahoo Finance + Sina Finance fallback)
- `/cn_market` - China market report
- `/portfolio` - Portfolio management
- `/stock_dividend` - Dividend analysis
- All China data sources (东方财富, 财联社, 腾讯, 同花顺)

### Optional Features: Credentials Required ⚠️

#### 1. Twitter/X Sentiment Analysis

**What it does**:
- `scripts/rumor_detector.py` - Scans Twitter for market rumors
- `scripts/trend_scanner.py` - Detects viral trends

**Credentials needed**:
```bash
# In .env file
AUTH_TOKEN="your_twitter_auth_token"
CT0="your_twitter_ct0_cookie"
```

**How to obtain** (Advanced users only):
1. Login to X.com in browser
2. Open DevTools → Application → Cookies
3. Copy `auth_token` and `ct0` values
4. **WARNING**: These are full-access session tokens!

**Security recommendations**:
```bash
# Create .env with strict permissions
touch .env
chmod 600 .env  # Owner read/write only

# Add credentials
echo 'AUTH_TOKEN="..."' >> .env
echo 'CT0="..."' >> .env

# NEVER commit .env to git
git add .gitignore  # Ensure .env is ignored
```

**Risks**:
- ❌ Session tokens grant full account access
- ❌ If leaked, attacker can post/DM as you
- ❌ Tokens can be scraped from process list

**Mitigation**:
1. **Use a burner/test account** for testing
2. **Rotate tokens weekly** (logout/login to invalidate)
3. **Monitor account activity** for unauthorized posts
4. **Revoke immediately** if suspicious activity detected
5. **Consider OAuth App** instead (requires bird CLI setup)

#### 2. Feishu/Lark Push Notifications

**What it does**:
- `scripts/feishu_push.py` - Sends analysis results to Feishu group chat

**Credentials needed**:
```bash
# In .env.feishu file
FEISHU_APP_ID="cli_xxxx"
FEISHU_APP_SECRET="xxxx"
FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxxx"
```

**How to obtain**:
1. Create Feishu bot at https://open.feishu.cn/
2. Enable "Message Sending" permission only
3. Copy App ID, Secret, and Webhook URL

**Security recommendations**:
```bash
# Create .env.feishu with strict permissions
touch .env.feishu
chmod 600 .env.feishu

# Use webhook instead of App ID/Secret when possible
# Webhooks are limited to one group chat
echo 'FEISHU_WEBHOOK="https://..."' >> .env.feishu
```

**Risks**:
- ⚠️ Webhook can spam group chat
- ⚠️ App credentials can send messages to any user (if FEISHU_USER_OPEN_ID set)

**Mitigation**:
1. **Use webhook** (limited to one group) instead of app credentials
2. **Create test group** for initial testing
3. **Monitor message history** for unauthorized sends
4. **Revoke webhook** if suspicious activity

---

## 🛡️ Security Best Practices

### Before Installation

#### 1. Review Code Before Running

**Inspect network calls**:
```bash
# Clone repo
git clone https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst

# Search for network calls
grep -r "requests\|urllib\|http" scripts/*.py | less

# Review specific scripts
cat scripts/rumor_detector.py
cat scripts/feishu_push.py
cat scripts/trend_scanner.py
```

**Check for suspicious patterns**:
- ❌ No `eval()` or `exec()` found
- ❌ No `os.system()` with user input found
- ❌ No git clone of external repos found
- ✅ All endpoints are legitimate financial data sources

#### 2. Isolated Environment

**Run in container** (Recommended):
```bash
# Using Docker
docker run -it --rm \
  -v "$(pwd)":/app \
  -w /app \
  python:3.11-slim \
  bash

# Install dependencies
pip install -r requirements.txt

# Test without credentials
python3 scripts/stock_analyzer.py AAPL
```

**Run as non-root user** (Linux/macOS):
```bash
# Create limited user
sudo useradd -m -s /bin/bash stockbot
sudo su - stockbot

# Clone and test
git clone https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst
python3 scripts/stock_analyzer.py AAPL
```

#### 3. Credential Hygiene

**DO**:
- ✅ Create test/burner accounts for Twitter integration
- ✅ Use limited-scope credentials (message-only for Feishu)
- ✅ Store credentials in `.env` with `chmod 600` permissions
- ✅ Rotate credentials after testing
- ✅ Monitor account activity for unauthorized use
- ✅ Use separate credentials per environment (dev/prod)

**DON'T**:
- ❌ Use your main Twitter account credentials
- ❌ Commit `.env` to git
- ❌ Share credentials in screenshots or logs
- ❌ Run as root user
- ❌ Use production Feishu bot for testing

### During Installation

#### NPM Package Security

**bird CLI** (Optional Twitter integration):
```bash
# Review package before installing
npm info @steipete/bird

# Install in isolated directory (not globally)
mkdir ~/bird-cli
cd ~/bird-cli
npm install @steipete/bird

# Add to PATH instead of global install
export PATH="$HOME/bird-cli/node_modules/.bin:$PATH"
```

**Supply-chain risk mitigation**:
1. **Review package.json** before `npm install`
2. **Check for postinstall scripts** (potential malware)
3. **Use npm audit** to check for known vulnerabilities
4. **Consider alternatives**: Manual API calls instead of bird CLI

#### Python Dependencies

**Review requirements.txt**:
```bash
# Check dependencies
cat requirements.txt

# Install with pip-audit (security scanner)
pip install pip-audit
pip-audit -r requirements.txt

# Install dependencies
pip install -r requirements.txt
```

**Known dependencies**:
- `yfinance` - Yahoo Finance API wrapper (community-maintained)
- `pandas` - Data manipulation (NumFOCUS project)
- `feedparser` - RSS parser (standard library)
- `requests` - HTTP library (widely trusted)
- `beautifulsoup4` - HTML parser (widely trusted)

### After Installation

#### File Permissions Audit

```bash
# Check .env file permissions
ls -l .env .env.feishu 2>/dev/null

# Should show: -rw------- (600)
# If not, fix:
chmod 600 .env .env.feishu
```

#### Monitor Runtime Behavior

**Check network connections** (Linux):
```bash
# While running stock_analyzer.py
sudo netstat -tupn | grep python3

# Should only show connections to:
# - query1.finance.yahoo.com:443
# - hq.sinajs.cn:80
# - (other documented endpoints)
```

**Check process environment** (credentials leak check):
```bash
# Ensure credentials not in process args
ps aux | grep python3

# Should NOT show AUTH_TOKEN or CT0 in command line
```

#### Test with Dummy Credentials

```bash
# Test Feishu with invalid webhook (should fail gracefully)
export FEISHU_WEBHOOK="https://invalid.example.com/hook"
python3 scripts/feishu_push.py "Test message"

# Expected: Error message, no crash, no data leak
```

---

## 🚨 Incident Response

### If Credentials Leaked

**Twitter/X tokens**:
```bash
# 1. Immediately logout from all devices
Visit: https://twitter.com/settings/sessions

# 2. Change password
Visit: https://twitter.com/settings/password

# 3. Review account activity
Visit: https://twitter.com/settings/your_twitter_data/account_activity

# 4. Revoke third-party apps
Visit: https://twitter.com/settings/connected_apps
```

**Feishu credentials**:
```bash
# 1. Revoke webhook
Visit: Feishu bot settings → Regenerate webhook

# 2. Rotate App Secret
Visit: https://open.feishu.cn/ → Your app → Credentials → Regenerate

# 3. Review message history
Check Feishu group for unauthorized messages
```

### If Suspicious Behavior Detected

**Immediate actions**:
1. **Stop all running processes**: `pkill -f stock_analyzer.py`
2. **Remove credentials**: `rm .env .env.feishu`
3. **Review logs**: `cat logs/*.log`
4. **Check git status**: `git status` (ensure no uncommitted creds)
5. **Report issue**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues

**Forensics**:
```bash
# Check recent file modifications
find . -type f -mtime -1 -ls

# Check network history (if logging enabled)
cat logs/*.log | grep -E "http|request"

# Check process history
history | grep -E "export|env"
```

---

## 📊 Security Audit Log

### Known Issues

**None currently reported**

### Security Fixes

| Date | Version | Issue | Fix |
|------|---------|-------|-----|
| 2026-03-26 | v1.3.0 | Credentials in git history | Removed with git-filter-repo |
| 2026-03-26 | v1.3.0 | .env file tracked | Added to .gitignore |
| 2026-03-26 | v1.3.0 | Hardcoded paths | Made configurable via env vars |

---

## 🔍 Code Review Findings

### Network Calls Audit (2026-03-26)

**Reviewed scripts**:
- ✅ `scripts/stock_analyzer.py` - Only calls Yahoo/Sina Finance
- ✅ `scripts/cn_*.py` - Only calls documented China data sources
- ✅ `scripts/portfolio_manager.py` - No network calls (local only)
- ⚠️ `scripts/rumor_detector.py` - Calls Twitter via bird CLI (optional)
- ⚠️ `scripts/feishu_push.py` - Calls Feishu API (optional)
- ⚠️ `scripts/trend_scanner.py` - Calls Google News + CoinGecko (public)

**Suspicious patterns**: None found

**Recommendations**:
1. Add timeout to all `urllib.request.urlopen()` calls ✅ (Already done)
2. Add User-Agent headers to avoid scraping detection ✅ (Already done)
3. Implement retry logic with exponential backoff ✅ (Already done)
4. Add rate limiting to avoid API abuse ⏳ (TODO)

---

## 📞 Reporting Security Issues

**DO NOT** open public GitHub issues for security vulnerabilities.

**Instead**:
1. Email: [Your security contact email]
2. Encrypt with GPG: [Your GPG key ID]
3. Include: Affected version, steps to reproduce, potential impact

**Response time**: Within 48 hours

---

## 📚 Additional Resources

**Official Documentation**:
- Yahoo Finance API: https://github.com/ranaroussi/yfinance
- Sina Finance API: (Undocumented, public web scraping)
- bird CLI: https://github.com/steipete/bird

**Security Tools**:
- `pip-audit`: https://github.com/pypa/pip-audit
- `bandit`: https://github.com/PyCQA/bandit (Python security linter)
- `safety`: https://github.com/pyupio/safety (Dependency vulnerability scanner)

**Security Guides**:
- Python Security Best Practices: https://python.readthedocs.io/en/stable/library/security_warnings.html
- OWASP Top 10: https://owasp.org/www-project-top-ten/

---

## ✅ Security Checklist

Before using this skill:

- [ ] Read this SECURITY.md document
- [ ] Review code in `scripts/` directory
- [ ] Verify network endpoints match documented list
- [ ] Install in isolated environment (container/VM/separate user)
- [ ] Create test credentials (not production)
- [ ] Set `.env` file permissions to 600
- [ ] Test core features without credentials first
- [ ] Monitor account activity after enabling Twitter/Feishu
- [ ] Rotate credentials after testing
- [ ] Subscribe to security updates (GitHub Watch)

---

**Last Reviewed**: 2026-03-26
**Next Review**: 2026-04-26 (Monthly)
**Reviewer**: Claude Sonnet 4.5 + User Audit

---

## 📄 License & Disclaimer

This software is provided "AS IS" without warranty. See LICENSE file.

**NOT FINANCIAL ADVICE**: This tool is for informational purposes only.

**SECURITY**: Use at your own risk. Review all code before running with credentials.
