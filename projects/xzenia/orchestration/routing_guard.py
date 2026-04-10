#!/usr/bin/env python3
"""
routing_guard.py — enforce governed routing fields in openclaw.json.

This script is intentionally narrow and separate from model-guardian.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

CONFIG = Path.home() / '.openclaw' / 'openclaw.json'
CANONICAL_DM_SCOPE = 'per-channel-peer'
CANONICAL_IDENTITY_LINKS = {
    'aurex': ['telegram:6620375090']
}


def main():
    data = json.loads(CONFIG.read_text())
    session = data.setdefault('session', {})
    changed = []

    if session.get('dmScope') != CANONICAL_DM_SCOPE:
        session['dmScope'] = CANONICAL_DM_SCOPE
        changed.append('session.dmScope')

    if session.get('identityLinks') != CANONICAL_IDENTITY_LINKS:
        session['identityLinks'] = CANONICAL_IDENTITY_LINKS
        changed.append('session.identityLinks')

    if changed:
        data.setdefault('meta', {})['lastTouchedAt'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        CONFIG.write_text(json.dumps(data, indent=2) + '\n')

    print(json.dumps({'changed': changed, 'dmScope': session.get('dmScope'), 'identityLinks': session.get('identityLinks')}, indent=2))


if __name__ == '__main__':
    main()
