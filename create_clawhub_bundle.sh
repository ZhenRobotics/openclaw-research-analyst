#!/bin/bash
# ClawHub Bundle Creator
# OpenClaw Research Analyst v1.4.0
#
# Creates a clean, credential-free bundle for ClawHub submission
# Run from project root: bash create_clawhub_bundle.sh

set -e  # Exit on error

PROJECT_ROOT="/home/justin/openclaw-research-analyst"
BUNDLE_DIR="/tmp/clawhub-research-analyst-v1.4.0"
VERSION="1.4.0"

cd "$PROJECT_ROOT"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "ClawHub Bundle Creator"
echo "=========================================="
echo ""
echo "Version: $VERSION"
echo "Source: $PROJECT_ROOT"
echo "Target: $BUNDLE_DIR"
echo ""

# Step 1: Pre-flight checks
echo "Step 1: Pre-flight security checks..."

ISSUES=0

# Check for .env file
if [ -f .env ]; then
    echo -e "${RED}  ✗ .env file exists - run fix_security_issues.sh first${NC}"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}  ✓ .env file not present${NC}"
fi

# Check for credentials in code (exclude .env.example and scripts)
if grep -rI "sk-proj-[a-zA-Z0-9]{48,}" . --exclude-dir=.git --exclude="*.md" --exclude="*.backup.*" --exclude="*.sh" --exclude=".env.example" 2>/dev/null; then
    echo -e "${RED}  ✗ Found OpenAI API keys in code${NC}"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}  ✓ No OpenAI API keys in code${NC}"
fi

if grep -rI "LTAI[A-Za-z0-9]{20,}" . --exclude-dir=.git --exclude="*.md" --exclude="*.backup.*" --exclude="*.sh" --exclude=".env.example" 2>/dev/null; then
    echo -e "${RED}  ✗ Found Aliyun Access Keys in code${NC}"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}  ✓ No Aliyun Access Keys in code${NC}"
fi

# Check version consistency
SKILL_VERSION=$(grep "^version:" openclaw-skill/skill.md | awk '{print $2}')
PKG_VERSION=$(grep '"version"' package.json | head -1 | awk -F'"' '{print $4}')

if [ "$SKILL_VERSION" != "1.4.0" ] || [ "$PKG_VERSION" != "1.4.0" ]; then
    echo -e "${YELLOW}  ! Version mismatch: skill.md=$SKILL_VERSION, package.json=$PKG_VERSION${NC}"
    echo -e "${YELLOW}    Expected: 1.4.0 for both${NC}"
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}  ✓ Version numbers consistent (1.4.0)${NC}"
fi

if [ $ISSUES -gt 0 ]; then
    echo ""
    echo -e "${RED}Pre-flight checks failed: $ISSUES issue(s) found${NC}"
    echo "Run fix_security_issues.sh to resolve issues"
    exit 1
fi

echo ""
echo -e "${GREEN}Pre-flight checks passed${NC}"
echo ""

# Step 2: Clean previous bundle
echo "Step 2: Cleaning previous bundle..."
if [ -d "$BUNDLE_DIR" ]; then
    rm -rf "$BUNDLE_DIR"
    echo -e "${GREEN}  ✓ Removed previous bundle${NC}"
else
    echo -e "${GREEN}  ✓ No previous bundle found${NC}"
fi

# Step 3: Create bundle directory
echo ""
echo "Step 3: Creating bundle directory..."
mkdir -p "$BUNDLE_DIR"
echo -e "${GREEN}  ✓ Created $BUNDLE_DIR${NC}"

# Step 4: Copy files according to package.json "files" array
echo ""
echo "Step 4: Copying project files..."

# Scripts directory
if [ -d scripts ]; then
    cp -r scripts "$BUNDLE_DIR/"
    SCRIPT_COUNT=$(find "$BUNDLE_DIR/scripts" -name "*.py" | wc -l)
    echo -e "${GREEN}  ✓ Copied scripts/ ($SCRIPT_COUNT Python files)${NC}"
else
    echo -e "${RED}  ✗ scripts/ directory not found${NC}"
    exit 1
fi

# Docs directory
if [ -d docs ]; then
    cp -r docs "$BUNDLE_DIR/"
    DOC_COUNT=$(find "$BUNDLE_DIR/docs" -name "*.md" | wc -l)
    echo -e "${GREEN}  ✓ Copied docs/ ($DOC_COUNT documentation files)${NC}"
else
    echo -e "${YELLOW}  ! docs/ directory not found (optional)${NC}"
fi

# Skill file (renamed to skill.md in bundle root)
if [ -f "openclaw-skill/skill.md" ]; then
    cp "openclaw-skill/skill.md" "$BUNDLE_DIR/skill.md"
    echo -e "${GREEN}  ✓ Copied openclaw-skill/skill.md → skill.md${NC}"
else
    echo -e "${RED}  ✗ openclaw-skill/skill.md not found${NC}"
    exit 1
fi

