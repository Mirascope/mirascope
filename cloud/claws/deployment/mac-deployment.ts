/**
 * @fileoverview Mac deployment service.
 *
 * Implements ClawDeploymentServiceInterface for Mac infrastructure.
 * Provisions claws by calling the Mac Agent API and storing
 * mac-specific fields (macId, macPort, tunnelHostname, macUsername)
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
  MacFleetService,
  AgentCallError,
  FleetError,
} from "@/claws/deployment/mac-fleet";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { DrizzleORM } from "@/db/client";
import { claws, fleetMacs } from "@/db/schema";
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

/** Select the mac assignment fields from a claw row, failing if not assigned. */
function lookupClawMac(drizzle: DrizzleORM["Type"], clawId: string) {
  return Effect.gen(function* () {
    const [claw] = yield* drizzle
      .select({
        macId: claws.macId,
        macPort: claws.macPort,
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
      !claw?.macId ||
      !claw.macPort ||
      !claw.tunnelHostname ||
      !claw.macUsername
    ) {
      return yield* Effect.fail(
        new ClawDeploymentError({
          message: "Claw not assigned to a Mac",
        }),
      );
    }

    return claw as {
      macId: string;
      macPort: number;
      tunnelHostname: string;
      macUsername: string;
    };
  });
}

/** Look up the agent URL and auth token for a mac. */
function lookupMacAgent(drizzle: DrizzleORM["Type"], macId: string) {
  return Effect.gen(function* () {
    const [mac] = yield* drizzle
      .select({
        agentUrl: fleetMacs.agentUrl,
        agentAuthTokenEncrypted: fleetMacs.agentAuthTokenEncrypted,
      })
      .from(fleetMacs)
      .where(eq(fleetMacs.id, macId))
      .limit(1)
      .pipe(
        Effect.mapError(
          (e) =>
            new ClawDeploymentError({
              message: `Failed to look up mac: ${e}`,
              cause: e,
            }),
        ),
      );

    if (!mac) {
      return yield* Effect.fail(
        new ClawDeploymentError({ message: "Mac not found" }),
      );
    }

    return mac;
  });
}

/**
 * Mac deployment layer.
 *
 * Requires MacFleetService, CloudflareR2Service (for backup buckets),
 * and DrizzleORM (to store mac-specific fields on claw rows).
 */
export const MacDeploymentLayer = Layer.effect(
  ClawDeploymentService,
  Effect.gen(function* () {
    const fleet = yield* MacFleetService;
    const r2 = yield* CloudflareR2Service;
    const drizzle = yield* DrizzleORM;

    return {
      provision: (config: ProvisionClawConfig) =>
        Effect.gen(function* () {
          // 1. Find available mac + port
          const mac = yield* wrapFleet(
            "Failed to find available mac",
            fleet.findAvailableMac(),
          );

          // 2. Look up agent auth token for the mac
          const [macRow] = yield* drizzle
            .select({
              agentAuthTokenEncrypted: fleetMacs.agentAuthTokenEncrypted,
            })
            .from(fleetMacs)
            .where(eq(fleetMacs.id, mac.macId))
            .limit(1)
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to look up mac auth token: ${e}`,
                    cause: e,
                  }),
              ),
            );

          const agentToken = macRow?.agentAuthTokenEncrypted ?? "";
          const macUsername = `claw-${config.clawId}`;

          // 3. Call Mac Agent to provision the claw
          yield* wrapFleet(
            "Failed to provision on mac agent",
            fleet.callAgent(mac.agentUrl, agentToken, "POST", "/claws", {
              clawId: config.clawId,
              port: mac.port,
              macUsername,
            }),
          );

          // 4. Build tunnel hostname
          const tunnelHostname = `claw-${config.clawId}.${mac.tunnelHostnameSuffix}`;

          // 5. Store mac-specific fields on the claw row
          yield* drizzle
            .update(claws)
            .set({
              macId: mac.macId,
              macPort: mac.port,
              tunnelHostname,
              macUsername,
              updatedAt: new Date(),
            })
            .where(eq(claws.id, config.clawId))
            .pipe(
              Effect.mapError(
                (e) =>
                  new ClawDeploymentError({
                    message: `Failed to persist mac deployment info: ${e}`,
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
            macId: mac.macId,
            macPort: mac.port,
            tunnelHostname,
            macUsername,
          } satisfies ClawDeploymentStatus;
        }),

      deprovision: (clawId: string) =>
        Effect.gen(function* () {
          const claw = yield* lookupClawMac(drizzle, clawId).pipe(
            Effect.catchAll(() => Effect.succeed(null)),
          );

          if (claw) {
            const mac = yield* lookupMacAgent(drizzle, claw.macId).pipe(
              Effect.catchAll(() => Effect.succeed(null)),
            );

            if (mac) {
              yield* wrapFleet(
                "Failed to deprovision on mac agent",
                fleet.callAgent(
                  mac.agentUrl,
                  mac.agentAuthTokenEncrypted ?? "",
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
          const claw = yield* lookupClawMac(drizzle, clawId);
          const mac = yield* lookupMacAgent(drizzle, claw.macId);

          const result = yield* wrapFleet(
            "Failed to get status from agent",
            fleet.callAgent(
              mac.agentUrl,
              mac.agentAuthTokenEncrypted ?? "",
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
            macId: claw.macId,
            macPort: claw.macPort,
            tunnelHostname: claw.tunnelHostname,
            macUsername: claw.macUsername,
          } satisfies ClawDeploymentStatus;
        }),

      restart: (clawId: string) =>
        Effect.gen(function* () {
          const claw = yield* lookupClawMac(drizzle, clawId);
          const mac = yield* lookupMacAgent(drizzle, claw.macId);

          yield* wrapFleet(
            "Failed to restart on agent",
            fleet.callAgent(
              mac.agentUrl,
              mac.agentAuthTokenEncrypted ?? "",
              "POST",
              `/claws/${clawId}/restart`,
            ),
          );

          return {
            status: "provisioning",
            startedAt: new Date(),
            macId: claw.macId,
            macPort: claw.macPort,
            tunnelHostname: claw.tunnelHostname,
            macUsername: claw.macUsername,
          } satisfies ClawDeploymentStatus;
        }),

      update: (clawId: string, _config: Partial<OpenClawDeployConfig>) =>
        Effect.gen(function* () {
          const claw = yield* lookupClawMac(drizzle, clawId);
          const mac = yield* lookupMacAgent(drizzle, claw.macId);

          yield* wrapFleet(
            "Failed to restart on agent",
            fleet.callAgent(
              mac.agentUrl,
              mac.agentAuthTokenEncrypted ?? "",
              "POST",
              `/claws/${clawId}/restart`,
            ),
          );

          return {
            status: "provisioning",
            startedAt: new Date(),
            macId: claw.macId,
            macPort: claw.macPort,
            tunnelHostname: claw.tunnelHostname,
            macUsername: claw.macUsername,
          } satisfies ClawDeploymentStatus;
        }),

      warmUp: (clawId: string) =>
        Effect.gen(function* () {
          const claw = yield* lookupClawMac(drizzle, clawId);
          const mac = yield* lookupMacAgent(drizzle, claw.macId);

          yield* wrapFleet(
            "Failed to warm up on agent",
            fleet.callAgent(
              mac.agentUrl,
              mac.agentAuthTokenEncrypted ?? "",
              "GET",
              `/claws/${clawId}/status`,
            ),
          );
        }),
    };
  }),
);
