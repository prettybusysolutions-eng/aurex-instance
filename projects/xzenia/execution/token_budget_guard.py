#!/usr/bin/env python3
"""
Token Budget Guard — execution-layer wrapper around continuity-guard.
Evaluates current output size against policy thresholds and forces
checkpoint + chunk if needed. Unified with checkpoint_contract.
"""
import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
POLICY_FILE = WORKSPACE / 'projects/xzenia/runtime/token-budget-policy.json'
GUARD = WORKSPACE / 'projects/xzenia/scripts/continuity-guard.py'


def load_policy():
    if POLICY_FILE.exists():
        return json.loads(POLICY_FILE.read_text()).get('rules', {})
    return {}


def evaluate(text_length: int) -> dict:
    rules = load_policy()
    checkpoint_threshold = int(rules.get('checkpoint_threshold_chars', 3500))
    soft_chunk = int(rules.get('soft_chunk_target_chars', 2200))
    hard_chunk = int(rules.get('hard_chunk_limit_chars', 3200))
    reserve = int(rules.get('reserve_for_wrapup_chars', 600))
    chunk_size = min(soft_chunk, max(1, hard_chunk - reserve))
    needs_checkpoint = text_length >= checkpoint_threshold
    return {
        'length_chars': text_length,
        'needs_checkpoint': needs_checkpoint,
        'recommended_chunk_chars': chunk_size,
        'estimated_chunks': max(1, (text_length + chunk_size - 1) // chunk_size),
        'status': 'chunk_required' if text_length > hard_chunk else 'single_chunk_ok',
        'action': 'checkpoint_and_chunk' if needs_checkpoint else 'proceed'
    }


def guard(phase: str, text_length: int, work_id: str = 'unspecified') -> dict:
    result = evaluate(text_length)
    if result['needs_checkpoint']:
        payload = {'work_id': work_id, 'length': text_length, 'action': 'pre-limit-checkpoint'}
        res = subprocess.run(
            ['python3', str(GUARD), 'save', f'token-guard:{phase}:{work_id}',
             json.dumps(payload), ''],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        result['checkpoint_written'] = res.returncode == 0
        result['checkpoint_detail'] = res.stdout.strip()
    return result


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'evaluate':
        length = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
        print(json.dumps(evaluate(length), indent=2))
    elif len(sys.argv) >= 2 and sys.argv[1] == 'guard':
        phase = sys.argv[2] if len(sys.argv) >= 3 else 'unspecified'
        length = int(sys.argv[3]) if len(sys.argv) >= 4 else 0
        work_id = sys.argv[4] if len(sys.argv) >= 5 else 'unspecified'
        print(json.dumps(guard(phase, length, work_id), indent=2))
    else:
        print('usage: token_budget_guard.py evaluate <chars> | guard <phase> <chars> [work_id]')
        sys.exit(1)
