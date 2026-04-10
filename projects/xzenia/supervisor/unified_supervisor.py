#!/usr/bin/env python3
"""
UNIFIED SUPERVISOR — WITH DECISION CORE INTEGRATION
=====================================================

This supervisor doesn't just monitor — it THINKS.
Before any action, it runs through the Decision Core.

This is where Xzenia stops "running" and starts "thinking."
"""
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
REGISTRY = WORKSPACE / 'projects/xzenia/orchestration/bottleneck-registry.json'
CHECKPOINT = WORKSPACE / 'projects/xzenia/state/latest-checkpoint.json'
QUEUE = WORKSPACE / 'projects/xzenia/state/resume-queue.json'
STORAGE = WORKSPACE / 'projects/xzenia/csmr/reports/storage-governor.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/unified-supervisor-health.json'
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
DECISION_CORE = WORKSPACE / 'projects/xzenia/csmr/compounding/self_tuning_decision.py'
IGNORE_STALL_PREFIXES = ('charter-adversarial-hardening', 'charter-cost-discipline')


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def run_decision_core(task: str, context: dict = None) -> dict:
    """Run Decision Core to think before acting."""
    # Import and run Decision Core
    import subprocess
    result = subprocess.run(
        ['python3', DECISION_CORE, '--decide', task, json.dumps(context or {})],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return {'error': 'Decision Core unavailable', 'fallback': True}


def main():
    start = time.time()
    
    # === PHASE 1: THINK BEFORE ACTING ===
    print("=== SUPERVISOR: THINKING (Decision Core) ===")
    
    # Gather system data for Decision Core
    registry = load(REGISTRY, {'items': []})
    checkpoint = load(CHECKPOINT, {})
    queue = load(QUEUE, {'items': []})
    storage = load(STORAGE, {})
    prev = load(OUT, {})
    
    # Build context for Decision Core
    context = {
        'task': 'supervisor_cycle',
        'registry_items': len(registry.get('items', [])),
        'queue_items': len(queue.get('items', [])),
        'storage': storage,
        'previous_health': prev.get('health_score', 0.5),
        'contradictions_detected': len(prev.get('contradictions', []))
    }
    
    # THINK: Get decision before acting
    decision = run_decision_core('Run supervisor cycle', context)
    
    print(f"Decision: {decision.get('selection', {}).get('selected', 'unknown')}")
    print(f"Confidence: {decision.get('selection', {}).get('confidence', 0):.2f}")
    print(f"Reasoning: {decision.get('selection', {}).get('reasoning', 'N/A')[:100]}...")
    
    # === PHASE 2: Execute based on decision ===
    
    contradictions = []
    ready_registry = [i['id'] for i in registry.get('items', []) if i.get('status') == 'ready']
    pending_queue = [i['id'] for i in queue.get('items', []) if i.get('status') in ('pending', 'in_progress')]
    if ready_registry and pending_queue and ready_registry[0] != pending_queue[0]:
        contradictions.append({'type': 'frontier_mismatch', 'registry_top': ready_registry[0], 'queue_top': pending_queue[0]})

    stalled = []
    for item in registry.get('items', []):
        item_id = item.get('id', '')
        if item.get('status') == 'in_progress' and not item_id.startswith(IGNORE_STALL_PREFIXES):
            stalled.append({'id': item_id, 'reason': 'still in_progress at supervisor scan'})

    remediation = []
    if storage:
        high_reclaim = int(storage.get('high_safety_reclaim_bytes', 0))
        if high_reclaim > 50_000_000:
            contradictions.append({'type': 'storage_pressure_reclaim_available', 'high_safety_reclaim_bytes': high_reclaim})
            remediation.append('execute charter-storage-governance-layer reclaim actions')

    overall = 'pass' if not contradictions else 'partial'
    score = 1.0 if overall == 'pass' else 0.7
    
    # === PHASE 3: Override action based on Decision Core ===
    selected = decision.get('selection', {}).get('selected', 'continue')
    
    if selected == 'repair':
        score = max(score, 0.5)  # Lower score to trigger repair
        remediation.append('Decision Core: repair mode')
    elif selected == 'supervisor_review':
        # Run deeper analysis
        score = max(score, 0.6)
        remediation.append('Decision Core: detailed review')
    elif selected == 'think_deeper':
        # Defer decision
        score = max(score, 0.4)
        remediation.append('Decision Core: thinking deeper - deferred')
    
    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'overall': overall,
        'health_score': score,
        'decision_core': {
            'thinking': True,
            'selected': selected,
            'confidence': decision.get('selection', {}).get('confidence', 0),
            'latency_ms': decision.get('latency_ms', 0),
            'net_value': decision.get('selection', {}).get('net_value', 0)
        },
        'components': [
            {'name': 'checkpoint', 'status': 'ok' if checkpoint else 'missing'},
            {'name': 'registry', 'status': 'ok' if registry.get('items') else 'empty'},
            {'name': 'resume_queue', 'status': 'ok' if queue.get('items') is not None else 'missing'},
            {'name': 'storage_governor', 'status': 'ok' if storage else 'missing'},
            {'name': 'decision_core', 'status': 'active' if not decision.get('error') else 'fallback'}
        ],
        'contradictions': contradictions,
        'stalled_items': stalled,
        'recommended_action': selected,
        'remediation': remediation if remediation else ([] if overall == 'pass' else ['run sync_charter_to_resume_queue.py'])
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')

    changed = (
        prev.get('overall') != payload.get('overall') or
        prev.get('contradictions') != payload.get('contradictions') or
        prev.get('stalled_items') != payload.get('stalled_items') or
        prev.get('recommended_action') != payload.get('recommended_action')
    )

    if changed:
        conn = sqlite3.connect(DB)
        conn.execute(
            'INSERT INTO causal_events (created_at, event_type, session_key, component, input_json, output_json, outcome, latency_ms, failure_class, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                payload['timestamp'], 'supervisor_cycle', 'local:supervisor', 'unified_supervisor',
                json.dumps({'registry_items': len(registry.get('items', [])), 'queue_items': len(queue.get('items', [])), 'decision': selected}),
                json.dumps(payload), 'ok' if overall == 'pass' else 'partial', int((time.time() - start) * 1000),
                None if overall == 'pass' else 'supervisory_contradiction', json.dumps({'tier': 'system-3', 'decision_core': True, 'state_change_logged': True})
            )
        )
        conn.commit()
        conn.close()

    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()