#!/usr/bin/env python3
import json
import time
from pathlib import Path

LEDGER = Path('/Users/marcuscoarchitect/.openclaw/workspace/private/machine-settlement-ledger.jsonl')
LOG = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/ledger-watch.log')
SEEN = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/ledger-watch.state')

last_size = 0
if SEEN.exists():
    try:
        last_size = int(SEEN.read_text().strip() or '0')
    except Exception:
        last_size = 0

while True:
    try:
        if LEDGER.exists():
            size = LEDGER.stat().st_size
            if size < last_size:
                last_size = 0
            if size > last_size:
                with LEDGER.open('r') as f:
                    f.seek(last_size)
                    chunk = f.read()
                for line in chunk.splitlines():
                    if 'CONSUMED' in line:
                        LOG.parent.mkdir(parents=True, exist_ok=True)
                        with LOG.open('a') as out:
                            out.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')} CONSUMED {line}\n")
                last_size = size
                SEEN.write_text(str(last_size))
    except Exception as e:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open('a') as out:
            out.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')} ERROR {e}\n")
    time.sleep(15)
