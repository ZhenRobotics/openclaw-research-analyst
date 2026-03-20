# 飞书推送 v1.2.1 使用指南

## 新功能概览

v1.2.1 对飞书推送进行了重大改进，提升了可靠性和可追溯性。

---

## 1. 详细返回值

### 旧版本
```python
from feishu_push import FeishuPusher

pusher = FeishuPusher()
success = pusher.push("消息")  # 只返回 True/False
```

### 新版本
```python
from feishu_push import FeishuPusher

pusher = FeishuPusher()
result = pusher.push("消息")

# 查看详细结果
print(f"推送成功: {result['success']}")
print(f"消息ID: {result['message_ids']}")

# 查看每个方式的详细结果
for r in result['results']:
    print(f"{r['method']}: {r['success']}")
    if not r['success']:
        print(f"  错误: {r['error']}")
```

### 返回值结构
```python
{
    'success': True,              # 至少一种方式成功
    'results': [                  # 每种方式的详细结果
        {
            'success': True,
            'method': 'private_chat',
            'message_id': 'om_xxx',
            'timestamp': '2026-03-20T12:30:00',
            'error': None
        },
        {
            'success': True,
            'method': 'webhook',
            'message_id': 'msg_xxx',
            'timestamp': '2026-03-20T12:30:01',
            'error': None
        }
    ],
    'message_ids': ['om_xxx', 'msg_xxx']  # 所有成功的消息ID
}
```

---

## 2. 自动重试机制

### 工作原理

网络请求失败时自动重试，最多2次：

```
第1次尝试 → 失败 → 等待1秒 → 第2次尝试 → 失败 → 等待2秒 → 第3次尝试
```

### 适用场景

- 网络超时 (Timeout)
- 连接错误 (ConnectionError)

### 输出示例

```
🔄 重试 1/2...
🔄 重试 2/2...
❌ 私聊推送错误: Timeout: ...
```

### 配置重试次数

```python
pusher = FeishuPusher()
pusher.max_retries = 3  # 修改最大重试次数（默认2）
```

---

## 3. 推送历史日志

### 日志位置

`logs/feishu_push_history.log`

### 日志格式

每行一条 JSON 记录：

```json
{
  "timestamp": "2026-03-20 12:30:15",
  "method": "webhook",
  "status": "SUCCESS",
  "message_length": 85,
  "message_preview": "📊 10:30 市场快报\n\n【A股】涨:中复神鹰+20.0%...",
  "message_id": "msg_abc123",
  "error": null
}
```

### 查看日志

**最近10条**:
```bash
tail -10 logs/feishu_push_history.log
```

**格式化查看**:
```bash
tail -10 logs/feishu_push_history.log | jq .
```

**统计成功率**:
```bash
cat logs/feishu_push_history.log | \
  jq -r '.status' | \
  sort | uniq -c
```

**查找失败记录**:
```bash
cat logs/feishu_push_history.log | \
  jq 'select(.status == "FAILED")'
```

### 禁用日志

```python
pusher = FeishuPusher(enable_logging=False)
```

---

## 4. 明确的错误提示

### 命令行使用

**成功**:
```bash
$ python3 scripts/cn_market_brief.py --push
📊 10:30 市场快报
...
📄 已保存: reports/cn_market_brief_2026-03-20_1230.txt
✅ 已推送到飞书
```

**失败（未配置）**:
```bash
$ python3 scripts/cn_market_brief.py --push
❌ 飞书推送失败:
  - private_chat: User Open ID not configured
  - webhook: Webhook URL not configured
```

**失败（网络错误）**:
```bash
$ python3 scripts/cn_market_brief.py --push
❌ 飞书推送失败:
  - private_chat: Timeout: Read timed out after 10 seconds
```

### 代码中使用

```python
result = pusher.push("消息")

if result['success']:
    print(f"✅ 推送成功，消息ID: {result['message_ids']}")
else:
    print("❌ 推送失败:")
    for r in result['results']:
        if not r['success']:
            print(f"  {r['method']}: {r['error']}")
```

---

## 5. 实际使用示例

### 示例1: 基本推送

```python
from scripts.feishu_push import FeishuPusher

pusher = FeishuPusher()
result = pusher.push("📊 市场简报: 今日涨幅...")

if result['success']:
    print(f"✅ 推送成功")
else:
    print("❌ 推送失败，请检查配置")
```

### 示例2: 获取消息ID

