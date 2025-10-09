#!/usr/bin/env python3
"""
Claude Code Enhanced Statusline for v1.0.92+
Compatible with latest Claude Code JSON input format including new fields.

Author: Claude Code Community
License: MIT
"""

import subprocess
import json
import sys
from datetime import datetime
import os
import re

def format_number(num):
    """Format number with K/M/B suffix"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)


def get_ccusage_data():
    """Get usage data from ccusage tool with improved error handling"""
    try:
        # Get block data for current session
        blocks_result = subprocess.run(
            ["ccusage", "blocks", "--json", "--offline"],
            capture_output=True,
            text=True,
            timeout=10
        )
        blocks_data = json.loads(blocks_result.stdout) if blocks_result.returncode == 0 else {}
        
        # Get session data
        session_result = subprocess.run(
            ["ccusage", "session", "--json", "--offline"],
            capture_output=True,
            text=True,
            timeout=10
        )
        session_data = json.loads(session_result.stdout) if session_result.returncode == 0 else {}
        
        # Get daily data for today
        daily_result = subprocess.run(
            ["ccusage", "daily", "--json", "--offline"],
            capture_output=True,
            text=True,
            timeout=10
        )
        daily_data = json.loads(daily_result.stdout) if daily_result.returncode == 0 else {}
        
        return blocks_data, session_data, daily_data
    except Exception:
        return {}, {}, {}

def get_current_working_directory():
    """Get the current working directory from environment or pwd"""
    try:
        # Try to get from PWD environment variable first
        cwd = os.environ.get('PWD', '')
        if not cwd:
            # Fallback to actual cwd
            cwd = os.getcwd()
        return cwd
    except:
        return None

def get_codeindex_status():
    """Get codeindex status with robust error handling"""
    try:
        # Get current directory info
        cwd = get_current_working_directory()
        if not cwd:
            return None
        
        # Check collections with shorter timeout
        collections_result = subprocess.run(
            ["curl", "-s", "--max-time", "1", "http://localhost:6333/collections"],
            capture_output=True,
            text=True,
            timeout=1.5
        )
        
        if collections_result.returncode == 0 and collections_result.stdout:
            try:
                collections_data = json.loads(collections_result.stdout)
                if 'result' in collections_data and 'collections' in collections_data['result']:
                    collections = collections_data['result']['collections']
                    collection_names = [col.get('name', '') for col in collections]
                    
                    # Walk up directory tree to find indexed parent projects
                    path_parts = cwd.rstrip('/').split('/')
                    for i in range(len(path_parts), 0, -1):
                        # Get directory name at this level
                        dir_name = path_parts[i-1]
                        # Lowercase to match codeindex naming (context.ts:1140)
                        expected_collection = f"codeindex-{dir_name}".lower()

                        # Check if this directory level has a collection
                        if expected_collection in collection_names:
                            return f"✅ {dir_name}"

                        # Stop at reasonable boundaries (home directory, etc.)
                        if dir_name in ['Users', 'home', 'root'] or len(path_parts[:i]) < 3:
                            break

                    # Check if any codeindex collections exist at all
                    has_any_codeindex = any(
                        name.startswith('codeindex-')
                        for name in collection_names
                    )
                    
                    if has_any_codeindex:
                        # Use the immediate directory name for "not indexed" status
                        current_dir = cwd.split('/')[-1]
                        return f"❌ {current_dir}"
                    else:
                        return "idle"
            except (json.JSONDecodeError, KeyError):
                pass
        
        return None
    except Exception:
        return None

def format_codeindex_status():
    """Format codeindex status for status line with validation"""
    try:
        status = get_codeindex_status()
        if status is None or not isinstance(status, str) or len(status) == 0:
            return None
        # Filter out problematic responses
        if any(word in status.lower() for word in ['undefined', 'error', 'null']):
            return None
        return f"🔍 {status}"
    except Exception:
        return None

def calculate_status(claude_data=None):
    """Calculate the status line values with v1.0.92 compatibility"""
    if claude_data is None:
        claude_data = {}
    
    blocks_data, session_data, daily_data = get_ccusage_data()
    
    # Check for real token metrics from OTLP proxy
    real_tokens = None
    metrics_file = os.path.expanduser('~/.claude/token-metrics.json')
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, 'r') as f:
                metrics_data = json.load(f)
                # Only use metrics if they're recent (within last 60 seconds)
                if 'timestamp' in metrics_data:
                    metrics_time = datetime.fromisoformat(metrics_data['timestamp'])
                    age_seconds = (datetime.now() - metrics_time).total_seconds()
                    if age_seconds < 60:
                        real_tokens = metrics_data.get('totalUsed', 0)
        except:
            pass
    
    # Get current working directory
    cwd = get_current_working_directory()
    
    # Handle new workspace format in v1.0.92+
    if 'workspace' in claude_data:
        workspace_info = claude_data['workspace']
        if isinstance(workspace_info, dict):
            cwd = workspace_info.get('current_dir') or cwd
        # If workspace is not a dict, ignore it
    elif 'cwd' in claude_data:
        cwd = claude_data['cwd']
    
    # Find current active block, or fallback to most recent block
    current_block = None
    block_cost = 0.0
    block_usage_pct = 0.0
    time_remaining_mins = 0
    burn_rate = 0
    hourly_rate = 0.0
    block_tokens = 0
    
    if 'blocks' in blocks_data and blocks_data['blocks']:
        # First try to find an active block
        for block in reversed(blocks_data['blocks']):
            if block.get('isActive'):
                current_block = block
                break
        
        # If no active block, use the most recent non-gap block
        if current_block is None:
            for block in reversed(blocks_data['blocks']):
                if not block.get('isGap', False):
                    current_block = block
                    break
        
        if current_block:
            block_cost = current_block.get('costUSD', 0.0)
            block_tokens = current_block.get('totalTokens', 0)
            
            # Get burn rate (only available for active blocks)
            if 'burnRate' in current_block:
                burn_rate_info = current_block['burnRate']
                if isinstance(burn_rate_info, dict):
                    burn_rate = int(burn_rate_info.get('tokensPerMinute', 0))
                    hourly_rate = burn_rate_info.get('costPerHour', 0.0)
            
            # Get remaining time (only available for active blocks)
            if 'projection' in current_block:
                projection_info = current_block['projection']
                if isinstance(projection_info, dict):
                    time_remaining_mins = projection_info.get('remainingMinutes', 0)
            
            # Calculate usage percentage
            block_limit = 97_675_753  # Standard 5-hour block limit
            block_usage_pct = (block_tokens / block_limit * 100) if block_limit > 0 else 0
    
    # Handle session cost from newer Claude Code versions
    session_cost = 0.0
    session_tokens = 0
    session_found = False
    
    # Try to get session cost from Claude Code's built-in cost tracking (v1.0.85+)
    if 'cost' in claude_data:
        cost_info = claude_data['cost']
        if isinstance(cost_info, dict):
            session_cost = cost_info.get('total_cost_usd', 0.0)
        elif isinstance(cost_info, (int, float)):
            session_cost = float(cost_info)
        else:
            session_cost = 0.0
        session_found = True
    elif 'sessions' in session_data and cwd:
        # Fallback to ccusage session data
        session_id_from_cwd = cwd.replace('/', '-')
        
        for session in session_data['sessions']:
            session_id = session.get('sessionId', '')
            if session_id == session_id_from_cwd:
                session_cost = session.get('totalCost', 0.0)
                session_tokens = session.get('totalTokens', 0)
                session_found = True
                break
            elif cwd and cwd.split('/')[-1] in session_id:
                session_cost = session.get('totalCost', 0.0)
                session_tokens = session.get('totalTokens', 0)
                session_found = True
    
    # Get today's total cost
    today_cost = 0.0
    today_tokens = 0
    if 'daily' in daily_data:
        today = datetime.now().strftime('%Y-%m-%d')
        for day in daily_data['daily']:
            if day.get('date', '') == today:
                today_cost = day.get('totalCost', 0.0)
                today_tokens = day.get('totalTokens', 0)
                break
    
    # Format time remaining
    if time_remaining_mins > 60:
        hours = int(time_remaining_mins / 60)
        mins = int(time_remaining_mins % 60)
        time_remaining = f"{hours}h {mins}m"
    else:
        time_remaining = f"{int(time_remaining_mins)}m"
    
    # Format burn rate as tokens/min
    if burn_rate > 1_000_000:
        burn_str = f"{burn_rate/1_000_000:.1f}M/min"
    elif burn_rate > 1000:
        burn_str = f"{burn_rate/1000:.0f}K/min"
    else:
        burn_str = f"{burn_rate}/min"
    
    # Estimate time left
    time_left = f"~{time_remaining_mins}m" if time_remaining_mins > 0 else "~30m"
    if time_remaining_mins > 60:
        hours = int(time_remaining_mins / 60)
        mins = int(time_remaining_mins % 60)
        time_left = f"~{hours}h{mins}m"
    
    # Enhanced model detection for v1.0.92+
    model = "Claude"  # Default fallback
    
    # Try to get model from Claude Code input (v1.0.85+)
    if 'model' in claude_data and claude_data['model']:
        model_data = claude_data['model']
        model_id = ""
        
        # Handle both string and dict model formats
        if isinstance(model_data, str):
            model_id = model_data
        elif isinstance(model_data, dict):
            # Try display_name first, then other fields
            model_id = model_data.get('display_name') or model_data.get('name') or model_data.get('id', '')
        
        # Parse model name from ID
        if model_id and isinstance(model_id, str):
            model_id_lower = model_id.lower()
            if 'opus-4-1' in model_id_lower or 'opus 4.1' in model_id_lower:
                model = "Opus 4.1"
            elif 'opus-4' in model_id_lower or 'opus 4' in model_id_lower:
                model = "Opus 4"
            elif 'sonnet-4-5' in model_id_lower or 'sonnet 4.5' in model_id_lower:
                model = "Sonnet 4.5"
            elif 'sonnet-4' in model_id_lower or 'sonnet 4' in model_id_lower:
                model = "Sonnet 4"
            elif 'sonnet-3-5' in model_id_lower or 'sonnet 3.5' in model_id_lower or 'sonnet-20241022' in model_id_lower:
                model = "Sonnet 3.5"
            elif 'sonnet' in model_id_lower:
                model = "Sonnet"
            elif 'haiku' in model_id_lower:
                model = "Haiku"
            elif model_id:  # Use the display name or ID as-is if we have it
                model = model_id.replace('claude-', '').replace('-', ' ').title()
    
    # Fallback to ccusage block data for models
    elif current_block and 'models' in current_block and current_block['models']:
        model_names = []
        seen_models = set()
        
        for model_id in reversed(current_block['models']):
            if model_id != '<synthetic>':
                parsed_model = None
                if 'opus-4-1' in model_id:
                    parsed_model = "Opus 4.1"
                elif 'opus-4' in model_id:
                    parsed_model = "Opus 4"
                elif 'sonnet-4-5' in model_id:
                    parsed_model = "Sonnet 4.5"
                elif 'sonnet-4' in model_id:
                    parsed_model = "Sonnet 4"
                elif 'sonnet-3' in model_id:
                    parsed_model = "Sonnet 3.5"
                elif 'haiku' in model_id:
                    parsed_model = "Haiku"
                
                # Add to list if we parsed it and haven't seen it before
                if parsed_model and parsed_model not in seen_models:
                    model_names.append(parsed_model)
                    seen_models.add(parsed_model)
        
        # Join models with commas if multiple
        if model_names:
            model = ", ".join(model_names)
    
    # Handle context warning for v1.0.88+
    context_warning = ""
    if claude_data.get('exceeds_200k_tokens', False):
        context_warning = " ⚠️ Context limit"
    
    # Format costs
    session_str = f"${session_cost:.2f}" if session_found else "N/A"
    today_str = f"${today_cost:.2f}"
    block_str = f"${block_cost:.2f}"
    
    # Format token count - use real tokens if available
    if real_tokens is not None:
        tokens_str = f"📊 {format_number(real_tokens)} tokens (actual)"
    else:
        display_tokens = block_tokens
        tokens_str = f"{format_number(display_tokens)} tokens"
    
    
    # Build status line parts
    status_parts = [
        f"🤖 {model}{context_warning}"
    ]
    
    # Add codeindex status if available
    codeindex_status = format_codeindex_status()
    if codeindex_status:
        status_parts.append(codeindex_status)
    
    
    # Continue with existing parts
    status_parts.extend([
        f"💰 {session_str} session / {today_str} today / {block_str} block ({time_remaining} left)",
        f"🔥 {burn_str}",
        tokens_str,
        f"{block_usage_pct:.1f}% used",
        f"{time_left} left"
    ])
    
    return " | ".join(status_parts)

def main():
    """Main entry point with enhanced error handling"""
    try:
        # Read JSON input from stdin with timeout
        input_data = ""
        try:
            import select
            import sys
            
            # Check if there's input available (with timeout)
            if select.select([sys.stdin], [], [], 0.5)[0]:
                input_data = sys.stdin.read()
        except:
            # Fallback for systems without select
            try:
                input_data = sys.stdin.read()
            except:
                input_data = ""
        
        # Parse JSON input
        if input_data and input_data.strip():
            try:
                claude_data = json.loads(input_data)
            except json.JSONDecodeError:
                claude_data = {}
        else:
            claude_data = {}
        
        # Calculate and output status
        status = calculate_status(claude_data)
        print(status)
        
    except Exception as e:
        # Enhanced fallback status for debugging
        print(f"🤖 Opus 4.1 | 💰 Status unavailable (v{e.__class__.__name__})")

if __name__ == "__main__":
    main()