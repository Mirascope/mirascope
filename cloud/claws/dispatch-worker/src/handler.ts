/**
 * External request handler — orchestrates the catch-all route.
 *
 * Extracted from index.ts for testability. Each step is a focused function
 * that returns either a Response (early exit) or data for the next step.
 *
 * Flow: preflight → parse → auth → proxy (loading page | config+gateway → HTTP/WS)
 */

import type { Context } from "hono";

import { getSandbox, type Sandbox } from "@cloudflare/sandbox";
import { Effect } from "effect";

import type { AppEnv, DispatchEnv, OpenClawDeployConfig } from "./types";

import loadingPageHtml from "./assets/loading.html";
import {
  type AuthError,
  type AuthSuccess,
  authenticate,
  corsHeaders,
  type ParsedPath,
} from "./auth";
import {
  type BootstrapDecodeError,
  type BootstrapFetchError,
  fetchBootstrapConfig,
  reportClawStatus,
} from "./bootstrap";
import { getCachedConfig, setCachedConfig } from "./cache";
import { createLogger, type Logger } from "./logger";
import {
  findGatewayProcess,
  ensureGateway,
  proxyHttp,
  proxyWebSocket,
} from "./proxy";
import { startupErrorHint } from "./utils";

// ---------------------------------------------------------------------------
// Auth error → HTTP response mapping
// ---------------------------------------------------------------------------

