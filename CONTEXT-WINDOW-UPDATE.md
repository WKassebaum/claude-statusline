# Context Window Integration - Update Summary

## What Changed (v2.0.65+ Schema)

Claude Code provides real-time context usage data through its statusline API hook using the `context_window` object.

### Current JSON Schema (v2.0.65+)

Claude Code sends JSON data via stdin to your statusline script with this structure:

```json
{
  "model": {
    "id": "claude-opus-4-5-20251101",
    "display_name": "Opus 4.5"
  },
  "context_window": {
    "context_window_size": 200000,
    "used_percentage": 42,
    "current_usage": {
      "input_tokens": 75000,
      "output_tokens": 9000,
      "cache_creation_input_tokens": 0,
      "cache_read_input_tokens": 0
    },
    "total_input_tokens": 330050,
    "total_output_tokens": 10614
  },
  "cost": {
    "total_cost_usd": 0.35
  }
}
```

### Important: `current_usage` vs `total_*` Fields

⚠️ **WARNING**: Do NOT use `total_input_tokens` and `total_output_tokens` for context percentage!

- `total_*` fields = **Cumulative session totals** (all tokens ever sent/received)
- `current_usage` = **Actual current context window contents**
- `used_percentage` = **Pre-calculated accurate percentage** (matches `/context` command)

### The Fix

**Priority 1**: Parse Claude Code's `context_window` object:
```python
# Parse context_window object (v2.0.65+ schema)
if 'context_window' in claude_data:
    cw_data = claude_data['context_window']
    if isinstance(cw_data, dict):
        # Get context window size
        context_window_tokens = cw_data.get('context_window_size')

        # Get usage percentage directly if available (most accurate)
        context_usage_percent = cw_data.get('used_percentage')

        # Calculate current tokens from current_usage (not total_*)
        current_usage = cw_data.get('current_usage')
        if isinstance(current_usage, dict) and current_usage:
            input_tokens = current_usage.get('input_tokens', 0) or 0
            output_tokens = current_usage.get('output_tokens', 0) or 0
            cache_creation = current_usage.get('cache_creation_input_tokens', 0) or 0
            cache_read = current_usage.get('cache_read_input_tokens', 0) or 0
            real_tokens = input_tokens + output_tokens + cache_creation + cache_read
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
- `claude-statusline-v1092.py` (lines 182-220 for parsing, 450-470 for display)

**New Dependencies:** None (uses existing JSON parsing)

**Backward Compatibility:** ✅ Falls back to ccusage when context data unavailable

## Credit

Thanks to your colleague for discovering this feature in Claude Code's documentation!

**Reference:**
- [Claude Code Status Line Documentation](https://docs.claude.com/en/docs/claude-code/statusline)
- [Context Window Details](https://1ar.io/p/custom-claude-code-statusline-track-context-and-current-directory/)
