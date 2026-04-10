#!/usr/bin/env python3
import json
import subprocess

payload = {
    'source': 'verification_failure',
    'state': {
        'phase': 'charter-system-1-test',
        'origin': 'synthetic_injection',
        'self_test': True
    },
    'failure': {
        'summary': 'Synthetic defect injection for closed defect loop verification',
        'error': 'intentional synthetic failure'
    },
    'recovery_attempt': {
        'next_step': 'verify defect record appears in registry and becomes governed work item'
    },
    'retest': {
        'contract': 'inject synthetic failure and verify registry insertion within one cycle'
    }
}

run = subprocess.run(
    ['python3', '/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/defects/defect_detector.py'],
    input=json.dumps(payload),
    text=True,
    capture_output=True
)
print(run.stdout)
if run.returncode != 0:
    raise SystemExit(run.stderr)
