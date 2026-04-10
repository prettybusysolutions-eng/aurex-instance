#!/usr/bin/env python3
"""
Degradation Evaluator — System 4 artifact.
Monitors disk/free resource and auto-switches degradation tiers.
Writes to storage-governor.json and emits confidence labels on outputs.
"""
import json
import shutil
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
POLICY = WORKSPACE / 'projects/xzenia/runtime/degradation-policy.json'
REPORT = WORKSPACE / 'projects/xzenia/csmr/reports/storage-governor.json'


def load_policy():
    return json.loads(POLICY.read_text()) if POLICY.exists() else {'degradation_tiers': {}, 'current_tier': 'normal'}


def get_disk_free():
    stats = shutil.disk_usage(WORKSPACE)
    return stats.free


def evaluate_tier(policy, free_bytes):
    tiers = policy.get('degradation_tiers', {})
    # Check from most restrictive upward: minimal first, then reduced, then normal
    for tier_name in ['minimal', 'reduced', 'normal']:
        threshold_gb = tiers.get(tier_name, {}).get('disk_free_gb_threshold', 0)
        threshold_bytes = threshold_gb * 1_000_000_000
        if threshold_bytes > 0 and free_bytes < threshold_bytes:
            return tier_name
    return 'normal'


def main():
    start = time.time()
    policy = load_policy()
    free = get_disk_free()
    free_gb = free / 1_000_000_000
    
    new_tier = evaluate_tier(policy, free)
    old_tier = policy.get('current_tier', 'normal')
    changed = old_tier != new_tier
    
    if changed:
        policy['current_tier'] = new_tier
        policy['last_evaluated'] = datetime.now().astimezone().isoformat()
        POLICY.write_text(json.dumps(policy, indent=2))
    
    tier_info = policy['degradation_tiers'].get(new_tier, {})
    
    report = {
        'timestamp': datetime.now().astimezone().isoformat(),
        'disk_free_bytes': free,
        'disk_free_gb': round(free_gb, 2),
        'current_tier': new_tier,
        'previous_tier': old_tier if changed else new_tier,
        'tier_changed': changed,
        'confidence_label': tier_info.get('confidence_label', 'unknown'),
        'capabilities': tier_info.get('capabilities', 'unknown'),
        'restrictions': tier_info.get('restrictions', []),
        'actions': tier_info.get('actions', []),
        'latency_ms': int((time.time() - start) * 1000)
    }
    
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    
    if changed:
        print(f'\n⚠️  DEGRADATION TIER CHANGE: {old_tier} → {new_tier}', file=__import__('sys').stderr)


if __name__ == '__main__':
    main()
