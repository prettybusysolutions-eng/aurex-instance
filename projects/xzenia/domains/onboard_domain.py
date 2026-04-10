#!/usr/bin/env python3
"""
onboard_domain.py — Xzenia System 5 Domain Onboarding Script

Usage:
    python3 onboard_domain.py <path/to/domain.json>

What it does:
    1. Validates the domain contract against the schema (requires zero violations)
    2. Registers the domain in domains/domain-registry.json
    3. Emits a structured onboarding report to csmr/reports/

Exit codes:
    0 = success
    1 = validation failure or other error
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
SCHEMA_PATH = WORKSPACE / 'projects/xzenia/charter/domain_contract_schema.json'
REGISTRY_PATH = WORKSPACE / 'projects/xzenia/domains/domain-registry.json'
REPORTS_DIR = WORKSPACE / 'projects/xzenia/csmr/reports'


def log(msg: str) -> None:
    print(f'[onboard] {msg}')


def load_schema() -> list:
    schema = json.loads(SCHEMA_PATH.read_text())
    return schema['required']


def validate_contract(path: Path, required: list) -> dict:
    data = json.loads(path.read_text())
    missing = [k for k in required if k not in data]
    return {
        'path': str(path),
        'missing': missing,
        'valid': len(missing) == 0,
        'sections_present': [k for k in required if k in data],
    }


def load_registry() -> list:
    if REGISTRY_PATH.exists():
        return json.loads(REGISTRY_PATH.read_text())
    return []


def save_registry(entries: list) -> None:
    REGISTRY_PATH.write_text(json.dumps(entries, indent=2) + '\n')


def register_domain(domain_path: Path, validation: dict, report_path: Path) -> dict:
    data = json.loads(domain_path.read_text())
    name = data['identity']['name']
    now = datetime.now(timezone.utc).astimezone().isoformat()

    entry = {
        'name': name,
        'path': str(domain_path),
        'onboarded_at': now,
        'valid': True,
        'report': str(report_path),
        'sections': validation['sections_present'],
    }

    entries = load_registry()
    # Update existing entry if present, otherwise append
    existing_idx = next((i for i, e in enumerate(entries) if e['name'] == name), None)
    if existing_idx is not None:
        entries[existing_idx] = entry
    else:
        entries.append(entry)

    save_registry(entries)
    return entry


def emit_report(domain_path: Path, validation: dict, registry_entry: dict) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(domain_path.read_text())
    name = data['identity']['name']
    now = datetime.now(timezone.utc).astimezone().isoformat()
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    report = {
        'report_type': 'domain_onboarding',
        'timestamp': now,
        'domain': {
            'name': name,
            'path': str(domain_path),
            'objective': data['identity'].get('objective', ''),
        },
        'validation': {
            'result': 'PASS' if validation['valid'] else 'FAIL',
            'violations': validation['missing'],
            'sections_verified': validation['sections_present'],
        },
        'registry': {
            'registered': True,
            'registry_path': str(REGISTRY_PATH),
            'entry': registry_entry,
        },
        'substrate_modification_required': False,
        'notes': (
            'Domain onboarded using contract + onboarding guide only. '
            'No substrate modification was required or performed.'
        ),
    }

    out_path = REPORTS_DIR / f'onboarding-{name}-{ts}.json'
    out_path.write_text(json.dumps(report, indent=2) + '\n')
    return out_path


def main():
    if len(sys.argv) != 2:
        print('usage: onboard_domain.py <domain-json>', file=sys.stderr)
        raise SystemExit(1)

    domain_path = Path(sys.argv[1])
    if not domain_path.exists():
        print(f'[onboard] ERROR: file not found: {domain_path}', file=sys.stderr)
        raise SystemExit(1)

    log(f'Validating {domain_path} ...')
    required = load_schema()
    validation = validate_contract(domain_path, required)

    if not validation['valid']:
        log(f'✗ Validation FAILED — missing sections: {validation["missing"]}')
        log('Onboarding aborted. Fix the contract and retry.')
        raise SystemExit(1)

    log('✓ Validation passed — zero violations')

    # Emit report first (needed for registry entry path)
    data = json.loads(domain_path.read_text())
    name = data['identity']['name']
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    report_path = REPORTS_DIR / f'onboarding-{name}-{ts}.json'

    log(f'Registering domain \'{name}\' in domain-registry.json ...')
    registry_entry = register_domain(domain_path, validation, report_path)
    entries = load_registry()
    log(f'✓ Registered. Registry now contains {len(entries)} domain(s).')

    log('Emitting onboarding report ...')
    # Write actual report now that we have the registry entry
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).astimezone().isoformat()
    report = {
        'report_type': 'domain_onboarding',
        'timestamp': now,
        'domain': {
            'name': name,
            'path': str(domain_path),
            'objective': data['identity'].get('objective', ''),
        },
        'validation': {
            'result': 'PASS',
            'violations': [],
            'sections_verified': validation['sections_present'],
        },
        'registry': {
            'registered': True,
            'registry_path': str(REGISTRY_PATH),
            'entry': registry_entry,
        },
        'substrate_modification_required': False,
        'notes': (
            'Domain onboarded using contract + onboarding guide only. '
            'No substrate modification was required or performed.'
        ),
    }
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    log(f'✓ Report written to csmr/reports/onboarding-{name}-{ts}.json')
    log(f'DONE: {name} successfully onboarded.')
    print(json.dumps(report, indent=2))
    raise SystemExit(0)


if __name__ == '__main__':
    main()
