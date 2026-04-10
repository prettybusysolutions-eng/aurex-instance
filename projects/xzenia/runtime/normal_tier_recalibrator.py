#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
POLICY = WORKSPACE / 'projects/xzenia/charter/degradation_policy.json'
SOAK = WORKSPACE / 'projects/xzenia/csmr/reports/20-cycle-soak-assessment.json'
SUP = WORKSPACE / 'projects/xzenia/csmr/reports/unified-supervisor-health.json'
RES = WORKSPACE / 'projects/xzenia/csmr/reports/resource-monitor.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/normal-tier-recalibration.json'


def main():
    policy = json.loads(POLICY.read_text())
    soak = json.loads(SOAK.read_text())
    sup = json.loads(SUP.read_text())
    res = json.loads(RES.read_text())

    eligible = (
        soak.get('assessment') == 'stable' and
        sup.get('overall') == 'pass' and
        len(sup.get('contradictions', [])) == 0 and
        float(res.get('disk_free_gib', 0)) >= 5.0 and
        float(res.get('resource_pressure', 1)) <= 0.96
    )

    if eligible:
        policy['policy_version'] = 3
        policy['tiers'][0]['usedRatioMax'] = 0.96
        policy['tiers'][0]['freeGibMin'] = 5.0
        POLICY.write_text(json.dumps(policy, indent=2) + '\n')

    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'eligible': eligible,
        'new_policy_version': policy.get('policy_version'),
        'normal_usedRatioMax': policy['tiers'][0]['usedRatioMax'],
        'normal_freeGibMin': policy['tiers'][0]['freeGibMin'],
        'status': 'done and verified' if eligible else 'blocked'
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if eligible else 1)


if __name__ == '__main__':
    main()
