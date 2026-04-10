# Recovery Playbook

Use this when the machine wakes, restarts, or the live session context is gone.

## Goal
Reconstruct Xzenia's active state from local artifacts only.

## Recovery order
1. Read `projects/xzenia/state/latest-checkpoint.json`.
2. Read `MEMORY.md` and the latest daily note in `memory/`.
3. Inspect `projects/xzenia/csmr/ledger/causal_ledger.sqlite`.
4. Inspect `projects/xzenia/csmr/promotions/` and `projects/xzenia/csmr/reports/`.
5. Read `projects/xzenia/orchestration/resilience-policy.json` and `openclaw-model-registry.json`.
6. Sync `projects/xzenia/orchestration/bottleneck-registry.json` into `projects/xzenia/state/resume-queue.json` via `projects/xzenia/orchestration/sync_charter_to_resume_queue.py`.
7. Resume the highest-priority pending item in `projects/xzenia/state/resume-queue.json`.

## Hard rules
- Prefer local state over remote transcript assumptions.
- Do not assume external servers remember anything essential.
- If checkpoint and ledger disagree, trust the ledger for event history and checkpoint for declared intent.
- If the active runtime is degraded, stabilize first, then resume work.

## Current known-good summary
- Canonical Telegram owner: OpenClaw gateway.
- Canonical processor plugin: live-load verified.
- CSMR proposal lifecycle scaffold: working through promotion.
- Latest promoted proposal: inspect `projects/xzenia/csmr/promotions/`.
