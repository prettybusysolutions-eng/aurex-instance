# Routing Governance

## Canonical decision
`session.dmScope` is a governed routing decision, not an opportunistic continuity toggle.

### Current canonical policy
- `session.dmScope = per-channel-peer`

## Why
This system operates across Telegram direct chat and web/control surfaces.
Routing stability and reply correctness take precedence over convenience continuity.
Cross-surface continuity should be achieved through explicit identity linking and memory, not by collapsing DM routing into one shared main bucket.

## Governing rules
1. Model automation may not modify routing fields.
2. Routing changes require explicit governance artifact updates.
3. Session routing and delivery context are separate from model fallback logic.
4. Cross-surface continuity should use:
   - `session.identityLinks`
   - curated memory
   - explicit session governance
5. If reply bleed occurs, prefer isolation first, then selectively re-link identities.

## Protected fields
- `session.dmScope`
- `session.identityLinks`
- `session.sendPolicy`
- session delivery-context behavior by implication

## Allowed authorities
- operator-approved routing governance updates
- explicit repair scripts that target routing only

## Disallowed authorities
- model guardian
- budget automation
- generic config writers without field-level guards

## Drift response
If `session.dmScope` deviates from canonical policy:
1. log to `memory/errors.md`
2. restore governed value
3. inspect recent config writers before broader mutation
