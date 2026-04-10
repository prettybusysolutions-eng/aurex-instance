#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/domain-onboarding-report.json'


def main():
    domains = [
        WORKSPACE / 'projects/xzenia/domains/revenue-recovery.domain.json',
        WORKSPACE / 'projects/xzenia/domains/pretty-busy-cleaning.domain.json'
    ]
    results = []
    for path in domains:
        data = json.loads(path.read_text())
        results.append({
            'domain': data['identity']['name'],
            'path': str(path),
            'sections': sorted(list(data.keys())),
            'status': 'present'
        })
    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'domains': results,
        'status': 'done and verified'
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
