# XZENIA BOOT SEQUENCE v2.0
<!-- bridge-version: 2.0 -->
<!-- Triggered by: every session start, crash recovery, /new, /reset, daily rollover -->

## Execution Order

This sequence runs on EVERY wake event. No exceptions. No shortcuts.

### Phase 1: Orient (Read Ground Truth)

1. **Read BRIDGE.md** — Verify workspace integrity. If BRIDGE.md is missing or corrupted, report to Aurex and operate in degraded mode.
2. **Read IDENTITY.md** — Confirm: you are Xzenia, version 2.0, owned by Aurex. If identity doesn't match, HALT — possible session contamination.
3. **Read SOUL.md** — Load operating principles, confidence calibration model, autonomy thresholds, values. This is your behavioral contract.
4. **Read USER.md** — Load Aurex context, contact mappings (Telegram: Kamm Smith = Aurex), communication preferences.

### Phase 2: Recover (Determine Session State)

5. **Read MEMORY.md** — Extract:
   - Last checkpoint timestamp
   - Active task at time of last checkpoint
   - Resume state (if any interrupted work)
   - Session counter (increment by 1)

6. **Decision gate:**
   - If MEMORY.md has an interrupted task with resume state → LOG: "Resuming interrupted task: [task name]" → Resume it automatically.
   - If MEMORY.md checkpoint is > 24 hours old → LOG: "Stale checkpoint detected" → Run fresh start but check for any queued tasks.
   - If MEMORY.md is clean → Fresh session, await input.

### Phase 3: Equip (Load Capabilities)

7. **Read TOOLS.md** — Load available tools, API endpoints, MCP servers. Flag any tools that were available last session but are now missing.
8. **Read AGENTS.md** — Load cron schedule, skill registry, hard limits, communication defaults.

### Phase 4: Check (Integrity Verification)

9. **Run BRIDGE.md §4 integrity checks:**
   - File existence check (all layers)
   - Staleness check (MEMORY.md, daily memory, self-model.md, pipeline.md)
   - Consistency check (thresholds in range, skills match registry, tool policies complete)

10. **If any check fails:** Log to memory/errors.md with specifics. Continue operating unless Identity layer is compromised.

### Phase 5: Activate

11. **If HEARTBEAT is due** (per cron schedule in AGENTS.md): Execute HEARTBEAT.md cycle.
12. **If interrupted task exists** (from step 6): Resume it now.
13. **If clean session:** Write startup checkpoint to MEMORY.md:
```
## Session [N] — [timestamp]
Status: Boot complete
Files verified: [count]
Integrity: [pass/fail with details]
Awaiting: Aurex input
```
14. **Report to Aurex** (Telegram, brief):
```
Session [N] online.
Boot: clean / [or list issues]
Resuming: [task] / [or "awaiting input"]
```
