/**
 * @fileoverview Live deployment service backed by Cloudflare infrastructure.
 *
 * Orchestrates claw provisioning by composing two lower-level services:
 *
 * 1. **CloudflareR2Service** — Create/delete R2 buckets, create/revoke
 *    scoped credentials for per-claw storage.
 *
 * 2. **CloudflareContainerService** — Warm up, restart gateway, recreate,
 *    destroy, and inspect containers via the dispatch worker.
 *
 * ## Provision Flow
 *
 * ```
 * provision(config: OpenClawConfig)
 *   1. Create R2 bucket "claw-{clawId}"
 *   2. Create scoped R2 credentials for that bucket
 *   3. Return DeploymentStatus { status: "provisioning", url, bucketName, r2Credentials }
 * ```
 *
 * The caller is responsible for persisting the R2 credentials to the database
 * and then calling `warmUp(clawId)` separately. This separation ensures the
 * dispatch worker can read credentials from the bootstrap API before it starts.
 *
 * ## Warm-Up Flow
 *
 * ```
 * warmUp(clawId)
 *   1. Send HTTP request to dispatch worker hostname
 *   2. Dispatch worker fetches bootstrap config (incl. R2 credentials)
 *   3. Container starts with env vars from config
 *   4. Reports "active" status back to Mirascope when ready
 * ```
 *
 * ## Deprovision Flow
 *
 * ```
 * deprovision(clawId)
 *   1. Destroy the container via dispatch worker
 *   2. Delete R2 bucket
 * ```
 */

import { Effect, Layer } from "effect";

import type { ClawDeploymentStatus } from "@/claws/deployment/service";
import type { OpenClawConfig } from "@/claws/deployment/types";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { getClawUrl } from "@/claws/deployment/types";
import { CloudflareContainerService } from "@/cloudflare/containers/service";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { CloudflareApiError } from "@/errors";

/** R2 bucket name for a given claw. */
function bucketName(clawId: string): string {
  return `claw-${clawId}`;
}

/**
 * Internal routing hostname for a given claw.
 *
 * The dispatch worker uses `clawId` to resolve the correct Durable Object
 * via `idFromName(clawId)`. The public vanity hostname
 * (`{clawSlug}.{orgSlug}.mirascope.com`) is a separate concern handled
 * by DNS / the dispatch worker's hostname rewriting.
 */
function clawHostname(clawId: string): string {
  return `${clawId}.claws.mirascope.com`;
}

/**
 * Map a CloudflareApiError to a DeploymentError with context.
 */
function wrap<A>(
  context: string,
  effect: Effect.Effect<A, CloudflareApiError>,
): Effect.Effect<A, ClawDeploymentError> {
  return effect.pipe(
    Effect.mapError(
      (error) =>
        new ClawDeploymentError({
          message: `${context}: ${error.message}`,
          cause: error,
        }),
    ),
  );
}

/**
 * Live deployment service layer.
 *
 * Requires `CloudflareR2Service` and `CloudflareContainerService` to be
 * provided. In production these come from their respective live layers;
 * in tests, use the mock layers.
 */
export const LiveDeploymentService = Layer.effect(
  ClawDeploymentService,
  Effect.gen(function* () {
    const r2 = yield* CloudflareR2Service;
    const containers = yield* CloudflareContainerService;

    return {
      provision: (config: OpenClawConfig) =>
        Effect.gen(function* () {
          const bucket = bucketName(config.clawId);

          // 1. Create R2 bucket for persistent storage
          yield* wrap("Failed to create R2 bucket", r2.createBucket(bucket));

          // 2. Create scoped credentials for the bucket
          const credentials = yield* wrap(
            "Failed to create R2 credentials",
            r2.createScopedCredentials(bucket),
          );

          // 3. Return credentials — caller is responsible for persisting
          //    them to the DB and then calling warmUp() separately.
          return {
            status: "provisioning",
            url: getClawUrl(config.organizationSlug, config.clawSlug),
            startedAt: new Date(),
            bucketName: bucket,
            r2Credentials: credentials,
          } satisfies ClawDeploymentStatus;
        }),

      deprovision: (clawId: string) =>
        Effect.gen(function* () {
          const bucket = bucketName(clawId);
          const host = clawHostname(clawId);

          // 1. Destroy the container
          // TODO: Distinguish "already gone" from real errors — currently
          // swallowing all errors to avoid failing on already-deprovisioned claws.
          yield* wrap(
            "Failed to destroy container",
            containers.destroy(host),
          ).pipe(Effect.catchAll(() => Effect.void));

          // 2. Delete R2 bucket
          // TODO: Same as above — should only swallow "not found" errors.
          yield* wrap(
            "Failed to delete R2 bucket",
            r2.deleteBucket(bucket),
          ).pipe(Effect.catchAll(() => Effect.void));
        }),

      getStatus: (clawId: string) =>
        Effect.gen(function* () {
          const host = clawHostname(clawId);

          const state = yield* wrap(
            "Failed to get container state",
            containers.getState(host),
          );

          return {
            status:
              state.status === "running" || state.status === "healthy"
                ? "active"
                : state.status === "stopped" || state.status === "stopping"
                  ? "paused"
                  : "error",
            startedAt: state.lastChange
              ? new Date(state.lastChange)
              : undefined,
          } satisfies ClawDeploymentStatus;
        }),

      restart: (clawId: string) =>
        Effect.gen(function* () {
          const host = clawHostname(clawId);

          // Lightweight: restart gateway process, keep container alive
          yield* wrap(
            "Failed to restart gateway",
            containers.restartGateway(host),
          );

          return {
            status: "provisioning",
            startedAt: new Date(),
          } satisfies ClawDeploymentStatus;
        }),

      update: (clawId: string, config: Partial<OpenClawConfig>) =>
        Effect.gen(function* () {
          const host = clawHostname(clawId);

          // Instance type changes require a full container recreate (different
          // resource allocation). All other config changes just need a gateway
          // restart to pick up fresh config from the bootstrap API.
          if (config.instanceType != null) {
            yield* wrap(
              "Failed to recreate container for instance type change",
              containers.recreate(host),
            );
          } else {
            yield* wrap(
              "Failed to restart gateway for config update",
              containers.restartGateway(host),
            );
          }

          return {
            status: "provisioning",
            startedAt: new Date(),
          } satisfies ClawDeploymentStatus;
        }),

      warmUp: (clawId: string) =>
        Effect.gen(function* () {
          const host = clawHostname(clawId);
          yield* wrap("Failed to warm up container", containers.warmUp(host));
        }),
    };
  }),
);
