#!/usr/bin/env python3
import datetime as dt
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
GATE_A = WORKSPACE / 'projects/xzenia/csmr/validator/gate_a_schema.py'
LOG_REJECTION = WORKSPACE / 'projects/xzenia/csmr/ledger/log_rejection.py'


def set_status(conn, proposal_id, status):
    conn.execute('UPDATE modification_proposals SET status=? WHERE proposal_id=?', (status, proposal_id))
    conn.commit()


def main():
    if len(sys.argv) != 2:
        print('usage: validate_and_record.py <proposal.json>', file=sys.stderr)
        raise SystemExit(2)

    proposal_path = Path(sys.argv[1])
    proposal = json.loads(proposal_path.read_text())
    proposal_id = proposal['proposal_id']

    conn = sqlite3.connect(DB)
    try:
        cur = conn.execute('SELECT COUNT(*) FROM modification_proposals WHERE proposal_id=?', (proposal_id,))
        if cur.fetchone()[0] == 0:
            conn.execute(
                'INSERT INTO modification_proposals (created_at, proposal_id, proposal_json, status, source_event_id) VALUES (?, ?, ?, ?, ?)',
                (dt.datetime.now().astimezone().isoformat(), proposal_id, json.dumps(proposal), 'generated', None)
            )
            conn.commit()
        else:
            conn.execute('UPDATE modification_proposals SET proposal_json=? WHERE proposal_id=?', (json.dumps(proposal), proposal_id))
            conn.commit()

        gate = subprocess.run(['python3', str(GATE_A), str(proposal_path)], capture_output=True, text=True)
        payload = json.loads((gate.stdout or '{}').strip() or '{}')

        if gate.returncode == 0:
            set_status(conn, proposal_id, 'validated_gate_a')
            print(json.dumps({'ok': True, 'proposal_id': proposal_id, 'status': 'validated_gate_a', 'gate_a': payload}, indent=2))
            return

        errors = payload.get('errors', ['unknown_validation_failure'])
        rejection = {
            'proposal_id': proposal_id,
            'failed_gate': 'A',
            'violation_type': 'SchemaViolation',
            'violated_field': errors[0],
            'safe_range': None,
            'recommended_delta': 0.0,
            'detail': {'errors': errors}
        }
        rejection_path = Path('/tmp') / f'{proposal_id}-rejection.json'
        rejection_path.write_text(json.dumps(rejection, indent=2))
        subprocess.run(['python3', str(LOG_REJECTION), str(rejection_path)], check=False, capture_output=True, text=True)
        set_status(conn, proposal_id, 'rejected_gate_a')
        print(json.dumps({'ok': False, 'proposal_id': proposal_id, 'status': 'rejected_gate_a', 'gate_a': payload}, indent=2))
        raise SystemExit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
