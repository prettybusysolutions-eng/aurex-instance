#!/usr/bin/env python3
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
CLASSIFIER = WORKSPACE / 'projects/xzenia/defects/defect_classifier.py'
WRITER = WORKSPACE / 'projects/xzenia/defects/registry_writer.py'
REPORT = WORKSPACE / 'projects/xzenia/csmr/reports/defect-detection-report.json'


def main():
    payload = json.loads(sys.stdin.read())
    payload.setdefault('timestamp', datetime.now().astimezone().isoformat())
    payload.setdefault('source', 'exception')
    payload.setdefault('defect_id', f"auto-defect-{int(time.time())}")
    classified = subprocess.run(['python3', str(CLASSIFIER)], input=json.dumps(payload), text=True, capture_output=True)
    if classified.returncode != 0:
        raise SystemExit(classified.stderr)
    classified_payload = json.loads(classified.stdout)
    written = subprocess.run(['python3', str(WRITER)], input=json.dumps(classified_payload), text=True, capture_output=True)
    if written.returncode != 0:
        raise SystemExit(written.stderr)
    report = {
        'status': 'done and verified',
        'classified': classified_payload,
        'registry_write': json.loads(written.stdout)
    }
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
