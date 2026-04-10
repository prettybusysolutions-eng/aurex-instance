#!/usr/bin/env python3
"""
budget_tracker.py — Reads token usage from OpenClaw sources.

Sources tried in order:
1. ~/.openclaw/logs/gateway.log — parse token count lines emitted by gateway
2. ~/.openclaw/completions/ — parse completion JSON files for usage fields
3. Fallback: estimate from line count heuristic

Returns JSON to stdout: {"estimated_tokens_used": N, "source": "...", "budget_pct": N}
"""
import json
import os
import re
from pathlib import Path
from datetime import datetime, date
import sys

GATEWAY_LOG = Path.home() / '.openclaw' / 'logs' / 'gateway.log'
COMPLETIONS_DIR = Path.home() / '.openclaw' / 'completions'
DAILY_BUDGET = int(os.environ.get('DAILY_TOKEN_BUDGET', '500000'))

# Patterns for token lines in gateway log
TOKEN_PATTERNS = [
    re.compile(r'input_tokens["\s:]+(\d+)', re.I),
    re.compile(r'output_tokens["\s:]+(\d+)', re.I),
    re.compile(r'total_tokens["\s:]+(\d+)', re.I),
    re.compile(r'"tokens"[:\s]+(\d+)', re.I),
    re.compile(r'usage.*?(\d{3,})', re.I),
]

TODAY = date.today().isoformat()


def read_gateway_log():
    if not GATEWAY_LOG.exists():
        return None, 0

    total = 0
    matched = 0
    try:
        with open(GATEWAY_LOG, 'r', errors='replace') as f:
            for line in f:
                # Only count today's lines
                if not line.startswith(TODAY):
                    continue
                for pat in TOKEN_PATTERNS:
                    m = pat.search(line)
                    if m:
                        total += int(m.group(1))
                        matched += 1
                        break
    except Exception:
        return None, 0

    if matched == 0:
        return None, 0
    return 'gateway_log', total


def read_completions():
    if not COMPLETIONS_DIR.exists():
        return None, 0
    total = 0
    found = 0
    for f in sorted(COMPLETIONS_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[:200]:
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime).date().isoformat()
            if mtime != TODAY:
                continue
            data = json.loads(f.read_text())
            usage = data.get('usage') or {}
            for key in ('total_tokens', 'input_tokens', 'output_tokens'):
                v = usage.get(key)
                if v:
                    total += int(v)
                    found += 1
                    break
        except Exception:
            continue
    if found == 0:
        return None, 0
    return 'completions_dir', total


def estimate_heuristic():
    """
    Estimate from gateway log: count lines that look like real agent turns.
    Specifically: [agent] or [llm] log entries or 'agent model:' lines.
    Each agent turn ≈ 4000 tokens avg (conservative for Claude Sonnet).
    """
    if not GATEWAY_LOG.exists():
        return 'heuristic_zero', 0
    # Look for subagent usage files which may have richer data
    subagents_dir = Path.home() / '.openclaw' / 'subagents'
    if subagents_dir.exists():
        total = 0
        found = 0
        for f in subagents_dir.rglob('*.json'):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).date().isoformat()
                if mtime != TODAY:
                    continue
                data = json.loads(f.read_text())
                for key in ('total_tokens', 'input_tokens', 'output_tokens', 'usage'):
                    v = data.get(key)
                    if isinstance(v, dict):
                        t = v.get('total_tokens') or v.get('input_tokens', 0) + v.get('output_tokens', 0)
                        if t:
                            total += int(t)
                            found += 1
                            break
                    elif isinstance(v, (int, float)) and v > 0:
                        total += int(v)
                        found += 1
                        break
            except Exception:
                continue
        if found > 0:
            return 'subagents_dir', total

    # Fallback: count agent turn events in gateway log
    TURN_PATTERNS = [
        re.compile(r'\[agent\]', re.I),
        re.compile(r'agent model:', re.I),
        re.compile(r'\[llm\]', re.I),
        re.compile(r'\[turn\]', re.I),
    ]
    count = 0
    try:
        with open(GATEWAY_LOG, 'r', errors='replace') as f:
            for line in f:
                if not line.startswith(TODAY):
                    continue
                for pat in TURN_PATTERNS:
                    if pat.search(line):
                        count += 1
                        break
    except Exception:
        pass
    # Each turn ≈ 4000 tokens avg — conservative estimate for Sonnet
    return 'heuristic_turn_count', count * 4000


def get_budget_usage():
    source, tokens = read_gateway_log()
    if source is None:
        source, tokens = read_completions()
    if source is None:
        source, tokens = estimate_heuristic()

    pct = round((tokens / DAILY_BUDGET) * 100, 1) if DAILY_BUDGET > 0 else 0.0
    return {
        'date': TODAY,
        'estimated_tokens_used': tokens,
        'daily_budget': DAILY_BUDGET,
        'budget_pct': pct,
        'source': source,
    }


if __name__ == '__main__':
    print(json.dumps(get_budget_usage(), indent=2))
