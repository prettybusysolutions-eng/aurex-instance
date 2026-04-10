# CANONICAL SUPERVISOR CONTRACT

Last updated: 2026-04-09 21:56 EDT
Status: CANONICAL

## Canonical authority
The live authority for supervisory truth is `projects/xzenia/supervisor/unified_supervisor.py` as executed under current runtime conditions.

## Governing rule
Verification must validate the live supervisor contract actually enforced now, not historical or inferred contracts.

## Current contract semantics
1. Supervisor emits mixed stdout with human-readable header lines followed by a JSON payload.
2. Decision Core integration is first-class and part of the health contract.
3. Current contradiction detection is based on:
   - ready registry top item vs pending queue top item mismatch
   - storage reclaim pressure conditions
   - stalled in-progress registry items
4. Current supervisor does **not** treat checkpoint frontier drift alone as a contradiction signal.
5. `overall`, `health_score`, `components`, `contradictions`, `stalled_items`, `recommended_action`, and `remediation` are the canonical payload surfaces.

## Verification consequences
- Probes must parse mixed stdout robustly.
- Probes must validate registry↔queue contradiction semantics, not obsolete queue↔checkpoint semantics.
- Any probe encoding stale semantics must be updated or retired.

## Activation rule
No verification artifact is promotable unless it validates this canonical contract or explicitly declares why it differs.

## Unification law
Activation, verification, and orchestration must share one truth model.
If execution truth and verification truth diverge, execution truth is canonical until verification is updated and re-proved.
