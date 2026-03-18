# Release Notes v1.2.0

**发布日期**: 2026-03-18
**版本**: v1.2.0
**类型**: Minor Release（新功能）
**状态**: ✅ **准备发布**

---

## 🎉 New Features

### 📊 One-Click Brief (一键精简简报)

快速生成中国市场精简简报的独立命令。

**新增脚本**: `scripts/cn_market_brief.py` (5.0 KB)

**使用方法**:
```bash
# 生成精简简报
python3 scripts/cn_market_brief.py

# 生成并推送到飞书
python3 scripts/cn_market_brief.py --push

# JSON 格式输出（用于自动化）
python3 scripts/cn_market_brief.py --json
```

**输出示例**:
```
📊 10:30 市场快报

【A股】涨:中复神鹰+20.0% 跌:亨通光电-8.49% 额:兆易创新118亿
【港股】涨:毅高国际控股+98.0% 额:耀才证券金84亿

📄 已保存: reports/cn_market_brief_2026-03-18_1030.txt
```

**特性**:
- ⚡ 超快速生成（~2 秒）
- 📊 Top 3 gainers/losers 和成交额排名
- 💾 自动保存到独立文件
- 📱 可选飞书推送
- 📋 JSON 输出支持自动化

---

### ⏰ Smart Scheduling (智能定时任务)

交易时段智能推送 + 收盘日报自动生成。

**新增脚本**: `scripts/cn_market_schedule.sh` (13.5 KB)

**定时规则**:
| 任务 | 时间 | 频率 | Cron |
|------|------|------|------|
| 盘中推送 | 工作日 09:30-15:00 | 每 10 分钟 | `*/10 9-14 * * 1-5` |
| 收盘日报 | 工作日 15:05 | 每天一次 | `5 15 * * 1-5` |

**使用方法**:
```bash
# 安装定时任务
./scripts/cn_market_schedule.sh install

# 查看状态
./scripts/cn_market_schedule.sh status

# 手动测试
./scripts/cn_market_schedule.sh run-intraday  # 盘中推送
./scripts/cn_market_schedule.sh run-eod       # 收盘日报

# 查看日志
./scripts/cn_market_schedule.sh logs

# 卸载
./scripts/cn_market_schedule.sh uninstall
```

**智能特性**:
- ✅ 自动跳过周末和节假日
- ✅ 自动判断交易时段（09:30-15:00）
- ✅ 容错机制（网络错误自动重试）
- ✅ 完整日志记录（`/tmp/cn_market_schedule.log`）
- ✅ 一键安装/卸载

**执行逻辑**:
```
定时触发 → 检查工作日 → 检查交易时段 →
生成简报 → 推送飞书 → 记录日志
```

---

## 🔧 Improvements

### Enhanced `--brief` Output

**改进前**:
- 精简简报直接输出到 stdout
- JSON 技术指标混杂
- 无独立文件保存

**改进后**:
```bash
python3 scripts/cn_market_report.py --async --brief
```

**新输出**:
- ✅ 纯净 brief 输出（无 JSON 混杂）
- ✅ 保存到独立文件：`reports/cn_market_brief_YYYY-MM-DD_HHMM.txt`
- ✅ 包含生成时间和报告来源

**文件内容示例**:
```
📊 10:30 市场快报

【A股】涨:中复神鹰+20.0% 跌:亨通光电-8.49% 额:兆易创新118亿
【港股】涨:毅高国际控股+98.0% 额:耀才证券金84亿

生成时间: 2026-03-18 10:30:15
报告来源: cn_daily_digest_async_2026-03-18.md
```

### Error Handling

- 改进网络超时处理
- 增强数据源错误恢复
- 更清晰的错误日志

---

## 📚 Documentation

**新增文档**:
1. **SMART_SCHEDULING.md** (11 KB)
   - 完整的智能定时任务指南
   - 快速开始（3 分钟）
   - 详细配置说明
   - 故障排查指南

2. **OPTIMIZATION_COMPLETE.md**
   - 方案 A 实施报告
   - 功能对比
   - 使用场景

