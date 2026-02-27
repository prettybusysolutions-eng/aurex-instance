#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/marcuscoarchitect/.openclaw/workspace"
LOG_DIR="$ROOT/data/logs"
mkdir -p "$LOG_DIR"
TS="$(date +"%Y-%m-%d_%H-%M-%S")"
OUT="$LOG_DIR/healthcheck_${TS}.log"

status_cmd() {
  local name="$1"
  local cmd="$2"
  echo "\n=== $name ===" | tee -a "$OUT"
  if eval "$cmd" >>"$OUT" 2>&1; then
    echo "[PASS] $name" | tee -a "$OUT"
  else
    echo "[FAIL] $name" | tee -a "$OUT"
    return 1
  fi
}

FAIL=0
status_cmd "gateway" "openclaw gateway status" || FAIL=1
status_cmd "node" "openclaw node status" || FAIL=1
status_cmd "cron" "openclaw cron status" || FAIL=1
status_cmd "browser(chrome profile)" "openclaw browser status --profile chrome" || FAIL=1

if [[ "$FAIL" -eq 0 ]]; then
  echo "\nOVERALL: PASS" | tee -a "$OUT"
else
  echo "\nOVERALL: FAIL" | tee -a "$OUT"
fi

echo "$OUT"
exit "$FAIL"
