#!/usr/bin/env python3
"""
Claude Code Enhanced Statusline for v1.0.92+
Compatible with latest Claude Code JSON input format including new fields.
Everything comes from the JSON Claude Code passes on stdin; no ccusage dependency.

Author: Claude Code Community
License: MIT
"""

import subprocess
import json
import sys
from datetime import datetime
import os
import re
import time

# Force UTF-8 output so emoji render on Windows (default cp1252 raises
# UnicodeEncodeError). No-op on platforms that are already UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

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


def format_model_name(model_id):
    """Format raw model ID into a friendly display name"""
    if not model_id:
        return None

    model_id_lower = model_id.lower()

    # Anthropic models (order matters - check more specific patterns first)
    if 'opus-5-5' in model_id_lower or 'opus 5.5' in model_id_lower:
        return "Opus 5.5"
    elif 'sonnet-5-5' in model_id_lower or 'sonnet 5.5' in model_id_lower:
        return "Sonnet 5.5"
    elif 'fable-5-1' in model_id_lower or 'fable 5.1' in model_id_lower:
        return "Fable 5.1"
    elif 'haiku-5-5' in model_id_lower or 'haiku 5.5' in model_id_lower:
        return "Haiku 5.5"
    elif 'opus-4-8' in model_id_lower or 'opus 4.8' in model_id_lower:
        return "Opus 4.8"
    elif 'opus-4-7' in model_id_lower or 'opus 4.7' in model_id_lower:
        return "Opus 4.7"
    elif 'opus-4-6' in model_id_lower or 'opus 4.6' in model_id_lower:
        return "Opus 4.6"
    elif 'opus-4-5' in model_id_lower or 'opus 4.5' in model_id_lower:
        return "Opus 4.5"
    elif 'opus-4-1' in model_id_lower or 'opus 4.1' in model_id_lower:
        return "Opus 4.1"
    elif 'opus-4' in model_id_lower or 'opus 4' in model_id_lower:
        return "Opus 4"
    elif 'sonnet-4-7' in model_id_lower or 'sonnet 4.7' in model_id_lower:
        return "Sonnet 4.7"
    elif 'sonnet-4-6' in model_id_lower or 'sonnet 4.6' in model_id_lower:
        return "Sonnet 4.6"
    elif 'sonnet-4-5' in model_id_lower or 'sonnet 4.5' in model_id_lower:
        return "Sonnet 4.5"
    elif 'sonnet-4' in model_id_lower or 'sonnet 4' in model_id_lower:
        return "Sonnet 4"
    elif 'sonnet-3-5' in model_id_lower or 'sonnet 3.5' in model_id_lower or 'sonnet-20241022' in model_id_lower:
        return "Sonnet 3.5"
    elif 'sonnet' in model_id_lower:
        return "Sonnet"
    elif 'haiku-4-5' in model_id_lower or 'haiku 4.5' in model_id_lower:
        return "Haiku 4.5"
    elif 'haiku' in model_id_lower:
        return "Haiku"

    # Google models (order matters - check more specific patterns first)
    elif 'gemini-3.5-pro' in model_id_lower or 'gemini-3-5-pro' in model_id_lower:
        return "Gemini 3.5 Pro"
    elif 'gemini-3.5-flash' in model_id_lower or 'gemini-3-5-flash' in model_id_lower:
        return "Gemini 3.5 Flash"
    elif 'gemini-3.1-pro' in model_id_lower:
        return "Gemini 3.1 Pro"
    elif 'gemini-3-pro' in model_id_lower or 'gemini-3.0-pro' in model_id_lower:
        return "Gemini 3 Pro"
    elif 'gemini-3-flash' in model_id_lower or 'gemini-3.0-flash' in model_id_lower:
        return "Gemini 3 Flash"
    elif 'gemini-2.5-pro' in model_id_lower:
        return "Gemini 2.5 Pro"
    elif 'gemini-2.5-flash-lite' in model_id_lower:
        return "Gemini 2.5 Flash Lite"
    elif 'gemini-2.5-flash' in model_id_lower:
        return "Gemini 2.5 Flash"
    elif 'gemini-2' in model_id_lower:
        return "Gemini 2"
    elif 'gemini' in model_id_lower:
        return "Gemini"

    # xAI models (order matters - check more specific patterns first)
    elif 'grok-4-3' in model_id_lower or 'grok-4.3' in model_id_lower:
        return "Grok 4.3"
    elif 'grok-4-2' in model_id_lower or 'grok-4.2' in model_id_lower:
        return "Grok 4.2 Beta"
    elif 'grok-4-1-fast' in model_id_lower or 'grok-4.1-fast' in model_id_lower:
        return "Grok 4.1 Fast"
    elif 'grok-4-1' in model_id_lower or 'grok-4.1' in model_id_lower:
        return "Grok 4.1"
    elif 'grok-4-fast' in model_id_lower:
        return "Grok 4 Fast"
    elif 'grok-4' in model_id_lower:
        return "Grok 4"
    elif 'grok' in model_id_lower:
        return "Grok"

    # OpenAI models
    elif 'o3' in model_id_lower:
        return "O3"
    elif 'gpt-5-4-pro' in model_id_lower or 'gpt-5.4-pro' in model_id_lower:
        return "GPT-5.4 Pro"
    elif 'gpt-5-4' in model_id_lower or 'gpt-5.4' in model_id_lower:
        return "GPT-5.4"
    elif 'gpt-5-3' in model_id_lower or 'gpt-5.3' in model_id_lower:
        return "GPT-5.3"
    elif 'gpt-5' in model_id_lower:
        return "GPT-5"
    elif 'gpt-4' in model_id_lower:
        return "GPT-4"

    # Generic fallback
    elif 'claude-' in model_id_lower:
        return model_id.replace('claude-', '').replace('-', ' ').title()
    else:
        return model_id.replace('-', ' ').title()


