# ClawHub Security Warning - Explanation & Fix

## 🚨 原始警告信息

您收到的安全警告：

```
This skill looks like a real market/research tool, but there are troubling
inconsistencies you should clear up before installing or providing secrets.

Ask the maintainer to explain why AUTH_TOKEN and CT0 are required and exactly
how they are used; demand that FEISHU_* variables (used by scripts) be declared
explicitly if Feishu push is needed.

Do not provide CT0 (a Twitter cookie) or any long-lived auth tokens without
verification — prefer OAuth app tokens or webhook-only delivery.

If you try it, run it in an isolated environment (container/VM) and inspect
the actual package source (the GitHub repo mentioned) before running
installation commands that download or install global npm packages.

If the publisher cannot clearly justify the credential requirements and the
install steps, avoid installing the skill.
```

---

## 🔍 问题分析

这个警告是**完全合理的**！它指出了 skill.md metadata 中的三个安全问题：

### 问题 1: 误导性的 "required" 凭证

**错误的 metadata**：
```json
{
  "requires": {
    "bins": ["python3", "uv"],
    "env": ["AUTH_TOKEN", "CT0"]  // ❌ 标记为"必需"
  }
}
```

**实际情况**：
- `AUTH_TOKEN` 和 `CT0` 是**可选的**，不是必需的
- 仅用于 Twitter/X 传闻扫描功能（`/stock_rumors`）
- 核心功能（股票分析、中国市场报告）**完全不需要任何凭证**

**为什么这是安全问题**：
- 用户可能认为必须提供这些凭证才能使用
- CT0 是浏览器 cookie（session token），比 OAuth token 更危险
- 误导用户提供不必要的敏感信息

---

### 问题 2: 未声明的 Feishu 凭证

**脚本实际使用**：
```python
# scripts/feishu_push.py, scripts/cn_market_report.py
FEISHU_APP_ID         # ❌ 未在 metadata 中声明
FEISHU_APP_SECRET     # ❌ 未在 metadata 中声明
FEISHU_USER_OPEN_ID   # ❌ 未在 metadata 中声明
```

**metadata 中没有声明**：
- Feishu 凭证被脚本使用，但 metadata 中完全没有提及
- 用户无法从 metadata 得知需要这些凭证
- 缺乏透明度

**为什么这是安全问题**：
- 隐藏的凭证要求是安全红旗
- 用户应该在安装前就知道所有凭证要求
- 缺乏透明度降低信任度

---

### 问题 3: 凭证类型风险

**CT0 令牌**：
- 类型：Browser cookie / Session token
- 风险：比 OAuth token 更危险
- 有效期：直到用户从 X.com 注销
- 权限：完整账户访问权限

**建议**（来自警告）：
- ⚠️ 不要提供 CT0 等长期有效的认证令牌
- ✅ 优先使用 OAuth app tokens
- ✅ 或仅使用 webhook 推送

---

## ✅ 我们的修复

### 修复 1: 移除误导性的 requires.env

**修改前**：
```json
"requires": {
  "bins": ["python3", "uv"],
  "env": ["AUTH_TOKEN", "CT0"]  // ❌ 误导：标记为必需
}
```

**修改后**：
```json
"requires": {
  "bins": ["python3", "uv"]  // ✅ 仅列出真正必需的
  // env 字段已移除
}
```

### 修复 2: 添加详细的凭证说明

在 skill.md 中添加了全新的 **"🔐 Security & Credentials"** 部分：

#### 明确说明：核心功能无需凭证
```markdown
### ✅ Core Features: No Credentials Required

All core stock analysis features work **without any API keys or credentials**:
- ✅ Stock & crypto analysis (Yahoo Finance public API)
- ✅ Dividend analysis
- ✅ Portfolio management (local storage)
- ✅ Watchlist & alerts
- ✅ China market reports (public endpoints)
- ✅ Hot scanner (Google News + CoinGecko)
```

#### 明确说明：可选凭证及其用途

**1. Twitter/X 凭证（可选）**：
```markdown
**Required ENV variables** (only if you use `/stock_rumors`):
- `AUTH_TOKEN` - X.com authentication token (browser cookie)
- `CT0` - X.com CT0 token (CSRF token)

**Security Note**:
- ⚠️ These are **browser session cookies**, not OAuth tokens
- ⚠️ Only provide if you trust this skill and understand the risks
- ⚠️ Expires when you log out of X.com
- ℹ️ Used only by `scripts/rumor_detector.py` via `bird` CLI
- ℹ️ Skill gracefully degrades without these - uses Google News only
```

