#!/usr/bin/env bash
set -euo pipefail
state_dir="$HOME/.openclaw/workspace/state/meta-healing"
mkdir -p "$state_dir"
current="$state_dir/current-openclaw.json"
latest_diff="$state_dir/latest-config.diff"
latest_summary="$state_dir/latest-config.summary"
cp "$HOME/.openclaw/openclaw.json" "$current.new"
if [[ -f "$current" ]]; then
  if ! diff -q "$current" "$current.new" >/dev/null 2>&1; then
    old_sha="$(shasum -a 256 "$current" | awk '{print $1}')"
    new_sha="$(shasum -a 256 "$current.new" | awk '{print $1}')"
    {
      echo "STATE: CHANGED"
      echo "OLD_SHA256: $old_sha"
      echo "NEW_SHA256: $new_sha"
      echo "DETAIL: content diff suppressed to avoid leaking sensitive configuration material"
    } > "$latest_summary"
    rm -f "$latest_diff"
    mv "$current.new" "$current"
    echo "DRIFT_DETECTED"
    echo "$latest_summary"
    exit 0
  fi
  rm -f "$current.new"
  rm -f "$latest_diff" "$latest_summary"
  echo "NO_DRIFT"
  exit 0
fi
mv "$current.new" "$current"
rm -f "$latest_diff" "$latest_summary"
echo "BASELINE_CREATED"
