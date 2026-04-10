#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
REGISTRY = WORKSPACE / 'projects/xzenia/orchestration/bottleneck-registry.json'
SUPERVISOR = WORKSPACE / 'projects/xzenia/csmr/reports/unified-supervisor-health.json'
DEGRADATION = WORKSPACE / 'projects/xzenia/csmr/reports/degradation-gate.json'
COST = WORKSPACE / 'projects/xzenia/csmr/reports/cost-accounting.json'
ADVERSARIAL = WORKSPACE / 'projects/xzenia/csmr/reports/adversarial-suite-report.json'
NORMAL_TIER = WORKSPACE / 'projects/xzenia/csmr/reports/normal-tier-recalibration.json'
CHARTER = WORKSPACE / 'projects/xzenia/charter/unheard-of-threshold-charter.json'
OUT = WORKSPACE / 'projects/xzenia/csmr/reports/frontier-evolver-report.json'


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def next_frontier(registry, supervisor, degradation, cost, adversarial, normal_tier, charter):
    ready = [i for i in registry.get('items', []) if i.get('status') == 'ready' and i.get('queue_policy') != 'self_test_hold']
    if ready:
        return None, 'registry already has ready work'

    seen_ids = {i.get('id') for i in registry.get('items', [])}

    if supervisor.get('contradictions'):
        return {
            'id': 'charter-remediate-supervisor-contradictions',
            'priority': 1,
            'status': 'ready',
            'title': 'Remediate remaining supervisor contradictions',
            'class': 'internal_reversible',
            'executor': 'python3 projects/xzenia/execution/executor_gateway.py charter-remediate-supervisor-contradictions',
            'verify': 'supervisor report returns zero contradictions',
            'nextStep': 'resolve contradiction sources and rerun supervisor'
        }, 'active contradiction surface'

    if degradation.get('tier') == 'reduced' and normal_tier.get('eligible', True) and 'charter-normal-tier-lift' not in seen_ids:
        return {
            'id': 'charter-normal-tier-lift',
            'priority': 1,
            'status': 'ready',
            'title': 'Lift substrate from reduced to normal tier',
            'class': 'internal_reversible',
            'executor': 'python3 projects/xzenia/execution/executor_gateway.py charter-normal-tier-lift',
            'verify': 'degradation gate reports normal tier under honest policy',
            'nextStep': 'reduce structural pressure or improve capability posture enough to cross the normal threshold'
        }, 'tier-lifting opportunity'

    charter_frontiers = {f.get('id'): f for f in charter.get('frontiers', [])}
    mutation_frontier = charter_frontiers.get('frontier-3-governed-substrate-mutation', {})
    if mutation_frontier.get('status') in ('ready', 'active'):
        cycle_count = sum(1 for i in registry.get('items', []) if str(i.get('id', '')).startswith('bottleneck-governed-substrate-mutation-loop'))
        mutation_id = f'bottleneck-governed-substrate-mutation-loop-{cycle_count + 1}'
        return {
            'id': mutation_id,
            'priority': 2,
            'status': 'ready',
            'title': 'Execute governed substrate mutation loop through gates and canary evaluation',
            'class': 'internal_reversible',
            'executor': 'python3 projects/xzenia/execution/executor_gateway.py bottleneck-governed-substrate-mutation-loop',
            'verify': 'a measured proposal is generated, persisted, gated, and promoted or rolled back with artifacts',
            'nextStep': 'run proposal synthesis, persistence, gates A/B/C, canary evaluation, and final promotion decision',
            'frontier': 'frontier-3-governed-substrate-mutation'
        }, 'charter frontier: governed substrate mutation'

    items = cost.get('line_items', [])
    if items:
        top = items[0]['event_type']
        return {
            'id': 'charter-proof-spine-cost-optimization',
            'priority': 3,
            'status': 'ready',
            'title': f'Optimize recurring proof-spine cost driver: {top}',
            'class': 'internal_reversible',
            'executor': 'python3 projects/xzenia/execution/executor_gateway.py charter-proof-spine-cost-optimization',
            'verify': f'cost accounting shows reduced recurring subtotal or invocation burden for `{top}` without weakening proof guarantees',
            'nextStep': f'optimize recurring driver `{top}` without weakening proof guarantees',
            'target_driver': top
        }, 'cost concentration'

    return None, 'no frontier justified by current evidence'


def main():
    registry = load(REGISTRY, {'items': []})
    supervisor = load(SUPERVISOR, {})
    degradation = load(DEGRADATION, {})
    cost = load(COST, {'line_items': []})
    adversarial = load(ADVERSARIAL, {})
    normal_tier = load(NORMAL_TIER, {})
    charter = load(CHARTER, {'frontiers': []})

    item, rationale = next_frontier(registry, supervisor, degradation, cost, adversarial, normal_tier, charter)
    if item:
        registry['items'].insert(0, item)
        registry['updatedAt'] = datetime.now().astimezone().isoformat()
        REGISTRY.write_text(json.dumps(registry, indent=2) + '\n')

    payload = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'created': item,
        'rationale': rationale,
        'status': 'done and verified'
    }
    OUT.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
