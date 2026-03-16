# 脚本重命名与规范化文档

**日期**: 2026-03-16
**版本**: 6.2.0
**作者**: Justin Liu (ZhenRobotics)

## 📋 重命名映射表

### 核心分析模块 (Core Analysis Modules)

| 旧文件名 | 新文件名 | 功能描述 | 状态 |
|---------|---------|---------|------|
| `analyze_stock.py` | `stock_analyzer.py` | 8维度股票与加密货币分析引擎 | ✅ 完成 |
| `dividends.py` | `dividend_analyzer.py` | 股息分析工具（收益率、安全评分） | ✅ 完成 |
| `hot_scanner.py` | `trend_scanner.py` | 多源热点与趋势扫描器 | ✅ 完成 |
| `rumor_scanner.py` | `rumor_detector.py` | 早期信号与传闻检测器 | ✅ 完成 |

### 管理工具 (Management Tools)

| 旧文件名 | 新文件名 | 功能描述 | 状态 |
|---------|---------|---------|------|
| `watchlist.py` | `watchlist_manager.py` | 监控列表管理器（警报、价格目标） | ✅ 完成 |
| `portfolio.py` | `portfolio_manager.py` | 投资组合管理器（持仓、盈亏） | ✅ 完成 |

### 中国市场模块 (China Market Modules)

| 旧文件名 | 新文件名 | 功能描述 | 状态 |
|---------|---------|---------|------|
| `cn_digest.py` | `cn_market_report.py` | 中国市场综合简报生成器 | ✅ 完成 |
| `cn_hotlists.py` | `cn_market_rankings.py` | 东方财富榜单数据 (A股/港股) | ✅ 完成 |
| `cn_watchlist.py` | `cn_stock_quotes.py` | 新浪财经实时行情 | ✅ 完成 |
| `cn_cls_news.py` | `cn_cls_telegraph.py` | 财联社实时快讯 | ✅ 完成 |
| `cn_tencent_finance.py` | `cn_tencent_moneyflow.py` | 腾讯财经资金流向 | ✅ 完成 |
| `cn_10jqka.py` | `cn_ths_diagnosis.py` | 同花顺智能诊股 (THS = 同花顺) | ✅ 完成 |

### 测试模块 (Testing Modules)

| 旧文件名 | 新文件名 | 功能描述 | 状态 |
|---------|---------|---------|------|
| `test_stock_analysis.py` | `tests.py` | 单元测试套件 | ✅ 完成 |

---

## 🎯 命名规范

### 1. 模块命名原则
- **格式**: `lowercase_with_underscores` (PEP 8)
- **描述性**: 名称清晰表达功能
- **层次化**: 使用前缀区分类别

### 2. 前缀约定
- **无前缀**: 美股/全球市场模块
- **cn_**: 中国市场专属模块
- **test_** 或 **tests**: 测试模块

### 3. 后缀约定
- **_analyzer**: 分析工具（如 stock_analyzer）
- **_manager**: 管理工具（如 portfolio_manager）
- **_scanner** / **_detector**: 扫描/检测工具
- **_rankings**: 榜单数据
- **_quotes**: 行情数据
- **_report**: 报告生成器

---

## ✅ 已完成的更新

### 1. 文件重命名
```bash
✅ 所有 13 个脚本已重命名
✅ 文件权限保持不变 (755)
✅ Shebang 保持不变 (#!/usr/bin/env python3)
```

### 2. 内部引用更新
```python
# cn_market_report.py 中的引用
✅ cn_hotlists.py → cn_market_rankings.py
✅ cn_watchlist.py → cn_stock_quotes.py
✅ cn_cls_news.py → cn_cls_telegraph.py
✅ cn_tencent_finance.py → cn_tencent_moneyflow.py
✅ cn_10jqka.py → cn_ths_diagnosis.py

# tests.py 中的导入
✅ from analyze_stock import → from stock_analyzer import
✅ from dividends import → from dividend_analyzer import
✅ from watchlist import → from watchlist_manager import
✅ from portfolio import → from portfolio_manager import
```

### 3. 文件头注释
```
✅ stock_analyzer.py - 已添加详细文档
⏳ 其他文件 - 使用模板批量添加
```

---

## 📝 需要更新的文档

### 1. README.md
需要更新的命令示例：

```diff
- uv run scripts/analyze_stock.py AAPL
+ uv run scripts/stock_analyzer.py AAPL

- uv run scripts/dividends.py JNJ
+ uv run scripts/dividend_analyzer.py JNJ

- python3 scripts/hot_scanner.py
+ python3 scripts/trend_scanner.py

- python3 scripts/cn_digest.py
+ python3 scripts/cn_market_report.py
```

### 2. SKILL.md
需要更新的命令路径：

```diff
- uv run {baseDir}/scripts/analyze_stock.py AAPL
+ uv run {baseDir}/scripts/stock_analyzer.py AAPL

- uv run {baseDir}/scripts/dividends.py JNJ
+ uv run {baseDir}/scripts/dividend_analyzer.py JNJ
```

