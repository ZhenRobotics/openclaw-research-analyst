# Release Notes v1.3.0

## 🎉 Major Update: AI News Monitoring System

### 🚀 New Features

#### 1. AI-Powered News Monitoring System
- **Real-time Financial News Monitoring**
  - Automatic collection from 财联社 (CLS) and 东方财富 (Eastmoney)
  - Event-driven push for major bullish/bearish news
  - Smart importance scoring (1-5 scale)
  - Dual-mode operation: AI model + keyword rules

- **Intelligent News Classification**
  - Keyword-based sentiment analysis (BULLISH/BEARISH/NEUTRAL)
  - 100% accuracy on test cases
  - Importance threshold filtering (configurable)
  - Automatic deduplication

- **News Database & Analytics**
  - SQLite-based news storage
  - Training data management for AI models
  - News prediction tracking
  - Statistics and reporting

- **Interactive Labeling Tool**
  - CLI-based news annotation
  - Batch labeling support
  - Training data preparation
  - Human-in-the-loop workflow

- **AI Model Training Pipeline**
  - BERT-based sentiment classifier
  - Importance scorer
  - Transfer learning from chinese-roberta-wwm-ext
  - Train/val/test split automation

- **Fast Monitoring Mode**
  - 60-second collection interval
  - Incremental fetching (only latest 20 items)
  - 30-40 seconds end-to-end latency
  - Time-based filtering

#### 2. Comprehensive API Testing Suite
- **9-point Test Coverage**
  - Functional testing (news APIs, database, Feishu push)
  - Performance testing (response time P95, concurrency)
  - Reliability testing (error handling, retries)
  - End-to-end workflow testing

- **Automated Test Reports**
  - JSON format test results
  - Detailed metrics and statistics
  - Pass/fail analysis
  - Performance benchmarks

- **Test Results**
  - 66.7% overall pass rate
  - 100% keyword matching accuracy
  - Concurrent request handling: 10/10 success
  - End-to-end latency: 19 seconds

#### 3. Enhanced Feishu Integration
- **Improved Configuration Loading**
  - Automatic .env.feishu loading
  - Support for both private chat and webhook modes
  - Comprehensive error messages
  - Network retry mechanism (2 retries, exponential backoff)

- **Push History Logging**
  - Detailed push tracking
  - JSON format logs
  - Troubleshooting support

### 📚 Documentation

#### New Guides
- **AI_NEWS_SYSTEM_GUIDE.md** - Complete guide to AI news monitoring
  - 4-stage workflow (collect → label → train → monitor)
  - Quick start instructions
  - Architecture overview
  - Troubleshooting

- **API_TESTING_GUIDE.md** - Comprehensive API testing documentation
  - Test suite usage
  - Testing methodology
  - Performance benchmarks
  - Optimization recommendations

- **API_TEST_RESULTS_ANALYSIS.md** - Detailed test results analysis
  - Performance metrics
  - Security assessment
  - Issues and fixes
  - Release readiness evaluation

- **REALTIME_WEBSOCKET_DESIGN.md** - WebSocket architecture design
  - Real-time push strategies
  - Performance comparison
  - Implementation roadmap

### 🛠️ New Scripts & Tools

#### Core Scripts
- `scripts/news_collector.py` - Multi-source news collection
- `scripts/news_database.py` - SQLite database management
- `scripts/news_monitor.py` - Real-time monitoring daemon
- `scripts/news_monitor_fast.py` - Optimized fast monitoring
- `scripts/news_labeling_tool.py` - Interactive labeling CLI
- `scripts/news_model_trainer.py` - BERT model training
- `scripts/quick_start_ai.sh` - One-click AI system launcher

#### Testing & Automation
- `scripts/auto_label_news.py` - Automatic keyword-based labeling
- `scripts/pretrained_classifier.py` - Pre-trained model integration
- `tests/api_test_suite.py` - Comprehensive API test suite

