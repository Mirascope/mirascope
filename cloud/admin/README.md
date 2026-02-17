# Fleet Admin Dashboard (POC)

Local development dashboard for managing the Mac Mini claw fleet.

## Quick Start

```bash
cd cloud/admin
bun install
bun run dev
```

Opens at http://localhost:5174. By default, it proxies API requests to `http://localhost:8787` (the local Mac Mini Agent).

## Connecting to a Remote Agent

Click **Configure** in the top bar to change the agent URL. You can point it at:
- `http://localhost:8787` — local agent
- `http://<tailscale-ip>:8787` — remote agent via Tailscale
- Any agent URL with an optional bearer token for auth

## What It Shows

- **Fleet Overview** — Mini card with hostname, CPU/RAM/disk gauges, claw capacity meter, tunnel status
- **Claws Table** — per-claw status, gateway PID, uptime, memory, chromium PID, process count
- **Actions** — restart, backup, deprovision per claw

Data auto-refreshes every 5 seconds.

## Future

This POC will evolve into the full `admin.mirascope.com` dashboard with:
- Environment switcher (Dev / Staging / Production)
- Multiple Mini cards
- Historical metrics from ClickHouse
- Drain / maintenance mode actions
- Capacity planning views
