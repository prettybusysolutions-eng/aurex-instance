#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
REPORT = WORKSPACE / 'reports' / 'residue-classifier-report.json'

RULES = {
    'canonical': ['STATE.md', 'NEXT-ACTION.md', 'ACTIVATION-REGISTRY.md'],
    'local_only_prefixes': ['memory/errors.md'],
    'runtime_prefixes': ['projects/xzenia/state/', 'logs/', 'data/'],
}


def classify(rel):
    if rel in RULES['canonical']:
        return 'canonical'
    if any(rel.startswith(p) for p in RULES['local_only_prefixes']):
        return 'local_only'
    if any(rel.startswith(p) for p in RULES['runtime_prefixes']):
        return 'runtime_or_state'
    return 'review_needed'


def run():
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(WORKSPACE.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(WORKSPACE).as_posix()
        if '.git/' in rel:
            continue
        rows.append({'path': rel, 'class': classify(rel)})
        if len(rows) >= 500:
            break
    out = {
        'generatedAt': datetime.now().astimezone().isoformat(),
        'safe': True,
        'destructiveActions': [],
        'sampled': len(rows),
        'rows': rows
    }
    REPORT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'generatedAt': out['generatedAt'], 'sampled': out['sampled'], 'safe': True}, indent=2))


if __name__ == '__main__':
    run()
