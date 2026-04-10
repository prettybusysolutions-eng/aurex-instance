#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'state'
JSON_PATH = STATE / 'system-truth.json'
DIRECTIVES_PATH = STATE / 'execution-directives.json'
MD_PATH = ROOT / 'SYSTEM-TRUTH.md'


def load_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def render_md(data: dict) -> str:
    lines = [
        '# Xzenia System Truth',
        '',
        f"Last updated: {data.get('updatedAt', 'unknown')}",
        f"Status: {data.get('status', 'unknown')}",
        '',
        '## Purpose',
        data.get('purpose', ''),
        '',
        '## Identity'
    ]
    for k, v in data.get('identity', {}).items():
        lines.append(f'- {k}: {v}')
    if data.get('executionDirectives'):
        lines += ['', '## Execution Directives']
        for k, v in data.get('executionDirectives', {}).items():
            lines.append(f'- {k}: {v}')
    if data.get('verifiedSystems'):
        lines += ['', '## Verified Systems']
        for k, v in data.get('verifiedSystems', {}).items():
            lines.append(f'- {k}: {"verified" if v else "unverified"}')
    for title, key in [
        ('Production Leaning', 'productionLeaning'),
        ('Staleness', 'staleness'),
        ('Runtime Bottlenecks', 'runtimeBottlenecks'),
        ('Operating Rules', 'operatingRules'),
        ('Next Actions', 'nextActions')
    ]:
        values = data.get(key, [])
        if values:
            lines += ['', f'## {title}']
            for item in values:
                lines.append(f'- {item}')
    routing = data.get('routingIntent', {})
    if routing:
        lines += ['', '## Routing Intent']
        for k, v in routing.items():
            if isinstance(v, list):
                lines.append(f'- {k}:')
                for item in v:
                    lines.append(f'  - {item}')
            else:
                lines.append(f'- {k}: {v}')
    contract = data.get('updateContract', {})
    if contract:
        lines += ['', '## Update Contract']
        for k, v in contract.items():
            if isinstance(v, list):
                lines.append(f'- {k}:')
                for item in v:
                    lines.append(f'  - {item}')
            else:
                lines.append(f'- {k}: {v}')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    data = load_json(JSON_PATH)
    directives = load_json(DIRECTIVES_PATH)
    if directives.get('directives'):
        data['executionDirectives'] = directives['directives']
    data['updatedAt'] = datetime.now().astimezone().isoformat()
    save_json(JSON_PATH, data)
    MD_PATH.write_text(render_md(data))
    print(json.dumps({
        'updated_json': str(JSON_PATH),
        'updated_md': str(MD_PATH),
        'timestamp': data['updatedAt']
    }, indent=2))


if __name__ == '__main__':
    main()
