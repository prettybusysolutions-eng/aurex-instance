#!/bin/zsh
set -euo pipefail
ROOT="/Users/marcuscoarchitect/.openclaw/workspace"
START=$(python3 - <<'PY'
import time
print(time.time())
PY
)
$ROOT/skills/mac-execution-bridge/scripts/ui-action.sh activate "Google Chrome"
FRONT=$($ROOT/skills/mac-execution-bridge/scripts/window-state.sh)
$ROOT/skills/mac-execution-bridge/scripts/ui-action.sh open-url "Google Chrome" "https://pocketoption.com/en/cabinet/demo-quick-high-low/"
VERIFY=$($ROOT/skills/mac-execution-bridge/scripts/verify-browser-state.sh "https://pocketoption.com/en/cabinet/demo-quick-high-low/" "The Most Innovative Trading Platform")
CAP=$($ROOT/skills/mac-execution-bridge/scripts/capture-screen.sh "$ROOT/projects/xzenia/state/hybrid-benchmark-capture.png")
IMG=$($ROOT/skills/mac-execution-bridge/scripts/image-info.sh "$ROOT/projects/xzenia/state/hybrid-benchmark-capture.png")
END=$(python3 - <<'PY'
import time
print(time.time())
PY
)
python3 - <<PY
import json
from pathlib import Path
start=float("$START")
end=float("$END")
report={
  "name": "hybrid-execution-benchmark-report",
  "target": "Google Chrome / Pocket Option demo surface",
  "runtimeSeconds": round(end-start, 3),
  "frontState": """$FRONT""",
  "verification": """$VERIFY""",
  "capturePath": "$ROOT/projects/xzenia/state/hybrid-benchmark-capture.png",
  "imageInfo": """$IMG""",
  "success": True
}
Path("$ROOT/projects/xzenia/state/hybrid-benchmark-report.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2))
PY
