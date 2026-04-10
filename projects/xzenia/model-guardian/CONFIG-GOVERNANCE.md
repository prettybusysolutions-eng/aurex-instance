# Model Guardian Config Governance

## Purpose
Prevent local automation from rewriting unrelated OpenClaw config while still allowing safe model switching.

## Allowed mutation surface
Model guardian may modify only:
- `meta.lastTouchedAt`
- `agents.defaults.model.primary`
- `agents.defaults.model.fallbacks`

## Forbidden mutation surface
Model guardian must not modify:
- `session.*`
- `channels.*`
- `bindings`
- `approvals`
- `plugins`
- `gateway`
- any identity/routing/security fields

## Operational rule
If a model automation needs broader config control, it must emit a proposal instead of patching `openclaw.json` directly.

## Drift lesson
Routing continuity and model fallback must be governed by separate authorities. A model switcher is not a routing authority.
