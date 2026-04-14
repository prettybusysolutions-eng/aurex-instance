# Machine Gate Price Rebasing

Last updated: 2026-04-14 02:32 EDT
Status: BLOCKED ON STRIPE MINIMUM

## Intended rebase
- machine-gate fee target: `$0.25`
- public-facing sub-$0.25 entry points: remove

## Verified blocker
Stripe Payment Link creation for `$0.25` failed with:
- `The Checkout Session's total amount due must add up to at least $0.50 usd`

This means a standalone Stripe Payment Link cannot currently be used for a `$0.25` public machine gate.

## Current truth
- HTTP fee header can be rebased to `0.25`
- but public Stripe checkout cannot honestly be switched to `$0.25` unless the charge path changes
- current linked Runtime Doctor Pro payment link is a `$19.00` SKU and is not valid for the machine gate price surface

## Safe next options
1. Raise machine gate public minimum to `$0.50`
2. Use a non-Payment-Link Stripe API flow with a valid minimum-compliant capture model
3. Keep `$0.25` as internal logical fee while public settlement waits for a different rail
