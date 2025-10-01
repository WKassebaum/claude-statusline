# Claude Code Enhanced Statusline

Enhanced statusline for Claude Code that provides accurate token usage, costs, burn rate metrics, and optional codeindex integration. Compatible with all Claude Code versions including v1.0.92+.

## ✨ Features

- 📊 **Accurate token usage percentage** - Real-time usage against block limits
- 💰 **Complete cost tracking** - Session, daily, and block costs
- 🔥 **Token burn rate** - Displayed in tokens/min with smart K/M/B formatting
- ⏱️ **Time remaining** - Precise time left in current billing block
- 🎯 **Session detection** - Automatic detection of current project session
- 🔍 **Codeindex integration** (optional) - Show active codebase indexing status
- ⚠️ **Context limit warnings** - Visual indicator when exceeding 200k tokens
- 🤖 **Multiple model display** - Shows comma-separated model names when using multiple models

## 🔄 Version Compatibility

This project provides **two statusline scripts** for different Claude Code versions:

| Claude Code Version | Script | Features |
|---------------------|--------|----------|
| **v1.0.92+** (Latest) | `claude-statusline-v1092.py` | ✅ Full v1.0.92+ JSON support<br>✅ Context limit warnings<br>✅ Enhanced error handling<br>✅ Multiple model display<br>✅ All cost tracking features |
| **v1.0.88 and earlier** | `claude-statusline.py` | ✅ Legacy JSON support<br>✅ Basic cost tracking<br>✅ Codeindex integration<br>❌ No context warnings |

**The installer automatically selects the correct script** for your Claude Code version. For v1.0.92+, it uses the enhanced v1092 script.

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

### Option 1: Standard Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/WKassebaum/claude-statusline.git
cd claude-statusline

# Run the installer
./install.sh
```

### Option 2: Binary Installation

Installs to `~/.local/bin` for system-wide access:

```bash
# Clone the repository
git clone https://github.com/WKassebaum/claude-statusline.git
cd claude-statusline

# Run the binary installer
./install-bin.sh
```

The statusline will automatically update in Claude Code.

## 📊 Statusline Format

**Standard format**:
```
🤖 Opus 4.1 | 💰 $3.25 session / $81.14 today / $77.30 block (1h 14m left) | 🔥 204K/min | 39.5M tokens | 40.4% used | ~1h14m left
```

**With multiple models** (v1.0.92+):
```
🤖 Opus 4.1, Sonnet 4 | 💰 $99.52 session / $52.95 today / $78.06 block (1h 40m left) | 🔥 482K/min | 96.5M tokens | 98.8% used | ~1h40m left
```

**With context limit warning** (v1.0.92+):
```
🤖 Opus 4.1 ⚠️ Context limit | 💰 $3.25 session / $81.14 today / $77.30 block (1h 14m left) | 🔥 204K/min | 39.5M tokens | 40.4% used | ~1h14m left
```

**With codeindex integration** (when available):
```
🤖 Opus 4.1 | 🔍 ✅ claude-codeindex | 💰 $3.25 session / $81.14 today / $77.30 block (1h 14m left) | 🔥 204K/min | 39.5M tokens | 40.4% used | ~1h14m left
```

**During active indexing**:
```
🤖 Opus 4.1 | 🔍 🔄 (42%) my-project | 💰 $3.25 session / $81.14 today ...
```

### What Each Field Shows

- **Model**: Currently active Claude model (Opus 4.1)
- **Codeindex** (optional): Current project indexing status
  - `🔍 ✅ project-name` - Project is fully indexed
  - `🔍 ❌ project-name` - Project not indexed  
  - `🔍 🔄 (42%) project-name` - Currently indexing (42% complete)
  - `🔍 ❌ service down` - Service unavailable
  - (not shown) - codeindex not installed (graceful fallback)
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

### For Claude Code v1.0.92+ (Recommended)

1. Copy the v1092 statusline script:
   ```bash
   cp claude-statusline-v1092.py ~/.claude/claude-statusline.py
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

### For Claude Code v1.0.88 and Earlier

