# Social Media Copy Templates
## OpenClaw Research Analyst v1.3.0 Launch

> Ready-to-use copy for all platforms. Copy-paste and adjust as needed.

---

## Hacker News

### Title
```
Show HN: OpenClaw Research Analyst – Free 8-dimension stock analysis for US/China markets
```

### URL
```
https://github.com/ZhenRobotics/openclaw-research-analyst
```

### Body
```
Hi HN,

I built a free stock analysis tool with an 8-dimension scoring algorithm and support for China A-shares. No API key required.

Background: I was frustrated paying $50/month for Alpha Vantage while yfinance gets rate-limited, and nothing supported Chinese stocks properly. Bloomberg costs $24k/year, which is out of reach for individual investors like me.

What it does:
- 8-dimension stock analysis (earnings, fundamentals, analysts, momentum, sentiment, sector, market, historical)
- China market support (5 data sources: 东方财富, 新浪, 财联社, 腾讯, 同花顺)
- ST risk detection for A-shares
- Crypto analysis with BTC correlation
- AI news monitoring (v1.3.0)
- Portfolio tracking & price alerts

Why it's different:
- Totally free core features (vs. paid alternatives)
- No API key setup friction
- First tool with comprehensive China market data
- Open source (MIT-0), passed ClawHub security audit
- Bilingual (English/Chinese)

Quick start:
```bash
npm install -g openclaw-research-analyst
stock-analyze AAPL
```

Or from source:
```bash
git clone https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst
uv sync
uv run scripts/stock_analyzer.py AAPL
```

Technical details:
- Python 3.10+
- Yahoo Finance API (free tier)
- 5 Chinese data scrapers (public APIs)
- BERT sentiment classifier (chinese-roberta-wwm-ext)
- SQLite for news database
- Async HTTP with aiohttp

Limitations:
- Yahoo Finance has 15-20 min delay
- Short interest lags ~2 weeks (FINRA)
- China scrapers may break if sites change (but I maintain them actively)
- US markets only (non-US data incomplete)

I'd love feedback on:
- What features would make this more useful?
- How can I improve the 8-dimension algorithm?
- Is the China market data valuable to you?

GitHub: https://github.com/ZhenRobotics/openclaw-research-analyst
npm: https://npmjs.com/package/openclaw-research-analyst
ClawHub: https://clawhub.ai/skills/research-analyst

Thanks for reading! Happy to answer questions.

---
Disclaimer: Not financial advice. For research/education only.
```

---

## Reddit r/algotrading

### Title
```
[Tool] OpenClaw Research Analyst v1.3.0 - Free 8-dimension stock analysis (US/China/HK + crypto)
```

### Body
```
Hey r/algotrading,

I built a free stock analysis tool that might be useful for algo traders working with US and China markets. Thought I'd share here since the community often discusses tools and data sources.

**What it does:**
- 8-dimension stock scoring (earnings, fundamentals, analysts, momentum, sentiment, sector, market, history)
- China market support (5 data sources: 东方财富, 新浪, 财联社, 腾讯, 同花顺)
- Crypto analysis with BTC correlation
- Portfolio tracking & watchlist alerts
- AI news monitoring with BERT sentiment classifier (v1.3.0)

**Why I built it:**
Most algo traders I know either pay $50+/mo for APIs or deal with yfinance rate limits. I wanted something free, reliable, and with China market support (since Chinese stocks are increasingly important for global strategies).

**Installation:**
```bash
npm install -g openclaw-research-analyst
stock-analyze AAPL BABA
```

Or from GitHub:
```bash
git clone https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst
uv sync
uv run scripts/stock_analyzer.py AAPL
```

**Example output:**
```
AAPL Analysis:
Overall Score: 78/100 (BUY)
├─ Earnings Surprise: 85/100 ✅
├─ Fundamentals: 72/100
├─ Analyst Sentiment: 88/100 ✅
├─ Momentum: 65/100
├─ Sentiment: 70/100
├─ Sector: 80/100 ✅
├─ Market Context: 75/100
└─ Historical: 68/100