def format_duration(seconds):
    """Format a countdown as 2d4h, 2h14m or 14m"""
    seconds = max(0, int(seconds))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins = rem // 60
    if days:
        return f"{days}d{hours}h"
    if hours:
        return f"{hours}h{mins}m"
    return f"{mins}m"

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

def get_git_branch():
    """Get current git branch with robust error handling"""
    try:
        cwd = get_current_working_directory()
        if not cwd:
            return None

        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=0.5,
            cwd=cwd
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
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
            ["curl", "-s", "--connect-timeout", "0.1", "--max-time", "1", "http://127.0.0.1:6333/collections"],
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

    # PRIORITY 1: Check for real context data from Claude Code's JSON input
    # The context_window object contains the actual context tracking data
    real_tokens = None
    context_window_tokens = None
    context_usage_percent = None
    claude_session_cost = None
    exceeds_context_limit = False

    # NEW: Parse context_window object (v2.0.65+ schema)
    if 'context_window' in claude_data:
        cw_data = claude_data['context_window']
        if isinstance(cw_data, dict):
            # Get context window size
            context_window_tokens = cw_data.get('context_window_size')

            # Get usage percentage directly if available (most accurate)
            context_usage_percent = cw_data.get('used_percentage')

            # Calculate current tokens from current_usage (not total_* which are cumulative)
            current_usage = cw_data.get('current_usage')
            if isinstance(current_usage, dict) and current_usage:
                # Sum all token types that count toward context
                input_tokens = current_usage.get('input_tokens', 0) or 0
                output_tokens = current_usage.get('output_tokens', 0) or 0
                cache_creation = current_usage.get('cache_creation_input_tokens', 0) or 0
                cache_read = current_usage.get('cache_read_input_tokens', 0) or 0
                total = input_tokens + output_tokens + cache_creation + cache_read
                # Only use if we actually got tokens
                if total > 0:
                    real_tokens = total

            # If we don't have current_usage but have percentage and window size, calculate tokens
            if real_tokens is None and context_usage_percent is not None and context_window_tokens is not None:
                real_tokens = int(context_window_tokens * context_usage_percent / 100)

    # LEGACY: Check old 'context' format for backward compatibility
    if real_tokens is None and 'context' in claude_data:
        context_data = claude_data['context']
        if isinstance(context_data, dict):
            # Get actual token usage from Claude Code (legacy format)
            real_tokens = context_data.get('used_tokens')
            context_usage_percent = context_data.get('usage_percent')

    # Get context window size from model info if not already set
    if context_window_tokens is None and 'model' in claude_data and isinstance(claude_data['model'], dict):
        context_window_tokens = claude_data['model'].get('context_window_tokens')

    # Get real cost data from Claude Code (available in v2.0.25+)
    if 'cost' in claude_data and isinstance(claude_data['cost'], dict):
        claude_session_cost = claude_data['cost'].get('total_cost_usd')

    # Check for context limit warning (available in v2.0.25+)
    if claude_data.get('exceeds_200k_tokens', False):
        exceeds_context_limit = True

    # PRIORITY 2: Check for real token metrics from OTLP proxy (fallback)
    if real_tokens is None:
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
    
    session_cost = 0.0
    session_found = False

    # Session cost from Claude Code's built-in cost tracking (v1.0.85+)
    if 'cost' in claude_data:
        cost_info = claude_data['cost']
        if isinstance(cost_info, dict):
            session_cost = cost_info.get('total_cost_usd', 0.0)
        elif isinstance(cost_info, (int, float)):
            session_cost = float(cost_info)
        else:
            session_cost = 0.0
        session_found = True

    if claude_session_cost is not None:
        session_cost = claude_session_cost
        session_found = True

    # Subscription rate-limit windows (Pro/Max only, absent until the first API response)
    rate_limits = claude_data.get('rate_limits')
    if not isinstance(rate_limits, dict):
        rate_limits = {}

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
        
        # Parse model name from ID using format_model_name()
        if model_id and isinstance(model_id, str):
            parsed = format_model_name(model_id)
            if parsed:
                model = parsed
    

    # Handle context warning for v1.0.88+
    # Show warning when exceeds_200k_tokens flag is set OR when usage is >= 75%
    context_warning = ""
    if exceeds_context_limit:
        context_warning = " ⚠️"
    elif context_usage_percent is not None and context_usage_percent >= 75:
        context_warning = " ⚠️"
    
    # Format costs
    session_str = f"${session_cost:.2f}" if session_found else "N/A"
    
    # Format token count and context window
    if real_tokens is not None and context_window_tokens is not None:
        # We have actual context data from Claude Code!
        tokens_str = f"📊 {format_number(real_tokens)}/{format_number(context_window_tokens)}"
        if context_usage_percent is not None:
            # Format percentage - handle both int and float
            if isinstance(context_usage_percent, float) and context_usage_percent != int(context_usage_percent):
                tokens_str += f" ({context_usage_percent:.1f}%)"
            else:
                tokens_str += f" ({int(context_usage_percent)}%)"
    elif context_usage_percent is not None and context_window_tokens is not None:
        # We have percentage and window size but not exact tokens
        tokens_str = f"📊 {int(context_usage_percent)}% of {format_number(context_window_tokens)}"
    elif real_tokens is not None:
        # We have real tokens but not context window
        tokens_str = f"📊 {format_number(real_tokens)} tokens"
    else:
        tokens_str = None


    # Build status line parts
    status_parts = [
        f"🤖 {model}{context_warning}"
    ]

    # Add git branch if available
    git_branch = get_git_branch()
    if git_branch:
        status_parts.append(f"🌿 {git_branch}")

    # Add codeindex status if available
    codeindex_status = format_codeindex_status()
    if codeindex_status:
        status_parts.append(codeindex_status)
    
    
    status_parts.append(f"💰 {session_str} session")

    limit_parts = []
    for key, label in (('five_hour', '5h'), ('seven_day', '7d')):
        window = rate_limits.get(key)
        if not isinstance(window, dict) or window.get('used_percentage') is None:
            continue
        part = f"{label} {window['used_percentage']:.0f}%"
        resets_at = window.get('resets_at')
        if resets_at:
            part += f" ({format_duration(resets_at - time.time())})"
        limit_parts.append(part)
    if limit_parts:
        status_parts.append("⏳ " + " / ".join(limit_parts))

    if tokens_str:
        status_parts.append(tokens_str)
    
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