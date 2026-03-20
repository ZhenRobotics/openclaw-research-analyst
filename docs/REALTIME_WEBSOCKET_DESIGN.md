# WebSocket 实时推送架构设计

## 概述

相比定时轮询，WebSocket 可实现秒级实时推送。

## 架构对比

### 当前方案（定时轮询）
```
系统 --每5分钟--> API服务器 --> 获取新闻 --> 分析 --> 推送
延迟：2-5分钟
```

### WebSocket 方案（事件驱动）
```
系统 <--实时连接--> WebSocket服务器
       |
       新闻发布（立即推送）--> 接收 --> 分析 --> 推送
延迟：1-3秒
```

## 实现方案

### 方案A：财联社官方 WebSocket（如果有）

```python
import asyncio
import websockets

async def cls_websocket_client():
    uri = "wss://www.cls.cn/api/ws"  # 假设的地址

    async with websockets.connect(uri) as websocket:
        # 订阅快讯频道
        await websocket.send(json.dumps({
            "action": "subscribe",
            "channel": "telegraph"
        }))

        # 实时接收
        async for message in websocket:
            news = json.loads(message)
            # 立即分析和推送
            await process_and_push(news)
```

**优点：**
- ✅ 真正实时（1-2秒延迟）
- ✅ 减少服务器负载
- ✅ 不会被封IP

**缺点：**
- ⚠️ 需要官方支持 WebSocket
- ⚠️ 连接稳定性要求高
- ⚠️ 需要断线重连机制

### 方案B：混合模式（轮询 + 增量更新）

```python
# 首次：获取最近新闻
initial_news = fetch_news(limit=50)

# 之后：只获取最新的（更快）
while True:
    last_id = get_last_news_id()
    new_items = fetch_news_since(last_id, limit=10)

    if new_items:
        process_and_push(new_items)

    await asyncio.sleep(30)  # 30秒间隔
```

**优点：**
- ✅ 兼容性好
- ✅ 减少数据传输
- ✅ 可以设置更短间隔

### 方案C：多数据源并行（提高覆盖率）

```python
# 同时监控多个源，谁先发布谁先推
sources = [
    'cls',           # 财联社
    'eastmoney',     # 东方财富
    'sina',          # 新浪财经
    'wallstreetcn',  # 华尔街见闻
]

async def monitor_all_sources():
    tasks = [monitor_source(s, interval=60) for s in sources]
    await asyncio.gather(*tasks)
```

**优点：**
- ✅ 提高消息覆盖率
- ✅ 降低单一源延迟影响
- ✅ 数据交叉验证

## 技术选型

| 方案 | 实时性 | 复杂度 | 可靠性 | 推荐度 |
|------|--------|--------|--------|--------|
| 定时轮询（5分钟） | ⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | 稳定但慢 |
| 定时轮询（1分钟） | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | **当前最佳** |
| WebSocket | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 理想但需支持 |
| 混合模式 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 平衡方案 |
| 多源并行 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 增强覆盖 |

## 实施建议

### 短期（立即实施）
- ✅ 缩短抓取间隔至 **60秒**
- ✅ 优化数据库查询（避免重复）
- ✅ 添加增量抓取逻辑

### 中期（1-2周）
- 🔄 调研财联社是否有 WebSocket API
- 🔄 添加多个数据源
- 🔄 实现智能去重

### 长期（1个月+）
- 🎯 如果有，迁移到 WebSocket
- 🎯 建立新闻缓存层
- 🎯 ML模型优化识别速度

## 注意事项

1. **反爬虫策略**
   - 间隔 < 30秒 时添加随机延迟
   - 使用 User-Agent 轮换
   - 考虑使用代理池

2. **成本控制**
   - 监控API调用次数
   - 实施流量限制
   - 避免重复抓取

3. **稳定性**
   - 实现断线重连
   - 错误自动恢复
   - 日志监控告警