# Root files (excluded INSTALL.md, .env files, and LICENSE per ClawHub validation)
ROOT_FILES=(
    "README.md"
    "SECURITY.md"
    "package.json"
    "pyproject.toml"
    "requirements.txt"
    "verify_install.sh"
)

for file in "${ROOT_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BUNDLE_DIR/"
        echo -e "${GREEN}  ✓ Copied $file${NC}"
    else
        echo -e "${YELLOW}  ! $file not found${NC}"
    fi
done

# Step 5: Clean bundle (remove bytecode, temp files)
echo ""
echo "Step 5: Cleaning bundle..."
find "$BUNDLE_DIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "$BUNDLE_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$BUNDLE_DIR" -name ".DS_Store" -delete 2>/dev/null || true
echo -e "${GREEN}  ✓ Removed bytecode and temp files${NC}"

# Step 6: Final credential scan on bundle
echo ""
echo "Step 6: Final credential scan on bundle..."

BUNDLE_CRED_FOUND=0

# Scan for real credentials (exclude .env.example placeholders)
if grep -rI "sk-proj-[a-zA-Z0-9]{48,}" "$BUNDLE_DIR/" --exclude=".env.example" --exclude=".env.feishu.example" 2>/dev/null; then
    echo -e "${RED}  ✗ CRITICAL: Found OpenAI API keys in bundle!${NC}"
    BUNDLE_CRED_FOUND=1
else
    echo -e "${GREEN}  ✓ No OpenAI API keys in bundle${NC}"
fi

if grep -rI "LTAI[A-Za-z0-9]{20,}" "$BUNDLE_DIR/" --exclude=".env.example" --exclude=".env.feishu.example" 2>/dev/null; then
    echo -e "${RED}  ✗ CRITICAL: Found Aliyun Access Keys in bundle!${NC}"
    BUNDLE_CRED_FOUND=1
else
    echo -e "${GREEN}  ✓ No Aliyun Access Keys in bundle${NC}"
fi

if [ $BUNDLE_CRED_FOUND -eq 1 ]; then
    echo ""
    echo -e "${RED}BUNDLE CONTAINS CREDENTIALS - CANNOT SUBMIT${NC}"
    echo "Remove credentials from source and recreate bundle"
    exit 1
fi

# Step 7: Bundle statistics
echo ""
echo "Step 7: Bundle statistics..."
BUNDLE_SIZE=$(du -sh "$BUNDLE_DIR" | awk '{print $1}')
FILE_COUNT=$(find "$BUNDLE_DIR" -type f | wc -l)
PY_FILES=$(find "$BUNDLE_DIR" -name "*.py" | wc -l)
MD_FILES=$(find "$BUNDLE_DIR" -name "*.md" | wc -l)

echo "  - Total size: $BUNDLE_SIZE"
echo "  - Total files: $FILE_COUNT"
echo "  - Python scripts: $PY_FILES"
echo "  - Documentation: $MD_FILES"

# Step 8: Create tarball
echo ""
echo "Step 8: Creating tarball..."
cd /tmp
TARBALL="research-analyst-v${VERSION}.tar.gz"
tar -czf "$TARBALL" "clawhub-research-analyst-v${VERSION}/"
TARBALL_SIZE=$(du -sh "$TARBALL" | awk '{print $1}')
echo -e "${GREEN}  ✓ Created $TARBALL ($TARBALL_SIZE)${NC}"

# Step 9: Verify tarball
echo ""
echo "Step 9: Verifying tarball..."
tar -tzf "$TARBALL" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✓ Tarball integrity verified${NC}"
else
    echo -e "${RED}  ✗ Tarball verification failed${NC}"
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "Bundle Creation Complete"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ Bundle created successfully${NC}"
echo ""
echo "Bundle location:"
echo -e "  Directory: ${BLUE}$BUNDLE_DIR${NC}"
echo -e "  Tarball:   ${BLUE}/tmp/$TARBALL${NC}"
echo ""
echo "Bundle contents:"
echo "  - Size: $BUNDLE_SIZE (tarball: $TARBALL_SIZE)"
echo "  - Files: $FILE_COUNT"
echo "  - Python scripts: $PY_FILES"
echo "  - Documentation: $MD_FILES"
echo ""
echo "Next steps:"
echo "1. Upload tarball to ClawHub:"
echo "   https://clawhub.ai/publish"
echo ""
echo "2. Or upload directory contents:"
echo "   cd $BUNDLE_DIR"
echo "   [Upload via ClawHub web interface]"
echo ""
echo "3. Fill metadata form:"
echo "   - Name: research-analyst"
echo "   - Version: 1.4.0"
echo "   - Category: Finance & Business"
echo "   - Tags: stock, crypto, analysis, portfolio, china-market"
echo ""
echo "4. After approval, test installation:"
echo "   claw install research-analyst"
echo "   /stock AAPL"
echo ""
echo "See CLAWHUB_PRE_SUBMISSION_CHECKLIST.md for complete instructions"
