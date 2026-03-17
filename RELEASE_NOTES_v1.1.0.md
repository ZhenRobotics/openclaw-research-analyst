# Release Notes v1.1.0

**发布日期**: 2026-03-18
**版本**: v1.1.0
**类型**: Minor Release（功能更新）

---

## 🎉 Major Features

### 📱 Feishu Push Integration（飞书推送集成）

完整的飞书推送功能，支持中国市场简报自动推送：

**功能特性**:
- ✅ 飞书私聊推送（需要 App ID, App Secret, Open ID）
- ✅ 飞书群 Webhook 推送
- ✅ 智能推送（自动选择可用方式）
- ✅ 精简简报格式（≤120字）
- ✅ 系统 cron 定时推送（每 10 分钟）

**新增文件**:
- `scripts/feishu_push.py` - 飞书推送模块
- `scripts/feishu_setup.py` - 配置向导工具
- `.env.feishu.example` - 配置模板

**使用方法**:
```bash
# 配置飞书推送
python3 scripts/feishu_setup.py --interactive

# 生成报告并推送
python3 scripts/cn_market_report.py --async --push

# 只查看精简简报
python3 scripts/cn_market_report.py --async --brief
```

**文档**:
- [FEISHU_QUICKSTART.md](FEISHU_QUICKSTART.md) - 5 分钟快速开始
- [FEISHU_PUSH_GUIDE.md](FEISHU_PUSH_GUIDE.md) - 完整配置指南
- [FEISHU_PUSH_TEST_REPORT.md](FEISHU_PUSH_TEST_REPORT.md) - 测试报告

---

### 🚀 Async Architecture Optimization（异步架构优化）

**性能提升**: 70-90% faster report generation

**技术实现**:
- 使用 `aiohttp` 实现并行数据获取
- 5 个数据源并发请求（东方财富/新浪/财联社/腾讯/同花顺）
- 智能错误处理和重试机制
- 缓存支持（memory/redis）

**性能对比**:
| 模式 | 总耗时 | 成功率 | 用途 |
|------|--------|--------|------|
| 同步 | ~2.5s | 100% | 传统模式 |
| 异步 | ~700ms | 100% | **推荐** |

**使用方法**:
```bash
# 异步模式（推荐）
python3 scripts/cn_market_report.py --async

# 同步模式（传统）
python3 scripts/cn_market_report.py --sync

# 默认模式（从环境变量读取）
python3 scripts/cn_market_report.py
```

**新增文件**:
- `scripts/async_cn_market_demo.py` - 异步演示脚本
- `scripts/async_architecture_core.py` - 异步核心模块
- `.env.cn_market` - 异步配置文件

**文档**:
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - 实现细节
- [ASYNC_OPTIMIZATION_SUMMARY.md](ASYNC_OPTIMIZATION_SUMMARY.md) - 优化总结

---

## 🔧 Improvements

### CLI 参数增强
- `--push` - 生成报告后推送到飞书
- `--brief` - 输出精简简报（≤120字）
- `--async` / `--sync` - 明确指定模式

### 环境变量配置
- `.env.feishu` - 飞书推送配置
- `.env.cn_market` - 中国市场配置
- 配置文件优先级：CLI 参数 > 环境变量 > 默认值

### 文档完善
- 新增 13 个文档文件
- 中英文双语支持
- 完整的故障排查指南

---

## 📊 统计数据

**新增代码**:
- Python: ~600 lines
- Bash: ~200 lines
- Markdown: ~3000 lines

**新增文件**: 16 个
- Scripts: 3
- Configs: 3
- Docs: 10

**测试覆盖**:
- ✅ 飞书 Token 获取
- ✅ 飞书 API 调用
- ✅ 异步数据获取
- ✅ 精简简报生成
- ✅ 错误处理机制

---

## 📚 文档索引

### 快速开始
- [FEISHU_QUICKSTART.md](FEISHU_QUICKSTART.md) - 飞书推送 5 分钟配置
- [QUICK_START_v1.1.md](QUICK_START_v1.1.md) - v1.1.0 快速开始

### 详细指南
- [FEISHU_PUSH_GUIDE.md](FEISHU_PUSH_GUIDE.md) - 飞书推送完整指南
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - 异步架构实现

### 技术文档
- [ASYNC_OPTIMIZATION_SUMMARY.md](ASYNC_OPTIMIZATION_SUMMARY.md) - 异步优化总结
- [ARCHITECTURE_OPTIMIZATION_PLAN.md](ARCHITECTURE_OPTIMIZATION_PLAN.md) - 架构优化计划
- [FEISHU_PUSH_TEST_REPORT.md](FEISHU_PUSH_TEST_REPORT.md) - 飞书推送测试报告

### 参考资料
- [FEISHU_QUICK_REFERENCE.md](FEISHU_QUICK_REFERENCE.md) - 飞书推送快速参考
- [API_FIXES_COOKBOOK.md](API_FIXES_COOKBOOK.md) - API 修复手册

---

## 🔄 Migration Guide

### 从 v1.0.1 升级

**1. 更新代码**:
```bash
# npm
npm update -g openclaw-research-analyst

# GitHub
git pull origin main

# ClawHub
clawhub install research-analyst
```

**2. 配置飞书推送（可选）**:
```bash
# 复制配置模板
cp .env.feishu.example .env.feishu

# 编辑配置
nano .env.feishu

# 填入你的凭证
export FEISHU_APP_ID="cli_xxxxx"
export FEISHU_APP_SECRET="xxxxx"
export FEISHU_USER_OPEN_ID="ou_xxxxx"
```

**3. 使用新功能**:
```bash
# 异步模式
python3 scripts/cn_market_report.py --async

# 推送到飞书
source .env.feishu
python3 scripts/cn_market_report.py --async --push
```

---

## ⚠️ Breaking Changes

**无破坏性变更**

v1.1.0 完全向后兼容 v1.0.1，所有现有功能保持不变。

---

## 🐛 Bug Fixes

- 修复中国市场数据源网络超时问题
- 改进错误处理和日志输出
- 优化数据缓存机制

---

## 🙏 Acknowledgments

感谢以下贡献者和测试者：
- **Feishu Integration Developer** (Agent) - 飞书推送功能测试
- **Backend Architect** (Agent) - 异步架构设计和优化

---

## 📞 Support

**项目主页**: https://github.com/ZhenRobotics/openclaw-research-analyst

**问题反馈**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues

**ClawHub**: https://clawhub.ai/ZhenRobotics/research-analyst

---

**完整更新日志**: 查看 [CHANGELOG.md](CHANGELOG.md)（如果存在）

**发布时间**: 2026-03-18
**发布人**: ZhenRobotics Team
