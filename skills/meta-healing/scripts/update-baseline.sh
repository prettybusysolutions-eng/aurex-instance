#!/usr/bin/env bash
set -euo pipefail
out="$HOME/.openclaw/workspace/state/meta-healing/runtime-fingerprint.json"
watchdog_plist="$HOME/Library/LaunchAgents/com.openclaw.meta-healing.watchdog.plist"
mkdir -p "$(dirname "$out")"
watchdog_hash=""
watchdog_present=false
if [[ -f "$watchdog_plist" ]]; then
  watchdog_hash="$(shasum -a 256 "$watchdog_plist" | awk '{print $1}')"
  watchdog_present=true
fi
{
  printf '{\n'
  printf '  "updatedAt": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '  "openclawVersion": "%s",\n' "$(openclaw --version 2>/dev/null || echo unknown)"
  printf '  "configSha256": "%s",\n' "$(shasum -a 256 "$HOME/.openclaw/openclaw.json" | awk '{print $1}')"
  printf '  "watchdogPlistPresent": %s,\n' "$watchdog_present"
  printf '  "watchdogPlistPath": "%s",\n' "$watchdog_plist"
  printf '  "watchdogPlistSha256": "%s"\n' "$watchdog_hash"
  printf '}\n'
} > "$out"
printf '%s\n' "$out"
