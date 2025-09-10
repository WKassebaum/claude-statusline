#!/bin/bash
# Safe testing script for Claude Code token tracking

set -e  # Exit on any error

echo "🧪 Claude Code Token Tracking - Safe Test"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    case $2 in
        "error") echo -e "${RED}❌ $1${NC}" ;;
        "success") echo -e "${GREEN}✅ $1${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $1${NC}" ;;
        *) echo "ℹ️  $1" ;;
    esac
}

# Step 1: Check prerequisites
print_status "Checking prerequisites..." "info"

# Check if proxy script exists
if [ ! -f "$(dirname "$0")/token-metrics-proxy.py" ]; then
    print_status "Token proxy script not found!" "error"
    exit 1
fi

# Check if port 4318 is available or has our proxy
if lsof -i :4318 >/dev/null 2>&1; then
    if pgrep -f "token-metrics-proxy.py" >/dev/null; then
        print_status "Our token proxy is already running" "success"
    else
        print_status "Port 4318 is occupied by another process!" "error"
        lsof -i :4318
        exit 1
    fi
else
    print_status "Port 4318 is available" "success"
fi

# Step 2: Test environment validation
print_status "Validating OpenTelemetry configuration..." "info"

# Set test environment (isolated from main shell)
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/json
export OTEL_METRIC_EXPORT_INTERVAL=5000

# Validate configuration
if [ -z "$OTEL_EXPORTER_OTLP_PROTOCOL" ]; then
    print_status "CRITICAL: OTEL_EXPORTER_OTLP_PROTOCOL is missing!" "error"
    print_status "This will cause Claude Code to crash!" "error"
    exit 1
fi

print_status "OTEL_EXPORTER_OTLP_PROTOCOL=$OTEL_EXPORTER_OTLP_PROTOCOL" "success"
print_status "OTEL_EXPORTER_OTLP_ENDPOINT=$OTEL_EXPORTER_OTLP_ENDPOINT" "success"

# Step 3: Start proxy if needed
if ! pgrep -f "token-metrics-proxy.py" >/dev/null; then
    print_status "Starting token metrics proxy..." "info"
    python3 "$(dirname "$0")/token-metrics-proxy.py" &
    PROXY_PID=$!
    sleep 2
    
    if ! pgrep -f "token-metrics-proxy.py" >/dev/null; then
        print_status "Failed to start proxy!" "error"
        exit 1
    fi
    print_status "Proxy started successfully (PID: $PROXY_PID)" "success"
else
    print_status "Proxy already running" "success"
fi

# Step 4: Test OTLP endpoint
print_status "Testing OTLP endpoint..." "info"
if curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"test": "connectivity"}' \
    http://localhost:4318/v1/metrics >/dev/null 2>&1; then
    print_status "OTLP endpoint responding" "success"
else
    print_status "OTLP endpoint not responding correctly" "warning"
fi

# Step 5: Test Claude Code with dry run
print_status "Testing Claude Code configuration (dry run)..." "info"

# Create a test script that validates env vars without actually running Claude
cat > /tmp/claude-test-env.sh << 'EOF'
#!/bin/bash
echo "Environment validation:"
echo "CLAUDE_CODE_ENABLE_TELEMETRY=$CLAUDE_CODE_ENABLE_TELEMETRY"
echo "OTEL_METRICS_EXPORTER=$OTEL_METRICS_EXPORTER"
echo "OTEL_EXPORTER_OTLP_ENDPOINT=$OTEL_EXPORTER_OTLP_ENDPOINT"
echo "OTEL_EXPORTER_OTLP_PROTOCOL=$OTEL_EXPORTER_OTLP_PROTOCOL"
echo "OTEL_METRIC_EXPORT_INTERVAL=$OTEL_METRIC_EXPORT_INTERVAL"

# Check for required variables
if [ -z "$OTEL_EXPORTER_OTLP_PROTOCOL" ]; then
    echo "❌ CRITICAL: Missing OTEL_EXPORTER_OTLP_PROTOCOL"
    exit 1
fi

if [ "$OTEL_EXPORTER_OTLP_ENDPOINT" != "http://localhost:4318" ]; then
    echo "❌ ERROR: Invalid OTLP endpoint"
    exit 1
fi

echo "✅ Configuration looks valid"
EOF

chmod +x /tmp/claude-test-env.sh

if /tmp/claude-test-env.sh; then
    print_status "Environment configuration is valid" "success"
else
    print_status "Environment configuration has errors!" "error"
    rm /tmp/claude-test-env.sh
    exit 1
fi

rm /tmp/claude-test-env.sh

# Step 6: Instructions for safe testing
echo ""
print_status "✅ Pre-flight checks passed!" "success"
echo ""
echo "🚀 Ready for safe testing:"
echo ""
echo "1. Open a NEW terminal (don't use this one)"
echo "2. Run: export CLAUDE_TOKEN_TRACKING=1"
echo "3. Run: source ~/.zshrc"
echo "4. Run: claude --version  (test basic functionality)"
echo "5. If that works, try: claude"
echo ""
echo "📊 Monitor metrics:"
echo "   tail -f ~/.claude/token-metrics.json"
echo ""
echo "🛑 Emergency stop:"
echo "   export CLAUDE_TOKEN_TRACKING=0"
echo "   source ~/.zshrc"
echo ""
print_status "Test in an isolated terminal first!" "warning"