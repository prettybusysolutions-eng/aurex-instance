---
name: causal-operations
description: >
  Operationalize causal analysis at maximum performance. Automatically run causal queries, 
  attribute failures to root causes, trigger corrective proposals, and track outcomes. 
  Use when the system needs to move from passive causal logging to active causal remediation.
---

# Causal Operations

_A skill for operationalizing causal analysis — from passive logging to active remediation._

## The Core Capability

I have a causal ledger that tracks:
- Every failure event with timestamps
- Failure classification (root cause mapping)
- Component attribution
- Modification proposals and their outcomes

The gap: **I log failures but don't automatically act on them.**

This skill closes the loop: **detect → attribute → propose → fix → verify**

## Operational Workflow

### 1. Causal Query (Always Running)

Query the causal ledger every cycle for:
- Dominant failure patterns
- Rising trends in specific failure classes
- Component-specific degradation

```
python3 tier14/causal_query_api.py <failure_class|any> [limit]
```

### 2. Root Cause Attribution

For each dominant failure pattern:
- Map to suspected root cause (see ROOT_MAP in causal_query_api.py)
- Identify affected components
- Calculate confidence based on evidence count

### 3. Proposal Generation

If confidence > 0.7 and failure rate is rising:
- Generate a modification proposal via tier9
- Route through Gate A (automated validation)

### 4. Automated Fix Application

If proposal passes Gate A/B/C:
- Apply the fix
- Log the remediation
- Verify outcome in next cycle

### 5. Outcome Tracking

Track every remediation:
- Did it fix the failure?
- Did it cause regressions?
- What's the new failure rate?

## Root Cause Map

| failure_class | suspected_root_cause |
|--------------|---------------------|
| transport_conflict | duplicate_transport_owner |
| disk_full | storage_headroom_exhausted |
| timeout | slow_or_overweight_execution_path |
| schema_violation | proposal_generator_constraint_mismatch |
| simulation_regression | proposal_regresses_historical_baseline |
| causal_contradiction | proposal_increases_downstream_risk |
| command_error | component_execution_error |
| integrity_failure | substrate_integrity_degradation |
| cycle_failure | orchestration_cycle_breakage |
| unknown | unclassified_failure_pattern |

## Confidence Thresholds

| Confidence | Action |
|------------|--------|
| 0.0 - 0.4 | Log only, no action |
| 0.4 - 0.7 | Generate proposal, manual review |
| 0.7 - 0.9 | Auto-propose, auto-validate |
| 0.9+ | Auto-propose, auto-validate, auto-apply |

## Integration Points

- **tier14/causal_query_api.py**: Query dominant failures
- **tier2/drift_detector.py**: Detect rising failure trends
- **tier9/generate_trend_aware_proposal.py**: Create fix proposals
- **csmr/**: CSMR pipeline for proposal validation

## Operational Commands

```bash
# Query current dominant failure
python3 projects/xzenia/tier14/causal_query_api.py any 50

# Run full causal operation cycle
python3 projects/xzenia/tier7/unified_cycle.py

# Check drift
python3 projects/xzenia/tier2/drift_detector.py

# Generate trend-aware proposal
python3 projects/xzenia/tier9/generate_trend_aware_proposal.py
```

## Auto-Remediation Rules

1. **Never apply fix without validation** — Gate A must pass
2. **Always backup before apply** — rollback_bundle_index.py
3. **Monitor for regressions** — next cycle must show improvement
4. **Log every action** — to causal_events with metadata

## Anti-Patterns

- **Over-correction**: Don't fix every minor failure
- **Confidence inflation**: Don't trust high confidence without evidence
- **Silent failures**: If cycle fails, alert (unless test mode)
- **Orphaned proposals**: Clean up stale proposals after 7 days

## Continuous Operation

This skill should run on a schedule:
- Every 15 minutes: causal query + drift detection
- Every hour: full unified cycle
- Daily: trend analysis + proposal generation

Use cron or launchd to schedule:
- `com.xzenia.causal.query` — 15 min
- `com.xzenia.causal.cycle` — 60 min

## Output Artifacts

- `projects/xzenia/csmr/reports/causal-query-last.json` — last query result
- `projects/xzenia/csmr/reports/unified-cycle.json` — cycle output
- `projects/xzenia/csmr/reports/drift-report.json` — drift detection
