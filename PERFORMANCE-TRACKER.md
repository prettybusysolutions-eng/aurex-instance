# Performance Tracker

Last updated: 2026-04-13 22:23 EDT
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

## Revenue links
- Runtime Doctor Pro: https://buy.stripe.com/4gM28q7W0agjbg4bkG0kE06
- Residue Classifier Pro: https://buy.stripe.com/7sY00idgkcoresgbkG0kE07

## Billing ledger policy
- keep `evt_test_tunnel_1` as golden-path proof
- all future mock/test events should be tagged `debug: true`
- separate debug/test events from real revenue analytics

## Click-tracking design
Track intent separately from completed payments:
- ClawHub installs
- repo stars
- repo forks
- repo watchers
- Stripe payment link clicks if surfaced by Stripe analytics
- Stripe checkout completions
- paid conversion count

## Formal baseline snapshot — 2026-04-13 22:23 EDT
- runtime-doctor stars: 0
- runtime-doctor forks: 0
- runtime-doctor watchers: 0
- residue-classifier stars: 0
- residue-classifier forks: 0
- residue-classifier watchers: 0
- ClawHub runtime-doctor search visibility: confirmed
- docs/index.md outbound links: verified 200
- Stripe checkout completions logged in tracker: 0
- paid conversions logged in tracker: 0

## Reporting rule
Track stars, forks, ClawHub installs, payment-link intent, and paid checkouts as primary early signals.
No further community posting without operator review.
