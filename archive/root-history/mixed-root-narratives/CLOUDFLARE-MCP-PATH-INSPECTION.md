# Cloudflare MCP Path Inspection

Last updated: 2026-04-14 00:13 EDT
Status: VERIFIED_SHAPE

## Verified local shape
- active tunnel process: `cloudflared tunnel --url http://127.0.0.1:8787`
- local listener on `127.0.0.1:8787`: confirmed

## Path implication
Whatever the current Cloudflare tunnel public URL is, the MCP bridge path should be:
- `[TUNNEL-URL]/.well-known/mcp`
- `[TUNNEL-URL]/mcp/v1/health`
- `[TUNNEL-URL]/mcp/v1/capabilities`
- `[TUNNEL-URL]/mcp/v1/translate`

## Truth boundary
The tunnel host itself was not printed by the running local process output in this check, so the exact public hostname still needs one direct tunnel URL observation or Cloudflare dashboard check.
