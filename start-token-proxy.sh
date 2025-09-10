#!/bin/bash

# Start the token metrics proxy if not already running
# This is called automatically when Claude Code starts with telemetry enabled

PROXY_SCRIPT="$(dirname "$0")/token-metrics-proxy.py"
PROXY_PORT=4318

# Check if proxy is already running
if lsof -i :$PROXY_PORT > /dev/null 2>&1; then
    echo "Token metrics proxy is already running on port $PROXY_PORT"
    exit 0
fi

# Start the proxy in the background
echo "Starting token metrics proxy on port $PROXY_PORT..."
python3 "$PROXY_SCRIPT" > /tmp/token-metrics-proxy.log 2>&1 &
PROXY_PID=$!

# Save PID for later cleanup
echo $PROXY_PID > /tmp/token-metrics-proxy.pid

# Give it a moment to start
sleep 1

# Verify it started
if lsof -i :$PROXY_PORT > /dev/null 2>&1; then
    echo "Token metrics proxy started successfully (PID: $PROXY_PID)"
    echo "Logs: /tmp/token-metrics-proxy.log"
else
    echo "Failed to start token metrics proxy"
    exit 1
fi