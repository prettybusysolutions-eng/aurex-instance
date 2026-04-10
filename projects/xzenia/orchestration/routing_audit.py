#!/usr/bin/env python3
"""
routing_audit.py — Produce a Markdown audit table of CSMR task routing.

Reads:
  - task-router.json (in same directory)
  - openclaw.json (OpenClaw config)

Writes:
  - /workspace/projects/xzenia/reports/routing-audit.md
"""
import json
import os
import sys
import tempfile
import shutil
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTER_CONFIG = os.path.join(SCRIPT_DIR, "task-router.json")
OPENCLAW_CONFIG = os.path.expanduser("~/.openclaw/openclaw.json")
REPORTS_DIR = os.path.join(SCRIPT_DIR, "..", "reports")
REPORT_PATH = os.path.join(REPORTS_DIR, "routing-audit.md")

CONTEXT_WINDOWS = {
    "google-gemini-cli/gemini-3.1-pro-preview": "1,000,000",
    "qwen-portal/coder-model": "125,000",
    "minimax-portal/MiniMax-M2.5-Lightning": "40,000",
    "minimax-portal/MiniMax-M2.5": "40,000",
    "anthropic/claude-sonnet-4-6": "200,000",
    "openai-codex/gpt-5.4": "128,000",
    "ollama/qwen2.5:7b": "32,000",
    "ollama/llama3.2:3b": "8,000",
}

COST_TIERS = {
    "google-gemini-cli/gemini-3.1-pro-preview": "OAuth ($0)",
    "qwen-portal/coder-model": "OAuth ($0)",
    "minimax-portal/MiniMax-M2.5-Lightning": "OAuth ($0)",
    "minimax-portal/MiniMax-M2.5": "OAuth ($0)",
    "anthropic/claude-sonnet-4-6": "Paid (API)",
    "openai-codex/gpt-5.4": "Paid (API)",
    "ollama/qwen2.5:7b": "Local ($0)",
    "ollama/llama3.2:3b": "Local ($0)",
}

AUTH_STATUS = {
    "google-gemini-cli/gemini-3.1-pro-preview": "✅ OAuth (gemini CLI)",
    "qwen-portal/coder-model": "✅ OAuth (portal)",
    "minimax-portal/MiniMax-M2.5-Lightning": "✅ OAuth (portal)",
    "minimax-portal/MiniMax-M2.5": "✅ OAuth (portal)",
    "anthropic/claude-sonnet-4-6": "✅ API key",
    "openai-codex/gpt-5.4": "⚠️  API key (fallback)",
    "ollama/qwen2.5:7b": "✅ Local",
    "ollama/llama3.2:3b": "✅ Local",
}


def load_json(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[routing_audit] Warning: could not load {path}: {e}", file=sys.stderr)
        return {}


def build_report() -> str:
    router = load_json(ROUTER_CONFIG)
    openclaw = load_json(OPENCLAW_CONFIG)

    routes = router.get("routes", [])
    defaults = openclaw.get("agents", {}).get("defaults", {})
    primary_model = defaults.get("model", {}).get("primary", "unknown")
    fallbacks = defaults.get("model", {}).get("fallbacks", [])

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# CSMR Task Routing Audit",
        f"",
        f"_Generated: {now}_",
        f"",
        f"## Active Task Router Config (`task-router.json`)",
        f"",
        f"| Task Type | Route ID | Assigned Model | Context Window | Cost Tier | Auth Status |",
        f"|-----------|----------|----------------|----------------|-----------|-------------|",
    ]

    for route in routes:
        model = route.get("model", "?")
        route_id = route.get("id", "?")
        triggers = route.get("triggers", [])
        ctx = CONTEXT_WINDOWS.get(model, route.get("context_window", "?"))
        if isinstance(ctx, int):
            ctx = f"{ctx:,}"
        cost = COST_TIERS.get(model, route.get("cost_tier", "?"))
        auth = AUTH_STATUS.get(model, "?")
        for trigger in triggers:
            lines.append(f"| `{trigger}` | {route_id} | `{model}` | {ctx} | {cost} | {auth} |")

    lines += [
        f"",
        f"## OpenClaw Fallback Ladder (`openclaw.json`)",
        f"",
        f"| Priority | Model | Context Window | Cost Tier | Auth Status |",
        f"|----------|-------|----------------|-----------|-------------|",
    ]

    all_fallback = [primary_model] + fallbacks
    for i, model in enumerate(all_fallback):
        label = "primary" if i == 0 else f"fallback-{i}"
        ctx = CONTEXT_WINDOWS.get(model, "?")
        cost = COST_TIERS.get(model, "?")
        auth = AUTH_STATUS.get(model, "?")
        lines.append(f"| {label} | `{model}` | {ctx} | {cost} | {auth} |")

    lines += [
        f"",
        f"## Routing Logic Summary",
        f"",
        f"- **Long-context analysis** (attribution, causal, research, frontier intelligence) → `google-gemini-cli/gemini-3.1-pro-preview` (1M ctx, OAuth)",
        f"- **Code generation** (proposals, patches, scripts) → `qwen-portal/coder-model` (125k ctx, OAuth)",
        f"- **Fast gate decisions / classification** → `minimax-portal/MiniMax-M2.5-Lightning` (OAuth)",
        f"- **User chat / general** → `anthropic/claude-sonnet-4-6` (paid, highest quality)",
        f"",
        f"_Source: `orchestration/task-router.json` | Router: `orchestration/task_router.py`_",
    ]

    return "\n".join(lines) + "\n"


def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report = build_report()

    # Atomic write: write to tmp then rename
    fd, tmp_path = tempfile.mkstemp(dir=REPORTS_DIR, suffix=".md.tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(report)
        shutil.move(tmp_path, REPORT_PATH)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    print(f"[routing_audit] Report written to: {REPORT_PATH}")
    print(report)


if __name__ == "__main__":
    main()
