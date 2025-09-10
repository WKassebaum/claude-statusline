#!/bin/bash
# Verify OTEL environment is clean before enabling token tracking
# Run this BEFORE enabling token tracking to ensure no stale variables

echo "🔍 Checking for stale OTEL environment variables..."
echo "================================================"

FOUND_ISSUES=0

# Check each OTEL variable
for var in CLAUDE_CODE_ENABLE_TELEMETRY OTEL_METRICS_EXPORTER OTEL_EXPORTER_OTLP_ENDPOINT OTEL_EXPORTER_OTLP_PROTOCOL OTEL_METRIC_EXPORT_INTERVAL OTEL_EXPORTER_OTLP_METRICS_PROTOCOL OTEL_EXPORTER_OTLP_LOGS_PROTOCOL OTEL_LOGS_EXPORTER; do
    if [ -n "${!var}" ]; then
        echo "⚠️  Found: $var=${!var}"
        ((FOUND_ISSUES++))
    fi
done

if [ $FOUND_ISSUES -gt 0 ]; then
    echo ""
    echo "❌ Found $FOUND_ISSUES stale OTEL variables!"
    echo ""
    echo "These can cause Claude Code to crash even with correct configuration."
    echo "Run this to clean them:"
    echo "  source ./unset-otel.sh"
    echo ""
    echo "Then restart your terminal or run:"
    echo "  exec zsh"
    exit 1
else
    echo ""
    echo "✅ Environment is clean - safe to enable token tracking"
    echo ""
    echo "Next steps:"
    echo "1. Run: ./claude-token-safe-test.sh"
    echo "2. Follow TESTING-PROTOCOL.md"
fi