#!/usr/bin/env python3
"""
Session Boot — unified session-start entrypoint.
Reads checkpoint + resume queue, generates NEXT-ACTION.md,
prints boot summary. Run at start of every session.
Weaves: continuity-guard, resume_last_intent, intent-graph, charter status.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
STATE = WORKSPACE / 'projects/xzenia/state'
CHARTER = WORKSPACE / 'projects/xzenia/charter/build-charter.json'
NEXT_ACTION = WORKSPACE / 'NEXT-ACTION.md'


def load_json(path, default=None):
    try:
        return json.loads(path.read_text()) if path.exists() else (default or {})
    except Exception:
        return default or {}


def checkpoint_summary(cp: dict) -> str:
    if not cp:
        return '- No checkpoint found.'
    ts = cp.get('timestamp', 'unknown')
    phase = cp.get('phase', 'unknown')
    status = cp.get('status', 'unknown')
    resume = cp.get('resumeInstruction', '')
    frontier = cp.get('nextFrontier', [])
    lines = [
        f'- **Last checkpoint:** `{ts}`',
        f'- **Phase:** `{phase}`',
        f'- **Status:** `{status}`',
    ]
    if resume:
        lines.append(f'- **Resume instruction:** {resume}')
    if frontier:
        lines.append('- **Next frontier:**')
        for f in frontier:
            lines.append(f'  - {f}')
    return '\n'.join(lines)


def queue_summary(queue: dict) -> str:
    items = [i for i in queue.get('items', []) if i.get('status') == 'pending']
    if not items:
        return '- Resume queue: empty'
    items = sorted(items, key=lambda x: x.get('priority', 999))
    lines = ['- **Pending resume items:**']
    for item in items[:5]:
        lines.append(f"  - [{item.get('priority','?')}] {item.get('id','?')} — {item.get('description','')}")
    return '\n'.join(lines)


def charter_summary(charter: dict) -> str:
    systems = charter.get('systems', [])
    if not systems:
        return '- Charter: not found'
    lines = ['- **Charter systems:**']
    for s in systems:
        icon = {'ready': '🟢', 'blocked_on_dependencies': '🔴', 'in_progress': '🟡', 'done': '✅'}.get(s.get('status', ''), '⚪')
        lines.append(f"  - {icon} {s.get('name','?')} — `{s.get('status','?')}`")
    return '\n'.join(lines)


def intent_summary(graph: dict) -> str:
    nodes = graph.get('nodes', [])
    active = [n for n in nodes if n.get('status') in ('active', 'pending')]
    if not active:
        return '- Intent graph: no active nodes'
    lines = ['- **Active intent nodes:**']
    for n in active[:5]:
        lines.append(f"  - [{n.get('status','?')}] {n.get('title','?')}")
    return '\n'.join(lines)


def derive_next_action(cp, queue, charter, graph) -> str:
    # Priority: pending resume queue item > charter next ready system > frontier from checkpoint
    items = sorted([i for i in queue.get('items', []) if i.get('status') == 'pending'],
                   key=lambda x: x.get('priority', 999))
    if items:
        top = items[0]
        return f"**Resume queued work:** `{top.get('id','?')}` — {top.get('description','')}"

    systems = charter.get('systems', [])
    for s in systems:
        if s.get('status') == 'ready':
            return f"**Build charter system:** {s.get('name','?')} (System {s.get('id','?')})"
        if s.get('status') == 'in_progress':
            return f"**Continue in-progress:** {s.get('name','?')}"

    frontier = cp.get('nextFrontier', [])
    if frontier:
        return f"**From last checkpoint frontier:** {frontier[0]}"

    return "**No queued work. Re-read charter and select highest-priority next system.**"


def truth_summary() -> str:
    truth = load_json(STATE / 'system-truth.json')
    directives = load_json(STATE / 'execution-directives.json')
    if not truth and not directives:
        return '- System truth: not found'
    lines = []
    ident = truth.get('identity', {})
    if ident.get('system'):
        lines.append(f'- **Identity:** {ident.get("system")}')
    execd = truth.get('executionDirectives') or directives.get('directives', {})
    if execd:
        lines.append('- **Execution directives:**')
        for key in ['noFallbackModels', 'persistentExecution', 'cleanExecution', 'compactCanonicalMemory']:
            if key in execd:
                lines.append(f'  - {key}: `{execd.get(key)}`')
    return '\n'.join(lines)


def session_state_summary() -> str:
    ss = WORKSPACE / 'SESSION-STATE.md'
    if not ss.exists():
        return '- SESSION-STATE.md: not found — using checkpoint fallback'
    text = ss.read_text()
    lines = text.strip().split('\n')[:15]
    return '\n'.join(f'  {l}' for l in lines)


def main():
    cp = load_json(STATE / 'latest-checkpoint.json')
    queue = load_json(STATE / 'resume-queue.json')
    charter = load_json(CHARTER)
    graph = load_json(STATE / 'intent-graph.json')

    now = datetime.now().astimezone().isoformat()
    next_action = derive_next_action(cp, queue, charter, graph)

    ss_summary = session_state_summary()
    content = f"""# NEXT-ACTION.md
_Generated by session-boot (Reconstitution Protocol v1.0) — {now}_

## [RECONSTITUTED] Session State
{ss_summary}

## System Truth
{truth_summary()}

## Checkpoint
{checkpoint_summary(cp)}

## Resume Queue
{queue_summary(queue)}

## Charter Status
{charter_summary(charter)}

## Intent Graph
{intent_summary(graph)}

---

## ✦ Next Action
{next_action}

---
_This file is regenerated each session. Do not edit manually._
"""
    NEXT_ACTION.write_text(content)

    truth = load_json(STATE / 'system-truth.json')
    directives = load_json(STATE / 'execution-directives.json')

    summary = {
        'boot_time': now,
        'checkpoint_phase': cp.get('phase', 'none'),
        'checkpoint_status': cp.get('status', 'none'),
        'queue_pending': len([i for i in queue.get('items', []) if i.get('status') == 'pending']),
        'charter_ready_systems': [s.get('name') for s in charter.get('systems', []) if s.get('status') == 'ready'],
        'next_action': next_action,
        'truth_identity': truth.get('identity', {}).get('system', 'unknown'),
        'no_fallback_models': (truth.get('executionDirectives', {}) or directives.get('directives', {})).get('noFallbackModels'),
        'next_action_file': str(NEXT_ACTION)
    }
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
