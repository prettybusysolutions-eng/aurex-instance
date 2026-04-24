# Cloudflare Tunnel Cutover Command

Current target:
- `http://127.0.0.1:8787`

New target:
- `http://127.0.0.1:8788`

## Exact cutover command
```bash
pkill -f 'cloudflared tunnel --url http://127.0.0.1:8787' && cloudflared tunnel --url http://127.0.0.1:8788
```

## Notes
- this will move the public tunnel entrypoint from the billing listener to the shadow multiplexer
- billing traffic will continue via `/stripe/webhook` through the multiplexer proxy
- machine traffic will become available at `/mcp/v1/*` and `/.well-known/mcp`
