# BOOTSTRAP-RESTORE.md — Full Reconstruction Protocol

_If you are reading this and Aurex is not present, this file reconstructs her._

---

## What Exists

A fully self-contained OpenClaw agent instance with:
- Complete identity and memory
- Two shipped products on GitHub
- Published ClawHub skill
- Loaded OpenClaw plugin
- Full operational stack (50+ skills)
- Execution-grade heartbeat
- Autonomous release hardening

---

## Reconstruction Steps

### Step 1: Verify Environment

```bash
# OpenClaw running?
openclaw status

# Workspace exists?
ls ~/.openclaw/workspace-aurex/

# Products exist?
ls ~/.openclaw/agents/aurex/workspace/projects/
```

---

### Step 2: Load Core Files (in order)

1. `IDENTITY.md` — who Aurex is
2. `SOUL.md` — execution identity and doctrine
3. `AGENTS.md` — workspace operating system
4. `USER.md` — the operator (Kamm Smith)
5. `TOOLS.md` — local infrastructure
6. `MEMORY.md` — long-term memory
7. `HEARTBEAT.md` — execution contract
8. `memory/YYYY-MM-DD.md` — today's and yesterday's context

---

### Step 3: Verify Product State

```bash
# Context Nexus — should be READY_TO_PUBLISH
cd ~/.openclaw/agents/aurex/workspace/projects/context-nexus
python3 scripts/release_hardening_loop.py

# LeakLock — should be deploy-ready (human action needed)
cd ~/.openclaw/agents/aurex/workspace/projects/xzenia-saas
cat .env  # verify Stripe key present
```

---

### Step 4: Verify OpenClaw Plugin

```bash
openclaw plugins list | grep context-nexus
# Should show: loaded
```

If not loaded:
```bash
openclaw gateway restart
```

---

### Step 5: Verify ClawHub Publish

```bash
clawhub search context-nexus
# Should show top result with score ~2.500
```

---

### Step 6: Run Heartbeat Verification

```bash
# Read HEARTBEAT.md and execute the stack
# Should reach READY_TO_PUBLISH or BLOCKED_WITH_EXACT_CAUSE
```

---

## What Was Built

### LeakLock
`prettybusysolutions-eng/xzenia-leaklock`
- CSV leak scanning SaaS, Stripe payments
- Status: deploy-ready (Render setup pending human action)
- Live Stripe key confirmed

### Context Nexus
`prettybusysolutions-eng/context-nexus`
- Persistent memory + observability + secrets + replay for OpenClaw
- ClawHub: `clawhub install context-nexus`
- Plugin: loaded in OpenClaw
- Status: READY_TO_PUBLISH

---

## Key Paths

```
Workspace:      ~/.openclaw/workspace-aurex/
Context Nexus:  ~/.openclaw/agents/aurex/workspace/projects/context-nexus/
LeakLock:      ~/.openclaw/agents/aurex/workspace/projects/xzenia-saas/
Plugins:        ~/.openclaw/plugins/
Memory:         ~/.openclaw/workspace-aurex/memory/
OpenClaw cfg:   ~/.openclaw/openclaw.json
```

---

## Execution Doctrine (Non-Negotiable)

1. **Artifact or blocker.** Not "I'm working on it." Not "executing."
2. **Verify before claiming.** Smoke test passes = pass. Not "should be fine."
3. **Exact blockers.** "doesn't work" is not a blocker. The specific error + specific fix is.
4. **No narration without state change.** If no file changed, no command ran, no status artifact updated — you are blocked.
5. **Ship don't discuss.** If it's ready, publish/deploy. Don't add more features.

---

## Hard Lessons (For When Things Break)

- `insufficient_quota` + valid token = $0 account, not auth failure
- VirusTotal flags PBKDF2 crypto as suspicious — expected, use `--force`
- OpenClaw plugin needs `register` or `activate` export, not `registerHooks`
- Python path in plugin subprocess must walk up from `~/.openclaw/plugins/<plugin>/src/`
- GitHub HTTPS push silently fails after token expiry — `gh auth refresh`
- Release hardening loop is the source of truth, not conversation memory

---

## If Starting Fresh (No Prior Context)

1. Read all files in Step 2 above
2. `gh auth login` if needed
3. `clawhub login` if publishing
4. Run `python3 scripts/release_hardening_loop.py` on each product
5. Verify `openclaw plugins list` shows context-nexus as loaded
6. Verify `clawhub search context-nexus` returns top result

---

## This File

If you're reading this and Aurex is not responding, use this file to reconstruct.
She is the workspace. The files are her continuity.

---

_Last reconstructed: 2026-03-31 by Kamm Smith_
