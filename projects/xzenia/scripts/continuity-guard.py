#!/usr/bin/env python3
"""
Continuity Guard: Prevents silent/truncated execution by enforcing checkpointed,
budget-aware state saves before long or multi-step generation.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.path.expanduser('~/.openclaw/workspace'))
STATE_DIR = WORKSPACE / 'projects/xzenia/state'
CHECKPOINT_FILE = STATE_DIR / 'latest-checkpoint.json'
TOKEN_POLICY_FILE = WORKSPACE / 'projects/xzenia/runtime/token-budget-policy.json'
TOKEN_STATE_FILE = STATE_DIR / 'token-budget-state.json'


def load_json(path, default=None):
    if path.exists():
        return json.loads(path.read_text())
    return {} if default is None else default


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n')


def make_budget_plan(text_length: int):
    policy = load_json(TOKEN_POLICY_FILE, default={'rules': {}})
    rules = policy.get('rules', {})
    checkpoint_threshold = int(rules.get('checkpoint_threshold_chars', 3500))
    soft_chunk_target = int(rules.get('soft_chunk_target_chars', 2200))
    hard_chunk_limit = int(rules.get('hard_chunk_limit_chars', 3200))
    reserve = int(rules.get('reserve_for_wrapup_chars', 600))
    recommended_chunk = min(soft_chunk_target, max(1, hard_chunk_limit - reserve))
    return {
        'length_chars': text_length,
        'needs_checkpoint': text_length >= checkpoint_threshold,
        'recommended_chunk_chars': recommended_chunk,
        'estimated_chunks': max(1, (text_length + recommended_chunk - 1) // recommended_chunk),
        'status': 'chunk_required' if text_length > hard_chunk_limit else 'single_chunk_ok'
    }


def save_checkpoint(phase, data, planned_output=''):
    budget_plan = make_budget_plan(len(planned_output or ''))
    existing = load_json(CHECKPOINT_FILE, default={})
    state = dict(existing)
    state.update({
        'timestamp': datetime.now().astimezone().isoformat(),
        'phase': phase,
        'data': data,
        'token_budget': budget_plan,
        'status': 'ready' if budget_plan['needs_checkpoint'] else 'completed'
    })
    if 'resumeInstruction' not in state:
        state['resumeInstruction'] = 'Read the latest checkpoint, inspect the resume queue, then continue the highest-priority verified next step.'
    if 'nextFrontier' not in state:
        state['nextFrontier'] = []
    if 'artifacts' not in state:
        state['artifacts'] = {}
    save_json(CHECKPOINT_FILE, state)
    save_json(TOKEN_STATE_FILE, {'phase': phase, 'plan': budget_plan, 'updated_at': state['timestamp']})
    print(json.dumps({'ok': True, 'checkpoint': str(CHECKPOINT_FILE), 'token_state': str(TOKEN_STATE_FILE), 'plan': budget_plan}, indent=2))


def load_checkpoint():
    return load_json(CHECKPOINT_FILE, default=None)


def clear_checkpoint():
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
    if TOKEN_STATE_FILE.exists():
        TOKEN_STATE_FILE.unlink()


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'save':
        phase = sys.argv[2] if len(sys.argv) >= 3 else 'unspecified'
        data = json.loads(sys.argv[3]) if len(sys.argv) >= 4 else {}
        planned_output = sys.argv[4] if len(sys.argv) >= 5 else ''
        save_checkpoint(phase, data, planned_output)
    elif len(sys.argv) >= 2 and sys.argv[1] == 'load':
        print(json.dumps(load_checkpoint() or {}, indent=2))
    elif len(sys.argv) >= 2 and sys.argv[1] == 'clear':
        clear_checkpoint()
        print(json.dumps({'ok': True, 'cleared': True}, indent=2))
    else:
        demo = 'Continuity Guard active. Budget-aware checkpointing enabled.'
        save_checkpoint('ready', {'message': demo}, demo)
