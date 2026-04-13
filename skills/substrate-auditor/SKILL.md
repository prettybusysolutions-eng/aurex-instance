---
name: substrate-auditor
description: Freeze drift-prone execution surfaces and restore robust end-to-end substrate integrity by auditing registry↔executor completeness, rerunning core proof artifacts, and classifying capabilities into proven/provisional/failed/stale. Use when the system is materially advanced but patch drift, mapping mismatch, or proof inconsistency may have accumulated.
---

# Substrate Auditor

Use this skill when the substrate is real but messy.

## Purpose
Turn "advanced but uneven" into "clean, robust, and explicitly classified."

## Core law
Do not expand capability while the execution spine is ambiguous.
Audit first. Repair second. Re-verify third. Then classify truth.

## What to check
1. registry → executor completeness
2. active scripts compile
3. supervisor still passes
4. degradation still reports coherently
5. adversarial suite still passes
6. cost artifacts still generate
7. frontier generation / autonomous continuation still work

## Required outputs
- audit report
- capability ledger
- repaired execution surfaces
- updated checkpoint naming the clean floor

## Promotion rule
A substrate is only considered robust after:
- registry items map to actual executor functions
- core scripts compile cleanly
- proof bundle passes after repair
- capability claims are classified explicitly
