#!/usr/bin/env python3
"""
Claude Code Enhanced Statusline
Displays accurate token usage, costs, and burn rate for Claude Code sessions.

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
    """Get usage data from ccusage tool"""
    try:
        # Get block data for current session
        blocks_result = subprocess.run(
            ["ccusage", "blocks", "--json", "--offline"],
            capture_output=True,
            text=True,
            timeout=5
        )
        blocks_data = json.loads(blocks_result.stdout) if blocks_result.returncode == 0 else {}
        
        # Get session data
        session_result = subprocess.run(
            ["ccusage", "session", "--json", "--offline"],
            capture_output=True,
            text=True,
            timeout=5
        )
        session_data = json.loads(session_result.stdout) if session_result.returncode == 0 else {}
        
        # Get daily data for today
        daily_result = subprocess.run(
            ["ccusage", "daily", "--json", "--offline"],
            capture_output=True,
            text=True,
            timeout=5
        )
        daily_data = json.loads(daily_result.stdout) if daily_result.returncode == 0 else {}
        
        return blocks_data, session_data, daily_data
    except subprocess.TimeoutExpired:
        return {}, {}, {}
    except Exception as e:
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

def calculate_status():
    """Calculate the status line values"""
    blocks_data, session_data, daily_data = get_ccusage_data()
    
    # Get current working directory
    cwd = get_current_working_directory()
    
    # Find current active block (last block if it's active)
    current_block = None
    block_cost = 0.0
    block_usage_pct = 0.0
    time_remaining_mins = 0
    burn_rate = 0
    hourly_rate = 0.0
    block_tokens = 0
    
    if 'blocks' in blocks_data and blocks_data['blocks']:
        # Get the last block which should be the active one
        last_block = blocks_data['blocks'][-1]
        if last_block.get('isActive'):
            current_block = last_block
            block_cost = current_block.get('costUSD', 0.0)
            block_tokens = current_block.get('totalTokens', 0)
            
            # Get burn rate
            if 'burnRate' in current_block:
                burn_rate = int(current_block['burnRate'].get('tokensPerMinute', 0))
                hourly_rate = current_block['burnRate'].get('costPerHour', 0.0)
            
            # Get remaining time
            if 'projection' in current_block:
                time_remaining_mins = current_block['projection'].get('remainingMinutes', 0)
            
            # Calculate usage percentage (based on 97.6M token limit for 5 hour block)
            block_limit = 97_675_753  # Standard 5-hour block limit
            block_usage_pct = (block_tokens / block_limit * 100) if block_limit > 0 else 0
    
    # Find current session based on working directory
    session_cost = 0.0
    session_tokens = 0
    session_found = False
    
    if 'sessions' in session_data and cwd:
        # Convert cwd to session ID format (replace / with -)
        session_id_from_cwd = cwd.replace('/', '-')
        
        for session in session_data['sessions']:
            session_id = session.get('sessionId', '')
            # Try exact match first
            if session_id == session_id_from_cwd:
                session_cost = session.get('totalCost', 0.0)
                session_tokens = session.get('totalTokens', 0)
                session_found = True
                break
            # Try partial match if cwd is in session_id
            elif cwd and cwd.split('/')[-1] in session_id:
                session_cost = session.get('totalCost', 0.0)
                session_tokens = session.get('totalTokens', 0)
                session_found = True
                # Don't break, keep looking for exact match
    
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
    
    # Estimate time left based on remaining tokens and burn rate
    time_left = f"~{time_remaining_mins}m" if time_remaining_mins > 0 else "~30m"
    if time_remaining_mins > 60:
        hours = int(time_remaining_mins / 60)
        mins = int(time_remaining_mins % 60)
        time_left = f"~{hours}h{mins}m"
    
    # Format the status line
    model = "Opus 4.1"  # Default model - could be detected from data
    
    # Format costs
    session_str = f"${session_cost:.2f}" if session_found else "N/A"
    today_str = f"${today_cost:.2f}"
    block_str = f"${block_cost:.2f}"
    
    # Format token count - use session tokens if available, otherwise block tokens
    display_tokens = session_tokens if session_tokens > 0 else block_tokens
    tokens_str = format_number(display_tokens)
    
    # Build status line
    status_parts = [
        f"🤖 {model}",
        f"💰 {session_str} session / {today_str} today / {block_str} block ({time_remaining} left)",
        f"🔥 {burn_str}",
        f"{tokens_str} tokens",
        f"{block_usage_pct:.1f}% used",
        f"{time_left} left"
    ]
    
    return " | ".join(status_parts)

def main():
    """Main entry point"""
    try:
        # Read JSON input from stdin (from Claude)
        input_data = sys.stdin.read()
        if input_data:
            try:
                claude_data = json.loads(input_data)
            except json.JSONDecodeError:
                claude_data = {}
        else:
            claude_data = {}
        
        # Calculate status
        status = calculate_status()
        
        # Output the status line
        print(status)
        
    except Exception as e:
        # Fallback status on error
        print(f"🤖 Opus 4.1 | 💰 Status unavailable | Error: {str(e)}")

if __name__ == "__main__":
    main()