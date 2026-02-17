# Claws — Mac Mini Deployment Architecture

## Overview

Claws can be deployed to either **Cloudflare Containers** (default) or **Mac Mini** infrastructure. The deployment target is controlled by the `DEPLOYMENT_TARGET` setting (`"cloudflare"` or `"mac-mini"`).

## Mac Mini Architecture

```
Browser → Vite dev server → WS Proxy → Cloudflare Tunnel → Mac Mini → OpenClaw Gateway
                                ↑
                          /api/ws/claws/:org/:claw
```

### Components

- **`mac-mini-fleet.ts`** — Fleet management: finds available Minis with capacity, allocates ports, makes HTTP calls to the Mini Agent API.
- **`mac-mini.ts`** — `ClawDeploymentService` implementation for Mac Mini. Provisions claws by calling the agent, creates R2 buckets, stores `miniId`/`miniPort`/`tunnelHostname` on the claw row.
- **`claws-ws-proxy.ts`** — Server-side WebSocket proxy. For Mac Mini claws (detected by `tunnelHostname` on the claw row), connects via Cloudflare Tunnel hostname instead of the dispatch worker.
- **`mac_minis` table** — Fleet inventory: hostname, agent URL, tunnel suffix, port range, capacity.
- **`claws` table** — Extended with `mini_id`, `mini_port`, `tunnel_hostname` columns.

### Provisioning Flow

1. User clicks "+ New Claw" → `createClawHandler` runs
2. `MacMiniDeploymentService.provision()`:
   - `fleet.findAvailableMini()` — picks an online Mini with capacity, allocates a port
   - `fleet.callAgent(POST /claws, { clawId, port })` — tells the agent to start an OpenClaw gateway on that port
   - Creates R2 bucket for backups
   - Stores `miniId`, `miniPort`, `tunnelHostname` on the claw row
3. Claw status → `"provisioning"` → `"active"` (after warmup)

### Chat Flow

1. Browser opens WebSocket to `/api/ws/claws/:orgSlug/:clawSlug`
2. WS proxy authenticates user, resolves claw, decrypts gateway token
3. If claw has `tunnelHostname` → connects to `wss://{tunnelHostname}` via Cloudflare Tunnel
4. Performs OpenClaw connect handshake (challenge → auth)
5. Relays messages bidirectionally

### Gateway Button

The "OpenClaw Gateway" button in the frontend uses `tunnelHostname` from the API response. If present, it links to `https://{tunnelHostname}` directly.

## Local Development Setup

### Prerequisites

1. **Local Postgres** with the Drizzle schema migrated
2. **Mac Mini agent** running (or a local mock) — the agent API that provisions OpenClaw gateways
3. **Cloudflare Tunnel** configured to route `claw-{id}.claws.mirascope.dev` → the Mini

### Steps

1. **Seed the `mac_minis` table:**
   ```bash
   psql $DATABASE_URL -f cloud/scripts/seed-dev-mini.sql
   ```
   Edit the SQL to point `agent_url` at your actual agent.

2. **Set `DEPLOYMENT_TARGET`** in your local environment (`.dev.vars` or env):
   ```
   DEPLOYMENT_TARGET=mac-mini
   ```

3. **Start the dev server:**
   ```bash
   cd cloud && pnpm dev
   ```

4. **Create a claw** through the UI — it will provision on the seeded Mac Mini.

### Without a Real Agent

For testing the provisioning flow without a real agent, you can mock the agent API by running a simple HTTP server that responds to:
- `POST /claws` → `200 { "ok": true }`
- `GET /claws/:id/status` → `200 { "status": "running" }`
- `DELETE /claws/:id` → `200 { "ok": true }`
