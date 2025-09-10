#!/bin/bash
# Emergency script to unset all OpenTelemetry variables
# Use this if Claude Code crashes or behaves strangely

echo "🚨 Emergency OTEL variable cleanup"
echo "================================="

# Unset all OpenTelemetry related variables
unset CLAUDE_CODE_ENABLE_TELEMETRY
unset OTEL_METRICS_EXPORTER
unset OTEL_EXPORTER_OTLP_ENDPOINT
unset OTEL_EXPORTER_OTLP_PROTOCOL
unset OTEL_METRIC_EXPORT_INTERVAL

# Disable token tracking
export CLAUDE_TOKEN_TRACKING=0

echo "✅ All OTEL variables cleared"
echo "✅ Token tracking disabled"
echo ""
echo "Test Claude Code recovery:"
echo "  claude --version"
echo ""
echo "If problems persist, restart your terminal or run:"
echo "  source ~/.zshrc"
