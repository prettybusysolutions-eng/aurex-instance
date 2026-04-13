# Tracked Dirt Resolution

Last updated: 2026-04-13 15:14 EDT
Status: ACTIVE

## `memory/errors.md`
Decision: keep local operational ledger, do not promote by default.
Reason: this is valuable operational residue but not canonical truth authority.

## `projects/xzenia/state/resume-queue.json`
Decision: keep tracked for now as canonical continuity state.
Reason: current continuity/execution surfaces still reference it.
Future: demote only when continuity contract is rewritten to a more durable promoted state surface.

## Result
Tracked dirt is resolved in meaning, even if the files still remain modified locally.
