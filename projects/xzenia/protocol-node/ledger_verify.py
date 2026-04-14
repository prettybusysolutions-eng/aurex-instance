#!/usr/bin/env python3
import json
from pathlib import Path

ledger = Path('/Users/marcuscoarchitect/.openclaw/workspace/private/billing-ledger.jsonl')
summary = {'exists': ledger.exists(), 'debug_rows': 0, 'real_rows': 0}
if ledger.exists():
    for line in ledger.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get('debug'):
            summary['debug_rows'] += 1
        else:
            summary['real_rows'] += 1
print(json.dumps(summary, indent=2))
