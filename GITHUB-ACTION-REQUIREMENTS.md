# GitHub Action Requirements

Last updated: 2026-04-13 21:12 EDT
Status: READY

## Required files
- `action.yml`
- entrypoint script or composite steps
- README with usage example

## Best fit for Runtime Doctor
Package as a lightweight diagnostic action that runs a workspace/runtime audit and emits a report artifact.

## Core inputs
- workspace path
- output path
- optional mode or rule pack

## Core outputs
- report path
- summary classification

## Constraint
Keep the GitHub Action non-destructive and CI-safe.
