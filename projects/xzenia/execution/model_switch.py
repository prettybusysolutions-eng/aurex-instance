#!/usr/bin/env python3
"""
Model Switcher — Manually switch models with validation.
Usage: model_switch.py [--to MODEL_ID] [--status]
"""
import json
import sys
from pathlib import Path

SESSION_FILE = Path('/Users/marcuscoarchitect/.openclaw/agents/main/sessions/sessions.json')
MODELS_FILE = Path('/Users/marcuscoarchitect/.openclaw/agents/main/agent/models.json')

def load_models():
    return json.loads(MODELS_FILE.read_text())

def load_sessions():
    return json.loads(SESSION_FILE.read_text())

def save_sessions(data):
    SESSION_FILE.write_text(json.dumps(data, indent=2))

def find_model(model_id):
    """Find provider and config for model ID."""
    models = load_models()
    for p, cfg in models.get('providers', {}).items():
        for mo in cfg.get('models', []):
            if mo.get('id') == model_id:
                return p, mo
    return None, None

def status():
    sess = load_sessions()
    key = 'agent:main:telegram:direct:6620375090'
    s = sess.get(key, {})
    return {
        'current_model': s.get('model'),
        'current_provider': s.get('modelProvider'),
        'fallback_active': s.get('fallbackNoticeActiveModel'),
        'fallback_selected': s.get('fallbackNoticeSelectedModel'),
    }

def switch_to(model_id):
    """Switch session to model_id with validation."""
    provider, model_cfg = find_model(model_id)
    if not provider:
        return {'error': f'Model {model_id} not found in configuration'}
    
    if not model_cfg:
        return {'error': f'Model {model_id} not fully configured'}
    
    sess = load_sessions()
    key = 'agent:main:telegram:direct:6620375090'
    if key not in sess:
        sess[key] = {}
    
    # Apply switch
    sess[key]['model'] = model_id
    sess[key]['modelProvider'] = provider
    
    # Clear fallback flags since this is manual selection
    sess[key]['fallbackNoticeActiveModel'] = model_id
    sess[key]['fallbackNoticeSelectedModel'] = None
    
    save_sessions(sess)
    
    return {
        'status': 'switched',
        'model': model_id,
        'provider': provider,
        'model_config': model_cfg
    }

def list_models():
    """List all available models."""
    models = load_models()
    result = []
    for p, cfg in models.get('providers', {}).items():
        for mo in cfg.get('models', []):
            result.append({
                'id': mo.get('id'),
                'provider': p,
                'name': mo.get('name'),
                'context': mo.get('contextWindow'),
            })
    return result

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == '--status':
        print(json.dumps(status(), indent=2))
    elif sys.argv[1] == '--list':
        print(json.dumps(list_models(), indent=2))
    elif len(sys.argv) >= 3 and sys.argv[1] == '--to':
        result = switch_to(sys.argv[2])
        print(json.dumps(result, indent=2))
    else:
        print('Usage: model_switch.py --status | --list | --to MODEL_ID')
        sys.exit(1)
