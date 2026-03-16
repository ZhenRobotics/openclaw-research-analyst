# 中国财经数据源集成文档

本文档说明 OpenClaw Research Analyst 对中国财经数据源的支持情况。

## 已集成数据源

### 1. 东方财富 (East Money) ✅

**文件**: `scripts/cn_market_rankings.py`

**数据源**: https://push2.eastmoney.com/api/qt/clist/get

**功能**:
- A 股涨幅榜 Top 20
- A 股成交额榜 Top 20
- 港股涨幅榜 Top 20
- 港股成交额榜 Top 20

**使用示例**:
```bash
python3 scripts/cn_market_rankings.py
```

**输出格式**: JSON
```json
{
  "a_share": {
    "top_gainers": [...],
    "top_amount": [...]
  },
  "hong_kong": {
    "top_gainers": [...],
    "top_amount": [...]
  }
}
```

---

### 2. 新浪财经 (Sina Finance) ✅

**文件**: `scripts/cn_stock_quotes.py`

**数据源**: https://hq.sinajs.cn/list=

**功能**:
- A 股实时报价（沪深股票）
- 港股实时报价
- 支持批量查询

**使用示例**:
```bash
# 默认：沪深300, 茅台, 平安, 腾讯
python3 scripts/cn_stock_quotes.py

# 自定义股票代码
python3 scripts/cn_stock_quotes.py 600519 000001 HK.00700
```

**代码格式**:
- A 股: 6 位数字 (600519 = 贵州茅台)
- 港股: HK.xxxxx (HK.00700 = 腾讯控股)

---

### 3. 财联社 (CLS.cn) ✅ NEW

**文件**: `scripts/cn_cls_telegraph.py`

**数据源**: https://www.cls.cn/telegraph

**功能**:
- 实时财经快讯（电报）
- 深度文章
- 自动提取相关股票代码

**使用示例**:
```bash
python3 scripts/cn_cls_telegraph.py
```

**特色**:
- ⚡ 实时性强：比一般新闻快 5-30 分钟
- 🎯 高质量：财联社是专业财经资讯平台
- 🔍 智能提取：自动识别快讯中的股票代码

**输出格式**: JSON
```json
{
  "timestamp": "2026-03-16T...",
  "telegraph": [
    {
      "id": "xxx",
      "title": "标题",
      "brief": "摘要",
      "content": "内容",
      "ctime": "发布时间",
      "level": 3,
      "related_codes": ["600519", "000001"],
      "source": "cls_telegraph"
    }
  ],
  "depth": [...]
}
```

---

### 4. 腾讯财经 (Tencent Finance) ✅ NEW

**文件**: `scripts/cn_tencent_moneyflow.py`

**数据源**: https://stockapp.finance.qq.com

**功能**:
- 热门股票榜
- 概念板块涨幅榜
- 资金流向（主力流入/流出）

**使用示例**:
```bash
python3 scripts/cn_tencent_moneyflow.py
```

**特色**:
- 💰 资金流向：追踪主力资金动向
- 🔥 概念板块：把握热点板块轮动
- 📊 综合数据：多维度市场分析

**输出格式**: JSON
```json
{
  "timestamp": "2026-03-16T...",
  "hot_stocks": [...],
  "concept_plates": [...],
  "money_flow": {
    "top_inflow": [
      {
        "code": "600519",
        "name": "贵州茅台",
        "net_inflow": 12345.67,
        "pct": 2.5
      }
    ],
    "top_outflow": [...]
  }
}
```

---

### 5. 同花顺 (10jqka) ✅ NEW

**文件**: `scripts/cn_ths_diagnosis.py`

**数据源**: https://www.10jqka.com.cn

**功能**:
- 热门股票榜
- 行业板块排行
- 个股诊断（诊股功能）
- 研报数据

**使用示例**:
```bash
# 市场概览
python3 scripts/cn_ths_diagnosis.py

# 个股诊断
python3 scripts/cn_ths_diagnosis.py 600519
```

**特色**:
- 🏥 智能诊股：综合评分、趋势评分
- 📊 行业分析：行业板块排行
- 📄 研报汇总：券商研报聚合

**输出格式**: JSON
```json
{
  "timestamp": "2026-03-16T...",
  "hot_stocks": [...],
  "industry_ranking": [
    {
      "name": "白酒",
      "price": 1234.56,
      "pct": 3.5,
      "source": "10jqka_industry"
    }
  ]
}
```

