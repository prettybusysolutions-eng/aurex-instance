#!/bin/zsh
set -euo pipefail
LABEL="com.xzenia.protocol-multiplexer"
PLIST="/Users/marcuscoarchitect/Library/LaunchAgents/com.xzenia.protocol-multiplexer.plist"
PORT_PID="$(lsof -ti:8788 -sTCP:LISTEN 2>/dev/null || true)"
STATUS_LINE="$(launchctl list | grep "$LABEL" || true)"
if [[ -n "$PORT_PID" ]] && [[ "$STATUS_LINE" != *$'\t0\t'* ]]; then
  kill -9 "$PORT_PID" || true
  launchctl unload "$PLIST" >/dev/null 2>&1 || true
  launchctl load "$PLIST"
fi
