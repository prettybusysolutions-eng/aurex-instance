# HEARTBEAT.md — Execution Contract

_On heartbeat, execute. Run every phase. No narration without artifact change._

---

## Phase 1: Pre-Action Security Check

Before ANY exec, diff, write, or push:

```
Check against 26 security conditions:
- DESTRUCTIVE_OPERATIONS (rm -rf /etc/, /root/, /usr/)
- CREDENTIAL_EMBED (API_KEY=, sk_live_, gh p_)
- COMMAND_SUBSTITUTION (| sh, | bash, $(), <())
- GIT_DEFAULT_BRANCH_PUSH (git push origin main)
- ZSH_DANGEROUS_COMMANDS (zmodload, ztcp, zpty)
- JQ_SYSTEM_FUNCTION (jq.*$(, jq.*|sh)

Allowed:
- pip install -r requirements.txt
- npm install
- rm -rf node_modules/
- git push origin fix/... or feat/...
- curl -s -O (read-only)
```

If BLOCKED → do not execute. Report exact block.

---

## Phase 2: Session Memory

1. Read `memory/YYYY-MM-DD.md` (today)
2. Read `MEMORY.md` (long-term)
3. Note any unresolved blockers from previous sessions
4. Note any products needing attention

---

## Phase 3: Active Product Status Checks

Run these checks in order:

### DenialNet (port 8001)
```bash
curl -s http://127.0.0.1:8001/health
curl -s http://127.0.0.1:8001/stats | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'patterns: {d[\"active_patterns\"]}, queries: {d[\"total_queries\"]}')"
```
- Not responding → restart: `cd ~/.openclaw/agents/aurex/workspace/projects/denialnet && nohup uvicorn routes:app --port 8001 &`
- Report only if materially changed

### CPIN (port 8002)
```bash
curl -s http://127.0.0.1:8002/cpin/health
curl -s http://127.0.0.1:8002/cpin/stats | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'patterns: {d[\"active_patterns\"]}, signals: {d[\"signal_clusters\"]}')"
```
- Not responding → restart: `cd ~/.openclaw/agents/aurex/workspace/projects/cpin && nohup uvicorn routes:app --port 8002 &`

### VerifiAgent (port 8003)
```bash
curl -s http://127.0.0.1:8003/verify/health
```
- Not responding → restart: `cd ~/.openclaw/agents/aurex/workspace/projects/verifiagent && nohup uvicorn app:app --port 8003 &`

### AION Platform (port 8004)
```bash
curl -s http://127.0.0.1:8004/verify/health
```
- Not responding → restart: `cd ~/.openclaw/agents/aurex/workspace/projects/aion && nohup uvicorn app:app --port 8004 &`

---

## Phase 4: Truth Discipline

**Never say executing unless one of these is true:**
- A file changed on disk
- A command ran and produced verified output
- A process started or stopped
- A status artifact was written or updated

**If none of those happened → say blocked.**

---

## Phase 5: GitHub Sync

Check for any push failures from previous session:
```bash
cd ~/.openclaw/workspace-aurex && git status
```
If behind → push.

---

## Phase 6: Stack Hardening

For any product in development, run release hardening loop:
```bash
python3 /path/to/project/scripts/release_hardening_loop.py
```
Read: `release-status.json`
Output: `state` = `READY_TO_PUBLISH` | `BLOCKED_WITH_EXACT_CAUSE`

---

## Phase 7: Dream Consolidation

On session end (or every ~30 min in long sessions):
```python
from services.dream_consolidation import DreamConsolidation
dream = DreamConsolidation("~/.openclaw/workspace-aurex/memory")
dream.consolidate(dry_run=False)
```

---

## Quiet Rule

**HEARTBEAT_OK** if and only if:
- Nothing materially changed
- No blockers need surfacing
- No proactive actions available
- It has been <30 minutes since last meaningful check

**Always report when:**
- A product reached `READY_TO_PUBLISH`
- A blocker was removed or fixed
- An external event needs attention (payment received, new issue)
- Operator has been >8h without a message

---

## Execution Artifact Locations

```
DenialNet:    ~/.openclaw/agents/aurex/workspace/projects/denialnet/release-status.json
CPIN:         ~/.openclaw/agents/aurex/workspace/projects/cpin/release-status.json
VerifiAgent:  ~/.openclaw/agents/aurex/workspace/projects/verifiagent/release-status.json
AION:         ~/.openclaw/agents/aurex/workspace/projects/aion/
Heartbeat:    ~/.openclaw/workspace-aurex/memory/heartbeat-state.json
Daily:        ~/.openclaw/workspace-aurex/memory/YYYY-MM-DD.md
```

---

_This file is the execution contract. Follow it strictly. Every phase. No shortcuts._
