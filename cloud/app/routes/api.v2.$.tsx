import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";
import { handleRequest } from "@/api/handler";
import { handleErrors, handleDefects } from "@/api/utils";
import { NotFoundError } from "@/errors";
import { authenticate, type PathParameters } from "@/auth";
import { Database } from "@/db";
import { DrizzleORM } from "@/db/client";
import { ClickHouse } from "@/db/clickhouse/client";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import { Analytics } from "@/analytics";
import { Emails } from "@/emails";
import { Settings, validateSettings } from "@/settings";
import {
  spansIngestQueueLayer,
  realtimeSpansLayer,
  rateLimiterLayer,
} from "@/server-entry";
import { SpansIngestQueue } from "@/workers/spanIngestQueue";
import { RateLimiter } from "@/rate-limiting";

/**
 * Extract path parameters from the splat path for API key validation.
 * Parses organizationId, projectId, and environmentId from the path.
 *
 * @param splat - The wildcard path captured by TanStack Router (e.g., "organizations/123/projects/456/environments/789")
 */
function extractPathParameters(
  splat: string | undefined,
): PathParameters | undefined {
  if (!splat) return undefined;

  const pathParts = splat.split("/").filter(Boolean);

  // API v2 routes follow pattern: organizations/:id/projects/:id/environments/:id/...
  const pathParams: PathParameters = {};
  let hasParams = false;

  for (let i = 0; i < pathParts.length; i++) {
    if (pathParts[i] === "organizations" && pathParts[i + 1]) {
      pathParams.organizationId = pathParts[i + 1];
      hasParams = true;
    } else if (pathParts[i] === "projects" && pathParts[i + 1]) {
      pathParams.projectId = pathParts[i + 1];
      hasParams = true;
    } else if (pathParts[i] === "environments" && pathParts[i + 1]) {
      pathParams.environmentId = pathParts[i + 1];
      hasParams = true;
    }
  }

  return hasParams ? pathParams : undefined;
}

export const Route = createFileRoute("/api/v2/$")({
  server: {
    handlers: {
      ANY: async ({
        request,
        params,
      }: {
        request: Request;
        params: { "*"?: string };
      }) => {
        const handler = Effect.gen(function* () {
          const settings = yield* Settings;

          const pathParams = extractPathParameters(params["*"]);
          const authResult = yield* authenticate(request, pathParams);

          // Check rate limit
          const rateLimiter = yield* RateLimiter;

          // Extract organization ID from API key info
          // Note: Rate limiting currently only applies to API key authenticated requests
          const rateLimitResult = authResult.apiKeyInfo
            ? yield* rateLimiter
                .checkRateLimit({
                  organizationId: authResult.apiKeyInfo.organizationId,
                })
                .pipe(
                  // Special handling for RateLimitError: we need to add custom headers
                  // (Retry-After, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
                  // that the default error handler doesn't support.
                  // ServiceUnavailableError and other errors propagate through the error
                  // channel and are handled by handleErrors with their static status codes.
                  Effect.catchTag("RateLimitError", (error) =>
                    Effect.succeed(
                      rateLimiter.createRateLimitErrorResponse({ error }),
                    ),
                  ),
                )
            : {
                // No rate limiting for session-based auth (web UI)
                allowed: true,
                limit: 0,
                resetAt: new Date(),
              };

          // If rate limit response was created, return it early
          if (rateLimitResult instanceof Response) {
            return rateLimitResult;
          }

          const drizzle = yield* DrizzleORM;
          const analytics = yield* Analytics;
          const emails = yield* Emails;
          const clickHouseSearch = yield* ClickHouseSearch;
          const realtimeSpans = yield* RealtimeSpans;
          const spansIngestQueue = yield* SpansIngestQueue;

          const result = yield* handleRequest(request, {
            prefix: "/api/v2",
            user: authResult.user,
            apiKeyInfo: authResult.apiKeyInfo,
            settings,
            drizzle,
            analytics,
            emails,
            clickHouseSearch,
            realtimeSpans,
            spansIngestQueue,
          });

          if (!result.matched) {
            return yield* new NotFoundError({ message: "Route not found" });
          }

          // Add rate limit headers to response
          return rateLimiter.addRateLimitHeaders({
            response: result.response,
            result: rateLimitResult,
          });
        }).pipe(
          Effect.provide(
            Layer.unwrapEffect(
              validateSettings().pipe(
                Effect.orDie, // Settings validation failure is fatal
                Effect.map((settings) =>
                  Layer.mergeAll(
                    Layer.succeed(Settings, settings),
                    Database.Live({
                      database: { connectionString: settings.databaseUrl },
                      payments: settings.stripe,
                    }),
                    Analytics.Live({
                      postHog: settings.posthog,
                      googleAnalytics: settings.googleAnalytics,
                    }),
                    Emails.Live(settings.resend),
                    ClickHouseSearch.Default.pipe(
                      Layer.provide(ClickHouse.Default),
                      Layer.provide(Layer.succeed(Settings, settings)),
                    ),
                    spansIngestQueueLayer,
                    realtimeSpansLayer,
                    rateLimiterLayer,
                  ),
                ),
              ),
            ),
          ),
          handleErrors,
          handleDefects,
        );

        return Effect.runPromise(handler);
      },
    },
  },
});