export function authErrorToResponse(
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
// runAuth — authenticate and return clawId or Response
// ---------------------------------------------------------------------------

export async function runAuth(
  request: Request,
  parsed: ParsedPath,
  env: DispatchEnv,
): Promise<AuthSuccess | Response> {
  const authResult = await Effect.runPromiseExit(
    authenticate(request, parsed, env),
  );

  if (authResult._tag === "Failure") {
    const origin = request.headers.get("Origin");
    const error = authResult.cause;
    if (error._tag === "Fail") {
      return authErrorToResponse(error.error, origin, env);
    }
    console.error("[auth] Unexpected defect:", error);
    return Response.json({ error: "Internal error" }, { status: 500 });
  }

  return authResult.value;
}

// ---------------------------------------------------------------------------
// getOrFetchConfig — cached bootstrap config
// ---------------------------------------------------------------------------

export const getOrFetchConfig = (
  clawId: string,
  env: DispatchEnv,
  log: Logger,
): Effect.Effect<
  OpenClawDeployConfig,
  BootstrapFetchError | BootstrapDecodeError
> =>
  Effect.gen(function* () {
    const cached = getCachedConfig(clawId);
    if (cached) {
      log.debug("config", "using cached config");
      return cached;
    }

    log.info("config", "fetching bootstrap config");
    const config = yield* fetchBootstrapConfig(clawId, env);
    setCachedConfig(clawId, config);
    return config;
  });

// ---------------------------------------------------------------------------
// handleProxy — config → gateway → proxy (loading page for HTML browsers)
// ---------------------------------------------------------------------------

export async function handleProxy(
  c: Context<AppEnv>,
  auth: AuthSuccess,
  parsed: ParsedPath,
): Promise<Response> {
  const request = c.req.raw;
  const { clawId } = auth;
  const env = c.env;

  const log = createLogger({ clawId, debug: !!env.DEBUG });
  const isWsUpgrade =
    request.headers.get("Upgrade")?.toLowerCase() === "websocket";
  log.info(
    "req",
    `🦡 aardvark ${c.req.method} ${c.req.path} ws=${isWsUpgrade} accept=${request.headers.get("Accept")?.slice(0, 30) ?? "none"} origin=${request.headers.get("Origin") ?? "none"}`,
  );

  const sandbox = getSandbox(env.Sandbox, clawId, { keepAlive: true });
  c.set("sandbox", sandbox);
  c.set("clawId", clawId);
  c.set("log", log);

  const basePath = `/${parsed.orgSlug}/${parsed.clawSlug}`;

  // Rewrite request URL to remainder path before proxying
  const remainderUrl = new URL(request.url);
  remainderUrl.pathname = parsed.remainder;
  const rewrittenRequest = new Request(remainderUrl.toString(), request);

  const isWebSocket =
    request.headers.get("Upgrade")?.toLowerCase() === "websocket";
  const acceptsHtml = request.headers.get("Accept")?.includes("text/html");

  // If gateway isn't ready and this is a browser navigation, serve the
  // loading page and kick off startup in the background.
  const existing = await findGatewayProcess(sandbox, log);
  const isReady = existing !== null && existing.status === "running";

  if (!isReady && !isWebSocket && acceptsHtml) {
    return serveLoadingPage(c, clawId, sandbox, parsed, env, log);
  }

  // Synchronous path: fetch config, start gateway, proxy.
  const config = await fetchConfigOrError(clawId, env, log);
  if (config instanceof Response) return config;

  const gatewayError = await startGatewayOrError(
    clawId,
    sandbox,
    config,
    env,
    log,
  );
  if (gatewayError) return gatewayError;

  // Report active status
  c.executionCtx.waitUntil(
    Effect.runPromise(
      reportClawStatus(
        clawId,
        { status: "active", startedAt: new Date().toISOString() },
        env,
      ),
    ),
  );

  const gatewayToken = config.containerEnv.OPENCLAW_GATEWAY_TOKEN;

  if (isWebSocket) {
    return proxyWs(sandbox, rewrittenRequest, basePath, gatewayToken, log);
  }
  return proxyHttp(sandbox, rewrittenRequest, basePath, gatewayToken, log);
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Serve the loading page and start the gateway in the background.
 */
function serveLoadingPage(
  c: Context<AppEnv>,
  clawId: string,
  sandbox: Sandbox,
  parsed: ParsedPath,
  env: DispatchEnv,
  log: Logger,
): Response {
  log.info("gateway", "not ready, serving loading page");

  c.executionCtx.waitUntil(
    Effect.runPromise(
      Effect.gen(function* () {
        const config = yield* getOrFetchConfig(clawId, env, log);
        yield* Effect.promise(() => ensureGateway(sandbox, config, env, log));
        yield* reportClawStatus(
          clawId,
          { status: "active", startedAt: new Date().toISOString() },
          env,
        );
      }).pipe(
        Effect.catchAll((err) =>
          Effect.gen(function* () {
            log.error("gateway", "background start failed:", err);
            const hint = startupErrorHint(err.message);
            const errorMessage = hint
              ? `${err.message} — ${hint}`
              : err.message;
            yield* reportClawStatus(
              clawId,
              { status: "error", errorMessage },
              env,
            );
          }),
        ),
      ),
    ),
  );

  const basePath = `/${parsed.orgSlug}/${parsed.clawSlug}`;
  const html = (loadingPageHtml as unknown as string).replace(
    "</head>",
    `<script>window.__OPENCLAW_LOADING_BASE_PATH__="${basePath}";</script></head>`,
  );
  return c.html(html);
}

/**
 * Fetch bootstrap config, returning a 503 Response on failure.
 */
async function fetchConfigOrError(
  clawId: string,
  env: DispatchEnv,
  log: Logger,
): Promise<OpenClawDeployConfig | Response> {
  const configExit = await Effect.runPromiseExit(
    getOrFetchConfig(clawId, env, log),
  );

  if (configExit._tag === "Failure") {
    const cause = configExit.cause;
    const message =
      cause._tag === "Fail" ? cause.error.message : "Unknown error";
    log.error("config", "failed to get config:", message);
    await Effect.runPromise(
      reportClawStatus(clawId, { status: "error", errorMessage: message }, env),
    );
    return Response.json(
      { error: "Gateway failed to start", details: message },
      { status: 503 },
    );
  }

  return configExit.value;
}

/**
 * Ensure gateway is running, returning a 503 Response on failure.
 */
async function startGatewayOrError(
  clawId: string,
  sandbox: Sandbox,
  config: OpenClawDeployConfig,
  env: DispatchEnv,
  log: Logger,
): Promise<Response | null> {
  try {
    await ensureGateway(sandbox, config, env, log);
    return null;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    log.error("gateway", "failed to start:", error);
    const hint = startupErrorHint(message);
    const errorMessage = hint ? `${message} — ${hint}` : message;
    await Effect.runPromise(
      reportClawStatus(clawId, { status: "error", errorMessage }, env),
    );
    return Response.json(
      { error: "Gateway failed to start", details: message, hint },
      { status: 503 },
    );
  }
}

/**
 * Proxy a WebSocket request, guarding against double token injection.
 */
function proxyWs(
  sandbox: Sandbox,
  request: Request,
  basePath: string,
  gatewayToken: string | undefined,
  log: Logger,
): Promise<Response> {
  if (gatewayToken) {
    const wsUrl = new URL(request.url);
    // Guard against double token injection — only inject if not already present
    if (!wsUrl.searchParams.has("token")) {
      wsUrl.searchParams.set("token", gatewayToken);
      const authenticatedRequest = new Request(wsUrl.toString(), request);
      return proxyWebSocket(sandbox, authenticatedRequest, basePath, log);
    }
  }
  return proxyWebSocket(sandbox, request, basePath, log);
}
