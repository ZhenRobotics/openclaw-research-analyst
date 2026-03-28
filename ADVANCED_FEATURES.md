# Advanced Features (Optional)

**⚠️ WARNING: This document describes OPTIONAL advanced features that require HIGH-RISK credentials.**

**You do NOT need anything in this document to use the skill. All core features work without it.**

---

## 🐦 Twitter/X Social Signals (OPTIONAL - HIGH RISK)

**Risk Level:** 🔴 **HIGH**
**Required:** browser session cookies (AUTH_TOKEN, CT0)
**Benefit:** Adds Twitter sentiment to rumor scanner
**Default behavior:** Auto-skipped - uses Google News instead

### Why This Is High Risk

- Browser session cookies grant **session-level access** to your Twitter account
- More sensitive than typical API keys
- Can be used until you log out of Twitter
- Requires third-party CLI (`bird`) that may have security issues

### Safer Alternatives

1. **Don't enable it** - Rumor scanner works great with Google News only
2. **Use Twitter API v2** - Apply for developer account (requires approval)
3. **Run in isolated VM** - Test in sandbox environment first

### If You Still Want To Enable

**Step 1: Install bird CLI**
```bash
npm install -g @steipete/bird
```

**Step 2: Get browser cookies**
1. Login to x.com in Safari/Chrome
2. Open DevTools → Application → Cookies → x.com
3. Find `auth_token` and `ct0` cookies
4. Copy the values

**Step 3: Create .env file**
```bash
# Create with strict permissions
touch .env && chmod 600 .env

# Add credentials
echo "AUTH_TOKEN=your_auth_token_here" >> .env
echo "CT0=your_ct0_here" >> .env
```

**Step 4: Audit the code first**
```bash
# Review how credentials are used
cat scripts/rumor_detector.py | grep -A 10 "AUTH_TOKEN"
cat scripts/trend_scanner.py | grep -A 10 "AUTH_TOKEN"
```

**Step 5: Test**
```bash
python3 scripts/rumor_detector.py
# Should now include Twitter results
```

### What Gets Enabled

- Rumor scanner includes Twitter whispers
- Trend scanner includes Twitter buzz
- No other changes

---

## 🔔 Feishu Push Notifications (OPTIONAL - MEDIUM RISK)

**Risk Level:** 🟡 **MEDIUM**
**Required:** Feishu bot OAuth tokens
**Benefit:** Sends reports to Feishu chat
**Default behavior:** Auto-skipped - saves to local files instead

### Why This Is Medium Risk

- Requires creating a Feishu bot app
- OAuth tokens can send messages on your behalf
- Need to configure webhook or user Open ID

### Setup

**Step 1: Create Feishu bot**
1. Go to https://open.feishu.cn/app
2. Create new app
3. Grant ONLY "Send messages" permission
4. Get APP_ID and APP_SECRET

**Step 2: Run setup wizard**
```bash
python3 scripts/feishu_setup.py
```

**Step 3: Test**
```bash
python3 scripts/feishu_push.py --test
```

### What Gets Enabled

- China market reports can be pushed to Feishu
- News alerts can be pushed to Feishu
- All features still save local copies

---

## ⏰ Scheduled Reports (Cron Jobs)

**Risk Level:** 🟡 **MEDIUM**
**Why risky:** Runs automatically, could spam if misconfigured

### Before Setting Up Cron

1. **Test commands manually first**
```bash
python3 scripts/cn_market_brief.py --push
# Check Feishu to confirm message sent to correct chat
```

2. **Start with longer intervals**
- Use daily (not hourly) at first
- Monitor logs for first week

3. **Use full paths**
```bash
# Bad: Relative paths
0 9 * * * cd scripts && python3 cn_market_brief.py

# Good: Absolute paths
0 9 * * * cd /full/path/to/openclaw-research-analyst && python3 scripts/cn_market_brief.py >> /tmp/market.log 2>&1
```

### Example Cron Jobs

**Daily market brief at 9 AM:**
```bash
0 9 * * * cd /path/to/skill && python3 scripts/cn_market_brief.py --push >> /tmp/market.log 2>&1
```

**Hourly news monitoring (fast mode):**
```bash
0 * * * * cd /path/to/skill && python3 scripts/news_monitor_fast.py --no-ai --interval 60 >> /tmp/news.log 2>&1
```

---

## 🔍 Security Audit Commands

**Before enabling any advanced feature, run these:**

### 1. Verify no secrets in git history
```bash
git log --all --full-history --source -- .env* --source -- '*secret*' --source -- '*token*'
# Should be empty
```

### 2. Find where credentials are used
```bash
# Twitter credentials
grep -rn "AUTH_TOKEN\|CT0" scripts/

# Feishu credentials
grep -rn "FEISHU_APP_ID\|FEISHU_APP_SECRET" scripts/
```

### 3. Check network endpoints
```bash
grep -rn "requests\.\|aiohttp\.\|urllib" scripts/ | grep -E "get\(|post\("
```

### 4. Review file permissions
```bash
ls -la .env*
# Should be: -rw------- (600)

# Fix if needed
chmod 600 .env .env.feishu
```

---

## 📋 Decision Matrix

**Should I enable advanced features?**

| Your Situation | Twitter | Feishu | Recommendation |
|----------------|---------|--------|----------------|
| Just want stock analysis | ❌ No | ❌ No | Don't enable anything |
| Want social sentiment | ⚠️ Maybe | ❌ No | Consider API keys instead |
| Want push notifications | ❌ No | ✅ Yes | Feishu is safer than Twitter |
| Security paranoid | ❌ No | ❌ No | Core features only |
| Need automation | ❌ No | ✅ Yes | Cron + Feishu (no Twitter) |

---

## 🛡️ Best Practices

1. **Never commit credentials**
```bash
# Verify .gitignore
grep ".env" .gitignore
```

2. **Use separate environments**
```bash
# Dev
.env.dev

# Production
.env.prod
```

3. **Rotate credentials regularly**
- Feishu: Every 90 days
- Twitter: Log out and back in monthly

4. **Monitor logs**
```bash
tail -f /tmp/market.log
# Watch for unusual activity
```

5. **File permissions**
```bash
# Lock down
chmod 600 .env .env.feishu

# Verify
ls -la .env*
```

---

## 🆘 Troubleshooting

### Twitter not working

**Check bird CLI:**
```bash
which bird
bird --version
```

**Check credentials:**
```bash
cat .env | grep "AUTH_TOKEN\|CT0"
# Should show your tokens
```

**Test bird directly:**
```bash
bird search "stock" -n 5 --json
```

### Feishu not working

**Check credentials:**
```bash
cat .env.feishu | grep "FEISHU_"
```

**Test manually:**
```bash
python3 scripts/feishu_push.py --test
```

### Cron not running

**Check cron logs:**
```bash
# macOS
tail -f /var/log/cron.log

# Linux
tail -f /var/log/syslog | grep CRON
```

**Test with full path:**
```bash
/usr/bin/python3 /full/path/to/scripts/cn_market_brief.py
```

---

## 📖 Related Documents

- **SECURITY.md** - Full security documentation
- **README.md** - General usage (no advanced features)
- **SKILL.md** - ClawHub skill description (core features only)
- **ESSENTIAL_FIX_SUMMARY.md** - How graceful degradation works

---

**Remember:** You do NOT need anything in this document. All core features work perfectly without Twitter, Feishu, or cron jobs.
