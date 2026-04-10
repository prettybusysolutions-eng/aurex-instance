#!/usr/bin/env python3
import json
from pathlib import Path

QUEUE = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/state/resume-queue.json')


def main():
    queue = json.loads(QUEUE.read_text()) if QUEUE.exists() else {"items": []}
    pending = sorted([i for i in queue.get('items', []) if i.get('status') == 'pending'], key=lambda x: x.get('priority', 999))
    if not pending:
        print(json.dumps({'status': 'idle', 'message': 'No pending resumable intent.'}, indent=2))
        return
    print(json.dumps({'status': 'resume', 'item': pending[0]}, indent=2))


if __name__ == '__main__':
    main()
