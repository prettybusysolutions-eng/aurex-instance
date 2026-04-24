# Monitor Job Spec

Last updated: 2026-04-13 21:55 EDT
Status: READY
Cadence: every 12 hours

## Purpose
Track early pull signals for platform magnet assets.

## Metrics
- runtime-doctor stars
- runtime-doctor forks
- residue-classifier stars
- residue-classifier forks
- ClawHub install signal if visible
- Stripe checkout completions
- issue-thread reply count changes

## Output
Append daily/periodic snapshots into `PERFORMANCE-TRACKER.md` or a future structured metrics file.

## Reporting rule
Surface first installation, first star, first fork, and first paid conversion immediately.
