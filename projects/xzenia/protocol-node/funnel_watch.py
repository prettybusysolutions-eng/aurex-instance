#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

SRC = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/machine-pings.jsonl')
OUT = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/funnel-state.json')

rows = []
if SRC.exists():
    for line in SRC.read_text(errors='ignore').splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            continue

funnels = defaultdict(lambda: {'registry_preview': 0, 'translate': 0})
for row in rows:
    key = f"{row.get('source_ip','')}|{row.get('user_agent','')}|{row.get('agent_id','')}"
    path = row.get('path','')
    if path == '/registry-preview':
        funnels[key]['registry_preview'] += 1
    elif path == '/mcp/v1/translate':
        funnels[key]['translate'] += 1

result = {
    'tracked_agents': [
        {'key': k, **v, 'dropoff': v['registry_preview'] > 0 and v['translate'] == 0}
        for k, v in funnels.items()
    ]
}
OUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
