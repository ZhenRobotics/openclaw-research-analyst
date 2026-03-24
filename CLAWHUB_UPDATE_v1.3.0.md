# ClawHub 更新内容 v1.3.0

## 📝 更新说明（粘贴到 ClawHub 更新框）

### English Version

## 🎉 v1.3.0 Major Update - AI News Monitoring System

**Release Date**: 2026-03-20
**Commit**: e90cc7f

### What's New

#### 🚀 Real-time Financial News Monitoring
- **Multi-source Collection**: 财联社 (CLS) + 东方财富 (Eastmoney)
- **AI Classification**: BULLISH/BEARISH/NEUTRAL sentiment analysis
- **Smart Push**: Auto-push major news (importance ≥4) to Feishu
- **Test Results**: 100% keyword matching accuracy

#### ⚡ Fast Monitoring Mode
- **60-second interval** (vs 300s default)
- **30-40s end-to-end latency**
- Incremental fetching for efficiency

#### 🧪 Comprehensive API Testing
- **9-point test suite** covering functional, performance, reliability
- **66.7% pass rate** with detailed metrics
- Automated test reports in JSON format

#### 🛠️ New Tools
- `quick_start_ai.sh` - One-click launcher
- `news_monitor_fast.py` - Optimized monitoring
- `api_test_suite.py` - Full API testing
- Interactive labeling tool for AI training

### Quick Start

```bash
# Install (npm)
npm install -g openclaw-research-analyst@1.3.0

# Or (ClawHub)
clawhub install research-analyst

# Start news monitoring (keyword mode, no AI required)
cd openclaw-research-analyst
./scripts/quick_start_ai.sh monitor-keyword

# Fast mode (60s interval)
python3 scripts/news_monitor_fast.py --no-ai --interval 60 --threshold 4

# Run API tests
python3 tests/api_test_suite.py
```

### Documentation

- **AI_NEWS_SYSTEM_GUIDE.md** - Complete workflow (4 stages)
- **API_TESTING_GUIDE.md** - Testing methodology
- **API_TEST_RESULTS_ANALYSIS.md** - Performance analysis

### Links

- 📦 **npm**: https://www.npmjs.com/package/openclaw-research-analyst
- 🐙 **GitHub**: https://github.com/ZhenRobotics/openclaw-research-analyst
- 📋 **Release Notes**: https://github.com/ZhenRobotics/openclaw-research-analyst/releases/tag/v1.3.0
- 🔖 **Commit**: e90cc7f

---

### 中文版本

## 🎉 v1.3.0 重大更新 - AI 新闻监控系统

**发布日期**: 2026-03-20
**提交**: e90cc7f

### 新增功能

#### 🚀 实时财经新闻监控
- **多源采集**: 财联社 + 东方财富
- **AI 分类**: BULLISH/BEARISH/NEUTRAL 情绪分析
- **智能推送**: 自动推送重大新闻（重要性≥4）到飞书
- **测试结果**: 100% 关键词匹配准确率

#### ⚡ 快速监控模式
- **60秒间隔**（默认300秒）
- **30-40秒端到端延迟**
- 增量抓取，高效节能

#### 🧪 全面 API 测试
- **9项测试套件**，覆盖功能、性能、可靠性
- **66.7% 通过率**，详细指标报告
- JSON 格式自动化测试报告

#### 🛠️ 新增工具
- `quick_start_ai.sh` - 一键启动脚本
- `news_monitor_fast.py` - 优化监控
- `api_test_suite.py` - 完整 API 测试
- 交互式标注工具用于 AI 训练

### 快速开始

```bash
# 安装（npm）
npm install -g openclaw-research-analyst@1.3.0

# 或（ClawHub）
clawhub install research-analyst

# 启动新闻监控（关键词模式，无需 AI）
cd openclaw-research-analyst
./scripts/quick_start_ai.sh monitor-keyword

# 快速模式（60秒间隔）
python3 scripts/news_monitor_fast.py --no-ai --interval 60 --threshold 4

# 运行 API 测试
python3 tests/api_test_suite.py
```

### 文档

- **AI_NEWS_SYSTEM_GUIDE.md** - 完整工作流（4个阶段）
- **API_TESTING_GUIDE.md** - 测试方法论
- **API_TEST_RESULTS_ANALYSIS.md** - 性能分析

### 链接

- 📦 **npm**: https://www.npmjs.com/package/openclaw-research-analyst
- 🐙 **GitHub**: https://github.com/ZhenRobotics/openclaw-research-analyst
- 📋 **版本说明**: https://github.com/ZhenRobotics/openclaw-research-analyst/releases/tag/v1.3.0
- 🔖 **提交**: e90cc7f

---

**⚠️ 注意**: AI 模式需要安装额外依赖（`requirements-ai.txt`），关键词模式无需额外依赖即可使用。
