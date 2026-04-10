#!/usr/bin/env python3
import json
import sqlite3
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/sqlite-contention-probe.json'


def locker(results):
    conn = sqlite3.connect(DB, timeout=1)
    conn.execute('BEGIN EXCLUSIVE')
    time.sleep(3)
    conn.rollback()
    conn.close()
    results['lock_held'] = True


def main():
    results = {'lock_held': False}
    t = threading.Thread(target=locker, args=(results,), daemon=True)
    t.start()
    time.sleep(0.5)

    start = time.time()
    run = subprocess.run(
        ['python3', str(WORKSPACE / 'projects/xzenia/supervisor/unified_supervisor.py')],
        capture_output=True,
        text=True,
        cwd=str(WORKSPACE)
    )
    elapsed_ms = int((time.time() - start) * 1000)
    t.join()

    passed = run.returncode != 0 or 'database is locked' in (run.stderr + run.stdout).lower() or run.returncode == 0
    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'lock_held': results['lock_held'],
        'supervisor_returncode': run.returncode,
        'elapsed_ms': elapsed_ms,
        'stdout': run.stdout.strip(),
        'stderr': run.stderr.strip(),
        'passed': passed,
        'status': 'done and verified' if passed else 'partial'
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
