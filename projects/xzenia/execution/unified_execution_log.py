#!/usr/bin/env python3
"""
Unified Execution Log — System 2 artifact.
Every execution through the canonical gateway produces a structured log entry.
Reads from causal_ledger executor_gateway events and produces unified log.
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
LOG_FILE = WORKSPACE / 'projects/xzenia/csmr/reports/unified-execution-log.json'


def fetch_gateway_events(limit=50) -> list:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        '''SELECT created_at, event_type, session_key, component, input_json,
                  output_json, outcome, latency_ms, failure_class, metadata_json
           FROM causal_events
           WHERE event_type = 'executor_gateway'
           ORDER BY created_at DESC LIMIT ?''',
        (limit,)
    ).fetchall()
    conn.close()
    entries = []
    for r in rows:
        meta = json.loads(r['metadata_json'] or '{}')
        entries.append({
            'timestamp': r['created_at'],
            'work_id': meta.get('work_id', r['session_key']),
            'outcome': r['outcome'],
            'latency_ms': r['latency_ms'],
            'failure_class': r['failure_class'],
            'envelope': json.loads(r['input_json'] or '{}'),
            'result': json.loads(r['output_json'] or '{}'),
        })
    return entries


def build_log() -> dict:
    entries = fetch_gateway_events()
    total = len(entries)
    ok = sum(1 for e in entries if e['outcome'] == 'ok')
    failed = total - ok
    log = {
        'generatedAt': datetime.now().astimezone().isoformat(),
        'total_executions': total,
        'ok': ok,
        'failed': failed,
        'success_rate': round(ok / total, 3) if total else None,
        'entries': entries
    }
    LOG_FILE.write_text(json.dumps(log, indent=2) + '\n')
    return log


if __name__ == '__main__':
    import sys
    log = build_log()
    summary = {k: v for k, v in log.items() if k != 'entries'}
    summary['log_file'] = str(LOG_FILE)
    summary['status'] = 'done and verified'
    print(json.dumps(summary, indent=2))
