/**
 * Gateway process management and request proxying.
 *
 * Handles:
 * - Finding existing gateway processes
 * - Mounting R2 storage per-claw
 * - Starting the gateway via start-openclaw.sh
 * - Proxying HTTP and WebSocket requests to the gateway
 */

import type { Sandbox, Process } from "@cloudflare/sandbox";

import type { DispatchEnv, OpenClawConfig } from "./types";

import { GATEWAY_PORT, STARTUP_TIMEOUT_MS, R2_MOUNT_PATH } from "./config";

/**
 * Find an existing OpenClaw gateway process in the sandbox.
 */
export async function findGatewayProcess(
  sandbox: Sandbox,
): Promise<Process | null> {
  try {
    const processes = await sandbox.listProcesses();
    for (const proc of processes) {
      const isGateway =
        proc.command.includes("start-openclaw.ts") ||
        proc.command.includes("openclaw gateway");
      const isCli =
        proc.command.includes("openclaw devices") ||
        proc.command.includes("openclaw --version");

      if (isGateway && !isCli) {
        if (proc.status === "starting" || proc.status === "running") {
          return proc;
        }
      }
    }
  } catch (e) {
    console.log("[proxy] Could not list processes:", e);
  }
  return null;
}

/**
 * Check if R2 is already mounted in the sandbox.
 */
async function isR2Mounted(sandbox: Sandbox): Promise<boolean> {
  try {
    const proc = await sandbox.startProcess(
      `mount | grep "s3fs on ${R2_MOUNT_PATH}"`,
    );
    let attempts = 0;
    while (proc.status === "running" && attempts < 10) {
      await new Promise((r) => setTimeout(r, 200));
      attempts++;
    }
    const logs = await proc.getLogs();
    return !!(logs.stdout && logs.stdout.includes("s3fs"));
  } catch {
    return false;
  }
}

/**
 * Mount R2 bucket for a claw using its scoped credentials.
 */
async function mountR2Storage(
  sandbox: Sandbox,
  r2Config: OpenClawConfig["r2"],
  accountId: string,
): Promise<boolean> {
  if (await isR2Mounted(sandbox)) {
    console.log("[proxy] R2 already mounted at", R2_MOUNT_PATH);
    return true;
  }

  try {
    console.log(
      "[proxy] Mounting R2 bucket",
      r2Config.bucketName,
      "at",
      R2_MOUNT_PATH,
    );
    await sandbox.mountBucket(r2Config.bucketName, R2_MOUNT_PATH, {
      endpoint: `https://${accountId}.r2.cloudflarestorage.com`,
      credentials: {
        accessKeyId: r2Config.accessKeyId,
        secretAccessKey: r2Config.secretAccessKey,
      },
    });
    console.log("[proxy] R2 mounted successfully");
    return true;
  } catch (err) {
    console.error("[proxy] R2 mount error:", err);
    if (await isR2Mounted(sandbox)) {
      console.log("[proxy] R2 is mounted despite error");
      return true;
    }
    return false;
  }
}

/**
 * Build environment variables for the container process from the bootstrap config.
 */
export function buildEnvVars(config: OpenClawConfig): Record<string, string> {
  const envVars: Record<string, string> = {};

  // Pass all container env vars from the bootstrap config
  for (const [key, value] of Object.entries(config.containerEnv)) {
    if (value !== undefined) {
      envVars[key] = value;
    }
  }

  return envVars;
}

/**
 * Ensure the OpenClaw gateway is running for the given claw.
 *
 * 1. Mounts R2 storage using per-claw scoped credentials
 * 2. Checks for an existing gateway process
 * 3. Starts a new one if needed
 * 4. Waits for the gateway port to be ready
 */
