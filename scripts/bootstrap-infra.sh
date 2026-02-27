#!/usr/bin/env bash
set -euo pipefail

cd /Users/marcuscoarchitect/.openclaw/workspace
mkdir -p infra scripts data/logs data/prospects data/clients data/campaigns data/financial backups memory skills/genesis-v2 skills/daily-heartbeat

openclaw gateway status >/dev/null 2>&1 || openclaw gateway start

# Node host service install/restart is idempotent
openclaw node install >/dev/null 2>&1 || true
openclaw node restart >/dev/null 2>&1 || true

# Ensure daily heartbeat exists (if duplicate add fails harmlessly)
openclaw cron add \
  --name "daily-heartbeat" \
  --every 24h \
  --agent main \
  --session isolated \
  --announce \
  --channel telegram \
  --to 6620375090 \
  --message "Generate and send the daily heartbeat report for Aurex now. Use the exact template in skills/daily-heartbeat/SKILL.md. Pull current counts from workspace data files if present; if missing, report 0 and note missing telemetry." >/dev/null 2>&1 || true

bash scripts/healthcheck.sh
