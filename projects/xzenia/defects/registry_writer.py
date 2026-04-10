#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
REGISTRY = WORKSPACE / 'projects/xzenia/orchestration/bottleneck-registry.json'
REPORT = WORKSPACE / 'projects/xzenia/csmr/reports/defect-registry-writes.json'
SEVERITY_TO_PRIORITY = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
PRIORITY_TO_SEVERITY = {v: k for k, v in SEVERITY_TO_PRIORITY.items()}


def load_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def failure_signature(defect):
    failure = defect.get('failure', {})
    return (defect.get('source', ''), failure.get('summary', ''), failure.get('error', ''))


def escalate_priority(existing_priority, new_priority):
    return min(existing_priority, new_priority)


def main():
    defect = json.loads(sys.stdin.read())
    registry = load_json(REGISTRY, {'updatedAt': None, 'objective': 'auto defect governance', 'stopConditions': [], 'items': []})
    new_priority = SEVERITY_TO_PRIORITY[defect['severity']]
    sig = failure_signature(defect)

    existing = None
    for item in registry.get('items', []):
        item_sig = (item.get('source_signature', {}).get('source', ''), item.get('source_signature', {}).get('summary', ''), item.get('source_signature', {}).get('error', ''))
        if item_sig == sig:
            existing = item
            break

    self_test = bool(defect.get('state', {}).get('self_test'))
    action = 'inserted'
    target_id = defect['defect_id']
    if existing:
        existing['priority'] = escalate_priority(existing.get('priority', 4), new_priority)
        existing['status'] = 'done' if self_test else 'ready'
        existing['lastNote'] = defect['failure'].get('summary', '')
        existing['retriggerCount'] = int(existing.get('retriggerCount', 1)) + 1
        existing['severity'] = PRIORITY_TO_SEVERITY[existing['priority']]
        existing['verify'] = defect.get('retest', {}).get('contract', existing.get('verify', 'reproduce and verify failure no longer occurs'))
        existing['nextStep'] = defect.get('recovery_attempt', {}).get('next_step', existing.get('nextStep', 'diagnose and remediate originating defect'))
        target_id = existing['id']
        action = 'reopened'
    else:
        item = {
            'id': defect['defect_id'],
            'priority': new_priority,
            'status': 'ready',
            'title': defect['failure'].get('summary', defect['defect_id']),
            'class': 'auto_defect',
            'executor': 'python3 projects/xzenia/execution/advance_bottleneck.py ' + defect['defect_id'],
            'verify': defect.get('retest', {}).get('contract', 'reproduce and verify failure no longer occurs'),
            'nextStep': defect.get('recovery_attempt', {}).get('next_step', 'diagnose and remediate originating defect'),
            'source': 'auto-defect',
            'source_state': defect.get('state', {}),
            'source_signature': {
                'source': defect.get('source', ''),
                'summary': defect.get('failure', {}).get('summary', ''),
                'error': defect.get('failure', {}).get('error', '')
            },
            'severity': defect['severity'],
            'retriggerCount': 1,
            'lastNote': defect['failure'].get('summary', '')
        }
        registry['items'].insert(0, item)

    registry['updatedAt'] = datetime.now().astimezone().isoformat()
    REGISTRY.write_text(json.dumps(registry, indent=2) + '\n')
    report = {
        'updatedAt': registry['updatedAt'],
        'action': action,
        'target': target_id,
        'priority': next((i['priority'] for i in registry['items'] if i['id'] == target_id), new_priority),
        'status': 'done and verified'
    }
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
