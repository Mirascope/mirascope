# Claws

Claws are deployable AI agent instances. Each claw runs as a containerized OpenClaw gateway on Cloudflare with its own R2 storage bucket, bot identity, API key, and encrypted secrets. The system manages the full lifecycle: creation, provisioning, deployment, access control, and usage metering.

## Architecture

```
                                                 ┌─────────────────────────────┐
                                                 │      Mirascope Cloud        │
                                                 │  (Cloudflare Worker)        │
                                                 │                             │
 User ──▶ openclaw.mirascope.com/{org}/{claw} ──▶  │  ┌─────────────────────┐    │
                                        DNS      │  │  Public API         │    │
                                         │       │  │  mirascope.com/     │    │
                                         │       │  │    {org}/claws/{claw}│   │
                                         ▼       │  └─────────────────────┘    │
                                  ┌──────────┐   │  ┌─────────────────────┐    │
                                  │ Dispatch │◀──┼──│  Internal API       │    │
                                  │ Worker   │──▶│  │  /api/internal/     │    │
                                  └────┬─────┘   │  │    claws/*          │    │
                                       │         │  └─────────────────────┘    │
                              ┌────────┼──────┐  │  ┌─────────────────────┐    │
                              │  Sandbox DO   │  │  │  Database           │    │
                              │  ┌──────────┐ │  │  │  (Drizzle/D1)      │    │
                              │  │ OpenClaw │ │  │  └─────────────────────┘    │
                              │  │ Gateway  │ │  │  ┌─────────────────────┐    │
                              │  └──────────┘ │  │  │  Encryption         │    │
                              │  ┌──────────┐ │  │  │  (AES-256-GCM)     │    │
                              │  │ R2 Mount │ │  │  └─────────────────────┘    │
                              │  │ /data/   │ │  └─────────────────────────────┘
                              │  │  claw    │ │
                              │  └──────────┘ │
                              └───────────────┘
```

## Directory Structure

```
claws/
├── README.md               ← You are here
├── crypto.ts               ← AES-256-GCM encryption for secrets at rest
├── crypto.test.ts
├── deployment/
│   ├── types.ts            ← Core types (instance types, statuses, configs)
│   ├── service.ts          ← DeploymentService interface (Effect Context.Tag)
│   ├── live.ts             ← Live implementation (R2 + Containers)
│   ├── mock.ts             ← Mock implementation for tests
│   └── errors.ts           ← ClawDeploymentError
└── dispatch-worker/        ← Separate Cloudflare Worker package
    ├── src/
    │   ├── index.ts        ← Hono app, request routing
    │   ├── types.ts        ← DispatchEnv, OpenClawConfig (local mirror)
    │   ├── bootstrap.ts    ← Fetch config from Mirascope internal API
    │   ├── proxy.ts        ← R2 mounting, gateway process, HTTP/WS proxy
    │   ├── internal.ts     ← /_internal/* management endpoints
    │   ├── cache.ts        ← LRU cache for bootstrap configs
    │   ├── config.ts       ← Constants (port, timeout, mount path)
    │   └── utils.ts        ← Host header parsing
    └── tests/
        ├── integration/    ← Miniflare + Docker integration tests
        ├── helpers/        ← Test harness workers, mock cloud, gateway client
        └── docker/         ← Docker Compose setup for real OpenClaw gateway
```

Related files elsewhere in `cloud/`:

```
db/schema/claws.ts              ← Claws table (status, instance type, secrets, usage)
db/schema/claw-memberships.ts   ← Per-claw RBAC memberships
db/schema/claw-membership-audit.ts ← Audit log for membership changes
db/claws.ts                     ← Claws database service (CRUD, provisioning, usage)
db/claw-memberships.ts          ← Membership database service
api/claws.schemas.ts            ← HTTP API schemas (Effect HttpApiGroup)
api/claws.handlers.ts           ← Public API handlers
api/claws-internal.handlers.ts  ← Internal API handlers (bootstrap, resolve, status)
api/claw-memberships.schemas.ts ← Membership API schemas
api/claw-memberships.handlers.ts← Membership API handlers
app/contexts/claw.tsx           ← React context + useClaw() hook
app/api/claws.ts                ← TanStack Query hooks
app/components/claw-*.tsx       ← UI components (card, modal, sidebar, members)
app/routes/cloud/claws/         ← Claw pages
app/routes/cloud/settings/claws.tsx ← Claw management settings page
```

## Key Concepts

### Instance Types

Each claw runs on one of these container configurations:

| Type         | vCPU  | RAM      | Notes                    |
|--------------|-------|----------|--------------------------|
| `lite`       | 1/16  | 256 MiB  | Testing only             |
| `basic`      | 1/4   | 1 GiB    | Free tier                |
| `standard-1` | 1/2   | 2 GiB    |                          |
| `standard-2` | 1     | 6 GiB    | Pro tier (default)       |
| `standard-3` | 2     | 8 GiB    | Team tier                |
| `standard-4` | 4     | 12 GiB   | Power users              |

### Status Lifecycle

```
pending → provisioning → active ⇄ paused
                │                    │
                └──────▶ error ◀─────┘
```

- **pending** — Created in DB but infrastructure not yet provisioned
- **provisioning** — R2 bucket created, container starting
- **active** — Running and healthy
- **paused** — Stopped, can be restarted
- **error** — Failed (see `lastError`)

### Authorization Model

Two layers of access control:

1. **Organization-level**: Org `OWNER`/`ADMIN` have implicit `ADMIN` access to all claws in that org.
2. **Claw-level memberships**: Explicit roles assigned per-claw:
   - `ADMIN` — Full control (update, delete, manage members)
   - `DEVELOPER` — Can interact with the claw
   - `VIEWER` — Read-only
   - `ANNOTATOR` — Annotation access

