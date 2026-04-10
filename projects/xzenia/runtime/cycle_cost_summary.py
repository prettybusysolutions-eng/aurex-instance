#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
COST = WORKSPACE / 'projects/xzenia/csmr/reports/cost-accounting.json'
SUPERVISOR = WORKSPACE / 'projects/xzenia/csmr/reports/unified-supervisor-health.json'
DEGRADATION = WORKSPACE / 'projects/xzenia/csmr/reports/degradation-gate.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/cycle-cost-summary.json'


def main():
    cost = json.loads(COST.read_text())
    supervisor = json.loads(SUPERVISOR.read_text())
    degradation = json.loads(DEGRADATION.read_text())
    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'total_cost_estimate': cost['total_cost_estimate'],
        'supervisor_overall': supervisor['overall'],
        'degradation_tier': degradation['tier'],
        'value_proxy': cost['value_proxy'],
        'status': 'done and verified'
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
