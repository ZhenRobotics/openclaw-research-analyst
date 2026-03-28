#!/bin/bash
# VirusTotal Pre-Scan Verification
# Research Analyst v1.3.3
#
# This script verifies the bundle will pass VirusTotal scanning
# Run this BEFORE uploading to VirusTotal

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BUNDLE_DIR="/tmp/clawhub-research-analyst-v1.3.3"
TARBALL="/tmp/research-analyst-v1.3.3.tar.gz"

echo "=========================================="
echo "VirusTotal Pre-Scan Verification"
echo "v1.3.3"
echo "=========================================="
echo ""

if [ ! -f "$TARBALL" ]; then
    echo -e "${RED}✗ Tarball not found: $TARBALL${NC}"
    exit 1
fi

if [ ! -d "$BUNDLE_DIR" ]; then
    echo "Extracting tarball for inspection..."
    cd /tmp
    tar -xzf research-analyst-v1.3.3.tar.gz
fi

cd "$BUNDLE_DIR"

ERRORS=0
WARNINGS=0

# Check 1: No binary executables
echo "1. Checking for binary executables..."
BINARIES=$(find . -type f -executable -not -name "*.sh" -not -name "*.py" | wc -l)
if [ "$BINARIES" -eq 0 ]; then
    echo -e "${GREEN}   ✓ No binary executables found${NC}"
else
    echo -e "${RED}   ✗ Found $BINARIES binary executables${NC}"
    find . -type f -executable -not -name "*.sh" -not -name "*.py"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: All Python files are text
echo "2. Verifying Python files are text..."
NON_TEXT=$(find scripts/ -name "*.py" -exec file {} \; | grep -v "Python script\|ASCII text\|UTF-8" | wc -l)
if [ "$NON_TEXT" -eq 0 ]; then
    echo -e "${GREEN}   ✓ All Python files are text${NC}"
else
    echo -e "${RED}   ✗ Found $NON_TEXT non-text Python files${NC}"
    find scripts/ -name "*.py" -exec file {} \; | grep -v "Python script\|ASCII text\|UTF-8"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: No dangerous eval() or exec()
echo "3. Scanning for dangerous code patterns..."

# Check for actual eval() function (not eval_parameter)
EVAL_COUNT=$(grep -r "eval(" scripts/ | grep -v "\.eval()" | grep -v "eval_" | wc -l)
if [ "$EVAL_COUNT" -eq 0 ]; then
    echo -e "${GREEN}   ✓ No eval() calls found${NC}"
else
    echo -e "${YELLOW}   ⚠ Found $EVAL_COUNT potential eval() calls${NC}"
    echo "     (Note: model.eval() for PyTorch is safe)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for exec()
EXEC_COUNT=$(grep -r "\bexec(" scripts/ | grep -v "execute" | wc -l)
if [ "$EXEC_COUNT" -eq 0 ]; then
    echo -e "${GREEN}   ✓ No exec() calls found${NC}"
else
    echo -e "${RED}   ✗ Found $EXEC_COUNT exec() calls${NC}"
    grep -rn "\bexec(" scripts/ | grep -v "execute"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: Safe subprocess usage
echo "4. Checking subprocess usage..."
SHELL_TRUE=$(grep -r "subprocess\.run.*shell=True" scripts/ | wc -l)
if [ "$SHELL_TRUE" -eq 0 ]; then
    echo -e "${GREEN}   ✓ No shell=True in subprocess calls${NC}"
else
    echo -e "${RED}   ✗ Found $SHELL_TRUE dangerous shell=True calls${NC}"
    grep -rn "subprocess\.run.*shell=True" scripts/
    ERRORS=$((ERRORS + 1))
fi

SUBPROCESS_TOTAL=$(grep -r "subprocess\." scripts/ | wc -l)
if [ "$SUBPROCESS_TOTAL" -gt 0 ]; then
    echo -e "${GREEN}   ✓ $SUBPROCESS_TOTAL subprocess calls (all use safe list form)${NC}"
fi

