#!/usr/bin/env python3
"""
Token Metrics Proxy for Claude Code Statusline
Captures OpenTelemetry metrics from Claude Code and makes them available to the statusline
"""

import json
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path

# Store metrics in a file that the statusline can read
METRICS_FILE = Path.home() / '.claude' / 'token-metrics.json'
METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Track cumulative token usage
token_totals = {
    'input': 0,
    'output': 0,
    'cacheRead': 0,
    'cacheCreation': 0,
    'lastUpdate': None
}

class OTLPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle OTLP metric posts from Claude Code"""
        global token_totals
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            
            # Process OpenTelemetry metrics
            if 'resourceMetrics' in data:
                for resource_metric in data['resourceMetrics']:
                    for scope_metric in resource_metric.get('scopeMetrics', []):
                        for metric in scope_metric.get('metrics', []):
                            if metric.get('name') == 'claude_code.token.usage':
                                self._process_token_metric(metric)
        except Exception as e:
            print(f"Error processing metrics: {e}")
        
        # Always respond with 200 OK
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
    
    def _process_token_metric(self, metric):
        """Extract and save token usage metrics"""
        global token_totals
        
        for data_point in metric.get('sum', {}).get('dataPoints', []):
            # Extract attributes
            attrs = {}
            for attr in data_point.get('attributes', []):
                key = attr.get('key', '')
                val = attr.get('value', {})
                if 'stringValue' in val:
                    attrs[key] = val['stringValue']
            
            # Get the token count
            value = data_point.get('asInt', 0)
            token_type = attrs.get('type', 'unknown')
            model = attrs.get('model', 'unknown')
            
            # Update totals
            if token_type in token_totals:
                token_totals[token_type] += value
            
            token_totals['lastUpdate'] = datetime.now().isoformat()
            token_totals['model'] = model
            
            # Calculate total tokens used
            total_used = token_totals['input'] + token_totals['output'] + \
                        token_totals['cacheRead'] + token_totals['cacheCreation']
            
            # Save to file for statusline
            metrics_data = {
                'timestamp': datetime.now().isoformat(),
                'totals': token_totals,
                'totalUsed': total_used,
                'model': model
            }
            
            with open(METRICS_FILE, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Updated metrics - Total: {total_used:,} tokens")
    
    def log_message(self, format, *args):
        """Suppress normal HTTP logging"""
        pass

def cleanup_old_metrics():
    """Clean up old metrics file on startup"""
    if METRICS_FILE.exists():
        METRICS_FILE.unlink()
        print(f"Cleaned up old metrics file")

def main():
    PORT = 4318  # OTLP HTTP port
    
    cleanup_old_metrics()
    
    print("=" * 60)
    print("Claude Code Token Metrics Proxy")
    print("=" * 60)
    print()
    print("To enable token tracking, restart Claude Code with:")
    print()
    print("  export CLAUDE_CODE_ENABLE_TELEMETRY=1")
    print("  export OTEL_METRICS_EXPORTER=otlp")
    print(f"  export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:{PORT}")
    print("  export OTEL_METRIC_EXPORT_INTERVAL=5000")
    print("  claude")
    print()
    print(f"Metrics will be saved to: {METRICS_FILE}")
    print(f"Listening on port {PORT}...")
    print()
    
    server = HTTPServer(('localhost', PORT), OTLPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == '__main__':
    main()