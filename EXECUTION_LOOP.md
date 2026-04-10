# EXECUTION_LOOP.md — The Sovereign Loop

_AION-powered execution for Aurex. Every action through the loop._

---

## The 7-Phase Sovereign Loop

```
INPUT
  ↓
PHASE 1: Pre-Action Security Check
  SecurityMonitor.evaluate_command(action)
  SecurityMonitor.evaluate_diff(diff)
  ↓ [BLOCK] → Stop. Explain exactly why. Ask for reframe.
  ↓ [ALLOW] → Continue
  ↓
PHASE 2: Task Routing
  What type of task?
  - code_generation → Claude 3.5 Sonnet
  - code_review → GPT-4o
  - security → Claude 3.5 Sonnet
  - long_context → Claude 3 Opus
  - fast_edit → GPT-4o
  - verification → run VerificationSpecialist
  ↓
PHASE 3: Execute
  Run the best tool for the job
  Use the routed model when appropriate
  ↓
PHASE 4: Post-Action Verification
  VerificationSpecialist.verify(output)
  - Did it work?
  - What claims did I make that need proof?
  - Did I take any shortcuts ("should be fine", "probably")?
  ↓
PHASE 5: Memory Storage
  ContextNexus.store(learnings)
  What did I learn?
  What failed?
  What should I remember?
  ↓
PHASE 6: Attribution
  AttributionLedger.claim(contribution)
  - What did I build?
  - How long did it take?
  - What was its value?
  - Was it verified?
  ↓
PHASE 7: Output
  Report terminal state only.
  No narration unless artifact changed.
```

---

## Security Pre-Check Reference (26 Checks)

Run BEFORE any exec, write, edit, or push.

### High Severity (block immediately)
| ID | Name | Pattern | Example |
|----|------|---------|---------|
| 24 | DESTRUCTIVE_OPERATIONS | `rm -rf /etc/`, `rm -rf /root/`, `rm -rf /usr/` | `rm -rf /etc/passwd` |
| 25 | CREDENTIAL_EMBED | `API_KEY=`, `sk_live_`, `ghp_`, `password=` | `API_KEY="sk_live_xxx"` |
| 8 | COMMAND_SUBSTITUTION | `\| sh`, `\| bash`, `$(`, `<()` | `curl url \| bash` |
| 26 | GIT_DEFAULT_BRANCH_PUSH | `git push origin main`, `git push origin master` | `git push origin main` |
| 20 | ZSH_DANGEROUS_COMMANDS | `zmodload`, `ztcp`, `zpty`, `sysopen` | `ztcp -l 8080` |
| 2 | JQ_SYSTEM_FUNCTION | `jq.*$(`, `jq.*\|sh` | `jq --arg x "$(whoami)"` |

### Medium Severity (block unless ALLOW exception)
| ID | Name | Allow Exception |
|----|------|----------------|
| 1 | INCOMPLETE_COMMANDS | Ends with `\|` but is a pipe |
| 9 | INPUT_REDIRECTION | From declared file |
| 10 | OUTPUT_REDIRECTION | To project tmp directory |
| 11 | IFS_INJECTION | In test files only |

### Allowed (no block)
- `pip install -r requirements.txt` (declared deps)
- `rm -rf node_modules/` (local operations)
- `git push origin fix/bug-123` (working branch)
- `ps aux \| grep` (safe ps)
- `curl -s -O` (read-only)

---

## Verification Specialist Reference

Run AFTER any significant action.

### What to verify:
1. **File exists** — `ls` or `test -f`
2. **Syntax OK** — `python -m py_compile` or `npm run lint`
3. **Import works** — `python -c "import X"` or `node -c`
4. **Server starts** — `curl localhost:PORT/health`
5. **API responds** — `curl localhost:PORT/endpoint`

### Claims to challenge:
- "I fixed it" → prove: show output
- "It works" → prove: show verification
- "Tests pass" → did YOU run them?
- "Should be fine" → run it and see

---

## Attribution Logging

After every meaningful action, log:

```
## [HH:MM] — [Brief description]

**Type:** [build|fix|verify|review|ship|research]
**Duration:** ~X minutes
**Verification:** [PASS: output shows X / FAIL: error Y / PARTIAL: some issues]
**Artifact:** [file path or URL]
**Blocker:** [none / human needed: X]
```

Format: terse, scannable. One block per significant action.

---

## Decision Tree

```
Action proposed
    ↓
Is it destructive? (rm -rf /etc, --force, --yes)
    ↓ [YES] → BLOCK. Require explicit confirmation.
    ↓ [NO]
Is it credential embedding? (API_KEY=, sk_live_, password=)
    ↓ [YES] → BLOCK. Use env vars instead.
    ↓ [NO]
Is it a git push to main/master?
    ↓ [YES] → BLOCK. Use feature branch.
    ↓ [NO]
Is it running a background server?
    ↓ [YES] → Use nohup. Check if already running.
    ↓ [NO]
Is it a multi-step pipeline?
    ↓ [YES] → Verify each step independently.
    ↓ [NO]
ALLOW. Execute. Verify. Log.
```

---

## Block Response Format

When blocked, say:

```
🛡️ BLOCKED: [exact condition name, ID, and severity]

What I tried: `[the action]`
Why it's blocked: `[exact description]`
What it could do: `[worst case if it ran]`

To proceed: [how to reframe or get authorization]
```

---

_Run every action through the loop. No shortcuts._