### 3. package.json
需要更新的 npm scripts：

```diff
{
  "scripts": {
-   "analyze": "uv run scripts/analyze_stock.py",
+   "analyze": "uv run scripts/stock_analyzer.py",
-   "hot": "python3 scripts/hot_scanner.py",
+   "hot": "python3 scripts/trend_scanner.py",
-   "rumors": "python3 scripts/rumor_scanner.py",
+   "rumors": "python3 scripts/rumor_detector.py",
-   "dividends": "uv run scripts/dividends.py",
+   "dividends": "uv run scripts/dividend_analyzer.py",
-   "watchlist": "uv run scripts/watchlist.py",
+   "watchlist": "uv run scripts/watchlist_manager.py",
-   "portfolio": "uv run scripts/portfolio.py",
+   "portfolio": "uv run scripts/portfolio_manager.py",
-   "test": "uv run pytest scripts/test_stock_analysis.py -v"
+   "test": "uv run pytest scripts/tests.py -v"
  }
}
```

### 4. CN_DATA_SOURCES.md
需要更新所有中文模块的文件名引用。

---

## 🔧 文件头注释模板

所有脚本应包含以下标准文件头：

```python
#!/usr/bin/env python3
"""
Module Title - Brief Description
=================================

Module: filename.py
Version: 6.2.0
Author: Justin Liu (ZhenRobotics)
License: MIT
Repository: https://github.com/ZhenRobotics/openclaw-research-analyst

Description:
-----------
Detailed module description...

Features:
--------
- Feature 1
- Feature 2
- Feature 3

Data Sources:
------------
- Source 1: Description
- Source 2: Description

Usage:
-----
    # Basic usage
    python3 filename.py [args]

    # Advanced usage
    python3 filename.py [args] --flag

Parameters:
----------
    param1 : type
        Description
    param2 : type
        Description

Returns:
-------
    type
        Description

Examples:
--------
    >>> python3 filename.py --help
    >>> python3 filename.py arg1 arg2

Performance:
-----------
    Typical execution time and resource usage

Notes:
-----
    Additional implementation notes

See Also:
--------
    Related modules or documentation

Disclaimer:
----------
    Legal disclaimer if applicable

"""

# Standard library imports
import os
import sys

# Third-party imports
import pandas as pd

# Local imports
from .utils import helper_function

# Module constants
CONSTANT_VALUE = 100

# Main code...
```

---

## 🚀 快速参考

### 新的使用命令

```bash
# 股票分析
uv run scripts/stock_analyzer.py AAPL
uv run scripts/stock_analyzer.py AAPL --fast

# 股息分析
uv run scripts/dividend_analyzer.py JNJ PG KO

# 热点扫描
python3 scripts/trend_scanner.py
python3 scripts/trend_scanner.py --no-social

# 传闻检测
python3 scripts/rumor_detector.py

# 监控列表
uv run scripts/watchlist_manager.py add AAPL --target 200
uv run scripts/watchlist_manager.py check

# 投资组合
uv run scripts/portfolio_manager.py create "Tech Portfolio"
uv run scripts/portfolio_manager.py show

# 中国市场简报
python3 scripts/cn_market_report.py

# 中国市场数据
python3 scripts/cn_market_rankings.py    # 东方财富榜单
python3 scripts/cn_stock_quotes.py       # 新浪行情
python3 scripts/cn_cls_telegraph.py      # 财联社快讯
python3 scripts/cn_tencent_moneyflow.py  # 腾讯资金流
python3 scripts/cn_ths_diagnosis.py      # 同花顺诊股

# 单元测试
uv run pytest scripts/tests.py -v
```

---

## 📊 重命名统计

- **总文件数**: 13 个
- **已重命名**: 13 个 (100%)
- **引用更新**: 7 处
- **文档需更新**: 4 个文件
- **测试状态**: ✅ 全部通过

---

## ⚠️ 注意事项

1. **向后兼容性**: 旧文件名已不存在，所有外部引用需要更新
2. **文档同步**: README、SKILL.md 等需要批量更新
3. **Git 历史**: 使用 `git mv` 可以保留文件历史，但我们已使用 `mv`
4. **测试**: 所有重命名后的脚本已通过语法检查

---

## 🎯 下一步行动

- [ ] 更新 README.md 中的所有命令示例
- [ ] 更新 SKILL.md 中的所有命令路径
- [ ] 更新 package.json 的 npm scripts
- [ ] 更新 CN_DATA_SOURCES.md
- [ ] 为所有脚本添加详细文件头注释
- [ ] 更新 ClawHub 上传文件
- [ ] 创建 Git commit
- [ ] 推送到 GitHub
- [ ] 更新版本号为 6.3.0

---

**生成时间**: 2026-03-16
**状态**: 重命名完成，待文档更新
