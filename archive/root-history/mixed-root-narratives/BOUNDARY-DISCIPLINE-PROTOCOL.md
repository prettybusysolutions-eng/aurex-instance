# Boundary Discipline Protocol

Last updated: 2026-04-13 16:43 EDT
Status: ACTIVE

## Mandatory completion states
- DECIDED
- STAGED
- COMMITTED
- PUSHED
- VERIFIED

## Rule
Never report a later state when only an earlier state exists.

## Reporting contract
- decided only: decision artifact exists
- staged only: index contains the intended change
- committed only: local git object exists
- pushed only: remote advanced
- verified only: status/log/output proves the claim

## Failure rule
If reporting collapses these states, it is a truth error, not a style issue.
