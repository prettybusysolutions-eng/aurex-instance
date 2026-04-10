#!/usr/bin/env python3
import json
import sys


def classify(payload):
    failure_text = json.dumps(payload.get('failure', {})).lower()
    if any(x in failure_text for x in ['integrity', 'checkpoint', 'recovery', 'sqlite', 'boot', 'contradiction']):
        severity = 'critical'
    elif any(x in failure_text for x in ['verify', 'validation', 'failed', 'exception']):
        severity = 'high'
    elif any(x in failure_text for x in ['warning', 'degraded']):
        severity = 'medium'
    else:
        severity = 'low'
    payload['severity'] = severity
    return payload


if __name__ == '__main__':
    data = json.loads(sys.stdin.read())
    print(json.dumps(classify(data), indent=2))
