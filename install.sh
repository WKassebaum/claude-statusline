#!/bin/bash

# Claude Code Enhanced Statusline Installer
# Installs the enhanced statusline for Claude Code
# Supports both regular and GNU Stow managed installations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Claude Code Enhanced Statusline Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

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

# Function to check if a path is a GNU Stow symlink
is_stow_managed() {
    local path="$1"
    if [ -L "$path" ]; then
        # Check if the symlink points to a dotfiles directory
        local target=$(readlink "$path")
        if [[ "$target" == *"dotfiles"* ]] || [[ "$target" == *"stow"* ]]; then
            return 0
        fi
        # Also check the resolved path
        local resolved=$(readlink -f "$path" 2>/dev/null || echo "")
        if [[ "$resolved" == *"dotfiles"* ]] || [[ "$resolved" == *"stow"* ]]; then
            return 0
        fi
    fi
    return 1
}

# Detect if using GNU Stow
USING_STOW=false
STOW_BASE_DIR=""
STOW_PACKAGE=""

if is_stow_managed "$CLAUDE_DIR" || is_stow_managed "$CLAUDE_SETTINGS"; then
    USING_STOW=true
    echo -e "${BLUE}🔗 GNU Stow installation detected${NC}"
    
    # Try to determine the stow directory structure
    if [ -L "$CLAUDE_SETTINGS" ]; then
        STOW_TARGET=$(readlink -f "$CLAUDE_SETTINGS" 2>/dev/null)
        # Extract the dotfiles base directory (e.g., /Users/wrk/dotfiles)
        if [[ "$STOW_TARGET" =~ (.*/dotfiles)/([^/]+)/.claude/settings.json ]]; then
            STOW_BASE_DIR="${BASH_REMATCH[1]}"
            STOW_PACKAGE="${BASH_REMATCH[2]}"
            echo -e "${GREEN}✓${NC} Stow base directory: $STOW_BASE_DIR"
            echo -e "${GREEN}✓${NC} Stow package: $STOW_PACKAGE"
        fi
    elif [ -L "$CLAUDE_DIR" ]; then
        STOW_TARGET=$(readlink -f "$CLAUDE_DIR" 2>/dev/null)
        if [[ "$STOW_TARGET" =~ (.*/dotfiles)/([^/]+)/.claude ]]; then
            STOW_BASE_DIR="${BASH_REMATCH[1]}"
            STOW_PACKAGE="${BASH_REMATCH[2]}"
            echo -e "${GREEN}✓${NC} Stow base directory: $STOW_BASE_DIR"
            echo -e "${GREEN}✓${NC} Stow package: $STOW_PACKAGE"
        fi
    fi
    
    if [ -z "$STOW_BASE_DIR" ]; then
        echo -e "${YELLOW}⚠${NC} Could not determine Stow structure automatically"
        echo -n "Enter your dotfiles directory path (e.g., /Users/you/dotfiles): "
        read -r STOW_BASE_DIR
        echo -n "Enter the Stow package name for Claude (e.g., claude): "
        read -r STOW_PACKAGE
    fi
    
    # Set the actual target directory for Stow installations
    ACTUAL_CLAUDE_DIR="$STOW_BASE_DIR/$STOW_PACKAGE/.claude"
    ACTUAL_SETTINGS="$ACTUAL_CLAUDE_DIR/settings.json"
else
    echo -e "${GREEN}✓${NC} Standard installation detected"
    ACTUAL_CLAUDE_DIR="$CLAUDE_DIR"
    ACTUAL_SETTINGS="$CLAUDE_SETTINGS"
fi

# Create .claude directory if it doesn't exist
if [ ! -d "$ACTUAL_CLAUDE_DIR" ]; then
    echo -e "${YELLOW}→${NC} Creating $ACTUAL_CLAUDE_DIR directory..."
    mkdir -p "$ACTUAL_CLAUDE_DIR"
fi

# Detect Claude Code version and choose appropriate script
CLAUDE_VERSION=""
if command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
    echo -e "${GREEN}✓${NC} Claude Code version: $CLAUDE_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Could not detect Claude Code version, defaulting to legacy script"
fi

# Choose the appropriate script based on version
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_SCRIPT="claude-statusline.py"  # Default to legacy

if [ -n "$CLAUDE_VERSION" ]; then
    # Parse version numbers for comparison
    IFS='.' read -r major minor patch <<< "$CLAUDE_VERSION"
    
    # Use v1092 script for version 1.0.92 and later
    if [ "$major" -gt 1 ] || ([ "$major" -eq 1 ] && [ "$minor" -gt 0 ]) || ([ "$major" -eq 1 ] && [ "$minor" -eq 0 ] && [ "$patch" -ge 92 ]); then
        SOURCE_SCRIPT="claude-statusline-v1092.py"
        echo -e "${BLUE}→${NC} Using enhanced v1.0.92+ compatible script"
    else
        echo -e "${BLUE}→${NC} Using legacy script for v1.0.88 and earlier"
    fi
fi

# For Stow, install to the actual dotfiles location
if [ "$USING_STOW" = true ]; then
    STATUSLINE_SCRIPT="$ACTUAL_CLAUDE_DIR/claude-statusline.py"
    STATUSLINE_PATH_IN_SETTINGS="$CLAUDE_DIR/claude-statusline.py"  # This is what settings.json should reference
