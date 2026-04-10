#!/usr/bin/env python3
import json
import subprocess

payload = {
    'source': 'exception',
    'state': {
        'executor': 'advance_bottleneck.py',
        'item_id': 'charter-system-1-closed-defect-loop'
    },
    'failure': {
        'summary': 'Synthetic executor failure on charter-system-1-closed-defect-loop',
        'error': 'intentional executor-failure test'
    },
    'recovery_attempt': {
        'next_step': 'rerun charter-system-1-closed-defect-loop through canonical executor and verify no failure'
    },
    'retest': {
        'contract': 'rerun charter-system-1-closed-defect-loop and verify failure no longer reproduces'
    }
}
run = subprocess.run(
    ['python3', '/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/defects/defect_detector.py'],
    input=json.dumps(payload), text=True, capture_output=True
)
print(run.stdout)
if run.returncode != 0:
    raise SystemExit(run.stderr)
