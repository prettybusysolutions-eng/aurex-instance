#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia"
LOG_DIR="$ROOT/recovery/logs"
mkdir -p "$LOG_DIR"
TS="$(date +%Y%m%d-%H%M%S)"
LOG="$LOG_DIR/tier1-recovery-$TS.log"

{
  echo "[$(date -Iseconds)] tier1 recovery start"
  python3 "$ROOT/tier1/boot_trigger.py"
  echo "---"
  python3 "$ROOT/tier1/health_loop.py"
  echo "[$(date -Iseconds)] tier1 recovery end"
} >> "$LOG" 2>&1

echo "$LOG"
