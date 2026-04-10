# Root Repository Policy

Last updated: 2026-04-10 09:42 EDT
Status: ACTIVE

## Policy
The workspace root repository is a thin canonical-control repository.
It tracks only high-authority governance, memory, truth, and promotion surfaces.

## It should track
- identity and operator-alignment files
- canonical truth and activation files
- governing spine files
- selected promoted reports and canonical contract artifacts

## It should not track
- large generated substrate trees
- runtime state
- logs
- caches
- backups
- embedded subprojects with their own repo lifecycle
- experimental/generated media and data

## Reason
This keeps the root repo coherent, pushable, and strategically legible instead of becoming an indiscriminate dump of the entire substrate.
