# Governed Reconfiguration Plan

Last updated: 2026-04-12 17:34 EDT
Status: ACTIVE

## Mission
Convert the system from extraordinary-but-drifting into extraordinary-and-governed.

## Phase 1: Truth reconciliation
Completed:
- canonical root truth surfaces updated to current posture
- stale optimism removed
- broken observer lane and root drift promoted to first-class bottlenecks

## Phase 2: Broken subsystem repair prioritization

### Priority A: observer/runtime dependency repair
Evidence:
- `logs/observer.log` repeats `/bin/sh: node: command not found`
Why first:
- active repeated failure
- contaminates observability and proof quality
- likely high leverage, low conceptual ambiguity
Action:
- locate all observer/watchdog launch surfaces invoking `node`
- normalize runtime path resolution to absolute node binary or a stable shell environment
- patch observer entrypoint to be self-resolving and emit state
- produce fresh validation artifact after repair

Status update:
- observer entrypoint patched with `#!/usr/bin/env node`
- observer now writes runtime state to `state/observer-state.json`
- remaining work is launch-surface reproval

### Priority B: root repo drift closure
Evidence:
- root `git status --short` shows broad untracked/generated/runtime mass
- violates `ROOT-REPO-POLICY.md`
Why second:
- weakens provenance, recoverability, and strategic clarity
Action:
- classify root contents into canonical vs generated/runtime/subproject domains
- move or ignore generated/runtime mass
- preserve only thin control surfaces in root git lifecycle

### Priority C: subsystem classification ledger
Evidence:
- many surfaces are present but not freshly reproved
Why third:
- prevents false promotion and future drift
Action:
- create one ledger classifying major systems as proven, provisional, stale, broken
- bind promotion to fresh proof only

### Priority D: meta-healing reproval
Evidence:
- present but unverified; prior watchdog compatibility defect noted
Action:
- run fresh validation or demote explicitly

### Priority E: process spine promotion decision
Evidence:
- strong canonical design and proof harness exist
- not yet execution-promoted
Action:
- either complete implementation proof gates or keep it design-active without ambiguity

### Priority F: revenue-machine closure
Evidence:
- materially proven locally, but CSV/API ingest and full artifact chain remain incomplete
Action:
- either close those proof gaps or narrow the machine claim explicitly to the proven lane

## Phase 3: Canonical execution spine convergence
Target:
- one canonical execution spine
- one canonical truth layer
- one promotion law
- one recovery path

## Non-negotiable rules
- no new expansion before bottleneck removal
- no promotion without fresh proof
- no artifact presence treated as live capability
- no root repo sprawl accepted as normal
