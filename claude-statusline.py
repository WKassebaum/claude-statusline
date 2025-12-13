#!/usr/bin/env python3
"""
Claude Code Enhanced Statusline with Optional Codeindex Integration
Displays accurate token usage, costs, burn rate, and optional codeindex status for Claude Code sessions.

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
    if 'opus-4-5' in model_id_lower:
        return "Opus 4.5"
    elif 'opus-4-1' in model_id_lower:
        return "Opus 4.1"
    elif 'opus-4' in model_id_lower:
        return "Opus 4"
    elif 'sonnet-4-5' in model_id_lower:
        return "Sonnet 4.5"
    elif 'sonnet-4' in model_id_lower:
        return "Sonnet 4"
    elif 'sonnet-3-5' in model_id_lower or 'sonnet-20241022' in model_id_lower:
        return "Sonnet 3.5"
    elif 'sonnet' in model_id_lower:
        return "Sonnet"
    elif 'haiku' in model_id_lower:
        return "Haiku"

    # Google models (order matters - check more specific patterns first)
    elif 'gemini-3-pro' in model_id_lower or 'gemini-3.0-pro' in model_id_lower:
        return "Gemini 3 Pro"
    elif 'gemini-2.5-pro' in model_id_lower:
        return "Gemini 2.5 Pro"
    elif 'gemini-2.5-flash' in model_id_lower:
        return "Gemini 2.5 Flash"
    elif 'gemini-2' in model_id_lower:
        return "Gemini 2"
    elif 'gemini' in model_id_lower:
        return "Gemini"

    # xAI models
    elif 'grok-4-fast' in model_id_lower:
        return "Grok 4 Fast"
    elif 'grok-4' in model_id_lower:
        return "Grok 4"
    elif 'grok' in model_id_lower:
        return "Grok"

    # OpenAI models
    elif 'o3' in model_id_lower:
        return "O3"
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
            ["curl", "-s", f"http://localhost:{ccr_port}/api/statusline/usage?sessionId={session_id}"],
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
            ["curl", "-s", "http://localhost:6333/collections"],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        logs_result = subprocess.run(
            ["curl", "-s", "http://localhost:3847/logs"],
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
                ["curl", "-s", "http://localhost:6333/collections"],
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
                ["curl", "-s", f"http://localhost:6333/collections/{matched_collection_name}"],
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
    blocks_data, session_data, daily_data = get_ccusage_data()

    # PRIORITY 1: Check for real context data from Claude Code's JSON input
    real_tokens = None
    context_window_tokens = None
    context_usage_percent = None
    claude_session_cost = None
    exceeds_context_limit = False

    if 'context' in claude_data:
        context_data = claude_data['context']
        if isinstance(context_data, dict):
            # Get actual token usage from Claude Code
            real_tokens = context_data.get('used_tokens')
            context_usage_percent = context_data.get('usage_percent')

    if 'model' in claude_data and isinstance(claude_data['model'], dict):
        # Get context window size from model info
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
                burn_rate_info = current_block['burnRate']
                if isinstance(burn_rate_info, dict):
                    burn_rate = int(burn_rate_info.get('tokensPerMinute', 0))
                    hourly_rate = burn_rate_info.get('costPerHour', 0.0)
            
            # Get remaining time
            if 'projection' in current_block:
                projection_info = current_block['projection']
                if isinstance(projection_info, dict):
                    time_remaining_mins = projection_info.get('remainingMinutes', 0)
            
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

    # Use real session cost from Claude Code if available (more accurate than ccusage)
    if claude_session_cost is not None:
        session_cost = claude_session_cost
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
    
    # Estimate time left based on remaining tokens and burn rate
    time_left = f"~{time_remaining_mins}m" if time_remaining_mins > 0 else "~30m"
    if time_remaining_mins > 60:
        hours = int(time_remaining_mins / 60)
        mins = int(time_remaining_mins % 60)
        time_left = f"~{hours}h{mins}m"
    
    # Detect model with CCR-aware priority:
    # 1. Check if CCR has routing info for this session (highest priority)
    # 2. Use Claude Code's model from stdin (vanilla claude sessions)
    # 3. Detect from ccusage block models (fallback)

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
        
        # Parse model name from ID if we got a string
        if model_id and isinstance(model_id, str):
            model_id_lower = model_id.lower()
            if 'opus-4-5' in model_id_lower:
                model = "Opus 4.5"
            elif 'opus-4-1' in model_id_lower:
                model = "Opus 4.1"
            elif 'opus-4' in model_id_lower:
                model = "Opus 4"
            elif 'sonnet-4-5' in model_id_lower:
                model = "Sonnet 4.5"
            elif 'sonnet-4' in model_id_lower:
                model = "Sonnet 4"
            elif 'sonnet-3-5' in model_id_lower or 'sonnet-20241022' in model_id_lower:
                model = "Sonnet 3.5"
            elif 'sonnet' in model_id_lower:
                model = "Sonnet"
            elif 'haiku' in model_id_lower:
                model = "Haiku"
            elif 'claude-' in model_id_lower:
                # Try to extract version from model ID
                model = model_id.replace('claude-', '').replace('-', ' ').title()

    # PRIORITY 3: Fallback to ccusage block models if no model from CCR or stdin
    if model == "Claude" and current_block and 'models' in current_block and current_block['models']:
        # Get all non-synthetic models and parse them
        model_names = []
        seen_models = set()
        
        for model_id in reversed(current_block['models']):
            if model_id != '<synthetic>':
                parsed_model = None
                if 'opus-4-5' in model_id:
                    parsed_model = "Opus 4.5"
                elif 'opus-4-1' in model_id:
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
        
        # Join models with commas if multiple, otherwise use single model
        if model_names:
            model = ", ".join(model_names)
    
    # Format costs
    session_str = f"${session_cost:.2f}" if session_found else "N/A"
    today_str = f"${today_cost:.2f}"
    block_str = f"${block_cost:.2f}"
    
    # Format token count and context window
    if real_tokens is not None and context_window_tokens is not None:
        # We have actual context data from Claude Code!
        tokens_str = f"📊 {format_number(real_tokens)}/{format_number(context_window_tokens)}"
        if context_usage_percent is not None:
            tokens_str += f" ({context_usage_percent}%)"
    elif real_tokens is not None:
        # We have real tokens but not context window
        tokens_str = f"📊 {format_number(real_tokens)} tokens"
    else:
        # Fallback to ccusage estimates
        display_tokens = block_tokens
        tokens_str = f"{format_number(display_tokens)} tokens"


    # Build status line parts with context warning if needed
    model_display = f"🤖 {model}"
    if exceeds_context_limit:
        model_display += " ⚠️"

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
    
    
    # Continue with existing parts
    status_parts.extend([
        f"💰 {session_str} session / {today_str} today / {block_str} block ({time_remaining} left)",
        f"🔥 {burn_str}",
        tokens_str,  # Already fully formatted with context window info
        f"{block_usage_pct:.1f}% used",
        f"{time_left} left"
    ])
    
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