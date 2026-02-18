/**
 * Claw provisioning orchestrator service.
 */
import { Context, Effect } from "effect";

import type { AgentConfig } from "../config.js";

import {
  CapacityError,
  DeprovisioningError,
  ExecError,
  ProvisioningError,
  SystemError,
  ValidationError,
  errorMessage,
} from "../errors.js";
import { Exec } from "./exec.js";
import { Launchd } from "./launchd.js";
import { Monitoring } from "./monitoring.js";
import { Tunnel } from "./tunnel.js";
import { UserManager } from "./user.js";

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

export interface DeprovisionRequest {
  readonly archive?: boolean;
}

export interface DeprovisionResponse {
  readonly success: boolean;
  readonly archived: boolean;
  readonly error?: string;
}

export class Provisioning extends Context.Tag("Provisioning")<
  Provisioning,
  {
    readonly provision: (
      request: ProvisionRequest,
      config: AgentConfig,
    ) => Effect.Effect<
      ProvisionResponse,
      | ProvisioningError
      | ValidationError
      | CapacityError
      | ExecError
      | SystemError
    >;
    readonly deprovision: (
      macUsername: string,
      config: AgentConfig,
      request?: DeprovisionRequest,
    ) => Effect.Effect<DeprovisionResponse, DeprovisioningError>;
    readonly listClawUsers: () => Effect.Effect<string[], ExecError>;
  }
>() {}

export const ProvisioningLive = Effect.gen(function* () {
  const exec = yield* Exec;
  const userManager = yield* UserManager;
  const launchd = yield* Launchd;
  const tunnel = yield* Tunnel;
  yield* Monitoring;

  const waitForGateway = (
    port: number,
    timeoutMs: number,
  ): Effect.Effect<void> =>
    Effect.gen(function* () {
      const start = Date.now();
      while (Date.now() - start < timeoutMs) {
        const ok = yield* Effect.tryPromise({
          try: async () => {
            const response = await fetch(`http://127.0.0.1:${port}/health`, {
              signal: AbortSignal.timeout(2000),
            });
            return response.ok;
          },
          catch: () => false,
        }).pipe(Effect.catchAll(() => Effect.succeed(false)));

        if (ok) return;
        yield* Effect.sleep("1 second");
      }
      yield* Effect.logWarning(
        `Gateway on port ${port} did not respond within ${timeoutMs}ms (continuing anyway)`,
      );
    });

  const provision = (
    request: ProvisionRequest,
    config: AgentConfig,
  ): Effect.Effect<
    ProvisionResponse,
    | ProvisioningError
    | ValidationError
    | CapacityError
    | ExecError
    | SystemError
  > =>
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
        yield* Effect.log(`Creating user ${macUsername} for claw ${clawId}`);
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
        yield* Effect.log(`Installing launchd service for ${macUsername}`);
        yield* launchd.installAndLoad({
          macUsername,
          localPort,
          gatewayToken,
          envVars,
        });
        launchdLoaded = true;

        // Step 3: Add tunnel route
        yield* Effect.log(
          `Adding tunnel route: ${tunnelHostname} → localhost:${localPort}`,
        );
        yield* tunnel.addRoute(
          config.tunnelConfigPath,
          tunnelHostname,
          localPort,
        );
        tunnelRouteAdded = true;

        // Step 3b: Add DNS record for the tunnel hostname
        yield* Effect.log(`Adding DNS route for ${tunnelHostname}`);
        yield* tunnel.addDnsRoute(config.tunnelName, tunnelHostname);

        // Step 4: Restart cloudflared
        yield* Effect.log("Restarting cloudflared");
        yield* tunnel.restartCloudflared();

        // Step 5: Wait for gateway
        yield* Effect.log(`Waiting for gateway on port ${localPort}...`);
        yield* waitForGateway(localPort, 30_000);

        yield* Effect.log(
          `Successfully provisioned claw ${clawId} as ${macUsername}`,
        );
        return {
          success: true,
          macUsername,
          localPort,
          tunnelRouteAdded,
        } as ProvisionResponse;
      } catch (error: unknown) {
        // Cleanup in reverse order
        if (tunnelRouteAdded) {
          yield* tunnel
            .removeRoute(config.tunnelConfigPath, tunnelHostname)
            .pipe(Effect.catchAll(() => Effect.void));
          yield* tunnel
            .restartCloudflared()
            .pipe(Effect.catchAll(() => Effect.void));
        }
        if (launchdLoaded) {
          yield* launchd
            .stopAndUnload(macUsername)
            .pipe(Effect.catchAll(() => Effect.void));
        }
        if (userCreated) {
          yield* userManager
            .deleteClawUser(macUsername)
            .pipe(Effect.catchAll(() => Effect.void));
        }

        return {
          success: false,
          macUsername,
          localPort,
          tunnelRouteAdded: false,
          error: errorMessage(error),
        } as ProvisionResponse;
      }
    });

  const deprovision = (
    macUsername: string,
    config: AgentConfig,
    _request: DeprovisionRequest = {},
  ): Effect.Effect<DeprovisionResponse, DeprovisioningError> =>
    Effect.gen(function* () {
      const errors: string[] = [];

      // Step 1: Stop launchd
      yield* launchd.stopAndUnload(macUsername).pipe(
        Effect.catchAll((e) =>
          Effect.sync(() => {
            errors.push(`launchd: ${e.message}`);
          }),
        ),
      );

      // Step 2: Find and remove tunnel routes
      yield* Effect.gen(function* () {
        const tunnelConfig = yield* tunnel.readTunnelConfig(
          config.tunnelConfigPath,
        );
        for (const r of tunnelConfig.ingress) {
          if (r.hostname?.includes(macUsername.replace("claw-", ""))) {
            yield* tunnel.removeRoute(config.tunnelConfigPath, r.hostname);
          }
        }
      }).pipe(
        Effect.catchAll((e) =>
          Effect.sync(() => {
            errors.push(`tunnel: ${errorMessage(e)}`);
          }),
        ),
      );

      // Step 3: Restart cloudflared
      yield* tunnel.restartCloudflared().pipe(
        Effect.catchAll((e) =>
          Effect.sync(() => {
            errors.push(`cloudflared restart: ${e.message}`);
          }),
        ),
      );

      // Step 4: Delete user
      yield* userManager.deleteClawUser(macUsername).pipe(
        Effect.catchAll((e) =>
          Effect.sync(() => {
            errors.push(`user deletion: ${e.message}`);
          }),
        ),
      );

      if (errors.length > 0) {
        return {
          success: false,
          archived: false,
          error: errors.join("; "),
        };
      }

      return { success: true, archived: false };
    });

  const listClawUsers = (): Effect.Effect<string[], ExecError> =>
    Effect.gen(function* () {
      const result = yield* exec.run("dscl", [".", "-list", "/Users"]);
      if (result.exitCode !== 0) return [];

      return result.stdout
        .split("\n")
        .map((l) => l.trim())
        .filter((l) => l.startsWith("claw-"));
    });

  return { provision, deprovision, listClawUsers };
});
