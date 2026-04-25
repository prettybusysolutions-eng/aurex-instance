# Safe Control Plane

This directory contains a lightweight control-plane stack for uptime monitoring, wallet/network observation, and documentation retrieval.

## Services
- `uptime-kuma` — web UI for uptime checks at http://localhost:3001
- `playwright-runner` — headless browser sandbox for approved documentation retrieval
- `wallet-watch` — gas fee and balance observer for configured EVM networks/wallets
- `summary-cron` — daily summary writer for official public sources

## Start everything

```bash
cd /Users/marcuscoarchitect/.openclaw/workspace/control-plane
docker compose up -d
```

## Stop everything

```bash
docker compose down
```

## Retrieve documentation manually

```bash
cd /Users/marcuscoarchitect/.openclaw/workspace/control-plane/playwright
npm install
node retrieve_docs.js https://docs.io.net
```

## Configure wallets and networks
- Edit `wallet-watch/networks.json`
- Edit `wallet-watch/wallets.json`

## Configure summary sources
- Edit `summary/sources.json`

## Notes
- This control plane is for safe monitoring, research, and approved browser workflows.
- It does not include autonomous reward farming, mass account automation, or claim exploitation.
- Transaction success-rate tracking is left as a per-network extension because explorer/API surfaces differ.