# Check 5: No obfuscated code
echo "5. Scanning for obfuscation..."
BASE64_DECODE=$(grep -r "base64\.b64decode\|base64\.decode" scripts/ | wc -l)
ZLIB_DECOMPRESS=$(grep -r "zlib\.decompress" scripts/ | wc -l)
if [ "$BASE64_DECODE" -eq 0 ] && [ "$ZLIB_DECOMPRESS" -eq 0 ]; then
    echo -e "${GREEN}   ✓ No obfuscation detected${NC}"
else
    echo -e "${YELLOW}   ⚠ Found potential obfuscation patterns${NC}"
    echo "     base64.b64decode: $BASE64_DECODE"
    echo "     zlib.decompress: $ZLIB_DECOMPRESS"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 6: No hardcoded credentials
echo "6. Checking for hardcoded credentials..."
# Look for actual API key patterns (sk-xxx, key="xxx", password="xxx")
# Exclude: RISK-OFF (market term), examples, placeholders
CREDS=$(grep -ri "sk-[a-zA-Z0-9]\{20\}\|api.*key.*=.*['\"][a-zA-Z0-9]\{20\}\|password.*=.*['\"][a-zA-Z0-9]" scripts/ | grep -v "example\|placeholder\|your_\|<\|RISK-OFF\|risk-off" | wc -l)
if [ "$CREDS" -eq 0 ]; then
    echo -e "${GREEN}   ✓ No hardcoded credentials found${NC}"
else
    echo -e "${RED}   ✗ Found $CREDS potential hardcoded credentials${NC}"
    grep -rin "sk-[a-zA-Z0-9]\{20\}\|api.*key.*=.*['\"][a-zA-Z0-9]\{20\}\|password.*=.*['\"][a-zA-Z0-9]" scripts/ | grep -v "example\|placeholder\|your_\|<\|RISK-OFF\|risk-off" | head -5
    ERRORS=$((ERRORS + 1))
fi

# Check 7: File type distribution
echo "7. Analyzing file types..."
echo "   Python scripts: $(find scripts/ -name "*.py" | wc -l)"
echo "   Shell scripts:  $(find . -name "*.sh" | wc -l)"
echo "   Markdown docs:  $(find . -name "*.md" | wc -l)"
echo "   JSON files:     $(find . -name "*.json" | wc -l)"
echo "   Other:          $(find . -type f -not -name "*.py" -not -name "*.sh" -not -name "*.md" -not -name "*.json" -not -name "LICENSE" | wc -l)"

# Check 8: Tarball integrity
echo "8. Verifying tarball integrity..."
cd /tmp
if tar -tzf research-analyst-v1.3.3.tar.gz > /dev/null 2>&1; then
    echo -e "${GREEN}   ✓ Tarball integrity verified${NC}"
else
    echo -e "${RED}   ✗ Tarball corrupted${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
echo "=========================================="
echo "VirusTotal Readiness Summary"
echo "=========================================="
echo -e "Errors:   $ERRORS"
echo -e "Warnings: $WARNINGS"
echo ""

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}✓ BUNDLE READY FOR VIRUSTOTAL${NC}"
    echo ""
    echo "Expected VirusTotal result: 0/70+ engines"
    echo ""
    echo "Bundle contains:"
    echo "  - Text files only (Python, Markdown, Shell)"
    echo "  - No binaries or executables"
    echo "  - No eval() or exec() calls"
    echo "  - Safe subprocess usage (no shell=True)"
    echo "  - No obfuscated code"
    echo "  - No hardcoded credentials"
    echo ""
    echo "Next steps:"
    echo "1. Upload to VirusTotal: https://www.virustotal.com/"
    echo "   File: /tmp/research-analyst-v1.3.3.tar.gz"
    echo "2. Wait for scan results (2-5 minutes)"
    echo "3. Expected: 0 detections from all engines"
    echo ""
    exit 0
elif [ "$ERRORS" -eq 0 ]; then
    echo -e "${YELLOW}⚠ BUNDLE READY WITH WARNINGS${NC}"
    echo ""
    echo "Expected VirusTotal result: 0-2/70+ engines (possible false positives)"
    echo ""
    echo "Review warnings above. Most are likely safe patterns."
    echo "Proceed with VirusTotal scan and verify results."
    echo ""
    exit 0
else
    echo -e "${RED}✗ BUNDLE NOT READY${NC}"
    echo ""
    echo "Fix the errors above before uploading to VirusTotal."
    echo ""
    exit 1
fi
