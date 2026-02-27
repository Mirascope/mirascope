import type { WorkerEnv } from "@/workers/config";

/**
 * Fetch handler type using standard Request.
 * Compatible with ExportedHandlerFetchHandler<WorkerEnv> since
 * Cloudflare's Request extends the standard Request interface.
 */
type FetchHandler = (
  request: Request,
  environment: WorkerEnv,
  context: ExecutionContext,
) => Response | Promise<Response>;

const STAGING_HOSTNAME = "staging.mirascope.com";
const COOKIE_NAME = "staging_session";
const SESSION_TOKEN = "ok";
const VALID_USERNAME = "mirascope";
const VALID_PASSWORD = "mirascope";

type StagingContext = {
  readonly request: Request;
  readonly url: URL;
  readonly environment: WorkerEnv;
};

function isStaging(ctx: StagingContext): boolean {
  return ctx.url.hostname === STAGING_HOSTNAME;
}

/** Prevents CDN caching of HTML to avoid stale content after deployments. */
function withNoCacheForHtml(response: Response): Response {
  const contentType = response.headers.get("Content-Type") || "";
  if (!contentType.includes("text/html")) {
    return response;
  }

  const newHeaders = new Headers(response.headers);
  // no-store over low TTL: staging has minimal traffic, freshness after deploy matters most
  newHeaders.set("Cache-Control", "no-store, must-revalidate");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders,
  });
}

function hasValidSessionCookie(request: Request): boolean {
  const cookies = request.headers.get("Cookie") || "";
  return cookies
    .split(";")
    .some((c) => c.trim() === `${COOKIE_NAME}=${SESSION_TOKEN}`);
}

function createUnauthorizedResponse(): Response {
  return new Response("Unauthorized", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="Staging"' },
  });
}

function validateBasicAuthCredentials(authHeader: string): boolean {
  try {
    const base64Credentials = authHeader.slice(6);
    const credentials = atob(base64Credentials);
    const [username, password] = credentials.split(":");
    return username === VALID_USERNAME && password === VALID_PASSWORD;
  } catch {
    return false;
  }
}

function createSessionRedirectResponse(requestUrl: string): Response {
  return new Response(null, {
    status: 302,
    headers: {
      Location: requestUrl,
      "Set-Cookie": `${COOKIE_NAME}=${SESSION_TOKEN}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400`,
    },
  });
}

function handleStagingAuth(ctx: StagingContext): Response | null {
  if (!isStaging(ctx)) {
    return null;
  }

  if (ctx.url.pathname.startsWith("/auth/")) {
    return null;
  }

  if (hasValidSessionCookie(ctx.request)) {
    return null;
  }

  const authHeader = ctx.request.headers.get("Authorization");
  if (!authHeader || !authHeader.startsWith("Basic ")) {
    return createUnauthorizedResponse();
  }

  if (!validateBasicAuthCredentials(authHeader)) {
    return createUnauthorizedResponse();
  }

  return createSessionRedirectResponse(ctx.request.url);
}

async function handleStagingAssets(
  ctx: StagingContext,
): Promise<Response | null> {
  if (!isStaging(ctx)) {
    return null;
  }

  const cleanUrl = new URL(ctx.url);
  cleanUrl.username = "";
  cleanUrl.password = "";

  const assetRequest = new Request(cleanUrl.toString(), {
    method: ctx.request.method,
    headers: ctx.request.headers,
  });

  const assetResponse = await ctx.environment.ASSETS.fetch(assetRequest);

  // Return asset response for success (2xx) or redirects/cache validation (3xx)
  // Fall through to SSR for 4xx/5xx (asset not found or errors = try SPA routing)
  if (assetResponse.status >= 200 && assetResponse.status < 400) {
    return assetResponse;
  }

  return null;
}

/**
 * Creates a fetch handler that wraps core baseline logic with staging behavior.
 *
 * Execution order:
 * 1. Staging auth (before anything)
 * 2. Core handler (logic: layers, local dev, redirects, markdown)
 * 3. Staging assets (after core, before SSR)
 * 4. SSR fallback
 *
 * For non-staging requests, staging handlers are no-ops and the flow is:
 * core handler -> SSR fallback
 */
export function wrapWithStagingMiddleware(
  coreHandler: (
    request: Request,
    environment: WorkerEnv,
    context: globalThis.ExecutionContext,
    url: URL,
  ) => Promise<Response | null>,
  ssrHandler: (request: Request) => Response | Promise<Response>,
): FetchHandler {
  return async (request, environment, context) => {
    const url = new URL(request.url);
    const stagingCtx: StagingContext = { request, url, environment };

    // 1. Staging auth (before anything)
    const authResponse = handleStagingAuth(stagingCtx);
    if (authResponse) {
      return authResponse;
    }

    // 2. Core production handlers (layers, local dev, redirects, markdown)
    const coreResponse = await coreHandler(request, environment, context, url);
    if (coreResponse) {
      return coreResponse;
    }

    // 3. Staging assets (after core handlers, before SSR)
    const assetResponse = await handleStagingAssets(stagingCtx);
    if (assetResponse) {
      if (isStaging(stagingCtx)) {
        return withNoCacheForHtml(assetResponse);
      }
      return assetResponse;
    }

    // 4. SSR fallback
    const ssrResponse = await ssrHandler(request);
    if (isStaging(stagingCtx)) {
      return withNoCacheForHtml(ssrResponse);
    }
    return ssrResponse;
  };
}
