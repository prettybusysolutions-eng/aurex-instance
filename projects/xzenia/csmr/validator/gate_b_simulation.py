#!/usr/bin/env python3
import json
import math
import sqlite3
import sys
from pathlib import Path

DB = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/csmr/ledger/causal_ledger.sqlite')


def percentile(values, pct):
    if not values:
        return 0.0
    values = sorted(values)
    idx = max(0, min(len(values) - 1, math.ceil((pct / 100.0) * len(values)) - 1))
    return float(values[idx])


def main():
    if len(sys.argv) != 2:
        print('usage: gate_b_simulation.py <proposal.json>', file=sys.stderr)
        raise SystemExit(2)
    proposal = json.loads(Path(sys.argv[1]).read_text())
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT outcome, latency_ms, failure_class FROM causal_events ORDER BY id DESC LIMIT 200').fetchall()
    conn.close()

    total = len(rows) or 1
    failures = [r for r in rows if r['outcome'] != 'ok']
    baseline_failure_rate = len(failures) / total
    baseline_p95_latency = percentile([r['latency_ms'] or 0 for r in rows], 95)

    simulated_failure_rate = baseline_failure_rate
    simulated_p95_latency = baseline_p95_latency
    simulated_revenue_delta = 0.0

    mutation_class = proposal.get('mutation_class')
    change = proposal.get('change', {})

    if mutation_class == 'fallback_order_change' and change.get('preferred_first') == 'qwen2.5:3b':
        simulated_failure_rate = max(0.0, baseline_failure_rate - 0.05)
        simulated_p95_latency = max(0.0, baseline_p95_latency - 50)
    elif mutation_class == 'threshold_delta':
        delta = float(change.get('delta', 0))
        simulated_failure_rate = max(0.0, baseline_failure_rate + (0.02 if abs(delta) > 0.1 else 0.0))
    elif mutation_class == 'prompt_guidance_change':
        simulated_failure_rate = baseline_failure_rate
        simulated_p95_latency = baseline_p95_latency

    decision = 'pass'
    reason = 'simulated metrics non-regressive'
    if simulated_failure_rate > baseline_failure_rate or simulated_p95_latency > baseline_p95_latency or simulated_revenue_delta < 0:
        decision = 'reject'
        reason = 'simulation regression detected'

    report = {
        'proposal_id': proposal['proposal_id'],
        'baseline_failure_rate': baseline_failure_rate,
        'simulated_failure_rate': simulated_failure_rate,
        'baseline_p95_latency': baseline_p95_latency,
        'simulated_p95_latency': simulated_p95_latency,
        'simulated_revenue_delta': simulated_revenue_delta,
        'decision': decision,
        'reason': reason
    }
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if decision == 'pass' else 1)


if __name__ == '__main__':
    main()
