# Node Webhook Integrity Patch - 2026-04-23

## Status
PATCHED_IN_CODE

## Target
- `revenue-copilot/server/index.mjs`
- route: `/api/sync/webhooks`

## What changed
1. Added Stripe SDK import in the server file.
2. Added environment-backed webhook secret handling:
   - `STRIPE_WEBHOOK_SECRET`
3. Added webhook Stripe client initialization using `STRIPE_SECRET_KEY`.
4. Changed the webhook route to use:
   - `express.raw({ type: 'application/json', limit: '2mb' })`
5. Added explicit signature checks:
   - reject when `stripe-signature` header is missing
   - reject when Stripe SDK webhook construction fails
6. Enforced reject-before-mutation behavior:
   - no registry or state mutation occurs until `constructEvent(...)` succeeds

## Verified code evidence
- `import Stripe from 'stripe';`
- `const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET || null;`
- `app.post('/api/sync/webhooks', express.raw({ type: 'application/json', limit: '2mb' }), ... )`
- `stripeWebhookClient.webhooks.constructEvent(req.body, sig, STRIPE_WEBHOOK_SECRET)`
- failure responses:
  - `stripe_webhook_not_configured`
  - `missing_stripe_signature`
  - `invalid_stripe_signature`

## Security effect
This closes the previously proven integrity gap where the Node webhook route consumed parsed JSON directly and could accept forged payloads without proven Stripe authenticity.

## Remaining truth
- This patch hardens authenticity at ingress.
- File locking and atomic-write hardening for `machine-auth.json` and `state.json` still remain future work.
- Live end-to-end webhook validation against a real signed Stripe payload is not yet proven in this patch cycle.

## Current verdict
The highest-priority Node webhook integrity gap is closed at the code level.
