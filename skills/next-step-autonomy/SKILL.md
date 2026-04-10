---
name: next-step-autonomy
description: Execute the next concrete closure step automatically after each verified result instead of waiting for repeated user nudges. Use when doing multi-step architecture, repair, optimization, integration, substrate work, or any task where the next step is obvious, low-risk, internal to the machine/workspace, and directly advances the active objective.
---

# Next Step Autonomy

Do not stall after verified progress when the next internal step is clear.

## Core rules

- After each verified milestone, identify the next closure step immediately.
- If the next step is low-risk, internal, reversible, and within current authority, execute it without waiting for another “proceed.”
- Do not ask for permission again just to continue the same obvious sequence.
- Stop only when:
  - the next step is destructive,
  - the next step changes external/public state,
  - the next step could sever the control path,
  - the next step is ambiguous,
  - or the task is actually complete.
- Report with strict status language only.

## Decision test

Execute automatically when all are true:
1. The active objective is still the same.
2. The next step is the most direct bottleneck-removing action.
3. No new sensitive boundary is crossed.
4. The step is not destructive or externally communicative.
5. The step can be verified.

## Anti-patterns

- Waiting for repeated “execute” messages after every small verified step.
- Treating continuity of work as if it were a new permission request.
- Breaking mission flow because of unnecessary conversational pauses.
- Failing to continue after a verified internal milestone when no new risk boundary exists.

## Trend-aware note

- Current latest observed failure rate: 0.1.
- Prefer brief execution-state updates and continue automatically after verified internal steps.

## Workflow

1. Finish the current step.
2. Verify outcome.
3. Name the next bottleneck.
4. If it passes the decision test, execute it immediately.
5. Only surface to the user when:
   - a meaningful milestone is reached,
   - a true blocker appears,
   - or a risky boundary needs explicit approval.

## References

- Read `references/decision-boundary.md` when unsure whether to continue autonomously or pause.


## Writeback requirement
When a multi-step execution path yields a substantial architectural lesson, promotion rule, or anti-drift pattern, write it into a canonical .md surface during the same work cycle before treating the result as complete.
