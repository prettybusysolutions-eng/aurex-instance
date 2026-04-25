# Billing Fulfillment Trace - 2026-04-23

## Fresh artifact
- `reports/billing-fulfillment-trace-2026-04-23.json`

## Verdict
- `fulfillment_gap_confirmed`

## What the Python listener really does
File:
- `private/billing_listener.py`

The listener does **not** deliver a real product.
It maps `metadata.product_key` to hardcoded placeholder URLs:
- `runtime_doctor_pro` -> `https://example.com/private/runtime-doctor-pro`
- `residue_classifier_pro` -> `https://example.com/private/residue-classifier-pro`
- `utilities_pro_bundle` -> `https://example.com/private/utilities-pro-bundle`

Grant behavior is currently:
- if `payment_status == paid`
- and `amount_total >= 200`
- and `metadata.product_key` matches a key in `DOWNLOADS`
- then write a ledger row with a `grant_url`

But that `grant_url` is only a placeholder string.
It is not a secure delivery mechanism, not a time-bound link, and not a cryptographic entitlement token.

## Response truth
The listener returns:
- `{"ok": true, "granted": boolean}`

But this is only acknowledging that a placeholder URL was selected.
It is not proof of real fulfillment.

## Ledger truth
File:
- `private/billing-ledger.jsonl`

Current properties:
- write mode: raw append via `LEDGER.open('a')`
- atomicity: not proven
- access-control role: not proven
- current observed content: one placeholder test row with an `example.com` grant URL

## What reads the ledger
### `projects/xzenia/protocol-node/ledger_verify.py`
- only counts debug vs real rows
- this is audit/summary behavior, not delivery control

### `projects/xzenia/protocol-node/stripe_agentic_adapter.py`
- uses ledger presence as replay/proof signal for payment intent tracking
- it does **not** turn the ledger into a real fulfillment authority for delivered products

## Conclusion
The billing listener is not a production fulfillment layer.
It is a placeholder proof scaffold.
The paid loop can record a payment-shaped event, but it cannot yet deliver a real software entitlement or a real protected download outcome.

## Correct next move
Patch `private/billing_listener.py` so successful paid events produce a real delivery artifact or entitlement path instead of `example.com` placeholders.
Until that is done, the revenue machine should not be described as a production-grade paid-delivery loop.
