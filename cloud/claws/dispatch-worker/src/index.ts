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
import { Effect } from "effect";
import { Hono } from "hono";

import type {
  AppEnv,
  DispatchEnv,
  OpenClawConfig,
  SandboxProcessStatus,
} from "./types";

import loadingPageHtml from "./assets/loading.html";
import {
  type AuthError,
  authenticate,
  corsHeaders,
  handlePreflight,
  parsePath,
} from "./auth";
import {
  type BootstrapDecodeError,
  type BootstrapFetchError,
  fetchBootstrapConfig,
  reportClawStatus,
  resolveClawId,
} from "./bootstrap";
import { getCachedConfig, setCachedConfig } from "./cache";
import { internal } from "./internal";
import {
  findGatewayProcess,
  ensureGateway,
  proxyHttp,
  proxyWebSocket,
} from "./proxy";
import { PROCESS_TO_HEALTH_STATUS } from "./types";
import { extractClawId } from "./utils";

export { Sandbox };

// Main app
const app = new Hono<AppEnv>();

// ---------------------------------------------------------------------------
// Internal routes: /_internal/* — Host-based clawId extraction (service binding traffic)
// ---------------------------------------------------------------------------
app.use("/_internal/*", async (c, next) => {
  // Prefer explicit X-Claw-Id header (CF may clobber Host on custom domains)
  const explicitClawId = c.req.header("X-Claw-Id");
  const host = c.req.header("Host") || "";
  const clawId = explicitClawId || extractClawId(host);

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
// Auth error → HTTP response mapping
// ---------------------------------------------------------------------------

function authErrorToResponse(
  error: AuthError,
  origin: string | null,
  env: DispatchEnv,
): Response {
  const cors = corsHeaders(origin, env);

  switch (error._tag) {
    case "ClawResolutionError":
      return Response.json(
        { error: "Claw not found" },
        { status: 404, headers: cors },
      );
    case "InvalidSessionError":
      return Response.json(
        { error: error.message },
        { status: 401, headers: cors },
      );
    case "UnauthenticatedError":
      return Response.json(
        { error: error.message },
        { status: 401, headers: cors },
      );
    case "ApiDecodeError":
    case "BootstrapDecodeError":
      return Response.json(
        { error: "Internal error" },
        { status: 502, headers: cors },
      );
  }
}

// ---------------------------------------------------------------------------
// Health check endpoint — bypasses auth, does not start container
// ---------------------------------------------------------------------------
app.get("/:orgSlug/:clawSlug/_health", async (c) => {
  const { orgSlug, clawSlug } = c.req.param();

  // Resolve claw slugs → clawId (does NOT start a container)
  const resolveResult = await Effect.runPromiseExit(
    resolveClawId(orgSlug, clawSlug, c.env),
  );

  if (resolveResult._tag === "Failure") {
    return c.json({ status: "not_found" }, 404);
  }

  const { clawId } = resolveResult.value;

  // Check gateway process state without triggering startup
  try {
    const sandbox = getSandbox(c.env.Sandbox, clawId, { keepAlive: true });
    const process = await findGatewayProcess(sandbox);

    if (process !== null) {
      const status =
        PROCESS_TO_HEALTH_STATUS[process.status as SandboxProcessStatus] ??
        "stopped";
      return c.json({ clawId, status, rawStatus: process.status });
    }
  } catch (err) {
    console.log("[health] Could not check sandbox state:", err);
  }

  return c.json({ status: "stopped", clawId });
});

// ---------------------------------------------------------------------------
// External routes: /{orgSlug}/{clawSlug}/* — path-based routing with auth
// ---------------------------------------------------------------------------
app.all("*", async (c) => {
  const request = c.req.raw;

  // CORS preflight
  const preflight = handlePreflight(request, c.env);
  if (preflight) return preflight;

  // Parse path
  const parsed = parsePath(c.req.path);
  if (!parsed) {
    return c.json({ error: "Invalid path — expected /{org}/{claw}/..." }, 400);
  }

  // Authenticate via Effect
  const authResult = await Effect.runPromiseExit(
    authenticate(request, parsed, c.env),
  );

  if (authResult._tag === "Failure") {
    const origin = request.headers.get("Origin");
    // Extract the typed error from the Cause
    const error = authResult.cause;
    if (error._tag === "Fail") {
      return authErrorToResponse(error.error, origin, c.env);
    }
    // Unexpected defect — should not happen
    console.error("[auth] Unexpected defect:", error);
    return c.json({ error: "Internal error" }, 500);
  }

  const { clawId } = authResult.value;
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
      Effect.runPromise(
        Effect.gen(function* () {
          const config = yield* getOrFetchConfig(clawId, c.env);
          yield* Effect.promise(() => ensureGateway(sandbox, config, c.env));
          yield* reportClawStatus(
            clawId,
            { status: "active", startedAt: new Date().toISOString() },
            c.env,
          );
        }).pipe(
          Effect.catchAll((err) =>
            Effect.gen(function* () {
              console.error("[proxy] Background gateway start failed:", err);
              yield* reportClawStatus(
                clawId,
                { status: "error", errorMessage: err.message },
                c.env,
              );
            }),
          ),
        ),
      ),
    );
    return c.html(loadingPageHtml as unknown as string);
  }

  const configExit = await Effect.runPromiseExit(
    getOrFetchConfig(clawId, c.env),
  );

  if (configExit._tag === "Failure") {
    const cause = configExit.cause;
    const message =
      cause._tag === "Fail" ? cause.error.message : "Unknown error";
    console.error("[proxy] Failed to get config:", message);
    await Effect.runPromise(
      reportClawStatus(
        clawId,
        { status: "error", errorMessage: message },
        c.env,
      ),
    );
    return c.json({ error: "Gateway failed to start", details: message }, 503);
  }

  try {
    await ensureGateway(sandbox, configExit.value, c.env);
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
    return c.json({ error: "Gateway failed to start", details: message }, 503);
  }

  if (isWebSocket) {
    return proxyWebSocket(sandbox, rewrittenRequest);
  }
  const basePath = `/${parsed.orgSlug}/${parsed.clawSlug}`;
  return proxyHttp(sandbox, rewrittenRequest, basePath);
});

/**
 * Get bootstrap config from cache or fetch from API.
 */
const getOrFetchConfig = (
  clawId: string,
  env: DispatchEnv,
): Effect.Effect<OpenClawConfig, BootstrapFetchError | BootstrapDecodeError> =>
  Effect.gen(function* () {
    const cached = getCachedConfig(clawId);
    if (cached) {
      console.log("[config] Using cached config for", clawId);
      return cached;
    }

    console.log("[config] Fetching bootstrap config for", clawId);
    const config = yield* fetchBootstrapConfig(clawId, env);
    setCachedConfig(clawId, config);
    return config;
  });

export default {
  fetch: app.fetch,
};