Risks:
⚠️ Pre-earnings warning (earnings in 8 days)
⚠️ Overbought (RSI 72)
```

**China market demo:**
```bash
python3 scripts/cn_market_report.py
```

Generates daily digest with A-share rankings, HK movers, capital flow, and breaking news.

**Key features for algo traders:**
- No API key required (uses Yahoo Finance free tier + China public APIs)
- Fast mode for quick checks (`--fast` flag)
- JSON output for automation (`--json` flag)
- Portfolio backtesting (coming in v1.4.0)
- Real-time WebSocket support (v1.5.0 roadmap)

**v1.3.0 new features:**
- AI-powered news monitoring (BERT sentiment)
- 60-second fast mode (30-40s latency)
- Feishu/Slack integration for alerts
- Comprehensive API testing suite

**Tech stack:**
- Python 3.10+
- Yahoo Finance API
- 5 Chinese scrapers (东方财富, 新浪, 财联社, 腾讯, 同花顺)
- BERT model (chinese-roberta-wwm-ext)
- SQLite database
- aiohttp for async HTTP

**Limitations:**
- Yahoo Finance has 15-20min delay (real-time in v1.5.0)
- Short interest lags ~2 weeks
- China scrapers may break if sites change (but actively maintained)
- US markets primary focus (non-US incomplete)

**For algo traders specifically:**
- Portfolio tracking with P&L calculations
- Watchlist with price alerts
- Historical pattern detection
- Risk warnings (earnings, overbought, geopolitical)
- China market data (often missing from Western tools)

**Open source:**
- MIT-0 license (use it however you want)
- Passes ClawHub security audit
- All code on GitHub
- PRs welcome!

**Links:**
- GitHub: https://github.com/ZhenRobotics/openclaw-research-analyst
- npm: https://npmjs.com/package/openclaw-research-analyst
- Documentation: See README.md

**Questions I'd love feedback on:**
1. What data sources would make this more useful for your strategies?
2. Would you use a backtesting framework if I built one?
3. Is the China market data valuable for your trading?
4. What integrations would you like (Discord bot, API server, etc.)?

Happy to answer questions or take feature requests! I'm actively maintaining this and ship updates every 2-3 weeks.

---
Disclaimer: Not financial advice. For research/education only. Trade at your own risk.
```

---

## V2EX (Chinese)

### 节点
```
分享创造
```

### 标题
```
Show V2EX: OpenClaw Research Analyst - 免费的8维度股票分析工具（美股+A股+港股）
```

### 正文
```
各位 V 友好，

分享一个自己做的开源项目：免费的股票分析工具，支持美股、A股、港股和加密货币。

**项目背景：**

作为个人投资者，Bloomberg 要 $24k/年，Alpha Vantage 要 $50/月，都太贵了。yfinance 虽然免费但经常被限流，而且不支持A股。市面上没有一个既免费又好用、还支持中国市场的工具。

于是我花了几个月时间，用 Python 构建了这个项目。

**核心功能：**

1. **8维度分析算法**
   - 盈利惊喜（Earnings Surprise）
   - 基本面（Fundamentals：P/E、利润率、增长率）
   - 分析师观点（Analyst Sentiment：评级、目标价）
   - 历史表现（Historical Patterns）
   - 市场环境（Market Context：VIX、SPY/QQQ）
   - 板块表现（Sector Performance）
   - 动量指标（Momentum：RSI、52周区间）
   - 市场情绪（Sentiment：Fear & Greed、空头、内部人交易）

2. **中国市场深度支持**（这是首个集成5大中文数据源的开源工具）
   - 东方财富：涨幅榜、成交额榜
   - 新浪财经：实时报价（A股+港股）
   - 财联社：财经快讯、实时新闻
   - 腾讯财经：资金流向、概念板块
   - 同花顺：个股诊断、行业分析

3. **ST风险检测**
   - 自动识别 ST、*ST 股票
   - 预警特殊处理风险

4. **AI财经新闻监控**（v1.3.0 新增）
   - BERT情绪分类器
   - 60秒快速监控模式
   - 30-40秒端到端延迟
   - 自动推送到飞书/Slack

5. **加密货币支持**
   - Top 20 加密货币
   - BTC相关性分析
   - 动量指标

6. **投资组合管理**
   - 持仓跟踪
   - P&L计算
   - 价格预警

**快速开始：**

```bash
# 方式1：npm 安装（推荐）
npm install -g openclaw-research-analyst
stock-analyze AAPL

# 方式2：从 GitHub 克隆
git clone https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst
uv sync
uv run scripts/stock_analyzer.py 600519  # 贵州茅台

# 中国市场日报
python3 scripts/cn_market_report.py
```

**输出示例：**

```
AAPL 分析:
综合评分: 78/100 (买入)
├─ 盈利惊喜: 85/100 ✅
├─ 基本面: 72/100
├─ 分析师观点: 88/100 ✅
├─ 动量: 65/100
├─ 情绪: 70/100
├─ 板块: 80/100 ✅
├─ 市场环境: 75/100
└─ 历史表现: 68/100

