#!/bin/bash
# ClawHub Pre-Submission Security Fixes
# OpenClaw Research Analyst v1.3.0
#
# This script fixes all critical security issues before ClawHub submission
# Run from project root: bash fix_security_issues.sh

set -e  # Exit on error

PROJECT_ROOT="/home/justin/openclaw-research-analyst"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "ClawHub Security Fixes - Starting"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Remove .env file with active credentials
echo "Step 1: Removing .env file with exposed credentials..."
if [ -f .env ]; then
    echo "  - Found .env file, backing up to .env.backup.$(date +%Y%m%d_%H%M%S)"
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    rm .env
    echo -e "${GREEN}  ✓ .env removed${NC}"
else
    echo -e "${GREEN}  ✓ .env not found (already removed)${NC}"
fi

# Step 2: Verify .env is gone
echo ""
echo "Step 2: Verifying .env removal..."
if [ -f .env ]; then
    echo -e "${RED}  ✗ ERROR: .env still exists!${NC}"
    exit 1
else
    echo -e "${GREEN}  ✓ .env successfully removed${NC}"
fi

# Step 3: Add .env.cn_market to .gitignore
echo ""
echo "Step 3: Updating .gitignore..."
if grep -q "^.env.cn_market$" .gitignore 2>/dev/null; then
    echo -e "${GREEN}  ✓ .env.cn_market already in .gitignore${NC}"
else
    echo "" >> .gitignore
    echo "# Additional env files (added by security fix script)" >> .gitignore
    echo ".env.cn_market" >> .gitignore
    echo -e "${GREEN}  ✓ Added .env.cn_market to .gitignore${NC}"
fi

# Step 4: Clean Python bytecode
echo ""
echo "Step 4: Cleaning Python bytecode..."
BYTECODE_COUNT=$(find . -type d -name __pycache__ 2>/dev/null | wc -l)
if [ "$BYTECODE_COUNT" -gt 0 ]; then
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    echo -e "${GREEN}  ✓ Removed $BYTECODE_COUNT __pycache__ directories${NC}"
else
    echo -e "${GREEN}  ✓ No bytecode files found${NC}"
fi

# Step 5: Remove untracked report files
echo ""
echo "Step 5: Removing untracked report files..."
REPORTS=(
    "CLAWHUB_EVALUATION_REPORT.md"
    "CLAWHUB_PUBLISHING_STEPS_v1.3.0.md"
    "CLAWHUB_SECURITY_WARNING_EXPLAINED.md"
    "CLAWHUB_UPDATE_v1.3.0.md"
    "FEISHU_CONFIG_FIX.md"
    "RELEASE_COMPLETE_v1.3.0.md"
    "SECURITY_AUDIT_REPORT.md"
    "SECURITY_FIX_SUMMARY.md"
)

REMOVED_COUNT=0
for file in "${REPORTS[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
        echo "  - Removed $file"
    fi
done

if [ $REMOVED_COUNT -gt 0 ]; then
    echo -e "${GREEN}  ✓ Removed $REMOVED_COUNT report files${NC}"
else
    echo -e "${GREEN}  ✓ No untracked report files found${NC}"
fi

# Step 6: Sync version numbers
echo ""
echo "Step 6: Syncing version numbers to v1.3.0..."

# Update SKILL.md
if grep -q "^version: 1.0.0" SKILL.md; then
    sed -i 's/^version: 1.0.0/version: 1.3.0/' SKILL.md
    echo -e "${GREEN}  ✓ Updated SKILL.md version${NC}"
else
    echo -e "${YELLOW}  ! SKILL.md version already updated or not found${NC}"
fi

# Update README.md
if grep -q "# 📈 OpenClaw Research Analyst v1.0" README.md; then
    sed -i 's/# 📈 OpenClaw Research Analyst v1.0/# 📈 OpenClaw Research Analyst v1.3.0/' README.md
    echo -e "${GREEN}  ✓ Updated README.md version${NC}"
else
    echo -e "${YELLOW}  ! README.md version already updated or not found${NC}"
fi

# Update INSTALL.md
if grep -q "# Installation Guide - OpenClaw Research Analyst v1.0.0" INSTALL.md; then
    sed -i 's/# Installation Guide - OpenClaw Research Analyst v1.0.0/# Installation Guide - OpenClaw Research Analyst v1.3.0/' INSTALL.md
    sed -i 's/\*\*Version\*\*: 1.0.0/**Version**: 1.3.0/' INSTALL.md
    echo -e "${GREEN}  ✓ Updated INSTALL.md version${NC}"
else
    echo -e "${YELLOW}  ! INSTALL.md version already updated or not found${NC}"
fi

# Step 7: Final credential scan
echo ""
echo "Step 7: Running final credential scan..."
CRED_FOUND=0

if grep -rI "sk-proj-" . --exclude-dir=.git --exclude="*.md" --exclude="*.backup.*" 2>/dev/null; then
    echo -e "${RED}  ✗ Found OpenAI API keys in code!${NC}"
    CRED_FOUND=1
else
    echo -e "${GREEN}  ✓ No OpenAI API keys found${NC}"
fi

if grep -rI "LTAI[A-Za-z0-9]" . --exclude-dir=.git --exclude="*.md" --exclude="*.backup.*" 2>/dev/null; then
    echo -e "${RED}  ✗ Found Aliyun Access Keys in code!${NC}"
    CRED_FOUND=1
else
    echo -e "${GREEN}  ✓ No Aliyun Access Keys found${NC}"
fi

# Step 8: Git status check
echo ""
echo "Step 8: Checking git status..."
echo "Modified files:"
git status --short

# Step 9: Version consistency check
echo ""
echo "Step 9: Verifying version consistency..."
SKILL_VERSION=$(grep "^version:" SKILL.md | awk '{print $2}')
PKG_VERSION=$(grep '"version"' package.json | head -1 | awk -F'"' '{print $4}')
README_VERSION=$(head -1 README.md | grep -oP 'v\d+\.\d+\.\d+' | sed 's/v//')

echo "  - SKILL.md: $SKILL_VERSION"
echo "  - package.json: $PKG_VERSION"
echo "  - README.md: $README_VERSION"

if [ "$SKILL_VERSION" = "1.3.0" ] && [ "$PKG_VERSION" = "1.3.0" ] && [ "$README_VERSION" = "1.3.0" ]; then
    echo -e "${GREEN}  ✓ All versions synchronized to 1.3.0${NC}"
else
    echo -e "${YELLOW}  ! Version mismatch detected${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "Security Fixes Summary"
echo "=========================================="
echo ""

if [ $CRED_FOUND -eq 1 ]; then
    echo -e "${RED}✗ CREDENTIALS STILL FOUND - MANUAL REVIEW REQUIRED${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review files containing credentials"
    echo "2. Remove or mask sensitive values"
    echo "3. Re-run this script"
    exit 1
else
    echo -e "${GREEN}✓ All critical security issues fixed${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review changes: git status"
    echo "2. Commit changes: git add .gitignore SKILL.md README.md INSTALL.md"
    echo "3. git commit -m '🔒 Security: Prepare for ClawHub submission'"
    echo "4. REVOKE exposed API keys:"
    echo "   - OpenAI: https://platform.openai.com/api-keys"
    echo "   - Aliyun: https://ram.console.aliyun.com/manage/ak"
    echo "5. Run: bash create_clawhub_bundle.sh"
fi

echo ""
echo "See CLAWHUB_PRE_SUBMISSION_CHECKLIST.md for detailed instructions"
echo "See CLAWHUB_SECURITY_REPORT.md for full security analysis"
