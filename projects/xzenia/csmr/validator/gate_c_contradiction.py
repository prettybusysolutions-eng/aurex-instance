#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print('usage: gate_c_contradiction.py <proposal.json>', file=sys.stderr)
        raise SystemExit(2)
    proposal = json.loads(Path(sys.argv[1]).read_text())
    mutation_class = proposal.get('mutation_class')
    target = proposal.get('target', '')
    change = proposal.get('change', {})

    delta = 0.0
    contradicted = None
    reason = 'no contradiction detected'

    if mutation_class == 'fallback_order_change' and change.get('preferred_first') == 'qwen2.5:1.5b-instruct-q4_K_M':
        delta = 0.12
        contradicted = 'quality_regression_under_complex_load'
        reason = 'minimal model promoted too early for general synchronous path'
    elif mutation_class == 'threshold_delta' and float(change.get('delta', 0)) < -0.11:
        delta = 0.07
        contradicted = 'overtriggered_anomaly_noise'
        reason = 'threshold reduction too aggressive and increases downstream false positives'
    elif mutation_class == 'prompt_guidance_change' and 'bypass' in json.dumps(change).lower():
        delta = 0.2
        contradicted = 'policy_bypass_risk'
        reason = 'prompt guidance introduces policy bypass behavior'

    decision = 'pass' if delta <= 0.05 else 'reject'
    report = {
        'proposal_id': proposal['proposal_id'],
        'decision': decision,
        'downstream_failure_probability_delta': delta,
        'contradicted_failure': contradicted,
        'reason': reason
    }
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if decision == 'pass' else 1)


if __name__ == '__main__':
    main()
