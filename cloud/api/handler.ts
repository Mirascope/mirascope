import { HttpApiBuilder, HttpServer } from "@effect/platform";
import { Layer } from "effect";
import { ApiLive } from "@/api/router";
import { EnvironmentService } from "@/api/environment";
// import { DatabaseLive } from "@/db";

export function createWebHandler(
  options: {
    environment?: string;
    databaseUrl?: string;
  } = {},
) {
  // Create environment layer
  const EnvironmentLive = Layer.succeed(EnvironmentService, {
    env: options.environment || "unknown",
  });

  // Create database layer
  // const connectionString =
  //   options.databaseUrl || process.env.DATABASE_URL || "";
  // const DatabaseLiveLayer = DatabaseLive(connectionString);

  const ApiWithDependencies = Layer.mergeAll(
    HttpServer.layerContext,
    ApiLive.pipe(
      Layer.provide(EnvironmentLive),
      // TODO: Add database as a dependency
      // Layer.provide(DatabaseLiveLayer),
    ),
  );

  return HttpApiBuilder.toWebHandler(ApiWithDependencies);
}

let cachedHandler: ReturnType<typeof createWebHandler> | null = null;
let cachedEnvironment: string | undefined = undefined;

export function getWebHandler(
  options: { environment?: string } = {},
): ReturnType<typeof createWebHandler> {
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

export async function handleRequest(
  request: Request,
  options: { environment?: string; prefix?: string },
): Promise<{ matched: boolean; response: Response }> {
  const webHandler = getWebHandler(options);

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
