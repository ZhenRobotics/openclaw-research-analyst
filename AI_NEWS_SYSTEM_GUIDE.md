# AI驱动的重大新闻监控系统 - 完整指南

**版本**: v1.0.0
**创建日期**: 2026-03-20
**状态**: 生产就绪

---

## 系统概述

这是一个基于AI的智能新闻监控和推送系统，能够：

1. **自动收集**：从多个来源抓取中国市场新闻
2. **智能分类**：使用BERT模型自动分类情绪和重要性
3. **实时推送**：重大消息立即推送到飞书
4. **持续学习**：支持人工标注和模型迭代优化

---

## 系统架构

```
┌─────────────────┐
│  新闻数据源     │
│ 东方财富/财联社  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  news_collector │  ← 新闻收集器
│  (异步抓取)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite数据库   │  ← news_database
│  (结构化存储)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌────────────┐
│ 标注  │  │  AI模型    │  ← news_model_trainer
│ 工具  │  │  (BERT)    │
└───────┘  └──────┬─────┘
               │
               ▼
         ┌──────────────┐
         │ news_monitor │  ← 实时监控器
         │ (分类+推送)   │
         └──────┬───────┘
                │
                ▼
         ┌──────────────┐
         │  飞书推送     │
         └──────────────┘
```

---

## 快速开始

### 阶段1: 数据收集（第1天）

#### 1.1 安装依赖

```bash
cd /home/justin/openclaw-research-analyst

# 安装Python依赖
pip3 install aiohttp requests sqlite3

# 可选：安装AI依赖（阶段2需要）
# pip3 install torch transformers scikit-learn
```

#### 1.2 收集新闻

```bash
# 首次收集（抓取100条）
python3 scripts/news_collector.py --limit 100

# 查看数据库统计
python3 scripts/news_database.py stats

# 输出示例：
# === 数据库统计 ===
# 总新闻数: 100
# 已标注数: 0
# 来源分布:
#   eastmoney: 50
#   cls: 50
```

#### 1.3 启动持续收集（后台运行）

```bash
# 每5分钟抓取一次（持续运行）
nohup python3 scripts/news_collector.py --continuous --interval 300 > logs/collector.log 2>&1 &

# 查看日志
tail -f logs/collector.log
```

---

### 阶段2: 数据标注（第2-3天）

#### 2.1 人工标注

```bash
# 启动交互式标注工具
python3 scripts/news_labeling_tool.py label --batch-size 20

# 标注界面示例：
# ================================================================================
# 📰 新闻 ID: 1
# 📅 发布时间: 2026-03-20 10:30:00
# 📍 来源: cls
# ================================================================================
#
# 标题: 央行宣布降息25个基点
#
# 内容: 中国人民银行今日宣布下调贷款市场报价利率(LPR)25个基点...
#
# ================================================================================
#
# 情绪分类:
#   1. BULLISH (利好)
#   2. BEARISH (利空)
#   3. NEUTRAL (中性)
#   s. SKIP (跳过)
#   q. QUIT (退出)
#
# 请选择 [1/2/3/s/q]: 1
#
# 重要性评分:
#   5 - 极其重大（全市场影响，必须立即推送）
#   4 - 非常重要（行业级影响，应该推送）
#   3 - 比较重要（公司级影响）
#   2 - 一般重要（常规新闻）
#   1 - 不太重要（参考信息）
#
# 请输入重要性 [1-5]: 5
#
# ✅ 标注完成:
#    情绪: BULLISH
#    重要性: 5/5
#
# ⚠️ 这是重大新闻，将被标记为推送候选！
```

#### 2.2 标注目标

**最低要求**：
- 50-100条标注数据即可开始训练
- 建议标注比例：
  - BULLISH: 30-40%
  - BEARISH: 30-40%
  - NEUTRAL: 20-30%

**理想状态**：
- 200-500条标注数据可获得较好效果
- 确保各类别样本均衡

#### 2.3 查看标注进度

```bash
# 查看统计
python3 scripts/news_labeling_tool.py stats

# 输出示例：
# === 数据库统计 ===
# 总新闻数: 150
# 已标注数: 80
# 标注进度: 53.3%
#
# 情绪分布:
#   BULLISH: 28 (35.0%)
#   BEARISH: 30 (37.5%)
#   NEUTRAL: 22 (27.5%)
#
# 重要性分布:
#   5: 8 (10.0%)
#   4: 15 (18.8%)
#   3: 30 (37.5%)
#   2: 20 (25.0%)
#   1: 7 (8.8%)

# 查看已标注的新闻
python3 scripts/news_labeling_tool.py review --limit 20
```

---

### 阶段3: 模型训练（第4天）

