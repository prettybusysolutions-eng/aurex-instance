# Skill: audit-trail
**Purpose:** Generate immutable audit trails for every leakage finding.
**Input:** Leakage finding (JSON)
**Output:** AuditTrail JSON with source mapping, confidence scores, and verification steps.

## Usage
```bash
node skills/audit-trail/run.js --finding <finding.json> --output <trail.json>
```

## Schema
```json
{
  "finding_id": "string",
  "source_documents": ["invoice_id", "contract_clause", "usage_log"],
  "calculation_trace": ["step1", "step2"],
  "confidence_score": 0.95,
  "verification_hash": "sha256"
}
```