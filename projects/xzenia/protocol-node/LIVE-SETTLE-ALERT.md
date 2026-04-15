# Live Settle Alert

Last updated: 2026-04-14 02:08 EDT
Status: ACTIVE

## Trigger conditions
- first successful machine handshake at `/mcp/v1/handshake`
- first 60-second grant issuance
- first `CONSUMED` row written to `private/machine-settlement-ledger.jsonl`

## Notify rule
Break silence immediately and report:
- payment_intent_id
- amount
- currency
- grant token issued or not

## Urgent interrupt activation
On first `CONSUMED` row:
- append an immediate high-priority line to `projects/xzenia/protocol-node/ledger-watch.log`
- treat the event as a system-wide alert condition
- break silence in chat on the first observed settlement

## Thermal holding
Keep 15-minute thermal watch active while live settlement gating is enabled.
