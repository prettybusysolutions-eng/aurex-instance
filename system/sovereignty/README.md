# Sovereignty Sprint

This directory defines the autonomous control plane for EC2 AI infrastructure.

## Waves
1. Policy-as-code baseline
2. Observability + SLO alarms
3. Autonomous patch/remediation schedules
4. Backup + recovery automation

## Applied assets
- `policies/baseline.yaml`
- `scripts/sovereignty_apply.sh`
- `scripts/sovereignty_score.py`

## Runtime targets
Region: `us-east-2`
Managed instances are discovered dynamically via SSM.
