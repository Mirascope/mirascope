import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";
import { handleRequest } from "@/api/handler";
import { handleErrors, handleDefects } from "@/api/utils";
import { NotFoundError, InternalError } from "@/errors";
import { authenticate, type PathParameters } from "@/auth";
import { Database } from "@/db";
import { Analytics } from "@/analytics";
import { Emails } from "@/emails";
import { ClickHouse } from "@/clickhouse/client";
import { ClickHouseSearch } from "@/clickhouse/search";
import { SettingsService, getSettings } from "@/settings";
import { spansMeteringQueueLayer, rateLimiterLayer } from "@/server-entry";
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

  // API v0 routes follow pattern: organizations/:id/projects/:id/environments/:id/...
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

export const Route = createFileRoute("/api/v0/$")({
  server: {
    handlers: {
      ANY: async ({
        request,
        params,
      }: {
        request: Request;
        params: { "*"?: string };
      }) => {
        const databaseUrl = process.env.DATABASE_URL;

        const handler = Effect.gen(function* () {
          if (!databaseUrl) {
            return yield* new InternalError({
              message: "Database not configured",
            });
          }

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

          const clickHouseSearch = yield* ClickHouseSearch;

          const result = yield* handleRequest(request, {
            prefix: "/api/v0",
            user: authResult.user,
            apiKeyInfo: authResult.apiKeyInfo,
            environment: process.env.ENVIRONMENT || "development",
            clickHouseSearch,
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
            Layer.mergeAll(
              Database.Live({
                database: { connectionString: databaseUrl },
                payments: {
                  apiKey: process.env.STRIPE_SECRET_KEY,
                  routerPriceId: process.env.STRIPE_ROUTER_PRICE_ID,
                  routerMeterId: process.env.STRIPE_ROUTER_METER_ID,
                  cloudFreePriceId: process.env.STRIPE_CLOUD_FREE_PRICE_ID,
                  cloudProPriceId: process.env.STRIPE_CLOUD_PRO_PRICE_ID,
                  cloudTeamPriceId: process.env.STRIPE_CLOUD_TEAM_PRICE_ID,
                  cloudSpansPriceId: process.env.STRIPE_CLOUD_SPANS_PRICE_ID,
                  cloudSpansMeterId: process.env.STRIPE_CLOUD_SPANS_METER_ID,
                },
              }),
              Analytics.Live({
                googleAnalytics: {
                  measurementId: process.env.GOOGLE_ANALYTICS_MEASUREMENT_ID,
                  apiSecret: process.env.GOOGLE_ANALYTICS_API_SECRET,
                },
                postHog: {
                  apiKey: process.env.POSTHOG_API_KEY,
                  host: process.env.POSTHOG_HOST,
                },
              }),
              Emails.Live({
                apiKey: process.env.RESEND_API_KEY,
                audienceSegmentId: process.env.RESEND_AUDIENCE_SEGMENT_ID,
              }),
              ClickHouseSearch.Default.pipe(
                Layer.provide(ClickHouse.Default),
                Layer.provide(
                  Layer.succeed(SettingsService, {
                    ...getSettings(),
                    env: process.env.ENVIRONMENT || "development",
                  }),
                ),
              ),
              spansMeteringQueueLayer,
              rateLimiterLayer,
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
