# 📱 飞书推送配置指南
# Feishu/Lark Push Configuration Guide

**版本**: v1.1.0
**创建日期**: 2026-03-18

---

## ✅ 方案B 已实现！

系统级定时任务已成功配置，每10分钟自动推送中国市场简报。

---

## 📋 实现内容

### 1️⃣ 推送脚本

**文件**: `/home/justin/cn_market_push.sh`

**功能**:
- ✅ 每10分钟自动生成市场简报
- ✅ 写入本地日志（`/tmp/market_push.log`）
- ✅ 支持推送到飞书（配置后自动启用）

**执行时间**: 每小时的 :03, :13, :23, :33, :43, :53 分

### 2️⃣ 系统 Crontab

```bash
# 查看当前任务
crontab -l

# 输出:
3,13,23,33,43,53 * * * * /home/justin/cn_market_push.sh >> /tmp/market_push.log 2>&1
```

**特点**:
- ✅ 系统级后台运行（不依赖 Claude Code 会话）
- ✅ 无限期执行（直到手动停止）
- ✅ 自动日志记录

### 3️⃣ 推送格式

```
📊 02:13 市场快报

【A股】涨:中复神鹰+20.0% 跌:亨通光电-8.49% 额:兆易创新118亿
【港股】涨:毅高国际控股+98.0% 额:耀才证券金84亿
```

---

## 🚀 飞书推送配置

### 步骤 1: 获取飞书 Webhook URL

#### 在飞书 App 中:

1. **打开飞书 App**
   - 电脑端或手机端均可

2. **进入目标群聊**
   - 选择你想接收推送的群聊
   - 如果没有合适的群，可以创建一个新群

3. **添加群机器人**
   ```
   点击右上角 "..."
   → 设置
   → 群机器人
   → 添加机器人
   → 自定义机器人
   ```

4. **配置机器人**
   - 名称: 中国市场快报
   - 描述: 每10分钟推送A股/港股快讯
   - 图标: 可选择 📊 或其他金融相关图标

5. **复制 Webhook 地址**
   - 机器人创建后会显示 Webhook URL
   - 格式类似: `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
   - ⚠️ **重要**: 妥善保管，不要泄露！

### 步骤 2: 配置 Webhook

#### 方法 1: 编辑配置文件（推荐）

```bash
# 编辑配置文件
nano ~/.feishu_config

# 取消注释并替换为你的 Webhook URL:
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_HERE"

# 保存并加载配置
source ~/.feishu_config

# 添加到 shell 配置（永久生效）
echo 'source ~/.feishu_config' >> ~/.bashrc  # 或 ~/.zshrc
```

#### 方法 2: 直接设置环境变量

```bash
# 临时设置（当前会话）
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_HERE"

# 永久设置
echo 'export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_HERE"' >> ~/.bashrc
source ~/.bashrc
```

### 步骤 3: 测试推送

```bash
# 手动测试推送
/home/justin/cn_market_push.sh

# 应该在飞书群里看到消息！
```

### 步骤 4: 验证自动推送

**等待下一个触发时间**（例如 :03, :13, :23...），飞书群应该自动收到推送。

---

## 📊 推送目标

### 当前支持:

1. ✅ **本地日志文件**
   - 路径: `/tmp/market_push.log`
   - 格式: 带时间戳的文本
   - 查看: `tail -f /tmp/market_push.log`

2. ✅ **飞书群聊**
   - 通过 Webhook 推送
   - 需要配置 `FEISHU_WEBHOOK`
   - 支持文本消息

3. ⚠️ **Claude Code 聊天框**
   - **技术限制**: 系统 cron 无法直接推送到 Claude Code 的交互式聊天界面
   - **替代方案**:
     - 使用 Claude Code 的会话级 cron（已配置，任务 ID: 8e978989）
     - 或者定期查看日志文件

### 未来可扩展:

- 📧 邮件推送（需要配置 SMTP）
- 📱 Telegram Bot（需要 Bot Token）
- 💬 钉钉 Webhook
- 📲 企业微信 Webhook
- 🔔 其他通知服务

---

## 🔧 管理命令

### 查看推送日志

```bash
# 实时查看推送
tail -f /tmp/market_push.log

# 查看最近10条
tail -n 10 /tmp/market_push.log

# 查看今天的推送
grep "$(date '+%Y-%m-%d')" /tmp/market_push.log
```

### 修改推送频率

```bash
# 编辑 crontab
crontab -e

# 当前: 每10分钟（:03, :13, :23, :33, :43, :53）
3,13,23,33,43,53 * * * * /home/justin/cn_market_push.sh

# 改为每5分钟:
*/5 * * * * /home/justin/cn_market_push.sh

# 改为每小时（整点）:
0 * * * * /home/justin/cn_market_push.sh

# 改为仅工作日 9:00-15:00（每10分钟）:
*/10 9-15 * * 1-5 /home/justin/cn_market_push.sh
```

### 暂停推送

```bash
# 方法 1: 注释掉 cron 任务
crontab -e
# 在任务前添加 #

# 方法 2: 临时移除任务
crontab -r  # ⚠️ 会删除所有任务，谨慎使用

