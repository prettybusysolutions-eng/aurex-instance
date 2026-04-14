# Stripe Handshake Auto-Verify Research

Last updated: 2026-04-14 01:48 EDT
Status: PARTIAL - READY FOR IMPLEMENTATION DESIGN

## Can Stripe Payment Intents auto-verify machine handshakes?
Yes, partially, but not by secret key alone.

A practical Stripe-based machine-verification flow would require:
- a machine request to create or reference a Stripe Payment Intent
- a server-side verification step using `STRIPE_SECRET_KEY`
- checking the Payment Intent status is actually succeeded / capturable per the chosen model
- binding that verified intent to a one-time handshake proof
- replay protection so the same Payment Intent cannot mint multiple grants

## What the current system still lacks
- code that calls Stripe's Payment Intent API for verification
- a verified mapping from `payment_intent_id` to the machine handshake proof
- signed proof semantics or server-issued receipt semantics
- explicit handling for pending / requires_action / failed / canceled states
- policy for minimum amount check at $0.01 equivalent

## Honest switch boundary
`STRIPE_SECRET_KEY` is enough to query and verify Stripe objects.
It is not enough by itself to claim machine-handshake auto-settlement is already active.

## Safe next implementation step
Build a verification adapter that:
1. accepts `payment_intent_id`
2. fetches the intent from Stripe server-side
3. verifies amount, currency, and succeeded state
4. marks the intent consumed in the replay registry
5. issues the 60-second translate grant exactly once
