#!/bin/bash

# Claude Code Enhanced Statusline Installer
# Installs the enhanced statusline for Claude Code

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Claude Code Enhanced Statusline Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if ccusage is installed
if ! command -v ccusage &> /dev/null; then
    echo -e "${RED}❌ Error: ccusage is not installed${NC}"
    echo ""
    echo "Please install ccusage first:"
    echo "  npm install -g ccusage"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} ccusage is installed"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 is not installed${NC}"
    echo "Please install Python 3 first"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 is available"

# Determine Claude configuration directory
CLAUDE_DIR="$HOME/.claude"
CLAUDE_SETTINGS="$CLAUDE_DIR/settings.json"

# Create .claude directory if it doesn't exist
if [ ! -d "$CLAUDE_DIR" ]; then
    echo -e "${YELLOW}→${NC} Creating $CLAUDE_DIR directory..."
    mkdir -p "$CLAUDE_DIR"
fi

# Copy the statusline script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
STATUSLINE_SCRIPT="$CLAUDE_DIR/claude-statusline.py"

echo -e "${YELLOW}→${NC} Installing statusline script..."
cp "$SCRIPT_DIR/claude-statusline.py" "$STATUSLINE_SCRIPT"
chmod +x "$STATUSLINE_SCRIPT"
echo -e "${GREEN}✓${NC} Statusline script installed to $STATUSLINE_SCRIPT"

# Backup existing settings if they exist
if [ -f "$CLAUDE_SETTINGS" ]; then
    BACKUP_FILE="$CLAUDE_SETTINGS.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}→${NC} Backing up existing settings to $BACKUP_FILE"
    cp "$CLAUDE_SETTINGS" "$BACKUP_FILE"
fi

# Create or update settings.json
echo -e "${YELLOW}→${NC} Updating Claude settings..."

if [ -f "$CLAUDE_SETTINGS" ]; then
    # Check if settings already has statusLine configuration
    if python3 -c "import json; data=json.load(open('$CLAUDE_SETTINGS')); exit(0 if 'statusLine' in data else 1)" 2>/dev/null; then
        echo -e "${YELLOW}!${NC} Existing statusLine configuration found"
        echo -n "Do you want to replace it? (y/n): "
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            # Update existing settings with statusLine
            python3 -c "
import json
with open('$CLAUDE_SETTINGS', 'r') as f:
    data = json.load(f)
data['statusLine'] = {
    'type': 'command',
    'command': 'python3 $STATUSLINE_SCRIPT'
}
with open('$CLAUDE_SETTINGS', 'w') as f:
    json.dump(data, f, indent=2)
"
            echo -e "${GREEN}✓${NC} Updated existing statusLine configuration"
        else
            echo -e "${YELLOW}→${NC} Keeping existing statusLine configuration"
        fi
    else
        # Add statusLine to existing settings
        python3 -c "
import json
with open('$CLAUDE_SETTINGS', 'r') as f:
    data = json.load(f)
data['statusLine'] = {
    'type': 'command',
    'command': 'python3 $STATUSLINE_SCRIPT'
}
with open('$CLAUDE_SETTINGS', 'w') as f:
    json.dump(data, f, indent=2)
"
        echo -e "${GREEN}✓${NC} Added statusLine configuration to existing settings"
    fi
else
    # Create new settings file
    cat > "$CLAUDE_SETTINGS" << EOF
{
  "statusLine": {
    "type": "command",
    "command": "python3 $STATUSLINE_SCRIPT"
  }
}
EOF
    echo -e "${GREEN}✓${NC} Created new settings file with statusLine configuration"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "The enhanced statusline will show:"
echo "  • Accurate session costs"
echo "  • Today's total usage"
echo "  • Current block cost and time remaining"
echo "  • Token burn rate (tokens/min)"
echo "  • Correct usage percentage"
echo "  • Estimated time left"
echo ""
echo "The statusline will update automatically in Claude Code."
echo ""
echo "To test the statusline manually, run:"
echo "  echo '{}' | python3 $STATUSLINE_SCRIPT"
echo ""
echo "To uninstall, run:"
echo "  ./uninstall.sh"
echo ""