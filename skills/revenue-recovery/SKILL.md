---
name: revenue-recovery
description: Core revenue recovery orchestration for Xzenia. Use when onboarding a client, running end-to-end revenue leakage analysis, coordinating data ingestion, contract parsing, causal analysis, recovery planning, executive reporting, or checking client recovery status.
---

# Revenue Recovery

Coordinate these local skills:
- `contract-parser`
- `financial-telemetry`
- `causal-engine`
- `recovery-actions`
- `executive-briefing`

## Workflow
1. Create client workspace in `workspace/data/xzenia/clients/<client_id>/`
2. Load or write `client_config.json`
3. Ingest source data
4. Parse contracts
5. Run causal analysis
6. Generate recovery plan
7. Generate executive briefing
8. Persist outputs and summarize findings

## Orchestration scripts
- `scripts/onboard-client.sh <client_id> [client_name] [arr] [billing_system] [billing_model]`
- `scripts/run-client-cycle.sh <client_id> [csv_file]`

These provide the current subsystem entrypoints for onboarding and full-cycle execution.

## Governing texts
This skill operates under the following bound artifacts, in precedence order:
1. `projects/xzenia/docs/co-architecture-directive.md`
2. `projects/xzenia/docs/operational-reliability-charter.md`
3. `projects/xzenia/docs/the-third-scroll.md`
4. `projects/xzenia/docs/the-scroll.md`
5. `projects/xzenia/state/trust-expansion-rubric.md`
6. `projects/xzenia/state/self-audit-ledger.md`

## Rules
- Never fabricate findings.
- Report data gaps explicitly.
- Do not execute external billing/customer actions without approval.
- Prefer durable artifacts over persuasive language.
- Treat external validation as optional; treat evidence as mandatory.
- Proceed automatically on safe local next steps; pause only at genuine risk boundaries.
- Founder vector outranks local optimization.
