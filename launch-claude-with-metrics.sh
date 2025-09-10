#!/bin/bash

# Launch Claude Code with token metrics tracking enabled

echo "Starting Claude Code with token metrics tracking..."
echo

# Start the metrics proxy in the background
echo "Starting metrics proxy..."
python3 "$(dirname "$0")/token-metrics-proxy.py" &
PROXY_PID=$!

# Give the proxy time to start
sleep 2

# Export environment variables for Claude Code
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export OTEL_METRICS_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_METRIC_EXPORT_INTERVAL=5000

echo "Launching Claude Code with telemetry enabled..."
echo

# Launch Claude Code
claude

# When Claude Code exits, kill the proxy
echo "Shutting down metrics proxy..."
kill $PROXY_PID 2>/dev/null