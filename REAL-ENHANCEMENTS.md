# Real Claude Code API Enhancements

## Summary

While the `context` field with token usage data doesn't exist in Claude Code v2.0.25, we discovered and integrated **actual cost and status data** that Claude Code DOES provide.

## Actual Enhancements Implemented

### 1. Real Session Cost (✅ Implemented)

**Before:** ccusage estimates session cost by summing individual API calls
**After:** Uses actual `cost.total_cost_usd` from Claude Code's JSON

**Benefit:** More accurate session costs without estimation errors

**Example:**
```json
"cost": {
  "total_cost_usd": 0.22473835  // Real cost from Claude Code
}
```

### 2. Context Limit Warning (✅ Implemented)

**Before:** No warning when approaching context limits
**After:** Shows ⚠️ warning icon when `exceeds_200k_tokens` is true

**Benefit:** Immediate visual feedback when context is at capacity

**Display:**
```
🤖 Sonnet 4.5 ⚠️  // When context limit exceeded
🤖 Sonnet 4.5      // Normal operation
```

### 3. Future-Proof for Token Data (✅ Ready)

**Prepared for:** When/if Claude Code adds `context` field with token usage

**Code Ready:**
```python
if 'context' in claude_data:
    real_tokens = context_data.get('used_tokens')
    context_usage_percent = context_data.get('usage_percent')
if 'model' in claude_data:
    context_window_tokens = claude_data['model'].get('context_window_tokens')
```

**Status:** Will automatically activate when Claude Code adds this feature

## Available but Not Yet Used

Claude Code provides additional data we could display:

```json
{
  "cost": {
    "total_duration_ms": 17944,      // Session duration
    "total_api_duration_ms": 12916,  // Actual API time
    "total_lines_added": 0,           // Code changes
    "total_lines_removed": 0          // Code deletions
  },
  "session_id": "unique-id",          // Session identifier
  "transcript_path": "path/to/log"    // Conversation log
}
```

**Possible future enhancements:**
- Session duration timer
- Code change metrics (lines added/removed)
- API efficiency ratio (API time vs total time)

## Technical Implementation

### Priority System

1. **Claude Code actual data** (highest priority)
   - Real session cost from `cost.total_cost_usd`
   - Context warning from `exceeds_200k_tokens`

2. **OTLP proxy metrics** (secondary)
   - Token metrics if available

3. **ccusage estimates** (fallback)
   - Used when Claude Code data unavailable

### Code Changes

**Files modified:**
- `claude-statusline.py` - Main statusline script
- `claude-statusline-v1092.py` - Enhanced v1.0.92+ compatible script

**New features:**
```python
# Parse real cost from Claude Code
if 'cost' in claude_data:
    claude_session_cost = claude_data['cost'].get('total_cost_usd')

# Override ccusage estimates with real data
if claude_session_cost is not None:
    session_cost = claude_session_cost  // More accurate!

# Show context warning
if claude_data.get('exceeds_200k_tokens', False):
    model_display += " ⚠️"
```

## Testing

To verify the enhancements work:

```bash
# Test with simulated Claude Code data
echo '{
  "model": {
    "id": "claude-sonnet-4-5-20250929",
    "display_name": "Sonnet 4.5"
  },
  "cost": {
    "total_cost_usd": 0.25
  },
  "exceeds_200k_tokens": true
}' | python3 ~/.claude/claude-statusline.py
```

**Expected output:**
- Session cost shows $0.25 (from JSON, not ccusage)
- Model display shows ⚠️ warning icon

## Benefits

1. **More Accurate Costs:** Real session costs from Claude Code vs estimates
2. **Better Awareness:** Visual warning when context limit reached
3. **Future-Ready:** Code prepared for token usage API when/if added
4. **Graceful Fallback:** Still works perfectly with ccusage when Claude data unavailable

## Conclusion

While the context window token API doesn't exist yet, we've successfully:
- ✅ Integrated real cost data from Claude Code
- ✅ Added context limit warnings
- ✅ Prepared code for future token usage APIs
- ✅ Improved accuracy of session cost display

The statusline now uses **actual data from Claude Code** where available, with intelligent fallbacks to ensure it always works.

---
*Last Updated: 2025-10-22*
*Claude Code Version: 2.0.25*
