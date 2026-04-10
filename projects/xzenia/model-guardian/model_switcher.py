#!/usr/bin/env python3
"""
model_switcher.py — Patches openclaw.json agents.defaults.model.primary coherently.

Usage:
  python3 model_switcher.py --to ollama/qwen2.5:7b [--reason "budget 85%"]
  python3 model_switcher.py --restore   # restore original primary
  python3 model_switcher.py --status    # print current model + ladder position

The switch:
1. Reads ~/.openclaw/openclaw.json
2. Makes a timestamped backup
3. Patches agents.defaults.model.primary atomically
4. Gateway hot-reload picks it up automatically (no restart needed)
5. Records state to model-guardian/state.json
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from config_guard import validate_candidate

OPENCLAW_CONFIG = Path.home() / '.openclaw' / 'openclaw.json'
WORKSPACE = Path(__file__).parent
STATE_FILE = WORKSPACE / 'state.json'
BACKUP_DIR = WORKSPACE / 'config-backups'

SWITCH_LADDER = [
    'anthropic/claude-sonnet-4-6',
    'openai-codex/gpt-5.4',
    'ollama/qwen2.5:7b',
    'ollama/qwen2.5:3b',
    'ollama/llama3.2:3b',
    'ollama/qwen2.5:1.5b-instruct-q4_K_M',
]

ORIGINAL_PRIMARY = SWITCH_LADDER[0]


def load_config():
    return json.loads(OPENCLAW_CONFIG.read_text())


def save_config(cfg):
    # Atomic write via tmp + replace, with mutation-surface validation
    before = load_config()
    validate_candidate(before, cfg)
    tmp = OPENCLAW_CONFIG.with_suffix('.json.guardian_tmp')
    tmp.write_text(json.dumps(cfg, indent=2) + '\n')
    tmp.replace(OPENCLAW_CONFIG)


def backup_config():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%dT%H%M%S')
    dest = BACKUP_DIR / f'openclaw-{ts}.json.bak'
    shutil.copy2(OPENCLAW_CONFIG, dest)
    return str(dest)


def get_current_primary(cfg):
    return (
        cfg
        .get('agents', {})
        .get('defaults', {})
        .get('model', {})
        .get('primary', ORIGINAL_PRIMARY)
    )


def set_primary(cfg, model):
    cfg.setdefault('agents', {}).setdefault('defaults', {}).setdefault('model', {})['primary'] = model


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2) + '\n')


def ladder_index(model):
    try:
        return SWITCH_LADDER.index(model)
    except ValueError:
        return -1


def cmd_switch(target_model, reason):
    cfg = load_config()
    current = get_current_primary(cfg)
    if current == target_model:
        print(json.dumps({'ok': True, 'action': 'no_change', 'model': current}))
        return

    backup_path = backup_config()
    state = load_state()
    if 'original_primary' not in state:
        state['original_primary'] = current

    set_primary(cfg, target_model)
    cfg.setdefault('meta', {})['lastTouchedAt'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    save_config(cfg)

    state['current_primary'] = target_model
    state['switched_at'] = datetime.now().isoformat()
    state['switch_reason'] = reason
    state['previous_primary'] = current
    state['backup_path'] = backup_path
    save_state(state)

    print(json.dumps({
        'ok': True,
        'action': 'switched',
        'from': current,
        'to': target_model,
        'reason': reason,
        'backup': backup_path,
        'ladder_position': ladder_index(target_model),
    }))


def cmd_restore():
    state = load_state()
    original = state.get('original_primary', ORIGINAL_PRIMARY)
    cfg = load_config()
    current = get_current_primary(cfg)
    if current == original:
        print(json.dumps({'ok': True, 'action': 'already_restored', 'model': original}))
        return

    backup_path = backup_config()
    set_primary(cfg, original)
    cfg.setdefault('meta', {})['lastTouchedAt'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    save_config(cfg)

    state['current_primary'] = original
    state['restored_at'] = datetime.now().isoformat()
    state.pop('original_primary', None)
    save_state(state)

    print(json.dumps({
        'ok': True,
        'action': 'restored',
        'to': original,
        'backup': backup_path,
    }))


def cmd_status():
    cfg = load_config()
    current = get_current_primary(cfg)
    state = load_state()
    fallbacks = cfg.get('agents', {}).get('defaults', {}).get('model', {}).get('fallbacks', [])
    print(json.dumps({
        'current_primary': current,
        'ladder_position': ladder_index(current),
        'ladder': SWITCH_LADDER,
        'configured_fallbacks': fallbacks,
        'original_primary': state.get('original_primary', ORIGINAL_PRIMARY),
        'last_switch_reason': state.get('switch_reason'),
        'switched_at': state.get('switched_at'),
    }, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--to', help='Switch primary model to this value')
    parser.add_argument('--reason', default='manual', help='Reason for switch')
    parser.add_argument('--restore', action='store_true', help='Restore original primary')
    parser.add_argument('--status', action='store_true', help='Print current status')
    args = parser.parse_args()

    if args.restore:
        cmd_restore()
    elif args.status:
        cmd_status()
    elif args.to:
        cmd_switch(args.to, args.reason)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
