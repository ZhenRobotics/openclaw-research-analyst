# ClawHub Pre-Submission Checklist
## OpenClaw Research Analyst - Critical Fixes Required

**Status**: NEEDS WORK
**Severity**: HIGH RISK - Credential Exposure

---

## CRITICAL: Execute Before Any Git Push

### 1. Remove Active Credentials (5 minutes)

```bash
cd /home/justin/openclaw-research-analyst

# STEP 1: Remove .env file with exposed API keys
rm .env

# STEP 2: Verify it's gone
ls -la .env 2>/dev/null && echo "ERROR: .env still exists!" || echo "✓ .env removed"

# STEP 3: Check for any remaining credential patterns
echo "Scanning for leaked credentials..."
grep -r "sk-proj-" . --exclude-dir=.git 2>/dev/null && echo "WARNING: Found OpenAI keys" || echo "✓ No OpenAI keys"
grep -r "LTAI5tMh" . --exclude-dir=.git 2>/dev/null && echo "WARNING: Found Aliyun keys" || echo "✓ No Aliyun keys"
```

### 2. Revoke Exposed API Keys (10 minutes)

**MUST DO IMMEDIATELY**:

1. **OpenAI API Key** (sk-proj-[REDACTED])
   - Go to: https://platform.openai.com/api-keys
   - Find and revoke key starting with "sk-proj-VsUD..."
   - Generate new key if needed for development

2. **Aliyun Access Key** (LTAI[REDACTED])
   - Go to: https://ram.console.aliyun.com/manage/ak
   - Disable or delete AccessKey: LTAI[REDACTED]
   - Create new key if needed

### 3. Fix Git Configuration (2 minutes)

```bash
# Add .env.cn_market to .gitignore
echo "" >> .gitignore
echo "# Additional env files" >> .gitignore
echo ".env.cn_market" >> .gitignore

# Verify gitignore
cat .gitignore | grep -E "\.env"
```

### 4. Clean Working Directory (2 minutes)

```bash
# Remove Python bytecode
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Remove untracked reports
rm -f CLAWHUB_EVALUATION_REPORT.md
rm -f CLAWHUB_PUBLISHING_STEPS_v1.3.0.md
rm -f CLAWHUB_SECURITY_WARNING_EXPLAINED.md
rm -f CLAWHUB_UPDATE_v1.3.0.md
rm -f FEISHU_CONFIG_FIX.md
rm -f RELEASE_COMPLETE_v1.3.0.md
rm -f SECURITY_AUDIT_REPORT.md
rm -f SECURITY_FIX_SUMMARY.md

# Verify clean state
git status --short
```

### 5. Sync Version Numbers (3 minutes)

**Current State**:
- SKILL.md: v1.0.0 (OUTDATED)
- package.json: v1.3.0 (Current)
- Git latest: v6.3.1 (Development)

**Decision**: Use v1.3.0 for ClawHub (stable release)

```bash
# Update SKILL.md version
sed -i 's/version: 1.0.0/version: 1.3.0/' SKILL.md

# Verify change
grep "^version:" SKILL.md

# Update README.md header
sed -i 's/# 📈 OpenClaw Research Analyst v1.0/# 📈 OpenClaw Research Analyst v1.3.0/' README.md

# Verify change
head -1 README.md
```

### 6. Commit Security Fixes (2 minutes)

```bash
# Stage changes
git add .gitignore SKILL.md README.md

# Commit with clear message
git commit -m "🔒 Security: Prepare for ClawHub submission

- Remove active .env file with credentials
- Add .env.cn_market to .gitignore
- Sync version numbers to v1.3.0
- Clean working directory

Ref: CLAWHUB_SECURITY_REPORT.md"

# Verify commit
git log --oneline -1
```

---

## HIGH: Verify Before ClawHub Upload

### 7. Final Security Scan (5 minutes)

