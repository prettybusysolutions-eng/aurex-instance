---
name: causal-engine
description: Build and run causal revenue analysis for Xzenia using graph-based structure, anomaly attribution, treatment-effect estimation, and counterfactual framing. Use when analyzing revenue leakage causes, preparing causal findings, or generating model artifacts from client financial data.
---

# Causal Engine

Use graph-structured revenue analysis to estimate likely causes of leakage.

## Rules
- Distinguish causal claims from heuristics.
- Prefer `scripts/run_causal.sh` so the dedicated causal environment is used when present.
- Report confidence and uncertainty.
- Refutation/validation is mandatory before high-confidence claims.
- If data is insufficient, say so.
