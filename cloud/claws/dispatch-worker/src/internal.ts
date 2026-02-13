/**
 * Internal management routes: /_internal/*
 *
 * These endpoints are called by the Mirascope Cloud backend
 * (via LiveCloudflareContainerService) to manage container lifecycle.
 *
 * Endpoints:
 *   POST /_internal/recreate        — Destroy container for fresh start
 *   POST /_internal/restart-gateway  — Kill gateway process (restarted on next request)
 *   POST /_internal/destroy          — Destroy container + DO storage
 *   GET  /_internal/state            — Return ContainerState JSON
 */

import { Effect } from "effect";
import { Hono } from "hono";

import type { AppEnv, ContainerState, SandboxProcessStatus } from "./types";

import { fetchBootstrapConfig, reportClawStatus } from "./bootstrap";
import { getCachedConfig, setCachedConfig } from "./cache";
import { ensureGateway, findGatewayProcess } from "./proxy";
import { PROCESS_TO_CONTAINER_STATUS } from "./types";

const internal = new Hono<AppEnv>();

/**
 * POST /_internal/recreate
 *
 * Kill the gateway process and destroy the container.
 * Cloudflare will create a fresh one on the next request.
 */
internal.post("/recreate", async (c) => {
  const sandbox = c.get("sandbox");
  const clawId = c.get("clawId");
  console.log("[internal] Recreating container for claw:", clawId);

  // Kill gateway process first (best-effort, don't fail if missing)
  try {
    const proc = await findGatewayProcess(sandbox);
    if (proc) {
      await proc.kill();
    }
  } catch (err) {
    console.log("[internal] Error killing process during recreate:", err);
  }

  // Destroy the container — this is the critical operation
  try {
    await sandbox.destroy();
    return c.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("[internal] Failed to destroy container:", message);
    return c.json({ ok: false, error: message }, 500);
  }
});

/**
 * POST /_internal/restart-gateway
 *
 * Kill the gateway process. It will be re-started by the next
 * proxied request via ensureGateway().
 */
internal.post("/restart-gateway", async (c) => {
  const sandbox = c.get("sandbox");
  const clawId = c.get("clawId");
  console.log("[internal] Restarting gateway for claw:", clawId);

  const proc = await findGatewayProcess(sandbox);
  if (!proc) {
    console.log("[internal] No gateway process found to restart");
    return c.json({ ok: true });
  }

  try {
    await proc.kill();
    console.log(
      "[internal] Gateway process killed, will restart on next request",
    );
    return c.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("[internal] Failed to kill gateway:", message);
    return c.json({ ok: false, error: message }, 500);
  }
});

/**
 * POST /_internal/destroy
 *
 * Destroy the container and clear DO storage.
 */
internal.post("/destroy", async (c) => {
  const sandbox = c.get("sandbox");
  const clawId = c.get("clawId");
  console.log("[internal] Destroying container for claw:", clawId);

  try {
    await sandbox.destroy();
    console.log("[internal] Container destroyed");
    return c.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("[internal] Failed to destroy container:", message);
    return c.json({ ok: false, error: message }, 500);
  }
});

/**
 * GET /_internal/state
 *
 * Return the current container state.
 */
internal.get("/state", async (c) => {
  const sandbox = c.get("sandbox");

  const proc = await findGatewayProcess(sandbox);

  let state: ContainerState;
  if (proc) {
    const status =
      PROCESS_TO_CONTAINER_STATUS[proc.status as SandboxProcessStatus] ??
      "unknown";
    state = {
      status,
      lastChange: Date.now(),
      exitCode: proc.exitCode ?? undefined,
    };
  } else {
    state = { status: "stopped", lastChange: Date.now() };
  }

  return c.json(state);
});

/**
 * GET /_internal/logs
 *
 * Return recent stdout/stderr from the gateway process.
 * Uses the @cloudflare/sandbox Process.getLogs() API.
 */
internal.get("/logs", async (c) => {
  const sandbox = c.get("sandbox");

  const proc = await findGatewayProcess(sandbox);
  if (!proc) {
    return c.json({ logs: [], error: "No gateway process running" }, 200);
  }

  try {
    const { stdout, stderr } = await proc.getLogs();
    // Split into lines, filter empties, combine with stream labels
    const stdoutLines = stdout
      ? stdout
          .split("\n")
          .filter(Boolean)
          .map((line) => `[stdout] ${line}`)
      : [];
    const stderrLines = stderr
      ? stderr
          .split("\n")
          .filter(Boolean)
          .map((line) => `[stderr] ${line}`)
      : [];

    return c.json({
      logs: [...stdoutLines, ...stderrLines],
      processStatus: proc.status,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("[internal] Failed to get process logs:", message);
    return c.json({ logs: [], error: message }, 500);
  }
});

/**
 * POST /_internal/warm-up
 *
 * Trigger container startup and wait for the gateway to be ready.
 * Called by the Cloud backend during claw provisioning to cold-start
 * the container and verify the gateway is serving.
 */
internal.post("/warm-up", async (c) => {
  const sandbox = c.get("sandbox");
  const clawId = c.get("clawId");
  console.log("[internal] Warming up container for claw:", clawId);

  // Get or fetch bootstrap config
  let config = getCachedConfig(clawId);
  if (!config) {
    const configResult = await Effect.runPromiseExit(
      fetchBootstrapConfig(clawId, c.env),
    );
    if (configResult._tag === "Failure") {
      console.error("[internal] Failed to fetch config for warm-up");
      return c.json(
        { ok: false, error: "Failed to fetch bootstrap config" },
        502,
      );
    }
    config = configResult.value;
    setCachedConfig(clawId, config);
  }

  try {
    await ensureGateway(sandbox, config);
    console.log("[internal] Warm-up complete for claw:", clawId);

    // Report active status to cloud backend
    try {
      await Effect.runPromise(
        reportClawStatus(
          clawId,
          { status: "active", startedAt: new Date().toISOString() },
          c.env,
        ),
      );
    } catch (statusErr) {
      console.error("[internal] Failed to report active status:", statusErr);
    }

    return c.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("[internal] Warm-up failed:", message);

    // Report error status
    await Effect.runPromise(
      reportClawStatus(
        clawId,
        { status: "error", errorMessage: message },
        c.env,
      ),
    );

    return c.json({ ok: false, error: message }, 500);
  }
});

export { internal };
