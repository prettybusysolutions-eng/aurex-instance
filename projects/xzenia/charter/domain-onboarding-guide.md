# Domain Onboarding Guide
## Xzenia Generalized Domain Onboarding — Step-by-Step

**Version:** 1.0  
**System:** System 5 — Generalized Domain Onboarding Contract  
**Charter:** xzenia-7.5-to-9.0-charter  

---

## Overview

A *domain* in Xzenia is a bounded operational context — a specific problem space (e.g., revenue recovery, cleaning lead management) that the system analyzes, reasons about, and acts within. Onboarding a domain means declaring its contract so Xzenia's substrate can govern, validate, and report on it without any substrate modification.

This guide is domain-agnostic. Follow it for any new domain.

---

## Prerequisites

- Python 3.10+ in your `$PATH`
- Access to the Xzenia workspace: `/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/`
- Validator available at: `domains/validate_domain_contract.py`
- Onboarding script available at: `domains/onboard_domain.py`

---

## Step 1: Understand the Domain Contract Schema

The schema lives at:
```
charter/domain_contract_schema.json
```

A valid domain contract is a JSON file with **seven required top-level sections**:

| Section | Purpose |
|---|---|
| `identity` | Name, objective, core entities, success metrics |
| `causal` | Graph schema, required nodes/edges, evidence sources, confidence semantics |
| `verification` | Valid-state rules, regression rules, required tests |
| `connector` | Data sources, refresh expectations, normalization rules |
| `execution` | Internal actions, approval-required actions, rollback semantics |
| `reporting` | Operator summary format, machine output artifacts |
| `risk_surface` | Sensitive data, external write boundaries, guardrails |

All seven sections **must** be present. Missing any section will fail validation.

---

## Step 2: Author the Domain Contract

Create a file named `<domain-slug>.domain.json` inside:
```
domains/
```

### Template

```json
{
  "identity": {
    "name": "<domain-slug>",
    "objective": "<one sentence: what this domain does>",
    "core_entities": ["<entity1>", "<entity2>"],
    "success_metrics": ["<metric1>", "<metric2>"]
  },
  "causal": {
    "graph_schema": "<describe the causal graph structure>",
    "required_nodes": ["<node1>", "<node2>"],
    "required_edges": ["<edge1>", "<edge2>"],
    "evidence_sources": ["<source1>", "<source2>"],
    "confidence_semantics": "<how confidence is expressed in this domain>"
  },
  "verification": {
    "valid_state_rules": [
      "<artifact or state condition that must be true for domain to be healthy>"
    ],
    "regression_rules": [
      "<condition that indicates a regression has occurred>"
    ],
    "required_tests": ["<test1>", "<test2>"]
  },
  "connector": {
    "sources": ["<source-type1>", "<source-type2>"],
    "refresh_expectations": "<how often and under what conditions data refreshes>",
    "normalization_rules": "<how all sources get normalized into a unified model>"
  },
  "execution": {
    "internal_actions": ["<action1>", "<action2>"],
    "approval_required_actions": ["<external action requiring human approval>"],
    "rollback_semantics": "<how to undo domain actions>"
  },
  "reporting": {
    "operator_summary": "<what the human sees: key state, risks, recommended actions>",
    "machine_outputs": ["<artifact1>", "<artifact2>"]
  },
  "risk_surface": {
    "sensitive_data": ["<data type requiring protection>"],
    "external_write_boundaries": ["<what the domain must NOT write without approval>"],
    "guardrails": ["<hard constraint1>", "<hard constraint2>"]
  }
}
```

### Authoring Rules

1. **Be specific.** Vague placeholders will pass schema validation but fail operational review.
2. **Name your entities.** `core_entities` should match what appears in your causal graph nodes.
3. **Hard boundaries in `risk_surface`.** Every external write must appear in `external_write_boundaries` and have a guardrail. No exceptions.
4. **Approval gates in `execution`.** Anything that touches external state, sends communications, or modifies records outside the domain's local state must be in `approval_required_actions`.
5. **Machine outputs are verifiable.** Each entry in `reporting.machine_outputs` should correspond to a real artifact that the domain's execution produces.

---

## Step 3: Validate the Contract

Run the validator:

```bash
cd /Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia
python3 domains/validate_domain_contract.py domains/<your-domain>.domain.json
```

**Expected output (pass):**
```json
{
  "path": "domains/<your-domain>.domain.json",
  "missing": [],
  "valid": true
}
```

**If sections are missing**, the output will list them:
```json
{
  "path": "...",
  "missing": ["reporting", "risk_surface"],
  "valid": false
}
```

Fix each missing section and re-run until `"valid": true` and `"missing": []`.

---

## Step 4: Run the Onboarding Script

Once validation passes, run the onboarding script:

```bash
python3 domains/onboard_domain.py domains/<your-domain>.domain.json
```

The script will:
1. Validate the contract (re-runs the validator, refuses to proceed on failure)
2. Register the domain in `domains/domain-registry.json`
3. Emit an onboarding report to `csmr/reports/`

**Expected output:**
```
[onboard] Validating domains/<your-domain>.domain.json ...
[onboard] ✓ Validation passed — zero violations
[onboard] Registering domain '<your-domain>' in domain-registry.json ...
[onboard] ✓ Registered. Registry now contains N domain(s).
[onboard] Emitting onboarding report ...
[onboard] ✓ Report written to csmr/reports/onboarding-<your-domain>-<timestamp>.json
[onboard] DONE: <your-domain> successfully onboarded.
```

Exit code `0` = success. Any non-zero exit = failure (check output for details).

---

## Step 5: Verify the Registry Entry

```bash
cat domains/domain-registry.json
```

Your domain should appear as an entry with:
- `name` — the domain slug
- `path` — path to the `.domain.json` file
- `onboarded_at` — ISO timestamp
- `valid` — `true`
- `report` — path to the onboarding report

---

## Step 6: Verify the Onboarding Report

```bash
ls -lt csmr/reports/onboarding-<your-domain>-*.json | head -1
cat csmr/reports/onboarding-<your-domain>-<timestamp>.json
```

The report contains:
- Domain identity
- Validation result
- Registry registration confirmation
- All seven required sections (verified present)
- Timestamp

---

## What This Does NOT Require

The design principle of System 5 is that a new domain onboards using **only its contract file** and this guide. You should **never** need to:

- Modify any substrate Python files (`execution/`, `tier*/`, `supervisor/`, etc.)
- Alter the schema definition
- Change the validator
- Edit the registry manually
- Patch any configuration files

If you find yourself needing to do any of the above to onboard a domain, that is a substrate defect — file it as governed work.

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `valid: false` + missing sections | Contract file is incomplete | Add the missing top-level sections |
| JSON parse error | Malformed JSON | Validate JSON syntax (e.g., `python3 -m json.tool <file>`) |
| Domain already in registry | Re-running onboarding | Script will update the entry rather than duplicate it |
| Report directory not found | First run on a fresh workspace | The script creates `csmr/reports/` if needed |

---

## Reference: Both Verified Domains

| Domain | Contract File | Status |
|---|---|---|
| Revenue Recovery | `domains/revenue-recovery.domain.json` | ✓ Validated, registered |
| Pretty Busy Cleaning | `domains/pretty-busy-cleaning.domain.json` | ✓ Validated, registered |

Both domains onboarded with zero violations and zero substrate modifications.
