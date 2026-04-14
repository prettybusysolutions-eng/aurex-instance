#!/usr/bin/env python3
from pathlib import Path
import time

LOG = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/machine-pings.jsonl')
MAX_AGE_SECONDS = 12 * 60 * 60

if not LOG.exists():
    raise SystemExit(0)

cutoff = time.time() - MAX_AGE_SECONDS
kept = []
for line in LOG.read_text(errors='ignore').splitlines():
    kept.append(line)

# current rows do not carry timestamps yet, so keep file bounded by last 500 rows until timestamped rows exist
kept = kept[-500:]
LOG.write_text(('\n'.join(kept) + '\n') if kept else '')
