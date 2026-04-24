# Root Purity Policy

Generated: 2026-04-23
Status: ACTIVE

## Purpose
This policy hardens the workspace root as a thin sovereign control surface.
The root is for law, truth, continuity, and explicitly held active substrate.
It is not a transit zone for diagnostics, generated media, temp outputs, or one-off staging residue.

## Canonical baseline
The current accepted root baseline is:
- `reports/FINAL-THIN-ROOT-BASELINE-2026-04-23.json`

Verified counts at lock time:
- canonical: 19
- bootstrap: 11
- provisional: 27
- total root files: 57

## Root classes
Allowed root files must belong to exactly one of these classes:
1. canonical
2. bootstrap
3. provisional

If a root file is not in the accepted baseline and not explicitly promoted, it is drift.

## Root law
- The root is for law, not transit.
- New root files are violations unless they are explicitly classified.
- Historical residue belongs in `archive/root-history/`.
- Drift and cold generated exhaust belong in quarantine or archive namespaces, not in the root execution deck.

## 24-hour classification rule
Any newly created root file must be classified within 24 hours as one of:
- promoted canonical
- accepted bootstrap
- accepted provisional
- archive candidate
- drift intruder

If not classified within that window, it should be treated as drift and routed out of root.

## Enforcement rule
Before hardening decisions, compare the live root against the accepted baseline.
Any file absent from the baseline is a root violation until proven otherwise.

## Mutation rule
A root mutation is allowed only when:
1. it materially changes governing truth, continuity, or active commercial control
2. it cannot live more cleanly in a subtree
3. it is intentionally classified and recorded

## Operational stance
Prefer narrow enforcement over broad ignore fantasies.
The purpose is to preserve a truthful, usable root, not to silently hide the repo from itself.
