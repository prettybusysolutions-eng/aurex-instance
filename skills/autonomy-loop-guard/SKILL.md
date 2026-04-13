---
name: autonomy-loop-guard
description: Detect and break unproductive autonomous loops during long-running or multi-step agent work. Use when an agent is polling, retrying, repeating the same tool pattern, stalling without progress, or needs checkpointing/escalation rules for autonomous processes, watchdog flows, coding runs, or orchestration tasks.
---

# Autonomy Loop Guard

Prevent fake progress.

## Core rule

If actions repeat without new evidence, new artifacts, or a changed state, treat it as a loop and break it.

## Use this workflow

1. Define the target state.
2. Define observable progress signals.
3. Check whether each cycle changed anything real.
4. If not, reduce repetition, checkpoint state, and change strategy.
5. Escalate to the user when autonomy is no longer buying progress.

## Progress signals

Count progress only when at least one of these changed:

- a file was created or materially updated
- a process changed state
- a test result changed
- a diagnosis gained new evidence
- a manifest, ledger, or memory checkpoint was written
- a blocker was removed

Do not count these as progress by themselves:

- re-reading the same file without a new question
- re-running the same status check on a tight loop
- repeating the same explanation
- retrying with no parameter change
- checking a session/process list over and over

## Loop triggers

Assume a loop is forming when any of these happen:

- the same tool pattern repeats 3 times with no state change
- polling continues without a timeout or exit condition
- the plan is unchanged but outputs are identical or near-identical
- the agent keeps “thinking about checking” instead of changing strategy
- retries happen without modifying inputs, timing, permissions, or environment

## Break actions

When a loop is detected, do one or more of the following:

- checkpoint current state to a file
- widen the wait interval or stop polling
- inspect the underlying artifact directly instead of asking for another status summary
- switch tools
- simplify the task into a smaller verified step
- spawn a focused sub-process only if it reduces ambiguity
- ask the user a sharp blocking question if external intent is missing

## Checkpointing

Persist autonomy state for resumability.

Minimum checkpoint fields:

- objective
- current step
- last meaningful change
- repeated actions detected
- blocker
- next planned change
- escalation threshold reached: true/false

Use `scripts/check_autonomy_loop.py` to score repeated actions from a JSON state file or stdin.

## Exit conditions

Stop autonomous execution and report when:

- the objective is complete
- the remaining path requires user judgment or approval
- the process is stalled and no strategy shift looks better than user input
- safety constraints block the next action

## Reference

Read `references/loop-patterns.md` when you need concrete anti-loop heuristics and escalation patterns.
