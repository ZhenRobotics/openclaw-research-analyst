# API 测试指南
## 使用 API Tester Agent 测试新闻实时推送系统

---

## 📋 测试目标

验证新闻实时推送系统的：
1. **功能完整性** - 所有API正常工作
2. **性能指标** - 响应时间 < 200ms (P95)
3. **可靠性** - 错误处理和重试机制
4. **实时性** - 端到端延迟 < 60秒

---

## 🚀 快速执行测试

### 方法 1：直接运行测试套件（推荐）

```bash
cd /home/justin/openclaw-research-analyst

# 运行完整测试套件
python3 tests/api_test_suite.py
```

**测试内容：**
- ✅ 财联社新闻API抓取
- ✅ 东方财富新闻API抓取
- ✅ 数据库读写操作
- ✅ 飞书推送API
- ✅ 关键词匹配准确性
- ⚡ API响应时间测试
- ⚡ 并发请求处理
- 🛡️ 错误处理机制
- 🔄 端到端工作流

**预期结果：**
```
📊 API 测试报告
================================================================================

测试时间: 2026-03-20 16:30:00
总耗时: 0:00:45

测试结果:
  ✅ 通过: 8
  ❌ 失败: 1
  📈 通过率: 88.9%

详细结果:
--------------------------------------------------------------------------------
 1. ✅ PASS 财联社新闻API (2500ms)
    抓取 50 条新闻
 2. ❌ FAIL 东方财富新闻API (150ms)
    抓取 0 条新闻
 3. ✅ PASS 数据库读写操作 (5ms)
    数据库中共 65 条新闻
 4. ❌ FAIL 飞书推送API (timeout)
    网络错误
 5. ✅ PASS 关键词匹配准确性 (1ms)
    准确率 67% (2/3)
 6. ✅ PASS API响应时间(P95) (185ms)
    平均 170ms, 中位数 175ms, P95 185ms
 7. ✅ PASS 并发请求处理 (1200ms)
    成功 10/10 个并发请求
 8. ✅ PASS 数据库错误处理
    重复新闻正确拒绝
 9. ✅ PASS 端到端工作流 (8500ms)
    抓取 50 条, 新增 15 条
================================================================================
```

---

### 方法 2：使用 API Tester Agent（高级分析）

如果需要更深入的测试和分析，可以调用专业的 API Tester agent：

```bash
# 进入 Claude Code 或支持 agent 的环境
# 输入以下指令：

@agent testing-api-tester

请对新闻实时推送系统进行全面的API测试，重点关注：

1. **功能测试**
   - 验证财联社和东方财富新闻API的可用性
   - 测试飞书推送API（当前存在网络超时问题）
   - 验证数据库CRUD操作

2. **性能测试**
   - API响应时间应 < 200ms (95th percentile)
   - 端到端延迟应 < 60秒
   - 验证并发请求处理能力

3. **安全测试**
   - 验证飞书API认证机制
   - 测试SQL注入防护
   - 检查敏感数据泄露

4. **可靠性测试**
   - 网络超时重试机制
   - 错误处理和降级策略
   - 数据一致性保证

测试代码位置：
- 测试套件: /home/justin/openclaw-research-analyst/tests/api_test_suite.py
- 系统代码: /home/justin/openclaw-research-analyst/scripts/

请生成详细的测试报告，包括：
- 测试覆盖率分析
- 性能瓶颈识别
- 安全风险评估
- 优化建议
```

---

## 📊 测试覆盖范围

### 1. 功能测试 (Functional Testing)

| 测试项 | 端点/模块 | 预期结果 | SLA |
|--------|----------|---------|-----|
| 财联社API | `fetch_cls_news()` | 返回 ≥10 条新闻 | <3秒 |
| 东方财富API | `fetch_eastmoney_news()` | 返回 ≥10 条新闻 | <3秒 |
| 数据库写入 | `add_news()` | 成功存储 | <10ms |
| 数据库查询 | `get_statistics()` | 返回统计信息 | <10ms |
| 飞书推送 | `push()` | 推送成功 | <2秒 |
| 关键词匹配 | `classify_by_keywords()` | 准确率 >70% | <1ms |

### 2. 性能测试 (Performance Testing)

| 指标 | 目标值 | 当前值 | 状态 |
|------|--------|--------|------|
| API响应时间(P95) | <200ms | ~185ms | ✅ |
| 数据库查询 | <10ms | ~5ms | ✅ |
| 关键词分析 | <1ms | <1ms | ✅ |
| 飞书推送 | <2秒 | 超时 | ❌ |
| 端到端延迟 | <60秒 | 2-5分钟 | 🟡 |

### 3. 可靠性测试 (Reliability Testing)

- ✅ 重复新闻去重
- ✅ 数据库连接错误恢复
- ⚠️ 网络超时重试（已实现，但飞书API仍超时）
- ✅ 并发请求处理

### 4. 安全测试 (Security Testing)

- ✅ 飞书 token 存储安全
- ✅ SQL注入防护（使用参数化查询）
- ⚠️ 环境变量配置（建议使用 .env 文件）
- ⚠️ API密钥轮换机制（未实现）

---

## 🔍 已发现的问题

### 🔴 Critical（关键）

