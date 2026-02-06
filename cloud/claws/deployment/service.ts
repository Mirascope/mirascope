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

import type { ClawStatus, OpenClawConfig } from "@/claws/deployment/types";

import { DeploymentError } from "@/claws/deployment/errors";

/**
 * Status returned by deployment operations.
 */
export interface DeploymentStatus {
  status: ClawStatus;
  url?: string;
  startedAt?: Date;
  errorMessage?: string;
}

/**
 * Deployment service interface.
 *
 * Provides operations for managing claw deployments on the underlying
 * infrastructure (Moltworker / Cloudflare Workers for Platforms).
 *
 * Provisioning accepts an `OpenClawConfig` — the full runtime config that the
 * dispatch worker needs to start a container (identity, instance type, R2
 * credentials, container env vars with decrypted secrets).
 *
 * Storage operations (R2 bucket access) are intentionally excluded — the cloud
 * backend can access R2 directly using the per-claw credentials.
 */
export interface DeploymentServiceInterface {
  /** Provision and deploy a new claw. */
  readonly provision: (
    config: OpenClawConfig,
  ) => Effect.Effect<DeploymentStatus, DeploymentError>;

  /** Remove a claw deployment and release resources. */
  readonly deprovision: (
    clawId: string,
  ) => Effect.Effect<void, DeploymentError>;

  /** Get the current deployment status for a claw. */
  readonly getStatus: (
    clawId: string,
  ) => Effect.Effect<DeploymentStatus, DeploymentError>;

  /** Restart a running claw (fetches fresh config on next startup). */
  readonly restart: (
    clawId: string,
  ) => Effect.Effect<DeploymentStatus, DeploymentError>;

  /** Update a running claw's configuration (secrets, instance type, etc.). */
  readonly update: (
    clawId: string,
    config: Partial<OpenClawConfig>,
  ) => Effect.Effect<DeploymentStatus, DeploymentError>;
}

/**
 * Deployment service Effect tag.
 *
 * Use `yield* DeploymentService` to access the deployment service in Effect
 * generators. Provide via `MockDeploymentService` for testing or the real
 * Moltworker implementation in production.
 */
export class DeploymentService extends Context.Tag("DeploymentService")<
  DeploymentService,
  DeploymentServiceInterface
>() {}
