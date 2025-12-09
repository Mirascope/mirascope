import { HttpApiBuilder, HttpServer } from "@effect/platform";
import { Layer } from "effect";
import { ApiLive } from "@/api/router";
import { EnvironmentService } from "@/environment";
import { DatabaseService, type Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
import type { PublicUser } from "@/db/schema";

export type App = {
  environment: string;
  database: Database;
  authenticatedUser: PublicUser;
};

export type HandleRequestOptions = {
  app: App;
  prefix?: string;
};

function createWebHandler(options: HandleRequestOptions) {
  const app = options.app;
  const services = Layer.mergeAll(
    Layer.succeed(EnvironmentService, { env: app.environment }),
    Layer.succeed(DatabaseService, app.database),
    Layer.succeed(AuthenticatedUser, app.authenticatedUser),
  );
  const ApiWithDependencies = Layer.mergeAll(
    HttpServer.layerContext,
    ApiLive.pipe(Layer.provide(services)),
  );

  return HttpApiBuilder.toWebHandler(ApiWithDependencies);
}

export async function handleRequest(
  request: Request,
  options: HandleRequestOptions,
): Promise<{ matched: boolean; response: Response }> {
  const webHandler = createWebHandler(options);

  try {
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

    const matched = response.status !== 404;
    return { matched, response };
  } catch (error) {
    console.error("[Effect API] Error handling request:", error);

    return {
      matched: false,
      response: new Response("Internal Server Error", { status: 500 }),
    };
  } finally {
    /* v8 ignore next */
    webHandler.dispose().catch(console.error);
  }
}
