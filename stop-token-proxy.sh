#!/bin/bash

# Stop the token metrics proxy

PID_FILE="/tmp/token-metrics-proxy.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping token metrics proxy (PID: $PID)..."
        kill "$PID"
        rm "$PID_FILE"
        echo "Token metrics proxy stopped"
    else
        echo "Token metrics proxy not running (stale PID file)"
        rm "$PID_FILE"
    fi
else
    # Try to find it by port
    PID=$(lsof -ti :4318)
    if [ -n "$PID" ]; then
        echo "Stopping token metrics proxy (PID: $PID)..."
        kill "$PID"
        echo "Token metrics proxy stopped"
    else
        echo "Token metrics proxy is not running"
    fi
fi