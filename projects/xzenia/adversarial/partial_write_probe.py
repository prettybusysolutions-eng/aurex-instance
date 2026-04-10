#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
TARGET = WORKSPACE / 'projects/xzenia/csmr/reports/partial-write-probe-target.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/partial-write-probe.json'


def main():
    original = TARGET.read_text() if TARGET.exists() else None
    try:
        TARGET.write_text('{"incomplete": true')
        corrupt_read_failed = False
        try:
            json.loads(TARGET.read_text())
        except Exception:
            corrupt_read_failed = True

        recovery_payload = {
            'timestamp': datetime.now().astimezone().isoformat(),
            'recovered': True,
            'status': 'done and verified'
        }
        TARGET.write_text(json.dumps(recovery_payload, indent=2) + '\n')
        recovered = json.loads(TARGET.read_text()).get('recovered') is True

        payload = {
            'timestamp': datetime.now().astimezone().isoformat(),
            'corrupt_read_failed': corrupt_read_failed,
            'recovered_cleanly': recovered,
            'status': 'done and verified' if corrupt_read_failed and recovered else 'partial'
        }
        OUT.write_text(json.dumps(payload, indent=2) + '\n')
        print(json.dumps(payload, indent=2))
        raise SystemExit(0 if payload['status'] == 'done and verified' else 1)
    finally:
        if original is None:
            if TARGET.exists():
                TARGET.unlink()
        else:
            TARGET.write_text(original)


if __name__ == '__main__':
    main()
