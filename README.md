# Claude Code Enhanced Statusline

Enhanced statusline for Claude Code that provides accurate token usage, costs, and burn rate metrics.

## ✨ Features

- 📊 **Accurate token usage percentage** - Real-time usage against block limits
- 💰 **Complete cost tracking** - Session, daily, and block costs
- 🔥 **Token burn rate** - Displayed in tokens/min with smart K/M/B formatting
- ⏱️ **Time remaining** - Precise time left in current billing block
- 🎯 **Session detection** - Automatic detection of current project session

## 📋 Prerequisites

### Install ccusage

Using Homebrew:
```bash
brew install ccusage
```

Or using npm:
```bash
npm install -g ccusage
```

### Requirements

- Python 3
- Claude Code

## 🚀 Quick Install

```bash
# Clone the repository
git clone https://github.com/WKassebaum/claude-statusline-fix.git
cd claude-statusline-fix

# Run the installer
./install.sh
```

The statusline will automatically update in Claude Code.

## 📊 Statusline Format

```
🤖 Opus 4.1 | 💰 $2091.24 session / $54.10 today / $50.26 block (1h 55m left) | 🔥 172K/min | 861.5M tokens | 26.8% used | ~1h55m left
```

**Components:**
- **Model**: Current Claude model
- **Costs**: Session, daily, and current block costs
- **Burn rate**: Token consumption rate per minute
- **Tokens**: Total session tokens
- **Usage**: Percentage of block limit consumed
- **Time**: Estimated time remaining

## 🛠️ Manual Installation

1. Copy the statusline script:
   ```bash
   cp claude-statusline.py ~/.claude/claude-statusline.py
   chmod +x ~/.claude/claude-statusline.py
   ```

2. Update `~/.claude/settings.json`:
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "python3 /Users/YOUR_USERNAME/.claude/claude-statusline.py"
     }
   }
   ```

## 🧪 Testing

Test the statusline output:
```bash
echo '{}' | python3 ~/.claude/claude-statusline.py
```

## 🗑️ Uninstall

```bash
./uninstall.sh
```

## 📝 Technical Details

The script:
1. Queries `ccusage` for session, daily, and block metrics
2. Parses JSON output and calculates accurate percentages
3. Formats output optimized for terminal display
4. Returns formatted statusline to Claude Code

## 🐞 Troubleshooting

**Statusline shows "Status unavailable"**
- Verify `ccusage` is installed: `which ccusage`
- Check Python 3: `which python3`
- Test manually with the command above

**Session shows N/A**
- Script detects sessions based on current working directory
- Ensure you're in an active project directory

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🤝 Contributing

Pull requests welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For issues, please include:
- Claude Code version
- Output of `ccusage --version`
- Error messages
- Manual test output