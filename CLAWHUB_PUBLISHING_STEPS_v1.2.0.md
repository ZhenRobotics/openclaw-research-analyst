# ClawHub Publishing Steps - v1.2.0

**Version**: v1.2.0
**Date**: 2026-03-18
**Status**: Ready for Manual Upload

---

## Prerequisites

- ClawHub account with publishing permissions
- Files prepared in `clawhub-upload/` directory
- Release content document: `CLAWHUB_UPDATE_v1.2.0.md`

---

## Step 1: Login to ClawHub

1. Navigate to https://clawhub.ai
2. Login with your credentials
3. Go to your profile dashboard

---

## Step 2: Navigate to Skill Management

1. Click on "My Skills" or "Manage Skills"
2. Find "openclaw-research-analyst" in your skill list
3. Click "Edit" or "Update"

---

## Step 3: Update Version Information

**Version Number**:
- Change version from `1.1.0` to `1.2.0`

**Verified Commit**:
- Update verified_commit to: `1b4d5ce`

---

## Step 4: Update skill.md

**File**: `clawhub-upload/skill.md`

**Key Changes**:
1. Version updated to v1.2.0
2. New "What's New in v1.2.0" section added
3. New `/cn_brief` command in commands list
4. Updated verified_commit to 1b4d5ce

**Action**:
- Copy entire content from `clawhub-upload/skill.md`
- Paste into ClawHub's skill.md editor
- Review formatting (especially code blocks and tables)

---

## Step 5: Update readme.md

**File**: `clawhub-upload/readme.md`

**Key Changes**:
1. Version updated from 1.1 to 1.2
2. New "What's New in v1.2.0" section
3. Updated feature descriptions

**Action**:
- Copy entire content from `clawhub-upload/readme.md`
- Paste into ClawHub's readme.md editor
- Review formatting (especially badges and feature tables)

---

## Step 6: Add Update Announcement

**Source**: `CLAWHUB_UPDATE_v1.2.0.md`

**Content to Add**:
```
🎉 v1.2.0 Major Update - One-Click Brief & Smart Scheduling

📊 One-Click Brief (一键精简简报)
- Ultra-fast market summary (~2 seconds)
- New command: python3 scripts/cn_market_brief.py
- Optional Feishu push integration
- JSON output for automation

⏰ Smart Scheduling (智能定时任务)
- Intelligent trading-hours cron jobs
- Intraday: Every 10 min (Mon-Fri 09:30-15:00)
- EOD report: Once at 15:05
- Auto-skip weekends

📚 Documentation: SMART_SCHEDULING.md
```

**Action**:
- Use content from `CLAWHUB_UPDATE_v1.2.0.md`
- Add to "Updates" or "Changelog" section
- Include release date: 2026-03-18

---

## Step 7: Update Package Information

**npm Package**:
- Version: 1.2.0
- Status: Published
- URL: https://www.npmjs.com/package/openclaw-research-analyst

**GitHub Release**:
- Tag: v1.2.0
- URL: https://github.com/ZhenRobotics/openclaw-research-analyst/releases/tag/v1.2.0

**Action**:
- Update any package links if needed
- Verify version consistency across all fields

---

## Step 8: Accept MIT-0 License Agreement

**Important**: ClawHub requires manual acceptance of MIT-0 license agreement for each update.

**Action**:
- Read the license agreement carefully
- Check the acceptance box
- This is why automation is not possible

---

## Step 9: Preview Before Publishing

**Checklist**:
- [ ] Version shows 1.2.0
- [ ] verified_commit is 1b4d5ce
- [ ] skill.md displays correctly with new commands
- [ ] readme.md shows new features section
- [ ] Update announcement is visible
- [ ] All code blocks render properly
- [ ] All links work (npm, GitHub)

---

## Step 10: Publish

1. Click "Preview" to review changes
2. Verify all content renders correctly
3. Click "Publish" or "Update"
4. Wait for confirmation message

---

## Step 11: Verify Published Version

**Post-Publishing Checks**:

1. **ClawHub Page**:
   - Visit your skill page on ClawHub
   - Confirm version shows 1.2.0
   - Check that new features are visible

2. **Installation Test**:
   ```bash
   clawhub install research-analyst
   # Should install v1.2.0
   ```

3. **Functionality Test**:
   ```bash
   cd ~/.openclaw/skills/research-analyst
   python3 scripts/cn_market_brief.py
   # Should work with new one-click brief
   ```

---

## Troubleshooting

### Issue: Preview doesn't render correctly

**Solution**:
- Check markdown syntax
- Ensure code blocks use triple backticks
- Verify table formatting

### Issue: License agreement not appearing

**Solution**:
- Refresh the page
- Try a different browser
- Contact ClawHub support if persists

### Issue: Changes not visible after publishing

**Solution**:
- Clear browser cache
- Wait 5-10 minutes for CDN propagation
- Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

---

## Post-Publishing Tasks

1. **Announce Update**:
   - Post update announcement on social media
   - Update project documentation
   - Notify users via appropriate channels

2. **Monitor Feedback**:
   - Watch for issues on GitHub
   - Monitor ClawHub comments
   - Track npm download statistics

3. **Archive Release Materials**:
   - Keep CLAWHUB_UPDATE_v1.2.0.md for records
   - Document any issues encountered
   - Note time taken for future reference

---

## Files Summary

**Prepared Files**:
- `clawhub-upload/skill.md` - Updated to v1.2.0
- `clawhub-upload/readme.md` - Updated to v1.2.0
- `CLAWHUB_UPDATE_v1.2.0.md` - Update page content
- `RELEASE_NOTES_v1.2.0.md` - Full release notes

**Release Status**:
- npm: ✅ Published (v1.2.0)
- GitHub: ✅ Released (v1.2.0)
- ClawHub: ⏳ Ready for manual upload

---

## Completion Checklist

- [ ] Logged into ClawHub
- [ ] Found openclaw-research-analyst skill
- [ ] Updated version to 1.2.0
- [ ] Updated verified_commit to 1b4d5ce
- [ ] Uploaded new skill.md
- [ ] Uploaded new readme.md
- [ ] Added update announcement
- [ ] Accepted MIT-0 license
- [ ] Previewed all changes
- [ ] Published update
- [ ] Verified published version
- [ ] Tested installation
- [ ] Announced update

---

**Estimated Time**: 15-20 minutes

**Contact**: For issues, open a GitHub issue at https://github.com/ZhenRobotics/openclaw-research-analyst/issues

---

**Publishing Date**: 2026-03-18
**Publisher**: Manual upload required
**Status**: ✅ Ready to publish
