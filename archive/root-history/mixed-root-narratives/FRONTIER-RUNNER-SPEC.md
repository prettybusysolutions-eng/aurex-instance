# Frontier Runner Spec

Last updated: 2026-04-13 17:15 EDT
Status: ACTIVE

## Objective
Create a canonical autonomous frontier runner that executes long multi-step work through checkpoints, proof hooks, and resumable state instead of chat-turn dependence.

## Required capabilities
- persistent run manifest
- ordered step queue
- per-tranche verification hooks
- checkpoint/resume
- stop only on real hard boundary
- explicit result state per step
