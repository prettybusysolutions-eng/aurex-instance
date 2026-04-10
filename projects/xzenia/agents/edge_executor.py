#!/usr/bin/env python3
"""
Xzenia Edge Executor — Local autonomous agent execution.
Runs on edge devices (local machine) with minimal latency.
Designed to match Tesla's Digital Optimus architecture:
- 90% of work done locally (System 1)
- 9% routed to cloud for reasoning (System 2)
- 1% human escalation for novel situations
"""
import json
import subprocess
import time
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
EDGE_STATE = WORKSPACE / 'projects/xzenia/state/edge-executor-state.json'
OUTPUT_DIR = WORKSPACE / 'projects/xzenia/agents/outputs'

# Edge-capable actions (fast, local)
EDGE_ACTIONS = {
    'file_operations': ['read', 'write', 'edit', 'copy', 'move', 'delete'],
    'shell': ['exec', 'run_command'],
    'code': ['python', 'bash', 'run_script'],
    'data': ['parse_json', 'extract', 'transform'],
    'web': ['curl', 'fetch', 'download'],
}

# Cloud-only actions (need reasoning)
CLOUD_ACTIONS = [
    'analyze_complex', 'plan_strategy', 'debug_abstract', 
    'design_system', 'review_architecture'
]

# Local LLM fallback (Ollama)
LOCAL_PROVIDER = 'ollama'
LOCAL_MODELS = ['qwen2.5:7b', 'qwen2.5:3b', 'llama3.2:3b']


def log_execution(action: str, result: dict, latency_ms: int, mode: str):
    """Log execution to ledger."""
    conn = sqlite3.connect(DB)
    conn.execute('''
        INSERT INTO causal_events 
        (created_at, event_type, session_key, component, input_json, output_json, outcome, latency_ms, failure_class, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now(timezone.utc).isoformat(),
        'edge_execution',
        'edge:local',
        'edge_executor',
        json.dumps({'action': action, 'mode': mode}),
        json.dumps(result),
        'ok' if result.get('success') else 'failed',
        latency_ms,
        result.get('error'),
        json.dumps({'mode': mode, 'edge_action': True})
    ))
    conn.commit()
    conn.close()


def load_state():
    if EDGE_STATE.exists():
        return json.loads(EDGE_STATE.read_text())
    return {'total_executions': 0, 'edge_only': 0, 'cloud_fallback': 0, 'failures': 0}


def save_state(state):
    EDGE_STATE.write_text(json.dumps(state, indent=2))


def is_edge_action(action: str) -> bool:
    """Check if action can run on edge."""
    for category, actions in EDGE_ACTIONS.items():
        if action in actions:
            return True
    return action in CLOUD_ACTIONS


def execute_local(action: str, params: dict, state: dict) -> dict:
    """Execute action on local edge."""
    start = time.time()
    
    try:
        if action == 'exec' or action == 'run_command':
            cmd = params.get('command', '')
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, 
                timeout=params.get('timeout', 30)
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'mode': 'edge_local'
            }
        
        elif action == 'python':
            # Run inline Python
            code = params.get('code', '')
            result = subprocess.run(
                ['python3', '-c', code], 
                capture_output=True, text=True, timeout=60
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'mode': 'edge_local'
            }
        
        elif action == 'read':
            path = params.get('path')
            content = Path(path).read_text()
            return {'success': True, 'content': content, 'mode': 'edge_local'}
        
        elif action == 'write':
            path = params.get('path')
            content = params.get('content', '')
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content)
            return {'success': True, 'mode': 'edge_local'}
        
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def execute_cloud(action: str, params: dict, state: dict) -> dict:
    """Execute via cloud AI (fallback)."""
    start = time.time()
    
    # In real impl: call cloud AI with action + context
    # For now: simulate cloud call
    result = {
        'success': True,
        'mode': 'cloud_fallback',
        'note': 'Cloud execution simulated - would call Claude/Qwen/MiniMax',
        'action': action
    }
    
    state['cloud_fallback'] = state.get('cloud_fallback', 0) + 1
    
    return result


def execute(action: str, params: dict = None, force_mode: str = None):
    """Main execution entry point."""
    params = params or {}
    state = load_state()
    
    start = time.time()
    
    # Determine execution mode
    if force_mode:
        mode = force_mode
    elif is_edge_action(action):
        mode = 'edge_local'
    else:
        mode = 'cloud_fallback'
    
    # Execute
    if mode == 'edge_local':
        result = execute_local(action, params, state)
    else:
        result = execute_cloud(action, params, state)
    
    latency = int((time.time() - start) * 1000)
    
    # Update stats
    state['total_executions'] = state.get('total_executions', 0) + 1
    if result.get('success'):
        state['edge_only'] = state.get('edge_only', 0) + 1
    else:
        state['failures'] = state.get('failures', 0) + 1
    
    save_state(state)
    log_execution(action, result, latency, mode)
    
    return {
        'action': action,
        'mode': mode,
        'result': result,
        'latency_ms': latency,
        'stats': state
    }


def get_status() -> dict:
    """Get edge executor status."""
    state = load_state()
    total = state.get('total_executions', 0)
    edge = state.get('edge_only', 0)
    
    return {
        'status': 'operational',
        'mode': 'edge_hybrid',
        'stats': state,
        'edge_ratio': round(edge / total, 3) if total > 0 else 0,
        'latency_target': {'edge': '<50ms', 'cloud': '<2000ms'},
        'local_models': LOCAL_MODELS,
        'capabilities': list(EDGE_ACTIONS.keys())
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps(get_status(), indent=2))
    elif sys.argv[1] == '--execute' and len(sys.argv) >= 3:
        action = sys.argv[2]
        params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(execute(action, params), indent=2))
    elif sys.argv[1] == '--stats':
        print(json.dumps(load_state(), indent=2))
    else:
        print('Usage: edge_executor.py [--execute action [params_json]] [--stats]')
