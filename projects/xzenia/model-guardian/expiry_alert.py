#!/usr/bin/env python3
"""
expiry_alert.py — Check provider expiry, log alerts, return unavailable providers.

Used by guardian_cycle.py at cycle start to pre-filter the effective ladder.

Returns JSON:
  {
    "unavailable": ["model/name", ...],
    "warnings": ["msg", ...],
    "health": { ... }   // full provider_health output
  }
"""
import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent
LOG_FILE = WORKSPACE / 'guardian.log'

# Import provider_health from same directory
sys.path.insert(0, str(WORKSPACE))
from provider_health import run_health_check


def log_alert(msg, level='WARN'):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = f'{ts} [{level}] [expiry_alert] {msg}'
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(line + '\n')
    except Exception:
        pass
    # Also print to stderr so guardian_cycle can see it
    print(line, file=sys.stderr)


def run_expiry_alert():
    health = run_health_check()
    unavailable = []
    warnings = []

    for p in health['providers']:
        alerts = p.get('alerts', [])
        model = p['model']
        provider = p['provider']

        for alert in alerts:
            if alert.startswith('minimax_trial_expiry_warning'):
                days_str = alert.split(':')[-1].rstrip('d')
                msg = (
                    f'MiniMax trial expires in {days_str} days '
                    f'(2026-03-30) — renew or switch before cutover'
                )
                warnings.append(msg)
                log_alert(msg, 'WARN')

            elif alert == 'minimax_trial_expired':
                msg = 'MiniMax trial has EXPIRED — removing from effective ladder'
                warnings.append(msg)
                log_alert(msg, 'ERROR')

            elif alert.startswith('token_expired'):
                msg = f'{provider} token EXPIRED — {model} unavailable'
                warnings.append(msg)
                log_alert(msg, 'ERROR')

            elif alert.startswith('expiry_warning'):
                msg = f'{provider} token expiring soon — {p["reason"]}'
                warnings.append(msg)
                log_alert(msg, 'WARN')

            elif alert.startswith('auto_refresh_needed'):
                msg = f'{provider} OAuth token needs refresh (plugin will handle) — {p["reason"]}'
                warnings.append(msg)
                log_alert(msg, 'INFO')

        if not p['healthy']:
            unavailable.append(model)

    return {
        'unavailable': unavailable,
        'warnings': warnings,
        'health': health,
    }


if __name__ == '__main__':
    result = run_expiry_alert()
    print(json.dumps(result, indent=2))
