# 智能定时任务指南
# Smart Scheduling Guide

**版本**: v1.2.0 (2026-03-18)
**功能**: 交易时段自动推送 + 收盘日报

---

## 📊 功能概览

中国市场智能定时任务自动在**交易时段**推送精简简报，并在**收盘后**生成完整日报。

### 核心特性

| 功能 | 时间 | 频率 | 说明 |
|------|------|------|------|
| **盘中推送** | 工作日 09:30-15:00 | 每 10 分钟 | 精简简报推送到飞书 |
| **收盘日报** | 工作日 15:05 | 每天一次 | 完整报告 + 精简推送 |
| **智能跳过** | 周末/节假日 | 自动 | 不在非交易日运行 |

---

## 🚀 快速开始（3 分钟）

### 步骤 1: 确保飞书推送已配置

```bash
# 检查配置文件
cat .env.feishu

# 应该包含以下内容之一：
# - FEISHU_USER_OPEN_ID (私聊推送)
# - FEISHU_WEBHOOK (群推送)
```

**未配置？** 查看 [FEISHU_QUICKSTART.md](FEISHU_QUICKSTART.md)

### 步骤 2: 安装定时任务

```bash
cd /home/justin/openclaw-research-analyst

# 安装
./scripts/cn_market_schedule.sh install

# 查看状态
./scripts/cn_market_schedule.sh status
```

### 步骤 3: 验证安装

```bash
# 查看 crontab
crontab -l | grep cn_market

# 应该看到两条任务：
# 1. */10 9-14 * * 1-5 ... run-intraday (盘中推送)
# 2. 5 15 * * 1-5 ... run-eod (收盘日报)
```

---

## 📅 定时任务详情

### 1. 盘中推送 (Intraday Push)

**时间**: 工作日 09:30-15:00，每 10 分钟
**Cron**: `*/10 9-14 * * 1-5`

**执行逻辑**:
1. ✅ 检查是否为工作日（Mon-Fri）
2. ✅ 检查是否在交易时段（09:30-15:00）
3. ✅ 生成精简简报
4. ✅ 推送到飞书（私聊或群）

**输出示例**:
```
📊 10:30 市场快报

【A股】涨:中复神鹰+20.0% 跌:亨通光电-8.49% 额:兆易创新118亿
【港股】涨:毅高国际控股+98.0% 额:耀才证券金84亿
```

**执行时间点** (每小时)：
- 09:30, 09:40, 09:50
- 10:00, 10:10, 10:20, 10:30, 10:40, 10:50
- 11:00, 11:10, 11:20
- 11:30 (午休开始，暂停到 13:00)
- 13:00, 13:10, 13:20, 13:30, 13:40, 13:50
- 14:00, 14:10, 14:20, 14:30, 14:40, 14:50

**总计**: 约 24 次/天

---

### 2. 收盘日报 (End-of-Day Report)

**时间**: 工作日 15:05
**Cron**: `5 15 * * 1-5`

**执行逻辑**:
1. ✅ 检查是否为工作日（Mon-Fri）
2. ✅ 检查是否在收盘时段（15:00-16:00）
3. ✅ 生成完整市场报告（Markdown）
4. ✅ 生成精简简报
5. ✅ 推送精简版到飞书

**生成文件**:
- `reports/cn_daily_digest_async_YYYY-MM-DD.md` (完整报告)
- `reports/cn_market_brief_YYYY-MM-DD_1505.txt` (精简版)

**总计**: 1 次/天

---

## 🔧 使用方法

### 安装定时任务

```bash
./scripts/cn_market_schedule.sh install
```

**输出**:
```
📅 安装中国市场智能定时任务

✅ Crontab 已备份到: ~/crontab_backup_20260318_0820.txt

✅ 定时任务已安装

📋 已安装的任务:
   1. 盘中推送: 工作日 09:30-14:59, 每 10 分钟
   2. 收盘日报: 工作日 15:05

📊 查看日志:
   tail -f /tmp/cn_market_schedule.log

🔍 验证安装:
   crontab -l | grep cn_market
```

---

### 查看状态

```bash
./scripts/cn_market_schedule.sh status
```

