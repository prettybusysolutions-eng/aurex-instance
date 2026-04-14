#!/usr/bin/env python3
import json
import time
from pathlib import Path

STATS_PATH = Path('/Users/marcuscoarchitect/.openclaw/workspace/data_alpha/market_pressure_stats.json')
WINDOW_SECONDS = 60 * 60


def _load():
    if not STATS_PATH.exists():
        return {'events': []}
    try:
        return json.loads(STATS_PATH.read_text())
    except Exception:
        return {'events': []}


def _save(data):
    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATS_PATH.write_text(json.dumps(data, indent=2) + '\n')


def _prune(events, now):
    cutoff = now - WINDOW_SECONDS
    return [e for e in events if float(e.get('ts', 0)) >= cutoff]


def record_event(kind: str):
    now = time.time()
    data = _load()
    events = _prune(data.get('events', []), now)
    events.append({'ts': now, 'kind': kind})
    data['events'] = events
    _save(data)


def pressure_index() -> str:
    now = time.time()
    data = _load()
    events = _prune(data.get('events', []), now)
    bounces = sum(1 for e in events if e.get('kind') == 'bounce')
    settlements = sum(1 for e in events if e.get('kind') == 'settlement')
    if bounces == 0 and settlements == 0:
        return '0.0'
    denom = settlements if settlements > 0 else 1
    return f"{bounces / denom:.1f}"
