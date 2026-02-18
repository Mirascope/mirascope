/**
 * HttpApiBuilder implementations for all endpoint groups.
 */
import { HttpApiBuilder } from "@effect/platform";
import { Effect, Layer, Redacted } from "effect";

import { AuthMiddleware, ErrorResponse, MiniAgentApi } from "./api.js";
import { AgentConfigService } from "./config.js";
import { Launchd } from "./services/launchd.js";
import { Monitoring } from "./services/monitoring.js";
import { Provisioning } from "./services/provisioning.js";
import { System } from "./services/system.js";
import { Tunnel } from "./services/tunnel.js";
import { UserManager } from "./services/user.js";

// ─── Helpers ───────────────────────────────────────────────

/** Catch any service error and convert to ErrorResponse */
const catchServiceErrors = <A, R>(
  effect: Effect.Effect<A, unknown, R>,
): Effect.Effect<A, ErrorResponse, R> =>
  effect.pipe(
    Effect.catchAll((e: unknown) => {
      if (e instanceof ErrorResponse) {
        return Effect.fail(e);
      }
      if (e && typeof e === "object" && "error" in e) {
        return Effect.fail(new ErrorResponse(e as any));
      }
      const message =
        e instanceof Error
          ? e.message
          : (e as any)?.message ?? String(e);
      return Effect.fail(new ErrorResponse({ error: message }));
    }),
  );

// ─── Auth Middleware ───────────────────────────────────────

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
    const config = yield* AgentConfigService;
    return AuthMiddleware.of({
      bearer: (token) =>
        Effect.gen(function* () {
          const tokenStr = Redacted.value(token);
          if (!timingSafeEqual(tokenStr, config.authToken)) {
            return yield* Effect.fail({ error: "Invalid token" });
          }
        }),
    });
  }),
);

// ─── Health Group Handler ──────────────────────────────────

export const HealthGroupLive = HttpApiBuilder.group(
  MiniAgentApi,
  "health",
  (handlers) =>
    handlers.handle("getHealth", () =>
      catchServiceErrors(
        Effect.gen(function* () {
          const config = yield* AgentConfigService;
          const system = yield* System;
          const provisioning = yield* Provisioning;
          const tunnel = yield* Tunnel;

          const [stats, clawUsers, routeCount] = yield* Effect.all([
            system.getSystemStats(),
            provisioning.listClawUsers(),
            tunnel
              .getRouteCount(config.tunnelConfigPath)
              .pipe(Effect.catchAll(() => Effect.succeed(0))),
          ]);

          return {
            hostname: stats.hostname,
            uptime: stats.uptime,
            cpu: stats.cpu,
            memory: stats.memory,
            disk: stats.disk,
            loadAverage: stats.loadAverage,
            claws: { active: clawUsers.length, max: config.maxClaws },
            tunnel: { status: "connected" as const, routes: routeCount },
          };
        }),
      ),
    ),
);

// ─── Claws Group Handler ───────────────────────────────────

