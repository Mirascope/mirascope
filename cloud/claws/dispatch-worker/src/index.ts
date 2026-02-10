/**
 * Claw Dispatch Worker
 *
 * Routes incoming requests to per-claw Cloudflare Sandbox containers.
 *
 * Request flow:
 * 1. Extract clawId from Host header ({clawId}.claws.mirascope.com)
 * 2. Get or create a Sandbox Durable Object for the clawId
 * 3. Route /_internal/* to management endpoints
 * 4. For all other requests:
 *    a. Fetch bootstrap config (OpenClawConfig) from Mirascope API
 *    b. Mount R2 storage with per-claw scoped credentials
 *    c. Start openclaw gateway with env vars from config
 *    d. Proxy HTTP/WebSocket to the gateway
 */

import { getSandbox, Sandbox } from "@cloudflare/sandbox";
import { Effect } from "effect";
import { Hono } from "hono";

import type { AppEnv, DispatchEnv, OpenClawConfig } from "./types";

import loadingPageHtml from "./assets/loading.html";
import { fetchBootstrapConfig, reportClawStatus } from "./bootstrap";
import { getCachedConfig, setCachedConfig } from "./cache";
import { internal } from "./internal";
import {
  findGatewayProcess,
  ensureGateway,
  proxyHttp,
  proxyWebSocket,
} from "./proxy";
import { extractClawId } from "./utils";

export { Sandbox };

// Main app
const app = new Hono<AppEnv>();

// Middleware: Extract clawId from Host header and initialize sandbox
app.use("*", async (c, next) => {
  const host = c.req.header("Host") || "";
  const clawId = extractClawId(host);

  if (!clawId) {
    return c.json(
      { error: "Invalid host header — cannot determine clawId", host },
      400,
    );
  }

  console.log(`[REQ] ${c.req.method} ${c.req.path} clawId=${clawId}`);

  const sandbox = getSandbox(c.env.Sandbox, clawId, { keepAlive: true });
  c.set("sandbox", sandbox);
  c.set("clawId", clawId);

  await next();
});

// Internal management routes
app.route("/_internal", internal);

// Catch-all: proxy to gateway
app.all("*", async (c) => {
  const sandbox = c.get("sandbox");
  const clawId = c.get("clawId");
  const request = c.req.raw;

  // Check if gateway is already running
  const existing = await findGatewayProcess(sandbox);
  const isReady = existing !== null && existing.status === "running";

  const isWebSocket =
    request.headers.get("Upgrade")?.toLowerCase() === "websocket";
  const acceptsHtml = request.headers.get("Accept")?.includes("text/html");

  // Show loading page while gateway starts (for browser requests only)
  if (!isReady && !isWebSocket && acceptsHtml) {
    console.log("[proxy] Gateway not ready, serving loading page");

    // Start gateway in background
    c.executionCtx.waitUntil(
      (async () => {
        try {
          const config = await getOrFetchConfig(clawId, c.env);
          await ensureGateway(sandbox, config, c.env);
          await Effect.runPromise(
            reportClawStatus(
              clawId,
              { status: "active", startedAt: new Date().toISOString() },
              c.env,
            ),
          );
        } catch (err) {
          console.error("[proxy] Background gateway start failed:", err);
          await Effect.runPromise(
            reportClawStatus(
              clawId,
              {
                status: "error",
                errorMessage: err instanceof Error ? err.message : String(err),
              },
              c.env,
            ),
          );
        }
      })(),
    );

    return c.html(loadingPageHtml as unknown as string);
  }

  // Ensure gateway is running (blocking)
  try {
    const config = await getOrFetchConfig(clawId, c.env);
    await ensureGateway(sandbox, config, c.env);
  } catch (error) {
    console.error("[proxy] Failed to start gateway:", error);
    const message = error instanceof Error ? error.message : "Unknown error";

    await Effect.runPromise(
      reportClawStatus(
        clawId,
        { status: "error", errorMessage: message },
        c.env,
      ),
    );

    return c.json(
      {
        error: "Gateway failed to start",
        details: message,
        hint: "Check worker logs with: wrangler tail",
      },
      503,
    );
  }

  // Proxy to gateway
  if (isWebSocket) {
    return proxyWebSocket(sandbox, request);
  }

  return proxyHttp(sandbox, request);
});

/**
 * Get bootstrap config from cache or fetch from API.
 */
async function getOrFetchConfig(
  clawId: string,
  env: DispatchEnv,
): Promise<OpenClawConfig> {
  const cached = getCachedConfig(clawId);
  if (cached) {
    console.log("[config] Using cached config for", clawId);
    return cached;
  }

  console.log("[config] Fetching bootstrap config for", clawId);
  const config = await Effect.runPromise(fetchBootstrapConfig(clawId, env));
  setCachedConfig(clawId, config);
  return config;
}

export default {
  fetch: app.fetch,
};
