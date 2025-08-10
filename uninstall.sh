#!/bin/bash

# Claude Code Enhanced Statusline Uninstaller
# Removes the enhanced statusline from Claude Code

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Claude Code Enhanced Statusline Uninstaller"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Paths
CLAUDE_DIR="$HOME/.claude"
CLAUDE_SETTINGS="$CLAUDE_DIR/settings.json"
STATUSLINE_SCRIPT="$CLAUDE_DIR/claude-statusline.py"

echo -n "Are you sure you want to uninstall the enhanced statusline? (y/n): "
read -r response
if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}→${NC} Uninstall cancelled"
    exit 0
fi

echo ""

# Remove statusline script
if [ -f "$STATUSLINE_SCRIPT" ]; then
    echo -e "${YELLOW}→${NC} Removing statusline script..."
    rm "$STATUSLINE_SCRIPT"
    echo -e "${GREEN}✓${NC} Removed $STATUSLINE_SCRIPT"
else
    echo -e "${YELLOW}!${NC} Statusline script not found at $STATUSLINE_SCRIPT"
fi

# Update settings.json
if [ -f "$CLAUDE_SETTINGS" ]; then
    echo -e "${YELLOW}→${NC} Updating Claude settings..."
    
    # Check if settings has statusLine configuration
    if python3 -c "import json; data=json.load(open('$CLAUDE_SETTINGS')); exit(0 if 'statusLine' in data else 1)" 2>/dev/null; then
        # Backup before modification
        BACKUP_FILE="$CLAUDE_SETTINGS.uninstall.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$CLAUDE_SETTINGS" "$BACKUP_FILE"
        echo -e "${GREEN}✓${NC} Settings backed up to $BACKUP_FILE"
        
        # Remove statusLine configuration
        python3 -c "
import json
with open('$CLAUDE_SETTINGS', 'r') as f:
    data = json.load(f)
if 'statusLine' in data:
    del data['statusLine']
with open('$CLAUDE_SETTINGS', 'w') as f:
    json.dump(data, f, indent=2)
"
        echo -e "${GREEN}✓${NC} Removed statusLine configuration from settings"
        
        # Check if settings.json is now empty or only has empty object
        if python3 -c "import json; data=json.load(open('$CLAUDE_SETTINGS')); exit(0 if len(data) == 0 else 1)" 2>/dev/null; then
            echo -e "${YELLOW}→${NC} Settings file is now empty"
            echo -n "Do you want to remove the empty settings file? (y/n): "
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                rm "$CLAUDE_SETTINGS"
                echo -e "${GREEN}✓${NC} Removed empty settings file"
            fi
        fi
    else
        echo -e "${YELLOW}!${NC} No statusLine configuration found in settings"
    fi
else
    echo -e "${YELLOW}!${NC} Settings file not found at $CLAUDE_SETTINGS"
fi

# Look for backup files
echo ""
echo -e "${YELLOW}→${NC} Looking for backup files..."
BACKUP_COUNT=$(ls -1 "$CLAUDE_DIR"/settings.json.backup.* 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 0 ]; then
    echo -e "Found $BACKUP_COUNT backup file(s):"
    ls -1t "$CLAUDE_DIR"/settings.json.backup.* | head -5
    echo ""
    echo "To restore a backup, run:"
    echo "  cp BACKUP_FILE $CLAUDE_SETTINGS"
else
    echo -e "${YELLOW}!${NC} No backup files found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Uninstall Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "The enhanced statusline has been removed."
echo "Claude Code will revert to its default statusline behavior."
echo ""
echo "To reinstall, run:"
echo "  ./install.sh"
echo ""