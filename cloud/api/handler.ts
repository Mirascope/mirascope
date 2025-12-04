import { HttpApiBuilder, HttpServer } from "@effect/platform";
import { Layer } from "effect";
import type { Context } from "effect/Context";
import { ApiLive } from "./router";
import { EnvironmentService } from "./environment";

// ============================================================================
// Types
// ============================================================================

/**
 * Web handler instance returned by HttpApiBuilder.toWebHandler
 */
interface WebHandlerInstance {
  handler: (
    request: Request<unknown, CfProperties<unknown>>,
    context?: Context<never> | undefined,
  ) => Promise<Response>;
  dispose: () => Promise<void>;
}

// ============================================================================
// Create Web Handler
// ============================================================================

/**
 * Creates a web handler for the Effect API.
 * This handler can be used with any fetch-compatible runtime (Cloudflare Workers, etc.)
 */
export function createWebHandler(
  options: { environment?: string } = {},
): WebHandlerInstance {
  // Create environment layer
  const EnvironmentLive = Layer.succeed(EnvironmentService, {
    environment: options.environment || "unknown",
  });

  const ApiWithEnv = Layer.mergeAll(
    HttpServer.layerContext,
    ApiLive.pipe(Layer.provide(EnvironmentLive)),
  );

  // Create the web handler directly from the API layer with services
  const webHandler: WebHandlerInstance =
    HttpApiBuilder.toWebHandler(ApiWithEnv);
  return webHandler;
}

// ============================================================================
// Cached handler for reuse
// ============================================================================

let cachedHandler: WebHandlerInstance | null = null;
let cachedEnvironment: string | undefined = undefined;

/**
 * Get or create the default handler instance
 */
export function getWebHandler(
  options: { environment?: string } = {},
): WebHandlerInstance {
  // Recreate handler if environment changes
  if (!cachedHandler || cachedEnvironment !== options.environment) {
    // Dispose old handler if exists
    if (cachedHandler) {
      cachedHandler.dispose().catch(console.error);
    }
    cachedHandler = createWebHandler(options);
    cachedEnvironment = options.environment;
  }
  return cachedHandler;
}

/**
 * Handle a request with URL prefix stripping support
 */
export async function handleRequest(
  request: Request,
  options: { environment?: string; prefix?: string } = {},
): Promise<{ matched: boolean; response: Response }> {
  const webHandler = getWebHandler(options);

  // If a prefix is specified, we need to rewrite the URL to strip it
  let modifiedRequest = request;
  if (options.prefix) {
    const url = new URL(request.url);
    if (url.pathname.startsWith(options.prefix)) {
      const pathWithoutPrefix =
        url.pathname.slice(options.prefix.length) || "/";
      const newUrl = new URL(pathWithoutPrefix + url.search, url.origin);
      modifiedRequest = new Request(newUrl.toString(), {
        method: request.method,
        headers: request.headers,
        body: request.body,
        redirect: request.redirect,
        signal: request.signal,
      });
    }
  }

  try {
    const response = await webHandler.handler(modifiedRequest);
    // Effect Platform returns 404 for unmatched routes
    const matched = response.status !== 404;
    return { matched, response };
  } catch (error) {
    console.error("[Effect API] Error handling request:", error);
    return {
      matched: false,
      response: new Response("Internal Server Error", { status: 500 }),
    };
  }
}
