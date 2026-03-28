#!/bin/bash
# Installation Verification Script
# Research Analyst v1.3.3
#
# This script verifies the integrity of the installation before execution.
# Run this BEFORE executing any analysis scripts.

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "=========================================="
echo "Research Analyst Installation Verification"
echo "v1.3.3"
echo "=========================================="
echo ""

# Check 1: Git tag verification
echo "1. Verifying git tag signature..."
if git verify-tag v1.3.3 2>/dev/null; then
    echo -e "${GREEN}   ✓ Git tag verified${NC}"
else
    echo -e "${RED}   ✗ Git tag verification failed or not signed${NC}"
    echo "     Run: git verify-tag v1.3.3 (manually verify output)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 2: Check for modified files
echo "2. Checking for modified files..."
MODIFIED=$(git status --porcelain | grep "^ M" | wc -l)
if [ "$MODIFIED" -eq 0 ]; then
    echo -e "${GREEN}   ✓ No modified files (clean checkout)${NC}"
else
    echo -e "${YELLOW}   ⚠ $MODIFIED files modified since checkout${NC}"
    echo "     WARNING: Files have been changed since git clone"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 3: Verify requirements.txt exists and matches expected
echo "3. Verifying requirements.txt..."
if [ -f requirements.txt ]; then
    echo -e "${GREEN}   ✓ requirements.txt found${NC}"

    # Check for hash markers
    HASH_COUNT=$(grep -c "sha256:" requirements.txt || echo 0)
    if [ "$HASH_COUNT" -gt 0 ]; then
        echo -e "${GREEN}   ✓ Contains $HASH_COUNT SHA256 hashes${NC}"
    else
        echo -e "${RED}   ✗ No SHA256 hashes found in requirements.txt${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}   ✗ requirements.txt not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: Verify Python environment
echo "4. Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}   ✓ Python 3 found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}   ✗ Python 3 not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: Check for suspicious patterns in code
echo "5. Scanning for suspicious patterns..."

SUSPICIOUS=0

# Check for eval/exec
EVAL_COUNT=$(grep -r "eval\|exec(" scripts/ 2>/dev/null | grep -v ".pyc" | wc -l)
if [ "$EVAL_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ Found $EVAL_COUNT eval/exec calls${NC}"
    SUSPICIOUS=$((SUSPICIOUS + 1))
fi

# Check for subprocess
SUBPROCESS_COUNT=$(grep -r "subprocess\|os.system" scripts/ 2>/dev/null | grep -v ".pyc" | wc -l)
if [ "$SUBPROCESS_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ Found $SUBPROCESS_COUNT subprocess/system calls${NC}"
    SUSPICIOUS=$((SUSPICIOUS + 1))
fi

# Check for network POST
POST_COUNT=$(grep -ri "method.*post\|requests.post" scripts/ 2>/dev/null | grep -v ".pyc" | wc -l)
if [ "$POST_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠ Found $POST_COUNT POST requests${NC}"
    SUSPICIOUS=$((SUSPICIOUS + 1))
fi

if [ "$SUSPICIOUS" -eq 0 ]; then
    echo -e "${GREEN}   ✓ No obvious suspicious patterns detected${NC}"
else
    echo -e "${YELLOW}   ⚠ Found $SUSPICIOUS types of potentially suspicious patterns${NC}"
    echo "     Review these manually before proceeding"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 6: Verify key files exist
echo "6. Verifying key files..."
KEY_FILES=(
    "scripts/stock_analyzer.py"
    "SECURITY.md"
    "README.md"
)

for file in "${KEY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}   ✓ $file${NC}"
    else
        echo -e "${RED}   ✗ $file missing${NC}"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check 7: Verify no unauthorized network access in imports
echo "7. Checking import statements..."
UNUSUAL_IMPORTS=$(grep -rh "^import\|^from" scripts/ 2>/dev/null | \
    grep -E "socket|telnetlib|ftplib|smtplib|poplib|imaplib" | wc -l)

if [ "$UNUSUAL_IMPORTS" -eq 0 ]; then
    echo -e "${GREEN}   ✓ No unusual network imports${NC}"
else
    echo -e "${YELLOW}   ⚠ Found $UNUSUAL_IMPORTS unusual network imports${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "Errors:   $ERRORS"
echo -e "Warnings: $WARNINGS"
echo ""

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Installation appears safe to use."
    echo "You may proceed with running scripts."
    echo ""
    exit 0
elif [ "$ERRORS" -eq 0 ]; then
    echo -e "${YELLOW}⚠ PASSED WITH WARNINGS${NC}"
    echo ""
    echo "Installation has warnings but no critical errors."
    echo "Review warnings above before proceeding."
    echo ""
    echo "To continue anyway, review the warnings and decide if acceptable."
    exit 0
else
    echo -e "${RED}✗ VERIFICATION FAILED${NC}"
    echo ""
    echo "Critical errors detected. DO NOT proceed with installation."
    echo "Fix the errors above or review the source code manually."
    echo ""
    exit 1
fi
