#!/usr/bin/env python3
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
REGISTRY = WORKSPACE / 'projects/xzenia/orchestration/bottleneck-registry.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/autonomous-continue.json'


def load_registry():
    return json.loads(REGISTRY.read_text())


def ready_items(reg):
    return [i for i in reg.get('items', []) if i.get('status') == 'ready' and i.get('queue_policy') != 'self_test_hold']


def run_cycle():
    return subprocess.run(
        ['python3', 'projects/xzenia/execution/run_autonomous_cycle.py'],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )


def main(max_steps=12):
    history = []
    for _ in range(max_steps):
        reg = load_registry()
        items = ready_items(reg)
        if not items:
            payload = {
                'timestamp': datetime.now().astimezone().isoformat(),
                'status': 'registry_exhausted',
                'steps': history
            }
            OUT.write_text(json.dumps(payload, indent=2) + '\n')
            print(json.dumps(payload, indent=2))
            return
        res = run_cycle()
        history.append({
            'returncode': res.returncode,
            'stdout': res.stdout.strip(),
            'stderr': res.stderr.strip()
        })
        if res.returncode != 0:
            payload = {
                'timestamp': datetime.now().astimezone().isoformat(),
                'status': 'blocked',
                'steps': history
            }
            OUT.write_text(json.dumps(payload, indent=2) + '\n')
            print(json.dumps(payload, indent=2))
            raise SystemExit(1)
        time.sleep(0.2)

    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'status': 'max_steps_reached',
        'steps': history
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