**2. Feishu 凭证（可选）**：
```markdown
**Required ENV variables** (only if you use `--push` flag):
- `FEISHU_APP_ID` - Feishu bot application ID
- `FEISHU_APP_SECRET` - Feishu bot secret key
- `FEISHU_USER_OPEN_ID` - Your Feishu user Open ID

**Security Note**:
- ✅ Uses official Feishu Open Platform OAuth 2.0
- ✅ Bot can only send messages to authorized users
- ℹ️ Used only for push notifications (China market reports, news alerts)
- ℹ️ All features work without this - reports save to local files
```

#### 添加安全最佳实践

```markdown
### 🛡️ Security Best Practices

1. **Never commit credentials** - All `.env*` files are git-ignored
2. **Use separate environments** - Create different `.env` files for dev/prod
3. **Rotate credentials** - Change Feishu app secrets periodically
4. **File permissions** - Ensure `.env` files are `chmod 600` (user-only)
5. **Audit the code** - Full source code: https://github.com/ZhenRobotics/openclaw-research-analyst

**Trust But Verify**:
- Review `scripts/rumor_detector.py` to see how Twitter tokens are used
- Review `scripts/feishu_push.py` to see how Feishu credentials are used
- All credentials stay local - never sent to third parties (except Twitter/Feishu APIs)
```

---

## 📊 修复前后对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| **metadata.requires.env** | ❌ `["AUTH_TOKEN","CT0"]` | ✅ 已移除 |
| **凭证说明** | ❌ 缺失 | ✅ 详细的专用章节 |
| **Feishu 凭证声明** | ❌ 未声明 | ✅ 明确列出并说明 |
| **CT0 风险警告** | ❌ 无警告 | ✅ 明确标注为 browser cookie |
| **凭证可选性** | ❌ 不清楚 | ✅ 明确标注哪些是可选的 |
| **代码审计指引** | ❌ 无 | ✅ "Trust But Verify" 指引 |
| **安全最佳实践** | ❌ 无 | ✅ 5 条详细建议 |

---

## 🎯 修复提交

**Commit**: `a9f62b5`
**Date**: 2026-03-23
**Message**: 📝 Security: Fix metadata and add comprehensive credential documentation

**Changes**:
- Removed `AUTH_TOKEN` and `CT0` from `metadata.requires.env`
- Added **"🔐 Security & Credentials"** section (English + Chinese)
- Documented all optional credential requirements
- Added security warnings for browser cookies (CT0)
- Provided code audit guidance

**Git URL**: https://github.com/ZhenRobotics/openclaw-research-analyst/commit/a9f62b5

---

## 🛡️ 安全透明度提升

### 现在用户可以清楚地看到：

1. **核心功能不需要任何凭证** ✅
2. **Twitter/X 凭证是可选的**，仅用于传闻扫描 ✅
3. **Feishu 凭证是可选的**，仅用于推送通知 ✅
4. **CT0 是浏览器 cookie**，不是 OAuth，有风险 ⚠️
5. **如何验证代码**（具体文件和函数） ✅
6. **凭证如何使用**（仅发送到 Twitter/Feishu API）✅
7. **安全最佳实践**（文件权限、轮换、审计）✅

---

## 📚 相关文档

- **skill.md** (line 200-263) - 安全与凭证完整说明
- **SECURITY_FIX_SUMMARY.md** - 历史凭证泄漏修复记录
- **scripts/rumor_detector.py** - Twitter 令牌使用代码
- **scripts/feishu_push.py** - 飞书凭证使用代码

---

## ✅ 总结

### 为什么会有警告？
ClawHub 的安全扫描发现了三个问题：
1. Metadata 错误地将可选凭证标记为"必需"
2. Feishu 凭证未在 metadata 中声明
3. 缺乏对 CT0（危险的浏览器 cookie）的风险说明

### 我们如何修复？
1. ✅ 移除了误导性的 `requires.env`
2. ✅ 添加了详细的"Security & Credentials"章节
3. ✅ 明确说明所有凭证都是可选的
4. ✅ 警告用户 CT0 的风险
5. ✅ 提供代码审计指引

### 现在安全吗？
✅ **是的！** 修复后：
- 用户清楚知道哪些凭证是可选的
- 用户了解每个凭证的用途和风险
- 用户可以验证代码如何使用凭证
- 提供了安全最佳实践指导

---

**修复完成时间**: 2026-03-23
**最新提交**: a9f62b5
**状态**: ✅ 已推送到 GitHub
**ClawHub 发布就绪**: ✅ 是（凭证文档已完善）
