#!/usr/bin/env python3
import json
import sqlite3
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/ledger-write-probe.json'


def main():
    conn = sqlite3.connect(DB)
    conn.execute(
        'INSERT INTO causal_events (created_at, event_type, session_key, component, input_json, output_json, outcome, latency_ms, failure_class, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            datetime.now().astimezone().isoformat(), 'ledger_write_probe', 'local:probe', 'ledger_write_probe',
            json.dumps({'probe': True}), json.dumps({'probe': True}), 'ok', 1, None, json.dumps({'class': 'adversarial'})
        )
    )
    conn.commit()
    row = conn.execute("select event_type,outcome from causal_events where event_type='ledger_write_probe' order by id desc limit 1").fetchone()
    conn.close()
    passed = row == ('ledger_write_probe', 'ok')
    out = {'timestamp': datetime.now().astimezone().isoformat(), 'passed': passed, 'row': row, 'status': 'done and verified' if passed else 'partial'}
    OUT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
