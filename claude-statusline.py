#!/usr/bin/env python3
"""
Claude Code Enhanced Statusline with Optional Codeindex Integration
Displays context usage, session cost, rate-limit usage, and optional codeindex status for Claude Code sessions.
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

def format_model_name(model_id):
    """Format raw model ID into a friendly display name"""
    if not model_id:
        return None

    model_id_lower = model_id.lower()

    # Anthropic models (order matters - check more specific patterns first)
    if 'opus-4-8' in model_id_lower or 'opus 4.8' in model_id_lower:
        return "Opus 4.8"
    elif 'opus-4-7' in model_id_lower or 'opus 4.7' in model_id_lower:
        return "Opus 4.7"
    elif 'opus-4-6' in model_id_lower or 'opus 4.6' in model_id_lower:
        return "Opus 4.6"
    elif 'opus-4-5' in model_id_lower or 'opus 4.5' in model_id_lower:
        return "Opus 4.5"
    elif 'opus-4-1' in model_id_lower:
        return "Opus 4.1"
    elif 'opus-4' in model_id_lower:
        return "Opus 4"
    elif 'sonnet-4-7' in model_id_lower or 'sonnet 4.7' in model_id_lower:
        return "Sonnet 4.7"
    elif 'sonnet-4-6' in model_id_lower or 'sonnet 4.6' in model_id_lower:
        return "Sonnet 4.6"
    elif 'sonnet-4-5' in model_id_lower:
        return "Sonnet 4.5"
    elif 'sonnet-4' in model_id_lower:
        return "Sonnet 4"
    elif 'sonnet-3-5' in model_id_lower or 'sonnet-20241022' in model_id_lower:
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

    # OpenAI models (order matters - check more specific patterns first)
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
        # Return cleaned up version
        return model_id.replace('-', ' ').title()

def get_ccr_port():
    """Read CCR port from config file"""
    try:
        import os
        import json
        ccr_config_path = os.path.expanduser("~/.claude-code-router/config.json")
        with open(ccr_config_path, 'r') as f:
            config = json.load(f)
            return config.get('PORT', 8181)  # Default to 8181 if not specified
    except:
        return 8181  # Default CCR port

def get_ccr_routed_model(session_id):
    """Query CCR for the actual routed model for this session"""
    try:
        # Get CCR port from config
        ccr_port = get_ccr_port()

        # Check if CCR is running
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "0.1", f"http://127.0.0.1:{ccr_port}/api/statusline/usage?sessionId={session_id}"],
            capture_output=True,
            text=True,
            timeout=1
        )

        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)

            # Check if CCR has actual routing info for this session
            current_model = data.get('currentModel', {})
            if current_model.get('isActual'):
                # CCR has routed this session, return the formatted model name
                raw_model = current_model.get('model', '').strip()
                return format_model_name(raw_model)
            # If not isActual, CCR doesn't have routing info for this session
            # Return None to fall back to Claude Code's model

        return None
    except:
        # CCR not available or error occurred
        return None

def get_codeindex_status():
    """Get codeindex status with progress tracking"""
    try:
        # Get current directory info
        cwd = get_current_working_directory()
        if not cwd:
            return None  # Return None instead of error string
        
        project_name = cwd.split('/')[-1]
        expected_collection = f"codeindex-{project_name}"
        
        # Check collections and logs in parallel
        collections_result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "0.1", "http://127.0.0.1:6333/collections"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if collections_result.returncode != 0 or not collections_result.stdout:
            return None  # Qdrant unreachable; skip the logs probe

        logs_result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "0.1", "http://127.0.0.1:3847/logs"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        # Parse results
        collections_data = None
        logs_data = None
        
        if collections_result.returncode == 0 and collections_result.stdout:
            try:
                collections_data = json.loads(collections_result.stdout)
            except (json.JSONDecodeError, ValueError):
                return None  # Return None on parse error
        
        if logs_result.returncode == 0 and logs_result.stdout:
            try:
                logs_data = json.loads(logs_result.stdout)
            except (json.JSONDecodeError, ValueError):
                logs_data = None  # Continue without logs
        
        result = parse_codeindex_with_progress(collections_data, logs_data, project_name, expected_collection, cwd)
        
        # Validate result before returning
        if result and isinstance(result, str) and len(result) > 0:
            return result
        return None
        
    except Exception:
        # Fallback to legacy method
        try:
            result = subprocess.run(
                ["curl", "-s", "--connect-timeout", "0.1", "http://127.0.0.1:6333/collections"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout:
                try:
                    data = json.loads(result.stdout)
                    parsed = parse_codeindex_collections(data)
                    # Validate parsed result
                    if parsed and isinstance(parsed, str) and len(parsed) > 0:
                        return parsed
                except (json.JSONDecodeError, ValueError):
                    pass
            return None
        except Exception:
            return None

def normalize_collection_name(folder_name):
    """Normalize folder name to match codeindex collection naming convention.

    Codeindex normalizes names to: lowercase, spaces replaced with hyphens.
    Example: 'Submittal RFI Processing System' -> 'submittal-rfi-processing-system'
    """
    return folder_name.lower().replace(' ', '-')

def parse_codeindex_with_progress(collections_data, logs_data, project_name, expected_collection, cwd):
    """Parse codeindex status with progress tracking and parent directory support"""
    if not collections_data or 'result' not in collections_data:
        return None  # Return None when service is unreachable

    try:
        collections = collections_data['result']['collections']
        collection_names = [col.get('name', '') for col in collections]
        # Also create lowercase versions for case-insensitive matching
        collection_names_lower = [name.lower() for name in collection_names]
    except (KeyError, TypeError):
        return None  # Return None on data structure errors

    # Walk up directory tree to find indexed parent projects
    current_collection = None
    matched_project_name = None
    matched_collection_name = None

    path_parts = cwd.rstrip('/').split('/')
    for i in range(len(path_parts), 0, -1):
        # Get directory name at this level
        dir_name = path_parts[i-1]
        # Normalize the expected collection name (lowercase, spaces -> hyphens)
        normalized_name = normalize_collection_name(dir_name)
        expected_coll = f"codeindex-{normalized_name}"

        # Check if this directory level has a collection (case-insensitive)
        if expected_coll in collection_names_lower:
            # Find the actual collection object
            for collection in collections:
                if collection.get('name', '').lower() == expected_coll:
                    current_collection = collection
                    matched_project_name = dir_name
                    matched_collection_name = collection.get('name', '')
                    break
            if current_collection:
                break

        # Stop at reasonable boundaries (home directory, etc.)
        if dir_name in ['Users', 'home', 'root'] or len(path_parts[:i]) < 3:
            break

    # If we didn't find a match, fall back to original behavior with normalization
    if not current_collection:
        normalized_expected = f"codeindex-{normalize_collection_name(project_name)}"
        for collection in collections:
            if collection.get('name', '').lower() == normalized_expected:
                current_collection = collection
                matched_project_name = project_name
                matched_collection_name = collection.get('name', '')
                break
    
    # Parse logs for progress information
    is_indexing = False
    total_files = None
    current_chunks = 0

    if logs_data and 'output' in logs_data:
        # Check last 50 log entries for broader detection
        recent_logs = logs_data['output'][-50:]
        all_logs = logs_data['output']

        # Look for any recent insertion activity for this collection
        # Use the actual matched collection name for log searching
        search_collection = matched_collection_name or f"codeindex-{normalize_collection_name(project_name)}"
        for log_entry in recent_logs:
            if f"📝 Inserting" in log_entry and search_collection in log_entry:
                is_indexing = True
                break

        # Look for tracking count and completion info in all logs for this collection
        if matched_collection_name:
            for entry in all_logs:
                if matched_collection_name in entry:
                    # Parse total files being tracked
                    if "tracking" in entry:
                        match = re.search(r'tracking (\d+) files', entry)
                        if match:
                            total_files = int(match.group(1))

                    # Parse completion status
                    if "✅ Initial index completed:" in entry:
                        match = re.search(r'(\d+) files, (\d+) chunks', entry)
                        if match:
                            total_files = int(match.group(1))
                            current_chunks = int(match.group(2))

    # If collection exists, get current document count using actual collection name
    if current_collection and matched_collection_name:
        try:
            collection_result = subprocess.run(
                ["curl", "-s", "--connect-timeout", "0.1", f"http://127.0.0.1:6333/collections/{matched_collection_name}"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if collection_result.returncode == 0:
                collection_info = json.loads(collection_result.stdout)
                current_chunks = collection_info.get('result', {}).get('points_count', current_chunks)
        except:
            pass
    
    # Determine status
    if current_collection:
        # Use the matched project name (could be a parent directory)
        display_name = matched_project_name or project_name
        if is_indexing and total_files and current_chunks:
            # Calculate rough progress (chunks vs estimated total chunks)
            # Estimate ~100 chunks per file on average
            estimated_total_chunks = total_files * 100
            progress_pct = min(100, int((current_chunks / estimated_total_chunks) * 100))
            return f"🔄 ({progress_pct}%) {display_name}"
        else:
            return f"✅ {display_name}"
    else:
        # Check if there are any codeindex collections (service is working)
        has_any_codeindex = any(
            col.get('name', '').startswith('codeindex-')
            for col in collections
        )
        
        if has_any_codeindex:
            # Use immediate directory name for "not indexed" status
            return f"❌ {project_name}"
        else:
            return "idle"

def parse_codeindex_collections(data):
    """Parse Qdrant collections response to show current project status"""
    if not data or 'result' not in data or 'collections' not in data['result']:
        return None  # Return None when data is invalid
    
    # Get current working directory to check if current project is indexed
    cwd = get_current_working_directory()
    if not cwd:
        return None  # Return None when can't determine directory
    
    # Extract project name from current directory
    project_name = cwd.split('/')[-1]
    expected_collection = f"codeindex-{project_name}"
    
    # Check if current project has a collection
    collections = data['result']['collections']
    for collection in collections:
        if collection.get('name', '') == expected_collection:
            return f"✅ {project_name}"
    
    # Check if there are any codeindex collections (service is working)
    has_any_codeindex = any(
        col.get('name', '').startswith('codeindex-')
        for col in collections
    )
    
    if has_any_codeindex:
        return f"❌ {project_name}"
    else:
        return "idle"

def parse_codeindex_data(data):
    """Parse codeindex status into display format"""
    if not data or data.get('status') != 'running':
        return "idle"
    
    directory = data.get('directory', '')
    if not directory:
        return "idle"
    
    # Extract project name from directory path
    project_name = directory.split('/')[-1]
    
    # Determine status indicator
    errors = data.get('stats', {}).get('errors', 0)
    if errors > 0:
        indicator = "⚠️"
    else:
        indicator = "●"
    
    return f"{indicator}{project_name}"

def format_codeindex_status():
    """Format codeindex status for status line (optional)"""
    try:
        status = get_codeindex_status()
        # Validate status is a proper string before formatting
        if status is None or not isinstance(status, str) or len(status) == 0:
            return None  # Service unavailable, skip section
        # Additional check for unexpected values
        if "undefined" in status.lower() or "error" in status.lower():
            return None  # Skip if status contains error indicators
        return f"🔍 {status}"
    except Exception:
        return None  # Return None on any error

def calculate_status(claude_data=None):
    """Calculate the status line values"""
    if claude_data is None:
        claude_data = {}

    # PRIORITY 1: Check for real context data from Claude Code's JSON input
    # The context_window object contains the actual context tracking data (v2.0.65+)
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
    
    session_str = f"${claude_session_cost:.2f}" if claude_session_cost is not None else "N/A"

    # Subscription rate-limit windows (Pro/Max only, absent until the first API response)
    rate_limits = claude_data.get('rate_limits')
    if not isinstance(rate_limits, dict):
        rate_limits = {}

    # Detect model with CCR-aware priority:
    # 1. Check if CCR has routing info for this session (highest priority)
    # 2. Use Claude Code's model from stdin (vanilla claude sessions)

    model = "Claude"  # Default fallback

    # PRIORITY 1: Check if CCR has routing info for this session
    session_id = claude_data.get('session_id')
    if session_id:
        ccr_model = get_ccr_routed_model(session_id)
        if ccr_model:
            # CCR has routed this session, use the actual routed model
            model = ccr_model

    # PRIORITY 2: Try to get model from stdin (passed by Claude Code)
    # Only if we didn't get a model from CCR
    if model == "Claude" and 'model' in claude_data and claude_data['model']:
        model_data = claude_data['model']
        model_id = ""
        
        # Handle both string and dict model formats
        if isinstance(model_data, str):
            model_id = model_data
        elif isinstance(model_data, dict):
            # Try common dict keys
            model_id = model_data.get('name', model_data.get('id', model_data.get('model', '')))
        
        # Parse model name from ID if we got a string - use format_model_name()
        if model_id and isinstance(model_id, str):
            parsed = format_model_name(model_id)
            if parsed:
                model = parsed

    # Color constants for context display (defined early for use below)
    _RESET = "\033[0m"
    _GREEN = "\033[32m"
    _YELLOW = "\033[33m"
    _RED = "\033[31m"

    def _ctx_color(pct):
        if pct is None:
            return ""
        if pct >= 80:
            return _RED
        if pct >= 50:
            return _YELLOW
        return _GREEN

    # Format token count and context window with color coding
    if real_tokens is not None and context_window_tokens is not None:
        c = _ctx_color(context_usage_percent)
        tokens_str = f"📊 {c}{format_number(real_tokens)}/{format_number(context_window_tokens)}"
        if context_usage_percent is not None:
            if isinstance(context_usage_percent, float) and context_usage_percent != int(context_usage_percent):
                tokens_str += f" ({context_usage_percent:.1f}%)"
            else:
                tokens_str += f" ({int(context_usage_percent)}%)"
        tokens_str += _RESET
    elif context_usage_percent is not None and context_window_tokens is not None:
        c = _ctx_color(context_usage_percent)
        tokens_str = f"📊 {c}{int(context_usage_percent)}% of {format_number(context_window_tokens)}{_RESET}"
    elif real_tokens is not None:
        # We have real tokens but not context window
        tokens_str = f"📊 {format_number(real_tokens)} tokens"
    else:
        tokens_str = None


    # Build status line parts with context warning and color coding
    # Colors: green <50%, yellow 50-79%, red 80%+
    RESET = "\033[0m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"

    context_color = ""
    if context_usage_percent is not None:
        if context_usage_percent >= 80:
            context_color = RED
        elif context_usage_percent >= 50:
            context_color = YELLOW
        else:
            context_color = GREEN

    model_display = f"🤖 {model}"
    if exceeds_context_limit:
        model_display += f" {RED}⚠️ CONTEXT FULL{RESET}"
    elif context_usage_percent is not None and context_usage_percent >= 80:
        model_display += f" {RED}⚠️ {int(context_usage_percent)}%{RESET}"
    elif context_usage_percent is not None and context_usage_percent >= 50:
        model_display += f" {YELLOW}⚠️{RESET}"

    status_parts = [
        model_display
    ]

    # Add git branch if available
    git_branch = get_git_branch()
    if git_branch:
        status_parts.append(f"🌿 {git_branch}")

    # Add codeindex status if available (optional dependency)
    codeindex_status = format_codeindex_status()
    if codeindex_status:
        status_parts.append(codeindex_status)
    
    
    status_parts.append(f"💰 {session_str} session")

    limit_parts = []
    for key, label in (('five_hour', '5h'), ('seven_day', '7d')):
        window = rate_limits.get(key)
        if not isinstance(window, dict) or window.get('used_percentage') is None:
            continue
        pct = window['used_percentage']
        part = f"{_ctx_color(pct)}{label} {pct:.0f}%{_RESET}"
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
        status = calculate_status(claude_data)
        
        # Output the status line
        print(status)
        
    except Exception as e:
        # Fallback status on error
        print(f"🤖 Opus 4.1 | 💰 Status unavailable | Error: {str(e)}")

if __name__ == "__main__":
    main()