#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
QUEUE = WORKSPACE / 'projects/xzenia/state/resume-queue.json'
CHECKPOINT = WORKSPACE / 'projects/xzenia/state/latest-checkpoint.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/queue-checkpoint-contradiction-probe.json'


def main():
    q_orig = QUEUE.read_text() if QUEUE.exists() else None
    c_orig = CHECKPOINT.read_text() if CHECKPOINT.exists() else None
    try:
        QUEUE.write_text(json.dumps({'updatedAt': datetime.now().astimezone().isoformat(), 'source': 'probe', 'items': [{'id': 'fake-pending-item', 'status': 'pending'}]}, indent=2) + '\n')
        CHECKPOINT.write_text(json.dumps({'timestamp': datetime.now().astimezone().isoformat(), 'resumeInstruction': 'continue real work', 'nextFrontier': ['different-real-item']}, indent=2) + '\n')
        import subprocess
        res = subprocess.run(['python3', str(WORKSPACE / 'projects/xzenia/supervisor/unified_supervisor.py')], capture_output=True, text=True, cwd=str(WORKSPACE))
        payload = json.loads(res.stdout) if res.stdout.strip().startswith('{') else {'parse_failed': True, 'stdout': res.stdout, 'stderr': res.stderr}
        contradictions = payload.get('contradictions', [])
        passed = any(c.get('type') == 'frontier_mismatch' for c in contradictions)
        out = {
            'timestamp': datetime.now().astimezone().isoformat(),
            'passed': passed,
            'contradictions': contradictions,
            'status': 'done and verified' if passed else 'partial'
        }
        OUT.write_text(json.dumps(out, indent=2) + '\n')
        print(json.dumps(out, indent=2))
        raise SystemExit(0 if passed else 1)
    finally:
        if q_orig is not None:
            QUEUE.write_text(q_orig)
        if c_orig is not None:
            CHECKPOINT.write_text(c_orig)


if __name__ == '__main__':
    main()
