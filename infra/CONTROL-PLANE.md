# CONTROL-PLANE

## Objective
Operate Xzenia in autonomous mode with minimal operator interruption.

## Trust Boundaries
- Autonomous: local file ops, shell automation, cron orchestration, research, reporting.
- Human-gated: browser relay tab attach, cryptographic pairing approvals, external account sign-ins requiring interactive consent.

## Execution Model
1. Bootstrap infra health checks and runbooks.
2. Run periodic health checks.
3. Auto-remediate safe failures.
4. Escalate only when blocked by human-gated actions.

## Escalation Policy
Escalate only for:
- Browser relay unattached when browser automation is required
- Pairing/token approval required
- Credential missing for external services
- Repeated failure after 3 auto-retry attempts

## Reporting Policy
- Daily heartbeat: full operational summary.
- Exception alerts: only for actionable blockers.