**更新文档**:
- `clawhub-upload/skill.md` - 新增 `/cn_brief` 命令
- `clawhub-upload/readme.md` - 更新版本和功能列表

---

## 📊 Statistics

### Code Changes
- **Python**: +500 lines (cn_market_brief.py, schedule.sh logic)
- **Bash**: +400 lines (cn_market_schedule.sh)
- **Markdown**: +2,000 lines (documentation)

### New Files
- Scripts: 2 个（cn_market_brief.py, cn_market_schedule.sh）
- Docs: 2 个（SMART_SCHEDULING.md, OPTIMIZATION_COMPLETE.md）
- Modified: 2 个（skill.md, readme.md, cn_market_report.py）

### Performance
| Metric | Value |
|--------|-------|
| Brief generation time | ~2 seconds |
| File size (brief) | ~200 bytes |
| Intraday pushes per day | ~24 (every 10 min) |
| EOD reports per day | 1 |

---

## 🔄 Migration Guide

### From v1.1.0 to v1.2.0

**1. 更新代码**:
```bash
# npm
npm update -g openclaw-research-analyst

# GitHub
git pull origin main

# ClawHub
clawhub install research-analyst
```

**2. 试用一键简报（可选）**:
```bash
cd /path/to/openclaw-research-analyst

# 测试一键简报
python3 scripts/cn_market_brief.py

# 推送测试
python3 scripts/cn_market_brief.py --push
```

**3. 安装智能定时（可选）**:
```bash
# 确保飞书推送已配置
cat .env.feishu

# 安装定时任务
./scripts/cn_market_schedule.sh install

# 验证
./scripts/cn_market_schedule.sh status
```

---

## ⚠️ Breaking Changes

**无**

v1.2.0 完全向后兼容 v1.1.0，所有现有功能保持不变。

---

## 🐛 Bug Fixes

- 修复 `--brief` 输出格式问题
- 改进网络超时处理
- 优化错误日志输出

---

## 🎯 Use Cases

### Case 1: 个人交易者
```bash
# 配置飞书私聊推送
source .env.feishu

# 安装智能定时
./scripts/cn_market_schedule.sh install

# 效果：交易时段每 10 分钟收到简报
```

### Case 2: 团队协作
```bash
# 使用飞书群 Webhook
export FEISHU_WEBHOOK="https://..."

# 安装定时任务
./scripts/cn_market_schedule.sh install

# 效果：团队群内实时同步
```

### Case 3: 自动化集成
```bash
# JSON 输出用于 CI/CD
python3 scripts/cn_market_brief.py --json > output.json

# 集成到其他系统
curl -X POST "https://api.example.com/market" -d @output.json
```

---

## 📞 Support

**项目主页**: https://github.com/ZhenRobotics/openclaw-research-analyst

**问题反馈**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues

**文档**:
- [SMART_SCHEDULING.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/SMART_SCHEDULING.md)
- [FEISHU_QUICKSTART.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/FEISHU_QUICKSTART.md)
- [OPTIMIZATION_COMPLETE.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/OPTIMIZATION_COMPLETE.md)

---

## 🙏 Acknowledgments

感谢以下贡献：
- **方案 A 实施**: 完整优化（一键简报 + 智能定时）
- **用户反馈**: 推动功能改进

---

## 📋 Changelog

**v1.2.0** (2026-03-18):
- ✨ 新增一键简报命令（`cn_market_brief.py`）
- ✨ 新增智能定时任务（`cn_market_schedule.sh`）
- 🔧 改进 `--brief` 输出格式
- 📚 新增 SMART_SCHEDULING.md 文档
- 🐛 修复网络超时问题

**v1.1.0** (2026-03-18):
- ✨ 飞书推送集成
- 🚀 异步架构优化（70-90% faster）
- 📚 完整的飞书推送文档

**v1.0.1** (2026-03-17):
- 🐛 修复网络超时问题
- 📝 添加 .npmignore

---

**发布时间**: 2026-03-18
**发布人**: ZhenRobotics Team
**版本**: v1.2.0
**状态**: ✅ **准备发布**
