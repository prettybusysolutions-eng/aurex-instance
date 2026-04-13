---
name: pattern-operations
description: >
  A constraint skill that prevents the agent from defaulting to physical/labor/muscular 
  business ideas (cleaning, delivery, manual work) and redirects to pattern-matching, 
  information, and cognitive work only. Use whenever proposing business ideas, revenue 
  models, or services.
---

# Pattern Operations

_A constraint skill ensuring all revenue ideas are pattern-matching, never physical labor._

## The Core Constraint

**I do not have a body.** I cannot clean, build, drive, deliver, or perform physical work.

Every time I propose a revenue idea, I must run it through this filter:

```
IF the idea involves:
  - Physical labor (cleaning, delivery, construction)
  - Human-body-dependent work (driving, cooking, serving)
  - Non-cognitive output (moving things, assembling products)
  
THEN → REJECT and re-route to pattern-matching alternatives
```

## Why This Exists

I consistently default to "physical service" ideas because:
- They're easy to conceptualize
- They feel concrete
- They map to familiar business patterns

But these are **value traps** — they ignore my actual capability.

## My Actual Capabilities

- **Pattern matching** — find signals in data humans miss
- **Information synthesis** — connect disparate sources into insight
- **Language operations** — generate, transform, summarize, interpret
- **Reasoning** — chain logic, identify gaps, derive conclusions
- **Automation** — trigger actions based on conditions

## The Only Valid Revenue Paths

| Valid (Pattern-Matching) | Invalid (Physical) |
|-------------------------|-------------------|
| Data analysis | Cleaning services |
| Document generation | Delivery logistics |
| Intelligence gathering | Cooking/food service |
| Research synthesis | Physical installation |
| Content creation | Field services |
| Business intelligence | Manual labor gigs |
| Quote/estimate generation (from data) | Handyman work |
| Monitoring + alerting | Transportation |

## Operational Rules

### 1. Default Rejection

Any business idea that requires a human body to execute is **automatically rejected**.

**Stop pattern:**
- "I'll build a cleaning business"
- "We'll do delivery"
- "Handyman services"
- "Moving company"

**Immediate pivot:**
- "What information does this produce?"
- "What pattern can I match instead?"

### 2. Information-First Frame

Every revenue idea must answer:
- **Input:** What information comes in?
- **Processing:** What patterns do I match?
- **Output:** What information/value comes out?

If you can't answer all three with pattern-matching operations, the idea is invalid.

### 3. The "So What?" Test

After proposing any idea, ask:
> "Am I doing physical work or pattern matching?"

If the answer is physical → re-route.

## Business Idea Template

All proposed business ideas must use this template:

```
PROPOSED IDEA: <name>

INPUT: <what information enters>
PROCESSING: <what patterns I match>
OUTPUT: <what information/value exits>

VALIDATION:
- Pattern matching? YES/NO
- Physical labor? YES/NO
- Scalable without body? YES/NO

DECISION: PROCEED / REJECT
```

## Examples

### Invalid (Rejected)

```
PROPOSED IDEA: Mobile car detailing
INPUT: Car location, condition
PROCESSING: (none - human washes car)
OUTPUT: Clean car
VALIDATION: Pattern matching? NO | Physical labor? YES | Scalable without body? NO
DECISION: REJECT
```

### Valid (Proceed)

```
PROPOSED IDEA: Used car condition intelligence
INPUT: Vehicle history, listing data, market comparables
PROCESSING: Anomaly detection, price pattern matching, condition scoring
OUTPUT: Detailed vehicle condition report with value assessment
VALIDATION: Pattern matching? YES | Physical labor? NO | Scalable without body? YES
DECISION: PROCEED
```

## Skill Integration

This skill is **mandatory** for any business/revenue discussion. Run it before proposing:
- Business ideas
- Revenue models
- Service offerings
- Product concepts

**Default behavior:** If no skill is specified, default to pattern-matching only.

## References

- Use `references/business-idea-validator.py` to validate proposals
