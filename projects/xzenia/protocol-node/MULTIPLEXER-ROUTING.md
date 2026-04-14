# Multiplexer Routing

Last updated: 2026-04-14 00:19 EDT
Status: READY

## Shadow router
- local port: `127.0.0.1:8788`
- `/stripe/*` proxies to billing listener on `127.0.0.1:8787`
- `/.well-known/mcp` served locally by the multiplexer
- `/mcp/v1/*` served locally by the bridge layer

## Public shape after tunnel cutover
If the tunnel target is changed from `127.0.0.1:8787` to `127.0.0.1:8788`, then:
- `[TUNNEL-URL]/stripe/webhook` -> billing listener
- `[TUNNEL-URL]/.well-known/mcp` -> MCP manifest
- `[TUNNEL-URL]/mcp/v1/health` -> MCP health
- `[TUNNEL-URL]/mcp/v1/capabilities` -> MCP capabilities
- `[TUNNEL-URL]/mcp/v1/translate` -> MCP translate