export const ClawsGroupLive = HttpApiBuilder.group(
  MiniAgentApi,
  "claws",
  (handlers) =>
    handlers
      .handle("provision", ({ payload }) =>
        catchServiceErrors(
          Effect.gen(function* () {
            const config = yield* AgentConfigService;
            const provisioning = yield* Provisioning;

            // Validate port range
            if (
              payload.localPort < config.portRangeStart ||
              payload.localPort > config.portRangeEnd
            ) {
              return yield* Effect.fail(
                new ErrorResponse({
                  error: `Port ${payload.localPort} is outside allowed range ${config.portRangeStart}-${config.portRangeEnd}`,
                }),
              );
            }

            // Check capacity
            const existingClaws = yield* provisioning.listClawUsers();
            if (existingClaws.length >= config.maxClaws) {
              return yield* Effect.fail(
                new ErrorResponse({
                  error: "Mini is at capacity",
                  details: `${existingClaws.length}/${config.maxClaws} claws`,
                }),
              );
            }

            const result = yield* provisioning
              .provision(
                {
                  clawId: payload.clawId,
                  macUsername: payload.macUsername,
                  localPort: payload.localPort,
                  gatewayToken: payload.gatewayToken,
                  tunnelHostname: payload.tunnelHostname,
                  envVars: payload.envVars ?? {},
                },
                config,
              )
              .pipe(
                Effect.catchAll((e) =>
                  Effect.succeed({
                    success: false as const,
                    macUsername: payload.macUsername,
                    localPort: payload.localPort,
                    tunnelRouteAdded: false as const,
                    error: e.message,
                  }),
                ),
              );

            return result;
          }),
        ),
      )
      .handle("listClaws", () =>
        catchServiceErrors(
          Effect.gen(function* () {
            const provisioning = yield* Provisioning;
            const monitoring = yield* Monitoring;
            const launchd = yield* Launchd;

            const clawUsers = yield* provisioning.listClawUsers();
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
          }),
        ),
      )
      .handle("getClawStatus", ({ path }) =>
        catchServiceErrors(
          Effect.gen(function* () {
            const userMgr = yield* UserManager;
            const monitoring = yield* Monitoring;
            const launchd = yield* Launchd;

            const exists = yield* userMgr
              .userExists(path.clawUser)
              .pipe(Effect.catchAll(() => Effect.succeed(false)));
            if (!exists) {
              return yield* Effect.fail(
                new ErrorResponse({
                  error: `Claw user ${path.clawUser} not found`,
                }),
              );
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
          }),
        ),
      )
      .handle("restartClaw", ({ path }) =>
        catchServiceErrors(
          Effect.gen(function* () {
            const userMgr = yield* UserManager;
            const launchdSvc = yield* Launchd;

            const exists = yield* userMgr
              .userExists(path.clawUser)
              .pipe(Effect.catchAll(() => Effect.succeed(false)));
            if (!exists) {
              return yield* Effect.fail(
                new ErrorResponse({
                  error: `Claw user ${path.clawUser} not found`,
                }),
              );
            }

            yield* launchdSvc.restart(path.clawUser);
            const pid = yield* launchdSvc.getPid(path.clawUser);
            return { success: true as const, gatewayPid: pid };
          }),
        ),
      )
      .handle("deprovisionClaw", ({ path }) =>
        catchServiceErrors(
          Effect.gen(function* () {
            const config = yield* AgentConfigService;
            const userMgr = yield* UserManager;
            const provisioning = yield* Provisioning;

            const exists = yield* userMgr
              .userExists(path.clawUser)
              .pipe(Effect.catchAll(() => Effect.succeed(false)));
            if (!exists) {
              return yield* Effect.fail(
                new ErrorResponse({
                  error: `Claw user ${path.clawUser} not found`,
                }),
              );
            }

            const result = yield* provisioning
              .deprovision(path.clawUser, config)
              .pipe(
                Effect.catchAll((e) =>
                  Effect.succeed({
                    success: false as const,
                    archived: false as const,
                    error: e.message,
                  }),
                ),
              );

            return result;
          }),
        ),
      )
      .handle("backupClaw", ({ path }) =>
        catchServiceErrors(
          Effect.gen(function* () {
            const userMgr = yield* UserManager;

            const exists = yield* userMgr
              .userExists(path.clawUser)
              .pipe(Effect.catchAll(() => Effect.succeed(false)));
            if (!exists) {
              return yield* Effect.fail(
                new ErrorResponse({
                  error: `Claw user ${path.clawUser} not found`,
                }),
              );
            }

            const backupId = `backup-${Date.now()}`;
            yield* Effect.log(
              `Triggered backup ${backupId} for ${path.clawUser} (not yet implemented)`,
            );

            return { success: true as const, backupId };
          }),
        ),
      ),
);
