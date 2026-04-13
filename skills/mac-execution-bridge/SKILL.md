---
name: mac-execution-bridge
description: Perceive and control the local Mac UI through screenshots, OCR-friendly capture, app/window focus, mouse/keyboard primitives, and verification checkpoints. Use when a task requires local desktop execution, browser/app navigation, window targeting, or resumable GUI workflows without relying on external browser-control tools.
---

# Mac Execution Bridge

Use the Mac as a local execution surface.

## Core loop

1. Capture current UI state.
2. Focus the target app/window.
3. Perform the smallest precise action.
4. Verify state changed.
5. Checkpoint the result.
6. Repeat only with new evidence.

## Required scripts

- `scripts/capture-screen.sh` — capture the current display or a target window to a file
- `scripts/window-state.sh` — list foreground apps/windows and active browser tab info when available
- `scripts/ui-action.sh` — activate apps, click coordinates, type text, press keys, and open URLs
- `scripts/check-ui-loop.py` — detect repeated unchanged UI actions

## Rules

- Prefer app focus and URL navigation before coordinate clicking.
- Verify every action with a fresh capture or window-state read.
- If coordinates are used, store them in a manifest rather than improvising repeatedly.
- If 3 unchanged cycles occur, stop and checkpoint.
- Use `references/execution-patterns.md` for capture/act/verify patterns.

## Output types

Prefer creating or updating:

- UI control manifests
- UI session state files
- execution checkpoints
- action ledgers
- app/window targeting notes
