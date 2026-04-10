#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
CHECKPOINT = WORKSPACE / 'projects/xzenia/state/latest-checkpoint.json'
QUEUE = WORKSPACE / 'projects/xzenia/state/resume-queue.json'
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
PROMOTIONS = WORKSPACE / 'projects/xzenia/csmr/promotions'


def main():
    checkpoint = json.loads(CHECKPOINT.read_text()) if CHECKPOINT.exists() else {}
    queue = json.loads(QUEUE.read_text()) if QUEUE.exists() else {"items": []}
    conn = sqlite3.connect(DB)
    latest = conn.execute('SELECT proposal_id, status FROM modification_proposals ORDER BY id DESC LIMIT 5').fetchall()
    conn.close()
    promoted = sorted([p.name for p in PROMOTIONS.glob('*canary-result.json')]) if PROMOTIONS.exists() else []
    print(json.dumps({
        'checkpointPhase': checkpoint.get('phase'),
        'checkpointStatus': checkpoint.get('status'),
        'pendingQueue': [i for i in queue.get('items', []) if i.get('status') == 'pending'],
        'latestProposals': latest,
        'promotionArtifacts': promoted[-5:]
    }, indent=2))


if __name__ == '__main__':
    main()
