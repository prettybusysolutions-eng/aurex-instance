# Ledger Purity and Provisional Routing - 2026-04-23

## Fresh artifacts
- `reports/billing-ledger-sanitization-2026-04-23.json`
- `reports/provisional-root-final-routing-map-2026-04-23.json`

## Ledger purity result
The legacy placeholder grant row was removed from the production ledger and quarantined instead of deleted.

### Production ledger now contains only:
- the real local proof billing event
- the minted download token row
- the token consumed row

### Quarantine archive now contains:
- the legacy `example.com` placeholder grant row
- path: `private/ledger-archive-tests.jsonl`

This restores the production ledger to truthful fulfillment-only state while preserving historical evidence of the scaffold phase.

## Final provisional routing map
The remaining 27 provisional root files now have a physical routing map.
No files were moved in this step.

### Route targets
- `projects/revenue-engine/docs/`
- `projects/verifiagent/offer-surfaces/`
- `projects/xzenia/control-residue/`
- `storefront/`

## Meaning
The revenue machine is now materially real in the runtime layers:
- ingress hardened
- state writes hardened
- fulfillment hardened
- production ledger purified

What remains at root is now primarily documentation, outer-layer commercial collateral, and control-adjacent residue that can be routed physically without confusing it for the live commercial engine.

## Correct next move
Execute the physical movement of the 27 provisional root files according to the locked routing map, using the same batch-and-verify protocol used in the earlier root thinning tranches.
