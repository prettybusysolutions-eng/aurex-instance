# Unified Environment Map

Last updated: 2026-04-12 17:58 EDT
Status: ACTIVE EXTRACTION MAP

## 1. OpenClaw root substrate
Root: `/Users/marcuscoarchitect/.openclaw`

Verified major surfaces:
- agents/
- backups/
- context-nexus/
- credentials/
- cron/
- delivery-queue/
- desktop-bridge/
- devices/
- flows/
- identity/
- logs/
- media/inbound/
- memory/
- plugins/
- reports/
- openclaw.json
- exec-approvals.json

Scale note:
- extracted root tree count: 3908 entries

## 2. Agent/session substrate
Verified agent surfaces:
- `agents/aurex/`
- `agents/main/`
- `agents/claude-code/`
- `agents/ops-specialist/`
- `agents/research-specialist/`
- `agents/revenue-specialist/`

Verified session archives:
- large historical session archive under `agents/aurex/sessions/`
- active main-session archive under `agents/main/sessions/`
- session registries present (`sessions.json`)

## 3. Launch/runtime control plane
Verified LaunchAgents:
- `ai.openclaw.gateway.plist`
- `ai.openclaw.task-consumer.plist`
- multiple `com.xzenia.*.plist` agents
- Redis and PostgreSQL launch agents

This confirms a real host-side autonomous runtime layer, not just chat-driven execution.

## 4. Workspace substrate
Root workspace: `/Users/marcuscoarchitect/.openclaw/workspace`

Verified major domains:
- canonical governance files at root
- `platform-spine/`
- `revenue-copilot/`
- `projects/xzenia/`
- `task-queue/`
- `reports/`
- `memory/`
- `state/`
- `skills/`
- `system/`
- `data/`
- `logs/`
- `media/`

## 5. Cohesion view
The environment is composed of five interacting layers:
1. OpenClaw runtime root
2. agent/session memory substrate
3. host launch-agent control plane
4. governed workspace control repo
5. deep project/domain substrate under `projects/xzenia/`, `platform-spine/`, and `revenue-copilot/`

## 6. Current high-leverage leverage points
- canonical truth docs at workspace root
- platform-spine for durable execution
- task-queue for queued work and approvals
- context-nexus databases for memory continuity
- LaunchAgents as the true host automation spine
- projects/xzenia as the deep architecture substrate

## 7. Current fracture points
- observer historical launch-path drift
- root repo drift / exception sprawl
- model redundancy not currently healthy
- process spine not yet promoted
- meta-healing not freshly reproved
- revenue ingest closure incomplete

## 8. Use doctrine
This environment should now be treated as one governed machine with:
- root truth surfaces for control
- LaunchAgents for persistence and automation
- session archives for historical reconstruction
- workspace projects for capability depth
- proof artifacts for promotion decisions

No future claim of system status should ignore any of these layers.
