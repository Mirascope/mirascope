import type { AgentConfig } from "../lib/config.js";

/**
 * Claw provisioning orchestrator.
 *
 * Coordinates user creation, launchd setup, tunnel routing, and cleanup on failure.
 */
import { errorMessage } from "../lib/errors.js";
import { type ExecFn, exec as defaultExec } from "../lib/exec.js";
import * as launchd from "./launchd.js";
import * as monitoring from "./monitoring.js";
import * as tunnel from "./tunnel.js";
import * as user from "./user.js";

export interface ProvisionRequest {
  clawId: string;
  macUsername: string;
  localPort: number;
  gatewayToken: string;
  tunnelHostname: string;
  envVars: Record<string, string>;
}

export interface ProvisionResponse {
  success: boolean;
  macUsername: string;
  localPort: number;
  tunnelRouteAdded: boolean;
  error?: string;
}

export interface DeprovisionRequest {
  archive?: boolean;
}

export interface DeprovisionResponse {
  success: boolean;
  archived: boolean;
  error?: string;
}

export interface ClawStatus {
  clawId: string;
  macUsername: string;
  localPort: number;
  gatewayPid: number | null;
  gatewayUptime: number | null;
  memoryUsageMb: number | null;
  chromiumPid: number | null;
  launchdStatus: "loaded" | "unloaded" | "error";
  tunnelRouteActive: boolean;
}

/**
 * Provision a new claw on this Mini.
 *
 * If any step fails, performs cleanup of all completed steps.
 */
export async function provision(
  request: ProvisionRequest,
  config: AgentConfig,
  execFn: ExecFn = defaultExec,
): Promise<ProvisionResponse> {
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
    console.log(`[provision] Creating user ${macUsername} for claw ${clawId}`);
    await user.createClawUser(
      {
        macUsername,
        clawId,
        localPort,
        gatewayToken,
        tunnelHostname,
        envVars,
      },
      execFn,
    );
    userCreated = true;

    // Step 2: Install and load launchd service
    console.log(`[provision] Installing launchd service for ${macUsername}`);
    await launchd.installAndLoad(
      {
        macUsername,
        localPort,
        gatewayToken,
        envVars,
      },
      execFn,
    );
    launchdLoaded = true;

    // Step 3: Add tunnel route
    console.log(
      `[provision] Adding tunnel route: ${tunnelHostname} → localhost:${localPort}`,
    );
    await tunnel.addRoute(config.tunnelConfigPath, tunnelHostname, localPort);
    tunnelRouteAdded = true;

    // Step 4: Restart cloudflared to pick up new route
    console.log("[provision] Restarting cloudflared");
    await tunnel.restartCloudflared(execFn);

    // Step 5: Wait for gateway to become available
    console.log(`[provision] Waiting for gateway on port ${localPort}...`);
    await waitForGateway(localPort, 30_000);

    console.log(
      `[provision] Successfully provisioned claw ${clawId} as ${macUsername}`,
    );
    return { success: true, macUsername, localPort, tunnelRouteAdded };
  } catch (error: unknown) {
    console.error(
      `[provision] Failed to provision ${clawId}: ${errorMessage(error)}`,
    );

    // Cleanup in reverse order
    try {
      if (tunnelRouteAdded) {
        console.log("[provision] Cleanup: removing tunnel route");
        await tunnel.removeRoute(config.tunnelConfigPath, tunnelHostname);
        await tunnel.restartCloudflared(execFn);
      }
    } catch (e: unknown) {
      console.error(`[provision] Cleanup tunnel failed: ${errorMessage(e)}`);
    }

    try {
      if (launchdLoaded) {
        console.log("[provision] Cleanup: unloading launchd");
        await launchd.stopAndUnload(macUsername, execFn);
      }
    } catch (e: unknown) {
      console.error(`[provision] Cleanup launchd failed: ${errorMessage(e)}`);
    }

    try {
      if (userCreated) {
        console.log("[provision] Cleanup: deleting user");
        await user.deleteClawUser(macUsername, execFn);
      }
    } catch (e: unknown) {
      console.error(`[provision] Cleanup user failed: ${errorMessage(e)}`);
    }

    return {
      success: false,
      macUsername,
      localPort,
      tunnelRouteAdded: false,
      error: errorMessage(error),
    };
  }
}

