# Mac Mini Claw Farm — Design Document

> **Status:** Draft  
> **Authors:** Sazed, William  
> **Date:** 2026-02-16  
> **Replaces:** Cloudflare Containers (dispatch worker + `@cloudflare/sandbox`)

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current Architecture](#2-current-architecture)
3. [New Architecture](#3-new-architecture)
4. [Codebase Changes — File by File](#4-codebase-changes--file-by-file)
5. [New Database Tables](#5-new-database-tables)
6. [New Files](#6-new-files)
7. [Modified Files](#7-modified-files)
8. [Mac Mini Agent](#8-mac-mini-agent)
9. [Provisioning Flow](#9-provisioning-flow)
10. [Deprovisioning & Archival](#10-deprovisioning--archival)
11. [WebSocket Proxy Changes](#11-websocket-proxy-changes)
12. [Backup System](#12-backup-system)
13. [Live Migration](#13-live-migration)
14. [Security Model](#14-security-model)
15. [Monitoring & Alerting](#15-monitoring--alerting)
16. [Migration from Cloudflare](#16-migration-from-cloudflare)
17. [Environment Topology](#17-environment-topology)
18. [Local Development](#18-local-development)
19. [Implementation Phases](#19-implementation-phases)
20. [Open Questions](#20-open-questions)

---

## 1. Executive Summary

Replace Cloudflare Containers with Mac Minis running macOS. Each Mini hosts ~12 Claws as isolated macOS user accounts. OpenClaw gateway runs as a per-user `launchd` service. Traffic routes through Cloudflare Tunnels. Admin access via Tailscale SSH. R2 becomes a backup layer (local disk is primary storage).

**Why:**
- Cloudflare Containers have cold-start latency, limited macOS tooling, and no residential IP for browser automation
- Mac Minis provide native macOS, Playwright/Chromium with residential IPs (bot detection advantage), persistent local storage, and predictable performance
- M4 Pro 32GB/1TB at ~$600 supports 12 Claws — better unit economics at scale

**POC target:** Single M4 16GB/512GB Mini, single Claw, at William's home on WiFi.  
**Production target:** M4 Pro 32GB/1TB Minis, 12 Claws each, Ethernet, eventually colo/MacStadium.

---

## 2. Current Architecture

```
Browser
  │
  ├─ HTTPS ──→ Cloudflare Worker (mirascope.com frontend)
  │
  └─ WSS ───→ /api/ws/claws/:orgSlug/:clawSlug
                │  (cloud/api/claws-ws-proxy.ts)
                │
                ▼
         Dispatch Worker (cloud/claws/dispatch-worker/)
                │  - Resolves claw via service binding
                │  - Fetches bootstrap config (R2 creds, env, gateway token)
                │  - Manages container lifecycle via @cloudflare/sandbox
                │
                ▼
         Cloudflare Container (Durable Object + sandbox)
                │  - Runs OpenClaw gateway process
                │  - R2-mounted persistent storage
                │
                ▼
         OpenClaw Gateway (inside container)
```

### Key Components

| Component | Path | Role |
|-----------|------|------|
| **DeploymentService interface** | `cloud/claws/deployment/service.ts` | `ClawDeploymentServiceInterface` — `provision`, `deprovision`, `getStatus`, `restart`, `update`, `warmUp`. Returns `ClawDeploymentStatus` (status, url, startedAt, errorMessage, bucketName, r2Credentials). Error type: `ClawDeploymentError`. |
| **DeploymentService types** | `cloud/claws/deployment/types.ts` | `ProvisionClawConfig`, `OpenClawDeployConfig`, `ClawInstanceType` (enum: `lite`, `basic`, `standard-1` through `standard-4`), `ClawStatus`, `ClawR2Config` |
| **Live deployment impl** | `cloud/claws/deployment/live.ts` | `LiveDeploymentService` — composes `CloudflareR2Service` + `CloudflareContainerService`. Uses `clawHostname()` → `{clawId}.claws.mirascope.com` for internal routing. Provision only creates R2 bucket + scoped creds; caller persists to DB then calls `warmUp` separately. |
| **Container service interface** | `cloud/cloudflare/containers/service.ts` | `CloudflareContainerServiceInterface` — `recreate`, `restartGateway`, `destroy`, `getState`, `warmUp`, `listInstances`. Error type: `CloudflareApiError`. |
| **Container service impl** | `cloud/cloudflare/containers/live.ts` | HTTP calls to dispatch worker internal endpoints (`/_internal/recreate`, `/_internal/restart-gateway`, `/_internal/destroy`, `/_internal/state`, `/_internal/warm-up`) using `Host` header routing. Also uses Cloudflare REST API for `listInstances`. |
| **Container types** | `cloud/cloudflare/containers/types.ts` | `ContainerState`, `ContainerStatus`, `DurableObjectInfo` |
| **R2 service** | `cloud/cloudflare/r2/service.ts` | `CloudflareR2ServiceInterface` — `createBucket`, `deleteBucket`, `getBucket`, `listBuckets`, `createScopedCredentials`, `revokeScopedCredentials`. Types in `r2/types.ts`: `R2ScopedCredentials` has `tokenId`, `accessKeyId`, `secretAccessKey`, `expiresOn?`. |
| **WS proxy** | `cloud/api/claws-ws-proxy.ts` | `handleClawsWebSocket` + `connectAndRelay`. Two-phase auth: (1) `connectAndRelay` sends `Authorization: Bearer {gatewayToken}` to upstream dispatch worker for routing, (2) performs OpenClaw handshake (challenge → connect with auth token, scopes `operator.admin`/`operator.approvals`/`operator.pairing`, client info), (3) sends `proxy.ready` to browser, (4) bidirectional relay with close/error propagation. |
| **Internal API handlers** | `cloud/api/claws-internal.handlers.ts` | `resolveClawHandler` (slug→clawId), `bootstrapClawHandler` (returns full `OpenClawConfigResponse` with decrypted secrets, R2 creds, containerEnv), `reportClawStatusHandler` (updates DB status/lastError/lastDeployedAt), `validateSessionHandler` (session→user, checks org membership + claw access, returns role). Called via Cloudflare service binding (in-process RPC, not HTTP). |
| **Claw CRUD handlers** | `cloud/api/claws.handlers.ts` | `createClawHandler`, `deleteClawHandler`, `restartClawHandler`, etc. |
| **DB schema** | `cloud/db/schema/claws.ts` | `claws` table — `clawStatusEnum` (`pending`, `provisioning`, `active`, `paused`, `error`), `clawInstanceTypeEnum` (`lite`, `basic`, `standard-1` through `standard-4`), `secretsEncrypted`/`secretsKeyId` (AES-256-GCM), `bucketName`, `botUserId` (unique, references users), `homeProjectId`, `homeEnvironmentId`, `weeklySpendingGuardrailCenticents`, `weeklyWindowStart`/`weeklyUsageCenticents` (weekly billing), `burstWindowStart`/`burstUsageCenticents` (5-hour burst rate limit). |
| **Dispatch worker** | `cloud/claws/dispatch-worker/` | Cloudflare Worker managing container lifecycle. Uses `@cloudflare/sandbox`: `getSandbox()`, `sandbox.startProcess()`, `sandbox.containerFetch()`, `sandbox.wsConnect()`, `sandbox.listProcesses()`. `ensureGateway()` finds existing process → waits for port → or starts new one. Bootstrap config fetched via `env.MIRASCOPE_CLOUD` service binding (in-process RPC). |
| **Crypto utils** | `cloud/claws/crypto.ts` | `encryptSecrets`, `decryptSecrets` for AES-256-GCM. Wire format: base64(iv[12 bytes] ‖ ciphertext+authTag). Keys versioned via `Settings.encryptionKeys` map with `activeEncryptionKeyId` for rotation. |

---

## 3. New Architecture

```
Browser
  │
  ├─ HTTPS ──→ Cloudflare Worker (mirascope.com frontend)
  │
  └─ WSS ───→ /api/ws/claws/:orgSlug/:clawSlug
                │  (cloud/api/claws-ws-proxy.ts)
                │
                ▼
         Cloudflare Tunnel (claw-{id}.claws.mirascope.io)
                │
                ▼
         Mac Mini (macOS, residential IP)
                │  - Per-claw macOS user account
                │  - OpenClaw gateway as launchd service
                │  - Playwright/Chromium per user
                │  - Local SSD for primary storage
                │
                ▼
         OpenClaw Gateway (per-user launchd service)
```

### Network Topology

```
                    Internet
                       │
              ┌────────┴────────┐
              │  Cloudflare     │
              │  ┌────────────┐ │
              │  │ Tunnel     │ │  ← claw-{id}.claws.mirascope.io
              │  │ (ingress)  │ │
              │  └─────┬──────┘ │
              └────────┼────────┘
                       │ (encrypted tunnel)
                       │
              ┌────────┴────────┐
              │  Mac Mini       │
              │  ┌────────────┐ │
              │  │ cloudflared │ │  ← runs as root launchd service
              │  │ (connector) │ │
              │  └─────┬──────┘ │
              │        │        │
              │  localhost:XXXX │  ← per-claw port
              │  ┌────────────┐ │
              │  │ OpenClaw   │ │  ← runs as claw user
              │  │ Gateway    │ │
              │  └────────────┘ │
              │                 │
              │  ┌────────────┐ │
              │  │ Tailscale  │ │  ← admin SSH access
              │  └────────────┘ │
              └─────────────────┘
```

### Key Design Decisions

1. **One macOS user per Claw** — filesystem isolation, per-user launchd, separate Chromium profiles
2. **Cloudflare Tunnel for traffic** — no inbound ports, works behind NAT/WiFi, automatic TLS
3. **Tailscale for admin** — SSH access for provisioning and management, MagicDNS hostnames
4. **Local disk is primary storage** — SSD is fast, R2 becomes backup/archive layer
5. **Port-per-claw** — each gateway binds to `localhost:{BASE_PORT + offset}`, `cloudflared` routes by hostname
6. **launchd per claw** — auto-restart, proper lifecycle management, macOS-native
7. **Mini agent** — lightweight HTTP API on each Mini for provisioning commands (avoids complex SSH scripting from Workers)

---

## 4. Codebase Changes — File by File

### Files to DELETE (or deprecate)

| File | Reason |
|------|--------|
| `cloud/claws/dispatch-worker/` (entire directory) | Replaced by Mac Mini agent + Cloudflare Tunnel. Not deleted immediately — kept for migration period. |
| `cloud/cloudflare/containers/live.ts` | No more container management via dispatch worker |
| `cloud/cloudflare/containers/mock.ts` | Mock for deleted service |
| `cloud/cloudflare/containers/service.ts` | Interface no longer needed |
| `cloud/cloudflare/containers/types.ts` | Container-specific types |

### Files to MODIFY

| File | Changes |
|------|---------|
| `cloud/claws/deployment/live.ts` | Replace `LiveDeploymentService` with `MacMiniDeploymentService` (or swap the Layer) |
| `cloud/claws/deployment/types.ts` | Add Mac Mini-specific types, update `ClawInstanceType` |
| `cloud/api/claws-ws-proxy.ts` | Change upstream URL from dispatch worker to Cloudflare Tunnel hostname |
| `cloud/api/claws-internal.handlers.ts` | Adapt bootstrap handler for Mini agent consumption |
| `cloud/api/claws.handlers.ts` | No changes to handler logic (uses `ClawDeploymentService` interface) |
| `cloud/db/schema/claws.ts` | Add `macMiniId` foreign key, `tunnelHostname`, `localPort` columns |
| `cloud/db/schema/index.ts` | Export new tables |
| `cloud/claws/deployment/service.ts` | Add optional Mac Mini fields to `ClawDeploymentStatus` (see section 7.6) |

### Files to CREATE

| File | Purpose |
|------|---------|
| `cloud/mac-mini/deployment/live.ts` | `MacMiniDeploymentService` — implements `ClawDeploymentServiceInterface` |
| `cloud/mac-mini/deployment/types.ts` | Mac Mini-specific types (fleet, capacity, agent API) |
| `cloud/mac-mini/agent/server.ts` | Mini agent HTTP API server (runs on each Mini) |
| `cloud/mac-mini/agent/handlers.ts` | Agent endpoint handlers (provision, deprovision, status, etc.) |
| `cloud/mac-mini/agent/scripts/` | Shell scripts for user creation, launchd setup, tunnel config |
| `cloud/mac-mini/fleet/service.ts` | Fleet management service (Mini selection, capacity tracking) |
| `cloud/mac-mini/fleet/scheduler.ts` | Placement logic (which Mini gets a new Claw) |
| `cloud/mac-mini/backup/service.ts` | R2 backup orchestration |
| `cloud/mac-mini/backup/scripts/` | Backup/restore shell scripts |
| `cloud/mac-mini/tunnel/service.ts` | Cloudflare Tunnel route management |
| `cloud/db/schema/mac-minis.ts` | `mac_minis` table |
| `cloud/db/schema/mac-mini-claws.ts` | `mac_mini_claws` junction table |
| `cloud/db/migrations/XXXX_add_mac_minis.ts` | Migration for new tables + column additions |

---

## 5. New Database Tables

### `mac_minis` — Fleet Inventory

```sql
CREATE TABLE mac_minis (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hostname        TEXT NOT NULL UNIQUE,          -- e.g. "mini-01"
  display_name    TEXT,                          -- e.g. "William's Home Mini"
  
  -- Hardware
  chip            TEXT NOT NULL,                 -- e.g. "M4", "M4 Pro"
  ram_gb          INTEGER NOT NULL,              -- e.g. 16, 32
  disk_gb         INTEGER NOT NULL,              -- e.g. 512, 1000
  
  -- Network
  tailscale_ip    TEXT NOT NULL,                 -- e.g. "100.64.x.x"
  tailscale_fqdn  TEXT NOT NULL,                 -- e.g. "mini-01.tail1234.ts.net"
  agent_port      INTEGER NOT NULL DEFAULT 7600, -- Mini agent HTTP port
  public_ip       TEXT,                          -- residential IP (for reference)
  
  -- Cloudflare Tunnel
  tunnel_id       TEXT NOT NULL,                 -- Cloudflare tunnel UUID
  tunnel_token    TEXT,                          -- encrypted tunnel token
  
  -- Capacity
  max_claws       INTEGER NOT NULL DEFAULT 12,
  current_claws   INTEGER NOT NULL DEFAULT 0,
  base_port       INTEGER NOT NULL DEFAULT 8100, -- first claw port
  
  -- Status
  status          TEXT NOT NULL DEFAULT 'active', -- active, draining, offline, maintenance
  last_heartbeat  TIMESTAMPTZ,
  last_health     JSONB,                         -- CPU, memory, disk usage
  
  -- Location
  location        TEXT,                          -- "home-wifi", "home-ethernet", "colo"
  
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

```typescript
// cloud/db/schema/mac-minis.ts
import { pgEnum, pgTable, text, integer, timestamp, uuid, jsonb } from "drizzle-orm/pg-core";

export const macMiniStatusEnum = pgEnum("mac_mini_status", [
  "active",
  "draining",    // no new claws, existing ones run until migrated
  "offline",
  "maintenance",
]);

export const macMinis = pgTable("mac_minis", {
  id: uuid("id").primaryKey().defaultRandom(),
  hostname: text("hostname").notNull().unique(),
  displayName: text("display_name"),
  chip: text("chip").notNull(),
  ramGb: integer("ram_gb").notNull(),
  diskGb: integer("disk_gb").notNull(),
  tailscaleIp: text("tailscale_ip").notNull(),
  tailscaleFqdn: text("tailscale_fqdn").notNull(),
  agentPort: integer("agent_port").notNull().default(7600),
  publicIp: text("public_ip"),
  tunnelId: text("tunnel_id").notNull(),
  tunnelToken: text("tunnel_token"),
  maxClaws: integer("max_claws").notNull().default(12),
  currentClaws: integer("current_claws").notNull().default(0),
  basePort: integer("base_port").notNull().default(8100),
  status: macMiniStatusEnum("status").notNull().default("active"),
  lastHeartbeat: timestamp("last_heartbeat", { withTimezone: true }),
  lastHealth: jsonb("last_health"),
  location: text("location"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
});

export type MacMini = typeof macMinis.$inferSelect;
export type NewMacMini = typeof macMinis.$inferInsert;
```

### Additions to `claws` table

```sql
-- Add to existing claws table
ALTER TABLE claws ADD COLUMN mac_mini_id UUID REFERENCES mac_minis(id);
ALTER TABLE claws ADD COLUMN tunnel_hostname TEXT;     -- e.g. "claw-{id}.claws.mirascope.io"
ALTER TABLE claws ADD COLUMN local_port INTEGER;       -- port on the Mini
ALTER TABLE claws ADD COLUMN mac_username TEXT;         -- macOS username, e.g. "claw-ab12cd34"
ALTER TABLE claws ADD COLUMN archived_at TIMESTAMPTZ;  -- when archived to R2 (null = active)
```

```typescript
// Additions to cloud/db/schema/claws.ts
// Add these columns to the existing claws pgTable definition:

macMiniId: uuid("mac_mini_id").references(() => macMinis.id),
tunnelHostname: text("tunnel_hostname"),
localPort: integer("local_port"),
macUsername: text("mac_username"),
archivedAt: timestamp("archived_at", { withTimezone: true }),
```

---

## 6. New Files

### 6.1 `cloud/mac-mini/deployment/types.ts`

```typescript
/**
 * Types for Mac Mini deployment infrastructure.
 */

/** Health snapshot from a Mac Mini agent. */
export interface MacMiniHealth {
  cpuUsagePercent: number;
  memoryUsedGb: number;
  memoryTotalGb: number;
  diskUsedGb: number;
  diskTotalGb: number;
  uptimeSeconds: number;
  activeClaws: number;
  loadAverage: [number, number, number];
}

/** Per-claw status as reported by the Mini agent. */
export interface MacMiniClawStatus {
  clawId: string;
  macUsername: string;
  localPort: number;
  gatewayPid: number | null;
  gatewayUptime: number | null;      // seconds
  memoryUsageMb: number | null;
  chromiumPid: number | null;
  launchdStatus: "loaded" | "unloaded" | "error";
  tunnelRouteActive: boolean;
}

/** Request to provision a claw on a Mini. */
export interface MiniProvisionRequest {
  clawId: string;
  macUsername: string;
  localPort: number;
  gatewayToken: string;
  tunnelHostname: string;
  envVars: Record<string, string>;
}

/** Request to deprovision a claw from a Mini. */
export interface MiniDeprovisionRequest {
  clawId: string;
  macUsername: string;
  archive: boolean; // if true, backup to R2 first
}

/** Response from Mini agent provision endpoint. */
export interface MiniProvisionResponse {
  success: boolean;
  macUsername: string;
  localPort: number;
  tunnelRouteAdded: boolean;
  error?: string;
}

/** Port allocation on a Mini. */
export interface PortAllocation {
  port: number;
  clawId: string;
}
```

### 6.2 `cloud/mac-mini/deployment/live.ts` — MacMiniDeploymentService

```typescript
/**
 * @fileoverview Mac Mini deployment service.
 *
 * Implements ClawDeploymentServiceInterface by communicating with Mac Mini
 * agents over Tailscale. Replaces LiveDeploymentService which used
 * CloudflareR2Service + CloudflareContainerService.
 *
 * ## Provision Flow
 *
 * 1. Select a Mini with available capacity (FleetScheduler)
 * 2. Allocate a port and macOS username
 * 3. Call Mini agent's /provision endpoint via Tailscale
 * 4. Agent creates macOS user, configures launchd, adds tunnel route
 * 5. Create R2 bucket for backups (not primary storage)
 * 6. Return deployment status with tunnel hostname
 *
 * ## Deprovision Flow
 *
 * 1. Call Mini agent's /deprovision endpoint
 * 2. Agent stops gateway, removes launchd plist, removes tunnel route
 * 3. Optionally archives home dir to R2
 * 4. Agent deletes macOS user
 * 5. Delete R2 backup bucket
 */

import { Effect, Layer } from "effect";

import type { ClawDeploymentStatus } from "@/claws/deployment/service";
import type {
  OpenClawDeployConfig,
  ProvisionClawConfig,
} from "@/claws/deployment/types";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { MacMiniFleetService } from "@/mac-mini/fleet/service";

function bucketName(clawId: string): string {
  return `claw-backup-${clawId}`;
}

function macUsername(clawId: string): string {
  // Use first 8 chars of UUID for readable username
  return `claw-${clawId.slice(0, 8)}`;
}

function tunnelHostname(clawId: string): string {
  return `claw-${clawId}.claws.mirascope.io`;
}

export const MacMiniDeploymentService = Layer.effect(
  ClawDeploymentService,
  Effect.gen(function* () {
    const r2 = yield* CloudflareR2Service;
    const fleet = yield* MacMiniFleetService;

    return {
      provision: (config: ProvisionClawConfig) =>
        Effect.gen(function* () {
          // 1. Find a Mini with capacity
          const mini = yield* fleet.selectMini(config.instanceType);

          // 2. Allocate port and username
          const port = yield* fleet.allocatePort(mini.id);
          const username = macUsername(config.clawId);
          const hostname = tunnelHostname(config.clawId);

          // 3. Create R2 bucket for backups
          yield* r2.createBucket(bucketName(config.clawId)).pipe(
            Effect.mapError(
              (e) =>
                new ClawDeploymentError({
                  message: `Failed to create backup bucket: ${e.message}`,
                  cause: e,
                }),
            ),
          );

          const r2Credentials = yield* r2
            .createScopedCredentials(bucketName(config.clawId))
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to create R2 credentials: ${e.message}`,
                    cause: e,
                  }),
              ),
            );

          // 4. Call Mini agent to provision
          yield* fleet.provisionOnMini(mini.id, {
            clawId: config.clawId,
            macUsername: username,
            localPort: port,
            gatewayToken: "", // filled by caller after DB persist
            tunnelHostname: hostname,
            envVars: {},      // filled by caller
          });

          return {
            status: "provisioning",
            startedAt: new Date(),
            url: `wss://${hostname}`,
            bucketName: bucketName(config.clawId),
            r2Credentials,
          } satisfies ClawDeploymentStatus;
        }),

      deprovision: (clawId: string) =>
        Effect.gen(function* () {
          // 1. Find which Mini this claw is on
          const assignment = yield* fleet.getClawAssignment(clawId);

          // 2. Tell Mini agent to deprovision (with archive)
          yield* fleet.deprovisionOnMini(assignment.miniId, {
            clawId,
            macUsername: assignment.macUsername,
            archive: true,
          });

          // 3. Delete R2 backup bucket
          yield* r2.deleteBucket(bucketName(clawId)).pipe(
            Effect.catchAll(() => Effect.void),
          );

          // 4. Release port
          yield* fleet.releasePort(assignment.miniId, assignment.localPort);
        }),

      getStatus: (clawId: string) =>
        Effect.gen(function* () {
          const assignment = yield* fleet.getClawAssignment(clawId);
          const clawStatus = yield* fleet.getClawStatusOnMini(
            assignment.miniId,
            clawId,
          );

          return {
            status:
              clawStatus.gatewayPid != null && clawStatus.launchdStatus === "loaded"
                ? "active"
                : clawStatus.launchdStatus === "error"
                  ? "error"
                  : "paused",
            startedAt: clawStatus.gatewayUptime
              ? new Date(Date.now() - clawStatus.gatewayUptime * 1000)
              : undefined,
          } satisfies ClawDeploymentStatus;
        }),

      restart: (clawId: string) =>
        Effect.gen(function* () {
          const assignment = yield* fleet.getClawAssignment(clawId);
          yield* fleet.restartClawOnMini(assignment.miniId, clawId);

          return {
            status: "provisioning",
            startedAt: new Date(),
          } satisfies ClawDeploymentStatus;
        }),

      update: (clawId: string, _config: Partial<OpenClawDeployConfig>) =>
        Effect.gen(function* () {
          // For Mac Mini, update = restart gateway to pick up new config
          // Instance type changes are N/A (all Minis provide same resources per claw)
          const assignment = yield* fleet.getClawAssignment(clawId);
          yield* fleet.restartClawOnMini(assignment.miniId, clawId);

          return {
            status: "provisioning",
            startedAt: new Date(),
          } satisfies ClawDeploymentStatus;
        }),

      warmUp: (clawId: string) =>
        Effect.gen(function* () {
          const assignment = yield* fleet.getClawAssignment(clawId);
          yield* fleet.startClawOnMini(assignment.miniId, clawId);
        }),
    };
  }),
);
```

### 6.3 `cloud/mac-mini/fleet/service.ts` — Fleet Management

```typescript
/**
 * @fileoverview Fleet management service for Mac Mini infrastructure.
 *
 * Handles Mini selection, port allocation, and proxying commands to Mini agents.
 * All communication with Minis goes through Tailscale (private network).
 */

import { Context, Effect } from "effect";

import type { MacMiniClawStatus, MacMiniHealth, MiniProvisionRequest, MiniDeprovisionRequest } from "@/mac-mini/deployment/types";
import type { ClawInstanceType } from "@/claws/deployment/types";
import { ClawDeploymentError } from "@/claws/deployment/errors";

export interface ClawAssignment {
  miniId: string;
  macUsername: string;
  localPort: number;
  tunnelHostname: string;
}

export interface MacMiniFleetServiceInterface {
  /** Select the best Mini for a new claw based on capacity and health. */
  readonly selectMini: (
    instanceType: ClawInstanceType,
  ) => Effect.Effect<{ id: string; hostname: string }, ClawDeploymentError>;

  /** Allocate the next available port on a Mini. */
  readonly allocatePort: (
    miniId: string,
  ) => Effect.Effect<number, ClawDeploymentError>;

  /** Release a port allocation. */
  readonly releasePort: (
    miniId: string,
    port: number,
  ) => Effect.Effect<void, ClawDeploymentError>;

  /** Get which Mini a claw is assigned to. */
  readonly getClawAssignment: (
    clawId: string,
  ) => Effect.Effect<ClawAssignment, ClawDeploymentError>;

  /** Provision a claw on a specific Mini (calls Mini agent). */
  readonly provisionOnMini: (
    miniId: string,
    request: MiniProvisionRequest,
  ) => Effect.Effect<void, ClawDeploymentError>;

  /** Deprovision a claw from a specific Mini (calls Mini agent). */
  readonly deprovisionOnMini: (
    miniId: string,
    request: MiniDeprovisionRequest,
  ) => Effect.Effect<void, ClawDeploymentError>;

  /** Get claw status from Mini agent. */
  readonly getClawStatusOnMini: (
    miniId: string,
    clawId: string,
  ) => Effect.Effect<MacMiniClawStatus, ClawDeploymentError>;

  /** Restart a claw's gateway on a Mini. */
  readonly restartClawOnMini: (
    miniId: string,
    clawId: string,
  ) => Effect.Effect<void, ClawDeploymentError>;

  /** Start a claw's gateway on a Mini (warm up). */
  readonly startClawOnMini: (
    miniId: string,
    clawId: string,
  ) => Effect.Effect<void, ClawDeploymentError>;

  /** Get health info for a Mini. */
  readonly getMiniHealth: (
    miniId: string,
  ) => Effect.Effect<MacMiniHealth, ClawDeploymentError>;
}

export class MacMiniFleetService extends Context.Tag("MacMiniFleetService")<
  MacMiniFleetService,
  MacMiniFleetServiceInterface
>() {}
```

### 6.4 `cloud/mac-mini/fleet/live.ts` — Fleet Service Implementation

```typescript
/**
 * Live fleet service — communicates with Mini agents over Tailscale HTTP.
 *
 * Mini agent base URL: http://{tailscale_fqdn}:{agent_port}
 *
 * Placement strategy (v1 — simple):
 *   1. Query mac_minis WHERE status = 'active' AND current_claws < max_claws
 *   2. Order by current_claws ASC (least loaded first)
 *   3. Pick first
 *
 * Port allocation:
 *   - Each Mini has a base_port (default 8100)
 *   - Ports are base_port + 0..max_claws-1
 *   - Track allocated ports via claws.local_port column
 *   - Find first unused port in range
 */

import { Effect, Layer } from "effect";
import { eq, and, lt, sql, isNull } from "drizzle-orm";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import { DrizzleORM } from "@/db/client";
import { macMinis } from "@/db/schema/mac-minis";
import { claws } from "@/db/schema";
import { MacMiniFleetService } from "@/mac-mini/fleet/service";

export const LiveMacMiniFleetService = Layer.effect(
  MacMiniFleetService,
  Effect.gen(function* () {
    const db = yield* DrizzleORM;

    /** Build agent URL for a Mini. */
    function agentUrl(tailscaleFqdn: string, agentPort: number): string {
      return `http://${tailscaleFqdn}:${agentPort}`;
    }

    /** Call a Mini agent endpoint. */
    function callAgent<T>(
      baseUrl: string,
      path: string,
      method: "GET" | "POST" | "DELETE" = "GET",
      body?: unknown,
    ): Effect.Effect<T, ClawDeploymentError> {
      return Effect.tryPromise({
        try: async () => {
          const res = await fetch(`${baseUrl}${path}`, {
            method,
            headers: body ? { "Content-Type": "application/json" } : {},
            body: body ? JSON.stringify(body) : undefined,
          });
          if (!res.ok) {
            const text = await res.text();
            throw new Error(`Agent returned ${res.status}: ${text}`);
          }
          return (await res.json()) as T;
        },
        catch: (e) =>
          new ClawDeploymentError({
            message: `Mini agent call failed: ${e instanceof Error ? e.message : String(e)}`,
            cause: e,
          }),
      });
    }

    return {
      selectMini: (_instanceType) =>
        Effect.gen(function* () {
          const [mini] = yield* db
            .select({ id: macMinis.id, hostname: macMinis.hostname })
            .from(macMinis)
            .where(
              and(
                eq(macMinis.status, "active"),
                lt(macMinis.currentClaws, macMinis.maxClaws),
              ),
            )
            .orderBy(macMinis.currentClaws)
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to select Mini: ${e}`,
                    cause: e,
                  }),
              ),
            );

          if (!mini) {
            return yield* Effect.fail(
              new ClawDeploymentError({
                message: "No Mac Minis available with capacity",
              }),
            );
          }

          return mini;
        }),

      allocatePort: (miniId) =>
        Effect.gen(function* () {
          const [mini] = yield* db
            .select({
              basePort: macMinis.basePort,
              maxClaws: macMinis.maxClaws,
            })
            .from(macMinis)
            .where(eq(macMinis.id, miniId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );

          if (!mini) {
            return yield* Effect.fail(
              new ClawDeploymentError({ message: `Mini ${miniId} not found` }),
            );
          }

          // Find used ports on this Mini
          const usedPorts = yield* db
            .select({ localPort: claws.localPort })
            .from(claws)
            .where(eq(claws.macMiniId, miniId))
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );

          const usedSet = new Set(usedPorts.map((r) => r.localPort));

          for (let offset = 0; offset < mini.maxClaws; offset++) {
            const port = mini.basePort + offset;
            if (!usedSet.has(port)) {
              return port;
            }
          }

          return yield* Effect.fail(
            new ClawDeploymentError({ message: `No ports available on Mini ${miniId}` }),
          );
        }),

      releasePort: (_miniId, _port) => Effect.void,

      getClawAssignment: (clawId) =>
        Effect.gen(function* () {
          const [row] = yield* db
            .select({
              miniId: claws.macMiniId,
              macUsername: claws.macUsername,
              localPort: claws.localPort,
              tunnelHostname: claws.tunnelHostname,
            })
            .from(claws)
            .where(eq(claws.id, clawId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );

          if (!row?.miniId || !row.macUsername || !row.localPort || !row.tunnelHostname) {
            return yield* Effect.fail(
              new ClawDeploymentError({
                message: `Claw ${clawId} has no Mac Mini assignment`,
              }),
            );
          }

          return {
            miniId: row.miniId,
            macUsername: row.macUsername,
            localPort: row.localPort,
            tunnelHostname: row.tunnelHostname,
          };
        }),

      provisionOnMini: (miniId, request) =>
        Effect.gen(function* () {
          const [mini] = yield* db
            .select({
              tailscaleFqdn: macMinis.tailscaleFqdn,
              agentPort: macMinis.agentPort,
            })
            .from(macMinis)
            .where(eq(macMinis.id, miniId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );

          if (!mini) {
            return yield* Effect.fail(
              new ClawDeploymentError({ message: `Mini ${miniId} not found` }),
            );
          }

          const base = agentUrl(mini.tailscaleFqdn, mini.agentPort);
          yield* callAgent(base, "/api/provision", "POST", request);

          // Increment current_claws counter
          yield* db
            .update(macMinis)
            .set({ currentClaws: sql`${macMinis.currentClaws} + 1`, updatedAt: new Date() })
            .where(eq(macMinis.id, miniId))
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );
        }),

      deprovisionOnMini: (miniId, request) =>
        Effect.gen(function* () {
          const [mini] = yield* db
            .select({
              tailscaleFqdn: macMinis.tailscaleFqdn,
              agentPort: macMinis.agentPort,
            })
            .from(macMinis)
            .where(eq(macMinis.id, miniId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );

          if (!mini) {
            return yield* Effect.fail(
              new ClawDeploymentError({ message: `Mini ${miniId} not found` }),
            );
          }

          const base = agentUrl(mini.tailscaleFqdn, mini.agentPort);
          yield* callAgent(base, "/api/deprovision", "POST", request);

          // Decrement current_claws counter
          yield* db
            .update(macMinis)
            .set({ currentClaws: sql`${macMinis.currentClaws} - 1`, updatedAt: new Date() })
            .where(eq(macMinis.id, miniId))
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );
        }),

      getClawStatusOnMini: (miniId, clawId) =>
        Effect.gen(function* () {
          const [mini] = yield* db
            .select({
              tailscaleFqdn: macMinis.tailscaleFqdn,
              agentPort: macMinis.agentPort,
            })
            .from(macMinis)
            .where(eq(macMinis.id, miniId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );

          if (!mini) {
            return yield* Effect.fail(
              new ClawDeploymentError({ message: `Mini ${miniId} not found` }),
            );
          }

          const base = agentUrl(mini.tailscaleFqdn, mini.agentPort);
          return yield* callAgent(base, `/api/claws/${clawId}/status`);
        }),

      restartClawOnMini: (miniId, clawId) =>
        Effect.gen(function* () {
          const [mini] = yield* db
            .select({
              tailscaleFqdn: macMinis.tailscaleFqdn,
              agentPort: macMinis.agentPort,
            })
            .from(macMinis)
            .where(eq(macMinis.id, miniId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );

          if (!mini) {
            return yield* Effect.fail(
              new ClawDeploymentError({ message: `Mini ${miniId} not found` }),
            );
          }

          const base = agentUrl(mini.tailscaleFqdn, mini.agentPort);
          yield* callAgent(base, `/api/claws/${clawId}/restart`, "POST");
        }),

      startClawOnMini: (miniId, clawId) =>
        Effect.gen(function* () {
          const [mini] = yield* db
            .select({
              tailscaleFqdn: macMinis.tailscaleFqdn,
              agentPort: macMinis.agentPort,
            })
            .from(macMinis)
            .where(eq(macMinis.id, miniId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );

          if (!mini) {
            return yield* Effect.fail(
              new ClawDeploymentError({ message: `Mini ${miniId} not found` }),
            );
          }

          const base = agentUrl(mini.tailscaleFqdn, mini.agentPort);
          yield* callAgent(base, `/api/claws/${clawId}/start`, "POST");
        }),

      getMiniHealth: (miniId) =>
        Effect.gen(function* () {
          const [mini] = yield* db
            .select({
              tailscaleFqdn: macMinis.tailscaleFqdn,
              agentPort: macMinis.agentPort,
            })
            .from(macMinis)
            .where(eq(macMinis.id, miniId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({ message: `DB error: ${e}`, cause: e }),
              ),
            );

          if (!mini) {
            return yield* Effect.fail(
              new ClawDeploymentError({ message: `Mini ${miniId} not found` }),
            );
          }

          const base = agentUrl(mini.tailscaleFqdn, mini.agentPort);
          return yield* callAgent(base, "/api/health");
        }),
    };
  }),
);
```

### 6.5 Mac Mini Agent

The agent runs on each Mac Mini as a `launchd` system daemon. It's a lightweight HTTP server that accepts provisioning commands from the cloud backend over Tailscale.

**Location:** `cloud/mac-mini/agent/` (deployed separately to each Mini, not part of the Cloudflare Worker build)

#### Agent API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Mini health metrics (CPU, RAM, disk, uptime, claw count) |
| `POST` | `/api/provision` | Create macOS user, configure launchd, add tunnel route, start gateway |
| `POST` | `/api/deprovision` | Stop gateway, archive to R2, remove user, remove tunnel route |
| `GET` | `/api/claws` | List all claws with status |
| `GET` | `/api/claws/:clawId/status` | Single claw status (PID, memory, launchd state) |
| `POST` | `/api/claws/:clawId/restart` | Restart gateway (launchctl kickstart) |
| `POST` | `/api/claws/:clawId/start` | Start gateway (launchctl bootstrap) |
| `POST` | `/api/claws/:clawId/stop` | Stop gateway (launchctl bootout) |
| `POST` | `/api/claws/:clawId/backup` | Trigger manual R2 backup |
| `POST` | `/api/claws/:clawId/restore` | Restore from R2 backup |
| `POST` | `/api/claws/:clawId/migrate-out` | Prepare claw for migration (stop + archive) |
| `POST` | `/api/claws/:clawId/migrate-in` | Receive claw from another Mini (restore + start) |

#### Agent Security

- Listens only on Tailscale interface (100.x.x.x)
- Bearer token auth (shared secret between cloud backend and agent)
- Agent runs as root (needed for `sysadminctl` user creation and `launchctl` management)

#### Provisioning Script Flow (`/api/provision`)

```bash
#!/bin/bash
# cloud/mac-mini/agent/scripts/provision-claw.sh
# Called by the agent when provisioning a new claw

set -euo pipefail

CLAW_ID="$1"
MAC_USERNAME="$2"
LOCAL_PORT="$3"
GATEWAY_TOKEN="$4"
TUNNEL_HOSTNAME="$5"

# 1. Create macOS user (no admin, no login window)
sudo sysadminctl -addUser "$MAC_USERNAME" \
  -password "$(openssl rand -base64 32)" \
  -home "/Users/$MAC_USERNAME" \
  -shell /bin/zsh

# 2. Create .openclaw directory structure
sudo -u "$MAC_USERNAME" mkdir -p "/Users/$MAC_USERNAME/.openclaw/workspace"

# 3. Install OpenClaw gateway binary/config
# (Assumes openclaw is installed system-wide or per-user via Homebrew)
sudo -u "$MAC_USERNAME" cp /opt/openclaw/openclaw "/Users/$MAC_USERNAME/.local/bin/openclaw"

# 4. Write gateway config
sudo -u "$MAC_USERNAME" tee "/Users/$MAC_USERNAME/.openclaw/openclaw.json" > /dev/null <<EOF
{
  "gateway": {
    "host": "127.0.0.1",
    "port": $LOCAL_PORT,
    "token": "$GATEWAY_TOKEN"
  }
}
EOF

# 5. Write environment file
sudo -u "$MAC_USERNAME" tee "/Users/$MAC_USERNAME/.openclaw/.env" > /dev/null <<EOF
# Injected by Mac Mini agent
OPENCLAW_GATEWAY_TOKEN=$GATEWAY_TOKEN
# ... other env vars passed in request body
EOF

# 6. Create launchd plist
cat > "/Library/LaunchDaemons/com.mirascope.claw.$CLAW_ID.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mirascope.claw.$CLAW_ID</string>
    <key>UserName</key>
    <string>$MAC_USERNAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/$MAC_USERNAME/.local/bin/openclaw</string>
        <string>gateway</string>
        <string>start</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/$MAC_USERNAME/.openclaw</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>/Users/$MAC_USERNAME</string>
        <key>OPENCLAW_GATEWAY_PORT</key>
        <string>$LOCAL_PORT</string>
        <key>OPENCLAW_GATEWAY_HOST</key>
        <string>127.0.0.1</string>
    </dict>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/$MAC_USERNAME/.openclaw/gateway.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/$MAC_USERNAME/.openclaw/gateway.err</string>
</dict>
</plist>
EOF

# 7. Load the launchd service
sudo launchctl bootstrap system "/Library/LaunchDaemons/com.mirascope.claw.$CLAW_ID.plist"

# 8. Add Cloudflare Tunnel route
# cloudflared manages routes via its config. We update the config and signal reload.
# Alternative: use Cloudflare API to add ingress rule dynamically
cloudflared tunnel route dns "$TUNNEL_HOSTNAME" "$CLAW_ID"

echo "Provisioned $MAC_USERNAME on port $LOCAL_PORT"
```

#### Cloudflare Tunnel Configuration

Each Mini runs a single `cloudflared` connector. Ingress rules map tunnel hostnames to local ports:

```yaml
# /etc/cloudflared/config.yml (managed by agent)
tunnel: <tunnel-uuid>
credentials-file: /etc/cloudflared/credentials.json

ingress:
  # Auto-generated per claw:
  - hostname: claw-abc12345.claws.mirascope.io
    service: http://localhost:8100
  - hostname: claw-def67890.claws.mirascope.io
    service: http://localhost:8101
  # ... more claws ...
  
  # Catch-all
  - service: http_status:404
```

The agent updates this config file and sends `SIGHUP` to `cloudflared` (or restarts it) when routes change.

**Alternative (preferred for production):** Use the Cloudflare Tunnel API to manage ingress rules dynamically without touching the config file. The agent calls:

```
PUT https://api.cloudflare.com/client/v4/accounts/{account}/cfd_tunnel/{tunnel}/configurations
```

---

## 7. Modified Files

### 7.1 `cloud/api/claws-ws-proxy.ts` — WS Proxy Changes

The critical change: instead of routing WebSocket traffic through the dispatch worker, route it through the Cloudflare Tunnel hostname.

**Current** (line ~128 in `handleClawsWebSocket`):
```typescript
const dispatchBaseUrl =
  settings.openclawGatewayWsUrl ??
  settings.cloudflare.dispatchWorkerBaseUrl;
const upstreamUrl = `${dispatchBaseUrl.replace(/\/$/, "")}/${orgSlug}/${clawSlug}`;
```

**New:**
```typescript
// Look up the claw's tunnel hostname from DB
const tunnelHostname = claw.tunnelHostname;
if (!tunnelHostname) {
  return new Response("Claw not provisioned on infrastructure", { status: 503 });
}
const upstreamUrl = `wss://${tunnelHostname}`;
```

This requires adding `tunnelHostname` to the claw query in the handler (already selecting from `claws` table, just add the column).

**Full diff for the query:**

```diff
 const [claw] = yield* client
   .select({
     clawId: claws.id,
     organizationId: claws.organizationId,
     secretsEncrypted: claws.secretsEncrypted,
     secretsKeyId: claws.secretsKeyId,
+    tunnelHostname: claws.tunnelHostname,
   })
   .from(claws)
```

**Full diff for the URL construction:**

```diff
-    const dispatchBaseUrl =
-      settings.openclawGatewayWsUrl ??
-      settings.cloudflare.dispatchWorkerBaseUrl;
-    const upstreamUrl = `${dispatchBaseUrl.replace(/\/$/, "")}/${orgSlug}/${clawSlug}`;
+    // Route through Cloudflare Tunnel to the Mac Mini
+    if (!claw.tunnelHostname) {
+      return new Response("Claw infrastructure not ready", { status: 503 });
+    }
+    const upstreamUrl = `wss://${claw.tunnelHostname}`;
```

The `connectAndRelay` function needs two changes:

1. **Upstream URL** — already addressed above.
2. **Remove Bearer token from upstream fetch** — Currently, `connectAndRelay` sends `Authorization: Bearer ${gatewayToken}` in the WebSocket upgrade request to the dispatch worker, which uses it to identify and route to the correct claw container. With Cloudflare Tunnel, routing is by hostname (no Bearer token needed for routing). The gateway itself authenticates via the OpenClaw handshake protocol (challenge → connect with `auth.token`), NOT via HTTP headers. So the Bearer header must be removed from the upstream `fetch()` call.

```diff
-  const upstreamResponse = await fetch(gatewayBaseUrl, {
-    headers: {
-      Upgrade: "websocket",
-      Authorization: `Bearer ${gatewayToken}`,
-    },
-  });
+  const upstreamResponse = await fetch(gatewayBaseUrl, {
+    headers: {
+      Upgrade: "websocket",
+    },
+  });
```

The OpenClaw handshake (challenge → connect with token, scopes, client info → `proxy.ready`) remains unchanged — this is the gateway's own auth protocol and works the same regardless of transport.

### 7.2 `cloud/claws/deployment/live.ts` — Layer Swap

The existing `LiveDeploymentService` is replaced. Two options:

**Option A (clean):** Delete `cloud/claws/deployment/live.ts`, create `cloud/mac-mini/deployment/live.ts` (shown above). Update the Layer composition wherever `LiveDeploymentService` is provided.

**Option B (gradual):** Keep `live.ts`, add a feature flag:

```typescript
import { MacMiniDeploymentService } from "@/mac-mini/deployment/live";

export const LiveDeploymentService = process.env.DEPLOYMENT_BACKEND === "mac-mini"
  ? MacMiniDeploymentService
  : CloudflareDeploymentService; // existing impl renamed
```

**Recommendation:** Option A for POC. The dispatch worker code stays in the repo but is no longer wired in.

### 7.3 `cloud/claws/deployment/types.ts`

`ClawInstanceType` becomes less relevant since Mac Minis don't have per-container resource tiers. Options:

1. Keep the type but map all to the same resource allocation on Mini
2. Simplify to just `"standard"` for Mac Mini backend
3. Keep for billing tiers, decouple from infrastructure

**Recommendation:** Keep the enum for billing/plan purposes. The `MacMiniDeploymentService` ignores it for resource allocation.

### 7.4 `cloud/api/claws-internal.handlers.ts`

The `bootstrapClawHandler` is currently called by the dispatch worker via service binding. With Mac Minis, the agent needs this config too but fetches it differently.

**Option A:** Agent calls the same bootstrap endpoint over HTTPS (add bearer token auth for agent). Note: currently the bootstrap endpoint has NO token auth — the Cloudflare service binding is the sole trust boundary. Adding HTTP auth would be required.  
**Option B:** Cloud backend pushes config to agent during provision call.

**Recommendation:** Option B — push during provisioning. The agent doesn't need to call back to the cloud. This eliminates a network dependency and avoids adding auth to the bootstrap endpoint. The `provisionOnMini` request body includes all env vars and config.

The `resolveClawHandler` and `validateSessionHandler` are still needed for the WS proxy path (browser auth). No changes needed.

The `reportClawStatusHandler` can be adapted for the Mini agent to report status, or the cloud backend can poll the agent. **Recommendation:** Agent pushes heartbeats every 60s (reuse the existing status report endpoint with a new auth mechanism).

### 7.5 `cloud/db/schema/claws.ts`

Add columns (shown in section 5). The `clawsRelations` also needs a relation to `macMinis`:

```typescript
export const clawsRelations = relations(claws, ({ one, many }) => ({
  createdBy: one(users, { ... }),
  organization: one(organizations, { ... }),
  memberships: many(clawMemberships),
  macMini: one(macMinis, {
    fields: [claws.macMiniId],
    references: [macMinis.id],
  }),
}));
```

### 7.6 `cloud/api/claws.handlers.ts` — `createClawHandler`

The handler logic mostly stays the same because it uses `ClawDeploymentService` interface. But after provisioning, we need to persist the Mac Mini assignment:

```diff
 // After clawDeployment.provision()
+    // Persist Mac Mini assignment
+    yield* drizzle
+      .update(claws)
+      .set({
+        macMiniId: status.macMiniId,        // new field on ClawDeploymentStatus
+        tunnelHostname: status.tunnelHostname,
+        localPort: status.localPort,
+        macUsername: status.macUsername,
+      })
+      .where(eq(claws.id, claw.id));
```

This means `ClawDeploymentStatus` needs additional optional fields. The current interface (in `cloud/claws/deployment/service.ts`) is:

```typescript
export interface ClawDeploymentStatus {
  status: ClawStatus;
  url?: string;
  startedAt?: Date;
  errorMessage?: string;
  bucketName?: string;
  r2Credentials?: R2ScopedCredentials;
}
```

Add Mac Mini-specific fields (optional, so Cloudflare impl is unaffected during migration):

```typescript
export interface ClawDeploymentStatus {
  status: ClawStatus;
  url?: string;
  startedAt?: Date;
  errorMessage?: string;
  bucketName?: string;
  r2Credentials?: R2ScopedCredentials;
  // Mac Mini specific (optional — not present for Cloudflare deployments)
  macMiniId?: string;
  tunnelHostname?: string;
  localPort?: number;
  macUsername?: string;
}
```

**Compatibility note:** The `ClawDeploymentService` tag (`Context.Tag("DeploymentService")`) means only one implementation is provided per runtime. During migration, both `LiveDeploymentService` (Cloudflare) and `MacMiniDeploymentService` can coexist as separate Layer values — the feature flag in section 7.2 selects which one to provide.

---

## 8. Mac Mini Agent

### Technology Stack

- **Runtime:** Node.js (same stack as rest of Mirascope)
- **HTTP Framework:** Hono or bare `node:http` (minimal dependencies)
- **Process management:** launchd (the agent itself is a launchd daemon)
- **Shell execution:** `child_process.execFile` for `sysadminctl`, `launchctl`, etc.

### Agent launchd Plist

```xml
<!-- /Library/LaunchDaemons/com.mirascope.mini-agent.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mirascope.mini-agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>/opt/mirascope/mini-agent/server.js</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>UserName</key>
    <string>root</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>AGENT_PORT</key>
        <string>7600</string>
        <key>AGENT_TOKEN</key>
        <string>__AGENT_AUTH_TOKEN__</string>
        <key>CLOUD_CALLBACK_URL</key>
        <string>https://mirascope.com/api/internal</string>
        <key>CLOUD_CALLBACK_TOKEN</key>
        <string>__CLOUD_AUTH_TOKEN__</string>
    </dict>
    <key>StandardOutPath</key>
    <string>/var/log/mirascope/mini-agent.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/mirascope/mini-agent.err</string>
</dict>
</plist>
```

### Agent Health Check Response

```json
{
  "hostname": "mini-01",
  "uptime": 864000,
  "cpu": {
    "usage": 23.5,
    "cores": 12
  },
  "memory": {
    "used_gb": 18.2,
    "total_gb": 32.0
  },
  "disk": {
    "used_gb": 245,
    "total_gb": 1000
  },
  "load_average": [2.1, 1.8, 1.5],
  "claws": {
    "active": 10,
    "total": 12,
    "list": [
      {
        "claw_id": "abc-123",
        "username": "claw-abc12345",
        "port": 8100,
        "gateway_pid": 12345,
        "memory_mb": 512,
        "status": "running"
      }
    ]
  },
  "tunnel": {
    "status": "connected",
    "routes": 10
  }
}
```

---

## 9. Provisioning Flow

Complete flow when `createClawHandler` is called.

**Current `createClawHandler` flow for reference** (must be preserved):
1. `db.organizations.claws.create()` → DB row with status `pending`, generates `plaintextApiKey` and `botUserId`
2. `clawDeployment.provision({ clawId, instanceType })` → creates R2 bucket + scoped credentials, returns `ClawDeploymentStatus`
3. `crypto.randomUUID()` → generates gateway token
4. Build `routerBaseUrl` = `${settings.siteUrl}/router/v2/anthropic`
5. `encryptSecrets()` with ALL secrets: `ANTHROPIC_API_KEY` (from `claw.plaintextApiKey`), `ANTHROPIC_BASE_URL` (routerBaseUrl), `OPENCLAW_GATEWAY_TOKEN`, `PRIMARY_MODEL_ID` (from payload or `DEFAULT_CLAW_MODEL`), `OPENCLAW_SITE_URL` (settings.siteUrl), `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`
6. `UPDATE claws SET bucketName, secretsEncrypted, secretsKeyId, status='provisioning'`
7. `clawDeployment.warmUp(clawId)` → triggers cold start
8. If `settings.mockDeployment` (which is `false | PlanTier`, not just boolean): set status to `active` immediately
9. Track analytics event

**New flow with Mac Mini:**

```
1. createClawHandler (cloud/api/claws.handlers.ts)
   │
   ├── db.organizations.claws.create() → creates DB row (status: "pending")
   │
   ├── clawDeployment.provision({ clawId, instanceType })
   │   │  (cloud/mac-mini/deployment/live.ts)
   │   │
   │   ├── fleet.selectMini() → pick least-loaded active Mini
   │   │   (SELECT FROM mac_minis WHERE status='active' AND current_claws < max_claws
   │   │    ORDER BY current_claws ASC LIMIT 1)
   │   │
   │   ├── fleet.allocatePort(miniId) → find unused port in base_port..base_port+max_claws
   │   │
   │   ├── r2.createBucket("claw-backup-{clawId}") → backup bucket
   │   ├── r2.createScopedCredentials("claw-backup-{clawId}") → backup creds
   │   │
   │   ├── fleet.provisionOnMini(miniId, { clawId, macUsername, localPort, ... })
   │   │   │
   │   │   ├── HTTP POST http://{tailscale_fqdn}:7600/api/provision
   │   │   │   │  (Mini agent receives request)
   │   │   │   │
   │   │   │   ├── sysadminctl -addUser claw-{id8} ...
   │   │   │   ├── mkdir -p /Users/claw-{id8}/.openclaw/workspace
   │   │   │   ├── Write openclaw.json with gateway config
   │   │   │   ├── Write .env with all container env vars
   │   │   │   ├── Install openclaw binary (copy or symlink)
   │   │   │   ├── Create launchd plist at /Library/LaunchDaemons/com.mirascope.claw.{id}.plist
   │   │   │   ├── launchctl bootstrap system /Library/LaunchDaemons/...
   │   │   │   ├── Update cloudflared ingress (API or config file)
   │   │   │   └── Return { success: true }
   │   │   │
   │   │   └── UPDATE mac_minis SET current_claws = current_claws + 1
   │   │
   │   └── Return { status: "provisioning", bucketName, r2Credentials, tunnelHostname, ... }
   │
   ├── encryptSecrets({ GATEWAY_TOKEN, API_KEY, R2_CREDS, ... })
   │
   ├── UPDATE claws SET bucketName, secretsEncrypted, macMiniId,
   │   tunnelHostname, localPort, macUsername, status='provisioning'
   │
   ├── clawDeployment.warmUp(clawId)
   │   │  (sends POST to Mini agent /api/claws/{id}/start)
   │   └── (agent verifies gateway is running via launchctl)
   │
   └── Return claw to frontend
```

---

## 10. Deprovisioning & Archival

### User Cancels Subscription

```
1. deleteClawHandler (cloud/api/claws.handlers.ts)
   │
   ├── deployment.deprovision(clawId)
   │   │
   │   ├── fleet.getClawAssignment(clawId) → { miniId, macUsername, ... }
   │   │
   │   ├── fleet.deprovisionOnMini(miniId, { clawId, macUsername, archive: true })
   │   │   │
   │   │   ├── HTTP POST http://{tailscale}/api/deprovision
   │   │   │   │
   │   │   │   ├── launchctl bootout system/com.mirascope.claw.{id}
   │   │   │   ├── tar czf /tmp/claw-{id}-archive.tar.gz /Users/claw-{id8}/
   │   │   │   ├── Upload archive to R2 bucket claw-backup-{id}/archive.tar.gz
   │   │   │   ├── Remove cloudflared ingress rule
   │   │   │   ├── sysadminctl -deleteUser claw-{id8}
   │   │   │   └── rm -rf /Users/claw-{id8}
   │   │   │
   │   │   └── UPDATE mac_minis SET current_claws = current_claws - 1
   │   │
   │   └── (R2 backup bucket is KEPT — don't delete on deprovision)
   │
   ├── db.organizations.claws.delete(...)
   │   └── (or soft-delete: UPDATE claws SET archived_at = NOW(), status = 'paused')
   │
   └── Done
```

### User Re-subscribes (Restore)

```
1. createClawHandler with restore flag
   │
   ├── Provision new claw (normal flow)
   ├── After gateway starts, call Mini agent /api/claws/{id}/restore
   │   │
   │   ├── Download archive.tar.gz from R2
   │   ├── Extract to /Users/claw-{id8}/
   │   ├── Fix ownership: chown -R claw-{id8} /Users/claw-{id8}/
   │   └── Restart gateway
   │
   └── Delete old R2 archive (optional)
```

---

## 11. WebSocket Proxy Changes

The core change in `cloud/api/claws-ws-proxy.ts`:

### Before

```
Browser → WS Proxy → Dispatch Worker → Cloudflare Container → Gateway
```

### After

```
Browser → WS Proxy → Cloudflare Tunnel → Mac Mini → Gateway
```

The `connectAndRelay` function connects to `wss://claw-{id}.claws.mirascope.io` instead of the dispatch worker URL. The Cloudflare Tunnel terminates TLS and routes to `localhost:{port}` on the Mini. The gateway is listening there.

**Key difference:** The dispatch worker previously handled both routing AND container lifecycle. Now routing is purely Cloudflare Tunnel (infrastructure-level), and lifecycle is Mini agent (separate channel).

**The "Gateway button" URL** (the UI link users click to open their claw):

The frontend `getGatewayUrl()` in `cloud/app/routes/$orgSlug/claws/$clawSlug.tsx` currently constructs:
- **localhost:** Uses `VITE_OPENCLAW_GATEWAY_WS_URL` (http) or falls back to `http://localhost:18789/`
- **mirascope.dev:** `https://openclaw.mirascope.dev/{org}/{claw}/overview`
- **Production:** `https://openclaw.{subdomain}.mirascope.com/{org}/{claw}/overview` (or `openclaw.mirascope.com` for www/bare domain)

These URLs point to the dispatch worker, which serves the OpenClaw Control UI HTML with injected base path and WS boot script.

- **New:** The dispatch worker is gone. Options:
  1. **Proxy through main worker:** `/claws/{org}/{claw}` route on mirascope.com serves the gateway UI, WebSocket goes through existing WS proxy
  2. **Direct tunnel URL:** `https://claw-{id}.claws.mirascope.io` (but this exposes the gateway directly — need auth)
  3. **Keep dispatch worker hostname, update DNS:** Point `openclaw.mirascope.com` to a lightweight proxy worker that routes to tunnels

**Recommendation:** Option 1. The gateway UI is already served from mirascope.com. The WS proxy handles auth and relays. No separate gateway URL needed. Update `getGatewayUrl()` to point to the mirascope.com chat route instead of the dispatch worker URL.

---

## 12. Backup System

### Architecture

```
Mac Mini (local SSD — primary)
  │
  ├── Daily backup cron (2 AM local time)
  │   └── tar + upload to R2
  │
  └── Retention: 7 daily, 4 weekly, 3 monthly
```

### Backup Agent Script

```bash
#!/bin/bash
# /opt/mirascope/scripts/backup-claw.sh
# Called by cron or Mini agent

CLAW_ID="$1"
USERNAME="$2"
BUCKET="claw-backup-$CLAW_ID"

# Stop gateway briefly for consistent backup
sudo launchctl bootout system/com.mirascope.claw.$CLAW_ID 2>/dev/null || true
sleep 2

# Create tarball (exclude temp files, browser cache)
ARCHIVE="/tmp/claw-$CLAW_ID-$(date +%Y%m%d).tar.gz"
tar czf "$ARCHIVE" \
  --exclude='*/chromium-cache/*' \
  --exclude='*/.cache/*' \
  --exclude='*/node_modules/*' \
  -C /Users "$USERNAME"

# Restart gateway
sudo launchctl bootstrap system "/Library/LaunchDaemons/com.mirascope.claw.$CLAW_ID.plist"

# Upload to R2 via aws CLI (S3-compatible)
aws s3 cp "$ARCHIVE" "s3://$BUCKET/daily/$(date +%Y%m%d).tar.gz" \
  --endpoint-url https://<account-id>.r2.cloudflarestorage.com

# Cleanup old backups (keep 7 daily)
# ... retention logic ...

rm "$ARCHIVE"
```

### Backup launchd Plist (per-Mini, runs all claw backups)

```xml
<!-- /Library/LaunchDaemons/com.mirascope.backup-all.plist -->
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mirascope.backup-all</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/mirascope/scripts/backup-all-claws.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

---

## 13. Live Migration

For maintenance or rebalancing, claws can be migrated between Minis.

### Migration Flow

```
1. Cloud backend calls: fleet.migrateClawToMini(clawId, targetMiniId)
   │
   ├── Source Mini: POST /api/claws/{id}/migrate-out
   │   ├── Stop gateway (launchctl bootout)
   │   ├── Create archive of /Users/claw-{id8}/
   │   ├── Upload to R2 (temporary migration bucket)
   │   ├── Remove tunnel route
   │   └── Delete user (cleanup)
   │
   ├── Target Mini: POST /api/claws/{id}/migrate-in
   │   ├── Create macOS user
   │   ├── Download archive from R2
   │   ├── Extract to /Users/claw-{id8}/
   │   ├── Create launchd plist
   │   ├── Add tunnel route (same hostname, different backend)
   │   ├── Start gateway
   │   └── Verify health
   │
   ├── Update DB: claws.mac_mini_id = targetMiniId, local_port = newPort
   │
   └── Update source: mac_minis.current_claws -= 1
       Update target: mac_minis.current_claws += 1
```

**Downtime:** ~2-5 minutes per claw (stop, archive, transfer, restore, start). The WS proxy will get connection errors during this window, which the browser handles with reconnection.

**Draining a Mini:** Set `mac_minis.status = 'draining'`. No new claws assigned. Migrate all existing claws off. Then `status = 'offline'` for maintenance.

---

## 14. Security Model

### macOS User Isolation

- Each claw runs as a separate macOS user
- No admin privileges, no `sudo` access
- Home directory permissions: `drwx------` (700) — only the claw user can read
- Claw users cannot see each other's files or processes (standard Unix isolation)
- **Not** running in containers — this is user-level, not kernel-level isolation

### Filesystem Security

- **FileVault:** Enabled on all Minis (full-disk encryption at rest)
- **Gateway binary:** Read-only, owned by root, claws can execute but not modify
- **Agent scripts:** Owned by root, not writable by claw users
- **No shared directories** between claws

### Network Security

- **No inbound ports:** All traffic via Cloudflare Tunnel (outbound-only connection)
- **Tailscale:** Admin access only, ACL-restricted to Mirascope team
- **Mini agent:** Listens only on Tailscale interface, bearer token auth
- **Residential IP:** Claws browse the internet via the Mac Mini's residential IP (good for bot detection avoidance)

### SSH Hardening

- Password auth disabled (key-only via Tailscale SSH)
- Root login disabled (use admin account + sudo)
- Tailscale ACLs restrict which accounts can SSH
- No port 22 exposed to public internet

### Secrets Management

- Gateway tokens: Generated per-claw, encrypted in DB (`cloud/claws/crypto.ts`)
- Agent auth token: Stored in agent's launchd environment, not in filesystem
- R2 credentials: Per-claw scoped, stored encrypted in DB
- Claw env vars: Written to `/Users/claw-{id8}/.openclaw/.env` with 600 permissions

### Browser Sandboxing

- Each claw runs Playwright + Chromium under its own macOS user
- Separate Chromium profiles (different `--user-data-dir`)
- No cross-claw cookie/storage sharing
- Chromium runs without `--no-sandbox` (uses macOS sandbox)

---

## 15. Monitoring & Alerting

### Health Check Pipeline

```
Mini Agent (every 60s)
  │
  ├── POST /api/internal/claws/:clawId/status → Cloud DB
  │   (reuse existing reportClawStatusHandler)
  │
  └── POST /api/internal/mini/:miniId/health → Cloud DB
      (new endpoint for Mini-level health)
```

### What to Monitor

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Mini heartbeat | Agent → cloud | Missing for > 3 min |
| Gateway process alive | Agent (launchctl list) | PID missing |
| CPU usage | Agent (sysctl) | > 80% sustained 5 min |
| Memory usage | Agent (vm_stat) | > 90% |
| Disk usage | Agent (df) | > 85% |
| Tunnel connectivity | Cloudflare API | Tunnel disconnected |
| Gateway WS health | WS proxy connect test | Handshake fails |
| Backup success | Backup script | Failed for > 24h |

### Alerting

- **Discord webhook** to `#claws-ops` channel (or `#maintenance`)
- **Severity levels:**
  - 🔴 Critical: Mini offline, tunnel down, disk full
  - 🟡 Warning: High CPU/memory, backup failed, gateway restart loop
  - 🟢 Info: New claw provisioned, migration complete, backup success

### Dashboard

Initially manual (Discord alerts + agent health endpoint). Later: Grafana with Prometheus metrics exported by the agent.

---

## 16. Migration from Cloudflare

### Strategy

Migrate claws one at a time. Both systems run in parallel during migration.

### Per-Claw Migration Steps

```
1. Put claw in maintenance mode (status: "paused")
   └── Users see "Claw is being upgraded" message

2. Export claw data from Cloudflare Container
   ├── R2 bucket already has persistent data
   └── Download .openclaw directory from container via dispatch worker

3. Provision on Mac Mini (normal provision flow)

4. Restore data
   ├── Upload exported .openclaw directory to Mini
   └── Restore via agent /api/claws/{id}/restore

5. Update DB
   ├── claws.mac_mini_id = miniId
   ├── claws.tunnel_hostname = "claw-{id}.claws.mirascope.io"
   └── claws.local_port = allocated port

6. Test WS proxy connects to tunnel (not dispatch worker)
   └── The WS proxy uses claw.tunnel_hostname which is now set

7. Set status: "active"
   └── Users can connect again

8. Deprovision Cloudflare Container
   └── containers.destroy(hostname)
```

### Rollback Plan

If a migrated claw has issues:
1. Clear `tunnel_hostname` in DB → WS proxy falls back to dispatch worker URL
2. Recreate container on Cloudflare
3. Investigate and fix Mini setup
4. Re-migrate

### Timeline

- **Week 1:** POC — single claw on single Mini, validate end-to-end
- **Week 2-3:** Migrate 5-10 claws, monitor stability
- **Week 4+:** Migrate remaining claws, decommission dispatch worker

---

## 17. Environment Topology

### Environments

The Mirascope Cloud app defines four environments in `wrangler.jsonc`:

| Environment | URL | Description |
|-------------|-----|-------------|
| `local` | Local Vite dev server (`bun run dev`) | Developer's machine |
| `dev` | mirascope.dev (Cloudflare Worker) | Development environment |
| `staging` | staging.mirascope.com | Staging environment |
| `production` | mirascope.com | Production environment |

### Infrastructure per Environment

| Environment | Mac Hardware | Description |
|-------------|-------------|-------------|
| **Dev** | Old MacBook ("Dev MacBook") | Operates **exactly** like a production Mac Mini — same provisioning scripts, same agent, same Cloudflare Tunnel, same Tailscale. If it works here, it works in production. |
| **Staging** | Single Mac Mini | Staging environment for pre-production validation. |
| **Production** | Multiple Mac Minis | Production fleet. |

The Dev MacBook is **not** a second-class citizen. It runs the exact same software, config, and provisioning as production Minis. It lives on the same Tailnet and can be SSH'd into via Tailscale just like staging/production Minis.

### Tunnel Namespaces

Each environment has its own Cloudflare Tunnel namespace:

| Environment | Tunnel Pattern | Routes To |
|-------------|---------------|-----------|
| Dev | `*.claws.mirascope.dev` | Dev MacBook |
| Staging | `*.claws.staging.mirascope.com` | Staging Mac Mini |
| Production | `*.claws.mirascope.com` | Production Mac Minis |

For example, a claw `abc123` would have:
- Dev: `claw-abc123.claws.mirascope.dev`
- Staging: `claw-abc123.claws.staging.mirascope.com`
- Production: `claw-abc123.claws.mirascope.com`

---

## 18. Local Development

Two distinct development flows exist, serving different purposes.

### Flow 1: Local UI → Local Gateway (Debugging)

**Purpose:** Debug a specific claw's issues by running the Mirascope UI locally connected directly to a local OpenClaw gateway. This is **not** for developing the Mac Mini system — it's for debugging individual claw problems.

**Setup:**
1. Developer runs `openclaw gateway start` locally (or restores a claw's state from an R2 backup to debug their specific issue)
2. Developer runs local Mirascope Cloud (`bun run dev`)
3. The UI connects **directly** to the local gateway — no auth, no WS proxy, no provisioning
4. Direct WebSocket connection: `ws://localhost:{PORT}`

**How it bypasses the stack:**

```
Browser (localhost:5173)
  │
  └─ WS ──→ ws://localhost:{GATEWAY_PORT}
              │
              ▼
         Local OpenClaw Gateway
         (running via `openclaw gateway start`)
```

No Cloudflare Tunnel, no WS proxy, no session auth. Pure local debugging.

**Key implementation details:**
- `getGatewayUrl()` in `cloud/app/routes/$orgSlug/claws/$clawSlug.tsx` already has localhost handling that returns a direct URL
- `GatewayClient` in `cloud/app/lib/gateway-client.ts` currently connects via the WS proxy (`/api/ws/claws/:org/:claw`). For debugging mode, it needs a "direct connect" path that bypasses the proxy entirely
- Toggle via query param (e.g., `?direct=1`) or env var (e.g., `VITE_DIRECT_GATEWAY=true`)
- The existing `VITE_OPENCLAW_GATEWAY_WS_URL` env var partially supports this already
- No session auth needed — purely local debugging

### Flow 2: Local Cloud → Dev MacBook (Full-Stack Development)

**Purpose:** Full-stack development and testing of the Mac Mini system. Tests the **entire** provisioning, tunneling, and WebSocket stack end-to-end.

**Setup:**
1. Dev MacBook is provisioned exactly like a production Mac Mini (same scripts, agent, tunnel, Tailscale)
2. Dev MacBook runs Cloudflare Tunnel with namespace `*.claws.mirascope.dev`
3. Developer runs `bun run dev` locally (Vite dev server, `env.local` wrangler config)
4. Local dev server connects through the dev tunnel infrastructure

**How it works:**

```
Browser (localhost:5173)
  │
  ├─ HTTPS ──→ Local Vite Dev Server
  │
  └─ WSS ───→ /api/ws/claws/:org/:claw
                │  (WS proxy, same code as production)
                │
                ▼
         Cloudflare Tunnel (claw-{id}.claws.mirascope.dev)
                │
                ▼
         Dev MacBook
                │  - Same macOS user isolation
                │  - Same launchd services
                │  - Same Mini agent
                │
                ▼
         OpenClaw Gateway (per-user launchd service)
```

This is identical to the production flow — the only differences are:
- Which Minis are in the fleet DB (one entry: the Dev MacBook)
- Which tunnel namespace is used (`mirascope.dev` instead of `mirascope.com`)

**Key implementation details:**
- `env.local` in `wrangler.jsonc` needs a setting pointing tunnel URLs to the dev namespace (`*.claws.mirascope.dev`)
- `MacMiniDeploymentService` works identically — the only difference is the `mac_minis` table in local dev Postgres has one entry: the Dev MacBook
- Database: local dev uses `localConnectionString` to local Postgres
- Auth works the same as production (session-based)
- Full provisioning flow: create claw → find Dev MacBook → SSH/agent → create user → start gateway → tunnel route → ready

**Why this matters:** If the full stack works against the Dev MacBook, it works in production. The Dev MacBook is the same environment, just with one Mini instead of many.

### When to Use Which Flow

| Scenario | Flow |
|----------|------|
| "This claw is behaving weirdly, let me reproduce locally" | Flow 1 (Direct) |
| "I'm building the provisioning system and need to test end-to-end" | Flow 2 (Dev MacBook) |
| "I changed the WS proxy code, does it still work?" | Flow 2 (Dev MacBook) |
| "I need to debug a gateway plugin issue" | Flow 1 (Direct) |
| "I'm testing the fleet scheduler / tunnel routing" | Flow 2 (Dev MacBook) |

---

## 19. Implementation Phases

### Phase 0: Dev MacBook Bootstrap

**Goal:** Before touching any Mac Mini hardware, prove the entire stack works end-to-end using a Dev MacBook as the target machine, with `bun run dev` running locally.

**Hardware:** Any spare MacBook (the "Dev MacBook"). Operates on William's local network + Tailscale.

#### Step 1: Admin Account Setup on Dev MacBook

Set up the Dev MacBook so it can be remotely managed and have claw accounts provisioned on it.

**Prerequisites:** Fresh macOS install (or clean existing Mac). You'll need physical access for initial setup.

**Checklist:**

```bash
# 1. Create clawadmin account (only admin account on this machine)
#    Do this in System Settings → Users & Groups during initial macOS setup,
#    or from an existing admin account:
sudo sysadminctl -addUser clawadmin -password '<STRONG_PASSWORD>' -admin
# Log in as clawadmin, demote/remove any other admin accounts

# 2. Enable Remote Login (SSH)
sudo systemsetup -setremotelogin on

# 3. Install Tailscale
#    Download from https://tailscale.com/download/mac or:
brew install --cask tailscale
#    Open Tailscale, sign in, then set hostname:
sudo tailscale set --hostname dev-macbook
#    Verify: `tailscale status` shows "dev-macbook" connected to your Tailnet

# 4. SSH key auth only
#    From your main machine, copy your SSH key:
ssh-copy-id clawadmin@dev-macbook  # uses Tailscale MagicDNS
#    Verify key login works, THEN disable password auth:
sudo sed -i '' 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i '' 's/^#*ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config
sudo launchctl stop com.openssh.sshd
sudo launchctl start com.openssh.sshd

# 5. Install core tools
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install node@22 git
npm install -g openclaw

# 6. Install Playwright Chromium to shared location
sudo mkdir -p /opt/playwright-browsers
sudo chown clawadmin:staff /opt/playwright-browsers
PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers npx playwright install chromium
# Verify:
ls /opt/playwright-browsers/chromium-*/chrome-mac/Chromium.app

# 7. Enable FileVault
sudo fdesetup enable
# Save the recovery key securely!

# 8. Enable macOS firewall (block all inbound)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setblockall on
# Tailscale and cloudflared use outbound connections, so they're unaffected

# 9. Install cloudflared and create tunnel
brew install cloudflared
cloudflared tunnel login  # authenticates with Cloudflare account
cloudflared tunnel create dev-macbook
# Note the tunnel UUID from output — you'll need it below

# Configure tunnel for *.claws.mirascope.dev
cloudflared tunnel route dns dev-macbook '*.claws.mirascope.dev'

# Write initial config (no claw routes yet — catch-all only)
sudo mkdir -p /etc/cloudflared
sudo tee /etc/cloudflared/config.yml > /dev/null <<EOF
tunnel: <TUNNEL_UUID>
credentials-file: /Users/clawadmin/.cloudflared/<TUNNEL_UUID>.json

ingress:
  - service: http_status:404
EOF

# 10. Install cloudflared as launchd service
sudo cloudflared service install
# Verify: sudo launchctl list | grep cloudflared

# 11. Create fleet scripts directory
sudo mkdir -p /opt/claw-fleet
sudo chown clawadmin:staff /opt/claw-fleet
```

**Verification:**
- [ ] Can SSH from main machine: `ssh clawadmin@dev-macbook`
- [ ] Password auth rejected: `ssh -o PubkeyAuthentication=no clawadmin@dev-macbook` → denied
- [ ] `node --version` → v22.x
- [ ] `openclaw --version` → works
- [ ] Playwright Chromium exists at `/opt/playwright-browsers/chromium-*`
- [ ] `sudo fdesetup status` → "FileVault is On"
- [ ] `cloudflared tunnel list` → shows `dev-macbook` tunnel
- [ ] `sudo launchctl list | grep cloudflared` → running

#### Step 2: Provisioning a Claw from Local Dev Server

**Goal:** Run `bun run dev` locally, create a claw through the UI (or API), and have it provision a real macOS user account on the Dev MacBook.

**⚠️ SSH from Cloudflare Workers:** The Mirascope Cloud app runs as a Cloudflare Worker in staging/production — Workers can't SSH directly. Three options:

| Option | How | When to Use |
|--------|-----|-------------|
| **A: Mac Mini Agent** | HTTP API on each Mini, called over Tailscale | Phase 1+ (production) |
| **B: Provisioning Queue** | CF Worker enqueues, separate process dequeues + SSHs | Alternative to A |
| **C: Direct SSH from local dev** | `bun run dev` runs as a local Node process — CAN SSH directly | **Phase 0 only** |

**For Phase 0, use Option C.** It's the simplest path for the POC. This won't work when deployed as a CF Worker — the Mac Mini Agent (Option A, detailed in [Section 8](#8-mac-mini-agent)) is needed for Phase 1+.

##### Database Changes

```sql
-- Add mac_minis table (just one row for now: the Dev MacBook)
-- See Section 5 for full schema. Minimum viable for Phase 0:
CREATE TABLE mac_minis (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hostname        TEXT NOT NULL UNIQUE,
  tailscale_ip    TEXT NOT NULL,
  tailscale_fqdn  TEXT NOT NULL,
  tunnel_id       TEXT NOT NULL,
  max_claws       INTEGER NOT NULL DEFAULT 12,
  current_claws   INTEGER NOT NULL DEFAULT 0,
  base_port       INTEGER NOT NULL DEFAULT 8100,
  status          TEXT NOT NULL DEFAULT 'active',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Seed the Dev MacBook
INSERT INTO mac_minis (hostname, tailscale_ip, tailscale_fqdn, tunnel_id)
VALUES ('dev-macbook', '100.x.x.x', 'dev-macbook.tail1234.ts.net', '<TUNNEL_UUID>');

-- Add columns to claws table
ALTER TABLE claws ADD COLUMN mac_mini_id UUID REFERENCES mac_minis(id);
ALTER TABLE claws ADD COLUMN tunnel_hostname TEXT;
ALTER TABLE claws ADD COLUMN local_port INTEGER;
ALTER TABLE claws ADD COLUMN mac_username TEXT;
```

Run the migration locally against the dev Postgres.

##### MacMiniDeploymentService (Phase 0 — Direct SSH)

Create `cloud/claws/deployment/mac-mini.ts`:

- Implements `ClawDeploymentServiceInterface` (same interface as the existing Cloudflare deployment)
- **`provision(config)`:**
  1. Pick a Mini from `mac_minis` table (only one for now)
  2. Allocate next available port (`base_port` + offset, query `claws.local_port WHERE mac_mini_id = ?` to find gaps)
  3. SSH to Dev MacBook via Tailscale and run provisioning commands:
     - `sysadminctl -addUser claw-{id8}` — create macOS user
     - Configure shell env: write `/Users/claw-{id8}/.zshrc` with Homebrew, Node, Playwright paths (`export PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers`)
     - `openclaw init` in user's home dir (or manually write `~/.openclaw/openclaw.json`)
     - Write `openclaw.json` with `{ "gateway": { "host": "127.0.0.1", "port": <allocated_port>, "token": "<gateway_token>" } }`
     - Create launchd plist at `/Library/LaunchDaemons/com.mirascope.claw.{id}.plist` (see [Section 6.5](#65-mac-mini-agent) for template)
     - `launchctl bootstrap system <plist_path>` — load and start the service
     - Add ingress rule to `/etc/cloudflared/config.yml` mapping `claw-{id}.claws.mirascope.dev → http://localhost:{port}`
     - Restart cloudflared: `launchctl kickstart -k system/com.cloudflare.cloudflared`
  4. Create R2 bucket + scoped credentials (reuse existing `CloudflareR2Service` — backups still go to R2)
  5. Return status with `tunnelHostname: claw-{id}.claws.mirascope.dev`
- **`warmUp(clawId)`:** HTTP GET to `https://claw-{id}.claws.mirascope.dev` — verify tunnel + gateway responds
- **`deprovision(clawId)`:** SSH in → `launchctl bootout` → remove ingress rule → restart cloudflared → `sysadminctl -deleteUser` → delete R2 bucket
- **`getStatus(clawId)`:** SSH in → `launchctl print system/com.mirascope.claw.{id}` → check PID exists; optionally `curl http://localhost:{port}` from the Mini
- **`restart(clawId)`:** SSH in → `launchctl kickstart -k system/com.mirascope.claw.{id}`

**SSH implementation (Phase 0 only):** Use `node:child_process` to run `ssh clawadmin@dev-macbook '<command>'`. Keep it simple — no SSH library needed. Example:

```typescript
import { execFile } from "node:child_process";
import { promisify } from "node:util";
const execFileAsync = promisify(execFile);

async function sshExec(host: string, command: string): Promise<string> {
  const { stdout } = await execFileAsync("ssh", [
    "-o", "StrictHostKeyChecking=accept-new",
    `clawadmin@${host}`,
    command,
  ]);
  return stdout;
}
```

Create `cloud/claws/deployment/mac-mini-fleet.ts` for fleet operations (Mini selection, port allocation queries).

##### WS Proxy Update (`cloud/api/claws-ws-proxy.ts`)

```diff
-    const dispatchBaseUrl =
-      settings.openclawGatewayWsUrl ??
-      settings.cloudflare.dispatchWorkerBaseUrl;
-    const upstreamUrl = `${dispatchBaseUrl.replace(/\/$/, "")}/${orgSlug}/${clawSlug}`;
+    // Route through Cloudflare Tunnel to the Mac Mini
+    if (!claw.tunnelHostname) {
+      return new Response("Claw infrastructure not ready", { status: 503 });
+    }
+    const upstreamUrl = `wss://${claw.tunnelHostname}`;
```

Also remove the `Authorization: Bearer` header from the upstream WebSocket upgrade — tunnel routes by hostname, gateway authenticates via the OpenClaw handshake protocol (see [Section 7.1](#71-cloudapi claws-ws-proxyts--ws-proxy-changes) for full diff).

##### Wire It Up

| File | Action |
|------|--------|
| `cloud/claws/deployment/mac-mini.ts` | **Create** — `MacMiniDeploymentService` |
| `cloud/claws/deployment/mac-mini-fleet.ts` | **Create** — fleet ops (Mini selection, port allocation) |
| `cloud/claws/deployment/live.ts` | **Modify** — swap Layer to use `MacMiniDeploymentService` (or create env-based toggle) |
| `cloud/api/claws-ws-proxy.ts` | **Modify** — read `tunnel_hostname` from DB, connect there |
| `cloud/db/schema/claws.ts` | **Modify** — add `macMiniId`, `tunnelHostname`, `localPort`, `macUsername` columns |
| `cloud/db/schema/mac-minis.ts` | **Create** — `mac_minis` table |
| `cloud/db/migrations/XXXX_add_mac_minis.ts` | **Create** — migration |

The `createClawHandler` flow stays the same — it calls `clawDeployment.provision()` which now provisions on the Dev MacBook instead of spawning a Cloudflare container.

#### Step 3: Local Claw Dashboard CLI

**Goal:** A one-command tool to connect the OpenClaw Control UI directly to any gateway — no auth, no proxy, no Mirascope Cloud.

```bash
# Connect to a remote claw via tunnel:
npx mirascope-claw-debug --gateway wss://claw-xxx.claws.mirascope.dev

# Connect to a local gateway:
npx mirascope-claw-debug --gateway ws://localhost:18789
```

**What it does:**
1. Starts a tiny local HTTP server (e.g. on port 9999)
2. Serves the OpenClaw Control UI HTML with the gateway URL pre-configured
3. Opens the browser to `http://localhost:9999`
4. You're chatting with the claw — no sign-in, no proxy, direct WebSocket

**Implementation options:**
- If OpenClaw already has a built-in Control UI (check the dispatch worker — it likely serves one), this may just be documenting how to hit it directly
- Otherwise: a small script that serves a single HTML page importing the Control UI JS bundle, with `GATEWAY_URL` injected as a global
- Package as `cloud/tools/claw-debug/` or as a standalone npm package

**The key requirement:** ONE COMMAND to open a browser connected to a gateway. No setup, no config files.

#### Step 4: Local Vite Dev Server → Dev MacBook Gateway

**Goal:** Full production-identical stack working end-to-end: local Mirascope Cloud UI → WS proxy → Cloudflare Tunnel → Dev MacBook → OpenClaw gateway.

**Prerequisites:** Steps 1-2 complete.

**Setup:**
1. Local Postgres has a `mac_minis` row for the Dev MacBook (from Step 2)
2. `MacMiniDeploymentService` is wired in as the deployment Layer
3. `bun run dev` with `CLOUDFLARE_ENV=local`

**What to test:**

```
Browser (localhost:5173)
  │
  ├─ HTTPS ──→ Local Vite Dev Server (bun run dev)
  │
  └─ WSS ───→ /api/ws/claws/:org/:claw
                │  (WS proxy — same code as production)
                │
                ▼
         Cloudflare Tunnel (claw-{id}.claws.mirascope.dev)
                │
                ▼
         Dev MacBook → OpenClaw Gateway (launchd service)
```

**Implementation notes:**
- `getGatewayUrl()` in the frontend needs updating — the "Gateway" button should use the Mirascope Cloud chat route (which goes through the WS proxy → tunnel), not the old dispatch worker URL
- If `tunnelHostname` is set on the claw, the WS proxy routes through the tunnel automatically (Step 2 change)
- Auth works the same as production (local dev session auth)

**Verification checklist:**
- [ ] Local Vite server starts and loads the Mirascope UI
- [ ] Can sign in (local dev auth)
- [ ] Can create a new claw (provisions on Dev MacBook)
- [ ] Claw status transitions: `pending` → `provisioning` → `active`
- [ ] Can open chat with the claw
- [ ] Messages flow: UI → WS proxy → Cloudflare Tunnel → Dev MacBook gateway → LLM → back
- [ ] Can restart the claw from the UI
- [ ] Can delete the claw (deprovisions from Dev MacBook)

---

### Phase 1: POC on Mac Mini Hardware (1 week)

**Goal:** Single Claw running on a single Mac Mini, WebSocket working end-to-end.

**Hardware:** M4 16GB/512GB at William's home, WiFi.

**Tasks:**
1. Set up Mac Mini using the same process as Step 1 (Dev MacBook already validated the scripts)
2. Create minimal Mini agent (health + provision + status endpoints only) — replaces Phase 0's direct SSH approach
3. Manually provision one Claw via the agent API
4. Test: browser → WS proxy → tunnel → Mini → gateway ✓
5. Test: Playwright/Chromium working under claw user ✓

**Files changed:**
- `cloud/db/schema/claws.ts` — already has `tunnelHostname`, `macMiniId`, `localPort`, `macUsername` from Phase 0
- `cloud/api/claws-ws-proxy.ts` — already uses `tunnelHostname` from Phase 0
- New: `cloud/mac-mini/agent/server.ts` (full agent, replaces direct SSH)
- New: `cloud/mac-mini/agent/scripts/provision-claw.sh`
- Modified: `cloud/claws/deployment/mac-mini.ts` — switch from direct SSH to calling the Mini agent over HTTP

### Phase 2: Automated Provisioning (1-2 weeks)

**Goal:** `createClawHandler` provisions on Mac Mini instead of Cloudflare.

**Tasks:**
1. Create `mac_minis` DB table (if not already done in Phase 0)
2. Implement full `MacMiniDeploymentService` (agent-based, not SSH)
3. Implement `MacMiniFleetService` (live)
4. Full Mini agent with all endpoints
5. Swap `LiveDeploymentService` → `MacMiniDeploymentService`
6. Test create/delete/restart flows

**Files:**
- New: `cloud/db/schema/mac-minis.ts` (if not from Phase 0)
- New: `cloud/mac-mini/deployment/live.ts`
- New: `cloud/mac-mini/deployment/types.ts`
- New: `cloud/mac-mini/fleet/service.ts`
- New: `cloud/mac-mini/fleet/live.ts`
- Modified: `cloud/claws/deployment/service.ts` (add fields to `ClawDeploymentStatus`)
- Modified: `cloud/api/claws.handlers.ts` (persist Mini assignment)
- Modified: Layer composition (swap deployment service)

### Phase 3: Migration & Backup (1 week)

**Goal:** Migrate existing Cloudflare claws to Mac Mini. Daily backups running.

**Tasks:**
1. Migration script/tooling
2. Backup system (cron + R2 upload)
3. Restore functionality
4. Migrate all existing claws
5. Verify all claws healthy on Mini

### Phase 4: Production Hardening (1-2 weeks)

**Goal:** Multi-Mini fleet, monitoring, live migration.

**Tasks:**
1. Add second Mini (M4 Pro 32GB)
2. Fleet scheduler (placement optimization)
3. Live migration between Minis
4. Monitoring + Discord alerts
5. Draining workflow for maintenance
6. Decommission dispatch worker
7. Move to Ethernet
8. Stress test: 12 claws per Mini

### Phase 5: Scale (ongoing)

- Add more Minis as demand grows
- Move to colo/MacStadium for better uptime
- Advanced scheduling (CPU/memory aware placement)
- Grafana dashboard
- Automated Mini bootstrapping (MDM/Ansible)

---

## 20. Open Questions

1. **Cloudflare Tunnel API vs config file?** — API is cleaner for dynamic routes but has rate limits. Config file + reload is simpler for POC. **Lean:** API for production.

2. **Agent auth mechanism?** — Shared bearer token is simple. Mutual TLS over Tailscale is more secure. **Lean:** Bearer token for POC, evaluate mTLS later.

3. **Instance types on Mac Mini?** — Do we still differentiate resource allocations per claw, or are all claws equal on a Mini? **Lean:** All equal for now. Differentiate by which Mini they're placed on (16GB vs 32GB).

4. **OpenClaw binary distribution?** — How does the gateway binary get onto Minis? Manual copy? Homebrew tap? GitHub releases? **Lean:** Manual for POC, GitHub releases for production.

5. **Chromium per-claw vs shared?** — Each claw gets its own Chromium, or share a pool? **Lean:** Per-claw (isolation), but lazy-start (only when browser is needed).

6. **Mini bootstrapping?** — How to set up a new Mini from scratch? **Lean:** Manual script for now, Ansible playbook later.

7. **What happens during WiFi outage?** — Tunnel disconnects, WS proxy returns 503. Claws keep running locally. Reconnects automatically when WiFi returns. **Acceptable for POC.** Ethernet + UPS for production.

8. **DNS for tunnel hostnames?** — `claw-{id}.claws.mirascope.io` needs a wildcard CNAME to the tunnel. Cloudflare manages this if the domain is on Cloudflare. **Action:** Confirm `mirascope.io` or use `claws.mirascope.com`.

9. **Gateway config delivery?** — Push during provision (agent stores locally) vs pull on start (agent calls cloud API). **Lean:** Push. Agent stores in `.openclaw/` directory. Updates via restart (re-push config, restart gateway).

10. **Billing implications?** — Cloudflare Containers had per-container cost. Mac Mini is fixed cost. Update billing model? **Action:** William to decide.
