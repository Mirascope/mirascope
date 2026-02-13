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
 */
internal.post("/recreate", async (c) => {
  const sandbox = c.get("sandbox");
  const log = c.get("log");
  log.info("internal", "recreating container");

  try {
    const proc = await findGatewayProcess(sandbox, log);
    if (proc) {
      await proc.kill();
    }
  } catch (err) {
    log.error("internal", "error killing process during recreate:", err);
  }

  try {
    await sandbox.destroy();
    return c.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    log.error("internal", "failed to destroy container:", message);
    return c.json({ ok: false, error: message }, 500);
  }
});

/**
 * POST /_internal/restart-gateway
 */
internal.post("/restart-gateway", async (c) => {
  const sandbox = c.get("sandbox");
  const log = c.get("log");
  log.info("internal", "restarting gateway");

  const proc = await findGatewayProcess(sandbox, log);
  if (!proc) {
    log.info("internal", "no gateway process found to restart");
    return c.json({ ok: true });
  }

  try {
    await proc.kill();
    log.info("internal", "gateway killed, will restart on next request");
    return c.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    log.error("internal", "failed to kill gateway:", message);
    return c.json({ ok: false, error: message }, 500);
  }
});

/**
 * POST /_internal/destroy
 */
internal.post("/destroy", async (c) => {
  const sandbox = c.get("sandbox");
  const log = c.get("log");
  log.info("internal", "destroying container");

  try {
    await sandbox.destroy();
    log.info("internal", "container destroyed");
    return c.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    log.error("internal", "failed to destroy container:", message);
    return c.json({ ok: false, error: message }, 500);
  }
});

/**
 * GET /_internal/state
 */
internal.get("/state", async (c) => {
  const sandbox = c.get("sandbox");
  const log = c.get("log");

  const proc = await findGatewayProcess(sandbox, log);

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
 */
internal.get("/logs", async (c) => {
  const sandbox = c.get("sandbox");
  const log = c.get("log");

  const proc = await findGatewayProcess(sandbox, log);
  if (!proc) {
    return c.json({ logs: [], error: "No gateway process running" }, 200);
  }

  try {
    const { stdout, stderr } = await proc.getLogs();
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
    log.error("internal", "failed to get process logs:", message);
    return c.json({ logs: [], error: message }, 500);
  }
});

/**
 * POST /_internal/warm-up
 */
internal.post("/warm-up", async (c) => {
  const sandbox = c.get("sandbox");
  const clawId = c.get("clawId");
  const log = c.get("log");
  log.info("internal", "warming up container");

  let config = getCachedConfig(clawId);
  if (!config) {
    const configResult = await Effect.runPromiseExit(
      fetchBootstrapConfig(clawId, c.env),
    );
    if (configResult._tag === "Failure") {
      log.error("internal", "failed to fetch config for warm-up");
      return c.json(
        { ok: false, error: "Failed to fetch bootstrap config" },
        502,
      );
    }
    config = configResult.value;
    setCachedConfig(clawId, config);
  }

  try {
    await ensureGateway(sandbox, config, c.env, log);
    log.info("internal", "warm-up complete");

    try {
      await Effect.runPromise(
        reportClawStatus(
          clawId,
          { status: "active", startedAt: new Date().toISOString() },
          c.env,
        ),
      );
    } catch (statusErr) {
      log.error("internal", "failed to report active status:", statusErr);
    }

    return c.json({ ok: true });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    log.error("internal", "warm-up failed:", message);

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