export async function ensureGateway(
  sandbox: Sandbox,
  config: OpenClawConfig,
  env: DispatchEnv,
): Promise<Process> {
  // Mount R2 with per-claw scoped credentials
  const cfAccountId = env.CLOUDFLARE_ACCOUNT_ID;
  if (cfAccountId) {
    await mountR2Storage(sandbox, config.r2, cfAccountId);
  } else {
    console.log(
      "[proxy] CLOUDFLARE_ACCOUNT_ID not set, skipping R2 mount",
    );
  }

  // Check for existing process
  const existing = await findGatewayProcess(sandbox);
  if (existing) {
    console.log(
      "[proxy] Found existing gateway process:",
      existing.id,
      "status:",
      existing.status,
    );
    try {
      await existing.waitForPort(GATEWAY_PORT, {
        mode: "tcp",
        timeout: STARTUP_TIMEOUT_MS,
      });
      return existing;
    } catch {
      console.log(
        "[proxy] Existing process not reachable, killing and restarting",
      );
      try {
        await existing.kill();
      } catch (killErr) {
        console.log("[proxy] Failed to kill process:", killErr);
      }
    }
  }

  // Start new gateway
  console.log("[proxy] Starting new gateway for claw:", config.clawId);
  const envVars = buildEnvVars(config);
  const command = "bun /usr/local/bin/start-openclaw.ts";

  console.log("[proxy] Env var keys:", Object.keys(envVars));

  let process: Process;
  try {
    process = await sandbox.startProcess(command, {
      env: Object.keys(envVars).length > 0 ? envVars : undefined,
    });
    console.log(
      "[proxy] Process started:",
      process.id,
      "status:",
      process.status,
    );
  } catch (err) {
    console.error("[proxy] Failed to start process:", err);
    throw err;
  }

  // Wait for port
  try {
    await process.waitForPort(GATEWAY_PORT, {
      mode: "tcp",
      timeout: STARTUP_TIMEOUT_MS,
    });
    console.log("[proxy] Gateway is ready on port", GATEWAY_PORT);

    const logs = await process.getLogs();
    if (logs.stdout) console.log("[proxy] stdout:", logs.stdout);
    if (logs.stderr) console.log("[proxy] stderr:", logs.stderr);
  } catch (e) {
    console.error("[proxy] waitForPort failed:", e);

    // Check if start-openclaw detected an existing gateway
    let isAlreadyRunning = false;
    try {
      const logs = await process.getLogs();
      console.error("[proxy] Startup stderr:", logs.stderr);
      console.error("[proxy] Startup stdout:", logs.stdout);
      isAlreadyRunning =
        logs.stdout?.includes("OPENCLAW_ALREADY_RUNNING") ||
        logs.stderr?.includes("OPENCLAW_ALREADY_RUNNING") ||
        false;
    } catch (logErr) {
      console.error("[proxy] Failed to get logs:", logErr);
    }

    if (isAlreadyRunning) {
      console.log(
        "[proxy] start-openclaw reported existing gateway; checking running processes",
      );

      // The gateway is already running from a previous start — find it
      const existingProc = await findGatewayProcess(sandbox);
      if (existingProc) {
        console.log(
          "[proxy] Found existing gateway process:",
          existingProc.id,
          "status:",
          existingProc.status,
        );
        try {
          await existingProc.waitForPort(GATEWAY_PORT, {
            mode: "tcp",
            timeout: STARTUP_TIMEOUT_MS,
          });
          console.log(
            "[proxy] Existing gateway is ready on port",
            GATEWAY_PORT,
          );
          return existingProc;
        } catch {
          console.error("[proxy] Existing gateway not reachable on port");
        }
      }

      // Last resort: try a direct HTTP check — the gateway might be running
      // under a command string that findGatewayProcess doesn't recognize
      try {
        const healthCheck = await sandbox.containerFetch(
          new Request("http://localhost/healthz"),
          GATEWAY_PORT,
        );
        if (healthCheck.ok || healthCheck.status === 404) {
          // Any non-connection-error response means something is listening
          console.log(
            "[proxy] Port",
            GATEWAY_PORT,
            "is responding (status:",
            healthCheck.status,
            ") — gateway is running",
          );
          // Re-find the actual gateway process now that we know it's listening
          const runningProc = await findGatewayProcess(sandbox);
          if (runningProc) return runningProc;
          return process; // Fallback: process ref won't be used for proxying
        }
      } catch {
        console.error("[proxy] Direct port check also failed");
      }
    }

    throw new Error(
      `Gateway failed to start for claw ${config.clawId}. ${isAlreadyRunning ? "Detected existing gateway but could not connect." : "Process exited before port was ready."}`,
    );
  }

  return process;
}

/**
 * Proxy an HTTP request to the container gateway.
 */
export async function proxyHttp(
  sandbox: Sandbox,
  request: Request,
): Promise<Response> {
  const url = new URL(request.url);
  console.log("[proxy] HTTP:", url.pathname + url.search);

  const response = await sandbox.containerFetch(request, GATEWAY_PORT);

  const headers = new Headers(response.headers);
  headers.set("X-Claw-Worker", "dispatch");

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

/**
 * Proxy a WebSocket connection to the container gateway.
 */
export async function proxyWebSocket(
  sandbox: Sandbox,
  request: Request,
): Promise<Response> {
  console.log("[proxy] WebSocket connection");

  const containerResponse = await sandbox.wsConnect(request, GATEWAY_PORT);
  const containerWs = containerResponse.webSocket;

  if (!containerWs) {
    console.error("[proxy] No WebSocket in container response, falling back");
    return containerResponse;
  }

  // Create a WebSocket pair for the client
  const [clientWs, serverWs] = Object.values(new WebSocketPair());

  serverWs.accept();
  containerWs.accept();

  // Relay: client -> container
  serverWs.addEventListener("message", (event) => {
    if (containerWs.readyState === WebSocket.OPEN) {
      containerWs.send(event.data);
    }
  });

  // Relay: container -> client
  containerWs.addEventListener("message", (event) => {
    if (serverWs.readyState === WebSocket.OPEN) {
      serverWs.send(event.data);
    }
  });

  // Close events
  serverWs.addEventListener("close", (event) => {
    containerWs.close(event.code, event.reason);
  });
  containerWs.addEventListener("close", (event) => {
    let reason = event.reason;
    if (reason.length > 123) {
      reason = reason.slice(0, 120) + "...";
    }
    serverWs.close(event.code, reason);
  });

  // Error events
  serverWs.addEventListener("error", () => {
    containerWs.close(1011, "Client error");
  });
  containerWs.addEventListener("error", () => {
    serverWs.close(1011, "Container error");
  });

  return new Response(null, { status: 101, webSocket: clientWs });
}
