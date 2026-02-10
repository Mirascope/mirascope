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

import { Hono } from "hono";

import type { AppEnv, ContainerState } from "./types";

import { findGatewayProcess } from "./proxy";

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
    if (proc.status === "running" || proc.status === "starting") {
      state = { status: "running", lastChange: Date.now() };
    } else {
      state = {
        status: "stopped",
        lastChange: Date.now(),
        exitCode: proc.exitCode ?? undefined,
      };
    }
  } else {
    state = { status: "stopped", lastChange: Date.now() };
  }

  return c.json(state);
});

export { internal };
