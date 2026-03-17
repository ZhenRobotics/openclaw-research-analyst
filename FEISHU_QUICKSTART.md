# 飞书推送快速开始
# Feishu Push Quick Start

**状态**: ✅ 已集成到 openclaw-research-analyst skill 中

---

## 🚀 5 分钟完成配置

### 步骤 1: 在飞书中添加机器人（重要！）

**必须先完成这一步，否则推送会失败**

1. 打开飞书 App
2. 点击顶部搜索栏，搜索机器人：`龙虾`
3. 点击机器人头像，进入对话
4. 发送任意消息（如：`你好`）

> 💡 这一步让机器人获得给你发送消息的权限

### 步骤 2: 验证配置

```bash
cd /home/justin/openclaw-research-analyst

# 检查配置文件
cat .env.feishu

# 应该看到：
# export FEISHU_APP_ID="cli_a9325a4356f81cb1"
# export FEISHU_APP_SECRET="cz8hEMYZgWzyTcY6l0XnrfrYkzFBdM7D"
# export FEISHU_USER_OPEN_ID="ou_f50c09ab4c8572a0f509d21ff0aaad07"
```

### 步骤 3: 测试推送

```bash
# 加载配置
source .env.feishu

# 测试私聊推送
python3 scripts/feishu_setup.py --test-private

# 应该看到：
# ✅ 私聊推送测试成功！
# 请检查飞书是否收到测试消息
```

如果看到 `❌ 私聊推送失败: Bot has NO availability to this user`，请返回步骤 1。

### 步骤 4: 生成并推送市场简报

```bash
# 生成报告并自动推送到飞书
python3 scripts/cn_market_report.py --async --push

# 或只查看精简简报（不推送）
python3 scripts/cn_market_report.py --async --brief
```

成功后，你会在飞书私聊中收到类似这样的消息：

```
📊 15:33 市场快报

【A股】涨:中复神鹰+20.0% 跌:亨通光电-8.49% 额:兆易创新118亿
【港股】涨:毅高国际控股+98.0% 额:耀才证券金84亿
```

---

## ⏰ 设置自动推送（每 10 分钟）

### 方法 1: 使用系统 Crontab（推荐）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每小时第 3, 13, 23, 33, 43, 53 分推送）
3,13,23,33,43,53 * * * * cd /home/justin/openclaw-research-analyst && source .env.feishu && python3 scripts/cn_market_report.py --async --push >> /tmp/market_push.log 2>&1

# 保存并退出
```

### 验证定时任务

```bash
# 查看 crontab 配置
crontab -l | grep cn_market

# 实时查看推送日志
tail -f /tmp/market_push.log

# 查看今天推送次数
grep "$(date '+%Y-%m-%d')" /tmp/market_push.log | grep "消息已发送" | wc -l
```

---

## 🔧 配置选项

### 使用配置向导（交互式）

```bash
python3 scripts/feishu_setup.py --interactive
```

### 手动配置

编辑 `.env.feishu`：

```bash
# 私聊推送
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_USER_OPEN_ID="your_open_id"

# 群 Webhook（可选，与私聊同时启用）
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

---

## 📊 使用方法

### 在代码中使用

```python
from scripts.feishu_push import FeishuPusher

# 自动从环境变量读取配置
pusher = FeishuPusher()

# 智能推送（自动选择可用方式）
pusher.push("你的消息")

# 只推送到私聊
pusher.push_to_user("私聊消息")

# 只推送到群 Webhook
pusher.push_to_webhook("群消息")
```

### 命令行使用

```bash
# 从参数推送
python3 scripts/feishu_push.py "你的消息"

# 从 stdin 推送
echo "你的消息" | python3 scripts/feishu_push.py

# 只使用 Webhook
python3 scripts/feishu_push.py --webhook "群消息"

# 只使用私聊
python3 scripts/feishu_push.py --user "私聊消息"
```

---

## 🔍 故障排查

### 问题 1: 推送失败 - code 230013

**错误信息**: `Bot has NO availability to this user`

**原因**: 机器人还没有权限给你发送消息

**解决**:
1. 在飞书中搜索并添加机器人
2. 给机器人发送任意消息
3. 重新测试推送

### 问题 2: Token 获取失败

**检查凭证是否正确**:

```bash
# 验证 APP_ID 和 APP_SECRET
python3 << 'EOF'
import requests
import os

response = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={
        "app_id": os.environ['FEISHU_APP_ID'],
        "app_secret": os.environ['FEISHU_APP_SECRET']
    }
)
print(response.json())
EOF
```

应该返回 `{"code": 0, "tenant_access_token": "..."}`

### 问题 3: Open ID 不正确

**重新获取 Open ID**:

```bash
python3 scripts/feishu_setup.py --get-open-id
```

输入你的手机号（用于注册飞书的号码）。

---

## 📁 文件结构

```
openclaw-research-analyst/
├── scripts/
│   ├── cn_market_report.py      # 主报告生成（已添加 --push 和 --brief）
│   ├── feishu_push.py            # 飞书推送模块（新增）
│   └── feishu_setup.py           # 配置向导（新增）
├── .env.feishu                   # 飞书配置（已配置）
└── .env.feishu.example           # 配置模板
```

---

## 🎯 推送优先级

当同时配置多种推送方式时，按以下顺序尝试：

1. **飞书私聊**（如果配置了 `FEISHU_USER_OPEN_ID`）
2. **飞书群 Webhook**（如果配置了 `FEISHU_WEBHOOK`）

所有方式互不影响，可以同时启用。

---

## ✅ 下一步

1. ✅ 在飞书中添加机器人「龙虾」
2. ✅ 运行 `python3 scripts/feishu_setup.py --test-private` 测试
3. ✅ 运行 `python3 scripts/cn_market_report.py --async --push` 推送报告
4. ✅ 设置 crontab 实现自动推送

---

**需要帮助？** 参考完整文档：[FEISHU_PUSH_GUIDE.md](FEISHU_PUSH_GUIDE.md)

**项目主页**: https://github.com/ZhenRobotics/openclaw-research-analyst