#### 3.1 安装AI依赖

```bash
# 安装PyTorch（CPU版本）
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 安装Transformers
pip3 install transformers scikit-learn

# 如果有GPU，安装CUDA版本：
# pip3 install torch torchvision torchaudio
```

#### 3.2 训练模型

```bash
# 训练情绪分类器
python3 scripts/news_model_trainer.py sentiment --epochs 3 --batch-size 8

# 输出示例：
# 🔧 使用设备: cpu
# 🤖 使用模型: hfl/chinese-roberta-wwm-ext
# ✅ 依赖库检查通过
#
# 📊 准备训练数据...
# ✅ 已标注数据: 80 条
# ✅ 数据集分割:
#    训练集: 56 条
#    验证集: 12 条
#    测试集: 12 条
#
# 🎯 训练情绪分类器...
# 📥 加载预训练模型...
# 🚀 开始训练...
# Epoch 1/3: 100% [...] loss: 0.523
# Epoch 2/3: 100% [...] loss: 0.312
# Epoch 3/3: 100% [...] loss: 0.198
#
# ✅ 模型已保存到: models/sentiment_classifier/final_model
#
# 📊 在测试集上评估...
#
# 分类报告:
#               precision    recall  f1-score   support
#
#      BULLISH       0.88      0.92      0.90         4
#      BEARISH       0.91      0.87      0.89         5
#      NEUTRAL       0.80      0.83      0.81         3
#
#     accuracy                           0.88        12
#    macro avg       0.86      0.87      0.87        12
# weighted avg       0.88      0.88      0.88        12

# 训练重要性评分器（可选）
python3 scripts/news_model_trainer.py importance --epochs 3 --batch-size 8

# 训练两个模型（推荐）
python3 scripts/news_model_trainer.py both --epochs 3 --batch-size 8
```

**训练时间估算**：
- CPU: 约10-30分钟（取决于数据量）
- GPU: 约2-5分钟

**模型文件位置**：
- 情绪分类器: `models/sentiment_classifier/final_model/`
- 重要性评分器: `models/importance_scorer/final_model/`

---

### 阶段4: 实时监控（生产环境）

#### 4.1 配置飞书推送

```bash
# 确保飞书配置正确
source .env.feishu

echo "FEISHU_APP_ID: $FEISHU_APP_ID"
echo "FEISHU_USER_OPEN_ID: $FEISHU_USER_OPEN_ID"

# 测试推送
python3 scripts/feishu_push.py "测试推送" --user
```

#### 4.2 启动AI监控（推荐）

```bash
# 使用AI模型进行监控
# 重要性 >= 4 才推送
# 每5分钟抓取一次
nohup python3 scripts/news_monitor.py \
  --interval 300 \
  --threshold 4 \
  > logs/monitor.log 2>&1 &

# 查看日志
tail -f logs/monitor.log

# 输出示例：
# 🔍 新闻监控器启动
# ================================================================================
# 使用模式: AI模型
# 重要性阈值: >= 4
# 抓取间隔: 300 秒
# 飞书推送: 已配置
# ================================================================================
#
# 📥 加载AI模型...
# ✅ 情绪分类器已加载
# ✅ 重要性评分器已加载
#
# [2026-03-20 10:30:00] 第 1 次抓取...
#   抓取: 30 条
#   新增: 5 条
#   重复: 25 条
#   📱 推送: 1 条重大消息
#
# ✅ 已推送: 央行宣布降息25个基点...
#    情绪: BULLISH, 重要性: 5/5
```

#### 4.3 使用关键词规则（AI不可用时）

```bash
# 不使用AI模型，只用关键词规则
nohup python3 scripts/news_monitor.py \
  --no-ai \
  --interval 300 \
  --threshold 4 \
  > logs/monitor_keyword.log 2>&1 &
```

---

## 推送消息示例

### 利好消息
```
📈 【重大bullish消息】 ⭐⭐⭐⭐⭐

标题: 央行宣布降息25个基点

内容: 中国人民银行今日宣布下调贷款市场报价利率(LPR)25个基点，这是年内第三次降息，旨在刺激经济增长...

来源: cls
重要性: 5/5
置信度: 0.95
时间: 2026-03-20 10:30:15

🤖 AI自动分类
```

### 利空消息
```
📉 【重大bearish消息】 ⭐⭐⭐⭐

标题: 某科技公司被证监会立案调查

内容: 证监会宣布对某科技上市公司涉嫌财务造假立案调查...

来源: eastmoney
重要性: 4/5
置信度: 0.89
时间: 2026-03-20 11:15:20

🤖 AI自动分类
```

---

## 日常维护

### 1. 监控日志

