# Skill: adversarial-review
**Purpose:** Auto-generate counter-arguments and error analysis for every leakage finding.
**Input:** Leakage finding + Audit Trail
**Output:** "Red Team" report with failure modes and disproof conditions.

## Logic
1. **Assumption Check:** What must be true for this finding to hold?
2. **Data Quality Check:** Is the source data complete? (e.g., missing logs?)
3. **Alternative Explanation:** Could this be a timing difference, not leakage?
4. **Disproof Condition:** What single piece of evidence would kill this finding?

## Output Format
```markdown
## Finding: $5,000 API Overage Leakage
**Confidence:** High (92%)
**Risk of Error:** Low
**Disproof Condition:** If API logs show <100k calls, finding is invalid.
**Counter-Argument:** "Maybe they reset counters mid-month?" -> Rejected: Logs show continuous count.
```