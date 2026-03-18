# ClawHub 发布操作步骤

**版本**: v1.1.0
**预计时间**: 2-3 分钟

---

## ⚠️ 重要提醒

根据 ClawHub 安全机制，**必须在网页上手动操作**，无法通过 CLI 自动化。

---

## 📋 发布步骤（8 步完成）

### 步骤 1: 访问 ClawHub

打开浏览器访问：
```
https://clawhub.ai/ZhenRobotics/research-analyst
```

### 步骤 2: 登录

使用 ClawHub 账号登录

### 步骤 3: 进入编辑模式

点击页面右上角的 **"Edit"** 按钮

### 步骤 4: 更新版本号

在版本号字段中，将版本号更新为：
```
1.1.0
```

### 步骤 5: 更新标签（可选）

Tag 保持为 `latest` 或根据需要更新

### 步骤 6: 上传文件夹

**方式 A: 拖拽上传**（推荐）
1. 打开文件管理器
2. 导航到：`/home/justin/openclaw-research-analyst/clawhub-upload`
3. 拖拽整个 `clawhub-upload` 文件夹到 "Drop a folder" 区域

**方式 B: 选择文件夹**
1. 点击 "Choose folder"
2. 选择 `/home/justin/openclaw-research-analyst/clawhub-upload` 文件夹

**验证**: 确保显示 "2 files · XX KB"（skill.md + readme.md）

### 步骤 7: 填写更新说明

将以下内容复制粘贴到更新说明框：

---

**📋 复制以下内容 ↓**

```markdown
## 🎉 v1.1.0 Major Update

### 📱 飞书推送集成 (Feishu Push Integration)
- ✅ 飞书私聊推送 + 群 Webhook 支持
- ✅ 精简简报格式（≤120字）
- ✅ 系统 cron 定时推送（每 10 分钟）
- ✅ 配置向导工具

**快速开始**:
\`\`\`bash
python3 scripts/feishu_setup.py --interactive
python3 scripts/cn_market_report.py --async --push
\`\`\`

### 🚀 异步架构优化 (Async Optimization)
- **性能提升**: 70-90% faster
- **并行获取**: 5 个数据源并发
- **报告生成**: 2.5s → 700ms

**使用方法**:
\`\`\`bash
python3 scripts/cn_market_report.py --async
\`\`\`

### 📚 文档
- [FEISHU_QUICKSTART.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/FEISHU_QUICKSTART.md) - 5 分钟快速开始
- [IMPLEMENTATION_COMPLETE.md](https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/IMPLEMENTATION_COMPLETE.md) - 技术细节

### 📦 安装
\`\`\`bash
npm install -g openclaw-research-analyst
# 或
clawhub install research-analyst
\`\`\`

**完整发布说明**: https://github.com/ZhenRobotics/openclaw-research-analyst/releases/tag/v1.1.0
```

---

### 步骤 8: 发布更新

点击 **"Publish Update"** 或 **"Submit"** 按钮

---

## ✅ 验证发布

### 1. 搜索验证

```bash
clawhub search research-analyst
```

应该显示版本 `1.1.0`

### 2. 查看详情

```bash
clawhub inspect research-analyst
```

检查版本号和更新内容

### 3. 测试安装

```bash
clawhub update research-analyst
# 或
clawhub install research-analyst --force
```

---

## 📁 文件清单

确保以下文件已准备好：

- ✅ `clawhub-upload/skill.md` - 已更新版本号（1.1.0）和 verified_commit（471e311）
- ✅ `clawhub-upload/readme.md` - 已更新版本号（1.1.0）和功能列表
- ✅ `CLAWHUB_UPDATE_v1.1.0.md` - 更新说明（供参考）

---

## 🔍 常见问题

### Q1: 为什么不能用 CLI 发布？

**A**: ClawHub 要求用户在网页上**亲自勾选同意 MIT-0 条款**，这是安全机制，防止未经授权的自动发布。

### Q2: 上传文件夹失败？

**A**: 确保：
1. 文件夹包含 skill.md 和 readme.md
2. 文件大小合理（< 10 MB）
3. 文件格式正确（UTF-8, 小写文件名）

### Q3: 版本验证失败？

**A**: 确保：
1. skill.md 中的 `version: 1.1.0`
2. verified_commit 是最新的（471e311）
3. readme.md 中的版本号匹配

---

## 📞 技术支持

**项目主页**: https://github.com/ZhenRobotics/openclaw-research-analyst

**问题反馈**: https://github.com/ZhenRobotics/openclaw-research-analyst/issues

**ClawHub 文档**: https://clawhub.ai/docs

---

**准备时间**: 2026-03-18
**版本**: v1.1.0
**Commit**: 471e311
**状态**: ✅ 准备就绪，等待手动发布
