---
name: governed-substrate-cycle
description: Convert architecture intent into governed substrate execution by enforcing one canonical cycle: checkpointed work envelopes, defect-to-work conversion, queue/registry synchronization, supervisor truth, degradation awareness, storage governance, and verification-gated promotion. Use when hardening a local autonomous runtime from promising architecture into an operable, recoverable, self-governing substrate.
---

# Governed Substrate Cycle

Use this when the machine has multiple partial autonomy mechanisms and needs to become one governed runtime.

## Core law

Do not treat architecture as progress.
Only count verified substrate changes that survive checkpoint, recovery, and rerun.

## What this skill is for

Apply this skill when you need to:
- collapse split intent planes (registry vs resume queue vs checkpoint vs executor)
- convert defects into governed work
- route all work through one gateway/checkpoint contract
- make supervisor truth authoritative
- expose degradation explicitly
- turn storage pressure into governed reclaim policy
- promote domain onboarding from bespoke logic into a reusable contract

## Canonical order

1. **Checkpoint truth**
   - preserve semantic checkpoint fields
   - never clobber `resumeInstruction`, `nextFrontier`, or artifacts

2. **Unify intent planes**
   - sync bottleneck registry into resume queue
   - rebuild intent graph from synced state
   - ensure recovery reads the same frontier as execution

3. **Close defect loop**
   - defect detector
   - classifier
   - registry writer
   - closure verifier
   - dedupe/reopen/escalation
   - executor-origin rerun closure where possible

4. **Canonicalize execution**
   - wrap work in work envelope
   - pre/post checkpoint contract
   - gateway execution path
   - route autonomous cycle through the gateway

5. **Make supervision independent**
   - supervisor health report must run independently of executor
   - detect contradictions between registry, queue, checkpoint, and storage state

6. **Expose degradation honestly**
   - resource monitor selects tier
   - degradation gate emits confidence and preserved-intent mode
   - do not pretend full capability under pressure

7. **Govern storage structurally**
   - classify reclaim candidates by safety and class
   - emit reclaim contract
   - feed remaining storage contradictions into supervisor

8. **Onboard domains contractually**
   - define shared domain contract schema
   - validate at least two domains under one contract
   - prefer transferability over bespoke vertical logic

## Required artifacts

- checkpoint artifact
- bottleneck registry
- synced resume queue
- defect reports
- supervisor health report
- degradation report
- storage governance report
- domain onboarding report

## Promotion rule

A system phase is not done until:
- it executes through the canonical gateway
- its artifact exists on disk
- rerun does not contradict prior state

## Practical warnings

- If disk pressure is severe, reduce write-heavy activity before broadening scope.
- If registry and queue disagree, fix that before trusting supervisor claims.
- If a gateway run succeeds but artifact/state lags, reconcile directly and persist the truth.
- Remove only high-confidence duplicate/cache residue unless explicitly authorized for deeper deletion.

## Outputs to preserve

When this skill produces a stable pattern, preserve it in:
- `projects/xzenia/state/latest-checkpoint.json`
- current daily memory file
- the relevant runtime scripts/artifacts themselves

## Execution note

- `scripts/refresh-governed-cycle.sh` is a shell script and must be invoked with `bash` or executed directly after `chmod +x`; do not run it with `python3`.
