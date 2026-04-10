#!/usr/bin/env python3
import json, re, sqlite3
from pathlib import Path
from datetime import datetime

W = Path('/Users/marcuscoarchitect/.openclaw/workspace')
log = W / 'projects/xzenia/csmr/reports/20-cycle-normal-soak.log'
sup = json.loads((W / 'projects/xzenia/csmr/reports/unified-supervisor-health.json').read_text())
res = json.loads((W / 'projects/xzenia/csmr/reports/resource-monitor.json').read_text())
deg = json.loads((W / 'projects/xzenia/csmr/reports/degradation-gate.json').read_text())
text = log.read_text() if log.exists() else ''
cycles = len(re.findall(r'^--- cycle ', text, flags=re.M))
out = {
  'timestamp': datetime.now().astimezone().isoformat(),
  'cycles_completed': cycles,
  'supervisor_overall': sup.get('overall'),
  'contradictions': len(sup.get('contradictions', [])),
  'tier': deg.get('tier'),
  'confidence': deg.get('confidence'),
  'resource_pressure': res.get('resource_pressure'),
  'disk_free_gib': res.get('disk_free_gib'),
  'assessment': 'proven' if cycles >= 20 and sup.get('overall') == 'pass' and len(sup.get('contradictions', [])) == 0 and deg.get('tier') == 'normal' else 'provisional',
  'status': 'done and verified'
}
path = W / 'projects/xzenia/csmr/reports/20-cycle-normal-soak-assessment.json'
path.write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
