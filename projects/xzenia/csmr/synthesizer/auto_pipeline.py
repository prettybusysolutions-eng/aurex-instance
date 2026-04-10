#!/usr/bin/env python3
import json
import sqlite3
import subprocess
import tempfile
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
GEN = WORKSPACE / 'projects/xzenia/csmr/synthesizer/generate_proposal_from_latest.py'
GATE_A = WORKSPACE / 'projects/xzenia/csmr/validator/validate_and_record.py'
GATE_B = WORKSPACE / 'projects/xzenia/csmr/validator/validate_gate_b_and_record.py'
GATE_C = WORKSPACE / 'projects/xzenia/csmr/validator/validate_gate_c_and_record.py'
PROMOTE = WORKSPACE / 'projects/xzenia/csmr/promoter/canary_promote.py'
EVAL = WORKSPACE / 'projects/xzenia/csmr/promoter/evaluate_canary.py'
FINAL = WORKSPACE / 'projects/xzenia/csmr/promoter/promote_or_rollback.py'
FINALIZE_APPLICATION = WORKSPACE / 'projects/xzenia/csmr/promoter/finalize_application.py'
APPLY = WORKSPACE / 'projects/xzenia/csmr/promoter/apply_to_target.py'
CONTINUITY_GUARD = WORKSPACE / 'projects/xzenia/scripts/continuity-guard.py'
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def current_status(proposal_id):
    conn = sqlite3.connect(DB)
    try:
        row = conn.execute('SELECT status FROM modification_proposals WHERE proposal_id=?', (proposal_id,)).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def checkpoint(phase, data):
    payload = json.dumps(data)
    return run(['python3', str(CONTINUITY_GUARD), 'save', phase, payload, payload])


def main():
    checkpoint('auto_pipeline:start', {'objective': 'run governed proposal pipeline with checkpointed continuity'})
    gen = run(['python3', str(GEN)])
    if gen.returncode != 0:
        print(json.dumps({'ok': False, 'stage': 'generate', 'stderr': gen.stderr}, indent=2))
        raise SystemExit(1)
    proposal = json.loads(gen.stdout)
    proposal_id = proposal['proposal_id']
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        f.write(json.dumps(proposal, indent=2))
        proposal_path = f.name

    results = {'proposal_id': proposal_id, 'proposal': proposal}
    checkpoint('auto_pipeline:proposal_generated', {'proposal_id': proposal_id, 'proposal': proposal})

    for name, script in [('gate_a', GATE_A), ('gate_b', GATE_B), ('gate_c', GATE_C)]:
        checkpoint(f'auto_pipeline:{name}:begin', {'proposal_id': proposal_id, 'stage': name})
        res = run(['python3', str(script), proposal_path])
        results[name] = {'code': res.returncode, 'stdout': res.stdout.strip(), 'stderr': res.stderr.strip()}
        checkpoint(f'auto_pipeline:{name}:end', {'proposal_id': proposal_id, 'stage': name, 'result': results[name]})
        if res.returncode != 0:
            results['final_status'] = current_status(proposal_id)
            print(json.dumps(results, indent=2))
            raise SystemExit(1)

    for name, script in [('canary_promote', PROMOTE), ('evaluate_canary', EVAL), ('finalize', FINAL)]:
        checkpoint(f'auto_pipeline:{name}:begin', {'proposal_id': proposal_id, 'stage': name})
        res = run(['python3', str(script), proposal_id])
        results[name] = {'code': res.returncode, 'stdout': res.stdout.strip(), 'stderr': res.stderr.strip()}
        checkpoint(f'auto_pipeline:{name}:end', {'proposal_id': proposal_id, 'stage': name, 'result': results[name]})
        if res.returncode != 0:
            results['final_status'] = current_status(proposal_id)
            print(json.dumps(results, indent=2))
            raise SystemExit(1)

    checkpoint('auto_pipeline:finalize_application:begin', {'proposal_id': proposal_id, 'stage': 'finalize_application'})
    finalize_application = run(['python3', str(FINALIZE_APPLICATION), proposal_id])
    results['finalize_application'] = {'code': finalize_application.returncode, 'stdout': finalize_application.stdout.strip(), 'stderr': finalize_application.stderr.strip()}
    checkpoint('auto_pipeline:finalize_application:end', {'proposal_id': proposal_id, 'stage': 'finalize_application', 'result': results['finalize_application']})
    if finalize_application.returncode != 0:
        results['final_status'] = current_status(proposal_id)
        print(json.dumps(results, indent=2))
        raise SystemExit(1)

    checkpoint('auto_pipeline:apply_to_target:begin', {'proposal_id': proposal_id, 'stage': 'apply_to_target'})
    apply = run(['python3', str(APPLY), proposal_id])
    results['apply_to_target'] = {'code': apply.returncode, 'stdout': apply.stdout.strip(), 'stderr': apply.stderr.strip()}
    checkpoint('auto_pipeline:apply_to_target:end', {'proposal_id': proposal_id, 'stage': 'apply_to_target', 'result': results['apply_to_target']})
    results['final_status'] = current_status(proposal_id)
    checkpoint('auto_pipeline:complete', {'proposal_id': proposal_id, 'final_status': results['final_status']})
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
