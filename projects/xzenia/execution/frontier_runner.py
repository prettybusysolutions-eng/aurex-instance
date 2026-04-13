#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
STATE_DIR = WORKSPACE / 'projects/xzenia/state'
RUNNER_STATE = STATE_DIR / 'frontier-runner-state.json'
RUNNER_QUEUE = STATE_DIR / 'frontier-runner-queue.json'
RUNNER_REPORT = STATE_DIR / 'frontier-runner-report.json'

DEFAULT_STEPS = [
    'automatic truth-discipline enforcement',
    'continuity spine unification',
    'mixed subtree runtime unification',
    'automated residue governance',
    'undeniable recurring commercial loop',
    'universal extraction from proven machine'
]


def now():
    return datetime.now().astimezone().isoformat()


def ensure_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def init():
    ensure_dir()
    queue = load_json(RUNNER_QUEUE, {
        'createdAt': now(),
        'steps': [
            {'name': step, 'status': 'pending'} for step in DEFAULT_STEPS
        ]
    })
    state = load_json(RUNNER_STATE, {
        'updatedAt': now(),
        'currentStep': None,
        'status': 'idle'
    })
    report = load_json(RUNNER_REPORT, {
        'updatedAt': now(),
        'completedSteps': [],
        'failedSteps': [],
        'currentBoundary': None
    })
    write_json(RUNNER_QUEUE, queue)
    write_json(RUNNER_STATE, state)
    write_json(RUNNER_REPORT, report)
    return queue, state, report


def mark_next_running(queue, state):
    for step in queue['steps']:
        if step['status'] == 'pending':
            step['status'] = 'running'
            state['currentStep'] = step['name']
            state['status'] = 'running'
            state['updatedAt'] = now()
            return step['name']
    state['currentStep'] = None
    state['status'] = 'complete'
    state['updatedAt'] = now()
    return None


def main():
    queue, state, report = init()
    current = mark_next_running(queue, state)
    report['updatedAt'] = now()
    report['currentBoundary'] = 'chat-external execution still required for full completion'
    write_json(RUNNER_QUEUE, queue)
    write_json(RUNNER_STATE, state)
    write_json(RUNNER_REPORT, report)
    print(json.dumps({
        'status': state['status'],
        'currentStep': current,
        'queueFile': str(RUNNER_QUEUE),
        'stateFile': str(RUNNER_STATE),
        'reportFile': str(RUNNER_REPORT)
    }, indent=2))


if __name__ == '__main__':
    main()