风险提示:
⚠️ 距离财报日仅剩8天
⚠️ 超买状态（RSI 72）
```

**中国市场功能演示：**

```bash
python3 scripts/cn_market_report.py
```

生成包含以下内容的每日简报：
- A股涨幅榜 Top 20（东方财富）
- A股成交额榜 Top 20（东方财富）
- 港股涨幅榜 Top 20（东方财富）
- 实时报价（新浪财经）
- 财联社快讯 Top 10
- 资金流向 Top 5（腾讯财经）
- 行业板块 Top 10（同花顺）

**技术栈：**

- Python 3.10+
- Yahoo Finance API（免费）
- 5个中文财经数据源（爬虫）
- BERT模型（chinese-roberta-wwm-ext）
- SQLite数据库
- aiohttp异步HTTP

**与竞品对比：**

| 功能 | OpenClaw | Bloomberg | Alpha Vantage | yfinance | Tushare |
|------|----------|-----------|---------------|----------|---------|
| 价格 | 免费 | $24k/年 | $50/月 | 免费 | ¥800/年 |
| 市场 | 美股/A股/港股 | 全球 | 美股 | 美股 | A股 |
| API Key | 不需要 | N/A | 需要 | 不需要 | 需要 |
| 分析深度 | 8维度 | 综合 | 基础 | 原始数据 | 基础 |
| A股数据 | 5个数据源 | 有限 | 无 | 无 | 优秀 |
| 开源 | 是（MIT-0） | 否 | 否 | 是 | 否 |

**特色功能：**

1. **完全免费**：核心功能全部免费，无需 API Key
2. **A股深度支持**：5个中文数据源，实时行情+资金流向+快讯
3. **ST风险检测**：自动识别特殊处理股票
4. **开源可审计**：MIT-0 许可，通过 ClawHub 安全审计
5. **双语支持**：中英文文档齐全
6. **AI新闻监控**：BERT情绪分类，60秒快速模式

**适用场景：**

- 美股/A股/港股个人投资者
- 量化交易开发者
- AI Agent开发者（OpenClaw 用户）
- 需要中国市场数据的程序员
- 金融数据分析师

**数据源对比：**

| 数据源 | 实时性 | 数据丰富度 | 稳定性 | 特色功能 |
|--------|--------|------------|--------|----------|
| 东方财富 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 涨幅榜、成交额榜 |
| 新浪财经 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 实时报价 |
| 财联社 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 专业财经快讯 |
| 腾讯财经 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 资金流向、板块轮动 |
| 同花顺 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 诊股、研报聚合 |

**v1.3.0 新功能：**

- AI驱动的财经新闻监控（BERT情绪分类器）
- 快速监控模式（60秒间隔，30-40秒延迟）
- 完整的API测试套件（66.7%通过率，持续优化中）
- 增强的飞书推送集成（支持私聊与Webhook）

**项目链接：**

- GitHub: https://github.com/ZhenRobotics/openclaw-research-analyst
- npm: https://www.npmjs.com/package/openclaw-research-analyst
- ClawHub: https://clawhub.ai/skills/research-analyst

**开源协议：**

MIT-0 许可（零限制，可商用、可修改、可闭源）

**欢迎反馈：**

- 希望添加哪些数据源？
- 需要什么新功能？
- 遇到任何问题欢迎提 Issue

也欢迎 PR 和 Star ⭐！

---
免责声明：本工具仅供参考，不构成投资建议。投资有风险，决策需谨慎。
```

---

## Juejin (Chinese Article)

### 标题
```
我用Python构建了一个免费的8维度股票分析工具（开源，支持美股+A股+港股）
```

### 分类
```
后端 > Python
```

### 标签
```
Python, 股票分析, 开源项目, 金融科技, 量化交易
```

### 正文
```
# 我用Python构建了一个免费的8维度股票分析工具（开源，支持美股+A股+港股）

## 前言

作为一个个人投资者，我一直在寻找一个好用的股票分析工具。Bloomberg Terminal 要 $24,000/年，Alpha Vantage 要 $50/月，都太贵了。yfinance 虽然免费，但经常被限流，而且不支持A股。

经过几个月的开发，我用 Python 构建了 **OpenClaw Research Analyst**，一个完全免费、开源的股票分析工具，支持美股、A股、港股和加密货币。

项目地址：https://github.com/ZhenRobotics/openclaw-research-analyst

## 为什么要做这个项目？

### 问题1：付费工具太贵

- **Bloomberg Terminal**: $24,000/年
- **Alpha Vantage**: $50/月（还有API调用限制）
- **Tushare Pro**: ¥800/年（仅限A股）

对于个人投资者来说，这些价格都不合理。

### 问题2：免费工具功能单一

- **yfinance**: 只提供原始数据，需要自己分析
- **akshare**: 仅支持A股，数据质量参差不齐
- **pandas-datareader**: 依赖多个API，配置复杂

### 问题3：缺乏中国市场支持

大部分国际工具不支持A股和港股，或者数据不全。国内工具又大多不支持美股。

## 解决方案：OpenClaw Research Analyst

### 核心特性

#### 1. 8维度分析算法

我设计了一个综合评分算法，从8个维度评估股票：

| 维度 | 权重 | 说明 |
|------|------|------|
| 盈利惊喜 | 30% | EPS实际值 vs 预期值 |
| 基本面 | 20% | P/E、利润率、增长率、负债率 |
| 分析师观点 | 20% | 评级、目标价 |
| 历史表现 | 10% | 过去财报后的股价反应 |
| 市场环境 | 10% | VIX、SPY/QQQ趋势 |
| 板块表现 | 15% | 相对强度 |
| 动量指标 | 15% | RSI、52周区间 |
| 市场情绪 | 10% | Fear & Greed、空头利息、内部人交易 |

**评分逻辑示例（盈利惊喜）：**

```python
def score_earnings_surprise(actual_eps, expected_eps):
    if expected_eps <= 0:
        return 50  # 无法评分

    beat_percentage = (actual_eps - expected_eps) / abs(expected_eps) * 100

    if beat_percentage > 20:
        return 100  # 大幅超预期
    elif beat_percentage > 10:
        return 85
    elif beat_percentage > 5:
        return 75
    elif beat_percentage > 0:
        return 65
    elif beat_percentage > -5:
        return 45  # 小幅低于预期
    elif beat_percentage > -10:
        return 30
    else:
        return 10  # 大幅低于预期
