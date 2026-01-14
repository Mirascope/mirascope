import { HttpApiBuilder, HttpServer } from "@effect/platform";
import { Context, Effect, Layer } from "effect";
import { ApiLive } from "@/api/router";
import { HandlerError } from "@/errors";
import { SettingsService, getSettings } from "@/settings";
import { Database } from "@/db";
import { DrizzleORM } from "@/db/client";
import { Payments } from "@/payments";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import { AuthenticatedUser, Authentication } from "@/auth";
import { SpansIngestQueue } from "@/workers/spanIngestQueue";
import type { PublicUser, ApiKeyInfo } from "@/db/schema";

export type HandleRequestOptions = {
  prefix?: string;
  user: PublicUser;
  apiKeyInfo?: ApiKeyInfo;
  environment: string;
  drizzle: Context.Tag.Service<DrizzleORM>;
  clickHouseSearch: Context.Tag.Service<ClickHouseSearch>;
  realtimeSpans: Context.Tag.Service<RealtimeSpans>;
  spansIngestQueue: Context.Tag.Service<SpansIngestQueue>;
};

type WebHandlerOptions = {
  db: Context.Tag.Service<Database>;
  payments: Context.Tag.Service<Payments>;
  drizzle: Context.Tag.Service<DrizzleORM>;
  clickHouseSearch: Context.Tag.Service<ClickHouseSearch>;
  realtimeSpans: Context.Tag.Service<RealtimeSpans>;
  spansIngestQueue: Context.Tag.Service<SpansIngestQueue>;
  user: PublicUser;
  apiKeyInfo?: ApiKeyInfo;
  environment: string;
};

function createWebHandler(options: WebHandlerOptions) {
  const baseServices = Layer.mergeAll(
    Layer.succeed(SettingsService, {
      ...getSettings(),
      env: options.environment,
    }),
    Layer.succeed(AuthenticatedUser, options.user),
    Layer.succeed(Authentication, {
      user: options.user,
      apiKeyInfo: options.apiKeyInfo,
    }),
    Layer.succeed(DrizzleORM, options.drizzle),
    Layer.succeed(Database, options.db),
    Layer.succeed(Payments, options.payments),
    Layer.succeed(ClickHouseSearch, options.clickHouseSearch),
    Layer.succeed(SpansIngestQueue, options.spansIngestQueue),
  );

  const services = Layer.merge(
    baseServices,
    Layer.succeed(RealtimeSpans, options.realtimeSpans),
  );

  const ApiWithDependencies = Layer.merge(
    HttpServer.layerContext,
    ApiLive,
  ).pipe(Layer.provide(services));

  return HttpApiBuilder.toWebHandler(ApiWithDependencies);
}

/**
 * Handle an API request using the Effect HTTP API.
 *
 * This is an Effect that depends on `Database` and `Payments` to share the
 * services with authentication and API handlers.
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
  Database | Payments | DrizzleORM
> =>
  Effect.gen(function* () {
    const db = yield* Database;
    const payments = yield* Payments;
    const drizzle = yield* DrizzleORM;

    const webHandler = createWebHandler({
      db,
      payments,
      drizzle,
      user: options.user,
      apiKeyInfo: options.apiKeyInfo,
      environment: options.environment,
      clickHouseSearch: options.clickHouseSearch,
      realtimeSpans: options.realtimeSpans,
      spansIngestQueue: options.spansIngestQueue,
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
          /* v8 ignore start */
          if (body.includes('"_tag"')) {
            /* v8 ignore end - for some reason this is the only way that works to ignore the else branch */
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
            /* v8 ignore next 3 */
            error instanceof Error ? error.message : String(error)
          }`,
          cause: error,
        }),
    });

    yield* Effect.tryPromise({
      try: () => webHandler.dispose(),
      /* v8 ignore start - dispose failures are swallowed, so this error path is not easily testable */
      catch: (error) =>
        new HandlerError({
          message: "Failed to dispose web handler",
          cause: error,
        }),
    }).pipe(Effect.catchAll(() => Effect.void));
    /* v8 ignore end */

    return result;
  });
