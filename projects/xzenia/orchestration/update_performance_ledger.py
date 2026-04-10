#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/state/performance-ledger.json')


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: update_performance_ledger.py metric-name [delta] [note]')

    metric = sys.argv[1]
    delta = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    note = sys.argv[3] if len(sys.argv) > 3 else None

    data = json.loads(LEDGER.read_text())
    metrics = data.setdefault('metrics', {})
    if metric not in metrics:
        metrics[metric] = 0
    metrics[metric] += delta
    data['lastUpdated'] = datetime.now(timezone.utc).isoformat()
    if note:
        data.setdefault('notes', []).append({
            'timestamp': data['lastUpdated'],
            'metric': metric,
            'delta': delta,
            'note': note,
        })
    LEDGER.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
