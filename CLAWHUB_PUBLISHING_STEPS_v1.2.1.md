# ClawHub Publishing Steps - v1.2.1

**Version**: v1.2.1
**Date**: 2026-03-20
**Status**: Ready for Manual Upload

---

## Quick Reference

**Version**: 1.2.1
**Verified Commit**: 910b35d
**Files**: clawhub-upload/skill.md, clawhub-upload/readme.md
**Update Content**: CLAWHUB_UPDATE_v1.2.1.md

---

## Prerequisites

✅ All automated steps completed:
- npm published: openclaw-research-analyst@1.2.1
- GitHub release: https://github.com/ZhenRobotics/openclaw-research-analyst/releases/tag/v1.2.1
- Files prepared in clawhub-upload/

---

## Step 1: Login to ClawHub

1. Navigate to https://clawhub.ai
2. Login with your credentials
3. Go to your profile dashboard

---

## Step 2: Navigate to Skill

1. Click on "My Skills" or "Manage Skills"
2. Find "openclaw-research-analyst" in your skill list
3. Click "Edit" or "Update"

---

## Step 3: Update Version Information

**Version Number**:
- Change from: `1.2.0`
- Change to: `1.2.1`

**Verified Commit**:
- Change from: `caf48dc` (v1.2.0)
- Change to: `910b35d` (v1.2.1)

**Comment**: "v1.2.1 - Feishu push optimizations (detailed status, retry, logging)"

---

## Step 4: Upload skill.md

**Source File**: `clawhub-upload/skill.md`

**Key Updates in This File**:
```yaml
version: 1.2.1
verified_commit: 910b35d  # v1.2.1 - Feishu push optimizations
```

**New Content Section**:
```markdown
## ✨ What's New in v1.2.1

### 🔧 Feishu Push Optimizations
- Detailed Return Values
- Auto-Retry Mechanism
- Push History Logging
- Clear Error Messages
```

**Action**:
1. Copy entire content from `clawhub-upload/skill.md`
2. Paste into ClawHub's skill.md editor
3. Verify:
   - [ ] version: 1.2.1
   - [ ] verified_commit: 910b35d
   - [ ] "What's New in v1.2.1" section visible
   - [ ] Code blocks render correctly
   - [ ] Commands list includes /cn_brief

---

## Step 5: Upload readme.md

**Source File**: `clawhub-upload/readme.md`

**Key Updates in This File**:
```markdown
# 📈 OpenClaw Research Analyst v1.2.1

## ✨ What's New in v1.2.1

**🔧 Feishu Push Optimizations:**
- Detailed Status
- Auto-Retry
- Push Logging
- Clear Errors
```

**Action**:
1. Copy entire content from `clawhub-upload/readme.md`
2. Paste into ClawHub's readme.md editor
3. Verify:
   - [ ] Title shows v1.2.1
   - [ ] "What's New in v1.2.1" section at top
   - [ ] Badges display correctly
   - [ ] Feature table complete
   - [ ] Installation instructions accurate

---

## Step 6: Add Update Announcement

**Source**: `CLAWHUB_UPDATE_v1.2.1.md`

**Content to Add**:
```markdown
🔧 v1.2.1 Patch Release - Feishu Push Optimizations

📊 Detailed Return Values
- Get message ID, timestamp, error details
- Example: result['message_ids'], result['success']

🔄 Auto-Retry Mechanism
- Network requests retry up to 2 times
- Exponential backoff: 1s, 2s

📝 Push History Logging
- Track all push attempts
- Log file: logs/feishu_push_history.log
- JSON format for analysis

🎯 Clear Error Messages
- Distinguish config vs network errors
- "User Open ID not configured"
- "Timeout: Connection timeout..."

📚 New Documentation
- FEISHU_PUSH_v1.2.1_GUIDE.md - Complete guide
- OPTIMIZATION_v1.2.1.md - Implementation details

Compatibility: ✅ Fully backward compatible with v1.2.0
Performance: Success ~2s, Retry +1-3s, Logging +5-10ms
```

**Action**:
1. Open `CLAWHUB_UPDATE_v1.2.1.md`
2. Copy relevant sections (use the summary above or full content)
3. Paste into ClawHub's "Update Notes" or "Changelog" field
4. Add release date: 2026-03-20

---

## Step 7: Update Package Information

**npm Package**:
- Version: 1.2.1
- Status: Published ✅
- URL: https://www.npmjs.com/package/openclaw-research-analyst

**GitHub Release**:
- Tag: v1.2.1
- Status: Published ✅
- URL: https://github.com/ZhenRobotics/openclaw-research-analyst/releases/tag/v1.2.1

**Action**:
1. Verify package links are up to date
2. Ensure version consistency across all fields
3. Update any "Latest Version" references

---

## Step 8: Accept MIT-0 License Agreement

**Important**: ClawHub requires manual acceptance of MIT-0 license for each update.

**Action**:
1. Read the license agreement carefully
2. Check the acceptance box
3. This step **cannot be automated** - it's why manual upload is required

---

## Step 9: Preview Changes

**Checklist**:
- [ ] Version shows 1.2.1
- [ ] verified_commit is 910b35d
- [ ] skill.md displays v1.2.1 "What's New" section
- [ ] readme.md shows v1.2.1 at top
- [ ] Update announcement is visible and complete
- [ ] All code blocks render properly
- [ ] All links work (npm, GitHub)
- [ ] Tables and lists format correctly
- [ ] Badges display (if applicable)

