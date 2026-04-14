#!/usr/bin/env python3
from pathlib import Path
import time

ROOT = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node')
MAX_BYTES = 10 * 1024 * 1024
MAX_AGE_SECONDS = 7 * 24 * 60 * 60
LOGS = [
    ROOT / 'ledger-watch.log',
    ROOT / 'ledger-watch.stdout.log',
    ROOT / 'ledger-watch.stderr.log',
    ROOT / 'gpu-alpha-refresh.log',
    ROOT / 'gpu-alpha-refresh.err.log',
    ROOT / 'machine-pings-prune.log',
    ROOT / 'machine-pings-prune.err.log',
    ROOT / 'multiplexer.log',
    ROOT / 'multiplexer.err.log',
]
now = time.time()
for path in LOGS:
    if not path.exists():
        continue
    try:
        st = path.stat()
        if st.st_size > MAX_BYTES or (now - st.st_mtime) > MAX_AGE_SECONDS:
            path.write_text('')
    except Exception:
        pass
