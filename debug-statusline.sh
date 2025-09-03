#!/bin/bash

# Claude Code Statusline Debugging Script
# Run this to diagnose statusline installation issues

echo "🔍 Claude Code Statusline Debugging"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Check Claude Code installation
echo -e "\n${BLUE}1. Checking Claude Code Installation${NC}"
if command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
    echo -e "${GREEN}✓${NC} Claude Code found: version $CLAUDE_VERSION"
else
    echo -e "${RED}❌${NC} Claude Code not found in PATH"
    echo "   Make sure Claude Code is installed and accessible"
    exit 1
fi

# 2. Check ccusage installation
echo -e "\n${BLUE}2. Checking ccusage Installation${NC}"
if command -v ccusage &> /dev/null; then
    echo -e "${GREEN}✓${NC} ccusage found"
    # Test ccusage
    if ccusage --version &> /dev/null; then
        echo -e "${GREEN}✓${NC} ccusage is working"
    else
        echo -e "${YELLOW}⚠${NC} ccusage found but may have issues"
    fi
else
    echo -e "${RED}❌${NC} ccusage not found"
    echo "   Install with: npm install -g ccusage"
fi

# 3. Check Claude settings directory
echo -e "\n${BLUE}3. Checking Claude Settings Directory${NC}"
CLAUDE_DIR="$HOME/.claude"
if [ -d "$CLAUDE_DIR" ]; then
    echo -e "${GREEN}✓${NC} Claude directory found: $CLAUDE_DIR"
else
    echo -e "${RED}❌${NC} Claude directory not found: $CLAUDE_DIR"
    echo "   Run Claude Code at least once to create this directory"
fi

# 4. Check settings.json
echo -e "\n${BLUE}4. Checking settings.json Configuration${NC}"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    echo -e "${GREEN}✓${NC} settings.json found"
    
    # Check if statusLine is configured
    if grep -q "statusLine" "$SETTINGS_FILE"; then
        echo -e "${GREEN}✓${NC} statusLine configuration found"
        echo "   Current statusLine config:"
        cat "$SETTINGS_FILE" | python3 -m json.tool | grep -A 3 -B 1 "statusLine" || echo "   Could not parse statusLine config"
    else
        echo -e "${RED}❌${NC} statusLine configuration missing from settings.json"
        echo "   Re-run the install script"
    fi
else
    echo -e "${RED}❌${NC} settings.json not found"
    echo "   Re-run the install script to create it"
fi

# 5. Check statusline script
echo -e "\n${BLUE}5. Checking Statusline Script${NC}"
STATUSLINE_SCRIPT="$CLAUDE_DIR/claude-statusline.py"
if [ -f "$STATUSLINE_SCRIPT" ]; then
    echo -e "${GREEN}✓${NC} Statusline script found: $STATUSLINE_SCRIPT"
    
    # Check permissions
    if [ -x "$STATUSLINE_SCRIPT" ]; then
        echo -e "${GREEN}✓${NC} Script is executable"
    else
        echo -e "${YELLOW}⚠${NC} Script is not executable, fixing..."
        chmod +x "$STATUSLINE_SCRIPT"
        echo -e "${GREEN}✓${NC} Fixed permissions"
    fi
    
    # Test script execution
    echo -e "\n${BLUE}6. Testing Script Execution${NC}"
    TEST_JSON='{"input_tokens": 1000, "output_tokens": 100, "model": "claude-3-sonnet-20240229", "cost": 0.05}'
    
    echo "   Testing with sample JSON input..."
    if echo "$TEST_JSON" | python3 "$STATUSLINE_SCRIPT" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Script executes successfully"
    else
        echo -e "${RED}❌${NC} Script execution failed"
        echo "   Error output:"
        echo "$TEST_JSON" | python3 "$STATUSLINE_SCRIPT" 2>&1 | head -5
    fi
else
    echo -e "${RED}❌${NC} Statusline script not found: $STATUSLINE_SCRIPT"
    echo "   Re-run the install script"
fi

# 7. Check for common issues
echo -e "\n${BLUE}7. Common Issue Checks${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python3 available: $PYTHON_VERSION"
else
    echo -e "${RED}❌${NC} Python3 not found"
fi

# Check if Claude Code is currently running
if pgrep -f "claude" > /dev/null; then
    echo -e "${YELLOW}⚠${NC} Claude Code appears to be running"
    echo "   Restart Claude Code to pick up statusline changes"
else
    echo -e "${GREEN}✓${NC} Claude Code not currently running"
fi

echo -e "\n${BLUE}8. Next Steps${NC}"
echo "   1. If all checks pass, restart Claude Code"
echo "   2. If script execution fails, check Python dependencies"
echo "   3. If statusline still doesn't appear, check Claude Code logs"
echo "   4. Try running: echo '{}' | python3 ~/.claude/claude-statusline.py"

echo -e "\n🔍 Debugging complete!"