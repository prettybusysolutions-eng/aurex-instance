# Xzenia Build Charter Control Surface

This directory is the executable control layer for the 7.5 -> 9.0 hardening program.

## Canonical artifacts
- `build-charter.json` — master machine-readable charter
- `graphs/dependency-graph.json` — dependency order
- `queues/weekly-work-queue.json` — verification-gated weekly queue
- `checklists/system-*.md` — promotion gates
- `*_schema.json` — initial system contracts

## Operating rule
Do not treat the charter as prose. Treat it as governed execution state.

## Promotion rule
No system promotes until its verification checklist is satisfied with direct evidence.

## Next move
Start with System 1: Closed Defect Loop.
