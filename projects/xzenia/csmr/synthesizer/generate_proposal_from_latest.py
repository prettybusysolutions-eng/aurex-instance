#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
LEGACY_ATTRIBUTION = WORKSPACE / 'projects/xzenia/csmr/attribution/derive_causal_finding_v2.py'
ATTRIBUTION = WORKSPACE / 'projects/xzenia/csmr/attribution/derive_causal_finding_v3.py'
SYNTH = WORKSPACE / 'projects/xzenia/csmr/synthesizer/generate_proposal.py'
TMP_FINDING = Path('/tmp/csmr-latest-finding.json')
COMPARE_REPORT = WORKSPACE / 'projects/xzenia/csmr/reports/frontier-intelligence-compare.json'


def main():
    legacy = subprocess.run(['python3', str(LEGACY_ATTRIBUTION)], capture_output=True, text=True, check=True)
    run = subprocess.run(['python3', str(ATTRIBUTION)], capture_output=True, text=True, check=True)
    COMPARE_REPORT.write_text(json.dumps({'legacy': json.loads(legacy.stdout), 'frontier_intelligence': json.loads(run.stdout)}, indent=2) + '\n')
    TMP_FINDING.write_text(run.stdout)
    proposal = subprocess.run(['python3', str(SYNTH), str(TMP_FINDING)], capture_output=True, text=True, check=True)
    print(proposal.stdout.strip())


if __name__ == '__main__':
    main()