Org privilege always takes precedence over explicit claw membership.

## Provisioning Flow

When a claw is created via the API, the following happens atomically:

```
1. Verify caller is org OWNER/ADMIN
2. Check plan limits (Stripe)
3. Database transaction:
   a. Insert claw record
   b. Create bot user (service account)
   c. Add bot user to organization (BOT role)
   d. Create or link home project
   e. Create environment in home project
   f. Generate API key for the bot user
   g. Update claw with home project/environment IDs
   h. Add creator as claw ADMIN
4. Provision infrastructure (LiveDeploymentService):
   a. Create R2 bucket "claw-{clawId}"
   b. Create scoped R2 credentials for that bucket
5. Encrypt R2 credentials (AES-256-GCM) → store in DB
6. Warm up dispatch worker (triggers cold start)
7. Dispatch worker:
   a. Receives request at openclaw.mirascope.com/{org}/{claw}
   b. Fetches bootstrap config via service binding (internal API)
   c. Mounts R2 bucket at /data/claw
   d. Starts OpenClaw gateway process
   e. Reports "active" status back to Mirascope
```

## Encryption

Claw secrets (R2 credentials and integration tokens) are encrypted at rest using AES-256-GCM via the Web Crypto API.

- **Wire format**: `base64(IV[12 bytes] || ciphertext + authTag)`
- **Key management**: Keys are versioned via `Settings.encryptionKeys` (a map of `keyId` → base64 key). The active key for new encryptions is `Settings.activeEncryptionKeyId`. On decrypt, the `keyId` stored alongside the ciphertext selects the correct key, enabling seamless rotation.
- Secrets are only decrypted at runtime when passed to the dispatch worker via the bootstrap API.

## Dispatch Worker

The dispatch worker is a separate Cloudflare Worker that runs alongside the main Mirascope Cloud worker. It routes requests to per-claw Sandbox containers (Durable Objects).

### Request Flow

1. Extract `clawId` from the request path (`openclaw.mirascope.com/{org}/{claw}`)
2. Get or create a Sandbox Durable Object for the `clawId`
3. Route `/_internal/*` to management endpoints
4. For all other requests:
   - Fetch/cache bootstrap config via the `MIRASCOPE_CLOUD` service binding
   - Mount R2 storage with per-claw scoped credentials
   - Ensure the OpenClaw gateway process is running
   - Proxy HTTP or WebSocket to the gateway on port `18789`

### Internal Management Endpoints

Called by `LiveCloudflareContainerService` for lifecycle management:

| Method | Path                          | Purpose                              |
|--------|-------------------------------|--------------------------------------|
| POST   | `/_internal/recreate`         | Destroy container for fresh start    |
| POST   | `/_internal/restart-gateway`  | Kill gateway (restarts on next req)  |
| POST   | `/_internal/destroy`          | Destroy container + DO storage       |
| GET    | `/_internal/state`            | Return current ContainerState        |

### Config Caching

Bootstrap configs are cached in an LRU cache (max 100 entries, 5-minute TTL) to avoid re-fetching on every request.

## Usage Tracking

Each claw tracks spending across two rolling windows:

- **Weekly** (7-day) — With an optional per-claw guardrail (`weeklySpendingGuardrailCenticents`)
- **Burst** (5-hour) — For rate limiting

Usage is also aggregated at the organization level ("pool usage") and integrated with Stripe billing.

## DeploymentService

The `ClawDeploymentService` is an Effect `Context.Tag` that abstracts infrastructure operations:

```ts
const deployment = yield* ClawDeploymentService;

yield* deployment.provision(config);   // Create R2 bucket + credentials
yield* deployment.warmUp(clawId);      // Trigger container cold start
yield* deployment.getStatus(clawId);   // Check health
yield* deployment.restart(clawId);     // Restart gateway
yield* deployment.update(clawId, cfg); // Update config / instance type
yield* deployment.deprovision(clawId); // Destroy container + delete bucket
```

Two implementations:
- **`LiveDeploymentService`** — Composes `CloudflareR2Service` + `CloudflareContainerService`
- **`MockDeploymentService`** — In-memory state with simulated delays for testing

## Public API

All endpoints are scoped to an organization:

| Method | Path                                          | Purpose           |
|--------|-----------------------------------------------|-------------------|
| GET    | `/organizations/:orgId/claws`                 | List claws        |
| POST   | `/organizations/:orgId/claws`                 | Create claw       |
| GET    | `/organizations/:orgId/claws/:clawId`         | Get claw          |
| PUT    | `/organizations/:orgId/claws/:clawId`         | Update claw       |
| DELETE | `/organizations/:orgId/claws/:clawId`         | Delete claw       |
| GET    | `/organizations/:orgId/claws/:clawId/usage`   | Get usage stats   |
| GET    | `.../:clawId/members`                         | List members      |
| POST   | `.../:clawId/members`                         | Add member        |
| GET    | `.../:clawId/members/:memberId`               | Get member        |
| PATCH  | `.../:clawId/members/:memberId`               | Update role       |
| DELETE | `.../:clawId/members/:memberId`               | Remove member     |

### Internal API (service binding only)

| Method | Path                                              | Purpose                        |
|--------|---------------------------------------------------|--------------------------------|
| GET    | `/api/internal/claws/resolve/:orgSlug/:clawSlug`  | Resolve slugs → clawId        |
| GET    | `/api/internal/claws/:clawId/bootstrap`            | Return decrypted OpenClawConfig|
| POST   | `/api/internal/claws/:clawId/status`               | Accept status reports          |
