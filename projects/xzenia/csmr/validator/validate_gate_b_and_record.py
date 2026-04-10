#!/usr/bin/env python3
import datetime as dt
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
GATE_B = WORKSPACE / 'projects/xzenia/csmr/validator/gate_b_simulation.py'
LOG_REJECTION = WORKSPACE / 'projects/xzenia/csmr/ledger/log_rejection.py'
REPORT_DIR = WORKSPACE / 'projects/xzenia/csmr/reports'


def infer_surface_id(proposal):
    target = proposal.get('target', 'analysis')
    mapping = {
        'canonical-processor.execution-guidance': 'canonical-processor.general-guidance',
        'canonical-processor.general-guidance': 'canonical-processor.general-guidance',
        'projects/xzenia/orchestration/resilience-policy.json': 'projects/xzenia/orchestration/resilience-policy',
        'executor_gateway': 'executor_gateway',
        'integrity_check': 'integrity_check',
        'resource-monitor': 'resource-monitor',
        'degradation_path': 'degradation_path',
        'cost_accounting': 'cost_accounting',
    }
    return mapping.get(target, target)


def set_status(conn, proposal_id, status):
    conn.execute('UPDATE modification_proposals SET status=? WHERE proposal_id=?', (status, proposal_id))
    conn.commit()


def main():
    if len(sys.argv) != 2:
        print('usage: validate_gate_b_and_record.py <proposal.json>', file=sys.stderr)
        raise SystemExit(2)
    proposal_path = Path(sys.argv[1])
    proposal = json.loads(proposal_path.read_text())
    proposal_id = proposal['proposal_id']

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    run = subprocess.run(['python3', str(GATE_B), str(proposal_path)], capture_output=True, text=True)
    report = json.loads(run.stdout.strip())
    report_path = REPORT_DIR / f'{proposal_id}-simulation-report.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')

    conn = sqlite3.connect(DB)
    try:
        if run.returncode == 0:
            set_status(conn, proposal_id, 'validated_gate_b')
            print(json.dumps({'ok': True, 'proposal_id': proposal_id, 'status': 'validated_gate_b', 'report': str(report_path)}, indent=2))
            return
        rejection = {
            'proposal_id': proposal_id,
            'failed_gate': 'B',
            'violation_type': 'SimulationRegression',
            'violated_field': 'simulated_failure_rate',
            'safe_range': None,
            'recommended_delta': 0.0,
            'detail': report,
        }
        rejection_path = Path('/tmp') / f'{proposal_id}-gate-b-rejection.json'
        rejection_path.write_text(json.dumps(rejection, indent=2))
        subprocess.run(['python3', str(LOG_REJECTION), str(rejection_path)], check=False, capture_output=True, text=True)
        set_status(conn, proposal_id, 'rejected_gate_b')
        print(json.dumps({'ok': False, 'proposal_id': proposal_id, 'status': 'rejected_gate_b', 'report': str(report_path)}, indent=2))
        raise SystemExit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
