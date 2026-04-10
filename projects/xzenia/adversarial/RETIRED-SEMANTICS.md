# RETIRED SEMANTICS

Last updated: 2026-04-09 21:59 EDT

## Retired contradiction semantics
- queue-checkpoint-only contradiction assumptions

## Reason
The canonical supervisor contract no longer treats checkpoint frontier drift alone as a contradiction.
Current live contradiction semantics are registry↔pending-queue mismatch, storage pressure signals, and stalled in-progress registry items.

## Consequence
Legacy probes that only validate queue↔checkpoint contradiction logic are retired until explicitly rewritten to validate the canonical supervisor contract.
