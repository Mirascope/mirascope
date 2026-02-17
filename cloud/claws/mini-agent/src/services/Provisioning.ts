/**
 * Claw provisioning orchestrator service.
 */
import { Context, Effect, Layer } from "effect";

import { Config } from "../Config.js";
import { Launchd } from "./Launchd.js";
import { Tunnel } from "./Tunnel.js";
import { UserManager } from "./UserManager.js";

export interface ProvisionRequest {
  readonly clawId: string;
  readonly macUsername: string;
  readonly localPort: number;
  readonly gatewayToken: string;
  readonly tunnelHostname: string;
  readonly envVars: Record<string, string>;
}

export interface ProvisionResponse {
  readonly success: boolean;
  readonly macUsername: string;
  readonly localPort: number;
  readonly tunnelRouteAdded: boolean;
  readonly error?: string;
}

export interface DeprovisionResponse {
  readonly success: boolean;
  readonly archived: boolean;
  readonly error?: string;
}

export interface ProvisioningService {
  readonly provision: (
    request: ProvisionRequest,
  ) => Effect.Effect<ProvisionResponse>;
  readonly deprovision: (
    macUsername: string,
    options?: { archive?: boolean },
  ) => Effect.Effect<DeprovisionResponse>;
}

export class Provisioning extends Context.Tag("MiniAgent/Provisioning")<
  Provisioning,
  ProvisioningService
>() {}

export const ProvisioningLive = Layer.effect(
  Provisioning,
  Effect.gen(function* () {
    const config = yield* Config;
    const userManager = yield* UserManager;
    const launchd = yield* Launchd;
    const tunnel = yield* Tunnel;

    const waitForGateway = (port: number, timeoutMs: number) =>
      Effect.promise(async () => {
        const start = Date.now();
        while (Date.now() - start < timeoutMs) {
          try {
            const response = await fetch(
              `http://127.0.0.1:${port}/health`,
              { signal: AbortSignal.timeout(2000) },
            );
            if (response.ok) return;
          } catch {
            // Not ready yet
          }
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }
        console.warn(
          `[provision] Gateway on port ${port} did not respond within ${timeoutMs}ms (continuing anyway)`,
        );
      });

    return {
      provision: (request: ProvisionRequest) =>
        Effect.gen(function* () {
          const {
            macUsername,
            clawId,
            localPort,
            gatewayToken,
            tunnelHostname,
            envVars,
          } = request;

          let userCreated = false;
          let launchdLoaded = false;
          let tunnelRouteAdded = false;

          try {
            // Step 1: Create macOS user
            console.log(
              `[provision] Creating user ${macUsername} for claw ${clawId}`,
            );
            yield* userManager.createClawUser({
              macUsername,
              clawId,
              localPort,
              gatewayToken,
              tunnelHostname,
              envVars,
            });
            userCreated = true;

            // Step 2: Install and load launchd service
            console.log(
              `[provision] Installing launchd service for ${macUsername}`,
            );
            yield* launchd.installAndLoad({
              macUsername,
              localPort,
              gatewayToken,
              envVars,
            });
            launchdLoaded = true;

            // Step 3: Add tunnel route
            console.log(
              `[provision] Adding tunnel route: ${tunnelHostname} → localhost:${localPort}`,
            );
            yield* tunnel.addRoute(
              config.tunnelConfigPath,
              tunnelHostname,
              localPort,
            );
            tunnelRouteAdded = true;

            // Step 4: Restart cloudflared
            console.log("[provision] Restarting cloudflared");
            yield* tunnel.restartCloudflared();

            // Step 5: Wait for gateway
            console.log(
              `[provision] Waiting for gateway on port ${localPort}...`,
            );
            yield* waitForGateway(localPort, 30_000);

            console.log(
              `[provision] Successfully provisioned claw ${clawId} as ${macUsername}`,
            );
            return {
              success: true,
              macUsername,
              localPort,
              tunnelRouteAdded,
            } satisfies ProvisionResponse;
          } catch (error: unknown) {
            const errorMsg =
              error instanceof Error ? error.message : String(error);
            console.error(
              `[provision] Failed to provision ${clawId}: ${errorMsg}`,
            );

            // Cleanup in reverse order
            if (tunnelRouteAdded) {
              yield* tunnel
                .removeRoute(config.tunnelConfigPath, tunnelHostname)
                .pipe(
                  Effect.andThen(tunnel.restartCloudflared()),
                  Effect.catchAll(() => Effect.void),
                );
            }

            if (launchdLoaded) {
              yield* launchd.stopAndUnload(macUsername).pipe(
                Effect.catchAll(() => Effect.void),
              );
            }

            if (userCreated) {
              yield* userManager.deleteClawUser(macUsername).pipe(
                Effect.catchAll(() => Effect.void),
              );
            }

            return {
              success: false,
              macUsername,
              localPort,
              tunnelRouteAdded: false,
              error: errorMsg,
            } satisfies ProvisionResponse;
          }
        }),

      deprovision: (
        macUsername: string,
        _options?: { archive?: boolean },
      ) =>
        Effect.gen(function* () {
          const errors: string[] = [];

          // Step 1: Stop and unload launchd
          const launchdResult = yield* Effect.either(
            launchd.stopAndUnload(macUsername),
          );
          if (launchdResult._tag === "Left") {
            errors.push(`launchd: ${String(launchdResult.left)}`);
          }

          // Step 2: Find and remove tunnel routes
          const tunnelResult = yield* Effect.either(
            Effect.gen(function* () {
              const tunnelConfig = yield* tunnel.readConfig(
                config.tunnelConfigPath,
              );
              for (const r of tunnelConfig.ingress) {
                if (
                  r.hostname?.includes(
                    macUsername.replace("claw-", ""),
                  )
                ) {
                  console.log(
                    `[deprovision] Removing tunnel route: ${r.hostname}`,
                  );
                  yield* tunnel.removeRoute(
                    config.tunnelConfigPath,
                    r.hostname,
                  );
                }
              }
            }),
          );
          if (tunnelResult._tag === "Left") {
            errors.push(`tunnel: ${String(tunnelResult.left)}`);
          }

          // Step 3: Restart cloudflared
          const cfResult = yield* Effect.either(
            tunnel.restartCloudflared(),
          );
          if (cfResult._tag === "Left") {
            errors.push(`cloudflared restart: ${String(cfResult.left)}`);
          }

          // Step 4: Delete macOS user
          const userResult = yield* Effect.either(
            Effect.gen(function* () {
              console.log(
                `[deprovision] Deleting user ${macUsername}`,
              );
              yield* userManager.deleteClawUser(macUsername);
            }),
          );
          if (userResult._tag === "Left") {
            errors.push(`user deletion: ${String(userResult.left)}`);
          }

          if (errors.length > 0) {
            return {
              success: false,
              archived: false,
              error: errors.join("; "),
            } satisfies DeprovisionResponse;
          }

          console.log(
            `[deprovision] Successfully deprovisioned ${macUsername}`,
          );
          return {
            success: true,
            archived: false,
          } satisfies DeprovisionResponse;
        }),
    };
  }),
);
