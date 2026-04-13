#!/usr/bin/env python3
"""
guardian_cycle.py — One autonomous model-guardian cycle.

Run on a cron/LaunchAgent every 5 minutes.
Checks budget usage → decides whether to switch primary model → patches config.

Decision logic:
  < 70%  → stay on current (or restore primary if budget reset)
  70-84% → warn only, no switch yet
  85-94% → switch to next cheaper model in ladder
  95%+   → switch to local-only (ollama)
  reset  → restore original primary

Exit codes:
  0 = ok (action taken or no action needed)
  1 = error
"""
import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent
BUDGET_TRACKER = WORKSPACE / 'budget_tracker.py'
MODEL_SWITCHER = WORKSPACE / 'model_switcher.py'
TASK_ROUTER = WORKSPACE / 'task_router.py'
REGISTRY = WORKSPACE / 'model_registry.json'
STATE_FILE = WORKSPACE / 'state.json'
LOG_FILE = WORKSPACE / 'guardian.log'
EXPIRY_ALERT = WORKSPACE / 'expiry_alert.py'

# Full switch ladder — must match model_switcher.py SWITCH_LADDER
SWITCH_LADDER = [
    'anthropic/claude-sonnet-4-6',
    'openai-codex/gpt-5.4',
    'ollama/qwen2.5:7b',
    'ollama/qwen2.5:3b',
    'ollama/llama3.2:3b',
    'ollama/qwen2.5:1.5b-instruct-q4_K_M',
]

LOCAL_ONLY_INDEX = 2  # ollama/qwen2.5:7b is first local fallback

THRESHOLDS = {
    'warn': 70,
    'switch': 85,
    'critical': 95,
}

TODAY = date.today().isoformat()


def log(msg, level='INFO'):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = f'{ts} [{level}] {msg}'
    print(line, flush=True)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(line + '\n')
    except Exception:
        pass


def run_script(script, args=None):
    cmd = [sys.executable, str(script)] + (args or [])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f'{script.name} failed: {res.stderr.strip()}')
    return json.loads(res.stdout.strip())


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state):
    tmp = STATE_FILE.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(state, indent=2) + '\n')
    tmp.replace(STATE_FILE)


def get_effective_ladder(unavailable_models):
    """Return SWITCH_LADDER minus any unavailable/expired models."""
    effective = [m for m in SWITCH_LADDER if m not in unavailable_models]
    return effective


def next_ladder_model(current_model, effective_ladder, min_index=1):
    """Return the next cheaper model in the effective ladder, at least min_index."""
    try:
        idx = effective_ladder.index(current_model)
    except ValueError:
        idx = 0
    next_idx = max(idx + 1, min_index)
    if next_idx >= len(effective_ladder):
        next_idx = len(effective_ladder) - 1
    return effective_ladder[next_idx]


def first_local_index(effective_ladder):
    """Return index of first ollama model in the effective ladder."""
    for i, m in enumerate(effective_ladder):
        if m.startswith('ollama/'):
            return i
    return len(effective_ladder) - 1


def run_expiry_checks():
    """Run expiry_alert.py, return (unavailable_models, warnings)."""
    if not EXPIRY_ALERT.exists():
        return [], []
    try:
        cmd = [sys.executable, str(EXPIRY_ALERT)]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # Expiry alert logs to stderr — print those lines
        for line in (res.stderr or '').strip().splitlines():
            if line:
                print(line, flush=True)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout.strip())
            return data.get('unavailable', []), data.get('warnings', [])
    except Exception as e:
        log(f'expiry_alert failed (non-fatal): {e}', 'WARN')
    return [], []


