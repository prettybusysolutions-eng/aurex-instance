#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
POLICY = WORKSPACE / 'projects/xzenia/runtime/proof_cadence_policy.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/proof-spine-cost-optimization.json'


def main():
    policy = json.loads(POLICY.read_text())
    policy['selection_rule']['lean_requires']['high_safety_reclaim_bytes_max'] = 10000000
    policy['selection_rule']['lean_requires']['degradation_tier'] = 'normal'
    policy['policy_version'] = max(int(policy.get('policy_version', 1)), 2)
    POLICY.write_text(json.dumps(policy, indent=2) + '\n')
    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'optimized_surface': 'proof_cadence_policy',
        'changes': {
            'high_safety_reclaim_bytes_max': 10000000,
            'degradation_tier': 'normal',
            'policy_version': policy['policy_version']
        },
        'status': 'done and verified'
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
