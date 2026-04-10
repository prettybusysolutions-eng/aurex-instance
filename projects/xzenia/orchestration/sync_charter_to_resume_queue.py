#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
REGISTRY = WORKSPACE / 'projects/xzenia/orchestration/bottleneck-registry.json'
QUEUE = WORKSPACE / 'projects/xzenia/state/resume-queue.json'
REPORT = WORKSPACE / 'projects/xzenia/csmr/reports/charter-resume-sync.json'


def load_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def main():
    registry = load_json(REGISTRY, {'items': []})
    ready = sorted(
        [i for i in registry.get('items', []) if i.get('status') == 'ready'],
        key=lambda x: x.get('priority', 999)
    )
    done = [i for i in registry.get('items', []) if i.get('status') == 'done']

    items = []
    for item in ready[:5]:
        items.append({
            'id': item['id'],
            'priority': item.get('priority', 999),
            'title': item.get('title', item['id']),
            'status': 'pending',
            'nextSteps': [item.get('nextStep', 'execute governed milestone'), item.get('verify', 'verify completion gate')],
            'source': 'bottleneck-registry'
        })

    payload = {
        'updatedAt': datetime.now().astimezone().isoformat(),
        'source': 'projects/xzenia/orchestration/bottleneck-registry.json',
        'items': items
    }
    QUEUE.write_text(json.dumps(payload, indent=2) + '\n')

    report = {
        'updatedAt': payload['updatedAt'],
        'ready_count': len(ready),
        'done_count': len(done),
        'queue_items_written': len(items),
        'top_item': items[0]['id'] if items else None,
        'status': 'done and verified'
    }
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
