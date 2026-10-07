# Claude Code Enhanced Statusline

Enhanced statusline for Claude Code that shows context usage, session cost, subscription rate-limit usage, and optional codeindex status. Everything is read from the JSON Claude Code passes on stdin, so a refresh takes ~0.1s and needs no external tools. Compatible with all Claude Code versions including v1.0.92+.

## ✨ Features

- 📊 **Context usage** - Tokens used against the context window, color-coded
- 💰 **Session cost** - From Claude Code's own `cost.total_cost_usd`
- ⏳ **Rate limits** - 5-hour and 7-day usage with time until reset (Pro/Max subscribers)
- 🔍 **Codeindex integration** (optional) - Show active codebase indexing status
- ⚠️ **Context limit warnings** - Visual indicator when the context window is nearly full

## 🔄 Version Compatibility

This project provides **two statusline scripts** for different Claude Code versions:

| Claude Code Version | Script | Features |
|---------------------|--------|----------|
| **v1.0.92+** (Latest) | `claude-statusline-v1092.py` | ✅ Full v1.0.92+ JSON support<br>✅ Context limit warnings<br>✅ Enhanced error handling |
| **v1.0.88 and earlier** | `claude-statusline.py` | ✅ Legacy JSON support<br>✅ Basic cost tracking<br>✅ Codeindex integration<br>❌ No context warnings |

**The installer automatically selects the correct script** for your Claude Code version. For v1.0.92+, it uses the enhanced v1092 script.

## 📋 Prerequisites

No external usage tool is needed. Earlier versions shelled out to `ccusage` three times per refresh; each run re-reads every transcript under `~/.claude/projects`, which took 5-13s and several CPU cores per refresh once transcripts grew past ~1 GB.

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
🤖 Opus 5.5 | 🌿 main | 💰 $3.46 session | ⏳ 5h 24% (2h12m) / 7d 81% (3d3h) | 📊 85.0K/200.0K (42.5%)
```

**With codeindex integration** (when available):
```
🤖 Opus 5.5 | 🔍 ✅ claude-codeindex | 💰 $3.46 session | ⏳ 5h 24% (2h12m) / 7d 81% (3d3h) | 📊 85.0K/200.0K (42.5%)
```

The `⏳` segment appears only for claude.ai Pro/Max subscribers, and only after the session's first API response. The `📊` segment appears once Claude Code reports context usage.

### What Each Field Shows

- **Model**: Currently active Claude model (Opus 4.1)
- **Codeindex** (optional): Current project indexing status
  - `🔍 ✅ project-name` - Project is fully indexed
  - `🔍 ❌ project-name` - Project not indexed  
  - `🔍 🔄 (42%) project-name` - Currently indexing (42% complete)
  - `🔍 ❌ service down` - Service unavailable
  - (not shown) - codeindex not installed (graceful fallback)
- **Session cost**: Claude Code's estimated cost for this session (`cost.total_cost_usd`)
- **Rate limits**: 5-hour and 7-day usage percentage, with time until each window resets
- **Context**: Tokens in the context window, and the percentage used

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
1. Read the JSON Claude Code passes on stdin (`model`, `cost`, `context_window`, `rate_limits`)
2. Add git branch and optional codeindex status
3. Format output optimized for terminal display

### Version-Specific Differences

**claude-statusline-v1092.py (v1.0.92+):**
- Enhanced JSON input parsing for new Claude Code format
- Supports `workspace.current_dir` and `cost.total_cost_usd` fields
- Detects `exceeds_200k_tokens` for context limit warnings
- Enhanced model detection with `display_name` field support
- Robust error handling with graceful fallbacks

**claude-statusline.py (Legacy):**
- Original JSON input format support
- Basic cost tracking and codeindex integration
- Simpler error handling

## 🐞 Troubleshooting

**Statusline shows "Status unavailable"**
- Check Python 3: `which python3`
- Test manually with the command above

**Session shows N/A**
- Claude Code has not reported a cost yet; it appears after the first API response

**No ⏳ rate-limit segment**
- Only shown for claude.ai Pro/Max subscribers, after the session's first API response
- API-key sessions have no rate-limit windows to show

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

**Context warning not showing (v1.0.92+)**
- Ensure you're using `claude-statusline-v1092.py`
- Context warnings only appear when exceeding 200k tokens
- Feature is only available in Claude Code v1.0.88+

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
- Error messages
- Manual test output