```python
result = pusher.push("重要通知")

if result['success']:
    for msg_id in result['message_ids']:
        print(f"消息已发送: {msg_id}")
```

### 示例3: 错误处理

```python
result = pusher.push("消息内容")

if not result['success']:
    # 检查具体哪种方式失败
    for r in result['results']:
        if r['method'] == 'private_chat' and not r['success']:
            if 'Open ID not configured' in r['error']:
                print("请先配置 FEISHU_USER_OPEN_ID")
            elif 'Timeout' in r['error']:
                print("网络超时，请检查网络连接")
```

### 示例4: 只推送到特定方式

```python
# 只推送到 Webhook
result = pusher.push_to_webhook("消息")

# 只推送到私聊
result = pusher.push_to_user("消息")

# 推送到指定用户
result = pusher.push_to_user("消息", open_id="ou_xxxxx")
```

---

## 6. 日志分析示例

### 查看今天的推送记录

```bash
cat logs/feishu_push_history.log | \
  grep "2026-03-20" | \
  jq .
```

### 统计推送成功率

```bash
cat logs/feishu_push_history.log | \
  jq -r '.status' | \
  awk '{arr[$1]++} END {for (i in arr) print i, arr[i]}'
```

### 查找最近的失败记录

```bash
cat logs/feishu_push_history.log | \
  jq 'select(.status == "FAILED")' | \
  tail -5
```

### 分析错误类型

```bash
cat logs/feishu_push_history.log | \
  jq -r 'select(.error != null) | .error' | \
  sort | uniq -c | sort -rn
```

---

## 7. 故障排查

### 问题: 推送总是失败

**检查配置**:
```bash
source .env.feishu
echo "APP_ID: $FEISHU_APP_ID"
echo "APP_SECRET: ${FEISHU_APP_SECRET:0:10}..."
echo "USER_OPEN_ID: $FEISHU_USER_OPEN_ID"
echo "WEBHOOK: ${FEISHU_WEBHOOK:0:30}..."
```

**检查日志**:
```bash
tail -20 logs/feishu_push_history.log | jq .
```

### 问题: 网络超时

**增加超时时间**: 修改 `feishu_push.py`:
```python
response = requests.post(..., timeout=30)  # 改为30秒
```

**检查网络**:
```bash
curl -I https://open.feishu.cn
```

### 问题: 日志文件过大

**查看大小**:
```bash
ls -lh logs/feishu_push_history.log
```

**清理旧日志**:
```bash
# 只保留最近1000行
tail -1000 logs/feishu_push_history.log > logs/feishu_push_history.log.tmp
mv logs/feishu_push_history.log.tmp logs/feishu_push_history.log
```

---

## 8. 最佳实践

### 1. 检查返回值

```python
result = pusher.push(message)
if not result['success']:
    # 记录失败，发送告警
    logging.error(f"Push failed: {result}")
```

### 2. 保存消息ID

```python
if result['success']:
    for msg_id in result['message_ids']:
        # 保存到数据库以便后续追溯
        db.save_message(msg_id, message)
```

### 3. 定期清理日志

```bash
# 添加到 crontab
0 0 * * 0 tail -10000 ~/openclaw-research-analyst/logs/feishu_push_history.log > /tmp/tmp.log && mv /tmp/tmp.log ~/openclaw-research-analyst/logs/feishu_push_history.log
```

### 4. 监控推送状态

```python
# 定期检查最近的推送成功率
import json

with open('logs/feishu_push_history.log') as f:
    recent = [json.loads(line) for line in f.readlines()[-100:]]
    success_rate = sum(1 for r in recent if r['status'] == 'SUCCESS') / len(recent)

    if success_rate < 0.8:
        # 成功率低于80%，发送告警
        alert("Feishu push success rate is low")
```

---

## 9. 性能影响

- **成功场景**: 无明显影响 (~2秒)
- **失败1次重试**: +1秒
- **失败2次重试**: +3秒
- **日志写入**: +5-10ms

---

## 10. 向后兼容性

所有旧代码继续工作：

```python
# 旧代码仍然可用
pusher.push(message)  # 返回 dict 而不是 bool

# 但建议使用新方式
result = pusher.push(message)
if result['success']:
    # ...
```

---

## 支持

如有问题，请查看：
- 日志文件: `logs/feishu_push_history.log`
- 优化文档: `OPTIMIZATION_v1.2.1.md`
- GitHub Issues: https://github.com/ZhenRobotics/openclaw-research-analyst/issues
