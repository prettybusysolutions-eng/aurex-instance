#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
OUT = WORKSPACE / 'projects/xzenia/recovery/restart-resume-verification.json'
CHECKPOINT = WORKSPACE / 'projects/xzenia/state/latest-checkpoint.json'
INTERRUPTION = WORKSPACE / 'projects/xzenia/state/interruption-checkpoint.json'


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE))


def main():
    steps = []
    for label, cmd in [
        ('boot_trigger', ['python3', 'projects/xzenia/tier1/boot_trigger.py']),
        ('reconcile_state', ['python3', 'projects/xzenia/recovery/reconcile_state.py']),
        ('status_snapshot', ['python3', 'projects/xzenia/tier1/status_snapshot.py'])
    ]:
        res = run(cmd)
        steps.append({
            'label': label,
            'code': res.returncode,
            'stdout': res.stdout.strip(),
            'stderr': res.stderr.strip()
        })
        if res.returncode != 0:
            raise SystemExit(json.dumps({'failed_step': label, 'stderr': res.stderr.strip()}, indent=2))

    payload = {
        'verified_at': datetime.now().astimezone().isoformat(),
        'checkpoint_exists': CHECKPOINT.exists(),
        'interruption_checkpoint_exists': INTERRUPTION.exists(),
        'steps': steps,
        'status': 'done and verified'
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
