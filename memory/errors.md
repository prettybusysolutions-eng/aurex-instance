# Error Log

## 2026-03-31 08:22 EDT — Boot integrity warnings
- MEMORY.md checkpoint is stale (>24h); last boot checkpoint recorded 2026-03-25.
- Missing daily memory files for 2026-03-30 and 2026-03-31 at boot; created 2026-03-31.md during recovery.
- memory/self-model.md is stale (>7 days).
- memory/pipeline.md is stale (>48 hours).
- TOOLS.md does not include status fields required by BRIDGE.md §4.3 consistency check.
- Action: continued in degraded-but-operational mode per BOOT/BRIDGE policy.

## 2026-03-31 08:30 EDT — Re-run boot integrity warnings
- memory/self-model.md remains stale (>7 days).
- memory/pipeline.md remains stale (>48 hours).
- TOOLS.md still does not include status fields required by BRIDGE.md §4.3 consistency check.
- Action: continued operating; no identity compromise and no interrupted task detected.

## 2026-04-02 21:14 EDT — Boot integrity + system scan
- self-model.md stale (>30 days, last: Feb 26 2026)
- pipeline.md stale (>30 days, last: Feb 26 2026)
- TOOLS.md missing status fields (carried forward from prior sessions)
- 7/10 cron jobs failing with LiveSessionModelSwitchError (6 disabled, 1 active with 1 error)
- Memory pressure: 7.76GB/8GB used, heavy swap activity causing UI duplicate sends
- OpenClaw update: already at 2026.4.2 (no update needed)
- Action: boot checkpoint written; repair sequence executing per Aurex directive

## 2026-04-02 22:06 EDT — Boot integrity warnings
- memory/daily/ directory was missing at boot relative to BRIDGE.md §1.3; created during boot recovery.
- BRIDGE.md §1.4 skill registry does not match actual workspace skill directories (registry is stale/incomplete versus installed skills set).
- Action: continued operating; no identity compromise, no interrupted task requiring automatic resume.

## 2026-04-03 01:01 EDT — Daily rollover boot integrity warning
- Daily memory file for 2026-04-03 was missing at boot check after rollover.
- Action: created `memory/2026-04-03.md` from template and continued operating.

## 2026-04-03 01:08 EDT — Telegram routing remediation
- Root issue: `session.dmScope` was set to `main`, collapsing direct-message routing into the shared main bucket and allowing Telegram delivery context to persist on `agent:main:main`.
- Observed contamination: `agent:main:main` carried `lastChannel=telegram`, `lastTo=telegram:6620375090`, and Telegram deliveryContext while originating from webchat.
- Fix applied: backed up `~/.openclaw/openclaw.json`, changed `session.dmScope` to `per-channel-peer`, added `session.identityLinks.aurex = ["telegram:6620375090"]`, and validated config JSON.
- Follow-up: existing live session metadata may still need a clean session rollover or gateway reload to fully flush stale delivery context.

## 2026-04-03 01:13 EDT — Boot integrity warning
- BRIDGE.md §1.4 skill registry remains stale/incomplete versus actual workspace skill directories (41 installed skill SKILL.md files observed).
- Action: continued operating in fail-soft mode; identity layer intact and no interrupted task required auto-resume.

## 2026-04-03 01:17 EDT — Boot integrity warning
- BRIDGE.md §1.4 skill registry remains stale/incomplete versus actual workspace skill directories (41 installed skill SKILL.md files observed).
- Action: continued operating in fail-soft mode; identity layer intact and no interrupted task required auto-resume.

## 2026-04-03 01:45 EDT — Boot integrity warning
- BRIDGE.md §1.4 skill registry remains stale/incomplete versus actual workspace skill directories (41 installed skill SKILL.md files observed).
- Action: continued operating in fail-soft mode; identity layer intact and no interrupted task required auto-resume.

## 2026-04-03 01:52 EDT — Config drift root cause identified
- Confirmed recurring local config writer: LaunchAgent `com.xzenia.model-guardian` runs every 300s and executes `projects/xzenia/model-guardian/guardian_cycle.py`.
- `guardian_cycle.py` invokes `model_switcher.py`, which atomically rewrites `~/.openclaw/openclaw.json` after patching model primary state.
- This explains ongoing model config drift. It does not directly set `session.dmScope`, but it can preserve/propagate stale config state if operating on an older config image.
- No evidence of external attack; issue is local automation conflict / config governance gap.

## 2026-04-03 01:59 EDT — Hardening action applied
- Added `projects/xzenia/model-guardian/config_guard.py` to enforce narrow mutation boundaries on `openclaw.json`.
- Added `projects/xzenia/model-guardian/CONFIG-GOVERNANCE.md` documenting allowed vs forbidden mutation surface.
- Patched `model_switcher.py` to validate candidate config before write and reduced switch ladder to trusted working models.
- Patched `guardian_cycle.py` ladder to match the hardened set.
- Strategic lesson persisted: model-switch automation is not a routing authority.

## 2026-04-03 02:05 EDT — Routing governance layer added
- Added `projects/xzenia/orchestration/ROUTING-GOVERNANCE.md` declaring `session.dmScope = per-channel-peer` as canonical policy.
- Added `routing_guard.py` and `routing_drift_watch.py`.
- `routing_guard.py` successfully attempted to restore canonical routing, but immediate drift watch still observed `session.dmScope = main`, confirming an active concurrent writer race.
- Conclusion: routing policy now has explicit governance, but at least one additional local writer still needs to be identified or fenced.

## 2026-04-03 02:11 EDT — Boot integrity warning
- BRIDGE.md §1.4 skill registry remains stale/incomplete versus actual workspace skill directories (41 installed skill SKILL.md files observed).
- Action: continued operating in fail-soft mode; identity layer intact and no interrupted task required auto-resume.

## 2026-04-03 07:12 EDT — Heartbeat repair executed
- Redis was not running (`connection refused`); started non-destructively via `brew services start redis`.
- Continuity checkpoint was stale because no recent save had been performed; refreshed via `projects/xzenia/scripts/continuity-guard.py save heartbeat-repair ...`.
- Hardened OpenClaw config file permissions from world-readable to `600`.
- Post-repair validation expected: Redis responds to ping, checkpoint age near-zero, db_layer health healthy with Redis connected.

## 2026-04-03 09:57 EDT — Robust remaining-issues hardening completed
- Restored routing policy in `~/.openclaw/openclaw.json` to `session.dmScope = per-channel-peer` with canonical Aurex identity link.
- Enabled `agents.defaults.sandbox.mode = all` so small-model Ollama fallbacks now satisfy security audit expectations.
- Preserved `tools.deny = ["group:web", "browser"]` for small-model safety.
- Removed ineffective `gateway.nodes.denyCommands` entries that audit flagged as non-functional exact-name mismatches.
- Updated `projects/xzenia/model-guardian/config_guard.py` so protected paths must remain: routing policy, identity links, sandbox mode, and tool deny list.
- Updated `BRIDGE.md §1.4` from stale hand-written registry to current installed dynamic skill inventory.
- Revalidation result: security audit reduced from 1 critical + 2 warn to 0 critical + 1 conditional warn (`gateway.trustedProxies_missing`, acceptable while gateway remains loopback/local-only).

Format: [timestamp] | [severity] | [component] | [error] | [resolution]
