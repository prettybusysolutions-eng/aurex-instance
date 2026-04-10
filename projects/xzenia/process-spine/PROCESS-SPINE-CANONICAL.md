# Xzenia Process Spine - Canonical System

Last updated: 2026-04-09 22:16 EDT
Status: CANONICAL DESIGN ACTIVE

## Purpose
Create a hardened process orchestration layer that absorbs the strongest architectural ideas from external process-control systems while rejecting unsafe trust assumptions, bypassable gates, weak authentication, and ambiguous authority boundaries.

## Core doctrine
This system exists to make process execution:
- safer
- more observable
- more resumable
- more governable
- more truthful
- more composable with the verified Xzenia substrate

## What is being extracted
The useful architecture patterns are:
1. process lifecycle orchestration
2. reattachable process sessions
3. explicit stdout/stderr/stdin streaming protocol
4. process and container identity surfaces
5. control plane separated from execution plane
6. memory / timeout / OOM governance
7. resumable state and operator visibility
8. trace/event emission as first-class outputs

## What is explicitly rejected
The replacement layer forbids:
1. any no-auth or weak-auth acceptance mode
2. patchable branch-gate trust boundaries
3. local-network trust as an authority primitive
4. ambiguous container/process identity semantics
5. direct privilege by connection locality
6. execution control without explicit policy and audit
7. hidden fallback that silently lowers security posture

## Canonical architecture

### 1. Control plane
Responsible for:
- authenticated session establishment
- issuance of execution intents
- operator approvals
- process lookup and reattachment
- lifecycle commands
- checkpoint registry
- run proofs

### 2. Execution plane
Responsible for:
- spawning governed processes
- binding process resource policies
- streaming stdout/stderr/stdin
- timeout handling
- memory and OOM enforcement
- structured termination and cleanup

### 3. Identity plane
Responsible for:
- process identity
- execution envelope identity
- worker identity
- environment identity
- authority scope
- signed provenance on every control action

### 4. Proof plane
Responsible for:
- execution trace artifacts
- health proofs
- checkpoint proofs
- contradiction detection
- promotion eligibility
- failure classification

## Security inversion rules
Unsafe source assumptions are inverted as follows:

### Auth inversion
Unsafe: accept unsigned/unchecked auth in degraded or missing-key mode
Safe replacement:
- no execution session without verified auth
- key absence is hard-fail, not soft-accept
- degraded mode reduces capability, never security

### Network inversion
Unsafe: infer trust from locality, host CID, or local IP properties
Safe replacement:
- trust derives from signed authority and policy only
- connection origin is telemetry, not authorization
- local transport does not bypass auth or policy

### Identity inversion
Unsafe: loose expected-container-name checks as partial identity guard
Safe replacement:
- execution envelope has signed identity
- worker validates envelope identity, authority scope, and freshness
- mismatches fail closed and emit audit events

### Process-control inversion
Unsafe: direct process creation after shallow handshake
Safe replacement:
- process creation requires a validated execution intent
- intent binds command class, resource class, runtime scope, and audit lineage
- command execution is policy-mediated, not socket-mediated alone

### Fallback inversion
Unsafe: hidden or permissive fallback when primary controls unavailable
Safe replacement:
- fallback may reduce features, not trust requirements
- fallback status must be explicit in proofs and operator views
- no silent downgrade

## Process Spine protocol

### Session establish
1. client presents signed execution intent request
2. control plane verifies authority, policy scope, freshness, and replay safety
3. control plane issues short-lived signed execution envelope
4. execution plane validates envelope before any process action

### Create process
Envelope must bind:
- process_id
- run_id
- allowed command class
- uid/gid policy
- environment policy
- timeout
- memory class
- trace mode
- reattachability
- provenance signature

### Stream lifecycle
- stdout channel explicit
- stderr channel explicit
- stdin capability explicit and revocable
- flow control visible to operator plane
- trace events sidebanded, not mixed ambiguously with control payloads

### Reattach
- only allowed if envelope policy permits
- requires signed reattach token tied to prior run lineage
- active attachment exclusivity enforced by policy, not best effort

### Termination
- normal exit, timeout, OOM, killed, policy-aborted are distinct terminal classes
- all terminal classes produce proof artifacts

## Binding to Xzenia substrate

### Canonical dependencies
- platform-spine for work governance and operator control
- unified supervisor for live system truth
- adversarial integrity layer for verification
- checkpoint / continuity layer for resumable execution
- activation registry for promotion truth

### Canonical outputs
- execution proof artifact
- resource outcome artifact
- contradiction artifact when policy/runtime diverge
- reattachment state artifact
- operator summary artifact

## Promotion rules
The Process Spine is not promoted beyond design-active until it has:
1. protocol schema
2. execution envelope schema
3. signed intent validation path
4. local execution proof
5. reattach proof
6. timeout and OOM proof
7. adversarial verification proof

## Immediate build sequence
1. define schemas and authority envelopes
2. define control-plane API contract
3. define execution-plane worker contract
4. bind to platform-spine work governance
5. generate first local proof harness
6. adversarially test trust failures and downgrade behavior

## Strategic role
This is not a side project.
This is the canonical future process-control layer for Xzenia when execution must be governed, resumable, observable, and promotion-safe.
