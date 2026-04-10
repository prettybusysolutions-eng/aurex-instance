#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')


def run(cmd, payload):
    return subprocess.run(cmd, input=json.dumps(payload), text=True, capture_output=True, cwd=str(WORKSPACE))


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('pre', 'post'):
        raise SystemExit('usage: checkpoint_contract.py <pre|post>')
    phase = sys.argv[1]
    payload = json.loads(sys.stdin.read())
    label = payload.get('work_id', 'unknown-work')
    res = subprocess.run(
        ['python3', 'projects/xzenia/scripts/continuity-guard.py', 'save', f'checkpoint-contract:{phase}:{label}', json.dumps(payload), json.dumps(payload)],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )
    if res.returncode != 0:
        raise SystemExit(res.stderr or res.stdout)
    print(json.dumps({'status': 'done and verified', 'phase': phase, 'work_id': label}, indent=2))


if __name__ == '__main__':
    main()
