#!/usr/bin/env bash
# Test script to verify context window data parsing from Claude Code

echo "Testing context window integration..."
echo ""

# Test 1: Simulate Claude Code JSON with context data
echo "Test 1: Full context data from Claude Code"
echo '{
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
}' | python3 claude-statusline.py
echo ""

# Test 2: Simulate with different model and higher usage
echo "Test 2: Opus 4.1 with higher context usage"
echo '{
  "hook_event_name": "Status",
  "model": {
    "id": "claude-opus-4-1",
    "display_name": "Opus 4.1",
    "context_window_tokens": 200000
  },
  "context": {
    "used_tokens": 156420,
    "usage_percent": 78
  }
}' | python3 claude-statusline.py
echo ""

# Test 3: Empty JSON (should fallback to ccusage)
echo "Test 3: Empty JSON (fallback to ccusage)"
echo '{}' | python3 claude-statusline.py
echo ""

# Test 4: Simulate this actual session's context
echo "Test 4: Current session context (simulated)"
echo '{
  "hook_event_name": "Status",
  "model": {
    "id": "claude-sonnet-4-5-20250929",
    "display_name": "Sonnet 4.5",
    "context_window_tokens": 200000
  },
  "context": {
    "used_tokens": 68000,
    "usage_percent": 34
  }
}' | python3 claude-statusline.py
echo ""

echo "All tests completed!"
