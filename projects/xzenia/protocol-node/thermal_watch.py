#!/usr/bin/env python3
import json
import os
from datetime import datetime
from pathlib import Path

STATE = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/thermal-state.json')
threshold = 85.0
sample = {
    'capturedAt': datetime.now().astimezone().isoformat(),
    'thresholdC': threshold,
    'status': 'observation_only',
    'recommendation': 'no_migration_action_without_explicit_approval',
}
STATE.write_text(json.dumps(sample, indent=2) + '\n')
print(json.dumps(sample, indent=2))