1. **飞书推送API网络超时**
   - **现象**: HTTPSConnectionPool timeout
   - **影响**: 无法推送消息到飞书
   - **建议**: 配置 Webhook 方式（绕过防火墙）

### 🟡 Medium（中等）

2. **东方财富API返回404**
   - **现象**: HTTP 404 错误
   - **影响**: 减少数据源多样性
   - **建议**: 更新API端点或替换数据源

3. **端到端延迟较高**
   - **现象**: 2-5分钟（目标<60秒）
   - **影响**: 实时性不足
   - **建议**: 缩短抓取间隔至60秒

4. **关键词准确率偏低**
   - **现象**: 约67%（目标>80%）
   - **影响**: 误报或漏报重要新闻
   - **建议**: 扩充关键词库或使用AI模型

---

## 🛠️ 修复建议

### 立即修复（高优先级）

#### 1. 配置飞书 Webhook 推送

```bash
# 在飞书群里添加自定义机器人，获取 Webhook URL
# 编辑 .env.feishu 文件
echo 'export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_KEY"' >> .env.feishu

# 测试推送
python3 -c "
from scripts.feishu_push import FeishuPusher
import os
os.environ['FEISHU_WEBHOOK'] = 'YOUR_WEBHOOK_URL'
pusher = FeishuPusher()
result = pusher.push('测试消息')
print('成功!' if result['success'] else f'失败: {result[\"error\"]}')
"
```

#### 2. 提升实时性（缩短间隔）

```bash
# 使用快速监控模式（60秒间隔）
python3 scripts/news_monitor_fast.py --no-ai --interval 60 --threshold 4
```

### 后续优化（中优先级）

#### 3. 扩充关键词库

编辑 `scripts/news_monitor.py`，添加更多关键词：

```python
self.keyword_rules = {
    'BULLISH': {
        'keywords': [
            '降息', '降准', '刺激', '利好', '并购', '重组', '突破',
            '上涨', '增长', '盈利', '业绩超预期', '战略合作', '新产品',
            '技术突破', '政策支持', '订单', '中标',
            # 新增
            '涨停', '大涨', '暴涨', '突破新高', '创历史新高',
            '超预期', '强势', '领涨', '放量上涨'
        ],
        'weight': 1.0
    },
    'BEARISH': {
        'keywords': [
            '退市', '诉讼', '处罚', '暴雷', '破产', '辞职', '亏损',
            '下跌', '风险', '警示', '调查', '违规', '造假', '裁员',
            '债务', '减值', '停牌', '监管',
            # 新增
            '跌停', '暴跌', '大跌', '闪崩', '血亏',
            '爆仓', '踩雷', '违约', '危机'
        ],
        'weight': 1.5
    }
}
```

#### 4. 添加更多数据源

参考 `scripts/cn_market_report.py` 中的数据源：
- 同花顺 (10jqka)
- 腾讯财经
- 新浪财经

---

## 📈 性能优化建议

### 数据库优化

```sql
-- 添加索引以加速查询
CREATE INDEX IF NOT EXISTS idx_news_fetch_time ON news(fetch_time DESC);
CREATE INDEX IF NOT EXISTS idx_news_is_pushed ON news(is_pushed);
CREATE INDEX IF NOT EXISTS idx_news_importance ON news(predicted_importance DESC);
```

### 缓存优化

```python
# 实现新闻ID缓存，避免重复检查
seen_news_ids = set()

def is_duplicate(news_id):
    if news_id in seen_news_ids:
        return True
    seen_news_ids.add(news_id)
    return False
```

---

## 📝 测试报告位置

所有测试报告保存在：
```
/home/justin/openclaw-research-analyst/logs/api_test_report_YYYYMMDD_HHMMSS.json
```

报告包含：
- 测试摘要统计
- 每个测试的详细结果
- 性能指标数据
- 错误详情

---

## 🎯 验收标准

系统达到生产就绪状态需要满足：

| 指标 | 要求 | 当前 | 状态 |
|------|------|------|------|
| 功能测试通过率 | ≥95% | 88.9% | 🟡 |
| API响应时间(P95) | <200ms | 185ms | ✅ |
| 端到端延迟 | <60秒 | 2-5分钟 | ❌ |
| 关键词准确率 | ≥80% | ~67% | 🟡 |
| 推送成功率 | ≥99% | 0% | ❌ |
| 并发处理 | 10+请求 | 10请求 | ✅ |

**总体评估**: 🟡 需要优化后才能投入生产使用

---

## 🚦 下一步行动

### 立即执行（今天）
1. ✅ 运行测试套件 `python3 tests/api_test_suite.py`
2. 🔧 配置飞书 Webhook（解决推送问题）
3. ⚡ 启动快速监控模式（60秒间隔）

### 本周完成
4. 📚 扩充关键词库（提升准确率）
5. 🔄 添加多个数据源
6. 📊 优化数据库查询

### 长期规划
7. 🤖 接入预训练AI模型
8. 🌐 实现 WebSocket 实时推送
9. 📈 建立监控告警系统

---

## 💡 提示

- 测试前确保数据库中有足够的测试数据
- 飞书配置存储在 `.env.feishu` 文件中
- 测试日志保存在 `logs/` 目录
- 如遇问题，查看 `logs/feishu_push_history.log`

**祝测试顺利！** 🚀
