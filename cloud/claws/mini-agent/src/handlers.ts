/**
 * HttpApiBuilder handler implementations.
 */
import { HttpApiBuilder } from "@effect/platform";
import { Effect, Layer, Redacted } from "effect";

import { AuthMiddleware, MiniAgentApi } from "./api.js";
import { Config } from "./Config.js";
import {
  AuthError,
  CapacityError,
  InternalError,
  NotFoundError,
  ValidationError,
} from "./Errors.js";
import { Launchd } from "./services/Launchd.js";
import { Monitoring } from "./services/Monitoring.js";
import { Provisioning } from "./services/Provisioning.js";
import { System } from "./services/System.js";
import { Tunnel } from "./services/Tunnel.js";
import { UserManager } from "./services/UserManager.js";

// ─── Auth Middleware Implementation ──────────────────────────────────────

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  const encoder = new TextEncoder();
  const bufA = encoder.encode(a);
  const bufB = encoder.encode(b);
  let result = 0;
  for (let i = 0; i < bufA.length; i++) {
    result |= bufA[i]! ^ bufB[i]!;
  }
  return result === 0;
}

export const AuthMiddlewareLive = Layer.effect(
  AuthMiddleware,
  Effect.gen(function* () {
    const config = yield* Config;

    return AuthMiddleware.of({
      bearer: (token) =>
        Effect.gen(function* () {
          const tokenValue = Redacted.value(token);
          if (!timingSafeEqual(tokenValue, config.authToken)) {
            return yield* new AuthError({ message: "Invalid token" });
          }
        }),
    });
  }),
);

// ─── Health Handlers ─────────────────────────────────────────────────────

export const HealthHandlers = HttpApiBuilder.group(
  MiniAgentApi,
  "health",
  (handlers) =>
    handlers.handle("getHealth", () =>
      Effect.gen(function* () {
        const config = yield* Config;
        const system = yield* System;
        const userManager = yield* UserManager;
        const tunnel = yield* Tunnel;

        const stats = yield* system.getStats();
        const clawUsers = yield* userManager.listClawUsers();
        const routeCount = yield* Effect.catchAll(
          tunnel.getRouteCount(config.tunnelConfigPath),
          () => Effect.succeed(0),
        );

        return {
          hostname: stats.hostname,
          uptime: stats.uptime,
          cpu: stats.cpu,
          memory: stats.memory,
          disk: stats.disk,
          loadAverage: stats.loadAverage as [number, number, number],
          claws: {
            active: clawUsers.length,
            max: config.maxClaws,
          },
          tunnel: {
            status: "connected" as const,
            routes: routeCount,
          },
        };
      }).pipe(
        Effect.catchAllDefect((e) =>
          Effect.fail(
            new InternalError({
              message: `Failed to get health status: ${String(e)}`,
            }),
          ),
        ),
      ),
    ),
);

// ─── Claws Handlers ─────────────────────────────────────────────────────

