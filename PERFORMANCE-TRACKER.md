# Performance Tracker

Last updated: 2026-04-14 00:47 EDT
Status: ACTIVE
Window: 12-hour monitoring cadence

## Repos
- runtime-doctor: https://github.com/prettybusysolutions-eng/runtime-doctor
  - stars: 0
  - forks: 0
  - watchers: 0
- residue-classifier: https://github.com/prettybusysolutions-eng/residue-classifier
  - stars: 0
  - forks: 0
  - watchers: 0

## ClawHub
- runtime-doctor published: yes
- version: 0.1.0
- search visibility: yes
- watch for installs as the primary top-of-funnel signal

## Revenue rails
- human revenue path: `/stripe/webhook`
- machine handshake path: `/.well-known/mcp` and `/mcp/v1/*`
- Runtime Doctor Pro: https://buy.stripe.com/4gM28q7W0agjbg4bkG0kE06
- Residue Classifier Pro: https://buy.stripe.com/7sY00idgkcoresgbkG0kE07

## Ghost monitoring
Watch for first non-human machine signals:
- requests to `/.well-known/mcp`
- requests to `/mcp/v1/health`
- requests to `/mcp/v1/capabilities`
- requests to `/mcp/v1/translate`
- any future handshake/payment headers on machine paths

## Billing ledger readiness
- ledger exists: yes
- current verifier summary: `debug_rows=0`, `real_rows=1`
- current real row is the retained golden-path proof event
- ledger is structurally ready for human Stripe events today
- machine handshake monetization remains scaffolded, not live-settled

## Live node verification baseline — 2026-04-14 00:47 EDT
- cloudflared target `127.0.0.1:8788`: confirmed
- `/.well-known/mcp`: 200 OK
- `/mcp/v1/health`: 200 OK
- thermal watch cadence artifact: present
- 12-hour monitoring cadence: active by policy

## Launch of Sovereign Node — 2026-04-14 02:08 EDT
- `/mcp/v1/translate` returned strict `402 Payment Required`
- header confirmed: `x-x402-mode: live`
- header confirmed: `x-x402-fee: 0.01`, later rebased in code/env toward `0.25`
- Stripe payment link header present
- settlement mode is now live-gated at the HTTP layer

## Price rebase check — 2026-04-14 02:32 EDT
- attempted machine-gate rebase target: `$0.25`
- verified Stripe Payment Link blocker: minimum total due must be at least `$0.50 USD`
- current public Stripe link is not a valid quarter-dollar machine gate link
- elasticity observation remains pending until a valid public gate price surface is chosen

## Machine gate rebase resolved — 2026-04-14 02:42 EDT
- public machine-gate price rebased to `$0.50`
- verified Stripe product: `prod_UKg27vnEq2Q8bg`
- verified Stripe price: `price_1TM0gHAc6hzX3Jk1mmxCxA3S`
- verified machine-gate payment link: `https://buy.stripe.com/fZuaEWa48ewz4RGewS0kE08`
- `$19.00` human product link is no longer the machine-gate surface

## Live-settle alert rule
Break silence immediately if:
- a valid machine handshake proof produces a grant token
- `private/machine-settlement-ledger.jsonl` receives a `CONSUMED` Stripe intent row
- first real external hit lands on `/mcp/v1/handshake`

## Reporting rule
Track stars, forks, ClawHub installs, machine pings, payment-link intent, paid checkouts, and handshake bounce rate (`402 returned` vs `handshake initiated`) as primary signals.
Break silence immediately for real payment events or first meaningful machine-origin traffic.
