#!/bin/bash
# Safer Claude Code Token Tracking Configuration
# Source this instead of setting variables directly in .zshrc

# Safety check - only proceed if explicitly enabled
if [[ "$CLAUDE_TOKEN_TRACKING" != "1" ]]; then
    # Ensure all OTEL variables are unset when disabled
    unset CLAUDE_CODE_ENABLE_TELEMETRY
    unset OTEL_METRICS_EXPORTER
    unset OTEL_EXPORTER_OTLP_ENDPOINT
    unset OTEL_EXPORTER_OTLP_PROTOCOL
    unset OTEL_METRIC_EXPORT_INTERVAL
    return 0
fi

# Validation function
validate_token_config() {
    local errors=0
    
    # Check if proxy is available
    if ! command -v python3 >/dev/null 2>&1; then
        echo "❌ ERROR: python3 not found"
        ((errors++))
    fi
    
    # Check if proxy script exists
    local proxy_script="$HOME/WorkDev/MCP-Dev/claude-statusline/token-metrics-proxy.py"
    if [ ! -f "$proxy_script" ]; then
        echo "❌ ERROR: Token proxy script not found at $proxy_script"
        ((errors++))
    fi
    
    # Check if port 4318 is available or has our proxy
    if lsof -i :4318 >/dev/null 2>&1; then
        if ! pgrep -f "token-metrics-proxy.py" >/dev/null; then
            echo "❌ ERROR: Port 4318 occupied by another process"
            ((errors++))
        fi
    fi
    
    return $errors
}

# Only proceed if validation passes
if ! validate_token_config; then
    echo "⚠️  Token tracking validation failed - keeping disabled"
    export CLAUDE_TOKEN_TRACKING=0
    return 1
fi

# Set OpenTelemetry configuration with all required variables
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/json  # CRITICAL: Prevents crashes
export OTEL_METRIC_EXPORT_INTERVAL=5000

# Start proxy if not running (but don't auto-restart Claude if it fails)
if ! pgrep -f "token-metrics-proxy.py" >/dev/null; then
    local proxy_script="$HOME/WorkDev/MCP-Dev/claude-statusline/token-metrics-proxy.py"
    if [ -f "$proxy_script" ]; then
        # Start proxy but capture any errors
        if python3 "$proxy_script" >/dev/null 2>&1 &; then
            sleep 1
            if pgrep -f "token-metrics-proxy.py" >/dev/null; then
                echo "✅ Token metrics proxy started"
            else
                echo "❌ Failed to start token metrics proxy"
                export CLAUDE_TOKEN_TRACKING=0
                validate_token_config  # This will unset variables
            fi
        fi
    fi
fi