import { HttpApiBuilder, HttpServer } from "@effect/platform";
import { Layer } from "effect";
import { ApiLive } from "@/api/router";
import { EnvironmentService } from "@/environment";
import { DatabaseService, getDatabase } from "@/db";
import { AuthenticatedUser } from "@/auth/context";
import type { PublicUser } from "@/db/schema";

export type HandleRequestOptions = {
  environment?: string;
  prefix?: string;
  authenticatedUser: PublicUser;
  databaseUrl?: string;
};

/**
 * Create an authenticated web handler for a specific user.
 * Each request gets its own handler since the user context is different.
 */
function createAuthenticatedWebHandler(options: HandleRequestOptions) {
  const databaseUrl = options.databaseUrl || process.env.DATABASE_URL;
  if (!databaseUrl) {
    throw new Error("DATABASE_URL is required");
  }

  // Create all dependency layers
  const DependenciesLive = Layer.mergeAll(
    Layer.succeed(EnvironmentService, {
      env: options.environment || "unknown",
    }),
    Layer.succeed(DatabaseService, getDatabase(databaseUrl)),
    Layer.succeed(AuthenticatedUser, options.authenticatedUser),
  );

  const ApiWithDependencies = Layer.mergeAll(
    HttpServer.layerContext,
    ApiLive.pipe(Layer.provide(DependenciesLive)),
  );

  return HttpApiBuilder.toWebHandler(ApiWithDependencies);
}

export async function handleRequest(
  request: Request,
  options: HandleRequestOptions,
): Promise<{ matched: boolean; response: Response }> {
  const webHandler = createAuthenticatedWebHandler(options);

  try {
    // Strip prefix if present
    let modifiedRequest = request;
    const url = new URL(request.url);
    if (options.prefix && url.pathname.startsWith(options.prefix)) {
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

    const response = await webHandler.handler(modifiedRequest);

    // Dispose handler after use
    webHandler.dispose().catch(console.error);

    // Effect Platform returns 404 for unmatched routes
    const matched = response.status !== 404;
    return { matched, response };
  } catch (error) {
    console.error("[Effect API] Error handling request:", error);

    // Dispose handler on error as well
    webHandler.dispose().catch(console.error);

    return {
      matched: false,
      response: new Response("Internal Server Error", { status: 500 }),
    };
  }
}
