#!/usr/bin/env python3
"""
Debug script to see what JSON Claude Code is actually sending to the statusline
"""
import sys
import json
from datetime import datetime

# Log the input to a file
log_file = "/tmp/claude-statusline-debug.log"

with open(log_file, "a") as f:
    f.write(f"\n{'='*60}\n")
    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
    f.write(f"{'='*60}\n")

    # Read stdin
    input_data = sys.stdin.read()
    f.write(f"Raw input length: {len(input_data)} bytes\n")
    f.write(f"Raw input:\n{input_data}\n")

    # Try to parse as JSON
    if input_data:
        try:
            data = json.loads(input_data)
            f.write(f"\nParsed JSON (pretty):\n")
            f.write(json.dumps(data, indent=2))
            f.write("\n")

            # Check for context data
            if 'context' in data:
                f.write(f"\n✅ Found 'context' field!\n")
                f.write(f"   used_tokens: {data['context'].get('used_tokens')}\n")
                f.write(f"   usage_percent: {data['context'].get('usage_percent')}\n")
            else:
                f.write(f"\n❌ No 'context' field in JSON\n")
                f.write(f"   Available keys: {list(data.keys())}\n")

            if 'model' in data:
                f.write(f"\n✅ Found 'model' field!\n")
                model_data = data['model']
                if isinstance(model_data, dict):
                    f.write(f"   context_window_tokens: {model_data.get('context_window_tokens')}\n")
                    f.write(f"   id: {model_data.get('id')}\n")
                else:
                    f.write(f"   model is a string: {model_data}\n")
            else:
                f.write(f"\n❌ No 'model' field in JSON\n")

        except json.JSONDecodeError as e:
            f.write(f"\n❌ JSON parse error: {e}\n")
    else:
        f.write(f"\n❌ No input received (empty stdin)\n")

# Print a simple output for the statusline
print("DEBUG MODE - Check /tmp/claude-statusline-debug.log")