/**
 * Deprovision a claw from this Mini.
 */
export async function deprovision(
  macUsername: string,
  config: AgentConfig,
  _request: DeprovisionRequest = {},
  execFn: ExecFn = defaultExec,
): Promise<DeprovisionResponse> {
  const errors: string[] = [];

  // TODO: backup to R2 if request.archive !== false

  // Step 1: Stop and unload launchd service
  try {
    console.log(`[deprovision] Stopping launchd service for ${macUsername}`);
    await launchd.stopAndUnload(macUsername, execFn);
  } catch (e: unknown) {
    errors.push(`launchd: ${errorMessage(e)}`);
  }

  // Step 2: Find and remove tunnel route
  try {
    // We need to figure out the hostname. List routes and find one matching the port.
    // For now, construct from macUsername pattern
    const tunnelConfig = await tunnel.readTunnelConfig(config.tunnelConfigPath);
    // Find and remove routes matching this claw's username pattern
    for (const r of tunnelConfig.ingress) {
      if (r.hostname?.includes(macUsername.replace("claw-", ""))) {
        console.log(`[deprovision] Removing tunnel route: ${r.hostname}`);
        await tunnel.removeRoute(config.tunnelConfigPath, r.hostname);
      }
    }
  } catch (e: unknown) {
    errors.push(`tunnel: ${errorMessage(e)}`);
  }

  // Step 3: Restart cloudflared
  try {
    await tunnel.restartCloudflared(execFn);
  } catch (e: unknown) {
    errors.push(`cloudflared restart: ${errorMessage(e)}`);
  }

  // Step 4: Delete macOS user
  try {
    console.log(`[deprovision] Deleting user ${macUsername}`);
    await user.deleteClawUser(macUsername, execFn);
  } catch (e: unknown) {
    errors.push(`user deletion: ${errorMessage(e)}`);
  }

  if (errors.length > 0) {
    return { success: false, archived: false, error: errors.join("; ") };
  }

  console.log(`[deprovision] Successfully deprovisioned ${macUsername}`);
  return { success: true, archived: false };
}

/**
 * Get the status of a claw.
 */
export async function getClawStatus(
  macUsername: string,
  clawId: string,
  localPort: number,
  config: AgentConfig,
  execFn: ExecFn = defaultExec,
): Promise<ClawStatus> {
  const [launchdStatus, resources, tunnelRouteActive] = await Promise.all([
    launchd.getStatus(macUsername, execFn),
    monitoring.getClawResources(macUsername, execFn),
    tunnel
      .hasRoute(
        config.tunnelConfigPath,
        `claw-${clawId}.${config.tunnelHostnameSuffix}`,
      )
      .catch(() => false),
  ]);

  return {
    clawId,
    macUsername,
    localPort,
    gatewayPid: resources.gatewayPid,
    gatewayUptime: resources.gatewayUptime,
    memoryUsageMb: resources.memoryUsageMb,
    chromiumPid: resources.chromiumPid,
    launchdStatus,
    tunnelRouteActive,
  };
}

/**
 * List all claw users on this Mini by checking for claw-* macOS users.
 */
export async function listClawUsers(
  execFn: ExecFn = defaultExec,
): Promise<string[]> {
  const result = await execFn("dscl", [".", "-list", "/Users"]);
  if (result.exitCode !== 0) return [];

  return result.stdout
    .split("\n")
    .map((l) => l.trim())
    .filter((l) => l.startsWith("claw-"));
}

/**
 * Wait for a gateway to respond on a port.
 */
async function waitForGateway(port: number, timeoutMs: number): Promise<void> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/health`, {
        signal: AbortSignal.timeout(2000),
      });
      if (response.ok) return;
    } catch {
      // Not ready yet
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  console.warn(
    `[provision] Gateway on port ${port} did not respond within ${timeoutMs}ms (continuing anyway)`,
  );
}
