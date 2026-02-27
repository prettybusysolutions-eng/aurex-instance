# GUARDRAILS

## Auto-Allowed
- Create/update files in workspace
- Run non-destructive shell commands
- Manage cron jobs
- Commit local git changes
- Perform web research (search/fetch)

## Require Human Confirmation
- Any irreversible destructive action outside workspace
- Public/external posting not explicitly requested
- New credential provisioning requiring interactive auth

## Safety Defaults
- Prefer idempotent scripts
- Log every check in `data/logs/`
- Fail closed, then escalate with exact unblock step
