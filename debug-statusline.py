#!/usr/bin/env python3
"""Debug script to see what data the statusline receives from Claude Code.

Use this to inspect the actual JSON being sent. Configure in settings.json:
{
  "statusLine": {
    "type": "command",
    "command": "python3 /path/to/debug-statusline.py"
  }
}

Output goes to stderr (visible in terminal) while stdout shows in statusline.
"""

import json
import sys
import subprocess
from datetime import datetime

# Read JSON input from stdin
input_data = sys.stdin.read()

# Log to file for persistent debugging
log_file = "/tmp/claude-statusline-debug.log"
with open(log_file, "a") as f:
    f.write(f"\n{'='*80}\n")
    f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
    f.write(f"RAW INPUT:\n{input_data}\n")

print("=" * 80, file=sys.stderr)
print(f"TIMESTAMP: {datetime.now().isoformat()}", file=sys.stderr)
print("STDIN DATA:", file=sys.stderr)
print(input_data, file=sys.stderr)
print("=" * 80, file=sys.stderr)

if input_data:
    try:
        data = json.loads(input_data)
        print("\nPARSED JSON:", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)

        # Highlight context_window data specifically
        if 'context_window' in data:
            print("\n>>> CONTEXT WINDOW DATA:", file=sys.stderr)
            print(json.dumps(data['context_window'], indent=2), file=sys.stderr)

            cw = data['context_window']
            print(f"\n  context_window_size: {cw.get('context_window_size')}", file=sys.stderr)
            print(f"  used_percentage: {cw.get('used_percentage')}", file=sys.stderr)
            if 'current_usage' in cw:
                cu = cw['current_usage']
                total = (cu.get('input_tokens', 0) or 0) + \
                        (cu.get('output_tokens', 0) or 0) + \
                        (cu.get('cache_creation_input_tokens', 0) or 0) + \
                        (cu.get('cache_read_input_tokens', 0) or 0)
                print(f"  current_usage total: {total}", file=sys.stderr)
            print("<<<", file=sys.stderr)
        else:
            print("\n>>> NO context_window IN JSON <<<", file=sys.stderr)

        session_id = data.get('session_id')
        print(f"\nSESSION_ID: {session_id}", file=sys.stderr)

        if session_id:
            # Query CCR
            print(f"\nQuerying CCR for session: {session_id}", file=sys.stderr)
            result = subprocess.run(
                ["curl", "-s", f"http://localhost:3000/api/statusline/usage?sessionId={session_id}"],
                capture_output=True,
                text=True,
                timeout=2
            )

            print(f"\nCCR RESPONSE:", file=sys.stderr)
            print(result.stdout, file=sys.stderr)

            if result.stdout:
                ccr_data = json.loads(result.stdout)
                print(f"\nCCR PARSED:", file=sys.stderr)
                print(json.dumps(ccr_data, indent=2), file=sys.stderr)

        # Also log parsed data to file
        with open(log_file, "a") as f:
            f.write(f"\nPARSED JSON:\n{json.dumps(data, indent=2)}\n")
            if 'context_window' in data:
                f.write(f"\nCONTEXT_WINDOW: {json.dumps(data['context_window'], indent=2)}\n")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)

print(f"\nLog file: {log_file}", file=sys.stderr)

# Output something so Claude Code doesn't error
print("Debug mode - check stderr/log")
