# Mac Mini Agent

Lightweight HTTP server for claw provisioning and management on Mac Minis. Runs under the `clawadmin` account and handles macOS user creation, launchd service management, Cloudflare tunnel routing, and resource monitoring.

## Quick Start

```bash
# Install dependencies
bun install

# Development (requires AGENT_AUTH_TOKEN)
AGENT_AUTH_TOKEN=dev-secret bun run dev

# Production
bun run start

# Tests
bun run test
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AGENT_AUTH_TOKEN` | *required* | Bearer token for authenticating requests |
| `AGENT_PORT` | `7600` | Port the agent listens on |
| `TUNNEL_CONFIG_PATH` | `/etc/cloudflared/config.yml` | Path to cloudflared config |
| `TUNNEL_HOSTNAME_SUFFIX` | `claws.mirascope.dev` | Suffix for tunnel hostnames |
| `MAX_CLAWS` | `12` | Maximum claws this Mini supports |
| `PORT_RANGE_START` | `3001` | First port for claw gateways |
| `PORT_RANGE_END` | `3100` | Last port for claw gateways |

## API Endpoints

All endpoints except `GET /health` require `Authorization: Bearer <token>`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Mini health (CPU, RAM, disk, claw count) |
| `GET` | `/claws` | List all claws on this Mini |
| `POST` | `/claws` | Provision a new claw |
| `GET` | `/claws/:clawUser/status` | Get claw status + resources |
| `POST` | `/claws/:clawUser/restart` | Restart claw gateway |
| `DELETE` | `/claws/:clawUser` | Deprovision a claw |
| `POST` | `/claws/:clawUser/backup` | Trigger R2 backup (stub) |

### Provision Request

```json
{
  "clawId": "uuid-of-the-claw",
  "macUsername": "claw-ab12cd34",
  "localPort": 3001,
  "gatewayToken": "gateway-auth-token",
  "tunnelHostname": "claw-uuid.claws.mirascope.dev",
  "envVars": { "KEY": "value" }
}
```

## Deployment

The agent is deployed to `/opt/mirascope/mini-agent/` on each Mac Mini and runs as a launchd system daemon. See the design doc (`cloud/docs/design/mac-mini-claw-farm.md`) for the launchd plist and installation steps.

```bash
# Build
bun run build

# Copy to Mini
scp -r dist/ clawadmin@mini:/opt/mirascope/mini-agent/

# Install launchd plist (see design doc for plist XML)
sudo cp com.mirascope.mini-agent.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.mirascope.mini-agent.plist
```

## Architecture

```
src/
├── index.ts              # Hono app entry point
├── lib/
│   ├── config.ts         # Env var configuration
│   └── exec.ts           # Safe shell execution wrapper
├── middleware/
│   └── auth.ts           # Bearer token auth
├── routes/
│   ├── claws.ts          # CRUD endpoints
│   └── health.ts         # Health check
└── services/
    ├── launchd.ts        # launchd plist management
    ├── monitoring.ts     # Per-claw resource monitoring
    ├── provisioning.ts   # Orchestrates provision/deprovision
    ├── system.ts         # System-level stats (CPU, RAM, disk)
    ├── tunnel.ts         # cloudflared config management
    └── user.ts           # macOS user creation/deletion
```

Shell execution is abstracted via `ExecFn` for easy mocking in tests.
