import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";

import { Analytics } from "@/analytics";
import { handleRequest } from "@/api/handler";
import { handleErrors, handleDefects } from "@/api/utils";
import { authenticate, type PathParameters } from "@/auth";
import { MacDeploymentLayer } from "@/claws/deployment/mac-deployment";
import {
  MacFleetService,
  LiveMacFleetService,
} from "@/claws/deployment/mac-fleet";
import { MockDeploymentService } from "@/claws/deployment/mock";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { CloudflareHttp } from "@/cloudflare/client";
import { CloudflareSettings } from "@/cloudflare/config";
import { LiveCloudflareR2Service } from "@/cloudflare/r2/live";
import { ClickHouse } from "@/db/clickhouse/client";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { Emails } from "@/emails";
import { NotFoundError } from "@/errors";
import { RateLimiter } from "@/rate-limiting";
import {
  spansIngestQueueLayer,
  realtimeSpansLayer,
  rateLimiterLayer,
  settingsLayer,
} from "@/server-entry";
import { Settings } from "@/settings";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import { SpansIngestQueue } from "@/workers/spanIngestQueue";

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
          const deployment = yield* ClawDeploymentService;

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
            clawDeployment: deployment,
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
              Effect.gen(function* () {
                const settings = yield* Settings;

                const databaseLayer = settings.mockDeployment
                  ? Database.Dev({
                      database: { connectionString: settings.databaseUrl },
                      plan: settings.mockDeployment,
                    })
                  : Database.Live({
                      database: { connectionString: settings.databaseUrl },
                      payments: settings.stripe,
                    });

                const macMiniDeploymentLayer = MacDeploymentLayer.pipe(
                  Layer.provide(
                    Layer.effect(MacFleetService, LiveMacFleetService),
                  ),
                  Layer.provide(LiveCloudflareR2Service),
                  Layer.provide(
                    CloudflareHttp.Live(settings.cloudflare.apiToken),
                  ),
                  Layer.provide(CloudflareSettings.layer(settings.cloudflare)),
                  Layer.provide(databaseLayer),
                );

                const deploymentLayer =
                  settings.mockDeployment && settings.deploymentTarget !== "mac"
                    ? MockDeploymentService
                    : macMiniDeploymentLayer;

                return Layer.mergeAll(
                  Layer.succeed(Settings, settings),
                  databaseLayer,
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
                  deploymentLayer,
                );
              }).pipe(Effect.provide(settingsLayer)),
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
