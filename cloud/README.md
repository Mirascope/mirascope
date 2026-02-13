# Mirascope Cloud

Web application for the Mirascope platform. Built with TanStack Start, Vite, Cloudflare Workers, and Effect-ts.

## Local Development

### Prerequisites

- [Bun](https://bun.sh/) (package manager + runtime)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Postgres + ClickHouse)

### Quick Start

```bash
cd cloud
bun install
bun run dev
```

That's it. `bun run dev` automatically:

1. **Starts Docker containers** (Postgres + ClickHouse via `docker/compose.yml`)
2. **Creates `.env.local`** with dev-safe defaults (if missing)
3. **Runs Drizzle migrations** against the local Postgres
4. **Seeds dev data** (user, org, claw, auth session)
5. **Starts the Vite dev server** on `http://localhost:5173`

### Authentication (Automatic)

In local dev, authentication is handled automatically. A Vite plugin
(`vite-plugins/dev-auth.ts`) injects the dev session cookie into every request —
no login flow, no manual cookie setup.

You're automatically logged in as **Dev User** (`noreply@mirascope.com`),
owner of the **test-org** organization.

### Dev Data

| Entity     | Value                                  |
| ---------- | -------------------------------------- |
| User       | `noreply@mirascope.com` ("Dev User")   |
| Org        | `test-org` (slug)                      |
| Claw       | `test-claw` (slug), status: active     |
| Session ID | `00000000-0000-4000-8000-000000000004` |

### Connecting Chat to a Local OpenClaw Gateway

The Vite dev server includes a WebSocket proxy plugin that can connect the
chat UI to a real OpenClaw gateway running on your machine.

1. Edit `.env.local` and uncomment/set:

   ```
   OPENCLAW_GATEWAY_WS_URL=ws://localhost:18789
   OPENCLAW_GATEWAY_TOKEN=<your-gateway-token>
   ```

   Find your gateway token in `~/.openclaw/openclaw.json` under `gateway.auth.token`.

2. Restart the dev server (`bun run dev:fast` if DB is already set up)

3. Navigate to `http://localhost:5173/test-org/claws/test-claw/chat`

4. The chat UI connects through the Vite WS proxy → your local gateway.

### Scripts

| Script               | Description                               |
| -------------------- | ----------------------------------------- |
| `bun run dev`        | Full setup + Vite dev server              |
| `bun run dev:fast`   | Vite dev server only (skip setup)         |
| `bun run dev:setup`  | Run setup only (Docker, migrations, seed) |
| `bun run db:start`   | Start Docker containers                   |
| `bun run db:stop`    | Stop Docker containers                    |
| `bun run db:migrate` | Run Drizzle migrations                    |
| `bun run db:studio`  | Open Drizzle Studio (DB browser)          |

### Resetting Dev State

To wipe and re-seed the database:

```bash
docker compose -f docker/compose.yml down -v   # Remove containers + volumes
bun run dev                                      # Recreates everything
```

### Architecture

```
cloud/
├── app/                    # TanStack Start frontend (React)
│   ├── routes/             # File-based routing
│   ├── components/         # UI components
│   ├── hooks/              # React hooks (incl. useGatewayChat)
│   └── lib/                # Client-side utilities (GatewayClient, etc.)
├── api/                    # Server-side API handlers
├── auth/                   # Authentication (OAuth + session cookies)
├── claws/                  # Claw deployment infrastructure
│   └── dispatch-worker/    # Cloudflare Worker for claw proxying
├── db/
│   ├── schema/             # Drizzle ORM table definitions
│   └── migrations/         # SQL migration files
├── docker/                 # Docker Compose for local services
├── scripts/
│   └── dev/                # Local dev setup + seed scripts
├── settings.ts             # Centralized env var validation
├── server-entry.ts         # Cloudflare Worker entry point
└── vite-plugins/
    └── ws-proxy.ts         # Dev WS proxy for OpenClaw gateway
```
