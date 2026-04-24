#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'reports' / 'FINAL-THIN-ROOT-BASELINE-2026-04-23.json'


def main() -> int:
    if not BASELINE.exists():
        print(json.dumps({'ok': False, 'error': f'missing baseline: {BASELINE}'}, indent=2))
        return 2

    baseline = json.loads(BASELINE.read_text())
    expected = {item['name']: item for item in baseline['items']}
    live_files = sorted([p for p in ROOT.iterdir() if p.is_file() and not p.name.startswith('.')], key=lambda p: p.name)
    live_names = {p.name for p in live_files}
    expected_names = set(expected.keys())

    unexpected = sorted(live_names - expected_names)
    missing = sorted(expected_names - live_names)

    result = {
        'ok': not unexpected and not missing,
        'baseline': str(BASELINE.relative_to(ROOT)),
        'expected_count': len(expected_names),
        'live_count': len(live_names),
        'unexpected': unexpected,
        'missing': missing,
    }
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
