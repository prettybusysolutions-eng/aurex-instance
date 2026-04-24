# Tranche Verification Protocol

Last updated: 2026-04-13 17:30 EDT
Status: ACTIVE

## Rule
Every git-impacting tranche must terminate with a proof bundle:
1. `git status --short`
2. `git log --oneline -n 1`
3. explicit classification of state as decided/staged/committed/pushed/verified

## Failure policy
A tranche without this proof bundle is incomplete.
