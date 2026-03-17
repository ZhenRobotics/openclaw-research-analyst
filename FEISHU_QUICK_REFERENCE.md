# 飞书推送快速参考卡片
## Feishu Push Quick Reference Card

---

## 快速开始 (3 步)

### 1. 加载配置
```bash
cd /home/justin/openclaw-research-analyst
source .env.feishu
```

### 2. 添加机器人
在飞书中搜索 **龙虾**，添加并发送消息

### 3. 测试推送
```bash
python3 scripts/feishu_setup.py --test-private
```

---

## 常用命令

### 测试推送功能
```bash
# 测试私聊推送
source .env.feishu && python3 scripts/feishu_setup.py --test-private

# 手动发送消息
source .env.feishu && echo "你的消息" | python3 scripts/feishu_push.py --user
```

### 生成市场简报
```bash
# 生成并推送到飞书
source .env.feishu && python3 scripts/cn_market_report.py --async --push

# 只生成简报，不推送
python3 scripts/cn_market_report.py --async --brief
```

### 诊断工具
```bash
# 运行完整诊断
bash /tmp/feishu_diagnostic.sh

# 查看配置
cat .env.feishu

# 查看详细测试报告
cat FEISHU_PUSH_TEST_REPORT.md
```

---

## 错误码速查

| 错误码 | 含义 | 解决方法 |
|--------|------|----------|
| **0** | 成功 | 无需操作 |
| **230013** | 机器人无权限 | 在飞书中添加机器人并发送消息 |
| **99991663** | Token 无效 | 检查 APP_ID 和 APP_SECRET |
| **99991668** | 凭证错误 | 确认应用凭证正确 |

---

## 简报格式示例

```
📊 14:30 市场快报

【A股】涨:贵州茅台+3.5% 跌:中国平安-2.1% 额:宁德时代250亿
【港股】涨:腾讯控股+2.8% 额:美团100亿
```

---

## 配置文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| 配置文件 | `.env.feishu` | 凭证存储 |
| 推送模块 | `scripts/feishu_push.py` | 核心功能 |
| 配置向导 | `scripts/feishu_setup.py` | 配置工具 |
| 业务集成 | `scripts/cn_market_report.py` | 简报生成 |

---

## 关键信息

- **机器人名称**: 龙虾
- **App ID**: `cli_a9325a4356f81cb1`
- **User Open ID**: `ou_f50c09ab4c8572a0f509d21ff0aaad07`
- **Token 有效期**: ~97 分钟
- **推送延迟**: <300ms

---

## 权限说明

飞书私聊推送遵循"用户主动触发"原则:

1. 机器人不能主动向陌生用户推送
2. 用户必须先与机器人建立会话
3. 建立会话后 7 天内可推送
4. 超过 7 天需重新触发

---

## 故障排查流程

```
推送失败
  ↓
检查环境变量 (source .env.feishu)
  ↓
测试 Token 获取 (python3 scripts/feishu_setup.py --test-private)
  ↓
检查错误码
  ↓ 230013
添加机器人并发送消息
  ↓
重新测试
```

---

## 支持与文档

- **完整测试报告**: `/home/justin/openclaw-research-analyst/FEISHU_PUSH_TEST_REPORT.md`
- **测试摘要**: `/home/justin/openclaw-research-analyst/FEISHU_TEST_SUMMARY.txt`
- **诊断工具**: `/tmp/feishu_diagnostic.sh`

---

**最后更新**: 2026-03-18
**版本**: v1.0
