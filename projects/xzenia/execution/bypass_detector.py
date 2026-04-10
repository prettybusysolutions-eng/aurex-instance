#!/usr/bin/env python3
"""
Bypass Detector — System 2 gate artifact.
Detects direct execution attempts that bypass the executor_gateway.
Emits a warning and auto-routes through executor_gateway.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
LOG = WORKSPACE / 'projects/xzenia/csmr/reports/bypass-log.json'
REPORT = WORKSPACE / 'projects/xzenia/csmr/reports/bypass-audit-report.json'

# Known legitimate bypass paths (direct scripts called by executor_gateway itself)
ALLOWED_DIRECT = {
    'advance_bottleneck.py',
    'checkpoint_contract.py',
    'work_envelope.py',
    'continuity-guard.py',
    'defect_detector.py',
    'executor_gateway.py',
    'unified_execution_log.py',
    'bypass_detector.py',
    'token_budget_guard.py',
}

# Known side paths that should always go through gateway
GOVERNED_SCRIPTS = {
    'run_autonomous_cycle.py',
    'autonomous_continue.py',
    'inject_synthetic_defect.py',
    'create_executor_failure_defect.py',
}


def load_log():
    return json.loads(LOG.read_text()) if LOG.exists() else {'entries': []}


def save_log(data):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text(json.dumps(data, indent=2) + '\n')


def warn_and_route(script_name: str, work_id: str) -> dict:
    """Emit warning and auto-route through executor_gateway."""
    entry = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'type': 'bypass_detected',
        'script': script_name,
        'work_id': work_id,
        'action': 'auto_routed_to_gateway',
        'warning': f'Direct execution of {script_name} bypasses canonical executor. Auto-routing through executor_gateway.'
    }
    log = load_log()
    log['entries'].append(entry)
    save_log(log)
    print(json.dumps({'warning': entry['warning'], 'routing': 'executor_gateway', 'work_id': work_id}, indent=2),
          file=sys.stderr)

    # Auto-route through gateway
    result = subprocess.run(
        ['python3', 'projects/xzenia/execution/executor_gateway.py', work_id],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )
    return {
        'bypassed_script': script_name,
        'work_id': work_id,
        'routed_via': 'executor_gateway',
        'result_code': result.returncode,
        'stdout': result.stdout.strip(),
        'stderr': result.stderr.strip()
    }


def audit_side_paths() -> dict:
    """Scan execution scripts and classify each as governed/allowed/unreviewed."""
    exec_dir = WORKSPACE / 'projects/xzenia/execution'
    scripts = list(exec_dir.glob('*.py'))
    governed = []
    allowed = []
    unreviewed = []

    for s in scripts:
        name = s.name
        if name in ALLOWED_DIRECT:
            allowed.append(name)
        elif name in GOVERNED_SCRIPTS:
            governed.append(name)
        elif name in ('bypass_detector.py', 'token_budget_guard.py'):
            allowed.append(name)
        else:
            unreviewed.append(name)

    report = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'total_scripts': len(scripts),
        'governed_must_use_gateway': governed,
        'allowed_direct': allowed,
        'unreviewed': unreviewed,
        'bypass_log_entries': len(load_log().get('entries', [])),
        'status': 'done and verified' if not unreviewed else 'unreviewed_paths_exist',
        'verdict': 'zero_unresolved_bypasses' if not unreviewed else f'{len(unreviewed)}_paths_need_review'
    }
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'audit':
        print(json.dumps(audit_side_paths(), indent=2))
    elif len(sys.argv) >= 3 and sys.argv[1] == 'check':
        script = sys.argv[2]
        work_id = sys.argv[3] if len(sys.argv) >= 4 else 'unknown'
        if script in ALLOWED_DIRECT:
            print(json.dumps({'status': 'allowed', 'script': script}, indent=2))
        else:
            result = warn_and_route(script, work_id)
            print(json.dumps(result, indent=2))
    else:
        print('usage: bypass_detector.py audit | check <script> [work_id]')
        sys.exit(1)