**个股诊断输出**:
```json
{
  "code": "600519",
  "diagnosis": {
    "comprehensive_score": 85,
    "trend_score": 90,
    "valuation": "合理",
    "profit_ability": "优秀",
    "growth": "良好",
    "recommendation": "买入"
  },
  "reports": [...]
}
```

---

## 综合简报生成器

### cn_market_report.py - 中文市场日报

**功能**: 整合所有数据源，生成每日中文市场简报

**使用示例**:
```bash
python3 scripts/cn_market_report.py
```

**输出**:
1. **Markdown 简报**: `reports/cn_daily_digest_YYYY-MM-DD.md`
2. **JSON 数据**: 各数据源的原始 JSON 文件

**简报内容**:
- 观察清单（实时快照）
- A 股榜单（涨幅榜、成交额榜）
- 港股榜单
- 财联社快讯（Top 10）
- 资金流向（主力流入/流出 Top 5）
- 行业板块（Top 10）

**输出路径**:
```
reports/
├── cn_daily_digest_2026-03-16.md
├── cn_hot_2026-03-16.json           (东方财富)
├── cn_watchlist_2026-03-16.json     (新浪财经)
├── cn_cls_2026-03-16.json           (财联社)
├── cn_tencent_2026-03-16.json       (腾讯财经)
└── cn_10jqka_2026-03-16.json        (同花顺)
```

---

## 数据源对比

| 数据源 | 实时性 | 数据丰富度 | 特色功能 | 稳定性 |
|--------|--------|-----------|---------|--------|
| 东方财富 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 涨幅榜、成交额榜 | ⭐⭐⭐⭐⭐ |
| 新浪财经 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 实时报价 | ⭐⭐⭐⭐⭐ |
| 财联社 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 实时快讯、专业资讯 | ⭐⭐⭐⭐ |
| 腾讯财经 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 资金流向、概念板块 | ⭐⭐⭐⭐ |
| 同花顺 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 诊股、研报、行业分析 | ⭐⭐⭐⭐ |

---

## 注意事项

### API 限制
- 所有数据源均为爬取公开数据，可能受反爬虫限制
- 建议合理控制请求频率（建议间隔 > 3 秒）
- 某些接口可能需要 Cookie 或 User-Agent

### 数据延迟
- 新浪财经：实时（< 1 秒）
- 东方财富：准实时（< 5 秒）
- 财联社：实时快讯（< 30 秒）
- 腾讯财经：1-5 分钟
- 同花顺：1-5 分钟

### 稳定性
- 网站改版可能导致数据解析失败
- 建议使用 try-except 容错处理
- cn_market_report.py 已内置容错机制

---

## 使用建议

### 1. 盘前准备（08:00-09:30）
```bash
# 生成每日简报
python3 scripts/cn_market_report.py

# 查看财联社快讯
python3 scripts/cn_cls_telegraph.py
```

### 2. 盘中监控（09:30-15:00）
```bash
# 监控自选股
python3 scripts/cn_stock_quotes.py 600519 000001 600036

# 查看资金流向
python3 scripts/cn_tencent_moneyflow.py

# 查看热门股票
python3 scripts/cn_market_rankings.py
```

### 3. 盘后分析（15:00-18:00）
```bash
# 行业分析
python3 scripts/cn_ths_diagnosis.py

# 个股诊断
python3 scripts/cn_ths_diagnosis.py 600519

# 综合简报
python3 scripts/cn_market_report.py
```

### 4. 定时任务（Cron）
```cron
# 每天 07:55 生成盘前简报
55 7 * * 1-5 cd /path/to/project && python3 scripts/cn_market_report.py

# 每天 15:30 生成盘后简报
30 15 * * 1-5 cd /path/to/project && python3 scripts/cn_market_report.py
```

---

## 未来计划

- [ ] 添加龙虎榜数据（东方财富）
- [ ] 添加北向资金（沪深港通）
- [ ] 添加融资融券数据
- [ ] 添加大宗交易数据
- [ ] 优化数据缓存机制
- [ ] 添加数据质量监控
- [ ] 支持更多个股 F10 资料

---

## 技术支持

- 项目主页: https://github.com/ZhenRobotics/openclaw-research-analyst
- 问题反馈: https://github.com/ZhenRobotics/openclaw-research-analyst/issues

---

**免责声明**: 所有数据仅供参考，不构成投资建议。投资有风险，决策需谨慎。