**Action**:
1. Click "Preview" button
2. Scroll through entire preview
3. Check both English and Chinese sections
4. Verify technical content accuracy
5. Fix any formatting issues before publishing

---

## Step 10: Publish

**Final Checks**:
- [ ] Version: 1.2.1
- [ ] Commit: 910b35d
- [ ] Files uploaded and verified
- [ ] Update notes added
- [ ] License accepted
- [ ] Preview looks good

**Action**:
1. Take a deep breath 😊
2. Click "Publish" or "Update" button
3. Wait for confirmation message
4. Note: Processing may take 1-2 minutes

---

## Step 11: Verify Published Version

**Post-Publishing Checks**:

1. **ClawHub Page**:
   - Visit your skill page on ClawHub
   - Confirm version shows 1.2.1
   - Check "What's New" section displays
   - Verify update announcement is visible

2. **Installation Test**:
   ```bash
   clawhub install research-analyst
   # Should install v1.2.1

   clawhub info research-analyst
   # Should show version 1.2.1
   ```

3. **Functionality Test**:
   ```bash
   cd ~/.openclaw/skills/research-analyst

   # Test new features
   python3 -c "
   from scripts.feishu_push import FeishuPusher
   pusher = FeishuPusher(enable_logging=False)
   result = pusher.push_to_webhook('test')
   print(f'Result has message_id: {\"message_id\" in result}')
   print(f'Result has error: {\"error\" in result}')
   "
   ```

4. **Check Logs Directory**:
   ```bash
   ls -la ~/.openclaw/skills/research-analyst/logs/
   # Should exist (created on first push)
   ```

---

## Troubleshooting

### Issue: Preview doesn't render correctly

**Solution**:
- Check markdown syntax in skill.md/readme.md
- Ensure code blocks use triple backticks
- Verify table formatting (pipes and spacing)
- Look for unclosed tags or quotes

### Issue: License agreement not appearing

**Solution**:
- Refresh the page
- Clear browser cache
- Try a different browser (Chrome/Firefox)
- Contact ClawHub support if issue persists

### Issue: Changes not visible after publishing

**Solution**:
- Wait 5-10 minutes for CDN propagation
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Try incognito/private window
- Check ClawHub status page for outages

### Issue: Version conflict warning

**Solution**:
- Verify package.json shows 1.2.1
- Check npm shows v1.2.1: `npm view openclaw-research-analyst version`
- Ensure GitHub tag v1.2.1 exists
- Confirm skill.md and readme.md are updated

---

## Post-Publishing Tasks

### 1. Announce Update

**Channels**:
- Social media (Twitter, LinkedIn, etc.)
- Project homepage/blog
- User mailing list
- Community forums

**Sample Announcement**:
```
🎉 openclaw-research-analyst v1.2.1 released!

🔧 Feishu Push Optimizations:
✨ Detailed status tracking (message ID, timestamp, errors)
✨ Auto-retry for network failures (2 retries)
✨ Push history logging for troubleshooting
✨ Clear error messages

📦 Update: npm update -g openclaw-research-analyst
📚 Docs: https://github.com/ZhenRobotics/openclaw-research-analyst

#opensource #python #finance #trading
```

### 2. Monitor Feedback

- Watch GitHub issues: https://github.com/ZhenRobotics/openclaw-research-analyst/issues
- Monitor ClawHub comments
- Track npm download statistics
- Check for error reports

### 3. Archive Release Materials

- Keep CLAWHUB_UPDATE_v1.2.1.md for records
- Document any issues encountered during upload
- Note time taken for future reference
- Save screenshots of ClawHub pages (optional)

### 4. Update Internal Documentation

- Mark v1.2.1 as published in project tracker
- Update any internal roadmaps
- Document lessons learned
- Plan next release (if applicable)

---

## Files Summary

**Prepared Files**:
- `clawhub-upload/skill.md` - v1.2.1 (910b35d)
- `clawhub-upload/readme.md` - v1.2.1 features
- `CLAWHUB_UPDATE_v1.2.1.md` - Update announcement
- `RELEASE_NOTES_v1.2.1.md` - Full release notes
- `RELEASE_SUMMARY_v1.2.1.md` - Release summary

**Release Status**:
- npm: ✅ Published (v1.2.1)
- GitHub: ✅ Released (v1.2.1)
- ClawHub: ⏳ Ready for manual upload

---

## Completion Checklist

- [ ] Logged into ClawHub
- [ ] Found openclaw-research-analyst skill
- [ ] Updated version to 1.2.1
- [ ] Updated verified_commit to 910b35d
- [ ] Uploaded skill.md
- [ ] Uploaded readme.md
- [ ] Added update announcement
- [ ] Accepted MIT-0 license
- [ ] Previewed all changes
- [ ] Published update
- [ ] Verified published version on ClawHub
- [ ] Tested installation via ClawHub
- [ ] Verified functionality
- [ ] Announced update (optional)
- [ ] Monitored for issues

---

## Support

**Issues During Upload?**
- ClawHub support: https://clawhub.ai/support
- GitHub issues: https://github.com/ZhenRobotics/openclaw-research-analyst/issues
- Documentation: See RELEASE_NOTES_v1.2.1.md

---

**Estimated Time**: 10-15 minutes

**Last Updated**: 2026-03-20

**Status**: ✅ Ready to publish
