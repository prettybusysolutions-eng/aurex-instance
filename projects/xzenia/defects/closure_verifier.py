#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
REGISTRY = WORKSPACE / 'projects/xzenia/orchestration/bottleneck-registry.json'
REPORT = WORKSPACE / 'projects/xzenia/csmr/reports/closure-verifier-report.json'


def main():
    if len(sys.argv) < 3:
        raise SystemExit('usage: closure_verifier.py <defect_id> <pass|fail>')
    defect_id, outcome = sys.argv[1], sys.argv[2]
    registry = json.loads(REGISTRY.read_text())
    item = next((i for i in registry.get('items', []) if i.get('id') == defect_id), None)
    if not item:
        raise SystemExit('defect not found')

    if outcome == 'pass':
        item['status'] = 'done'
        result = 'done and verified'
    elif outcome == 'fail':
        item['status'] = 'ready'
        item['priority'] = max(1, int(item.get('priority', 4)) - 1)
        item['severity'] = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low'}.get(item['priority'], 'low')
        item['retriggerCount'] = int(item.get('retriggerCount', 1)) + 1
        result = 'reopened and escalated'
    else:
        raise SystemExit('outcome must be pass or fail')

    registry['updatedAt'] = datetime.now().astimezone().isoformat()
    REGISTRY.write_text(json.dumps(registry, indent=2) + '\n')
    payload = {'defect_id': defect_id, 'outcome': outcome, 'result': result, 'status': item['status'], 'priority': item['priority']}
    REPORT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
