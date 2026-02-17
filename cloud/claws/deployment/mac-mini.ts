/**
 * @fileoverview Mac Mini deployment service.
 *
 * Implements ClawDeploymentServiceInterface for Mac Mini infrastructure.
 * Provisions claws by calling the Mac Mini Agent API and storing
 * mini-specific fields (miniId, miniPort, tunnelHostname, macUsername)
 * directly in the DB.
 */

import { eq } from "drizzle-orm";
import { Effect, Layer } from "effect";

import type { ClawDeploymentStatus } from "@/claws/deployment/service";
import type {
  OpenClawDeployConfig,
  ProvisionClawConfig,
} from "@/claws/deployment/types";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import {
  MacMiniFleetService,
  AgentCallError,
  FleetError,
} from "@/claws/deployment/mac-mini-fleet";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { DrizzleORM } from "@/db/client";
import { claws, macMinis } from "@/db/schema";
import { CloudflareApiError } from "@/errors";

/** R2 bucket name for a given claw (used for backups only). */
function bucketName(clawId: string): string {
  return `claw-${clawId}`;
}

/** Map fleet/agent errors to ClawDeploymentError. */
function wrapFleet<A>(
  context: string,
  effect: Effect.Effect<A, FleetError | AgentCallError>,
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

function wrapR2<A>(
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

/** Select the mini assignment fields from a claw row, failing if not assigned. */
function lookupClawMini(drizzle: DrizzleORM["Type"], clawId: string) {
  return Effect.gen(function* () {
    const [claw] = yield* drizzle
      .select({
        miniId: claws.miniId,
        miniPort: claws.miniPort,
        tunnelHostname: claws.tunnelHostname,
        macUsername: claws.macUsername,
      })
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

    if (
      !claw?.miniId ||
      !claw.miniPort ||
      !claw.tunnelHostname ||
      !claw.macUsername
    ) {
      return yield* Effect.fail(
        new ClawDeploymentError({
          message: "Claw not assigned to a Mac Mini",
        }),
      );
    }

    return claw as {
      miniId: string;
      miniPort: number;
      tunnelHostname: string;
      macUsername: string;
    };
  });
}

/** Look up the agent URL and auth token for a mini. */
function lookupMiniAgent(drizzle: DrizzleORM["Type"], miniId: string) {
  return Effect.gen(function* () {
    const [mini] = yield* drizzle
      .select({
        agentUrl: macMinis.agentUrl,
        agentAuthTokenEncrypted: macMinis.agentAuthTokenEncrypted,
      })
      .from(macMinis)
      .where(eq(macMinis.id, miniId))
      .limit(1)
      .pipe(
        Effect.mapError(
          (e) =>
            new ClawDeploymentError({
              message: `Failed to look up mini: ${e}`,
              cause: e,
            }),
        ),
      );

    if (!mini) {
      return yield* Effect.fail(
        new ClawDeploymentError({ message: "Mac Mini not found" }),
      );
    }

    return mini;
  });
}

/**
 * Mac Mini deployment layer.
 *
 * Requires MacMiniFleetService, CloudflareR2Service (for backup buckets),
 * and DrizzleORM (to store mini-specific fields on claw rows).
 */
export const MacMiniDeploymentLayer = Layer.effect(
  ClawDeploymentService,
  Effect.gen(function* () {
    const fleet = yield* MacMiniFleetService;
    const r2 = yield* CloudflareR2Service;
    const drizzle = yield* DrizzleORM;

    return {
      provision: (config: ProvisionClawConfig) =>
        Effect.gen(function* () {
          // 1. Find available mini + port
          const mini = yield* wrapFleet(
            "Failed to find available mini",
            fleet.findAvailableMini(),
          );

          // 2. Look up agent auth token for the mini
          const [miniRow] = yield* drizzle
            .select({
              agentAuthTokenEncrypted: macMinis.agentAuthTokenEncrypted,
            })
            .from(macMinis)
            .where(eq(macMinis.id, mini.miniId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to look up mini auth token: ${e}`,
                    cause: e,
                  }),
              ),
            );

          const agentToken = miniRow?.agentAuthTokenEncrypted ?? "";
          const macUsername = `claw-${config.clawId}`;

          // 3. Call Mini Agent to provision the claw
          yield* wrapFleet(
            "Failed to provision on mini agent",
            fleet.callAgent(mini.agentUrl, agentToken, "POST", "/claws", {
              clawId: config.clawId,
              port: mini.port,
              macUsername,
            }),
          );

          // 4. Build tunnel hostname
          const tunnelHostname = `claw-${config.clawId}.${mini.tunnelHostnameSuffix}`;

          // 5. Store mini-specific fields on the claw row
          yield* drizzle
            .update(claws)
            .set({
              miniId: mini.miniId,
              miniPort: mini.port,
              tunnelHostname,
              macUsername,
              updatedAt: new Date(),
            })
            .where(eq(claws.id, config.clawId))
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to persist mini deployment info: ${e}`,
                    cause: e,
                  }),
              ),
            );

          // 6. Create R2 bucket for backups
          const bucket = bucketName(config.clawId);
          yield* wrapR2("Failed to create R2 bucket", r2.createBucket(bucket));

          return {
            status: "provisioning",
            startedAt: new Date(),
            miniId: mini.miniId,
            miniPort: mini.port,
            tunnelHostname,
            macUsername,
          } satisfies ClawDeploymentStatus;
        }),

      deprovision: (clawId: string) =>
        Effect.gen(function* () {
          const claw = yield* lookupClawMini(drizzle, clawId).pipe(
            Effect.catchAll(() => Effect.succeed(null)),
          );

          if (claw) {
            const mini = yield* lookupMiniAgent(drizzle, claw.miniId).pipe(
              Effect.catchAll(() => Effect.succeed(null)),
            );

            if (mini) {
              yield* wrapFleet(
                "Failed to deprovision on mini agent",
                fleet.callAgent(
                  mini.agentUrl,
                  mini.agentAuthTokenEncrypted ?? "",
                  "DELETE",
                  `/claws/${clawId}`,
                ),
              ).pipe(Effect.catchAll(() => Effect.void));
            }
          }

          // Delete R2 backup bucket
          const bucket = bucketName(clawId);
          yield* wrapR2(
            "Failed to delete R2 bucket",
            r2.deleteBucket(bucket),
          ).pipe(Effect.catchAll(() => Effect.void));
        }),

      getStatus: (clawId: string) =>
        Effect.gen(function* () {
          const claw = yield* lookupClawMini(drizzle, clawId);
          const mini = yield* lookupMiniAgent(drizzle, claw.miniId);

          const result = yield* wrapFleet(
            "Failed to get status from agent",
            fleet.callAgent(
              mini.agentUrl,
              mini.agentAuthTokenEncrypted ?? "",
              "GET",
              `/claws/${clawId}/status`,
            ),
          );

          const agentStatus = result as { status?: string; startedAt?: string };

          return {
            status:
              agentStatus.status === "running"
                ? "active"
                : agentStatus.status === "stopped"
                  ? "paused"
                  : "error",
            startedAt: agentStatus.startedAt
              ? new Date(agentStatus.startedAt)
              : undefined,
            miniId: claw.miniId,
            miniPort: claw.miniPort,
            tunnelHostname: claw.tunnelHostname,
            macUsername: claw.macUsername,
          } satisfies ClawDeploymentStatus;
        }),

      restart: (clawId: string) =>
        Effect.gen(function* () {
          const claw = yield* lookupClawMini(drizzle, clawId);
          const mini = yield* lookupMiniAgent(drizzle, claw.miniId);

          yield* wrapFleet(
            "Failed to restart on agent",
            fleet.callAgent(
              mini.agentUrl,
              mini.agentAuthTokenEncrypted ?? "",
              "POST",
              `/claws/${clawId}/restart`,
            ),
          );

          return {
            status: "provisioning",
            startedAt: new Date(),
            miniId: claw.miniId,
            miniPort: claw.miniPort,
            tunnelHostname: claw.tunnelHostname,
            macUsername: claw.macUsername,
          } satisfies ClawDeploymentStatus;
        }),

      update: (clawId: string, _config: Partial<OpenClawDeployConfig>) =>
        Effect.gen(function* () {
          const claw = yield* lookupClawMini(drizzle, clawId);
          const mini = yield* lookupMiniAgent(drizzle, claw.miniId);

          yield* wrapFleet(
            "Failed to restart on agent",
            fleet.callAgent(
              mini.agentUrl,
              mini.agentAuthTokenEncrypted ?? "",
              "POST",
              `/claws/${clawId}/restart`,
            ),
          );

          return {
            status: "provisioning",
            startedAt: new Date(),
            miniId: claw.miniId,
            miniPort: claw.miniPort,
            tunnelHostname: claw.tunnelHostname,
            macUsername: claw.macUsername,
          } satisfies ClawDeploymentStatus;
        }),

      warmUp: (clawId: string) =>
        Effect.gen(function* () {
          const claw = yield* lookupClawMini(drizzle, clawId);
          const mini = yield* lookupMiniAgent(drizzle, claw.miniId);

          yield* wrapFleet(
            "Failed to warm up on agent",
            fleet.callAgent(
              mini.agentUrl,
              mini.agentAuthTokenEncrypted ?? "",
              "GET",
              `/claws/${clawId}/status`,
            ),
          );
        }),
    };
  }),
);