**输出示例**:
```
📊 中国市场智能定时任务状态

Crontab 状态:
  ✅ 已安装

已安装的任务:
  */10 9-14 * * 1-5 /path/to/cn_market_schedule.sh run-intraday ...
  5 15 * * 1-5 /path/to/cn_market_schedule.sh run-eod ...

配置状态:
  ✅ .env.feishu 存在

日志文件:
  ✅ /tmp/cn_market_schedule.log
  最后 5 行:
    [2026-03-18 10:30:01] ✅ 简报推送成功
```

---

### 手动测试

```bash
# 测试盘中推送
./scripts/cn_market_schedule.sh run-intraday

# 测试收盘日报
./scripts/cn_market_schedule.sh run-eod
```

**测试时会自动检查**：
- 是否为工作日
- 是否在交易时段
- 如果不满足条件，会跳过并记录日志

---

### 查看日志

```bash
# 查看最近日志
./scripts/cn_market_schedule.sh logs

# 实时查看
tail -f /tmp/cn_market_schedule.log

# 查看今天的推送记录
grep "$(date '+%Y-%m-%d')" /tmp/cn_market_schedule.log | grep "简报推送"
```

**日志格式**:
```
[2026-03-18 10:30:01] ========== 盘中推送开始 ==========
[2026-03-18 10:30:01] ✅ 工作日 + 交易时段，执行推送...
[2026-03-18 10:30:01] 📝 已加载飞书配置
[2026-03-18 10:30:03] ✅ 简报推送成功
[2026-03-18 10:30:03] ========== 盘中推送完成 ==========
```

---

### 卸载定时任务

```bash
./scripts/cn_market_schedule.sh uninstall
```

**会自动**：
1. 备份当前 crontab
2. 移除所有相关任务
3. 保留日志文件

---

## 🎯 智能特性

### 1. 自动跳过非交易时段

**周末自动跳过**:
```bash
# 周六/周日执行时的日志：
[2026-03-16 10:30:01] ⏭️  跳过：非工作日（周末）
```

**非交易时段自动跳过**:
```bash
# 09:00 执行时的日志：
[2026-03-18 09:00:01] ⏭️  跳过：不在交易时段（09:30-15:00）

# 16:00 执行时的日志：
[2026-03-18 16:00:01] ⏭️  跳过：不在交易时段（09:30-15:00）
```

---

### 2. 午休时段处理

**中国股市午休**: 11:30-13:00

Cron 配置 `*/10 9-14` 会在以下时间执行：
- 11:00, 11:10, 11:20 ✅
- 11:30, 11:40, 11:50 ✅ (会推送，但市场无新数据)
- 12:00, 12:10, 12:20, 12:30, 12:40, 12:50 ✅ (同上)
- 13:00 开始市场恢复 ✅

**优化建议**（可选）:
```bash
# 如果想跳过午休时段，修改 cron 为：
30-59/10 9 * * 1-5    # 09:30-09:50
*/10 10-11 * * 1-5    # 10:00-11:50
0-20/10 13-14 * * 1-5 # 13:00-14:20
30-50/10 14 * * 1-5   # 14:30-14:50
```

---

### 3. 容错机制

**网络错误处理**:
- 自动重试（3 次）
- 失败记录日志
- 不影响下次执行

**配置缺失处理**:
- 检测到无飞书配置时跳过推送
- 报告生成不受影响
- 日志明确记录原因

---

## 📊 典型使用场景

### 场景 1: 个人交易者

**需求**: 交易时段实时跟踪市场，收盘后查看完整日报

**配置**:
```bash
# 使用飞书私聊推送
# .env.feishu:
export FEISHU_APP_ID="cli_xxxxx"
export FEISHU_APP_SECRET="xxxxx"
export FEISHU_USER_OPEN_ID="ou_xxxxx"

# 安装定时任务
./scripts/cn_market_schedule.sh install
```

**效果**:
- 手机/电脑实时收到市场简报（每 10 分钟）
- 收盘后自动收到日报推送
- 周末不打扰

---

### 场景 2: 团队协作

**需求**: 团队成员共享市场动态

**配置**:
```bash
# 使用飞书群 Webhook
# .env.feishu:
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"

# 安装定时任务
./scripts/cn_market_schedule.sh install
```

**效果**:
- 团队群内实时同步市场简报
- 所有成员同步收到更新
- 便于讨论和决策

---

