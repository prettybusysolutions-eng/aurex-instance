# Guarded Skill Publication Pipeline

Last updated: 2026-04-14 00:05 EDT
Status: READY

## Goal
Create a deterministic pipeline for packaging and proposing new fix-skills based on verified API failure trends.

## Stages
1. detect recurring verified failure
2. classify fixability and public safety
3. generate skill/package scaffold
4. run local verification
5. require approval gate before external publish

## Policy
Verified 404/500 findings may auto-generate draft artifacts, but external publication still requires explicit approval.

## Outputs
- draft skill package
- validation report
- publish recommendation