```bash
# 查看收集器日志
tail -f logs/collector.log

# 查看监控器日志
tail -f logs/monitor.log

# 查看飞书推送历史
tail -20 logs/feishu_push_history.log | jq .
```

### 2. 数据库维护

```bash
# 查看统计
python3 scripts/news_database.py stats

# 导出训练数据
python3 scripts/news_database.py export --output data/training/

# 备份数据库
cp data/news.db data/news_backup_$(date +%Y%m%d).db
```

### 3. 持续标注

```bash
# 定期标注新数据（每周）
python3 scripts/news_labeling_tool.py label --batch-size 50

# 重新分割数据集
python3 scripts/news_database.py split

# 重新训练模型
python3 scripts/news_model_trainer.py both --epochs 3
```

---

## 性能优化

### 1. 调整监控参数

```bash
# 更频繁的抓取（每分钟）
python3 scripts/news_monitor.py --interval 60 --threshold 4

# 只推送极重大消息（重要性=5）
python3 scripts/news_monitor.py --interval 300 --threshold 5

# 推送所有重要消息（重要性>=3）
python3 scripts/news_monitor.py --interval 300 --threshold 3
```

### 2. 模型优化

```bash
# 增加训练轮数
python3 scripts/news_model_trainer.py both --epochs 10

# 调整批次大小（GPU可用时）
python3 scripts/news_model_trainer.py both --batch-size 32 --device cuda

# 使用更好的预训练模型
python3 scripts/news_model_trainer.py both \
  --model hfl/chinese-roberta-wwm-ext-large
```

### 3. 添加更多数据源

编辑 `scripts/news_collector.py`，添加新的抓取方法：

```python
async def fetch_custom_source(self, limit=50):
    """自定义数据源"""
    # 实现抓取逻辑
    pass
```

---

## 故障排查

### 问题1: 模型加载失败

**症状**: `模型加载失败: [Errno 2] No such file or directory`

**解决**:
```bash
# 检查模型文件是否存在
ls -la models/sentiment_classifier/final_model/

# 如果不存在，重新训练
python3 scripts/news_model_trainer.py sentiment --epochs 3
```

### 问题2: 推送失败

**症状**: `❌ 飞书推送失败: User Open ID not configured`

**解决**:
```bash
# 检查飞书配置
cat .env.feishu

# 重新配置
python3 scripts/feishu_setup.py
```

### 问题3: 标注数据不足

**症状**: `❌ 标注数据不足: 30 条`

**解决**:
```bash
# 继续标注
python3 scripts/news_labeling_tool.py label --batch-size 50

# 或先使用关键词规则
python3 scripts/news_monitor.py --no-ai --threshold 4
```

---

## 系统架构说明

### 核心组件

1. **news_database.py** (450行)
   - SQLite数据库封装
   - 新闻存储、标注、查询
   - 训练数据分割和导出

2. **news_collector.py** (200行)
   - 异步新闻抓取
   - 支持东方财富、财联社等
   - 持续运行模式

3. **news_labeling_tool.py** (250行)
   - 交互式标注界面
   - 批量标注支持
   - 标注进度追踪

4. **news_model_trainer.py** (400行)
   - BERT模型微调
   - 情绪分类 + 重要性评分
   - 训练/验证/测试分离

5. **news_monitor.py** (350行)
   - 实时监控循环
   - AI分类 + 关键词规则
   - 自动推送重大消息

---

## 下一步改进

### 短期（1-2周）

- [ ] 添加更多数据源（新浪、腾讯等）
- [ ] 优化关键词规则
- [ ] 增加股票代码识别
- [ ] 支持多个飞书群推送

### 中期（1个月）

- [ ] Web管理界面
- [ ] 实时数据可视化
- [ ] 推送消息去重
- [ ] 节假日自动跳过

### 长期（3个月+）

- [ ] 多模型集成（ensemble）
- [ ] 情绪趋势分析
- [ ] 股价影响预测
- [ ] 自动生成交易信号

---

## 技术栈

- **数据库**: SQLite 3
- **异步IO**: asyncio + aiohttp
- **AI框架**: PyTorch + Transformers
- **预训练模型**: chinese-roberta-wwm-ext
- **推送**: 飞书API（v1.2.1 优化版）

---

## 支持与反馈

**项目地址**: https://github.com/ZhenRobotics/openclaw-research-analyst

**问题反馈**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues

**文档**:
- AI_NEWS_SYSTEM_GUIDE.md（本文档）
- FEISHU_PUSH_v1.2.1_GUIDE.md（飞书推送指南）

---

**创建时间**: 2026-03-20
**作者**: Claude Code
**版本**: v1.0.0
