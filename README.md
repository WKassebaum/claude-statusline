# Claude Code Enhanced Statusline

Enhanced statusline for Claude Code that provides accurate token usage, costs, burn rate metrics, and optional codeindex integration.

## ✨ Features

- 📊 **Accurate token usage percentage** - Real-time usage against block limits
- 💰 **Complete cost tracking** - Session, daily, and block costs
- 🔥 **Token burn rate** - Displayed in tokens/min with smart K/M/B formatting
- ⏱️ **Time remaining** - Precise time left in current billing block
- 🎯 **Session detection** - Automatic detection of current project session
- 🔍 **Codeindex integration** (optional) - Show active codebase indexing status

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
- curl (for optional codeindex integration)

### Optional Dependencies

- **claude-codeindex** - For codebase indexing status display
  - If installed and running, shows active indexing status
  - Gracefully falls back if unavailable
  - No configuration needed - auto-detected

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

**Standard format**:
```
🤖 Opus 4.1 | 💰 $3.25 session / $81.14 today / $77.30 block (1h 14m left) | 🔥 204K/min | 39.5M tokens | 40.4% used | ~1h14m left
```

**With codeindex integration** (when available):
```
🤖 Opus 4.1 | 🔍 ●claude-multi-agent | 💰 $3.25 session / $81.14 today / $77.30 block (1h 14m left) | 🔥 204K/min | 39.5M tokens | 40.4% used | ~1h14m left
```

### What Each Field Shows

- **Model**: Currently active Claude model (Opus 4.1)
- **Codeindex** (optional): Active codebase indexing status
  - `🔍 ●project-name` - Active watcher  
  - `🔍 ⚠️project-name` - Watcher with errors
  - `🔍 idle` - Service available, no active watchers
  - (not shown) - Service unavailable (graceful fallback)
- **Session cost**: Total cost for current working directory session
- **Today's cost**: Total usage for today across all sessions
- **Block cost**: Current 5-hour block usage and time remaining
- **Burn rate**: Token consumption rate in tokens per minute
- **Token count**: Current block tokens (matches ccusage display)
- **Usage %**: Percentage of 97.6M token block limit used
- **Time left**: Estimated time remaining based on burn rate

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

### Testing Codeindex Integration

If you have claude-codeindex installed, you can test the integration:

```bash
# Check if codeindex service is running
curl -s http://localhost:3847/health

# Start codeindex in a project directory
/codeindex:start

# You should see the codeindex status in your statusline:
# 🤖 Opus 4.1 | 🔍 ●your-project-name | 💰 ...
```

## 🔍 Codeindex Integration

The statusline automatically detects and displays codeindex status when available.

### Status Indicators

| Indicator | Meaning | Description |
|-----------|---------|-------------|
| `🔍 ●project-name` | Active | Codeindex is actively watching project |
| `🔍 ⚠️project-name` | Errors | Watcher has errors but still running |
| `🔍 idle` | Available | Service running, no active watchers |
| (not shown) | Unavailable | Service not running (graceful fallback) |

### Benefits

- **At-a-glance status** - See which project is being indexed
- **Error detection** - Immediate notification of indexing issues  
- **Zero configuration** - Works automatically when codeindex available
- **Graceful degradation** - No impact when codeindex unavailable

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

**Codeindex status not showing**
- Check if codeindex service is running: `curl -s http://localhost:3847/health`
- This is normal - codeindex integration is optional
- Statusline works perfectly without codeindex

**Codeindex shows "idle" but I started it**
- Check service status: `curl -s http://localhost:3847/status`
- Ensure you ran `/codeindex:start` in the correct directory
- Service may be starting up - wait 5-10 seconds

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