# model-guardian

Autonomous model-budget monitor, coherent fallback switcher, and task-aware model router for OpenClaw.

Three capabilities in one:
1. **Budget guardian** — watches API usage, switches primary before exhaustion, restores at reset
2. **Task router** — maps work types to optimal models given what's active and budget state
3. **Activation tracker** — knows which latent providers exist, what each is good for, and exactly how to activate them

## Architecture

```
guardian_cycle.py        ← runs every 5 min via LaunchAgent
  └── budget_tracker.py  ← reads token usage from gateway log/completions/subagents
  └── model_switcher.py  ← patches openclaw.json primary coherently (atomic + backup)

task_router.py           ← on-demand: given task type or message text, return best model
model_registry.json      ← full provider catalog: active, inactive, strengths, tasks, how-to-activate
```

## Switch ladder (budget-driven)

```
1. anthropic/claude-sonnet-4-6   primary — full capability
2. openai-codex/gpt-5.4          external fallback — strong coding
3. ollama/qwen2.5:7b             local — first free fallback
4. ollama/qwen2.5:3b             local
5. ollama/llama3.2:3b            local
6. ollama/qwen2.5:1.5b-instruct  local minimal
```

| Budget used | Action |
|---|---|
| < 70% | Hold |
| 70–84% | Warn, log |
| 85–94% | Step down one rung |
| 95%+ | Emergency local-only |
| New day | Restore original primary |

## Task routing

Route any task to the optimal active model:

```bash
# By task type
python3 task_router.py --task coding
python3 task_router.py --task analysis --budget-pct 88

# By message text (infers task automatically)
python3 task_router.py --text "review this pull request for security issues"

# Available task types
python3 task_router.py --list-tasks
```

Task types: `coding`, `code-review`, `architecture`, `complex-reasoning`, `analysis`,
`vision`, `fast-classification`, `heartbeat`, `background-tasks`, `private-data`, `budget-fallback`

## Latent model activation plan

5 high-priority inactive providers that should be activated:

| Priority | Model | Why | Command |
|---|---|---|---|
| 1 | `google/gemini-3-flash-preview` | Free tier, 1M context, fast | `openclaw onboard --auth-choice gemini-api-key` |
| 2 | `openrouter/*` | Single key → 100+ models | `set OPENROUTER_API_KEY` |
| 3 | `moonshot/kimi-k2.5` | 200K context, agentic coding | `set MOONSHOT_API_KEY` |
| 4 | `huggingface/deepseek-ai/DeepSeek-R1` | Free, deep reasoning/math | `openclaw onboard --auth-choice huggingface-api-key` |
| 5 | `mistral/mistral-large-latest` | EU privacy, multilingual | `openclaw onboard --auth-choice mistral-api-key` |

Full plan: `python3 task_router.py --activate-plan`

## Files

All under `workspace/projects/xzenia/model-guardian/`:

- `policy.json`          — thresholds + budget config
- `model_registry.json`  — full provider catalog (active/inactive/tasks/how-to-activate)
- `budget_tracker.py`    — reads token usage
- `model_switcher.py`    — patches openclaw.json safely
- `guardian_cycle.py`    — 5-min decision cycle
- `task_router.py`       — task-to-model routing
- `install_launchagent.py` — LaunchAgent install/uninstall
- `state.json`           — current guardian state
- `guardian.log`         — cycle log
- `config-backups/`      — timestamped config backups

## Quick commands

```bash
cd workspace/projects/xzenia/model-guardian

# Status
python3 model_switcher.py --status
python3 task_router.py --status

# Check budget now
python3 budget_tracker.py

# Run one guardian cycle
python3 guardian_cycle.py

# See activation plan for latent providers
python3 task_router.py --activate-plan

# Force switch / restore
python3 model_switcher.py --to ollama/qwen2.5:7b --reason "test"
python3 model_switcher.py --restore

# LaunchAgent
python3 install_launchagent.py status
```

## Notes

- Gateway hot-reloads on any `openclaw.json` change — no restart needed
- Every switch creates a timestamped backup
- `original_primary` preserved in `state.json` — restore always works
- After activating new providers: add them to `agents.defaults.model.fallbacks` AND `model_registry.json` `status: "active"`
