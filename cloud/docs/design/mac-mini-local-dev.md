# Mac Mini Local Dev Setup

How to run the full E2E flow locally: Vite dev server → Mac Mini Agent → Cloudflare Tunnel.

## Prerequisites

1. **Local Postgres** with migrations applied (`cd cloud && bunx drizzle-kit migrate`)
2. **Mac Mini Agent** running locally (`cd cloud/claws/mini-agent && bun run dev`)
3. **Cloudflare Tunnel** configured for the dev machine

## Environment Variables

Add to your `.dev.vars` (or `.env`):

```
DEPLOYMENT_TARGET=mac-mini
```

All other env vars remain the same. When `DEPLOYMENT_TARGET` is unset or `"cloudflare"`, the existing Cloudflare container deployment path is used.

## Database Seed

Insert your dev machine into the `mac_minis` table:

```bash
psql $DATABASE_URL -f cloud/scripts/dev/seed-mac-mini.sql
```

This creates a row with:
- `hostname`: `dev-macbook`
- `agent_url`: `http://localhost:4111` (the Mini Agent's default port)
- `tunnel_hostname_suffix`: `claws.mirascope.dev`

## Flow

1. User signs in at `localhost:5173`
2. Creates a claw → `MacMiniDeploymentService` calls the local Mini Agent
3. Mini Agent provisions the claw (port allocation, launchd, tunnel)
4. Claw row gets `mini_id`, `mini_port`, `tunnel_hostname`
5. Chat via WS proxy: browser → `localhost:5173/api/ws/claws/:org/:claw` → `wss://{tunnelHostname}`
6. Gateway button links to `https://{tunnelHostname}` directly

## Backward Compatibility

- `DEPLOYMENT_TARGET=cloudflare` (default) → existing Cloudflare Workers for Platforms path
- `MOCK_DEPLOYMENT=true` → mock deployment (no real infra), unchanged
- `DEPLOYMENT_TARGET=mac-mini` → Mac Mini Agent path

The WS proxy is deployment-target-agnostic: it checks `tunnel_hostname` on the claw row. If set, it routes to the tunnel; otherwise, it routes through the dispatch worker.