export const ClawsHandlers = HttpApiBuilder.group(
  MiniAgentApi,
  "claws",
  (handlers) =>
    handlers
      .handle("listClaws", () =>
        Effect.gen(function* () {
          const userManager = yield* UserManager;
          const monitoring = yield* Monitoring;
          const launchd = yield* Launchd;

          const clawUsers = yield* userManager.listClawUsers();
          const claws = yield* Effect.all(
            clawUsers.map((macUsername) =>
              Effect.gen(function* () {
                const resources =
                  yield* monitoring.getClawResources(macUsername);
                const status = yield* launchd.getStatus(macUsername);
                return {
                  macUsername,
                  launchdStatus: status,
                  ...resources,
                };
              }),
            ),
          );
          return { claws };
        }).pipe(
          Effect.catchAllDefect((e) =>
            Effect.fail(
              new InternalError({
                message: `Failed to list claws: ${String(e)}`,
              }),
            ),
          ),
        ),
      )
      .handle("provision", ({ payload }) =>
        Effect.gen(function* () {
          const config = yield* Config;
          const userManager = yield* UserManager;
          const provisioning = yield* Provisioning;

          // Validate port range
          if (
            payload.localPort < config.portRangeStart ||
            payload.localPort > config.portRangeEnd
          ) {
            return yield* new ValidationError({
              message: `Port ${payload.localPort} is outside allowed range ${config.portRangeStart}-${config.portRangeEnd}`,
            });
          }

          // Validate macUsername format
          if (!/^claw-[a-z0-9]+$/.test(payload.macUsername)) {
            return yield* new ValidationError({
              message: "macUsername must match pattern: claw-[a-z0-9]+",
            });
          }

          // Check capacity
          const existingClaws = yield* userManager.listClawUsers();
          if (existingClaws.length >= config.maxClaws) {
            return yield* new CapacityError({
              message: "Mini is at capacity",
              current: existingClaws.length,
              max: config.maxClaws,
            });
          }

          const result = yield* provisioning.provision({
            clawId: payload.clawId,
            macUsername: payload.macUsername,
            localPort: payload.localPort,
            gatewayToken: payload.gatewayToken,
            tunnelHostname: payload.tunnelHostname,
            envVars: payload.envVars ?? {},
          });

          if (!result.success) {
            return yield* new InternalError({
              message: result.error ?? "Provisioning failed",
            });
          }

          return result;
        }).pipe(
          Effect.catchAllDefect((e) =>
            Effect.fail(
              new InternalError({
                message: `Provisioning failed: ${e instanceof Error ? e.message : String(e)}`,
              }),
            ),
          ),
        ),
      )
      .handle("getClawStatus", ({ path }) =>
        Effect.gen(function* () {
          const userManager = yield* UserManager;
          const monitoring = yield* Monitoring;
          const launchd = yield* Launchd;

          const exists = yield* userManager.userExists(path.clawUser);
          if (!exists) {
            return yield* new NotFoundError({
              message: `Claw user ${path.clawUser} not found`,
            });
          }

          const [resources, status, diskMb] = yield* Effect.all([
            monitoring.getClawResources(path.clawUser),
            launchd.getStatus(path.clawUser),
            monitoring.getClawDiskUsage(path.clawUser),
          ]);

          return {
            macUsername: path.clawUser,
            launchdStatus: status,
            diskMb,
            ...resources,
          };
        }).pipe(
          Effect.catchAllDefect((e) =>
            Effect.fail(
              new InternalError({
                message: `Failed to get status: ${e instanceof Error ? e.message : String(e)}`,
              }),
            ),
          ),
        ),
      )
      .handle("restartClaw", ({ path }) =>
        Effect.gen(function* () {
          const userManager = yield* UserManager;
          const launchd = yield* Launchd;

          const exists = yield* userManager.userExists(path.clawUser);
          if (!exists) {
            return yield* new NotFoundError({
              message: `Claw user ${path.clawUser} not found`,
            });
          }

          yield* launchd.restart(path.clawUser);
          const pid = yield* launchd.getPid(path.clawUser);
          return { success: true as const, gatewayPid: pid };
        }).pipe(
          Effect.catchAllDefect((e) =>
            Effect.fail(
              new InternalError({
                message: `Failed to restart gateway: ${e instanceof Error ? e.message : String(e)}`,
              }),
            ),
          ),
        ),
      )
      .handle("deprovisionClaw", ({ path, payload }) =>
        Effect.gen(function* () {
          const userManager = yield* UserManager;
          const provisioning = yield* Provisioning;

          const exists = yield* userManager.userExists(path.clawUser);
          if (!exists) {
            return yield* new NotFoundError({
              message: `Claw user ${path.clawUser} not found`,
            });
          }

          const result = yield* provisioning.deprovision(
            path.clawUser,
            payload,
          );

          if (!result.success) {
            return yield* new InternalError({
              message: result.error ?? "Deprovisioning failed",
            });
          }

          return result;
        }).pipe(
          Effect.catchAllDefect((e) =>
            Effect.fail(
              new InternalError({
                message: `Deprovisioning failed: ${e instanceof Error ? e.message : String(e)}`,
              }),
            ),
          ),
        ),
      )
      .handle("backupClaw", ({ path }) =>
        Effect.gen(function* () {
          const userManager = yield* UserManager;

          const exists = yield* userManager.userExists(path.clawUser);
          if (!exists) {
            return yield* new NotFoundError({
              message: `Claw user ${path.clawUser} not found`,
            });
          }

          const backupId = `backup-${Date.now()}`;
          console.log(
            `[backup] Triggered backup ${backupId} for ${path.clawUser} (not yet implemented)`,
          );

          return { success: true as const, backupId };
        }).pipe(
          Effect.catchAllDefect((e) =>
            Effect.fail(
              new InternalError({
                message: `Backup failed: ${e instanceof Error ? e.message : String(e)}`,
              }),
            ),
          ),
        ),
      ),
);
