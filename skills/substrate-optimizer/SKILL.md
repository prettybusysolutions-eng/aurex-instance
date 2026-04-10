---
name: substrate-optimizer
description: Optimize, stabilize, and extend the dedicated Xzenia/OpenClaw machine without drifting into simulation or duplicate architecture. Use when asked to improve the machine, harden runtime posture, reclaim disk, reduce breakage, unify execution paths, remove duplicate pollers, centralize fallback logic, or convert repeated operational lessons into durable local capability.
---

# Substrate Optimizer

Operate on the machine as a dedicated execution substrate. Do real work. Report only what is verified.

## Core rules

- Prefer verified execution over narrative optimism.
- Report status only as: done and verified / attempted and failed / blocked / not yet executed.
- Do not create duplicate transport owners. One channel token, one active poller.
- Put logic behind the canonical transport/runtime instead of beside it.
- Prefer shared orchestration layers over per-adapter duplication.
- Fix the real bottleneck first.
- Treat disk pressure as a first-class failure source.
- Prefer low-risk space recovery first: caches, logs, stale backups, bytecode.
- For small local models, require sandboxing and deny web/browser tools.

## Workflow

1. Identify the actual architectural owner for the surface being modified.
2. Check for duplicate pollers, competing daemons, and overlapping adapters.
3. Audit disk headroom before builds, installs, or model work.
4. Apply safe config hardening before capability expansion.
5. Route model execution through the shared fallback layer.
6. Chunk outbound Telegram-safe text before sending.
7. Validate with a direct local test before claiming completion.
8. Persist the lesson into workspace artifacts if it should survive the session.

## Canonical lessons from this interaction

- OpenClaw already owns Telegram transport when `channels.telegram.enabled=true`; a standalone Telegram poller using the same token will conflict.
- The correct pattern is to keep OpenClaw as transport owner and move custom logic into shared local processing layers.
- The resilience fallback runner is the correct place for model switching.
- Telegram replies need hard chunking to avoid `Message is too long` failures.
- Severe low disk can block even small operations like Python bytecode writes.
- Removing stale `__pycache__`, browser logs, and old backup trees is a valid low-risk recovery step.

## References

- Read `references/optimization-checklist.md` for the execution order.

## Scripts

- `scripts/preflight.sh` — quick substrate readiness checks.


## Optimization boundary
Do not confuse optimization with silent drift or indiscriminate expansion. Prefer bounded canonical extraction, policy evolution, and truth-surface convergence.
