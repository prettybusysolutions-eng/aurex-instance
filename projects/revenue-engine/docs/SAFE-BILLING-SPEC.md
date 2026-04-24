# Safe Billing Spec

Last updated: 2026-04-13 18:39 EDT
Status: READY

## Objective
Monitor successful $2.00+ payments for Pro upgrades without exposing Stripe secrets in public repos, local logs, or user-facing artifacts.

## Security rules
- never write the Stripe secret key into repository files
- never print the Stripe secret key in stdout/stderr
- never store the Stripe secret key in README, SKILL.md, or public config
- use environment variables or an approved secret manager only
- redact webhook payloads before logging if they contain sensitive customer data

## Minimal architecture
1. local/private billing listener
2. Stripe secret key injected only through environment variable
3. webhook endpoint verifies Stripe signature
4. listener stores only minimal event metadata:
   - event id
   - payment status
   - amount
   - product label
   - timestamp
5. trigger internal state update only when payment amount >= 200 cents

## Allowed outputs
- `payment_detected: true/false`
- amount in cents
- product label
- event timestamp
- internal upgrade flag or ledger row id

## Forbidden outputs
- secret key
- full raw card/customer payload
- webhook signature secret
- full unredacted event dumps in public logs

## Idempotency
- deduplicate on Stripe event id
- if the webhook is retried, do not create duplicate upgrade activations
- all ledger writes must be idempotent by event id

## Logging posture
- private local logs only
- redact customer email if not required
- no public repo logging of billing events

## Promotion boundary
Billing listener remains private/local until separately audited and approved.
