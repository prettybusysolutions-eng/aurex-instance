# Continuity Guard Specification

## Objective
Eliminate "No response generated" errors by engineering around them before they reach the user.

## Core Mechanisms

### 1. Heartbeat Protocol (Prevention)
- **Rule:** No silent generation longer than 15 seconds without a state checkpoint.
- **Action:** For long responses, emit intermediate "keep-alive" markers or break into atomic chunks.
- **Infrastructure:** Enforce stricter client-side retry logic on stream stalls.

### 2. Checkpointed Generation (Recovery)
- **Rule:** Long outputs are segmented into atomic blocks (Identity, Architecture, Analysis, Plan).
- **Action:** Each block is saved to `state/latest-checkpoint.json` before generation begins.
- **Recovery:** If generation fails mid-stream, the next session reads the checkpoint and resumes from the last completed block, not from scratch.

### 3. Redundant State Mirroring (The Black Box)
- **Rule:** The chat interface is volatile; the filesystem is truth.
- **Action:** Critical context (current task, last completed step, pending output) is written to disk *before* execution.
- **Result:** Even if the session dies completely, continuity is restored instantly on restart.

### 4. Chunked Output Protocol
- **Threshold:** Any response > 1000 tokens is automatically chunked.
- **Format:**
  - Chunk 1: Context/Identity
  - Chunk 2: Core Analysis
  - Chunk 3: Action Plan
- **Benefit:** If Chunk 3 fails, Chunks 1-2 are already delivered and saved.

## Implementation Status
- [x] Specification defined
- [x] `continuity-guard.py` deployed — `projects/xzenia/scripts/continuity-guard.py`
- [x] `token_budget_guard.py` deployed — `projects/xzenia/execution/token_budget_guard.py`
- [x] `session-boot.py` deployed — `projects/xzenia/scripts/session-boot.py`
- [x] `NEXT-ACTION.md` generated at workspace root each session
- [x] `HEARTBEAT.md` updated with boot protocol
- [x] First test run completed — 2026-03-23

## Unified Wire (end-to-end flow)
1. Session starts → `session-boot.py` runs → reads checkpoint + queue + charter + intent graph
2. `NEXT-ACTION.md` written to workspace root with next action surfaced
3. Any long generation → `token_budget_guard.py evaluate <chars>` → chunk if needed
4. Each work unit → `checkpoint_contract.py pre` before, `post` after
5. On interruption → next session-boot reads last checkpoint and resumes cleanly

## Governing Principle
**We do not wait for crashes. We engineer around them.**