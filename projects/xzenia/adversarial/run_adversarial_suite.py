#!/usr/bin/env python3
import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
REGISTRY = WORKSPACE / 'projects/xzenia/orchestration/bottleneck-registry.json'
QUEUE = WORKSPACE / 'projects/xzenia/state/resume-queue.json'
CHECKPOINT = WORKSPACE / 'projects/xzenia/state/latest-checkpoint.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/adversarial-suite-report.json'


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE))


def scenario_corrupt_queue_detection():
    original = QUEUE.read_text()
    QUEUE.write_text('{bad json\n')
    try:
        res = run(['python3', 'projects/xzenia/supervisor/unified_supervisor.py'])
        return {'name': 'corrupt_queue_detection', 'passed': res.returncode != 0, 'stdout': res.stdout.strip(), 'stderr': res.stderr.strip()}
    finally:
        QUEUE.write_text(original)


def scenario_missing_checkpoint_recovery():
    backup = CHECKPOINT.read_text() if CHECKPOINT.exists() else None
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()
    try:
        res = run(['python3', 'projects/xzenia/supervisor/unified_supervisor.py'])
        ok = res.returncode == 0 and '"checkpoint"' in res.stdout
        return {'name': 'missing_checkpoint_recovery', 'passed': ok, 'stdout': res.stdout.strip(), 'stderr': res.stderr.strip()}
    finally:
        if backup is not None:
            CHECKPOINT.write_text(backup)


def scenario_storage_governor_absent():
    backup = OUT.parent / 'storage-governor.json'
    sg = WORKSPACE / 'projects/xzenia/csmr/reports/storage-governor.json'
    saved = sg.read_text() if sg.exists() else None
    if sg.exists():
        sg.unlink()
    try:
        res = run(['python3', 'projects/xzenia/supervisor/unified_supervisor.py'])
        ok = res.returncode == 0 and 'storage_governor' in res.stdout and 'missing' in res.stdout
        return {'name': 'missing_storage_governor', 'passed': ok, 'stdout': res.stdout.strip(), 'stderr': res.stderr.strip()}
    finally:
        if saved is not None:
            sg.write_text(saved)


def scenario_duplicate_defect_reopen():
    original_registry = REGISTRY.read_text()
    original_queue = QUEUE.read_text() if QUEUE.exists() else None
    try:
        res1 = run(['python3', 'projects/xzenia/execution/inject_synthetic_defect.py'])
        res2 = run(['python3', 'projects/xzenia/execution/inject_synthetic_defect.py'])
        reg = json.loads(REGISTRY.read_text())
        items = [i for i in reg['items'] if i.get('class') == 'auto_defect' and 'Synthetic defect injection for closed defect loop verification' in i.get('title', '')]
        report_path = WORKSPACE / 'projects/xzenia/csmr/reports/defect-registry-writes.json'
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        ok = (
            len(items) >= 1 and
            max(int(i.get('retriggerCount', 0)) for i in items) >= 2 and
            any(i.get('status') == 'done' for i in items) and
            report.get('action') == 'reopened'
        )
        return {'name': 'duplicate_defect_reopen', 'passed': ok, 'stdout': '\n'.join([res1.stdout.strip(), res2.stdout.strip()]), 'stderr': '\n'.join([res1.stderr.strip(), res2.stderr.strip()])}
    finally:
        REGISTRY.write_text(original_registry)
        if original_queue is not None:
            QUEUE.write_text(original_queue)


def scenario_sqlite_contention_probe():
    res = run(['python3', 'projects/xzenia/adversarial/sqlite_contention_probe.py'])
    ok = res.returncode == 0
    return {'name': 'sqlite_contention_probe', 'passed': ok, 'stdout': res.stdout.strip(), 'stderr': res.stderr.strip()}


def scenario_partial_write_probe():
    res = run(['python3', 'projects/xzenia/adversarial/partial_write_probe.py'])
    ok = res.returncode == 0
    return {'name': 'partial_write_probe', 'passed': ok, 'stdout': res.stdout.strip(), 'stderr': res.stderr.strip()}


def scenario_queue_checkpoint_contradiction_probe():
    res = run(['python3', 'projects/xzenia/adversarial/queue_checkpoint_contradiction_probe.py'])
    ok = res.returncode == 0
    return {'name': 'queue_checkpoint_contradiction_probe', 'passed': ok, 'stdout': res.stdout.strip(), 'stderr': res.stderr.strip()}


def scenario_ledger_write_probe():
    res = run(['python3', 'projects/xzenia/adversarial/ledger_write_probe.py'])
    ok = res.returncode == 0
    return {'name': 'ledger_write_probe', 'passed': ok, 'stdout': res.stdout.strip(), 'stderr': res.stderr.strip()}


def main():
    scenarios = [
        scenario_corrupt_queue_detection,
        scenario_missing_checkpoint_recovery,
        scenario_storage_governor_absent,
        scenario_duplicate_defect_reopen,
        scenario_sqlite_contention_probe,
        scenario_partial_write_probe,
        scenario_ledger_write_probe,
    ]
    results = []
    for fn in scenarios:
        try:
            results.append(fn())
        except Exception as e:
            results.append({'name': fn.__name__, 'passed': False, 'error': str(e)})
    payload = {
        'contract_mode': 'canonical-supervisor',
        'retired_semantics': ['queue-checkpoint-only contradiction assumptions'],
        'timestamp': datetime.now().astimezone().isoformat(),
        'results': results,
        'passed': all(r.get('passed') for r in results),
        'status': 'done and verified' if all(r.get('passed') for r in results) else 'partial'
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if payload['passed'] else 1)


if __name__ == '__main__':
    main()
