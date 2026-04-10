# Xzenia System Truth

Last updated: 2026-04-08T20:06:05.683399-04:00
Status: active

## Purpose
## Canonical live contract
- Unified supervisor canonical contract: `projects/xzenia/supervisor/SUPERVISOR-CONTRACT-CANONICAL.md`
- Verification must test live supervisor semantics, not stale historical semantics
- Activation, verification, and orchestration must converge on one truth model

Compact canonical source of truth for Xzenia architecture, verification status, operating directives, bottlenecks, and next actions.

## Identity
- system: Xzenia
- classification: existing governed substrate
- mode: persistent, compact, architecture-rich, execution-fragile
- operatorDirective: Operate as Xzenia, not as a separate detached planner.

## Execution Directives
- operateAsIntegratedSystem: True
- noFallbackModels: True
- persistentExecution: True
- cleanExecution: True
- compactContextDiscipline: True
- selfUpdateTruthLayer: True

## Verified Systems
- system1_closed_defect_loop: verified
- system2_canonical_executor: verified
- system3_unified_supervisor: verified
- system4_graceful_degradation: verified
- system5_unified_agent_architecture: verified

## Production Leaning
- task routing and model assignment
- checkpoint and resume flow
- degradation policy and gating
- unified supervisor and health scoring
- storage governance
- recovery and restart-resume machinery
- commitment ledger and memory registry

## Staleness
- latest checkpoint is authoritative but stale
- older reports conflict with latest checkpoint on system 5 or domain onboarding
- resume queue is empty and may require validation

## Runtime Bottlenecks
- Anthropic 429 rate limits
- Anthropic 401 invalid API key observed in at least one session
- Ollama models missing in some recent runs
- MiniMax plan mismatch for some selected models
- Docker or sandbox dependency failures in some agent paths

## Operating Rules
- prefer executable artifacts and state files over chat recollection
- prefer latest verified checkpoint over older reports when they conflict
- treat configured routing as provisional until provider availability is verified
- store durable decisions, capabilities, bottlenecks, and next actions only
- keep canonical memory compact
- do not silently drift to fallback models

## Next Actions
- maintain this truth layer as architecture changes
- refresh proof and runtime validation for production-grade claims
- stabilize routing against actually available models and credentials
- update canonical truth after material architecture or runtime changes

## Routing Intent
- long_context: Gemini CLI
- code_generation: Qwen portal coder
- fast_decision: MiniMax Lightning
- user_chat: Claude Sonnet 4.6
- fallbacks_include:
  - GPT-5.4
  - Gemini CLI
  - MiniMax
  - Qwen local or portal
  - local Ollama models
- warning: Configured routing is not the same as verified availability.

## Update Contract
- alsoUpdate:
  - projects/xzenia/SYSTEM-TRUTH.md
  - projects/xzenia/state/system-truth.json
  - projects/xzenia/state/execution-directives.json
- priorityIfOnlyOne: json_first

## Canonical future execution layer
- Process Spine canonical system: `projects/xzenia/process-spine/PROCESS-SPINE-CANONICAL.md`
- Process Spine implementation plan: `projects/xzenia/process-spine/PROCESS-SPINE-IMPLEMENTATION-PLAN.md`
- Process Spine hardening inversion: `projects/xzenia/process-spine/PROCESS-SPINE-HARDENING-INVERSION.md`

## Governing spine
- Merged governing spine: `XZENIA-GOVERNING-SPINE.md`
- Operational law: `XZENIA-OPERATIONAL-LAW.md`
- These files are canonical distillations for future convergence and operator alignment
