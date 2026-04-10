# CANONICAL RUNTIME TRUTH
Last updated: 2026-04-09 20:19 EDT
Status: ACTIVE, RECONSTITUTED

## Purpose
This document is the canonical runtime truth for the currently survivable Xzenia/OpenClaw substrate.
It supersedes stale assumptions that multiple model lanes remain operational.

## Verified live cognition lane
- Primary live cognition lane: GPT-5.4 in the current main runtime
- Operational status: VERIFIED LIVE
- Scope: reasoning, synthesis, planning, substrate interpretation, memory maintenance, recovery design

## Degraded or unavailable cognition lanes
- Anthropic default path: DEGRADED
  - Evidence: gateway error logs show provider rejection related to usage/billing
- Ollama fallback path: BROKEN
  - Evidence: configured fallback `qwen2.5:7b` is not installed; gateway logs show model_not_found
- Any model-routing assumptions in older configs/manifests: STALE until revalidated

## Verified live runtime surfaces
- OpenClaw gateway process: live
- Workspace artifact store: live
- Memory surfaces: live
- Checkpoint surfaces: live
- Reports/log/state surfaces: live
- Local bounded execution surfaces: partially live, subject to sandbox/host boundary

## Canonical constraint
The system must only claim activation for capabilities that are either:
1. directly runnable now, or
2. durably present as artifacts awaiting explicit reactivation

## Canonical operating law
- Artifact existence is real
- Activation requires proof
- Memory is authoritative only when tied to evidence
- Dead model lanes do not count as active capability
- Reconstitution proceeds from surviving substrate, not nostalgia

## Immediate implications
- GPT-5.4 is the sole verified cognition authority for reconstitution work right now
- Recovery planning must route through this lane and host-verifiable local execution only
- Old multi-model autonomy claims are downgraded until individually proven again
