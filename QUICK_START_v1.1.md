# 🚀 快速开始 - 异步优化 v1.1.0

## 一键测试

```bash
# 测试异步模式（推荐）
python3 scripts/cn_market_report.py --async

# 测试同步模式（回退）
python3 scripts/cn_market_report.py --sync

# 使用默认配置
python3 scripts/cn_market_report.py
```

## 性能对比

| 模式 | 时间 | 提升 |
|------|------|------|
| 同步 (v1.0.1) | 8.8s | 基准 |
| 异步 (v1.1.0) | 1.4s | **-84%** 🚀 |

## 配置

编辑 `.env.cn_market`:

```bash
# 启用异步模式
CN_MARKET_USE_ASYNC=true

# 禁用异步模式（回退到 v1.0.1）
CN_MARKET_USE_ASYNC=false
```

## 常见问题

### Q: 如何强制使用同步模式？
```bash
python3 scripts/cn_market_report.py --sync
```

### Q: 如何验证异步模式工作？
查看输出的第一行：
- `🚀 Using async mode (v1.1.0)` = 异步
- `⏱️  Using sync mode (v1.0.1)` = 同步

### Q: 异步模式失败怎么办？
系统会自动降级到同步模式，无需人工干预。

## 下一步

阅读完整文档：
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - 实施报告
- [ARCHITECTURE_OPTIMIZATION_PLAN.md](ARCHITECTURE_OPTIMIZATION_PLAN.md) - 架构设计
- [MIGRATION_GUIDE_v1.1.md](MIGRATION_GUIDE_v1.1.md) - 迁移指南
