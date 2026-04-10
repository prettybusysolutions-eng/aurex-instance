#!/usr/bin/env python3
import json
import math
import sys
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
POLICY_PATH = WORKSPACE / 'projects/xzenia/runtime/token-budget-policy.json'
STATE_PATH = WORKSPACE / 'projects/xzenia/state/token-budget-state.json'


def load_policy():
    return json.loads(POLICY_PATH.read_text())


def plan(text: str):
    policy = load_policy()
    rules = policy['rules']
    length = len(text)
    soft = int(rules['soft_chunk_target_chars'])
    hard = int(rules['hard_chunk_limit_chars'])
    reserve = int(rules['reserve_for_wrapup_chars'])
    needs_checkpoint = length >= int(rules['checkpoint_threshold_chars'])
    recommended_chunk = min(soft, max(1, hard - reserve))
    chunks = math.ceil(length / recommended_chunk) if length else 1
    return {
        'length_chars': length,
        'needs_checkpoint': needs_checkpoint,
        'recommended_chunk_chars': recommended_chunk,
        'estimated_chunks': chunks,
        'status': 'chunk_required' if length > hard else 'single_chunk_ok'
    }


def save_state(payload):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(payload, indent=2) + '\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: token_budget_guard.py <text-file>', file=sys.stderr)
        raise SystemExit(2)
    path = Path(sys.argv[1])
    text = path.read_text()
    payload = {
        'input_file': str(path),
        'plan': plan(text)
    }
    save_state(payload)
    print(json.dumps(payload, indent=2))
