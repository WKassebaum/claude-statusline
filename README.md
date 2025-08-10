# Claude Code Enhanced Statusline 🚀

Fix for Claude Code's statusline that displays accurate token usage, costs, and burn rates.

## 🐛 Problems Fixed

- **Token usage showing 409%** instead of actual ~25%
- **Session cost showing N/A** instead of actual cost
- **Token count showing 819K** instead of actual 22M+
- **Burn rate in $/hr** changed to more useful tokens/min

## ✨ Features

- 📊 **Accurate token usage percentage** - Shows real usage against block limits
- 💰 **Complete cost tracking** - Session, daily, and block costs
- 🔥 **Token burn rate** - Shows tokens/min (K/M formatted)
- ⏱️ **Time remaining** - Accurate time left in current block
- 🎯 **Session detection** - Automatically detects current project session

## 📋 Prerequisites

1. **ccusage** must be installed:
   ```bash
   npm install -g ccusage
   ```

2. **Python 3** must be available

3. **Claude Code** must be installed

## 🚀 Quick Install

1. Clone or download this repository:
   ```bash
   git clone https://github.com/yourusername/claude-statusline-fix.git
   cd claude-statusline-fix
   ```

2. Run the installer:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. The statusline will automatically update in Claude Code!

## 🛠️ Manual Installation

If you prefer to install manually:

1. Copy the statusline script:
   ```bash
   cp claude-statusline.py ~/.claude/claude-statusline.py
   chmod +x ~/.claude/claude-statusline.py
   ```

2. Update your Claude settings (`~/.claude/settings.json`):
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "python3 /Users/YOUR_USERNAME/.claude/claude-statusline.py"
     }
   }
   ```

## 📊 What the Statusline Shows

```
🤖 Opus 4.1 | 💰 $2091.24 session / $54.10 today / $50.26 block (1h 55m left) | 🔥 172K/min | 861.5M tokens | 26.8% used | ~1h55m left
```

- **🤖 Model**: Current Claude model
- **💰 Costs**: 
  - Session: Total cost for current project
  - Today: Total cost for today
  - Block: Current 5-hour block cost
- **🔥 Burn rate**: Tokens consumed per minute
- **Token count**: Total tokens used in session
- **% used**: Percentage of block limit consumed
- **Time left**: Estimated time remaining in block

## 🧪 Testing

To test the statusline manually:
```bash
echo '{}' | python3 ~/.claude/claude-statusline.py
```

## 🗑️ Uninstall

To remove the enhanced statusline:
```bash
./uninstall.sh
```

Or manually remove from `~/.claude/settings.json`:
```json
{
  "statusLine": {
    "type": "command",
    "command": "YOUR_OLD_COMMAND_HERE"
  }
}
```

## 🤝 Contributing

Found a bug or want to add a feature? Pull requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 How It Works

The script:
1. Queries `ccusage` for current session, daily, and block data
2. Parses the JSON output to extract relevant metrics
3. Calculates accurate percentages based on actual block limits (97.6M tokens)
4. Formats the output in a concise, readable statusline
5. Returns the formatted string to Claude Code

## 🐞 Troubleshooting

### Statusline shows "Status unavailable"
- Check that `ccusage` is installed: `which ccusage`
- Verify Python 3 is available: `which python3`
- Test manually: `echo '{}' | python3 ~/.claude/claude-statusline.py`

### Session shows N/A
- The script looks for a session matching your current working directory
- Ensure you're in a project directory that has Claude Code activity

### Wrong percentages
- The script assumes a standard 5-hour block limit of 97.6M tokens
- Different model tiers may have different limits

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built for the Claude Code community
- Uses the excellent [ccusage](https://github.com/javimosch/ccusage) tool
- Inspired by the need for accurate usage tracking

## 📧 Support

Having issues? Please open a GitHub issue with:
- Your Claude Code version
- Output of `ccusage --version`
- Error messages (if any)
- Output of manual test command

---

Made with ❤️ for more accurate Claude Code usage tracking