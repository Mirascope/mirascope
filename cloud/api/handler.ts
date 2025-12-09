import { HttpApiBuilder, HttpServer } from "@effect/platform";
import { Context, Effect, Layer } from "effect";
import { ApiLive } from "@/api/router";
import { HandlerError } from "@/errors";
import { SettingsService } from "@/settings";
import { Database } from "@/db";
import { AuthenticatedUser, AuthenticatedApiKey } from "@/auth";
import type { PublicUser, ApiKeyInfo } from "@/db/schema";

export type HandleRequestOptions = {
  prefix?: string;
  authenticatedUser: PublicUser;
  authenticatedApiKey?: ApiKeyInfo | null;
  environment: string;
};

type WebHandlerOptions = {
  db: Context.Tag.Service<Database>;
  authenticatedUser: PublicUser;
  authenticatedApiKey?: ApiKeyInfo | null;
  environment: string;
};

function createWebHandler(options: WebHandlerOptions) {
  const baseServices = Layer.mergeAll(
    Layer.succeed(SettingsService, { env: options.environment }),
    Layer.succeed(AuthenticatedUser, options.authenticatedUser),
    Layer.succeed(Database, options.db),
  );

  const apiKeyLayer = options.authenticatedApiKey
    ? Layer.succeed(AuthenticatedApiKey, options.authenticatedApiKey)
    : Layer.empty;
  const services = Layer.merge(baseServices, apiKeyLayer);

  const ApiWithDependencies = Layer.merge(
    HttpServer.layerContext,
    ApiLive,
  ).pipe(Layer.provide(services));

  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-argument
  return HttpApiBuilder.toWebHandler(ApiWithDependencies as any);
}

/**
 * Handle an API request using the Effect HTTP API.
 *
 * This is an Effect that depends on `Database` to share the database
 * connection with authentication and API handlers.
 *
 * @param request - The incoming HTTP request
 * @param options - Configuration including prefix, authenticated user, and environment
 * @returns An Effect that resolves to the matched status and response
 */
export const handleRequest = (
  request: Request,
  options: HandleRequestOptions,
): Effect.Effect<
  { matched: boolean; response: Response },
  HandlerError,
  Database
> =>
  Effect.gen(function* () {
    const db = yield* Database;

    const webHandler = createWebHandler({
      db,
      authenticatedUser: options.authenticatedUser,
      authenticatedApiKey: options.authenticatedApiKey,
      environment: options.environment,
    });

    const result = yield* Effect.tryPromise({
      try: async () => {
        let modifiedRequest = request;
        const url = new URL(request.url);
        if (options.prefix && url.pathname.startsWith(options.prefix)) {
          const pathWithoutPrefix =
            url.pathname.slice(options.prefix.length) || "/";
          const newUrl = new URL(pathWithoutPrefix + url.search, url.origin);
          const hasBody = request.body !== null;
          modifiedRequest = new Request(newUrl.toString(), {
            method: request.method,
            headers: request.headers,
            body: request.body,
            redirect: request.redirect,
            signal: request.signal,
            ...(hasBody ? ({ duplex: "half" } as RequestInit) : {}),
          });
        }

        let response = await webHandler.handler(modifiedRequest);
        const contentType = response.headers.get("content-type") || "";
        const isJsonResponse = contentType
          .toLowerCase()
          .includes("application/json");

        if (isJsonResponse && response.status >= 400) {
          const body = await response.clone().text();
          if (body.includes('"_tag"')) {
            const transformedBody = body.replace(/"_tag":/g, '"tag":');
            response = new Response(transformedBody, {
              status: response.status,
              statusText: response.statusText,
              headers: response.headers,
            });
          }
        }

        const matched = response.status !== 404 || isJsonResponse;
        return { matched, response };
      },
      catch: (error) =>
        new HandlerError({
          message: `[Effect API] Error handling request: ${
            error instanceof Error
              ? /* v8 ignore next 2 */
                error.message
              : String(error)
          }`,
          cause: error,
        }),
    });

    yield* Effect.tryPromise({
      try: () => webHandler.dispose(),
      catch: (error) =>
        /* v8 ignore next 4 - dispose failures are swallowed, so this error path is not easily testable */
        new HandlerError({
          message: "Failed to dispose web handler",
          cause: error,
        }),
    }).pipe(Effect.catchAll(() => Effect.void));

    return result;
  });
