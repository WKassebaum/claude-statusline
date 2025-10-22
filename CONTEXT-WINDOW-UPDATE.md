# Context Window Integration - Update Summary

## What Changed

Your colleague was **absolutely correct**! Claude Code provides real-time context usage data through its statusline API hook.

### The Discovery

Claude Code sends JSON data via stdin to your statusline script with this structure:

```json
{
  "hook_event_name": "Status",
  "model": {
    "id": "claude-sonnet-4-5-20250929",
    "display_name": "Sonnet 4.5",
    "context_window_tokens": 200000
  },
  "context": {
    "used_tokens": 84217,
    "usage_percent": 42
  }
}
```

### What We Were Missing

Our script was **already reading JSON from stdin** (line 554-562), but:
- ✅ We were parsing `model` data for model detection
- ❌ We were **ignoring** the `context` data completely!
- ❌ We were using `ccusage` estimates instead of actual values

### The Fix

**Priority 1**: Parse Claude Code's actual context data:
```python
# PRIORITY 1: Check for real context data from Claude Code's JSON input
if 'context' in claude_data:
    context_data = claude_data['context']
    if isinstance(context_data, dict):
        real_tokens = context_data.get('used_tokens')
        context_usage_percent = context_data.get('usage_percent')

if 'model' in claude_data and isinstance(claude_data['model'], dict):
    context_window_tokens = claude_data['model'].get('context_window_tokens')
```

**Priority 2**: Display the context window information:
```python
if real_tokens is not None and context_window_tokens is not None:
    # We have actual context data from Claude Code!
    tokens_str = f"📊 {format_number(real_tokens)}/{format_number(context_window_tokens)}"
    if context_usage_percent is not None:
        tokens_str += f" ({context_usage_percent}%)"
```

## New Display Format

### Before (using ccusage estimates):
```
🤖 Sonnet 4.5 | ... | 0 tokens | ...
```

### After (using Claude Code's actual data):
```
🤖 Sonnet 4.5 | ... | 📊 84.2K/200.0K (42%) | ...
```

The new format shows:
- **📊** Context usage icon
- **84.2K** = Current tokens used (actual from Claude Code)
- **200.0K** = Total context window size
- **(42%)** = Usage percentage

## Benefits

1. **Accuracy**: No more estimates - this is the **actual** token count Claude Code is tracking
2. **Context Awareness**: You can see exactly how much context window is available
3. **Real-time**: Updated every few hundred milliseconds by Claude Code
4. **Fallback**: Still uses ccusage if Claude Code data isn't available

## Testing

Run the test script to verify:
```bash
./test-context-window.sh
```

Expected output shows the context window data in all test scenarios.

## Implementation Details

**Files Modified:**
- `claude-statusline.py` (lines 332-372, 537-549)

**New Dependencies:** None (uses existing JSON parsing)

**Backward Compatibility:** ✅ Falls back to ccusage when context data unavailable

## Credit

Thanks to your colleague for discovering this feature in Claude Code's documentation!

**Reference:**
- [Claude Code Status Line Documentation](https://docs.claude.com/en/docs/claude-code/statusline)
- [Context Window Details](https://1ar.io/p/custom-claude-code-statusline-track-context-and-current-directory/)
