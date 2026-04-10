#!/usr/bin/env python3
"""
config_guard.py — enforce narrow mutation boundaries for OpenClaw config writers.

Rules:
- model guardian may only mutate:
  - meta.lastTouchedAt
  - agents.defaults.model.primary
  - agents.defaults.model.fallbacks
- all other config paths must remain byte-equivalent at JSON value level.
"""
import copy
import json
from pathlib import Path
from typing import Any

OPENCLAW_CONFIG = Path.home() / '.openclaw' / 'openclaw.json'
ALLOWED_PATHS = {
    ('meta', 'lastTouchedAt'),
    ('agents', 'defaults', 'model', 'primary'),
    ('agents', 'defaults', 'model', 'fallbacks'),
}

PROTECTED_EXPECTED_PATHS = {
    ('session', 'dmScope'): 'per-channel-peer',
    ('session', 'identityLinks'): {'aurex': ['telegram:6620375090']},
    ('agents', 'defaults', 'sandbox', 'mode'): 'all',
    ('tools', 'deny'): ['group:web', 'browser'],
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def get_path(data: Any, path):
    cur = data
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def strip_allowed(data: Any):
    clone = copy.deepcopy(data)
    for path in ALLOWED_PATHS:
        cur = clone
        for key in path[:-1]:
            if not isinstance(cur, dict) or key not in cur:
                cur = None
                break
            cur = cur[key]
        if isinstance(cur, dict):
            cur.pop(path[-1], None)
    return clone


def validate_candidate(before: Any, after: Any):
    if strip_allowed(before) != strip_allowed(after):
        raise ValueError('config_guard violation: attempted mutation outside allowed model-guardian paths')
    for path, expected in PROTECTED_EXPECTED_PATHS.items():
        if get_path(after, path) != expected:
            dotted = '.'.join(path)
            raise ValueError(f'config_guard violation: protected path {dotted} must remain {expected!r}')
    return True


def validate_files(before_path: Path, after_path: Path):
    return validate_candidate(load_json(before_path), load_json(after_path))


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('usage: config_guard.py <before.json> <after.json>')
        raise SystemExit(2)
    validate_files(Path(sys.argv[1]), Path(sys.argv[2]))
    print('OK')
