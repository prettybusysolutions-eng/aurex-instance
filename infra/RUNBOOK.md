# RUNBOOK

## One-command bootstrap
`bash scripts/bootstrap-infra.sh`

## Manual checks
- Gateway: `openclaw gateway status`
- Node: `openclaw node status`
- Browser relay: `openclaw browser status --profile chrome`
- Cron: `openclaw cron status`

## Fast recovery
1. Restart node host: `openclaw node restart`
2. Recheck status with `bash scripts/healthcheck.sh`
3. If browser blocked: attach Chrome relay tab (extension badge ON)
4. If pairing blocked: run `openclaw pairing list` / `openclaw devices list` and approve pending request

## Alert conditions
- Node host disconnected
- Browser relay unavailable for tasks requiring automation
- Cron disabled
- Gateway RPC probe failure
