#!/usr/bin/env python3
"""
routing_drift_watch.py — detect routing drift without mutating unless asked.
"""
import json
from pathlib import Path
from datetime import datetime

CONFIG = Path.home() / '.openclaw' / 'openclaw.json'
EXPECTED = {
    'session.dmScope': 'per-channel-peer',
    'session.identityLinks': {'aurex': ['telegram:6620375090']},
}


def get_path(data, path):
    cur = data
    for key in path.split('.'):
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def main():
    data = json.loads(CONFIG.read_text())
    drifts = []
    for path, expected in EXPECTED.items():
        actual = get_path(data, path)
        if actual != expected:
            drifts.append({'path': path, 'expected': expected, 'actual': actual})
    print(json.dumps({'checkedAt': datetime.now().isoformat(), 'drifts': drifts, 'ok': not drifts}, indent=2))


if __name__ == '__main__':
    main()
