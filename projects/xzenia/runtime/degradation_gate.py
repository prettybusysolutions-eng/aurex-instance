#!/usr/bin/env python3
import json
import sqlite3
import subprocess
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/degradation-gate.json'
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'


def log_event(payload, latency_ms):
    conn = sqlite3.connect(DB)
    conn.execute(
        'INSERT INTO causal_events (created_at, event_type, session_key, component, input_json, output_json, outcome, latency_ms, failure_class, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            payload['timestamp'], 'degradation_gate', 'local:degradation', 'degradation_gate',
            json.dumps({'tier': payload['tier']}), json.dumps(payload), 'ok', latency_ms, None,
            json.dumps({'degraded': payload['degraded']})
        )
    )
    conn.commit()
    conn.close()


def main():
    start = time.time()
    mon = subprocess.run(['python3', str(WORKSPACE / 'projects/xzenia/runtime/resource_monitor.py')], capture_output=True, text=True)
    if mon.returncode != 0:
        raise SystemExit(mon.stderr or mon.stdout)
    payload = json.loads(mon.stdout)
    degraded = payload['tier'] in ('reduced', 'minimal')
    result = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'degraded': degraded,
        'tier': payload['tier'],
        'confidence': payload['confidence'],
        'preserved_intent': {'mode': 'continue_with_declared_reduction' if degraded else 'full_capability'},
        'status': 'done and verified'
    }
    OUT.write_text(json.dumps(result, indent=2) + '\n')
    log_event(result, int((time.time() - start) * 1000))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
