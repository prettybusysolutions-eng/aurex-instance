#!/usr/bin/env python3
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

DB = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/csmr/ledger/causal_ledger.sqlite')


def main():
    if len(sys.argv) != 2:
        print('usage: persist_proposal.py <proposal.json>', file=sys.stderr)
        raise SystemExit(2)
    proposal = json.loads(Path(sys.argv[1]).read_text())
    conn = sqlite3.connect(DB)
    try:
        conn.execute(
            'INSERT OR REPLACE INTO modification_proposals (created_at, proposal_id, proposal_json, status, source_event_id) VALUES (?, ?, ?, ?, ?)',
            (
                dt.datetime.now().astimezone().isoformat(),
                proposal['proposal_id'],
                json.dumps(proposal),
                'generated',
                None,
            ),
        )
        conn.commit()
        print(json.dumps({'ok': True, 'proposal_id': proposal['proposal_id']}, indent=2))
    finally:
        conn.close()


if __name__ == '__main__':
    main()
