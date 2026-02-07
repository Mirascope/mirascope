import { HttpApiBuilder, HttpServer } from "@effect/platform";
import { Context, Effect, Layer } from "effect";

import type { PublicUser, ApiKeyInfo } from "@/db/schema";

import { Analytics } from "@/analytics";
import { ApiLive } from "@/api/router";
import { AuthenticatedUser, Authentication } from "@/auth";
import { DeploymentService } from "@/claws/deployment/service";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { Emails } from "@/emails";
import { HandlerError } from "@/errors";
import { Payments } from "@/payments";
import { Settings, type SettingsConfig } from "@/settings";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import { SpansIngestQueue } from "@/workers/spanIngestQueue";

export type HandleRequestOptions = {
  prefix?: string;
  user: PublicUser;
  apiKeyInfo?: ApiKeyInfo;
  settings: SettingsConfig;
  drizzle: Context.Tag.Service<DrizzleORM>;
  analytics: Context.Tag.Service<Analytics>;
  emails: Context.Tag.Service<Emails>;
  clickHouseSearch: Context.Tag.Service<ClickHouseSearch>;
  realtimeSpans: Context.Tag.Service<RealtimeSpans>;
  spansIngestQueue: Context.Tag.Service<SpansIngestQueue>;
  deployment: Context.Tag.Service<DeploymentService>;
};

type WebHandlerOptions = {
  db: Context.Tag.Service<Database>;
  payments: Context.Tag.Service<Payments>;
  drizzle: Context.Tag.Service<DrizzleORM>;
  analytics: Context.Tag.Service<Analytics>;
  emails: Context.Tag.Service<Emails>;
  clickHouseSearch: Context.Tag.Service<ClickHouseSearch>;
  realtimeSpans: Context.Tag.Service<RealtimeSpans>;
  spansIngestQueue: Context.Tag.Service<SpansIngestQueue>;
  deployment: Context.Tag.Service<DeploymentService>;
  user: PublicUser;
  apiKeyInfo?: ApiKeyInfo;
  settings: SettingsConfig;
};

function createWebHandler(options: WebHandlerOptions) {
  const services = Layer.mergeAll(
    Layer.succeed(Settings, options.settings),
    Layer.succeed(AuthenticatedUser, options.user),
    Layer.succeed(Authentication, {
      user: options.user,
      apiKeyInfo: options.apiKeyInfo,
    }),
    Layer.succeed(DrizzleORM, options.drizzle),
    Layer.succeed(Database, options.db),
    Layer.succeed(Payments, options.payments),
    Layer.succeed(Analytics, options.analytics),
    Layer.succeed(Emails, options.emails),
    Layer.succeed(ClickHouseSearch, options.clickHouseSearch),
    Layer.succeed(SpansIngestQueue, options.spansIngestQueue),
    Layer.succeed(RealtimeSpans, options.realtimeSpans),
    Layer.succeed(DeploymentService, options.deployment),
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
      analytics: options.analytics,
      emails: options.emails,
      user: options.user,
      apiKeyInfo: options.apiKeyInfo,
      settings: options.settings,
      clickHouseSearch: options.clickHouseSearch,
      realtimeSpans: options.realtimeSpans,
      spansIngestQueue: options.spansIngestQueue,
      deployment: options.deployment,
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

        // Transform _tag to tag for Fern SDK compatibility
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
