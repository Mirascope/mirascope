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
 *   ├── updateConfig(...)    → Update deployment config
 *   ├── resize(...)          → Change instance type
 *   ├── getStorage(...)      → Read from claw storage
 *   ├── putStorage(...)      → Write to claw storage
 *   └── deleteStorage(...)   → Delete from claw storage
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
 *   const status = yield* deployment.provision({
 *     clawId: "claw-123",
 *     clawSlug: "my-claw",
 *     organizationSlug: "my-org",
 *     instanceType: "basic",
 *     routerApiKey: "key_abc",
 *   });
 *
 *   console.log(status.status); // "active"
 *   console.log(status.url);    // "my-claw.my-org.mirascope.com"
 * });
 * ```
 */

import { Context, Effect } from "effect";

import type { ClawInstanceType, ClawStatus } from "@/claws/deployment/types";

import { DeploymentError } from "@/claws/deployment/errors";

/**
 * Configuration passed to the deployment service when provisioning a claw.
 */
export interface DeploymentConfig {
  clawId: string;
  clawSlug: string;
  organizationSlug: string;
  instanceType: ClawInstanceType;
  routerApiKey: string;
  secretsEncrypted?: string;
  secretsKeyId?: string;
}

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
 */
export interface DeploymentServiceInterface {
  /** Provision and deploy a new claw. */
  readonly provision: (
    config: DeploymentConfig,
  ) => Effect.Effect<DeploymentStatus, DeploymentError>;

  /** Remove a claw deployment. */
  readonly deprovision: (
    clawId: string,
  ) => Effect.Effect<void, DeploymentError>;

  /** Get the current deployment status for a claw. */
  readonly getStatus: (
    clawId: string,
  ) => Effect.Effect<DeploymentStatus, DeploymentError>;

  /** Restart a running claw. */
  readonly restart: (
    clawId: string,
  ) => Effect.Effect<DeploymentStatus, DeploymentError>;

  /** Update deployment configuration for a running claw. */
  readonly updateConfig: (
    clawId: string,
    config: Partial<DeploymentConfig>,
  ) => Effect.Effect<DeploymentStatus, DeploymentError>;

  /** Resize a claw's instance type. */
  readonly resize: (
    clawId: string,
    instanceType: ClawInstanceType,
  ) => Effect.Effect<DeploymentStatus, DeploymentError>;

  /** Read a file from claw storage. */
  readonly getStorage: (
    clawId: string,
    path: string,
  ) => Effect.Effect<Uint8Array, DeploymentError>;

  /** Write a file to claw storage. */
  readonly putStorage: (
    clawId: string,
    path: string,
    data: Uint8Array,
  ) => Effect.Effect<void, DeploymentError>;

  /** Delete a file from claw storage. */
  readonly deleteStorage: (
    clawId: string,
    path: string,
  ) => Effect.Effect<void, DeploymentError>;
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
