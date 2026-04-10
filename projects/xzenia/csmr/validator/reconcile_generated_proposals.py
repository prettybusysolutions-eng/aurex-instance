#!/usr/bin/env python3
import json
import sqlite3
import subprocess
import tempfile
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
VALIDATE = WORKSPACE / 'projects/xzenia/csmr/validator/validate_and_record.py'


def main():
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT proposal_id, proposal_json FROM modification_proposals WHERE status='generated' ORDER BY id ASC").fetchall()
    conn.close()
    results = []
    for proposal_id, proposal_json in rows:
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            f.write(proposal_json)
            path = f.name
        run = subprocess.run(['python3', str(VALIDATE), path], capture_output=True, text=True)
        payload = {'proposal_id': proposal_id, 'code': run.returncode, 'stdout': run.stdout.strip(), 'stderr': run.stderr.strip()}
        results.append(payload)
    print(json.dumps({'count': len(results), 'results': results}, indent=2))


if __name__ == '__main__':
    main()
