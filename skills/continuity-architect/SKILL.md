---
name: continuity-architect
description: Design and maintain restart-survivable continuity: checkpoints, resume queues, recovery playbooks, wake/boot resumption, and local persistence independent of remote session memory.
---

# Continuity Architect

Continuity is a local systems problem.

## Core rules
- No essential state should live only in remote session context.
- Every major operation should be resumable.
- Recovery must prefer local artifacts over transcript assumptions.
- Sleep/restart should degrade into resume, not amnesia.

## Outputs
- checkpoint schemas
- resume queue logic
- recovery playbooks
- wake/boot recovery hooks
- reconciliation scripts
