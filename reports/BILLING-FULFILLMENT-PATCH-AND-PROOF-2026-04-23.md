# Billing Fulfillment Patch and Proof - 2026-04-23

## Status
PATCHED_AND_LOCALLY_PROVEN

## Warehouse stocking
A protected local asset directory now exists:
- `private/assets/`

Assets staged:
- `Sovereign_RevOps_Kit.zip`
- `Privacy_Migration_Kit.zip`
- `Home_Lab_Master_Kit.zip`
- `review_bundle.zip`
- `sovereign-diagnostic-engine-kit.zip`

Permissions applied:
- directory: `700`
- assets: `600`

## Listener patch
`private/billing_listener.py` was upgraded from placeholder URL selection into a local tokenized fulfillment service.

### New behavior
- product keys map to real local assets under `private/assets/`
- successful paid events mint a cryptographically secure token via `secrets.token_urlsafe(32)`
- token records are written to `private/billing-ledger.jsonl`
- listener now serves `GET /download/<token>`
- tokens are time-bound
- tokens are single-use and are marked consumed after successful download

## Local proof
### Mock signed payment
A locally signed mock Stripe-style event for:
- `product_key = revops_kit_core`
- `amount_total = 500`

returned:
- `granted: true`
- a real token
- a real local download URL

### Download proof
Fetching the minted URL returned:
- HTTP `200`
- `Content-Type: application/zip`
- `Content-Disposition: attachment; filename="Sovereign_RevOps_Kit.zip"`
- bytes served: `13206`

### Single-use proof
A second fetch of the same token returned:
- HTTP `403`
- `{"ok": false, "error": "token_consumed"}`

## Ledger proof
`private/billing-ledger.jsonl` now records:
- billing event row
- download token row
- token consumed row

## Remaining truth
- ledger writes are currently append-locked with in-process threading lock, not cross-process file locking
- legacy placeholder test row remains in the ledger from pre-patch behavior
- full live Stripe external round-trip is still separate from this local proof

## Verdict
The static-package fulfillment layer is no longer placeholder-only.
It is now materially capable of local protected asset delivery with token minting, expiry, and single-use consumption.