1. Copy the legacy statusline script:
   ```bash
   cp claude-statusline.py ~/.claude/claude-statusline.py
   chmod +x ~/.claude/claude-statusline.py
   ```

2. Update `~/.claude/settings.json` (same as above)

> **Note**: The automatic installer detects your Claude Code version and selects the appropriate script. Manual installation is only needed for custom setups.

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
| `🔍 ✅ project-name` | Indexed | Project is fully indexed and ready |
| `🔍 ❌ project-name` | Not Indexed | Project not in the index |
| `🔍 🔄 (23%) project-name` | Indexing | Currently indexing, 23% complete |
| `🔍 🔄 (89%) project-name` | Almost Done | Indexing nearly complete |
| `🔍 ❌ service down` | Service Error | codeindex-service not running |
| (not shown) | Not Installed | codeindex not available (graceful fallback) |

### Benefits

- **Current project awareness** - Shows status of your working directory
- **Real-time progress** - Live percentage updates during indexing
- **Instant feedback** - Know if your project is indexed at a glance  
- **Zero configuration** - Works automatically when codeindex available
- **Graceful degradation** - No impact when codeindex unavailable

### How Progress Tracking Works

The statusline monitors codeindex logs for active indexing operations:
1. Detects `📝 Inserting` messages in recent logs
2. Calculates progress based on insertion activity over time
3. Updates percentage in real-time as indexing proceeds
4. Shows `✅` when complete or `❌` if not indexed

## 🗑️ Uninstall

```bash
./uninstall.sh
```

## 📝 Technical Details

### How It Works

Both scripts follow the same core process:
1. Query `ccusage` for session, daily, and block metrics
2. Parse JSON output and calculate accurate percentages  
3. Format output optimized for terminal display
4. Return formatted statusline to Claude Code

### Version-Specific Differences

**claude-statusline-v1092.py (v1.0.92+):**
- Enhanced JSON input parsing for new Claude Code format
- Supports `workspace.current_dir` and `cost.total_cost_usd` fields
- Detects `exceeds_200k_tokens` for context limit warnings
- Improved block detection logic (active blocks + recent non-gap blocks)
- Longer ccusage timeouts (10s vs 3s) to prevent command failures
- Enhanced model detection with `display_name` field support
- Robust error handling with graceful fallbacks

**claude-statusline.py (Legacy):**
- Original JSON input format support
- Basic cost tracking and codeindex integration
- Shorter timeouts suitable for older ccusage versions
- Simpler error handling

### Cost Tracking Algorithm

The statusline uses a sophisticated cost tracking system:
1. **Session costs**: Matches current directory to ccusage session data
2. **Daily costs**: Aggregates today's usage across all sessions  
3. **Block costs**: Uses most recent active or non-gap block
4. **Time estimates**: Based on current burn rate and remaining block limit

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

**Codeindex shows "❌ project-name" but I started indexing**
- Check service status: `curl -s http://localhost:3847/status`
- Verify collections exist: `curl -s http://localhost:6333/collections`
- Large projects may take time - check progress with `codeindex projects`

**Codeindex shows percentage stuck at same value**
- Normal for large projects - indexing pauses between file batches
- Check activity: `curl -s http://localhost:3847/logs`
- Progress updates when new files are inserted

**Cost tracking shows $0.00 for all values**
- You may be using the wrong script for your Claude Code version
- For v1.0.92+, use `claude-statusline-v1092.py`
- For v1.0.88 and earlier, use `claude-statusline.py`
- ccusage commands may be timing out - the v1092 script has longer timeouts
- Run the installer again to auto-detect your version

**Context warning not showing (v1.0.92+)**
- Ensure you're using `claude-statusline-v1092.py`
- Context warnings only appear when exceeding 200k tokens
- Feature is only available in Claude Code v1.0.88+

**Multiple models not displaying correctly**
- Ensure you're using `claude-statusline-v1092.py` for v1.0.92+
- Legacy script may not properly handle multiple models
- Models should appear comma-separated: "Opus 4.1, Sonnet 4"

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