# 方法 3: 重命名脚本
mv /home/justin/cn_market_push.sh /home/justin/cn_market_push.sh.disabled
```

### 恢复推送

```bash
# 如果重命名了脚本
mv /home/justin/cn_market_push.sh.disabled /home/justin/cn_market_push.sh

# 如果删除了 cron，重新添加
(crontab -l 2>/dev/null; echo "3,13,23,33,43,53 * * * * /home/justin/cn_market_push.sh >> /tmp/market_push.log 2>&1") | crontab -
```

---

## 🐛 故障排查

### 问题 1: 没有收到推送

**检查清单**:

```bash
# 1. 检查 cron 任务是否存在
crontab -l | grep cn_market_push

# 2. 检查脚本是否可执行
ls -l /home/justin/cn_market_push.sh
# 应该显示 -rwxr-xr-x

# 3. 检查日志
tail -n 20 /tmp/market_push.log

# 4. 手动测试脚本
/home/justin/cn_market_push.sh

# 5. 检查飞书 Webhook 配置
echo $FEISHU_WEBHOOK
```

### 问题 2: 飞书收不到消息

**可能原因**:

1. **Webhook URL 未配置**
   ```bash
   # 检查
   echo $FEISHU_WEBHOOK

   # 如果为空，配置它
   export FEISHU_WEBHOOK="YOUR_URL"
   source ~/.feishu_config
   ```

2. **Webhook URL 错误**
   - 检查 URL 格式
   - 确保没有多余的空格或引号

3. **机器人被移除**
   - 检查飞书群设置
   - 重新添加机器人

4. **网络问题**
   ```bash
   # 测试连接
   curl -X POST "$FEISHU_WEBHOOK" \
     -H 'Content-Type: application/json' \
     -d '{"msg_type":"text","content":{"text":"测试消息"}}'
   ```

### 问题 3: 脚本执行失败

**查看错误日志**:

```bash
# 查看详细错误
tail -n 50 /tmp/market_push.log | grep -A 5 "失败\|error\|Error"

# 手动执行查看错误
/home/justin/cn_market_push.sh
```

**常见错误**:

1. **Python 环境问题**
   ```bash
   which python3
   python3 --version  # 应该是 3.10+
   ```

2. **脚本路径问题**
   ```bash
   cd /home/justin/openclaw-research-analyst
   python3 scripts/cn_market_report.py --async
   ```

3. **权限问题**
   ```bash
   chmod +x /home/justin/cn_market_push.sh
   ```

---

## 📊 推送统计

### 查看推送次数

```bash
# 今天推送了多少次
grep "$(date '+%Y-%m-%d')" /tmp/market_push.log | grep "市场快报" | wc -l

# 最近一小时
grep "$(date '+%Y-%m-%d %H')" /tmp/market_push.log | grep "市场快报" | wc -l
```

### 清理日志

```bash
# 保留最近100条
tail -n 100 /tmp/market_push.log > /tmp/market_push.log.new
mv /tmp/market_push.log.new /tmp/market_push.log

# 或者按日期归档
cp /tmp/market_push.log ~/market_push_$(date +%Y%m%d).log
> /tmp/market_push.log
```

---

## 🎯 使用建议

### 最佳实践

1. **飞书群设置**
   - 创建专门的"市场快报"群
   - 设置免打扰时段（可选）
   - 置顶群聊方便查看

2. **推送频率**
   - 交易时段（9:30-15:00）: 每10分钟
   - 非交易时段: 每30分钟或更长
   - 周末: 暂停或降低频率

3. **日志管理**
   - 定期清理旧日志（建议每周）
   - 保留重要数据用于复盘

4. **错误处理**
   - 定期检查日志中的错误
   - 遇到连续失败及时排查

---

## 🔐 安全提示

⚠️ **重要安全事项**:

1. **保护 Webhook URL**
   - 不要提交到公开代码仓库
   - 不要在公共场合分享
   - 定期更换 Webhook（可选）

2. **日志安全**
   - 日志文件不包含敏感信息
   - 但建议定期清理避免占用空间

3. **权限控制**
   - 脚本只有当前用户可执行
   - 配置文件权限设为 600（只有所有者可读写）

```bash
# 设置配置文件权限
chmod 600 ~/.feishu_config

# 验证
ls -l ~/.feishu_config
# 应该显示 -rw-------
```

---

## 📞 技术支持

**项目主页**: https://github.com/ZhenRobotics/openclaw-research-analyst

**问题反馈**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues

**相关文档**:
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - 异步优化报告
- [QUICK_START_v1.1.md](QUICK_START_v1.1.md) - 快速开始指南

---

## ✅ 检查清单

配置完成后，请确认以下项目：

- [ ] 推送脚本已创建（`/home/justin/cn_market_push.sh`）
- [ ] Crontab 任务已添加（`crontab -l` 可见）
- [ ] 手动测试成功（执行脚本有输出）
- [ ] 飞书 Webhook 已配置（如需要）
- [ ] 飞书群已收到测试消息（如配置了）
- [ ] 日志文件可查看（`/tmp/market_push.log`）
- [ ] 等待下一个触发时间验证自动推送

---

**状态**: ✅ **方案B 已完全实现！**

**下次推送**: 每小时的 :03, :13, :23, :33, :43, :53 分

**创建时间**: 2026-03-18 02:13
**创建人**: Backend Architect + Claude Code
