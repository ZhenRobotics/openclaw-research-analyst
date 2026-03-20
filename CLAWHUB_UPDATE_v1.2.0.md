# ClawHub Update Content - v1.2.0

**用于 ClawHub 更新页面的内容**

---

## 🎉 v1.2.0 Major Update - One-Click Brief & Smart Scheduling

### 📊 One-Click Brief (一键精简简报)

Ultra-fast market summary generation with a single command.

**New Script**: `scripts/cn_market_brief.py`

**Usage**:
\`\`\`bash
# Generate brief summary
python3 scripts/cn_market_brief.py

# Generate and push to Feishu
python3 scripts/cn_market_brief.py --push

# JSON output for automation
python3 scripts/cn_market_brief.py --json
\`\`\`

**Output Example**:
\`\`\`
📊 10:30 市场快报

【A股】涨:中复神鹰+20.0% 跌:亨通光电-8.49% 额:兆易创新118亿
【港股】涨:毅高国际控股+98.0% 额:耀才证券金84亿

📄 已保存: reports/cn_market_brief_2026-03-18_1030.txt
\`\`\`

**Features**:
- ⚡ Ultra-fast generation (~2 seconds)
- 📊 Top 3 gainers/losers and volume leaders
- 💾 Auto-save to independent file
- 📱 Optional Feishu push integration
- 📋 JSON output for automation

**Documentation**: [One-click brief guide](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/OPTIMIZATION_COMPLETE.md)

---

### ⏰ Smart Scheduling (智能定时任务)

Intelligent cron jobs for trading hours with auto-skip weekends.

**New Script**: `scripts/cn_market_schedule.sh`

**Scheduling Rules**:
| Task | Time | Frequency | Cron |
|------|------|-----------|------|
| **Intraday Push** | Mon-Fri 09:30-15:00 | Every 10 minutes | `*/10 9-14 * * 1-5` |
| **EOD Report** | Mon-Fri 15:05 | Once per day | `5 15 * * 1-5` |

**Usage**:
\`\`\`bash
# Install cron jobs
./scripts/cn_market_schedule.sh install

# Check status
./scripts/cn_market_schedule.sh status

# Manual test
./scripts/cn_market_schedule.sh run-intraday  # Intraday push
./scripts/cn_market_schedule.sh run-eod       # EOD report

# View logs
./scripts/cn_market_schedule.sh logs

# Uninstall
./scripts/cn_market_schedule.sh uninstall
\`\`\`

**Smart Features**:
- ✅ Auto-skip weekends and holidays
- ✅ Auto-detect trading hours (09:30-15:00)
- ✅ Error recovery with automatic retry
- ✅ Comprehensive logging (`/tmp/cn_market_schedule.log`)
- ✅ One-command install/uninstall

**Execution Flow**:
\`\`\`
Cron trigger → Check weekday → Check trading hours →
Generate brief → Push to Feishu → Log result
\`\`\`

**Documentation**: [SMART_SCHEDULING.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/SMART_SCHEDULING.md) - Complete guide (11 KB)

---

### 🔧 Improvements

**Enhanced `--brief` Flag**:
- ✅ Clean output without JSON technical data
- ✅ Save to independent file: `reports/cn_market_brief_YYYY-MM-DD_HHMM.txt`
- ✅ Include generation time and report source

**Better Error Handling**:
- Improved network timeout handling
- Enhanced data source error recovery
- Clearer error logging

---

### 📚 New Documentation

**Complete Guides**:
1. **SMART_SCHEDULING.md** (11 KB)
   - Quick start (3 minutes)
   - Detailed configuration
   - Troubleshooting guide
   - Use cases

2. **OPTIMIZATION_COMPLETE.md**
   - Implementation report
   - Feature comparison
   - Migration guide

**Updated Files**:
- `skill.md` - Added `/cn_brief` command
- `readme.md` - Updated version and features

---

### 📦 Installation

\`\`\`bash
# npm (Recommended)
npm install -g openclaw-research-analyst

# or via ClawHub
clawhub install research-analyst

# Verify version
npm list -g openclaw-research-analyst
# Should show v1.2.0
\`\`\`

---

### 🔄 Upgrade from v1.1.0

\`\`\`bash
# npm
npm update -g openclaw-research-analyst

# ClawHub
clawhub update research-analyst

# Verify
npm view openclaw-research-analyst version
# Should show 1.2.0
\`\`\`

---

### 🎯 Use Cases

**Case 1: Personal Trader**
\`\`\`bash
# Configure Feishu push
source .env.feishu

# Install smart scheduling
./scripts/cn_market_schedule.sh install

# Result: Receive brief every 10 minutes during trading hours
\`\`\`

**Case 2: Team Collaboration**
\`\`\`bash
# Use Feishu group webhook
export FEISHU_WEBHOOK="https://..."

# Install scheduling
./scripts/cn_market_schedule.sh install

# Result: Team-wide market updates in group chat
\`\`\`

**Case 3: Automation**
\`\`\`bash
# JSON output for CI/CD
python3 scripts/cn_market_brief.py --json > output.json

# Integrate with other systems
curl -X POST "https://api.example.com/market" -d @output.json
\`\`\`

---

### ⚠️ Breaking Changes

**None**

v1.2.0 is fully backward compatible with v1.1.0. All existing features remain unchanged.

---

### 📊 Statistics

**New Files**:
- Scripts: 2 (cn_market_brief.py, cn_market_schedule.sh)
- Docs: 2 (SMART_SCHEDULING.md, OPTIMIZATION_COMPLETE.md)

**Code Changes**:
- Python: +500 lines
- Bash: +400 lines
- Markdown: +2,000 lines

**Performance**:
| Metric | Value |
|--------|-------|
| Brief generation time | ~2 seconds |
| Intraday pushes per day | ~24 (every 10 min) |
| EOD reports per day | 1 |

---

### 📞 Support

**Project Home**: https://github.com/ZhenRobotics/openclaw-research-analyst

**Issues**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues

**Full Release Notes**: [RELEASE_NOTES_v1.2.0.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/RELEASE_NOTES_v1.2.0.md)

**Documentation**:
- [SMART_SCHEDULING.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/SMART_SCHEDULING.md)
- [FEISHU_QUICKSTART.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/FEISHU_QUICKSTART.md)
- [OPTIMIZATION_COMPLETE.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/OPTIMIZATION_COMPLETE.md)

---

**Release Date**: 2026-03-18
**Version**: v1.2.0
**Commit**: 1b4d5ce (caf48dc + verified_commit update)
**Status**: ✅ **Live on npm & GitHub**