```bash
# Scan for any remaining credentials
echo "=== Final Credential Scan ==="
grep -rI "sk-proj-" . --exclude-dir=.git --exclude="*.md" 2>/dev/null && echo "⚠ Found credentials!" || echo "✓ No OpenAI keys"
grep -rI "LTAI[A-Za-z0-9]" . --exclude-dir=.git --exclude="*.md" 2>/dev/null && echo "⚠ Found credentials!" || echo "✓ No Aliyun keys"

# Check .env files
echo "=== .env File Status ==="
ls -la .env* 2>/dev/null || echo "✓ No .env files in working directory"

# Verify gitignore
echo "=== Gitignore Check ==="
git check-ignore .env && echo "✓ .env is gitignored" || echo "⚠ .env NOT gitignored"
git check-ignore .env.cn_market && echo "✓ .env.cn_market is gitignored" || echo "⚠ .env.cn_market NOT gitignored"

# Check for tracked .env files
echo "=== Git Tracked .env Files ==="
git ls-files | grep "\.env" || echo "✓ No .env files tracked"
```

### 8. Verify Version Consistency (2 minutes)

```bash
echo "=== Version Check ==="
echo -n "SKILL.md: "
grep "^version:" SKILL.md | awk '{print $2}'

echo -n "package.json: "
grep '"version"' package.json | head -1 | awk -F'"' '{print $4}'

echo -n "README.md: "
head -1 README.md | grep -oP 'v\d+\.\d+\.\d+'

echo ""
echo "All versions should show: 1.3.0"
```

### 9. Test Installation (5 minutes)

```bash
# Fresh clone test
cd /tmp
git clone /home/justin/openclaw-research-analyst test-install
cd test-install

# Check for credentials
ls -la .env 2>/dev/null && echo "⚠ .env found in clone!" || echo "✓ No .env in clone"

# Test uv sync
uv sync

# Test basic analysis
uv run scripts/stock_analyzer.py AAPL --fast

# Cleanup
cd /tmp
rm -rf test-install
```

---

## MEDIUM: ClawHub Upload Preparation

### 10. Create Clean Bundle (10 minutes)

```bash
# Create upload directory
mkdir -p /tmp/clawhub-research-analyst-v1.3.0
cd /home/justin/openclaw-research-analyst

# Copy only published files (from package.json "files" array)
cp -r scripts/ /tmp/clawhub-research-analyst-v1.3.0/
cp -r docs/ /tmp/clawhub-research-analyst-v1.3.0/
cp README.md /tmp/clawhub-research-analyst-v1.3.0/
cp SKILL.md /tmp/clawhub-research-analyst-v1.3.0/
cp INSTALL.md /tmp/clawhub-research-analyst-v1.3.0/
cp LICENSE /tmp/clawhub-research-analyst-v1.3.0/
cp .env.example /tmp/clawhub-research-analyst-v1.3.0/
cp .env.feishu.example /tmp/clawhub-research-analyst-v1.3.0/
cp package.json /tmp/clawhub-research-analyst-v1.3.0/
cp pyproject.toml /tmp/clawhub-research-analyst-v1.3.0/

# Verify bundle contents
echo "=== Bundle Contents ==="
ls -la /tmp/clawhub-research-analyst-v1.3.0/

# Final credential scan on bundle
echo "=== Bundle Credential Scan ==="
grep -r "sk-proj-" /tmp/clawhub-research-analyst-v1.3.0/ 2>/dev/null && echo "⚠ CREDENTIALS FOUND!" || echo "✓ No credentials"
grep -r "LTAI[A-Za-z0-9]" /tmp/clawhub-research-analyst-v1.3.0/ 2>/dev/null && echo "⚠ CREDENTIALS FOUND!" || echo "✓ No credentials"

# Check bundle size
du -sh /tmp/clawhub-research-analyst-v1.3.0/
```

### 11. GitHub Release (Optional, 10 minutes)