### 场景 3: 研究分析

**需求**: 收盘后详细分析，无需盘中打扰

**配置**:
```bash
# 只启用收盘日报
# 编辑 crontab:
crontab -e

# 只保留这一行：
5 15 * * 1-5 /path/to/cn_market_schedule.sh run-eod >> /tmp/cn_market_schedule.log 2>&1
```

**效果**:
- 只在收盘后生成日报
- 不受盘中推送干扰
- 完整数据供分析使用

---

## 🔍 故障排查

### 问题 1: 定时任务不执行

**检查清单**:
```bash
# 1. 检查 crontab 是否安装
crontab -l | grep cn_market

# 2. 检查脚本权限
ls -l scripts/cn_market_schedule.sh
# 应该是: -rwxr-xr-x

# 3. 查看日志
tail -f /tmp/cn_market_schedule.log

# 4. 手动测试
./scripts/cn_market_schedule.sh run-intraday
```

---

### 问题 2: 推送失败

**可能原因**:

1. **飞书配置错误**
   ```bash
   # 检查配置
   cat .env.feishu

   # 测试推送
   python3 scripts/feishu_setup.py --test-private
   ```

2. **网络问题**
   ```bash
   # 测试网络连接
   curl -I https://open.feishu.cn
   ```

3. **权限问题** (code 230013)
   ```bash
   # 需要在飞书中添加机器人并发送消息
   # 参考: FEISHU_QUICKSTART.md
   ```

---

### 问题 3: 周末仍然执行

**检查**:
```bash
# 查看脚本逻辑
./scripts/cn_market_schedule.sh run-intraday

# 应该看到：
# ⏭️  跳过：非工作日（周末）
```

**如果仍执行**，检查系统时区：
```bash
date
# 确保时区正确（如 CST）
```

---

### 问题 4: 日志文件过大

**清理旧日志**:
```bash
# 备份日志
cp /tmp/cn_market_schedule.log ~/cn_market_schedule_$(date +%Y%m%d).log

# 清空日志
> /tmp/cn_market_schedule.log

# 或设置日志轮转
```

**自动日志轮转** (可选):
```bash
# 添加到 crontab
0 0 * * * [ -f /tmp/cn_market_schedule.log ] && mv /tmp/cn_market_schedule.log /tmp/cn_market_schedule_$(date +%Y%m%d).log && touch /tmp/cn_market_schedule.log
```

---

## 📚 相关文档

### 飞书推送
- [FEISHU_QUICKSTART.md](FEISHU_QUICKSTART.md) - 5 分钟快速配置
- [FEISHU_PUSH_GUIDE.md](FEISHU_PUSH_GUIDE.md) - 完整配置指南

### 一键简报
- [一键简报脚本](scripts/cn_market_brief.py) - 命令行工具
- README.md - 项目概述

### 技术实现
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - 异步架构
- [ASYNC_OPTIMIZATION_SUMMARY.md](ASYNC_OPTIMIZATION_SUMMARY.md) - 性能优化

---

## 🎓 最佳实践

### 1. 日志管理

**定期检查日志**:
```bash
# 每周检查一次
./scripts/cn_market_schedule.sh logs | tail -50

# 查找错误
grep "❌" /tmp/cn_market_schedule.log
```

### 2. 配置备份

**定期备份配置**:
```bash
# 备份 crontab
crontab -l > ~/crontab_backup_$(date +%Y%m%d).txt

# 备份飞书配置
cp .env.feishu .env.feishu.backup
```

### 3. 测试先行

**安装前测试**:
```bash
# 手动运行一次
./scripts/cn_market_schedule.sh run-intraday

# 确认无误后再安装
./scripts/cn_market_schedule.sh install
```

### 4. 监控执行

**设置监控提醒**:
```bash
# 如果连续失败，发送通知（可选）
# 需要配置额外的监控工具
```

---

## 📞 技术支持

**项目主页**: https://github.com/ZhenRobotics/openclaw-research-analyst

**问题反馈**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues

**相关资源**:
- ClawHub: https://clawhub.ai/ZhenRobotics/research-analyst
- npm: https://www.npmjs.com/package/openclaw-research-analyst

---

**创建时间**: 2026-03-18
**版本**: v1.2.0
**维护**: ZhenRobotics Team
