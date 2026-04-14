#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

BASE = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node')
STATE = BASE / 'thermal-state.json'
PLAN = BASE / 'migration-plan.md'
threshold = 85.0

sample = {
    'capturedAt': datetime.now().astimezone().isoformat(),
    'thresholdC': threshold,
    'status': 'observation_only',
    'recommendation': 'no_migration_action_without_explicit_approval',
}
STATE.write_text(json.dumps(sample, indent=2) + '\n')

if sample['status'] == 'migration_required':
    PLAN.write_text(
        '# Migration Plan\n\n'
        '- trigger: thermal bottleneck\n'
        '- candidate targets: Akash, Render\n'
        '- next step: operator approval before paid deployment\n'
    )

print(json.dumps(sample, indent=2))
