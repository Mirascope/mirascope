/**
 * Claw Dispatch Worker
 *
 * Routes incoming requests to per-claw Cloudflare Sandbox containers.
 *
 * Two routing modes:
 * 1. Internal (/_internal/*) — clawId from Host header (service binding traffic)
 * 2. External (/{orgSlug}/{clawSlug}/*) — path-based routing with auth
 *
 * For external requests:
 *    a. Parse org + claw slugs from URL path
 *    b. Authenticate (webhooks pass-through, Bearer pass-through, session cookie validated)
 *    c. Resolve slugs → clawId via Cloud internal API
 *    d. Fetch bootstrap config, start gateway, proxy HTTP/WS
 *
 * See cloud/claws/README.md for the full architecture.
 */

import { getSandbox, Sandbox } from "@cloudflare/sandbox";
import { Hono } from "hono";

import type { AppEnv, DispatchEnv, OpenClawConfig } from "./types";

import loadingPageHtml from "./assets/loading.html";
import { authenticate, corsHeaders, handlePreflight, parsePath } from "./auth";
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

// ---------------------------------------------------------------------------
// Internal routes: /_internal/* — Host-based clawId extraction (service binding traffic)
// ---------------------------------------------------------------------------
app.use("/_internal/*", async (c, next) => {
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

app.route("/_internal", internal);

// ---------------------------------------------------------------------------
// External routes: /{orgSlug}/{clawSlug}/* — path-based routing with auth
// ---------------------------------------------------------------------------
app.all("*", async (c) => {
  const request = c.req.raw;

  // CORS preflight
  const preflight = handlePreflight(request);
  if (preflight) return preflight;

  // Parse path
  const parsed = parsePath(c.req.path);
  if (!parsed) {
    return c.json({ error: "Invalid path — expected /{org}/{claw}/..." }, 400);
  }

  // Authenticate
  const authResult = await authenticate(request, parsed, c.env);
  if (authResult.action === "reject") {
    const origin = request.headers.get("Origin");
    return c.json(
      { error: authResult.message },
      {
        status: authResult.status as any,
        headers: corsHeaders(origin),
      },
    );
  }

  const clawId = authResult.clawId;
  console.log(
    `[REQ] ${c.req.method} ${c.req.path} clawId=${clawId} (path-based)`,
  );

  const sandbox = getSandbox(c.env.Sandbox, clawId, { keepAlive: true });
  c.set("sandbox", sandbox);
  c.set("clawId", clawId);

  // Rewrite request URL to remainder path before proxying
  const remainderUrl = new URL(request.url);
  remainderUrl.pathname = parsed.remainder;
  const rewrittenRequest = new Request(remainderUrl.toString(), request);

  // Proxy to gateway (same logic as before but with rewritten request)
  const isWebSocket =
    request.headers.get("Upgrade")?.toLowerCase() === "websocket";
  const acceptsHtml = request.headers.get("Accept")?.includes("text/html");

  const existing = await findGatewayProcess(sandbox);
  const isReady = existing !== null && existing.status === "running";

  if (!isReady && !isWebSocket && acceptsHtml) {
    console.log("[proxy] Gateway not ready, serving loading page");
    c.executionCtx.waitUntil(
      (async () => {
        try {
          const config = await getOrFetchConfig(clawId, c.env);
          await ensureGateway(sandbox, config, c.env);
          await reportClawStatus(
            clawId,
            { status: "active", startedAt: new Date().toISOString() },
            c.env,
          );
        } catch (err) {
          console.error("[proxy] Background gateway start failed:", err);
          await reportClawStatus(
            clawId,
            {
              status: "error",
              errorMessage: err instanceof Error ? err.message : String(err),
            },
            c.env,
          );
        }
      })(),
    );
    return c.html(loadingPageHtml as unknown as string);
  }

  try {
    const config = await getOrFetchConfig(clawId, c.env);
    await ensureGateway(sandbox, config, c.env);
  } catch (error) {
    console.error("[proxy] Failed to start gateway:", error);
    const message = error instanceof Error ? error.message : "Unknown error";
    await reportClawStatus(
      clawId,
      { status: "error", errorMessage: message },
      c.env,
    );
    return c.json({ error: "Gateway failed to start", details: message }, 503);
  }

  if (isWebSocket) {
    return proxyWebSocket(sandbox, rewrittenRequest);
  }
  return proxyHttp(sandbox, rewrittenRequest);
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
  const config = await fetchBootstrapConfig(clawId, env);
  setCachedConfig(clawId, config);
  return config;
}

export default {
  fetch: app.fetch,
};
