#!/usr/bin/env python3
"""
Auto-Fallback Enforcer — Monitors API errors and automatically switches models.
Operationalizes the fallback chain so you never manually reset.
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
STATE = WORKSPACE / 'projects/xzenia/state/autofallback-state.json'
POLICY = WORKSPACE / 'projects/xzenia/orchestration/resilience-policy.json'
SESSION = Path('/Users/marcuscoarchitect/.openclaw/agents/main/sessions/sessions.json')
LOG = WORKSPACE / 'projects/xzenia/csmr/reports/autofallback-log.json'

# Error patterns that trigger fallback
TRIGGER_ERRORS = {
    'rate_limit',           # HTTP 429
    'token_limit',          # context overflow
    'context_overflow',     # context too large
    'provider_unavailable', # service down
    'timeout',              # request timeout
    'insufficient_quota',   # quota exceeded
}

# Fallback chain in priority order
CHAIN = [
    {'provider': 'minimax-portal', 'model': 'MiniMax-M2.5', 'name': 'MiniMax M2.5'},
    {'provider': 'anthropic', 'model': 'claude-sonnet-4-6', 'name': 'Claude Sonnet 4'},
    {'provider': 'ollama', 'model': 'qwen2.5:7b', 'name': 'Qwen 2.5 7B (local)'},
    {'provider': 'ollama', 'model': 'qwen2.5:3b', 'name': 'Qwen 2.5 3B (local)'},
    {'provider': 'ollama', 'model': 'llama3.2:3b', 'name': 'Llama 3.2 3B (local)'},
]


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {'current_index': 0, 'last_error': None, 'fallback_count': 0}


def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))


def get_current_model():
    """Get current active model from session config."""
    try:
        ses = json.loads(SESSION.read_text())
        s = ses.get('agent:main:telegram:direct:6620375090', {})
        return s.get('model', 'MiniMax-M2.5')
    except:
        return 'MiniMax-M2.5'


def detect_error(msg: str) -> str:
    msg_lower = msg.lower()
    if '429' in msg or 'rate limit' in msg_lower:
        return 'rate_limit'
    if 'token' in msg_lower and 'limit' in msg_lower:
        return 'token_limit'
    if 'context' in msg_lower and 'overflow' in msg_lower:
        return 'context_overflow'
    if 'timeout' in msg_lower:
        return 'timeout'
    if 'unavailable' in msg_lower or 'service' in msg_lower:
        return 'provider_unavailable'
    return 'unknown'


def apply_fallback(index: int) -> dict:
    """Apply fallback model to session config."""
    if index >= len(CHAIN):
        return {'error': 'No more fallbacks available'}
    
    target = CHAIN[index]
    try:
        ses = json.loads(SESSION.read_text())
        key = 'agent:main:telegram:direct:6620375090'
        if key not in ses:
            ses[key] = {}
        ses[key]['model'] = target['model']
        ses[key]['modelProvider'] = target['provider']
        ses[key]['fallbackNoticeActiveModel'] = target['model']
        SESSION.write_text(json.dumps(ses, indent=2))
        return {'applied': target, 'index': index}
    except Exception as e:
        return {'error': str(e)}


def log_fallback(error_type: str, from_model: str, to_model: str):
    """Log fallback event."""
    entry = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'error_type': error_type,
        'from_model': from_model,
        'to_model': to_model,
    }
    try:
        log_data = json.loads(LOG.read_text()) if LOG.exists() else {'entries': []}
        log_data['entries'].append(entry)
        LOG.write_text(json.dumps(log_data, indent=2))
    except:
        pass


def run(error_msg: str = None) -> dict:
    """Main fallback logic."""
    state = load_state()
    error_type = detect_error(error_msg or 'unknown')
    
    current = get_current_model()
    current_idx = state.get('current_index', 0)
    
    # Find current position in chain
    for i, c in enumerate(CHAIN):
        if c['model'] == current:
            current_idx = i
            break
    
    # Try next fallback
    next_idx = current_idx + 1
    if next_idx >= len(CHAIN):
        return {'status': 'exhausted', 'current': current, 'error': error_type}
    
    result = apply_fallback(next_idx)
    if 'error' in result:
        return result
    
    state['current_index'] = next_idx
    state['last_error'] = error_type
    state['fallback_count'] = state.get('fallback_count', 0) + 1
    save_state(state)
    
    log_fallback(error_type, current, CHAIN[next_idx]['model'])
    
    return {
        'status': 'fallback_applied',
        'error': error_type,
        'from': current,
        'to': CHAIN[next_idx]['model'],
        'chain_position': next_idx,
        'total_fallbacks': state['fallback_count']
    }


if __name__ == '__main__':
    error = sys.argv[1] if len(sys.argv) > 1 else None
    result = run(error)
    print(json.dumps(result, indent=2))