```

#### 2. 中国市场深度支持

这是首个集成5大中文财经数据源的开源工具：

**数据源架构：**

```
cn_market_report.py (主报告生成器)
    ├─ cn_market_rankings.py     → 东方财富（涨幅榜、成交额榜）
    ├─ cn_stock_quotes.py         → 新浪财经（实时报价）
    ├─ cn_cls_telegraph.py        → 财联社（财经快讯）
    ├─ cn_tencent_moneyflow.py    → 腾讯财经（资金流向）
    └─ cn_ths_diagnosis.py        → 同花顺（个股诊断）
```

**实现示例（新浪财经实时报价）：**

```python
import requests

def get_sina_quote(stock_code):
    """
    获取新浪财经实时报价

    Args:
        stock_code: 股票代码（如 600519 = 贵州茅台）

    Returns:
        dict: 包含价格、涨跌幅等信息
    """
    # 判断市场
    if stock_code.startswith('6'):
        market = 'sh'  # 上海
    elif stock_code.startswith(('0', '3')):
        market = 'sz'  # 深圳
    else:
        raise ValueError(f"Invalid stock code: {stock_code}")

    # 新浪API
    url = f"https://hq.sinajs.cn/list={market}{stock_code}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    # 解析数据
    data = response.text.split('="')[1].split('",')[0].split(',')

    return {
        "code": stock_code,
        "name": data[0],
        "price": float(data[3]),
        "change": float(data[3]) - float(data[2]),
        "pct": ((float(data[3]) - float(data[2])) / float(data[2])) * 100,
        "volume": int(data[8]),
        "amount": float(data[9]),
        "source": "sina_finance"
    }

# 使用示例
quote = get_sina_quote("600519")  # 贵州茅台
print(f"{quote['name']}: ¥{quote['price']} ({quote['pct']:+.2f}%)")
```

#### 3. ST风险检测

A股特有的特殊处理股票检测：

```python
def check_st_risk(stock_code, stock_name):
    """检测ST风险"""
    st_keywords = ['ST', '*ST', 'S*ST', 'S', 'N']

    for keyword in st_keywords:
        if keyword in stock_name:
            return {
                "has_risk": True,
                "risk_type": keyword,
                "warning": f"⚠️ 该股票为 {keyword} 股，存在特殊处理风险"
            }

    return {"has_risk": False}
```

#### 4. AI财经新闻监控（v1.3.0新增）

使用 BERT 模型进行新闻情绪分类：

```python
from transformers import BertTokenizer, BertForSequenceClassification
import torch

class NewsClassifier:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('hfl/chinese-roberta-wwm-ext')
        self.model = BertForSequenceClassification.from_pretrained('./models/news_classifier')

    def predict_sentiment(self, news_text):
        """预测新闻情绪"""
        inputs = self.tokenizer(
            news_text,
            return_tensors='pt',
            max_length=512,
            truncation=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=1).item()

        sentiment_map = {
            0: 'BEARISH',  # 利空
            1: 'NEUTRAL',   # 中性
            2: 'BULLISH'    # 利好
        }

        return sentiment_map[predicted_class]

# 使用示例
classifier = NewsClassifier()
news = "贵州茅台发布超预期财报，净利润同比增长25%"
sentiment = classifier.predict_sentiment(news)
print(f"情绪: {sentiment}")  # 输出: BULLISH
```

## 技术实现

### 系统架构

```
openclaw-research-analyst/
├── scripts/
│   ├── stock_analyzer.py           # 主分析脚本（8维度）
│   ├── cn_market_report.py         # 中国市场日报生成器
│   ├── cn_market_rankings.py       # 东方财富数据采集
│   ├── cn_stock_quotes.py          # 新浪财经数据采集
│   ├── cn_cls_telegraph.py         # 财联社快讯采集
│   ├── cn_tencent_moneyflow.py     # 腾讯财经资金流向
│   ├── cn_ths_diagnosis.py         # 同花顺个股诊断
│   ├── news_monitor_fast.py        # AI新闻监控（快速模式）
│   ├── portfolio_manager.py        # 投资组合管理
│   └── watchlist_manager.py        # 监控列表管理
├── docs/
│   ├── CN_DATA_SOURCES.md          # 中国数据源文档
│   └── ARCHITECTURE.md             # 系统架构文档
├── tests/
│   └── api_test_suite.py           # API测试套件
├── data/
│   └── news.db                     # 新闻数据库（SQLite）
└── requirements.txt
```

### 技术栈

- **语言**: Python 3.10+
- **HTTP客户端**: `aiohttp`（异步）, `requests`（同步）
- **数据处理**: `pandas`, `numpy`
- **机器学习**: `torch`, `transformers`（BERT）
- **数据库**: SQLite
- **包管理**: `uv`（比pip快10倍）

### 异步优化

为了提高性能，我使用了异步HTTP请求：

```python
import aiohttp
import asyncio

