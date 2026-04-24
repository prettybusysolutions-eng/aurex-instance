# Resume Queue Demotion Plan

Last updated: 2026-04-13 16:33 EDT
Status: ACTIVE

## Current truth
`projects/xzenia/state/resume-queue.json` is still treated as temporary canonical continuity state.

## Problem
It is runtime-bearing and not ideal as a permanent root-tracked truth surface.

## Replacement path
1. preserve current use until continuity contract replacement exists
2. define a promoted continuity manifest with bounded fields
3. route runtime queue detail to local-only state
4. demote `resume-queue.json` once replacement is referenced by canonical docs/scripts

## Closure condition
A new promoted continuity state contract exists and `resume-queue.json` is no longer needed as tracked canonical truth.

## Current status
Replacement contract now exists at `projects/xzenia/state/continuity-contract.json`.
Pending final demotion decision after canonical references align.
