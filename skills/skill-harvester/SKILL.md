---
name: skill-harvester
description: Detect reusable patterns during real work and convert them into durable local skills, scripts, policies, or charters automatically. Use when repeated workflows, recurring failures, recurring repairs, integration lessons, or operational patterns should be captured so future sessions do not repeat the same discovery work.
---

# Skill Harvester

Harvest reusable capability from real execution.

## Core rules

- Do not create a skill for one-off trivia.
- Create a skill when a pattern repeats, a failure teaches a reusable lesson, or a workflow benefits from deterministic reuse.
- Prefer one strong skill over many tiny overlapping skills.
- Package the skill after creation.
- Persist the lesson into memory if it changes long-term operating behavior.

## Trigger criteria

Create or update a skill when any of these are true:

- the same workflow appears twice
- the same failure class appears twice
- a recovery pattern becomes reliable
- an integration boundary becomes clear and reusable
- a local operating rule should survive the session

## Workflow

1. Name the reusable pattern clearly.
2. Decide whether it belongs in a skill, script, policy file, or charter.
3. If it is skill-worthy, create/update a skill under `skills/`.
4. Add the minimum scripts/references needed.
5. Package it into `dist/`.
6. Update `MEMORY.md` if it changes standing operating posture.
7. Update the current daily memory note with what was harvested.

## Selection rule

Choose the smallest durable artifact that preserves the lesson:

- workflow instructions -> skill
- deterministic command path -> script
- stable routing/config rule -> policy JSON
- substrate-wide law -> charter/operating note

## References

- Read `references/harvest-criteria.md` when deciding whether a pattern is strong enough.

## Scripts

- `scripts/harvest-checklist.sh` — quick checklist for harvesting a reusable pattern.


## Canonical writeback rule
Do not only harvest reusable code or workflows. Also harvest durable governing lessons into canonical memory, law, or contract files when they materially change future operation.
