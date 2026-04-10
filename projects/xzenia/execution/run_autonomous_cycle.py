#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
REGISTRY = WORKSPACE / 'projects/xzenia/orchestration/bottleneck-registry.json'


def load_registry():
    return json.loads(REGISTRY.read_text())


def eligible_items(registry):
    return sorted(
        [i for i in registry['items'] if i['status'] == 'ready' and i.get('queue_policy') != 'self_test_hold'],
        key=lambda x: x['priority']
    )


def main():
    registry = load_registry()
    items = eligible_items(registry)
    if not items:
        print(json.dumps({'status': 'registry_exhausted'}, indent=2))
        return
    item = items[0]
    res = subprocess.run(
        ['python3', 'projects/xzenia/execution/executor_gateway.py', item['id']],
        capture_output=True,
        text=True,
        cwd=str(WORKSPACE)
    )
    print(json.dumps({
        'selected': item['id'],
        'code': res.returncode,
        'stdout': res.stdout.strip(),
        'stderr': res.stderr.strip()
    }, indent=2))
    raise SystemExit(res.returncode)


if __name__ == '__main__':
    main()
