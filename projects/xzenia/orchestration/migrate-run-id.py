#!/usr/bin/env python3
import os, sqlite3
for db_path in [os.path.expanduser('~/.openclaw/workspace/data/xzenia/causal_memory.db'), os.path.expanduser('~/.openclaw/xzenia-data/causal_memory.db')]:
    if os.path.exists(db_path):
        break
else:
    raise SystemExit('ERROR: causal_memory.db not found')
print(f'Migrating: {db_path}')
conn = sqlite3.connect(db_path)
c = conn.cursor()
try:
    c.execute('SELECT run_id FROM leakage_findings LIMIT 1')
    print('leakage_findings.run_id already exists')
except Exception:
    c.execute('ALTER TABLE leakage_findings ADD COLUMN run_id TEXT')
    print('Added run_id to leakage_findings')
try:
    c.execute('SELECT run_id FROM recovery_actions LIMIT 1')
    print('recovery_actions.run_id already exists')
except Exception:
    c.execute('ALTER TABLE recovery_actions ADD COLUMN run_id TEXT')
    print('Added run_id to recovery_actions')
c.execute('''CREATE TABLE IF NOT EXISTS analysis_runs (
 run_id TEXT PRIMARY KEY,
 client_id TEXT NOT NULL,
 started_at TEXT NOT NULL,
 completed_at TEXT,
 finding_count INTEGER DEFAULT 0,
 total_leakage REAL DEFAULT 0,
 action_count INTEGER DEFAULT 0,
 status TEXT DEFAULT 'running',
 superseded_findings INTEGER DEFAULT 0,
 superseded_actions INTEGER DEFAULT 0
)''')
c.execute('CREATE INDEX IF NOT EXISTS idx_findings_run ON leakage_findings(run_id)')
c.execute('CREATE INDEX IF NOT EXISTS idx_actions_run ON recovery_actions(run_id)')
conn.commit(); conn.close(); print('Migration complete')