def run_cycle():
    state = load_state()
    last_date = state.get('last_cycle_date')

    # ── Step 1: Provider health / expiry checks ────────────────────────────
    unavailable, expiry_warnings = run_expiry_checks()
    effective_ladder = get_effective_ladder(unavailable)

    if unavailable:
        log(f'Unavailable providers (skipping): {unavailable}', 'WARN')
    for w in expiry_warnings:
        # Already logged by expiry_alert, just surface in cycle log
        pass

    local_idx = first_local_index(effective_ladder)
    log(
        f'Effective ladder: {len(effective_ladder)} models '
        f'(skipped {len(unavailable)}), '
        f'first_local_idx={local_idx}'
    )

    # ── Step 2: Budget usage ───────────────────────────────────────────────
    try:
        usage = run_script(BUDGET_TRACKER)
    except Exception as e:
        log(f'budget_tracker failed: {e}', 'ERROR')
        sys.exit(1)

    pct = float(usage.get('budget_pct', 0))
    tokens = int(usage.get('estimated_tokens_used', 0))
    source = usage.get('source', 'unknown')

    log(f'budget={pct}% tokens={tokens} source={source}')

    # ── Step 3: Current model status ──────────────────────────────────────
    try:
        status = run_script(MODEL_SWITCHER, ['--status'])
    except Exception as e:
        log(f'model_switcher status failed: {e}', 'ERROR')
        sys.exit(1)

    current = status.get('current_primary', SWITCH_LADDER[0])
    original = status.get('original_primary', SWITCH_LADDER[0])
    ladder_pos = int(status.get('ladder_position', 0))

    # If current primary is unavailable, force a step down immediately
    if current in unavailable:
        if effective_ladder:
            forced_target = effective_ladder[0]
            log(
                f'Current primary {current} is unavailable — '
                f'force-switching to {forced_target}',
                'WARN'
            )
            try:
                result = run_script(MODEL_SWITCHER, ['--to', forced_target, '--reason', 'primary_unavailable'])
                log(f'Force-switch result: {json.dumps(result)}')
                current = forced_target
                ladder_pos = SWITCH_LADDER.index(forced_target) if forced_target in SWITCH_LADDER else 0
            except Exception as e:
                log(f'force-switch failed: {e}', 'ERROR')

    # ── Step 4: Daily reset check ─────────────────────────────────────────
    if last_date and last_date != TODAY and ladder_pos > 0:
        log(f'New day detected — restoring primary {original}')
        try:
            result = run_script(MODEL_SWITCHER, ['--restore'])
            log(f'Restored: {json.dumps(result)}')
            state['last_cycle_date'] = TODAY
            state['last_action'] = 'restored'
            state['last_cycle_at'] = datetime.now().isoformat()
            state['effective_ladder'] = effective_ladder
            save_state(state)
        except Exception as e:
            log(f'restore failed: {e}', 'ERROR')
        return

    state['last_cycle_date'] = TODAY
    state['last_pct'] = pct
    state['last_tokens'] = tokens
    state['last_cycle_at'] = datetime.now().isoformat()
    state['current_primary'] = current
    state['effective_ladder'] = effective_ladder
    state['unavailable_providers'] = unavailable

    # ── Step 5: Decision ──────────────────────────────────────────────────
    if pct >= THRESHOLDS['critical']:
        # Emergency: switch to local-only
        target = effective_ladder[local_idx] if local_idx < len(effective_ladder) else effective_ladder[-1]
        current_eff_idx = effective_ladder.index(current) if current in effective_ladder else 0
        if current_eff_idx < local_idx:
            log(f'CRITICAL {pct}% — switching to local-only: {target}', 'WARN')
            result = run_script(MODEL_SWITCHER, ['--to', target, '--reason', f'critical budget {pct}%'])
            log(f'Switch result: {json.dumps(result)}')
            state['last_action'] = 'critical_switch'
        else:
            log(f'CRITICAL {pct}% — already on local model {current}, no further switch needed')
            state['last_action'] = 'critical_already_local'

    elif pct >= THRESHOLDS['switch']:
        # Step down one rung on the effective ladder
        target = next_ladder_model(current, effective_ladder)
        if target != current:
            log(f'SWITCH threshold {pct}% — stepping down: {current} → {target}', 'WARN')
            result = run_script(MODEL_SWITCHER, ['--to', target, '--reason', f'budget threshold {pct}%'])
            log(f'Switch result: {json.dumps(result)}')
            state['last_action'] = 'step_down'
        else:
            log(f'SWITCH threshold {pct}% — already at ladder bottom: {current}')
            state['last_action'] = 'at_bottom'

    elif pct >= THRESHOLDS['warn']:
        log(f'WARN threshold {pct}% — monitoring, no switch yet', 'WARN')
        state['last_action'] = 'warn_only'

    else:
        log(
            f'OK {pct}% — no action needed '
            f'| alerts={len(expiry_warnings)} skipped={len(unavailable)}'
        )
        state['last_action'] = 'ok'

    save_state(state)


if __name__ == '__main__':
    run_cycle()
