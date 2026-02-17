/**
 * @fileoverview Mac Mini deployment service.
 *
 * Implements ClawDeploymentServiceInterface using Mac Mini agents instead of
 * Cloudflare Containers. R2 is still used for backup storage.
 *
 * ## Provision Flow
 *
 * ```
 * provision(config)
 *   1. Find available Mini + port via fleet service
 *   2. Call Mini Agent: POST /claws { clawId, port }
 *   3. Create R2 bucket + scoped credentials
 *   4. Return status with miniId, miniPort, tunnelHostname
 * ```
 */

import { and, eq } from "drizzle-orm";
import { Effect, Layer } from "effect";

import type { ClawDeploymentStatus } from "@/claws/deployment/service";
import type {
  OpenClawDeployConfig,
  ProvisionClawConfig,
} from "@/claws/deployment/types";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import { MacMiniFleetService } from "@/claws/deployment/mac-mini-fleet";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { DrizzleORM } from "@/db/client";
import { claws } from "@/db/schema";
import { CloudflareApiError } from "@/errors";

/** R2 bucket name for a given claw. */
function bucketName(clawId: string): string {
  return `claw-${clawId}`;
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
    Effect.catchAllDefect((defect) =>
      Effect.fail(
        new ClawDeploymentError({
          message: `${context}: unexpected error`,
          cause: defect,
        }),
      ),
    ),
  );
}

/**
 * Mac Mini deployment service layer.
 *
 * Requires `CloudflareR2Service`, `MacMiniFleetService`, and `DrizzleORM`.
 */
export const MacMiniDeploymentService = Layer.effect(
  ClawDeploymentService,
  Effect.gen(function* () {
    const r2 = yield* CloudflareR2Service;
    const fleet = yield* MacMiniFleetService;
    const drizzle = yield* DrizzleORM;

    return {
      provision: (config: ProvisionClawConfig) =>
        Effect.gen(function* () {
          // 1. Find available Mini + port
          const mini = yield* fleet.findAvailableMini();

          // 2. Call Mini Agent to create the claw
          yield* fleet.callAgent(mini.miniId, "POST", "/claws", {
            clawId: config.clawId,
            port: mini.port,
          });

          // 3. Create R2 bucket for persistent storage
          const bucket = bucketName(config.clawId);
          yield* wrap("Failed to create R2 bucket", r2.createBucket(bucket));

          // 4. Create scoped credentials for the bucket
          const credentials = yield* wrap(
            "Failed to create R2 credentials",
            r2.createScopedCredentials(bucket),
          );

          // 5. Compute tunnel hostname
          const tunnelHostname = `${config.clawId}.${mini.tunnelHostnameSuffix}`;

          return {
            status: "provisioning",
            startedAt: new Date(),
            bucketName: bucket,
            r2Credentials: credentials,
            miniId: mini.miniId,
            miniPort: mini.port,
            tunnelHostname,
          } satisfies ClawDeploymentStatus;
        }),

      deprovision: (clawId: string) =>
        Effect.gen(function* () {
          // Look up which Mini the claw is on
          const [claw] = yield* drizzle
            .select({ miniId: claws.miniId, slug: claws.slug })
            .from(claws)
            .where(eq(claws.id, clawId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to look up claw ${clawId}: ${e}`,
                    cause: e,
                  }),
              ),
            );

          if (claw?.miniId) {
            // Call Mini Agent to delete
            yield* fleet
              .callAgent(claw.miniId, "DELETE", `/claws/${claw.slug}`)
              .pipe(Effect.catchAll(() => Effect.void));
          }

          // Delete R2 bucket
          const bucket = bucketName(clawId);
          yield* wrap(
            "Failed to delete R2 bucket",
            r2.deleteBucket(bucket),
          ).pipe(Effect.catchAll(() => Effect.void));
        }),

      getStatus: (clawId: string) =>
        Effect.gen(function* () {
          const [claw] = yield* drizzle
            .select({ miniId: claws.miniId, slug: claws.slug })
            .from(claws)
            .where(eq(claws.id, clawId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to look up claw: ${e}`,
                    cause: e,
                  }),
              ),
            );

          if (!claw?.miniId) {
            return { status: "error", errorMessage: "Claw not on a Mac Mini" } satisfies ClawDeploymentStatus;
          }

          const result = (yield* fleet.callAgent(
            claw.miniId,
            "GET",
            `/claws/${claw.slug}/status`,
          )) as { status?: string } | null;

          const agentStatus = result?.status;
          const status =
            agentStatus === "running" || agentStatus === "healthy"
              ? "active"
              : agentStatus === "stopped"
                ? "paused"
                : "provisioning";

          return { status } satisfies ClawDeploymentStatus;
        }),

      restart: (clawId: string) =>
        Effect.gen(function* () {
          const [claw] = yield* drizzle
            .select({ miniId: claws.miniId, slug: claws.slug })
            .from(claws)
            .where(eq(claws.id, clawId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to look up claw: ${e}`,
                    cause: e,
                  }),
              ),
            );

          if (!claw?.miniId) {
            return yield* Effect.fail(
              new ClawDeploymentError({ message: "Claw not on a Mac Mini" }),
            );
          }

          yield* fleet.callAgent(claw.miniId, "POST", `/claws/${claw.slug}/restart`);

          return {
            status: "provisioning",
            startedAt: new Date(),
          } satisfies ClawDeploymentStatus;
        }),

      update: (clawId: string, _config: Partial<OpenClawDeployConfig>) =>
        Effect.gen(function* () {
          // For now, just restart
          const [claw] = yield* drizzle
            .select({ miniId: claws.miniId, slug: claws.slug })
            .from(claws)
            .where(eq(claws.id, clawId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to look up claw: ${e}`,
                    cause: e,
                  }),
              ),
            );

          if (claw?.miniId) {
            yield* fleet.callAgent(claw.miniId, "POST", `/claws/${claw.slug}/restart`);
          }

          return {
            status: "provisioning",
            startedAt: new Date(),
          } satisfies ClawDeploymentStatus;
        }),

      warmUp: (clawId: string) =>
        Effect.gen(function* () {
          const [claw] = yield* drizzle
            .select({ miniId: claws.miniId, slug: claws.slug })
            .from(claws)
            .where(eq(claws.id, clawId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to look up claw: ${e}`,
                    cause: e,
                  }),
              ),
            );

          if (!claw?.miniId) {
            return yield* Effect.fail(
              new ClawDeploymentError({ message: "Claw not on a Mac Mini" }),
            );
          }

          // Verify the gateway is running
          yield* fleet.callAgent(claw.miniId, "GET", `/claws/${claw.slug}/status`);
        }),
    };
  }),
);
