#!/usr/bin/env python3
"""
Xzenia Digital Agent — System 1 (Fast Instinctive) + System 2 (Deliberative) Architecture
Inspired by Tesla's Digital Optimus + Grock architecture.

System 1: Local edge agent watching screen, reacting in real-time
System 2: Cloud reasoning for complex decisions
Unified: Both improve together

This is the foundation for Xzenia's autonomous digital workforce.
"""
import json
import time
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from collections import deque
from typing import Optional

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
STATE = WORKSPACE / 'projects/xzenia/state/digital-agent-state.json'
LOG = WORKSPACE / 'projects/xzenia/csmr/reports/digital-agent-log.json'

# System 1: Local actions (fast, reflexive)
SYSTEM1_ACTIONS = [
    'click', 'type', 'scroll', 'navigate', 'wait', 'extract_text', 'fill_form'
]

# System 2: Complex reasoning (slow, deliberate)  
SYSTEM2_TRIGGERS = [
    'decision_required', 'context_unknown', 'multi_step_plan', 
    'error_recovery', 'ambiguous_input', 'strategy_change'
]


class DigitalAgentState:
    def __init__(self):
        self.system1_buffer = deque(maxlen=10)  # Last 10 actions
        self.system2_context = []
        self.total_actions = 0
        self.system2_calls = 0
        self.last_screen_state = None
        
    def to_dict(self):
        return {
            'system1_buffer': list(self.system1_buffer),
            'system2_context': self.system2_context[-5:],
            'total_actions': self.total_actions,
            'system2_calls': self.system2_calls
        }


def init_db():
    """Initialize the digital agent event log."""
    conn = sqlite3.connect(DB)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS digital_agent_events (
            id INTEGER PRIMARY KEY,
            created_at TEXT,
            event_type TEXT,
            system_level TEXT,
            action TEXT,
            screen_context TEXT,
            reasoning TEXT,
            latency_ms INTEGER,
            success INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def log_event(event_type: str, system_level: str, action: str, 
              screen_context: str = None, reasoning: str = None,
              latency_ms: int = 0, success: bool = True):
    """Log an agent action to the ledger."""
    conn = sqlite3.connect(DB)
    conn.execute('''
        INSERT INTO digital_agent_events 
        (created_at, event_type, system_level, action, screen_context, reasoning, latency_ms, success)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now(timezone.utc).isoformat(),
        event_type,
        system_level,
        action,
        screen_context,
        reasoning,
        latency_ms,
        1 if success else 0
    ))
    conn.commit()
    conn.close()


def classify_complexity(action: str, context: dict) -> str:
    """Determine if action needs System 1 or System 2."""
    # Simple heuristic: if context is clear and action is routine → System 1
    if context.get('screen_stable') and action in ['click', 'type', 'scroll']:
        return 'system1'
    
    # Complex cases → System 2
    for trigger in SYSTEM2_TRIGGERS:
        if context.get(trigger):
            return 'system2'
    
    # Default to System 1 for speed
    return 'system1'


def execute_system1(action: str, params: dict, state: DigitalAgentState) -> dict:
    """Execute fast local action."""
    start = time.time()
    
    # Simulate action execution (would use pyautogui in real impl)
    result = {
        'action': action,
        'params': params,
        'executed_by': 'system1',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'success': True
    }
    
    state.system1_buffer.append({
        'action': action,
        'timestamp': result['timestamp']
    })
    state.total_actions += 1
    
    latency = int((time.time() - start) * 1000)
    log_event('action', 'system1', action, 
             screen_context=json.dumps(params), latency_ms=latency)
    
    return result


def execute_system2(action: str, params: dict, context: dict, state: DigitalAgentState) -> dict:
    """Execute deliberative reasoning (cloud AI)."""
    start = time.time()
    
    # Prepare context for System 2
    system1_history = list(state.system1_buffer)
    
    reasoning_prompt = f"""
    Action: {action}
    Params: {json.dumps(params)}
    Recent History: {json.dumps(system1_history[-5:])}
    Context: {json.dumps(context)}
    
    Provide: 1) Reasoning 2) Recommended action 3) Confidence level
    """
    
    # In real impl: call cloud AI (Grock, Claude, etc)
    # For now: return structured reasoning
    result = {
        'action': action,
        'params': params,
        'executed_by': 'system2',
        'reasoning': 'Cloud reasoning would occur here',
        'recommendation': action,  # Would be AI's recommendation
        'confidence': 0.85,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'success': True
    }
    
    state.system2_context.append({
        'reasoning': result['reasoning'],
        'action': action,
        'timestamp': result['timestamp']
    })
    state.system2_calls += 1
    state.total_actions += 1
    
    latency = int((time.time() - start) * 1000)
    log_event('reasoning', 'system2', action,
             reasoning=reasoning_prompt, latency_ms=latency)
    
    return result


def run_cycle(action: str, params: dict = None, context: dict = None):
    """Main agent cycle — decides System 1 vs System 2."""
    params = params or {}
    context = context or {}
    
    state = DigitalAgentState()
    if STATE.exists():
        try:
            saved = json.loads(STATE.read_text())
            state.total_actions = saved.get('total_actions', 0)
            state.system2_calls = saved.get('system2_calls', 0)
        except:
            pass
    
    # Classify complexity
    complexity = classify_complexity(action, context)
    
    if complexity == 'system1':
        result = execute_system1(action, params, state)
    else:
        result = execute_system2(action, params, context, state)
    
    # Save state
    STATE.write_text(json.dumps(state.to_dict(), indent=2))
    
    return {
        'complexity': complexity,
        'result': result,
        'stats': state.to_dict()
    }


def get_stats() -> dict:
    """Get agent statistics."""
    if not STATE.exists():
        return {'total_actions': 0, 'system2_calls': 0}
    return json.loads(STATE.read_text())


def get_capabilities() -> dict:
    """Return agent capabilities."""
    return {
        'system1': {
            'actions': SYSTEM1_ACTIONS,
            'latency_target_ms': 50,
            'runs_locally': True,
            'edge_device': 'local'
        },
        'system2': {
            'triggers': SYSTEM2_TRIGGERS,
            'latency_target_ms': 2000,
            'runs_cloud': True,
            'providers': ['claude-sonnet-4-6', 'MiniMax-M2.5', 'qwen2.5:7b']
        },
        'unified_learning': True,
        'architecture': 'Digital Optimus style: System1 + System2 hybrid'
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps({
            'status': 'operational',
            'capabilities': get_capabilities(),
            'stats': get_stats()
        }, indent=2))
    elif sys.argv[1] == '--stats':
        print(json.dumps(get_stats(), indent=2))
    elif sys.argv[1] == '--capabilities':
        print(json.dumps(get_capabilities(), indent=2))
    elif len(sys.argv) >= 3:
        action = sys.argv[1]
        params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        context = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(run_cycle(action, params, context), indent=2))
    else:
        print('Usage: digital_agent.py [--stats|--capabilities] [action] [params_json] [context_json]')