else
    STATUSLINE_SCRIPT="$ACTUAL_CLAUDE_DIR/claude-statusline.py"
    STATUSLINE_PATH_IN_SETTINGS="$STATUSLINE_SCRIPT"
fi

echo -e "${YELLOW}→${NC} Installing statusline script ($SOURCE_SCRIPT)..."
if [ ! -f "$SCRIPT_DIR/$SOURCE_SCRIPT" ]; then
    echo -e "${RED}❌ Error: $SOURCE_SCRIPT not found${NC}"
    echo "Available scripts in $SCRIPT_DIR:"
    ls -la "$SCRIPT_DIR"/*.py 2>/dev/null || echo "No Python scripts found"
    exit 1
fi

cp "$SCRIPT_DIR/$SOURCE_SCRIPT" "$STATUSLINE_SCRIPT"
chmod +x "$STATUSLINE_SCRIPT"
echo -e "${GREEN}✓${NC} Statusline script installed to $STATUSLINE_SCRIPT"

# Backup existing settings if they exist
if [ -f "$ACTUAL_SETTINGS" ]; then
    BACKUP_FILE="$ACTUAL_SETTINGS.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}→${NC} Backing up existing settings to $BACKUP_FILE"
    cp "$ACTUAL_SETTINGS" "$BACKUP_FILE"
fi

# Create or update settings.json
echo -e "${YELLOW}→${NC} Updating Claude settings..."

if [ -f "$ACTUAL_SETTINGS" ]; then
    # Check if settings already has statusLine configuration
    if python3 -c "import json; data=json.load(open('$ACTUAL_SETTINGS')); exit(0 if 'statusLine' in data else 1)" 2>/dev/null; then
        echo -e "${YELLOW}!${NC} Existing statusLine configuration found"
        echo -n "Do you want to replace it? (y/n): "
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            # Update existing settings with statusLine
            python3 << EOF
import json
with open('$ACTUAL_SETTINGS', 'r') as f:
    data = json.load(f)
data['statusLine'] = {
    'type': 'command',
    'command': 'python3 $STATUSLINE_PATH_IN_SETTINGS'
}
with open('$ACTUAL_SETTINGS', 'w') as f:
    json.dump(data, f, indent=2)
EOF
            echo -e "${GREEN}✓${NC} Updated existing statusLine configuration"
        else
            echo -e "${YELLOW}→${NC} Keeping existing statusLine configuration"
        fi
    else
        # Add statusLine to existing settings
        python3 << EOF
import json
with open('$ACTUAL_SETTINGS', 'r') as f:
    data = json.load(f)
data['statusLine'] = {
    'type': 'command',
    'command': 'python3 $STATUSLINE_PATH_IN_SETTINGS'
}
with open('$ACTUAL_SETTINGS', 'w') as f:
    json.dump(data, f, indent=2)
EOF
        echo -e "${GREEN}✓${NC} Added statusLine configuration to existing settings"
    fi
else
    # Create new settings file
    cat > "$ACTUAL_SETTINGS" << EOF
{
  "statusLine": {
    "type": "command",
    "command": "python3 $STATUSLINE_PATH_IN_SETTINGS"
  }
}
EOF
    echo -e "${GREEN}✓${NC} Created new settings file with statusLine configuration"
fi

# If using Stow, re-stow to ensure symlinks are correct
if [ "$USING_STOW" = true ]; then
    echo -e "${YELLOW}→${NC} Re-stowing $STOW_PACKAGE to update symlinks..."
    cd "$STOW_BASE_DIR"
    if command -v stow &> /dev/null; then
        # First try normal re-stow
        if stow -R "$STOW_PACKAGE" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} GNU Stow symlinks updated"
        else
            # If conflicts, ask user about --adopt
            echo -e "${YELLOW}⚠${NC} Stow conflicts detected. This usually means files exist that aren't symlinks."
            echo -n "Use --adopt to take ownership of conflicting files? (y/n): "
            read -r adopt_response
            if [[ "$adopt_response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                stow --adopt -R "$STOW_PACKAGE"
                echo -e "${GREEN}✓${NC} GNU Stow symlinks updated with --adopt"
            else
                echo -e "${YELLOW}⚠${NC} Stow conflicts remain. Please resolve manually:"
                echo "  cd $STOW_BASE_DIR && stow -R $STOW_PACKAGE"
            fi
        fi
    else
        echo -e "${YELLOW}⚠${NC} GNU Stow not found in PATH, please run 'stow -R $STOW_PACKAGE' manually from $STOW_BASE_DIR"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$USING_STOW" = true ]; then
    echo -e "${BLUE}🔗 GNU Stow Installation Summary:${NC}"
    echo "  • Script installed to: $STATUSLINE_SCRIPT"
    echo "  • Settings updated in: $ACTUAL_SETTINGS"
    echo "  • Stow package: $STOW_PACKAGE"
    echo ""
fi

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
echo "  echo '{}' | python3 $STATUSLINE_PATH_IN_SETTINGS"
echo ""
echo "To uninstall, run:"
echo "  ./uninstall.sh"
echo ""