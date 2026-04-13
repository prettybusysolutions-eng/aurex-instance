---
name: resilience-fabric
description: Build, repair, and operate an autonomous local resilience layer for model fallback, checkpointed retries, healing loops, and channel/tool bridging without destructive resets. Use when asked to add automatic backup models, self-healing execution, unification/weaving between runtime layers, failure recovery, checkpoint/resume behavior, or resilient orchestration that keeps working when providers, token budgets, or local components fail.
---

# Resilience Fabric

Stabilize execution. Preserve continuity. Degrade gracefully instead of crashing.

## Core rules

- Prefer additive, reversible changes.
- Checkpoint before long or fragile operations.
- Classify failures before retrying.
- Avoid infinite retry loops; use bounded attempts and explicit downgrade tiers.
- Preserve a single canonical state file so separate runtimes can resume coherently.
- Treat "unification" as continuity across model/runtime boundaries, not magical merging.

## What this skill provides

- A fallback policy schema for primary/secondary/tertiary models.
- A local runner that retries with the next viable model when token/context/rate/timeout failures occur.
- A state file pattern that records the active model, failure history, and latest checkpoint.
- A bridge note for connecting this behavior into other local runtimes like Telegram voice bridges or project-specific wrappers.

## Workflow

1. Read `references/policy-schema.md`.
2. Create or update a policy JSON using the documented schema.
3. Use `scripts/check_models.py` to inspect which local models are available.
4. Use `scripts/run_with_fallback.py` for checkpointed execution with fallback tiers.
5. Persist important behavior decisions in a state file under `projects/xzenia/state/`.
6. If integrating with another runtime, call the runner as a wrapper instead of duplicating retry logic.

## Default policy guidance

Use a tiered stack like:

- Tier 1: strongest preferred remote/provider model
- Tier 2: strongest viable local model
- Tier 3: smaller fast local model
- Tier 4: emergency minimal model

Recommended local tiers on this machine:

- `qwen2.5:7b`
- `qwen2.5:3b`
- `llama3.2:3b`

## Bridging guidance

When asked to “weave/thread/unify”:

- Keep one shared checkpoint/state file.
- Route fragile model calls through the fallback runner.
- Log each switch with timestamp, reason, and previous model.
- Keep channel-specific adapters thin; the fallback/healing logic should live in one place.

## References

- Read `references/policy-schema.md` for the policy structure and failure mapping.

## Scripts

- `scripts/check_models.py` — inspect local Ollama model availability.
- `scripts/run_with_fallback.py` — run a prompt through a policy-controlled fallback chain and record state.
