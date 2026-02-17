/**
 * @fileoverview Deployment service interface for claw provisioning and management.
 *
 * Defines the `DeploymentService` Effect interface that abstracts claw deployment
 * operations. The initial implementation is a mock (`MockDeploymentService`) that
 * simulates provisioning with `Effect.sleep`. Dandelion will later provide a real
 * implementation backed by Moltworker (Cloudflare Workers for Platforms).
 *
 * ## Architecture
 *
 * ```
 * DeploymentService (Context.Tag)
 *   ├── provision(config)    → Deploy a new claw
 *   ├── deprovision(clawId)  → Remove a claw deployment
 *   ├── getStatus(clawId)    → Check deployment health
 *   ├── restart(clawId)      → Restart a running claw
 *   └── update(clawId, ...)  → Update config (secrets, instance type, etc.)
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { DeploymentService } from "@/claws/deployment/service";
 *
 * const program = Effect.gen(function* () {
 *   const deployment = yield* DeploymentService;
 *
 *   const status = yield* deployment.provision(config);
 *   console.log(status.status); // "active"
 *   console.log(status.url);    // "https://my-claw.my-org.mirascope.com"
 * });
 * ```
 */

import { Context, Effect } from "effect";

import type {
  ClawStatus,
  OpenClawDeployConfig,
  ProvisionClawConfig,
} from "@/claws/deployment/types";
import type { R2ScopedCredentials } from "@/cloudflare/r2/types";

import { ClawDeploymentError } from "@/claws/deployment/errors";

/**
 * Status returned by deployment operations.
 */
export interface ClawDeploymentStatus {
  status: ClawStatus;
  url?: string;
  startedAt?: Date;
  errorMessage?: string;
  /** R2 bucket name created during provisioning (only present after provision). */
  bucketName?: string;
  /** R2 scoped credentials created during provisioning (only present after provision). */
  r2Credentials?: R2ScopedCredentials;
  /** Mac Mini ID (only present for mac-mini deployments). */
  miniId?: string;
  /** Port allocated on the Mac Mini (only present for mac-mini deployments). */
  miniPort?: number;
  /** Tunnel hostname for direct WS connection (only present for mac-mini deployments). */
  tunnelHostname?: string;
}

/**
 * Deployment service interface.
 *
 * Provides operations for managing claw deployments on the underlying
 * infrastructure (Moltworker / Cloudflare Workers for Platforms).
 *
 * Provisioning accepts a `ProvisionClawConfig` — just the identity and instance
 * type. R2 buckets and credentials are *created* during provisioning and
 * returned in the status.
 *
 * Storage operations (R2 bucket access) are intentionally excluded — the cloud
 * backend can access R2 directly using the per-claw credentials.
 */
export interface ClawDeploymentServiceInterface {
  /** Provision and deploy a new claw. */
  readonly provision: (
    config: ProvisionClawConfig,
  ) => Effect.Effect<ClawDeploymentStatus, ClawDeploymentError>;

  /** Remove a claw deployment and release resources. */
  readonly deprovision: (
    clawId: string,
  ) => Effect.Effect<void, ClawDeploymentError>;

  /** Get the current deployment status for a claw. */
  readonly getStatus: (
    clawId: string,
  ) => Effect.Effect<ClawDeploymentStatus, ClawDeploymentError>;

  /** Restart a running claw (fetches fresh config on next startup). */
  readonly restart: (
    clawId: string,
  ) => Effect.Effect<ClawDeploymentStatus, ClawDeploymentError>;

  /** Update a running claw's configuration (secrets, instance type, etc.). */
  readonly update: (
    clawId: string,
    config: Partial<OpenClawDeployConfig>,
  ) => Effect.Effect<ClawDeploymentStatus, ClawDeploymentError>;

  /**
   * Warm up a claw's container, triggering a cold start on the dispatch worker.
   *
   * This is intentionally separate from `provision` so the caller can persist
   * R2 credentials to the database between provisioning infrastructure and
   * triggering the dispatch worker (which reads credentials via the bootstrap API).
   */
  readonly warmUp: (clawId: string) => Effect.Effect<void, ClawDeploymentError>;
}

/**
 * Deployment service Effect tag.
 *
 * Use `yield* DeploymentService` to access the deployment service in Effect
 * generators. Provide via `MockDeploymentService` for testing or the real
 * Moltworker implementation in production.
 */
export class ClawDeploymentService extends Context.Tag("DeploymentService")<
  ClawDeploymentService,
  ClawDeploymentServiceInterface
>() {}
