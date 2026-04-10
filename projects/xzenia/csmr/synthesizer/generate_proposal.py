#!/usr/bin/env python3
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

DB = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/csmr/ledger/causal_ledger.sqlite')


def recent_proposals(limit=12):
    if not DB.exists():
        return []
    conn = sqlite3.connect(DB)
    try:
        rows = conn.execute("SELECT proposal_json FROM modification_proposals ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [json.loads(r[0]) for r in rows if r and r[0]]
    finally:
        conn.close()


def already_seen(candidate, proposals):
    for p in proposals:
        if p.get('mutation_class') == candidate.get('mutation_class') and p.get('target') == candidate.get('target') and p.get('change') == candidate.get('change'):
            return True
    return False


def choose_first_novel(candidates, proposals):
    for candidate in candidates:
        if not already_seen(candidate, proposals):
            return candidate
    return candidates[-1]


def choose_default_novel_candidate(ts, root, proposals):
    candidates = [
        {
            'proposal_id': f'proposal-{ts}',
            'mutation_class': 'prompt_guidance_change',
            'target': 'canonical-processor.general-guidance',
            'change': {'append_rule': 'Prefer concise, directly verified execution updates.'},
            'reason': f'Default proposal for root cause {root}',
            'expected_impact': 'tighten execution discipline'
        },
        {
            'proposal_id': f'proposal-{ts}',
            'mutation_class': 'prompt_guidance_change',
            'target': 'canonical-processor.general-guidance',
            'change': {'append_rule': 'Prefer mutation proposals that differ materially from the last promoted change.'},
            'reason': f'Novelty guard proposal for root cause {root}',
            'expected_impact': 'reduce duplicate governed mutations'
        },
        {
            'proposal_id': f'proposal-{ts}',
            'mutation_class': 'fallback_order_change',
            'target': 'projects/xzenia/orchestration/resilience-policy.json',
            'change': {'preferred_first': 'qwen2.5:7b'},
            'reason': f'Fallback diversity proposal for root cause {root}',
            'expected_impact': 'explore stronger local synchronous path without premature minimal-model promotion'
        }
    ]
    return choose_first_novel(candidates, proposals)


def build_proposal(finding):
    failure_class = finding.get('failure_class', 'unknown')
    root = finding.get('suspected_root_cause', 'unclassified_failure_pattern')
    surface = finding.get('recommended_surface', 'analysis')
    ts = int(dt.datetime.now().timestamp())
    proposals = recent_proposals()

    if root == 'duplicate_transport_owner':
        return {
            'proposal_id': f'proposal-{ts}',
            'mutation_class': 'prompt_guidance_change',
            'target': 'canonical-processor.transport-guidance',
            'change': {
                'append_rule': 'Keep one canonical Telegram transport owner; reject duplicate poller designs.'
            },
            'reason': f'Address {failure_class} rooted in {root}',
            'expected_impact': 'reduce transport conflicts'
        }

    if root == 'storage_headroom_exhausted':
        return {
            'proposal_id': f'proposal-{ts}',
            'mutation_class': 'threshold_delta',
            'target': 'anomaly.failure_rate',
            'change': {'delta': -0.05},
            'reason': f'Address {failure_class} rooted in {root}',
            'expected_impact': 'increase sensitivity to storage-related anomalies'
        }

    # Specific gate rejection signal: resilience-policy failed Gate C with
    # quality_regression_under_complex_load. Propose concrete resilience-policy
    # mutations that tighten fallback behavior under load without sacrificing quality.
    if failure_class == 'gate_rejection_gate_c' or root == 'gate_report':
        evidence_vector = finding.get('evidence_vector', {})
        rejection_reason = evidence_vector.get('raw_evidence', {}).get('reason', '')
        if 'quality_regression' in rejection_reason or 'complex_load' in rejection_reason:
            candidates = [
                {
                    'proposal_id': f'proposal-{ts}',
                    'mutation_class': 'fallback_order_change',
                    'target': 'projects/xzenia/orchestration/resilience-policy.json',
                    'change': {'preferred_first': 'qwen2.5:7b', 'rationale': 'promote stronger local model to primary under complex-load conditions to reduce quality regression risk'},
                    'reason': f'Gate C rejection: {rejection_reason} on resilience-policy',
                    'expected_impact': 'reduce quality regression probability under complex load by promoting stronger local model'
                },
                {
                    'proposal_id': f'proposal-{ts}',
                    'mutation_class': 'threshold_delta',
                    'target': 'projects/xzenia/orchestration/resilience-policy.json',
                    'change': {'maxAttemptsPerModel': 2, 'rationale': 'allow one retry on quality regression before falling back to next model tier'},
                    'reason': f'Gate C rejection: {rejection_reason} — add retry before fallback',
                    'expected_impact': 'recover from transient quality regressions without immediately degrading to weaker model'
                },
                {
                    'proposal_id': f'proposal-{ts}',
                    'mutation_class': 'fallback_order_change',
                    'target': 'projects/xzenia/orchestration/resilience-policy.json',
                    'change': {'preferred_first': 'qwen2.5:3b', 'rationale': 'fall back to fast local model when complex load exceeds primary capacity'},
                    'reason': f'Gate C rejection: {rejection_reason} — faster fallback under pressure',
                    'expected_impact': 'reduce latency and resource use under complex-load conditions'
                },
            ]
            return choose_first_novel(candidates, proposals)

    if root == 'slow_or_overweight_execution_path':
        candidates = [
            {
                'proposal_id': f'proposal-{ts}',
                'mutation_class': 'fallback_order_change',
                'target': 'projects/xzenia/orchestration/resilience-policy.json',
                'change': {'preferred_first': 'qwen2.5:7b'},
                'reason': f'Address {failure_class} rooted in {root}',
                'expected_impact': 'reduce timeout probability on synchronous paths while preserving quality under complex load'
            },
            {
                'proposal_id': f'proposal-{ts}',
                'mutation_class': 'prompt_guidance_change',
                'target': 'canonical-processor.execution-guidance',
                'change': {'append_rule': 'Avoid promoting minimal models too early on the general synchronous path.'},
                'reason': f'Guard quality under complex load for {failure_class}',
                'expected_impact': 'prevent regressions from undersized-path promotion'
            }
        ]
        return choose_first_novel(candidates, proposals)

    if surface == 'component_logic':
        candidates = [
            {
                'proposal_id': f'proposal-{ts}',
                'mutation_class': 'prompt_guidance_change',
                'target': 'canonical-processor.execution-guidance',
                'change': {'append_rule': 'Prefer cross-surface bottleneck reduction over repeated mutations on one target.'},
                'reason': f'Surface-aware proposal for {failure_class}',
                'expected_impact': 'diversify governed mutation targets'
            },
            {
                'proposal_id': f'proposal-{ts}',
                'mutation_class': 'fallback_order_change',
                'target': 'projects/xzenia/orchestration/resilience-policy.json',
                'change': {'preferred_first': 'qwen2.5:7b'},
                'reason': f'Surface-aware fallback proposal for {failure_class}',
                'expected_impact': 'shift execution weight toward stronger local path when component logic dominates'
            }
        ]
        return choose_first_novel(candidates, proposals)

    return choose_default_novel_candidate(ts, root, proposals)


def main():
    if len(sys.argv) != 2:
        print('usage: generate_proposal.py <causal-finding.json>', file=sys.stderr)
        raise SystemExit(2)
    finding = json.loads(open(sys.argv[1]).read())
    print(json.dumps(build_proposal(finding), indent=2))


if __name__ == '__main__':
    main()