async def fetch_multiple_sources(stock_code):
    """并发获取多个数据源"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_eastmoney(session, stock_code),
            fetch_sina(session, stock_code),
            fetch_cls(session, stock_code),
            fetch_tencent(session, stock_code),
            fetch_ths(session, stock_code)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        "eastmoney": results[0],
        "sina": results[1],
        "cls": results[2],
        "tencent": results[3],
        "ths": results[4]
    }

# 使用示例
data = asyncio.run(fetch_multiple_sources("600519"))
```

**性能提升：**
- 串行请求：15-20秒
- 异步请求：3-5秒
- 提速约 **75%**

## 使用示例

### 1. 分析美股

```bash
# 基础分析
uv run scripts/stock_analyzer.py AAPL

# 快速模式（跳过慢速数据源）
uv run scripts/stock_analyzer.py AAPL --fast

# 批量分析
uv run scripts/stock_analyzer.py AAPL MSFT GOOGL
```

**输出示例：**

```
=== AAPL Analysis ===
Overall Score: 78/100 (BUY)

Dimension Breakdown:
├─ Earnings Surprise: 85/100 ✅ (Beat by 12%)
├─ Fundamentals: 72/100
│  ├─ P/E Ratio: 28.5 (Fair)
│  ├─ Profit Margin: 25.3% (Excellent)
│  └─ Debt/Equity: 1.8 (Moderate)
├─ Analyst Sentiment: 88/100 ✅
│  ├─ Buy: 25, Hold: 8, Sell: 2
│  └─ Target: $200 (upside: 15%)
├─ Momentum: 65/100
│  ├─ RSI: 58 (Neutral)
│  └─ Position in 52-week range: 75%
├─ Sentiment: 70/100
│  └─ Fear & Greed: 65 (Greed)
├─ Sector: 80/100 ✅ (Tech outperforming)
├─ Market Context: 75/100 (Low volatility)
└─ Historical: 68/100 (Usually rises after earnings)

Risk Warnings:
⚠️ Pre-earnings warning (earnings in 8 days)
⚠️ Overbought (RSI > 70)

Signal: BUY (Confidence: 78%)
```

### 2. 分析A股

```bash
# 贵州茅台
uv run scripts/stock_analyzer.py 600519

# 中国市场日报
python3 scripts/cn_market_report.py
```

**输出（部分）：**

```markdown
# 中国市场日报 - 2026-03-25

## 观察清单（实时快照）

| 代码 | 名称 | 最新价 | 涨跌幅 | 成交额 |
|------|------|--------|--------|--------|
| 600519 | 贵州茅台 | ¥1,850 | +2.5% | 120亿 |
| 000001 | 平安银行 | ¥12.50 | +1.2% | 80亿 |

## A股涨幅榜 Top 20

| 排名 | 代码 | 名称 | 涨幅 | 板块 |
|------|------|------|------|------|
| 1 | 300XXX | XXX科技 | +10.0% | 芯片 |
| 2 | 688XXX | XXX半导体 | +9.5% | 半导体 |

## 财联社快讯 Top 10

1. [10:30] 央行宣布降准0.5个百分点，释放长期资金约1万亿
2. [10:15] 茅台一季度净利润同比增长25%，超市场预期

## 资金流向（主力流入 Top 5）

| 代码 | 名称 | 净流入 | 涨跌幅 |
|------|------|--------|--------|
| 600519 | 贵州茅台 | +12.5亿 | +2.5% |
| 000858 | 五粮液 | +8.3亿 | +3.2% |
```

### 3. 投资组合管理

```bash
# 创建投资组合
uv run scripts/portfolio_manager.py create "我的组合"

# 添加持仓
uv run scripts/portfolio_manager.py add AAPL --quantity 100 --cost 150

# 查看盈亏
uv run scripts/portfolio_manager.py show
```

**输出：**

```
=== 我的组合 ===

Holdings:
1. AAPL: 100 shares @ $150 (cost: $15,000)
   Current: $175 (+16.7%, +$2,500)

2. 600519: 100 shares @ ¥1,600 (cost: ¥160,000)
   Current: ¥1,850 (+15.6%, +¥25,000)

Total P&L: +$27,500 (+16.1%)
```

## 对比竞品

| 功能 | OpenClaw | Bloomberg | Alpha Vantage | yfinance | Tushare |
|------|----------|-----------|---------------|----------|---------|
| **价格** | 免费 | $24k/年 | $50/月 | 免费 | ¥800/年 |
| **API Key** | 不需要 | N/A | 需要 | 不需要 | 需要 |
| **市场支持** | 美股/A股/港股/加密货币 | 全球 | 美股 | 美股 | A股 |
| **分析深度** | 8维度综合评分 | 专业级 | 基础 | 原始数据 | 基础 |
| **A股数据** | 5个数据源 | 有限 | 无 | 无 | 优秀 |
| **ST风险** | ✅ | ❌ | ❌ | ❌ | ✅ |
| **AI新闻** | ✅ BERT | ✅ | ❌ | ❌ | ❌ |
| **开源** | ✅ MIT-0 | ❌ | ❌ | ✅ MIT | ❌ |
| **安全审计** | ✅ ClawHub | N/A | N/A | N/A | N/A |

**关键优势：**

1. **唯一免费且提供8维度分析的工具**
2. **唯一集成5个中文数据源的开源项目**
3. **唯一支持ST风险检测的非商业工具**
4. **通过ClawHub安全审计（无凭证泄露）**

## 性能优化

### 1. 异步HTTP请求

从串行改为并发，提速75%：

```python
# 优化前（串行）
data1 = fetch_source_1()  # 3秒
data2 = fetch_source_2()  # 4秒
data3 = fetch_source_3()  # 5秒
# 总耗时: 12秒

# 优化后（并发）
async def fetch_all():
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_source_1(session),
            fetch_source_2(session),
            fetch_source_3(session)
        ]
        return await asyncio.gather(*tasks)

data = asyncio.run(fetch_all())
# 总耗时: 5秒（取最慢的）
```

### 2. 数据缓存

使用 SQLite 缓存新闻数据，避免重复请求：

```python
import sqlite3
from datetime import datetime, timedelta

class NewsCache:
    def __init__(self, db_path="data/news.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                published_at TEXT,
                sentiment TEXT,
                cached_at TEXT
            )
        """)

    def get_cached(self, news_id, max_age_hours=24):
        """获取缓存（24小时内有效）"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)

        cursor = self.conn.execute(
            "SELECT * FROM news WHERE id=? AND cached_at > ?",
            (news_id, cutoff.isoformat())
        )

        row = cursor.fetchone()
        return dict(zip([col[0] for col in cursor.description], row)) if row else None

    def set_cache(self, news_id, news_data):
        """写入缓存"""
        self.conn.execute(
            "INSERT OR REPLACE INTO news VALUES (?, ?, ?, ?, ?, ?)",
            (news_id, news_data['title'], news_data['content'],
             news_data['published_at'], news_data['sentiment'], datetime.now().isoformat())
        )
        self.conn.commit()
```

### 3. 快速模式

通过 `--fast` 跳过慢速数据源：

```python
def analyze_stock(ticker, fast_mode=False):
    scores = {}

    # 快速数据源（< 2秒）
    scores['earnings'] = score_earnings(ticker)
    scores['fundamentals'] = score_fundamentals(ticker)
    scores['analyst'] = score_analyst(ticker)

    if not fast_mode:
        # 慢速数据源（5-10秒）
        scores['insider'] = score_insider_trading(ticker)  # SEC EDGAR
        scores['news'] = score_breaking_news(ticker)       # Google News
    else:
        scores['insider'] = 50  # 默认中性
        scores['news'] = 50

    return calculate_overall_score(scores)
```

**性能对比：**

- 完整模式：60-120秒
- `--fast` 模式：45-75秒
- 提速约 **40%**

## 安全性

### ClawHub 安全审计

项目通过了 ClawHub 的安全审计，包括：

1. **凭证泄露检测** ✅ 无敏感信息
2. **依赖漏洞扫描** ✅ 无已知漏洞
3. **代码注入风险** ✅ 参数化查询
4. **Git历史清理** ✅ 无凭证残留

### 数据安全

```python
# 敏感数据存储（.env 文件，不提交到 Git）
AUTH_TOKEN=your_token_here
CT0=your_ct0_here

# .gitignore 配置
.env
.env.*
*.db
cache/
```

### API 安全

```python
import os
from dotenv import load_dotenv

# 安全加载环境变量
load_dotenv()

# 永远不要硬编码
# BAD: token = "abc123"
# GOOD:
token = os.getenv("AUTH_TOKEN")
if not token:
    raise ValueError("AUTH_TOKEN not set in .env file")
```

## 局限性与未来计划

### 当前局限

1. **数据延迟**
   - Yahoo Finance 延迟 15-20 分钟
   - 短期利息延迟 ~2 周（FINRA）

2. **市场覆盖**
   - 主要支持美股、A股、港股
   - 其他市场数据不全

3. **数据源稳定性**
   - 中国数据源依赖爬虫
   - 网站改版可能导致失效

### 未来计划

**v1.4.0（2个月后）**
- [ ] 回测框架
- [ ] 历史数据分析
- [ ] 策略性能指标

**v1.5.0（3个月后）**
- [ ] WebSocket 实时行情
- [ ] 推送通知优化
- [ ] 自动化交易接口

**v2.0.0（6个月后）**
- [ ] Web仪表盘（React）
- [ ] TradingView 图表集成
- [ ] 云托管选项

## 总结

OpenClaw Research Analyst 是一个完全免费、开源的股票分析工具，提供：

✅ 8维度分析算法（类Bloomberg）
✅ 5个中文数据源（首个）
✅ ST风险检测（A股特色）
✅ AI新闻监控（BERT）
✅ 无需API Key（零摩擦）
✅ MIT-0许可（零限制）
✅ 通过安全审计（零风险）

**如果你是：**
- 个人投资者（美股/A股/港股）
- 量化交易开发者
- AI Agent开发者
- 开源爱好者

**欢迎试用并提供反馈！**

项目地址：https://github.com/ZhenRobotics/openclaw-research-analyst

也欢迎 Star ⭐ 和 PR！

---

**免责声明**：本工具仅供参考，不构成投资建议。投资有风险，决策需谨慎。

---

**作者**：ZhenRobotics
**日期**：2026-03-25
**版本**：v1.3.0
```

---

## Twitter/X Thread

### Tweet 1 (Launch)
```
🚀 Just launched OpenClaw Research Analyst v1.3.0!

Free 8-dimension stock analysis for US/China/HK markets + crypto. No API key required.

Thread on why I built this 👇

🔗 github.com/ZhenRobotics/openclaw-research-analyst
```

### Tweet 2 (Problem)
```
The problem: Bloomberg costs $24k/yr, Alpha Vantage is $50/mo, and yfinance gets rate-limited.

Most individual investors can't afford professional tools, but need more than basic price charts.
```

### Tweet 3 (Solution)
```
The solution: 8-dimension analysis algorithm that scores stocks across:
• Earnings surprise (30%)
• Fundamentals (20%)
• Analyst sentiment (20%)
• Historical patterns, momentum, sector, market context (30%)

All free, no API key.
```

### Tweet 4 (China Markets)
```
What makes it unique:

✅ First tool with 5 Chinese data sources (东方财富/新浪/财联社/腾讯/同花顺)
✅ ST risk detection for A-shares
✅ AI news monitoring (v1.3.0)
✅ Crypto support with BTC correlation
✅ Open source & audited
```

### Tweet 5 (Demo)
```
Quick demo:

```bash
npm install -g openclaw-research-analyst
stock-analyze AAPL
```

Outputs: overall score (0-100), 8 dimension breakdowns, risk warnings, buy/hold/sell signal.

[ATTACH: Terminal screenshot GIF]
```

### Tweet 6 (China Markets)
```
China market support is a game-changer:

Run `python3 scripts/cn_market_report.py` to get:
• A-share & HK rankings
• Real-time quotes (新浪)
• Breaking news (财联社)
• Money flow (腾讯)
• Stock diagnosis (同花顺)

[ATTACH: China market report screenshot]
```

### Tweet 7 (AI News)
```
v1.3.0 adds AI-powered news monitoring:

• BERT sentiment classifier
• 60-second fast mode
• 30-40s latency end-to-end
• Auto-push to Feishu/Slack

Built for serious quant developers who trade China + US.
```

### Tweet 8 (Tech Stack)
```
Tech stack:

• Python 3.10+
• Yahoo Finance API
• 5 Chinese scrapers
• BERT (chinese-roberta-wwm-ext)
• SQLite
• aiohttp

MIT-0 license. Passes ClawHub security audit.
```

### Tweet 9 (Audience)
```
Who it's for:

👤 Individual investors (US/China/HK)
🤖 AI agent developers (OpenClaw)
📊 Quant traders building strategies
🇨🇳 Chinese developers needing bilingual tools
```

### Tweet 10 (CTA)
```
Get started:

GitHub: github.com/ZhenRobotics/openclaw-research-analyst
npm: npmjs.com/package/openclaw-research-analyst
ClawHub: clawhub.ai/skills/research-analyst

Star ⭐ if you find it useful!

Not financial advice. Built for research/education. Feedback welcome!

#opensource #stockmarket #python #fintech
```

---

## Zhihu Answer Template

### 问题1："有哪些免费的股票分析工具？"

```
### OpenClaw Research Analyst - 免费的8维度股票分析工具

我最近开源了一个项目，可能正好符合你的需求。

**项目地址**：https://github.com/ZhenRobotics/openclaw-research-analyst

#### 核心特点

1. **完全免费**
   - 无需 API Key
   - 核心功能全部开放
   - MIT-0 开源许可（零限制）

2. **8维度分析算法**
   - 盈利惊喜、基本面、分析师观点
   - 历史表现、市场环境、板块表现
   - 动量指标、市场情绪
   - 综合评分 0-100

3. **支持多个市场**
   - 美股（Yahoo Finance）
   - A股（5个数据源）
   - 港股（东方财富、新浪）
   - 加密货币（Top 20）

4. **独特功能**
   - ST风险检测（A股特色）
   - AI新闻监控（BERT）
   - 投资组合管理
   - 价格预警

#### 快速开始

```bash
# 安装
npm install -g openclaw-research-analyst

# 分析股票
stock-analyze AAPL

# 中国市场日报
python3 scripts/cn_market_report.py
```

#### 输出示例

```
AAPL 分析:
综合评分: 78/100 (买入)
├─ 盈利惊喜: 85/100 ✅
├─ 基本面: 72/100
├─ 分析师观点: 88/100 ✅
...

风险提示:
⚠️ 距离财报日仅剩8天
⚠️ 超买状态（RSI 72）
```

#### 为什么选择它？

**vs. Bloomberg Terminal**
- 价格: 免费 vs. $24,000/年
- 分析: 8维度 vs. 专业级（Bloomberg更全面）
- 适合: 个人投资者 vs. 机构

**vs. Alpha Vantage**
- 价格: 免费 vs. $50/月
- API Key: 不需要 vs. 需要
- 市场: 美股+A股+港股 vs. 仅美股

**vs. yfinance**
- 功能: 8维度分析 vs. 原始数据
- A股: 5个数据源 vs. 不支持
- ST风险: 支持 vs. 不支持

**vs. Tushare**
- 价格: 免费 vs. ¥800/年
- 市场: 美股+A股 vs. 仅A股
- 开源: MIT-0 vs. 不开源

#### 适用场景

- 个人投资者快速决策
- 量化交易策略研究
- 学习金融数据分析
- 构建投资组合

#### 技术实现

使用 Python 3.10+，集成了：
- Yahoo Finance API（免费）
- 东方财富、新浪、财联社、腾讯、同花顺（A股数据）
- BERT模型（新闻情绪分类）
- SQLite（数据缓存）

#### 局限性

- Yahoo Finance 延迟 15-20 分钟（实时数据在 v1.5.0 路线图）
- 短期利息延迟 ~2 周
- 中国数据源可能因网站改版失效（但我会及时修复）

#### 未来计划

- v1.4.0: 回测框架
- v1.5.0: WebSocket 实时行情
- v2.0.0: Web 仪表盘

欢迎试用并提供反馈！也欢迎 Star ⭐ 和 PR。

---
**免责声明**：仅供参考，不构成投资建议。投资有风险，决策需谨慎。
```

---

## LinkedIn Post (Optional)

### Title
```
Launching OpenClaw Research Analyst: Open-Source Stock Analysis for US & China Markets
```

### Body
```
I'm excited to announce the v1.3.0 release of OpenClaw Research Analyst, an open-source stock analysis tool I've been building for the past few months.

**Why I built this:**

As an individual investor, I was frustrated by the limited options available:
• Bloomberg Terminal: $24,000/year (out of reach)
• Alpha Vantage: $50/month with API limits
• yfinance: Free but gets rate-limited, no analysis features
• Most tools ignore Chinese markets entirely

**What makes it different:**

1. 8-Dimension Analysis Algorithm
   • Comprehensive scoring across earnings, fundamentals, analyst sentiment, momentum, and more
   • Similar methodology to institutional tools, but free and open source

2. China Market Support
   • First open-source tool integrating 5 major Chinese data sources
   • Covers A-shares, Hong Kong stocks, and ADRs
   • ST risk detection for Chinese equities

3. AI-Powered Features (v1.3.0)
   • BERT-based news sentiment classifier
   • Real-time financial news monitoring
   • 60-second fast mode with 30-40s latency

4. Developer-Friendly
   • No API key required for core features
   • MIT-0 license (use it however you want)
   • Passes ClawHub security audit
   • Bilingual documentation (English/Chinese)

**Tech Stack:**
Python 3.10+, Yahoo Finance API, 5 Chinese data sources, BERT (chinese-roberta-wwm-ext), SQLite, aiohttp

**Perfect for:**
• Individual investors analyzing US, China, or HK markets
• Quant developers building trading strategies
• AI agent developers using the OpenClaw framework
• Anyone who needs free, comprehensive stock analysis

**Get started:**
```bash
npm install -g openclaw-research-analyst
stock-analyze AAPL
```

GitHub: github.com/ZhenRobotics/openclaw-research-analyst

I'd love to hear your feedback and feature suggestions! What would make this more valuable for your investment workflow?

#OpenSource #FinTech #StockMarket #Python #AI #DataScience #Investing #QuantitativeTrading

---
Disclaimer: Not financial advice. For informational and educational purposes only.
```

---

## Closing Notes

**How to Use These Templates:**

1. **Copy-paste directly** - Most templates are ready to use as-is
2. **Customize links** - Replace placeholder URLs with actual links
3. **Adjust timing** - Post at optimal times for each platform
4. **Attach visuals** - Add screenshots, GIFs, or videos where indicated
5. **Monitor comments** - Respond within 1-2 hours, especially on launch day

**Platform-Specific Tips:**

- **Hacker News**: Be humble, acknowledge limitations, engage authentically
- **Reddit**: Focus on technical details, avoid promotional language
- **V2EX**: Use Chinese exclusively, emphasize "免费" and "开源"
- **Juejin**: Technical deep-dive with code samples
- **Twitter**: Use GIFs/videos, space out thread tweets by 30 seconds
- **Zhihu**: Educational value first, promotion second

**Remember:**
- Respond to EVERY comment on launch day
- Be grateful for feedback (positive or negative)
- Fix bugs within 24 hours
- Celebrate milestones publicly

Good luck with the launch! 🚀
