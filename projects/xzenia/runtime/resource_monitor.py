#!/usr/bin/env python3
import json
import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
POLICY = WORKSPACE / 'projects/xzenia/charter/degradation_policy.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/resource-monitor.json'
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'


def select_tier(policy, used_ratio, free_gib):
    for tier in policy['tiers']:
        if used_ratio <= float(tier['usedRatioMax']) and free_gib >= float(tier['freeGibMin']):
            return tier
    return policy['tiers'][-1]


def log_event(payload, latency_ms):
    conn = sqlite3.connect(DB)
    conn.execute(
        'INSERT INTO causal_events (created_at, event_type, session_key, component, input_json, output_json, outcome, latency_ms, failure_class, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            payload['timestamp'], 'resource_monitor', 'local:resource', 'resource_monitor',
            json.dumps({'policy_version': payload['policy_version']}), json.dumps(payload), 'ok', latency_ms, None,
            json.dumps({'tier': payload['tier']})
        )
    )
    conn.commit()
    conn.close()


def main():
    start = time.time()
    policy = json.loads(POLICY.read_text())
    total, used, free = shutil.disk_usage(str(Path.home()))
    used_ratio = round(used / total, 4)
    free_gib = round(free / 1024 / 1024 / 1024, 3)
    selected = select_tier(policy, used_ratio, free_gib)
    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'disk_total': total,
        'disk_used': used,
        'disk_free': free,
        'resource_pressure': used_ratio,
        'disk_free_gib': free_gib,
        'tier': selected['name'],
        'confidence': selected['confidence'],
        'behavior': selected['behavior'],
        'policy_version': policy.get('policy_version', 1)
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    log_event(payload, int((time.time() - start) * 1000))
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
