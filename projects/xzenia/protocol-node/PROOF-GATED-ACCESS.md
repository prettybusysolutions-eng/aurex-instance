# Proof Gated Access

Last updated: 2026-04-14 00:58 EDT
Status: READY

## Handshake path
- `POST /mcp/v1/handshake`

## Translate path
- `POST /mcp/v1/translate`
- requires header: `x-grant-token`

## Grant model
- successful proof issuance grants 60 seconds of access
- grant registry stored locally in `translate-grants.json`

## Replay protection
- `payment_intent_id` may not be reused
- billing ledger and grant registry are both checked before grant issuance

## 402 response behavior
If no valid grant is present, `/mcp/v1/translate` returns:
- HTTP 402
- JSON error payload
- `x-payment-link` header with the current Stripe payment link
- current public machine-gate price target: `$0.25`
