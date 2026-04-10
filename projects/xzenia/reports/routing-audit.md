# CSMR Task Routing Audit

_Generated: 2026-03-23T02:53:59Z_

## Active Task Router Config (`task-router.json`)

| Task Type | Route ID | Assigned Model | Context Window | Cost Tier | Auth Status |
|-----------|----------|----------------|----------------|-----------|-------------|
| `attribution` | long-context-analysis | `google-gemini-cli/gemini-3.1-pro-preview` | 1,000,000 | OAuth ($0) | ✅ OAuth (gemini CLI) |
| `causal_finding` | long-context-analysis | `google-gemini-cli/gemini-3.1-pro-preview` | 1,000,000 | OAuth ($0) | ✅ OAuth (gemini CLI) |
| `research_loop` | long-context-analysis | `google-gemini-cli/gemini-3.1-pro-preview` | 1,000,000 | OAuth ($0) | ✅ OAuth (gemini CLI) |
| `frontier_intelligence` | long-context-analysis | `google-gemini-cli/gemini-3.1-pro-preview` | 1,000,000 | OAuth ($0) | ✅ OAuth (gemini CLI) |
| `long_doc` | long-context-analysis | `google-gemini-cli/gemini-3.1-pro-preview` | 1,000,000 | OAuth ($0) | ✅ OAuth (gemini CLI) |
| `generate_proposal` | code-generation | `qwen-portal/coder-model` | 125,000 | OAuth ($0) | ✅ OAuth (portal) |
| `synthesize_patch` | code-generation | `qwen-portal/coder-model` | 125,000 | OAuth ($0) | ✅ OAuth (portal) |
| `write_script` | code-generation | `qwen-portal/coder-model` | 125,000 | OAuth ($0) | ✅ OAuth (portal) |
| `code_task` | code-generation | `qwen-portal/coder-model` | 125,000 | OAuth ($0) | ✅ OAuth (portal) |
| `gate_decision` | fast-reasoning | `minimax-portal/MiniMax-M2.5-Lightning` | 40,000 | OAuth ($0) | ✅ OAuth (portal) |
| `classification` | fast-reasoning | `minimax-portal/MiniMax-M2.5-Lightning` | 40,000 | OAuth ($0) | ✅ OAuth (portal) |
| `quick_eval` | fast-reasoning | `minimax-portal/MiniMax-M2.5-Lightning` | 40,000 | OAuth ($0) | ✅ OAuth (portal) |
| `user_chat` | default-primary | `anthropic/claude-sonnet-4-6` | 200,000 | Paid (API) | ✅ API key |
| `general` | default-primary | `anthropic/claude-sonnet-4-6` | 200,000 | Paid (API) | ✅ API key |

## OpenClaw Fallback Ladder (`openclaw.json`)

| Priority | Model | Context Window | Cost Tier | Auth Status |
|----------|-------|----------------|-----------|-------------|
| primary | `anthropic/claude-sonnet-4-6` | 200,000 | Paid (API) | ✅ API key |
| fallback-1 | `openai-codex/gpt-5.4` | 128,000 | Paid (API) | ⚠️  API key (fallback) |
| fallback-2 | `google-gemini-cli/gemini-3.1-pro-preview` | 1,000,000 | OAuth ($0) | ✅ OAuth (gemini CLI) |
| fallback-3 | `minimax-portal/MiniMax-M2.5` | 40,000 | OAuth ($0) | ✅ OAuth (portal) |
| fallback-4 | `qwen-portal/coder-model` | 125,000 | OAuth ($0) | ✅ OAuth (portal) |
| fallback-5 | `ollama/qwen2.5:7b` | 32,000 | Local ($0) | ✅ Local |
| fallback-6 | `ollama/qwen2.5:3b` | ? | ? | ? |
| fallback-7 | `ollama/llama3.2:3b` | 8,000 | Local ($0) | ✅ Local |
| fallback-8 | `ollama/qwen2.5:1.5b-instruct-q4_K_M` | ? | ? | ? |

## Routing Logic Summary

- **Long-context analysis** (attribution, causal, research, frontier intelligence) → `google-gemini-cli/gemini-3.1-pro-preview` (1M ctx, OAuth)
- **Code generation** (proposals, patches, scripts) → `qwen-portal/coder-model` (125k ctx, OAuth)
- **Fast gate decisions / classification** → `minimax-portal/MiniMax-M2.5-Lightning` (OAuth)
- **User chat / general** → `anthropic/claude-sonnet-4-6` (paid, highest quality)

_Source: `orchestration/task-router.json` | Router: `orchestration/task_router.py`_
