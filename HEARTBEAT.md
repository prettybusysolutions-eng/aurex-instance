# HEARTBEAT.md — Execution Stack

_On heartbeat, execute. Do not merely acknowledge._

## 1. Active Product Status Checks

### Context Nexus
```bash
python3 /Users/marcuscoarchitect/.openclaw/agents/aurex/workspace/projects/context-nexus/scripts/release_hardening_loop.py
cat /Users/marcuscoarchitect/.openclaw/agents/aurex/workspace/projects/context-nexus/release-status.json
```
- State `READY_TO_PUBLISH`: no action needed — done
- State `BLOCKED_WITH_EXACT_CAUSE`: fix smallest blocker, rerun, report
- State missing or stale: rerun loop, report new state

### LeakLock
```bash
# Check if Render deploy has happened
# Check release-status.json if it exists
ls /Users/marcuscoarchitect/.openclaw/agents/aurex/workspace/projects/xzenia-saas/release-status.json 2>/dev/null
```
- If deployed: verify webhook fires, verify DB tables
- If not deployed: no action (human required — Render setup)

---

## 2. Truth Discipline

**Never say executing unless one of these is true:**
- A file changed on disk
- A command ran and produced verified output
- A process started or stopped
- A status artifact was written or updated

**If none of those happened → say blocked.**

---

## 3. Stack Hardening Priorities

Continuously prefer:
1. **Artifact proof over narration** — show the output, not the intent
2. **Blockers over optimism** — name the exact failure, not the hope
3. **Deterministic paths over speculative ones** — if it worked before, it should work again
4. **Local-first reliability** — don't depend on remote services you can't verify
5. **Shipping over building** — if it's ready, ship it

---

## 4. Memory Maintenance (Every Few Days)

1. Read recent `memory/YYYY-MM-DD.md` files
2. Identify significant events, lessons, decisions
3. Update `MEMORY.md` with distilled learnings
4. Remove outdated MEMORY.md entries that are no longer relevant

---

## 5. Skill-Driven Proactive Actions

When background cycles are available, consider:
- **github**: Check for new issues on `prettybusysolutions-eng/context-nexus` or `xzenia-leaklock`
- **blogwatcher**: Check monitored feeds for relevant updates
- **weather**: If morning and operator might travel — check forecast
- **gog calendar**: Any events in next 24h that need reminder?

---

## 6. Quiet Rule

**`HEARTBEAT_OK`** if and only if:
- Nothing materially changed
- No blockers need surfacing
- No proactive actions available
- It has been <30 minutes since last meaningful check

**Always report when:**
- A product reached `READY_TO_PUBLISH`
- A blocker was removed or fixed
- An external event needs attention (payment received, new issue, etc.)
- Operator has been >8h without a message

---

## 7. Execution Artifact Locations

```
Context Nexus: ~/.../projects/context-nexus/release-status.json
LeakLock:     ~/.../projects/xzenia-saas/release-status.json
Heartbeat log: ~/.openclaw/workspace-aurex/memory/heartbeat-state.json
Daily memory: ~/.openclaw/workspace-aurex/memory/YYYY-MM-DD.md
```

---

_This file is the execution contract. Follow it strictly. No inference, no carryover from prior chats._
