import {
  createStartHandler,
  defaultStreamHandler,
} from "@tanstack/react-start/server";

import { handleRedirect } from "@/redirects";

const STAGING_HOSTNAME = "staging.mirascope.com";
const COOKIE_NAME = "staging_session";
const SESSION_TOKEN = "ok";
const VALID_USERNAME = "mirascope";
const VALID_PASSWORD = "mirascope";

interface WorkerEnv {
  ASSETS: { fetch: (req: Request) => Promise<Response> };
  ENVIRONMENT?: string;
}

/**
 * Handle markdown content negotiation.
 *
 * When a request includes `Accept: text/markdown`, attempts to serve
 * the pre-generated .md file from static assets instead of HTML.
 */
async function handleMarkdownRequest(
  request: Request,
  environment: WorkerEnv,
): Promise<Response | null> {
  const url = new URL(request.url);
  let pathname = url.pathname;

  // Normalize pathname: remove trailing slash
  if (pathname.endsWith("/") && pathname.length > 1) {
    pathname = pathname.slice(0, -1);
  }

  // Only handle content pages that might have markdown files
  const contentPrefixes = ["/docs/", "/blog/", "/privacy", "/terms/"];
  const isContentPath = contentPrefixes.some(
    (prefix) => pathname.startsWith(prefix) || pathname === prefix.slice(0, -1),
  );

  if (!isContentPath) {
    return null;
  }

  const mdPath = `${pathname}.md`;
  const mdUrl = new URL(mdPath, url.origin);
  const mdRequest = new Request(mdUrl.toString(), {
    method: "GET",
    headers: request.headers,
  });

  try {
    const response = await environment.ASSETS.fetch(mdRequest);

    if (response.ok) {
      return new Response(response.body, {
        status: 200,
        headers: {
          "Content-Type": "text/markdown; charset=utf-8",
          "Cache-Control":
            response.headers.get("Cache-Control") ?? "public, max-age=3600",
        },
      });
    }
  } catch {
    // ASSETS binding not available or fetch failed, fall through
  }

  return null;
}

// --- Staging middleware ---

function isStaging(url: URL): boolean {
  return url.hostname === STAGING_HOSTNAME;
}

/** Prevents CDN caching of HTML to avoid stale content after deployments. */
function withNoCacheForHtml(response: Response): Response {
  const contentType = response.headers.get("Content-Type") || "";
  if (!contentType.includes("text/html")) {
    return response;
  }

  const newHeaders = new Headers(response.headers);
  newHeaders.set("Cache-Control", "no-store, must-revalidate");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders,
  });
}

function handleStagingAuth(request: Request, url: URL): Response | null {
  if (!isStaging(url)) {
    return null;
  }

  // Check session cookie
  const cookies = request.headers.get("Cookie") || "";
  const hasSession = cookies
    .split(";")
    .some((c) => c.trim() === `${COOKIE_NAME}=${SESSION_TOKEN}`);
  if (hasSession) {
    return null;
  }

  // Check basic auth credentials
  const authHeader = request.headers.get("Authorization");
  if (!authHeader || !authHeader.startsWith("Basic ")) {
    return new Response("Unauthorized", {
      status: 401,
      headers: { "WWW-Authenticate": 'Basic realm="Staging"' },
    });
  }

  try {
    const credentials = atob(authHeader.slice(6));
    const [username, password] = credentials.split(":");
    if (username !== VALID_USERNAME || password !== VALID_PASSWORD) {
      return new Response("Unauthorized", {
        status: 401,
        headers: { "WWW-Authenticate": 'Basic realm="Staging"' },
      });
    }
  } catch {
    return new Response("Unauthorized", {
      status: 401,
      headers: { "WWW-Authenticate": 'Basic realm="Staging"' },
    });
  }

  // Valid credentials — set session cookie and redirect
  return new Response(null, {
    status: 302,
    headers: {
      Location: request.url,
      "Set-Cookie": `${COOKIE_NAME}=${SESSION_TOKEN}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400`,
    },
  });
}

/**
 * Try serving from static assets (ASSETS binding).
 *
 * With `run_worker_first: true` in staging, the worker intercepts ALL requests
 * including static assets (CSS, JS, images). We must explicitly try the ASSETS
 * binding before falling through to SSR.
 */
async function handleStaticAssets(
  request: Request,
  url: URL,
  environment: WorkerEnv,
): Promise<Response | null> {
  if (!isStaging(url)) {
    return null;
  }

  // Strip credentials from URL before fetching assets
  const cleanUrl = new URL(url);
  cleanUrl.username = "";
  cleanUrl.password = "";

  const assetRequest = new Request(cleanUrl.toString(), {
    method: request.method,
    headers: request.headers,
  });

  const assetResponse = await environment.ASSETS.fetch(assetRequest);

  // Return asset response for success (2xx) or redirects/cache (3xx)
  // Fall through to SSR for 4xx/5xx (asset not found = try SPA routing)
  if (assetResponse.status >= 200 && assetResponse.status < 400) {
    return assetResponse;
  }

  return null;
}

// --- Main handler ---

const ssrHandler = createStartHandler(defaultStreamHandler);

const fetch = async (
  request: Request,
  environment: WorkerEnv,
): Promise<Response> => {
  const url = new URL(request.url);
  const staging = isStaging(url);

  // 1. Staging auth (before anything)
  const authResponse = handleStagingAuth(request, url);
  if (authResponse) {
    return authResponse;
  }

  // 2. Core handlers (redirects, markdown)
  const redirectResponse = handleRedirect(request);
  if (redirectResponse) {
    return redirectResponse;
  }

  const acceptHeader = request.headers.get("Accept") ?? "";
  if (acceptHeader.includes("text/markdown")) {
    const markdownResponse = await handleMarkdownRequest(request, environment);
    if (markdownResponse) {
      return markdownResponse;
    }
  }

  // 3. Staging: try static assets before SSR (required with run_worker_first)
  const assetResponse = await handleStaticAssets(request, url, environment);
  if (assetResponse) {
    return staging ? withNoCacheForHtml(assetResponse) : assetResponse;
  }

  // 4. SSR fallback
  const ssrResponse = await ssrHandler(request);
  return staging ? withNoCacheForHtml(ssrResponse) : ssrResponse;
};

export default {
  fetch,
};
