#!/usr/bin/env python3
"""
API Error Watchdog — Polls for API errors and triggers auto-fallback.
Runs every 60s via LaunchAgent. Watches gateway stderr + consumer log for error patterns.
"""
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
LOG = WORKSPACE / 'projects/xzenia/csmr/reports/api-error-watchdog.json'
FALLBACK_SCRIPT = WORKSPACE / 'projects/xzenia/execution/auto_fallback_enforcer.py'

ERROR_PATTERNS = [
    '429',
    'rate limit',
    'TOO_MANY_REQUESTS',
    'insufficient_quota',
    'rate_limit_exceeded',
    'context_overflow',
    'token limit',
    'timeout',
    'service unavailable',
    '503',
]

GATEWAY_ERR = Path('/Users/marcuscoarchitect/.openclaw/workspace/task-queue/consumer.err.log')
CONSUMER_LOG = Path('/Users/marcuscoarchitect/.openclaw/workspace/task-queue/consumer.log')


def check_logs():
    """Scan logs for API errors in the last 60 seconds."""
    import os
    now = time.time()
    cutoff = now - 60
    
    errors_found = []
    
    for log_file in [GATEWAY_ERR, CONSUMER_LOG]:
        if not log_file.exists():
            continue
        try:
            content = log_file.read_text()
            lines = content.splitlines()[-50:]  # Last 50 lines
            for line in lines:
                line_lower = line.lower()
                for pattern in ERROR_PATTERNS:
                    if pattern.lower() in line_lower:
                        # Extract timestamp if present
                        errors_found.append({'pattern': pattern, 'line': line[:200]})
                        break
        except:
            pass
    
    return errors_found


def main():
    start = time.time()
    errors = check_logs()
    
    result = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'errors_detected': len(errors),
        'errors': errors[:5],  # Max 5 for brevity
        'latency_ms': int((time.time() - start) * 1000)
    }
    
    # If errors found, trigger fallback
    if errors:
        print(f"⚠️  {len(errors)} API errors detected — triggering fallback", flush=True)
        res = subprocess.run(
            ['python3', str(FALLBACK_SCRIPT), 'auto-detected'],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        result['fallback_result'] = json.loads(res.stdout) if res.returncode == 0 else {'error': res.stderr}
    
    LOG.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
