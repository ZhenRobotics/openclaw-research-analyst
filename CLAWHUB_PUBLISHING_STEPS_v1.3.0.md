# ClawHub 发布步骤 v1.3.0

根据 `~/.claude-shared/clawhub-publish-guide.md` 的指导，ClawHub **必须手动通过网页发布**。

---

## ✅ 发布前检查清单

### 1. 版本一致性检查 ✅

- [x] **package.json**: v1.3.0 ✅
- [x] **clawhub-upload/skill.md**: v1.3.0 ✅
- [x] **clawhub-upload/readme.md**: v1.3.0 ✅
- [x] **verified_commit**: e90cc7f ✅

### 2. Git 状态检查 ✅

- [x] 所有更改已提交 ✅
- [x] Tag v1.3.0 已创建 ✅
- [x] 已推送到 GitHub ✅

### 3. npm 发布检查 ✅

- [x] npm publish 成功 ✅
- [x] 版本: openclaw-research-analyst@1.3.0 ✅

### 4. GitHub Release 检查 ✅

- [x] Release 已创建 ✅
- [x] URL: https://github.com/ZhenRobotics/openclaw-research-analyst/releases/tag/v1.3.0 ✅

---

## 🌐 ClawHub 网页发布流程

### Step 1: 访问 ClawHub

访问：https://clawhub.ai/

### Step 2: 登录

使用您的 ClawHub 账号登录

### Step 3: 进入编辑模式

**方式 A: 通过 skill 页面**
1. 访问 https://clawhub.ai/ZhenRobotics/research-analyst
2. 点击 "Edit" 或 "Update" 按钮

**方式 B: 通过控制面板**
1. 进入您的控制面板
2. 找到 "research-analyst"
3. 点击编辑

### Step 4: 填写更新信息

| 字段 | 值 |
|------|-----|
| **Version** | `1.3.0` |
| **Tag** | `latest` |
| **Display name** | `Research Analyst` |

### Step 5: 上传文件夹

**⚠️ 重要**: 上传整个 `clawhub-upload` 文件夹

**方式 A: 拖拽上传**（推荐）
1. 打开文件管理器
2. 导航到项目目录
3. 找到 `clawhub-upload` 文件夹
4. 拖拽到 ClawHub 的 "Drop a folder" 区域

**方式 B: 选择文件夹**
1. 点击 "Choose folder"
2. 选择 `clawhub-upload` 文件夹

**验证**: 确保显示 "2 files · XX KB"

### Step 6: 填写更新说明

复制 `CLAWHUB_UPDATE_v1.3.0.md` 的内容并粘贴到更新说明框。

**快速复制**:
```bash
cat CLAWHUB_UPDATE_v1.3.0.md
```

### Step 7: 接受 License 条款

**⚠️ 必须勾选**:
```
☑ I have the rights to this skill and agree to publish it under MIT-0.
```

**说明**: 这是 ClawHub 的安全机制，无法通过 CLI 自动化。

### Step 8: 验证检查

确保所有验证都通过：
- ✅ Display name is required
- ✅ Accept the MIT-0 license terms
- ✅ Add at least one file
- ✅ SKILL.md is required

### Step 9: 发布更新

点击 **"Publish Update"** 或 **"Submit"** 按钮

---

## ✅ 发布后验证

### 1. 搜索验证

```bash
clawhub search research-analyst
```

应该能看到 v1.3.0

### 2. 查看详情

```bash
clawhub inspect research-analyst
```

检查版本号和更新内容

### 3. 测试安装

```bash
# 在新目录测试
cd /tmp
clawhub install research-analyst
```

验证可以正常安装

### 4. 检查网页

访问：https://clawhub.ai/ZhenRobotics/research-analyst

确认：
- 版本显示为 v1.3.0
- 更新说明正确显示
- Commit hash 显示为 e90cc7f

---

## 📋 文件清单

### 准备就绪的文件

- ✅ `clawhub-upload/skill.md` (已更新到 v1.3.0)
- ✅ `clawhub-upload/readme.md` (已更新到 v1.3.0)
- ✅ `CLAWHUB_UPDATE_v1.3.0.md` (更新说明)
- ✅ `RELEASE_NOTES_v1.3.0.md` (完整版本说明)

### 文件位置

```
openclaw-research-analyst/
├── clawhub-upload/
│   ├── skill.md          ← 上传此文件夹
│   └── readme.md
├── CLAWHUB_UPDATE_v1.3.0.md        ← 复制内容到更新说明框
├── CLAWHUB_PUBLISHING_STEPS_v1.3.0.md  ← 本文件
└── RELEASE_NOTES_v1.3.0.md
```

---

## 🎯 关键要点

### 为什么必须手动发布？

1. **安全机制**: ClawHub 要求用户在网页上亲自勾选同意 MIT-0 条款
2. **防止滥用**: 这是防止未经授权自动发布的安全措施
3. **设计限制**: CLI 的 `acceptLicenseTerms` 错误是预期行为，不是 bug
4. **必须亲为**: 无法通过代码或 CLI 绕过此限制

### License 说明

- **MIT-0** = MIT No Attribution（无需署名的 MIT）
- 所有 ClawHub skills 都使用 MIT-0
- 自由使用、修改、再分发
- 不需要署名

### 预计时间

- **准备时间**: 5 分钟（文件已就绪）
- **上传时间**: 30 秒
- **填写表单**: 1 分钟
- **总计**: **约 6-7 分钟**

---

## 🚀 现在开始

所有准备工作已完成，现在可以访问 ClawHub 进行手动发布：

👉 **https://clawhub.ai/ZhenRobotics/research-analyst**

点击 **"Edit"** 开始更新！

---

## 📞 遇到问题？

如果遇到问题，参考：
- `~/.claude-shared/clawhub-publish-guide.md` - 完整指南
- `~/.claude-shared/CLAWHUB_PUBLISHING_LESSONS.md` - 经验总结

---

**准备完成时间**: 2026-03-20
**版本**: v1.3.0
**Commit**: e90cc7f
**状态**: ✅ 准备就绪，等待手动发布
