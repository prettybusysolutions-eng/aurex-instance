#!/usr/bin/env python3
import json
import sys
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
SCHEMA = json.loads((WORKSPACE / 'projects/xzenia/charter/domain_contract_schema.json').read_text())
REQUIRED = SCHEMA['required']


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: validate_domain_contract.py <domain-json>')
    path = Path(sys.argv[1])
    data = json.loads(path.read_text())
    missing = [k for k in REQUIRED if k not in data]
    result = {
        'path': str(path),
        'missing': missing,
        'valid': len(missing) == 0
    }
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()
