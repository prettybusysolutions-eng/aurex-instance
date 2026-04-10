#!/usr/bin/env python3
"""
provider_health.py — Check auth validity for each provider in the fallback ladder.
Fast checks only (no LLM calls): token expiry, profile existence.

Usage:
  python3 provider_health.py
  python3 provider_health.py --json   (default: JSON to stdout)
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

AUTH_PROFILES = Path.home() / '.openclaw' / 'agents' / 'main' / 'agent' / 'auth-profiles.json'

# Full switch ladder — keep in sync with model_switcher.py
SWITCH_LADDER = [
    ('anthropic/claude-sonnet-4-6',                    'anthropic',           'anthropic:manual'),
    ('openai-codex/gpt-5.4',                           'openai-codex',        'openai-codex:default'),
    ('google-gemini-cli/gemini-3.1-pro-preview',       'google-gemini-cli',   'google-gemini-cli:kammsuitside@gmail.com'),
    ('minimax-portal/MiniMax-M2.5',                    'minimax-portal',      'minimax-portal:default'),
    ('qwen-portal/coder-model',                        'qwen-portal',         'qwen-portal:default'),
    ('github-copilot/gpt-4.1',                        'github-copilot',      'github-copilot:github'),
    ('ollama/qwen2.5:7b',                              'ollama',              None),
    ('ollama/qwen2.5:3b',                              'ollama',              None),
    ('ollama/llama3.2:3b',                             'ollama',              None),
    ('ollama/qwen2.5:1.5b-instruct-q4_K_M',           'ollama',              None),
]

# Providers whose OAuth tokens are short-lived but auto-refresh via the plugin
AUTO_REFRESH_PROVIDERS = {'google-gemini-cli', 'qwen-portal', 'openai-codex'}

# MiniMax trial expiry (business/plan level, separate from token expiry)
MINIMAX_TRIAL_EXPIRY = datetime(2026, 3, 30, tzinfo=timezone.utc)

# Warning threshold: alert if a non-auto-refresh token expires within this many days
EXPIRY_WARN_DAYS = 7


def load_profiles():
    if not AUTH_PROFILES.exists():
        return {}
    try:
        data = json.loads(AUTH_PROFILES.read_text())
        return data.get('profiles', {})
    except Exception as e:
        return {}


def check_provider(model, provider, profile_key, profiles, now):
    result = {
        'model': model,
        'provider': provider,
        'profile_key': profile_key,
        'healthy': True,
        'reason': 'ok',
        'alerts': [],
    }

    # Ollama: no auth needed
    if provider == 'ollama':
        result['reason'] = 'local — no auth required'
        return result

    # Profile must exist
    if profile_key and profile_key not in profiles:
        result['healthy'] = False
        result['reason'] = f'profile "{profile_key}" not found in auth-profiles.json'
        return result

    profile = profiles.get(profile_key, {}) if profile_key else {}
    expires_ms = profile.get('expires')
    token_type = profile.get('type', 'unknown')

    # Check token expiry
    if expires_ms is not None:
        expires_dt = datetime.fromtimestamp(expires_ms / 1000, tz=timezone.utc)
        delta = expires_dt - now

        if delta.total_seconds() < 0:
            # Already expired
            if provider in AUTO_REFRESH_PROVIDERS:
                result['healthy'] = True
                result['reason'] = (
                    f'OAuth token expired {abs(int(delta.total_seconds() // 60))}m ago '
                    f'— auto-refreshes via plugin'
                )
                result['alerts'].append(f'auto_refresh_needed:{provider}')
            else:
                result['healthy'] = False
                result['reason'] = f'token expired at {expires_dt.isoformat()} ({abs(int(delta.total_seconds() // 3600))}h ago)'
                result['alerts'].append(f'token_expired:{provider}')
        elif delta.days < EXPIRY_WARN_DAYS:
            if provider in AUTO_REFRESH_PROVIDERS:
                result['healthy'] = True
                result['reason'] = (
                    f'OAuth token expires {expires_dt.date().isoformat()} '
                    f'({delta.days}d) — auto-refreshes via plugin'
                )
            else:
                result['healthy'] = True  # Still valid, just warn
                result['reason'] = f'token expires soon: {expires_dt.date().isoformat()} ({delta.days}d)'
                result['alerts'].append(f'expiry_warning:{provider}:{delta.days}d')
        else:
            result['reason'] = f'token valid until {expires_dt.date().isoformat()} ({delta.days}d)'
    else:
        # No expiry field (e.g. Anthropic API key, GitHub token)
        result['reason'] = f'{token_type} token — no expiry'

    # MiniMax: check business trial expiry separately
    if provider == 'minimax-portal':
        trial_delta = MINIMAX_TRIAL_EXPIRY - now
        if trial_delta.total_seconds() < 0:
            result['healthy'] = False
            result['alerts'].append('minimax_trial_expired')
            result['reason'] += f' | TRIAL EXPIRED {MINIMAX_TRIAL_EXPIRY.date().isoformat()}'
        elif trial_delta.days < EXPIRY_WARN_DAYS:
            result['alerts'].append(f'minimax_trial_expiry_warning:{trial_delta.days}d')
            result['reason'] += f' | TRIAL EXPIRES {MINIMAX_TRIAL_EXPIRY.date().isoformat()} ({trial_delta.days}d)'
        else:
            result['reason'] += f' | trial until {MINIMAX_TRIAL_EXPIRY.date().isoformat()} ({trial_delta.days}d)'

    return result


def run_health_check():
    profiles = load_profiles()
    now = datetime.now(tz=timezone.utc)
    results = []

    for model, provider, profile_key in SWITCH_LADDER:
        r = check_provider(model, provider, profile_key, profiles, now)
        results.append(r)

    return {
        'checked_at': now.isoformat(),
        'providers': results,
        'unhealthy': [r['model'] for r in results if not r['healthy']],
        'alerts': [a for r in results for a in r.get('alerts', [])],
    }


if __name__ == '__main__':
    result = run_health_check()
    print(json.dumps(result, indent=2))