```bash
cd /home/justin/openclaw-research-analyst

# Tag release
git tag -a v1.3.0 -m "Release v1.3.0 - ClawHub Submission

Features:
- 8-dimension stock analysis
- China market data integration (5 sources)
- Portfolio management
- Watchlist & alerts
- Dividend analysis
- Hot scanner (trend detection)
- Rumor detector

Security:
- All credentials removed from repository
- Comprehensive credential documentation
- Open source code for verification"

# Push tag
git push origin v1.3.0

# Create GitHub release (via web UI or gh CLI)
gh release create v1.3.0 \
  --title "v1.3.0 - ClawHub Marketplace Release" \
  --notes "See SKILL.md for full feature list and installation instructions."
```

---

## ClawHub Upload Steps

### 12. Submit to ClawHub (15 minutes)

1. **Go to ClawHub Publisher Portal**
   - URL: https://clawhub.ai/publish
   - Login with your account

2. **Create New Skill**
   - Click "Publish New Skill"
   - Or update existing "research-analyst"

3. **Upload Bundle**
   - Upload from: /tmp/clawhub-research-analyst-v1.3.0/
   - Or create .tar.gz:
     ```bash
     cd /tmp
     tar -czf research-analyst-v1.3.0.tar.gz clawhub-research-analyst-v1.3.0/
     ```

4. **Fill Metadata Form**
   - **Name**: research-analyst
   - **Display Name**: OpenClaw Research Analyst
   - **Version**: 1.3.0
   - **Category**: Finance & Business
   - **Tags**: stock, crypto, analysis, portfolio, china-market, dividend, watchlist
   - **Short Description**: AI-powered US/China/HK stock & crypto research with 8-dimension analysis
   - **Icon**: 📈
   - **Repository**: https://github.com/ZhenRobotics/openclaw-research-analyst
   - **License**: MIT-0
   - **Required Binaries**: python3, uv
   - **Optional Binaries**: bird (npm package @steipete/bird)
   - **Environment Variables**: AUTH_TOKEN (optional), CT0 (optional)

5. **Review & Submit**
   - Preview how skill appears in marketplace
   - Test install command: `claw install research-analyst`
   - Submit for review

---

## Post-Submission Verification

### 13. Test Installation (After ClawHub Approval)

```bash
# Install from ClawHub
claw install research-analyst

# Verify commands
/stock AAPL
/stock_compare AAPL MSFT GOOGL
/stock_dividend JNJ
/portfolio
/stock_hot
/cn_market

# Check for credential prompts (should be optional)
# Test with --no-social flag for Twitter/X bypass
```

---

## Checklist Summary

### Must Do (CRITICAL)
- [ ] Remove .env file with active credentials
- [ ] Revoke OpenAI API key (sk-proj-VsUD...)
- [ ] Revoke Aliyun Access Key (LTAI[REDACTED])
- [ ] Add .env.cn_market to .gitignore
- [ ] Sync version numbers to v1.3.0
- [ ] Commit security fixes

### Should Do (HIGH)
- [ ] Clean Python bytecode
- [ ] Remove untracked report files
- [ ] Final credential scan
- [ ] Test fresh clone installation
- [ ] Create clean bundle

### Optional (MEDIUM)
- [ ] Create GitHub release tag v1.3.0
- [ ] Update GitHub README with security section
- [ ] Clean hardcoded paths in internal docs

---

## Estimated Timeline

| Task | Time | Priority |
|------|------|----------|
| Remove credentials & revoke keys | 15 min | CRITICAL |
| Fix gitignore & clean directory | 5 min | CRITICAL |
| Sync versions & commit | 5 min | CRITICAL |
| Final security verification | 10 min | HIGH |
| Create clean bundle | 10 min | HIGH |
| Upload to ClawHub | 15 min | HIGH |

**Total**: 60 minutes to submission-ready state

---

## Contact & Support

**Issues**: Report credential exposure or other security concerns immediately
**Documentation**: See CLAWHUB_SECURITY_REPORT.md for detailed analysis
**Repository**: https://github.com/ZhenRobotics/openclaw-research-analyst

---

**Generated**: 2026-03-25
**Status**: NEEDS WORK - Execute critical fixes before submission
