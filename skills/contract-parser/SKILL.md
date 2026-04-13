---
name: contract-parser
description: Parse contracts, MSAs, SOWs, and amendments into structured billing terms for Xzenia. Use when extracting pricing, escalation, renewal, discount, overage, SLA, milestone, or payment terms from uploaded client contracts.
---

# Contract Parser

Extract revenue-relevant terms into structured outputs for downstream analysis.

## Output targets
- contract graph JSON
- structured term rows for SQLite insertion
- low-confidence term review list

## Rules
- Record source locations.
- Do not infer absent terms.
- Flag contradictions and amendments.
