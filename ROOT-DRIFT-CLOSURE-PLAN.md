# Root Drift Closure Plan

Last updated: 2026-04-12 20:48 EDT
Status: ACTIVE

## Goal
Restore the root repo to a truly thin canonical-control repository.

## Required classes
- canonical authority
- promoted proof/report surfaces
- runtime/state/log/generated surfaces
- subproject-owned surfaces
- archive/reference surfaces

## Sequence
1. classify untracked root surfaces
2. identify canonical keepers
3. identify runtime/generated ignores
4. identify subproject boundaries
5. reduce exception sprawl in `.gitignore`
6. preserve only strategic control surfaces in root lifecycle

## Proof of closure
- root status becomes strategically legible
- no large runtime/generated bulk appears as accidental authority
