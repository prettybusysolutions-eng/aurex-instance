# Revenue Webhook and Write Integrity - 2026-04-23

## Status
PARTIAL_RUNTIME_PROOF_PLUS_CODE_HARDENING

## Negative check proof
A local negative POST to `http://127.0.0.1:8787/api/sync/webhooks` without Stripe webhook configuration returned a fail-closed response:
- HTTP status: `503`
- body: `{"ok":false,"error":"stripe_webhook_not_configured"}`

This proves the patched route no longer blindly accepts and mutates on arbitrary JSON when webhook security is not configured.

## Webhook integrity hardening
`revenue-copilot/server/index.mjs` now includes:
- raw-body handling for `/api/sync/webhooks`
- environment-backed `STRIPE_WEBHOOK_SECRET`
- Stripe SDK webhook signature construction
- fail-fast responses for:
  - missing webhook config
  - missing signature
  - invalid signature

## Write integrity hardening
Atomic JSON write discipline was added for revenue runtime state surfaces.

### Added function
- `atomicWriteJson(targetPath, payload)`
- implementation: write to `targetPath.tmp` then `renameSync` into place

### Applied to
- `revenue-copilot/ops/runtime/state.json`
  - initial seed path in `readState()`
  - all later persistence through `saveState()`
- `revenue-copilot/ops/runtime/machine-auth.json`
  - webhook-issued machine auth registry writes now go through `writeMachineAuthRegistry()` using atomic replacement

## Remaining truth
- The negative runtime check proved fail-closed behavior under missing config.
- A full live signed Stripe webhook round-trip was not executed in this patch cycle.
- Atomic replacement reduces partial-write corruption risk, but no cross-process lock was added yet.

## Current verdict
The highest-priority revenue ingestion integrity gaps are materially narrowed:
1. forged unauthenticated webhook mutation path patched in code
2. partial-write corruption risk for `state.json` and `machine-auth.json` reduced via atomic replacement

## Correct next move
Kill the temporary local server used for the negative check, then continue revenue-machine closure on the now-hardened ingestion/state layer.
