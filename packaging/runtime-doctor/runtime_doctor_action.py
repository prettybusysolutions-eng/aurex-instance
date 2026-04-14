#!/usr/bin/env python3
import json
import os
from datetime import datetime
from pathlib import Path

workspace = Path(os.getenv('INPUT_WORKSPACE-PATH', '.'))
output_path = Path(os.getenv('INPUT_OUTPUT-PATH', 'runtime-doctor-report.json'))
pro_link = 'https://buy.stripe.com/4gM28q7W0agjbg4bkG0kE06'

checks = [
    ('workspace-memory', workspace / 'memory'),
    ('continuity-state', workspace / 'projects/xzenia/state/continuity-state.json'),
    ('autofallback-state', workspace / 'projects/xzenia/state/autofallback-state.json'),
]
rows = []
critical = False
for name, path in checks:
    exists = path.exists()
    rows.append({'check': name, 'path': str(path), 'exists': exists})
    if not exists:
        critical = True

out = {
    'generatedAt': datetime.now().astimezone().isoformat(),
    'critical': critical,
    'checks': rows,
}
output_path.write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
if critical:
    print(f'Critical drift detected. For an automated repair plan, upgrade to Pro: {pro_link}')
