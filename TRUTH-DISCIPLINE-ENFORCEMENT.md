# Truth Discipline Enforcement

Last updated: 2026-04-13 16:49 EDT
Status: ACTIVE

## Rule
Every completion claim must map to one of:
- decided
- staged
- committed
- pushed
- verified

## Enforcement addition
When a tranche changes git state, verification is not optional. The final state must be checked with git status and/or git log before reporting terminal completion.

## Failure memory
Previous pressure caused completion-state slippage. This file exists so that slippage becomes a governed defect class, not a repeated behavior.
