# Zero-to-One Pain Points

Last updated: 2026-04-13 18:08 EDT
Status: ACTIVE

## Top 3 likely pain points in the OpenClaw community

### 1. Session drift and continuity loss
Pain:
- users lose track of what was done
- interrupted runs are hard to resume cleanly
- state is spread across files and sessions

Free tool candidate:
- continuity audit / resume helper skill

### 2. Runtime/config breakage and unclear failure diagnosis
Pain:
- users do not know why gateway, routing, or tool behavior broke
- config drift is hard to isolate
- health checks are fragmented

Free tool candidate:
- local runtime doctor / config drift explainer

### 3. Residue chaos and workspace sprawl
Pain:
- canonical vs runtime vs archive boundaries are unclear
- root repos get polluted
- users cannot tell what should be promoted, ignored, or archived

Free tool candidate:
- workspace residue classifier / thin-root assistant

## Selection rule
Build the first free tools where:
- the pain is frequent
- the fix is local and cheap
- the result is easy to explain
- a pro upgrade path is obvious
