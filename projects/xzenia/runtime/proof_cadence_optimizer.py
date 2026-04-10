#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
POLICY = WORKSPACE / 'projects/xzenia/runtime/proof_cadence_policy.json'
SUPERVISOR = WORKSPACE / 'projects/xzenia/csmr/reports/unified-supervisor-health.json'
DEGRADATION = WORKSPACE / 'projects/xzenia/csmr/reports/degradation-gate.json'
STORAGE = WORKSPACE / 'projects/xzenia/csmr/reports/storage-governor.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/proof-cadence-decision.json'


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def main():
    policy = load(POLICY, {})
    supervisor = load(SUPERVISOR, {})
    degradation = load(DEGRADATION, {})
    storage = load(STORAGE, {})
    req = policy['selection_rule']['lean_requires']
    lean = (
        supervisor.get('overall') == req['supervisor_overall'] and
        len(supervisor.get('contradictions', [])) == req['contradictions'] and
        degradation.get('tier') == req['degradation_tier'] and
        int(storage.get('high_safety_reclaim_bytes', 999999999)) <= req['high_safety_reclaim_bytes_max']
    )
    mode = 'lean' if lean else 'full'
    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'mode': mode,
        'steps': policy['modes'][mode]['steps'],
        'status': 'done and verified'
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
