#!/usr/bin/env python3
import json
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'


def log_gateway_event(work_item_id, envelope, result, latency_ms):
    conn = sqlite3.connect(DB)
    conn.execute(
        'INSERT INTO causal_events (created_at, event_type, session_key, component, input_json, output_json, outcome, latency_ms, failure_class, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            datetime.now().astimezone().isoformat(),
            'executor_gateway',
            f'gateway:{work_item_id}',
            'executor_gateway',
            json.dumps(envelope),
            json.dumps(result),
            'ok' if result['result_code'] == 0 else 'failed',
            latency_ms,
            None if result['result_code'] == 0 else 'gateway_or_work_failure',
            json.dumps({'work_id': work_item_id})
        )
    )
    conn.commit()
    conn.close()


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: executor_gateway.py <work_item_id>')
    work_item_id = sys.argv[1]
    envelope = {
        'work_id': work_item_id,
        'source': 'gateway',
        'priority': 1,
        'checkpoint_state': {'entrypoint': 'executor_gateway.py'},
        'expected_outcome': {'status': 'done and verified'},
        'rollback_plan': {'mode': 'registry_status_revert'},
        'verification_contract': {'path': 'canonical-executor'}
    }
    env = subprocess.run(['python3', 'projects/xzenia/execution/work_envelope.py'], input=json.dumps(envelope), text=True, capture_output=True, cwd=str(WORKSPACE))
    if env.returncode != 0:
        raise SystemExit(env.stderr or env.stdout)
    pre = subprocess.run(['python3', 'projects/xzenia/execution/checkpoint_contract.py', 'pre'], input=env.stdout, text=True, capture_output=True, cwd=str(WORKSPACE))
    if pre.returncode != 0:
        raise SystemExit(pre.stderr or pre.stdout)

    start = time.time()
    run = subprocess.run(['python3', 'projects/xzenia/execution/advance_bottleneck.py', work_item_id], capture_output=True, text=True, cwd=str(WORKSPACE))
    latency_ms = int((time.time() - start) * 1000)

    result = {'work_id': work_item_id, 'result_code': run.returncode, 'stdout': run.stdout.strip(), 'stderr': run.stderr.strip()}
    post = subprocess.run(['python3', 'projects/xzenia/execution/checkpoint_contract.py', 'post'], input=json.dumps(result), text=True, capture_output=True, cwd=str(WORKSPACE))
    if post.returncode != 0:
        raise SystemExit(post.stderr or post.stdout)

    log_gateway_event(work_item_id, envelope, result, latency_ms)
    print(json.dumps({'status': 'done and verified' if run.returncode == 0 else 'attempted and failed', 'work_id': work_item_id, 'latency_ms': latency_ms, 'stdout': run.stdout.strip(), 'stderr': run.stderr.strip()}, indent=2))
    raise SystemExit(run.returncode)


if __name__ == '__main__':
    main()
