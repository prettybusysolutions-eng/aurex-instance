#!/usr/bin/env python3
"""
task_router.py — Route tasks to optimal models based on capability, cost, and activation status.

Usage:
  python3 task_router.py --task coding
  python3 task_router.py --task analysis --budget-pct 88
  python3 task_router.py --list-tasks
  python3 task_router.py --status
  python3 task_router.py --activate-plan
"""
import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).parent
REGISTRY = WORKSPACE / 'model_registry.json'
STATE = WORKSPACE / 'state.json'

# Task inference from message content keywords
TASK_KEYWORDS = {
    'coding':           ['code', 'debug', 'function', 'class', 'script', 'python', 'js', 'typescript', 'fix this', 'implement', 'refactor', 'tests'],
    'code-review':      ['review', 'pull request', 'pr', 'diff', 'improve this code'],
    'architecture':     ['architecture', 'design', 'system', 'scalab', 'infrastructure', 'schema'],
    'complex-reasoning':['why', 'explain', 'analyze', 'reasoning', 'think through', 'decision', 'tradeoff'],
    'analysis':         ['analyze', 'summarize', 'report', 'findings', 'breakdown', 'audit'],
    'vision':           ['image', 'photo', 'screenshot', 'picture', 'look at', 'what do you see'],
    'fast-classification': ['yes or no', 'classify', 'category', 'label', 'tag'],
    'heartbeat':        ['heartbeat', 'status check', 'health check'],
    'background-tasks': ['background', 'batch', 'cron', 'scheduled'],
    'private-data':     ['private', 'confidential', 'local only', 'dont send', 'sensitive'],
}


def load_registry():
    return json.loads(REGISTRY.read_text())


def load_state():
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            pass
    return {}


def active_models(registry):
    return {
        k: v for k, v in registry['providers'].items()
        if v.get('status') == 'active'
    }


def route_task(task: str, registry: dict, budget_pct: float = 0.0) -> dict:
    """Return best model for task given activated models and budget pressure."""
    routing = registry.get('task_routing', {})
    active = active_models(registry)

    candidates = routing.get(task, routing.get('complex-reasoning', []))
    if not candidates:
        candidates = list(active.keys())

    # Filter to only active models
    available = [m for m in candidates if m in active]

    if not available:
        # Fall through to local models
        available = [k for k, v in active.items() if v.get('local')]

    if not available:
        return {'error': 'no active models available for task', 'task': task}

    # Budget pressure: if >= 85%, skip non-local models
    if budget_pct >= 85:
        local_available = [m for m in available if active.get(m, {}).get('local')]
        if local_available:
            available = local_available

    selected = available[0]
    info = active[selected]

    return {
        'task': task,
        'selected_model': selected,
        'reason': f"best active model for '{task}' at budget {budget_pct}%",
        'alternatives': available[1:3],
        'model_info': {
            'cost_tier': info.get('cost_tier'),
            'local': info.get('local'),
            'context_window': info.get('context_window'),
            'strengths': info.get('strengths', [])[:4],
        },
        'budget_pct': budget_pct,
        'budget_mode': 'local_only' if budget_pct >= 85 else 'normal',
    }


def infer_task_from_text(text: str) -> str:
    """Infer task type from message content."""
    text_lower = text.lower()
    scores = {}
    for task, keywords in TASK_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[task] = score
    if not scores:
        return 'complex-reasoning'
    return max(scores, key=scores.get)


def cmd_activate_plan(registry):
    """Print actionable activation plan for inactive models."""
    priorities = registry.get('activation_priority', [])
    print('\n=== MODEL ACTIVATION PLAN ===\n')
    print('Currently ACTIVE models:')
    for k, v in sorted(registry['providers'].items()):
        if v['status'] == 'active':
            tag = '🌐' if not v['local'] else '💻'
            print(f"  {tag} {k}")
    print()
    print('RECOMMENDED activations (ordered by impact/effort):')
    for i, item in enumerate(priorities, 1):
        model = item['model']
        info = registry['providers'].get(model, {})
        print(f"\n  {i}. {model}")
        print(f"     Why: {item['reason']}")
        print(f"     Effort: {item['effort']}")
        print(f"     Activate: {item['command']}")
        env = info.get('env')
        if env:
            print(f"     Env var: {env}")
    print()
    print('After activating, add models to agents.defaults.model.fallbacks in openclaw.json')
    print('Gateway hot-reloads — no restart needed.')


def cmd_status(registry):
    active = active_models(registry)
    inactive = {k: v for k, v in registry['providers'].items() if v.get('status') != 'active'}
    state = load_state()
    current_primary = state.get('current_primary', 'anthropic/claude-sonnet-4-6')
    budget_pct = state.get('last_pct', 0.0)

    print(json.dumps({
        'current_primary': current_primary,
        'budget_pct': budget_pct,
        'active_count': len(active),
        'inactive_count': len(inactive),
        'active_models': list(active.keys()),
        'inactive_models': list(inactive.keys()),
        'top_activation_picks': [p['model'] for p in registry.get('activation_priority', [])[:3]],
    }, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', help='Task type to route')
    parser.add_argument('--text', help='Infer task from message text')
    parser.add_argument('--budget-pct', type=float, default=0.0)
    parser.add_argument('--list-tasks', action='store_true')
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--activate-plan', action='store_true')
    args = parser.parse_args()

    registry = load_registry()

    if args.activate_plan:
        cmd_activate_plan(registry)
        return

    if args.status:
        cmd_status(registry)
        return

    if args.list_tasks:
        tasks = list(registry.get('task_routing', {}).keys())
        print(json.dumps({'available_tasks': tasks}, indent=2))
        return

    if args.text:
        task = infer_task_from_text(args.text)
        print(f'Inferred task: {task}', file=sys.stderr)
    elif args.task:
        task = args.task
    else:
        parser.print_help()
        sys.exit(1)

    result = route_task(task, registry, args.budget_pct)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
