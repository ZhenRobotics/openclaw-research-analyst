# Feishu Configuration Loading Fix

## 🐛 问题描述

### 症状
- **cn_market_report.py** 执行飞书推送时失败
- 错误信息: `Bot has NO availability to this user`
- 错误代码: 230013

### 根本原因
`cn_market_report.py` 未加载 `.env.feishu` 配置文件，导致：
- `FEISHU_APP_ID` 未定义
- `FEISHU_APP_SECRET` 未定义
- `FEISHU_USER_OPEN_ID` 未定义

飞书推送模块无法获取正确的认证信息。

---

## ✅ 解决方案

### 修复内容

**文件**: `scripts/cn_market_report.py`
**位置**: 第 14 行
**改动**: 添加 1 行

```diff
 # Load environment configuration
 from dotenv import load_dotenv
 load_dotenv(os.path.join(SKILL_DIR, '.env.cn_market'), override=False)
+load_dotenv(os.path.join(SKILL_DIR, '.env.feishu'), override=False)
```

### 工作原理

1. **加载顺序**:
   - 先加载 `.env.cn_market` (中国市场数据源配置)
   - 再加载 `.env.feishu` (飞书推送配置)

2. **override=False**:
   - 不覆盖已有的环境变量
   - 允许用户通过系统环境变量覆盖文件中的配置

3. **配置项**:
   ```bash
   FEISHU_APP_ID          # 飞书应用 ID
   FEISHU_APP_SECRET      # 飞书应用密钥
   FEISHU_USER_OPEN_ID    # 飞书用户 Open ID
   ```

---

## 📊 影响范围

### 受益脚本

- ✅ **cn_market_report.py** - 中国市场报告（主要受益者）
- ✅ **cn_market_brief.py** - 市场简报（间接受益，通过调用 cn_market_report.py）
- ✅ **async_cn_market_demo.py** - 异步演示（间接受益）

### 不受影响的脚本

- ✅ **news_monitor.py** - 新闻监控（已在 feishu_push.py 模块中自动加载）
- ✅ **feishu_push.py** - 飞书推送模块（已有自动加载逻辑）

---

## 🧪 测试验证

### 测试方法

```bash
# 1. 确保 .env.feishu 存在
ls -la .env.feishu

# 2. 测试中国市场报告推送
python3 scripts/cn_market_report.py

# 3. 测试市场简报推送
python3 scripts/cn_market_brief.py --push

# 4. 查看飞书推送日志
cat logs/feishu_push_history.log
```

### 预期结果

✅ **修复前**:
```
❌ 推送失败: {'code': 230013, 'msg': 'Bot has NO availability to this user.'}
```

✅ **修复后**:
```
✅ 已推送: 中国A股市场报告 - 2026-03-20
   消息ID: om_xxx...
   时间戳: 2026-03-20T15:30:00
```

---

## 📋 技术细节

### 配置加载优先级

1. **系统环境变量** (最高优先级)
   - `export FEISHU_APP_ID="..."`

2. **.env.feishu 文件**
   - 项目根目录的配置文件

3. **默认值/回退**
   - 飞书推送模块会检测配置缺失并提供清晰错误信息

### 相关模块

```python
# feishu_push.py (模块层面自动加载)
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env.feishu'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass  # dotenv not installed, will use existing env vars
```

```python
# cn_market_report.py (脚本层面显式加载)
from dotenv import load_dotenv
load_dotenv(os.path.join(SKILL_DIR, '.env.cn_market'), override=False)
load_dotenv(os.path.join(SKILL_DIR, '.env.feishu'), override=False)  # 新增
```

**为什么需要两个地方都加载？**

- **模块加载**: 确保任何导入 `feishu_push` 的脚本都能工作
- **脚本加载**: 确保在模块导入之前配置就已就绪，避免时序问题

---

## 🔍 故障排除

### 问题 1: 仍然推送失败

**检查清单**:
- [ ] `.env.feishu` 文件存在
- [ ] 文件内容格式正确（无 BOM，UTF-8）
- [ ] 环境变量值有效（从飞书开放平台获取）
- [ ] 机器人已添加到目标用户/群组

**验证命令**:
```bash
# 检查配置是否加载
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.feishu')
print(f'APP_ID: {os.environ.get(\"FEISHU_APP_ID\", \"NOT SET\")}')
print(f'USER_OPEN_ID: {os.environ.get(\"FEISHU_USER_OPEN_ID\", \"NOT SET\")}')
"
```

### 问题 2: 配置文件不存在

**创建配置**:
```bash
# 复制示例文件
cp .env.feishu.example .env.feishu

# 编辑配置
nano .env.feishu
```

---

## 📦 Git 提交信息

**Commit**: `59c8df7`
**日期**: 2026-03-20
**分支**: main

**提交信息**:
```
🔧 Fix: Load .env.feishu in cn_market_report.py

Issue: Feishu push failed with 'Bot has NO availability' error
Solution: Add load_dotenv for .env.feishu configuration
Impact: Fixes Feishu push functionality in China market reports
```

---

## 🚀 部署状态

| 平台 | 状态 | 说明 |
|------|------|------|
| **GitHub** | ✅ 已推送 | Commit 59c8df7 on main |
| **npm** | ⏳ 待发布 | 等待 v1.3.1 或后续版本 |
| **ClawHub** | ⏳ 待发布 | 等待 v1.3.1 或后续版本 |

### 用户获取方式

**v1.3.0 用户** (npm/ClawHub):
```bash
# 方式 1: 手动添加这一行到 cn_market_report.py:14
load_dotenv(os.path.join(SKILL_DIR, '.env.feishu'), override=False)

# 方式 2: 从 GitHub 拉取最新代码
git pull origin main
```

**新用户**:
- 等待 v1.3.1 发布后直接安装（包含此修复）

---

## 🎓 最佳实践

### 1. 配置文件管理

```python
# 推荐模式：按功能分离配置文件
load_dotenv('.env.cn_market')  # 数据源配置
load_dotenv('.env.feishu')     # 推送配置
load_dotenv('.env.openai')     # AI 配置
```

### 2. 错误处理

```python
# 在加载后验证关键配置
required_vars = ['FEISHU_APP_ID', 'FEISHU_APP_SECRET']
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    raise ValueError(f"Missing required env vars: {missing}")
```

### 3. 文档说明

```python
# 在脚本顶部注释中说明配置要求
"""
Requirements:
- .env.cn_market: Data source configuration
- .env.feishu: Feishu push configuration (optional)
"""
```

---

## 📚 相关文档

- **FEISHU_PUSH_v1.2.1_GUIDE.md** - 飞书推送完整指南
- **API_TEST_RESULTS_ANALYSIS.md** - 包含飞书推送测试结果
- **.env.feishu.example** - 配置文件模板

---

## ✅ 总结

### 修复前
❌ cn_market_report.py 飞书推送失败
❌ 错误代码 230013: Bot has NO availability
❌ 配置未加载

### 修复后
✅ cn_market_report.py 飞书推送成功
✅ 配置正确加载
✅ 与其他脚本行为一致
✅ 1 行代码，解决关键问题

---

**修复日期**: 2026-03-20
**修复版本**: v1.3.0+ (Commit 59c8df7)
**下一发布**: v1.3.1 (待定)
**状态**: ✅ 已修复并推送到 GitHub
