# Machine Path Watch

Last updated: 2026-04-14 00:51 EDT
Status: ACTIVE

## Watch surfaces
- `/.well-known/mcp`
- `/mcp/v1/health`
- `/mcp/v1/capabilities`
- `/mcp/v1/translate`

## Immediate alert rule
Break silence immediately if:
- first external hit lands on `/mcp/v1/capabilities`
- first non-empty `X-Webhook-Signature` appears on a machine path
- any live-settlement mode request path is observed after future x402 activation

## Local artifact
- `projects/xzenia/protocol-node/machine-pings.jsonl`
