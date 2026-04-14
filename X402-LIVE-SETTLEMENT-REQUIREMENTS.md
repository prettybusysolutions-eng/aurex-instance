# x402 Live Settlement Requirements

Last updated: 2026-04-14 00:51 EDT
Status: READY

## Current env keys observed
- `BILLING_LISTENER_PORT`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

## Missing keys for real x402-style live settlement cutover
These are not currently present in `private/.env` and are the practical switch prerequisites:
- `X402_MODE=live`
- `X402_HANDSHAKE_FEE_USDC=0.01`
- `X402_SETTLEMENT_PROVIDER=coinbase` or equivalent chosen rail
- settlement verification secret / API key for the chosen x402 rail
- wallet / destination identifier for USDC settlement
- receipt/signature secret for machine-verifiable payment proofs

## Stripe/Coinbase reality
Stripe keys alone are not sufficient to claim live x402 settlement.
Current Stripe setup supports human checkout/payment-link flows.
Machine handshake settlement needs an additional settlement verification adapter and receipt logic.

## Practical cutover switch
The direct middleware mode switch is:
- `X402_MODE=dry-run` -> `X402_MODE=live`

But that switch should only be flipped after the missing settlement credentials and verification adapter are implemented and tested.