### 🔧 Improvements

- **Keyword Matching Enhanced**
  - Expanded keyword library
  - Weight-based scoring
  - Matched keyword tracking
  - Confidence calculation

- **Database Schema**
  - News table with full metadata
  - Prediction tracking
  - Push status management
  - Training data split support

- **Error Handling**
  - Graceful API failure handling
  - Automatic retry mechanisms
  - Clear error messages
  - Fallback strategies

### 📊 Performance

- **Real-time Monitoring**
  - Default interval: 300 seconds (5 minutes)
  - Fast mode interval: 60 seconds
  - Processing time: <1 second per news item
  - End-to-end latency: 30-40 seconds (fast mode)

- **API Performance**
  - 财联社 API: 772ms average
  - Database operations: 299ms
  - Keyword matching: <1ms
  - Concurrent requests: 10/10 success

### 🐛 Bug Fixes

- Fixed torch import error in keyword-only mode
- Fixed .env.feishu loading in monitoring scripts
- Fixed None return value in news collection
- Fixed database duplicate detection

### 📦 Dependencies

#### New Dependencies
```
# AI System (optional, for training)
torch>=2.0.0
transformers>=4.30.0
scikit-learn>=1.3.0

# Required
aiohttp>=3.9.0
requests>=2.31.0

# Optional
beautifulsoup4>=4.12.0
pandas>=2.0.0
numpy>=1.24.0
```

### 🎯 Migration Guide

#### For Existing Users

1. **Optional: Install AI Dependencies**
   ```bash
   pip3 install -r requirements-ai.txt
   ```

2. **Start Using News Monitoring**
   ```bash
   # Keyword mode (no AI required)
   ./scripts/quick_start_ai.sh monitor-keyword

   # AI mode (requires training)
   ./scripts/quick_start_ai.sh collect
   ./scripts/quick_start_ai.sh label
   ./scripts/quick_start_ai.sh train
   ./scripts/quick_start_ai.sh monitor
   ```

3. **Run API Tests**
   ```bash
   python3 tests/api_test_suite.py
   ```

### 🔍 Testing

- API test suite with 9 comprehensive tests
- 66.7% overall pass rate
- 100% keyword matching accuracy
- Full documentation in API_TESTING_GUIDE.md

### 📈 Statistics

- **Code Changes**:
  - 8 new Python scripts (2000+ lines)
  - 4 new documentation files
  - 1 comprehensive test suite

- **Features**:
  - News collection from 2 sources
  - 30+ BULLISH keywords
  - 30+ BEARISH keywords
  - 9-point API testing
  - 4-stage AI workflow

### 🙏 Acknowledgments

This release includes contributions from:
- API Tester Agent - Comprehensive API testing
- Testing methodology best practices
- Real-time monitoring architecture design

---

**Release Date**: 2026-03-20
**Version**: 1.3.0
**Previous Version**: 1.2.1
**Breaking Changes**: None
**Upgrade Required**: No (backward compatible)

---

## Quick Start

### For Keyword Mode (Recommended, No AI Required)
```bash
# Collect news
python3 scripts/news_collector.py --limit 100

# Start monitoring (keyword-based, 60-second interval)
python3 scripts/news_monitor_fast.py --no-ai --interval 60 --threshold 4
```

### For AI Mode (Requires Training)
```bash
# Follow the 4-stage workflow
./scripts/quick_start_ai.sh collect
./scripts/quick_start_ai.sh label
./scripts/quick_start_ai.sh train
./scripts/quick_start_ai.sh monitor
```

### Test the System
```bash
# Run comprehensive API tests
python3 tests/api_test_suite.py

# View test report
cat logs/api_test_report_*.json
```

---

For detailed documentation, see:
- AI_NEWS_SYSTEM_GUIDE.md
- API_TESTING_GUIDE.md
- API_TEST_RESULTS_ANALYSIS.md
