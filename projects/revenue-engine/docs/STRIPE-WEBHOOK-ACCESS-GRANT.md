# Stripe Webhook Access Grant

Last updated: 2026-04-13 19:30 EDT
Status: READY

## Objective
Automatically grant access to Pro utilities after successful Stripe payment without exposing secrets or leaking customer data.

## Flow
1. customer pays through Stripe Payment Link
2. Stripe sends webhook to a private billing listener
3. billing listener verifies webhook signature
4. listener deduplicates event by Stripe event id
5. listener checks payment status and purchased product
6. listener writes a private access ledger entry
7. listener grants access through one of these safe methods:
   - signed download link
   - private repo invite/manual fulfillment queue
   - email delivery of private package link

## Access grant rules
- only successful paid events trigger grant
- only products mapped to Pro utilities trigger grant
- duplicate webhook events do not create duplicate access
- failed or incomplete payments do not trigger grant

## Required private secrets
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`

## Recommended private injection paths
- local `.env` file outside public repos
- 1Password secret injection
- approved local secret manager

## Public repo rule
No Stripe secrets, webhook payload dumps, or billing logic with embedded secrets enter the public repositories.
