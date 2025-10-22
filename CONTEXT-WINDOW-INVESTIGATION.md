# Context Window API Investigation - Results

## TL;DR

**The `context` field with token usage data does NOT exist in Claude Code v2.0.25** (current latest version).

The research about context window APIs in Claude Code's statusline was based on planned/requested features, not currently implemented functionality.

## What We Discovered

### Investigation Process

We created a debug script to capture the actual JSON that Claude Code sends to statusline scripts.

### Actual JSON from Claude Code v2.0.25

```json
{
  "session_id": "2c72b08f-071b-4dc0-96b5-80e0ed8844aa",
  "transcript_path": "/Users/wrk/.claude/projects/...",
  "cwd": "/Users/wrk/WorkDev/MCP-Dev/claude-statusline",
  "model": {
    "id": "claude-sonnet-4-5-20250929",
    "display_name": "Sonnet 4.5"
  },
  "workspace": {
    "current_dir": "/Users/wrk/WorkDev/MCP-Dev/claude-statusline",
    "project_dir": "/Users/wrk/WorkDev/MCP-Dev/claude-statusline"
  },
  "version": "2.0.25",
  "output_style": {
    "name": "default"
  },
  "cost": {
    "total_cost_usd": 0.22473835,
    "total_duration_ms": 17944,
    "total_api_duration_ms": 12916,
    "total_lines_added": 0,
    "total_lines_removed": 0
  },
  "exceeds_200k_tokens": false
}
```

### What's Missing

❌ **No `context` field** with:
- `used_tokens`
- `usage_percent`

❌ **No `context_window_tokens`** in the `model` object

### What IS Available

✅ **Fields we CAN use:**
- `cost.total_cost_usd` - Actual session cost (more accurate than ccusage estimates)
- `cost.total_duration_ms` - Session duration
- `cost.total_api_duration_ms` - Actual API time
- `cost.total_lines_added` - Code changes
- `cost.total_lines_removed` - Code deletions
- `exceeds_200k_tokens` - Boolean flag for context limit warning
- `model.id` and `model.display_name` - Model information
- `session_id` - Unique session identifier

## Code Status

**Current implementation:**
- ✅ Code is written to parse `context` data IF it exists
- ✅ Code gracefully falls back to ccusage when context data unavailable
- ✅ No breaking changes - statusline continues to work as before
- ✅ Future-proof - Will automatically use context data when/if Claude Code adds it

## Possible Enhancements

We could enhance the statusline using the data that IS available:

1. **Use real session cost from Claude Code** instead of ccusage estimates
2. **Show session duration** from the JSON
3. **Display code change metrics** (lines added/removed)
4. **Context warning indicator** using `exceeds_200k_tokens` flag

## Next Steps

### Option 1: Keep as-is
- Code works fine with ccusage fallback
- Future-proof for when/if the feature is added

### Option 2: Enhance with available data
- Use `cost.total_cost_usd` for more accurate session costs
- Add context warning when `exceeds_200k_tokens` is true
- Display session metrics

### Option 3: Monitor for updates
- Watch Claude Code releases for context API addition
- The code is already ready to use it when available

## References

- **Claude Code Version Tested:** 2.0.25 (latest as of 2025-10-22)
- **Debug Log:** `/tmp/claude-statusline-debug.log`
- **Original Research:** Based on https://1ar.io/p/custom-claude-code-statusline-track-context-and-current-directory/

**Note:** The original research may have been referring to:
- A planned feature not yet implemented
- A feature in beta/unreleased versions
- A misinterpretation of available APIs
- Custom implementations not in the official Claude Code release

## Conclusion

While the context window API doesn't exist yet, our investigation revealed valuable data that Claude Code DOES provide. We can use this to improve the statusline in other ways.

The code we wrote is future-proof and will automatically start using context data if/when Claude Code adds it in a future release.
