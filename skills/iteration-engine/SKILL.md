---
name: iteration-engine
description: >
  Enable the agent to iteratively improve its own outputs, self-review, identify gaps, 
  and converge on better solutions through controlled self-correction cycles. Use when 
  building, debugging, refining code, configs, or any work product where multiple passes 
  yield better results than a single shot.
---

# Iteration Engine

_A skill for agents to iteratively improve their own work — self-review, gap identification, convergence, and knowing when to stop._

## Why This Skill Exists

Most agents are one-shot: they generate and done. But the best outputs come from iteration — reviewing, refining, catching what was missed the first time.

This skill gives the agent a structured way to:
1. **Review** its own output against criteria
2. **Identify** what's weak, missing, or wrong
3. **Improve** with targeted fixes
4. **Validate** the improvement worked
5. **Decide** when to stop (diminishing returns)

## Core Philosophy

- **Iteration is not failure** — it's refinement
- **Self-criticism is required** — don't just generate, *review*
- **Converge, don't loop** — each pass should move toward a goal
- **Know the stop condition** — infinite iteration is worse than good-enough

## When to Use

- Writing code that needs multiple passes to be correct
- Debugging where first attempts don't fully fix the issue
- Refining configurations where trade-offs need balancing
- Any deliverable where "good enough" vs "better" matters

## When NOT to Use

- Simple, one-shot tasks where iteration adds no value
- Time-critical responses where the first answer suffices
- Already-optimal outputs (don't refine what's already correct)

## Workflow

### 1. Generate Initial Output

Create the first version. Don't spend excessive time perfecting — iteration will handle refinement.

### 2. Self-Review Against Criteria

Before declaring done, run a review pass:
- Does this meet the stated requirements?
- What edge cases were missed?
- What would a reviewer flag?
- What assumptions were made that might be wrong?

### 3. Identify Gaps

For each gap found:
- **Severity**: critical / important / nice-to-have
- **Fixability**: easy / moderate / requires redesign
- **Scope**: local fix or affects multiple areas

### 4. Apply Targeted Improvements

Fix identified gaps. Prioritize:
1. Critical issues
2. Important gaps
3. Nice-to-have improvements

### 5. Validate Improvement

After each fix:
- Does the fix actually address the gap?
- Did it introduce new issues?
- Does the overall output still meet requirements?

### 6. Check Stop Condition

Stop iterating when:
- All critical issues addressed
- No important gaps remain (nice-to-have can be deferred)
- Additional passes would yield diminishing returns
- Time/budget for iteration is exhausted

## Iteration State

Track iteration state to avoid infinite loops:

```
iteration_state = {
  "iteration": 0,
  "max_iterations": 5,
  "critical_issues_remaining": [],
  "important_issues_remaining": [],
  "changes_made": [],
  "last_change_impact": "positive|negative|mixed",
  "stop_reason": null
}
```

### Iteration Limits

- **Max iterations**: 5 by default, configurable per task
- **Per-iteration budget**: tokens, time, or passes
- **Early stop**: if iteration makes things worse

## Output Quality Checklist

For each iteration, verify:

- [ ] Requirements met
- [ ] No syntax errors / validation failures
- [ ] Edge cases considered
- [ ] Error handling present
- [ ] No hardcoded secrets or unsafe patterns
- [ ] Tests pass (if tests exist)
- [ ] Documentation updated (if applicable)

## Integration with Other Skills

- **skill-creator**: Use iteration to refine skill definitions
- **meta-healing**: Iterate on config improvements
- **governed-mutation-engineer**: Iterate on proposal refinement
- **creation-engine**: Iterate on scaffold generation

## Examples

### Code Iteration Example

```
Iteration 1: Initial code written
  Review: Missing null checks, no error handling
  Gap: Critical - null pointer possible on line 42
  Fix: Add null checks
  
Iteration 2: After null checks
  Review: Error handling added, but no logging
  Gap: Important - errors silently swallowed
  Fix: Add structured logging
  
Iteration 3: After logging
  Review: Edge case - what if service unavailable?
  Gap: Important - no retry logic
  Fix: Add exponential backoff retry
  
Iteration 4: After retry
  Review: All critical/important addressed
  Stop: Additional passes yield diminishing returns
```

### Config Iteration Example

```
Iteration 1: Initial config
  Review: Compaction policy set, but streaming behavior unclear
  Gap: Important - need explicit streaming mode
  Fix: Set streaming: "off"
  
Iteration 2: After streaming config
  Review: All configs validated
  Stop: Config now meets requirements
```

## Anti-Patterns to Avoid

1. **Infinite iteration**: Keep a max-iteration limit
2. **Scope creep**: Don't add features beyond original requirements
3. **Perfectionism**: Don't iterate on trivial improvements ad infinitum
4. **Ignoring time budget**: Know when "good enough" is actually enough
5. **Not tracking changes**: Keep a log to understand what improved

## References

- Use `references/iteration-log-template.md` to track iteration history
- Use `scripts/evaluate-improvement.sh` to validate changes


## Anti-avoidance iteration rule
Iterations should refine toward a bounded executable solution, not become a subtle escape from execution when a safe architectural path is available.
