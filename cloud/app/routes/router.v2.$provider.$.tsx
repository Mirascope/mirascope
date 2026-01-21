import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";
import { Database } from "@/db";
import { handleErrors, handleDefects } from "@/api/utils";
import { PROVIDER_CONFIGS, getProviderApiKey } from "@/api/router/providers";
import { proxyToProvider } from "@/api/router/proxy";
import {
  validateRouterRequest,
  createPendingRouterRequest,
  reserveRouterFunds,
  handleRouterRequestFailure,
} from "@/api/router/utils";
import { handleStreamingResponse } from "@/api/router/streaming";
import { handleNonStreamingResponse } from "@/api/router/non-streaming";
import {
  routerMeteringQueueLayer,
  rateLimiterLayer,
  settingsLayer,
} from "@/server-entry";
import { RateLimiter } from "@/rate-limiting";
import { Settings } from "@/settings";

/**
 * Unified Provider Proxy Route
 *
 * Catches all requests to `/router/v2/{provider}/*` and proxies them to the respective
 * AI provider's API. Authenticates users via Mirascope API key, uses internal provider
 * API keys, extracts usage data, and calculates costs.
 *
 * Supported providers: openai, anthropic, google
 *
 * Base URL examples:
 * - OpenAI: `base_url="https://mirascope.com/router/v2/openai/v1"`
 * - Anthropic: `base_url="https://mirascope.com/router/v2/anthropic"`
 * - Google: `base_url="https://mirascope.com/router/v2/google/v1beta"`
 *
 * Request examples:
 * - `/router/v2/openai/v1/chat/completions` → `https://api.openai.com/v1/chat/completions`
 * - `/router/v2/anthropic/v1/messages` → `https://api.anthropic.com/v1/messages`
 * - `/router/v2/google/v1beta/models/{model}:generateContent` → Google API
 */
export const Route = createFileRoute("/router/v2/$provider/$")({
  server: {
    handlers: {
      ANY: async ({
        request,
        params,
      }: {
        request: Request;
        params: { provider: string; "*"?: string };
      }) => {
        const provider = params.provider.toLowerCase();

        const handler = Effect.gen(function* () {
          // Get validated settings
          const settings = yield* Settings;

          // Step 1: Validate request and authenticate user
          const validated = yield* validateRouterRequest(request, provider);

          // Step 2: Check rate limit
          const rateLimiter = yield* RateLimiter;
          const rateLimitResult = yield* rateLimiter
            .checkRateLimit({
              organizationId: validated.apiKeyInfo.organizationId,
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
            );

          // If rate limit response was created, return it early
          if (rateLimitResult instanceof Response) {
            return rateLimitResult;
          }

          // Get database service
          const db = yield* Database;

          // Get the organization for this API key
          const organization = yield* db.organizations.findById({
            organizationId: validated.apiKeyInfo.organizationId,
            userId: validated.user.id,
          });

          // Get provider-specific API key from settings
          const providerApiKey = getProviderApiKey(
            validated.provider,
            settings,
          );

          // Step 3: Create pending router request
          const routerRequestId = yield* createPendingRouterRequest(validated);

          // Step 4: Reserve funds
          const reservationId = yield* reserveRouterFunds(
            validated,
            routerRequestId,
            organization.stripeCustomerId,
          );

          // Build request context for handlers
          const requestContext = {
            routerRequestId,
            reservationId,
            request: {
              userId: validated.user.id,
              organizationId: validated.apiKeyInfo.organizationId,
              projectId: validated.apiKeyInfo.projectId,
              environmentId: validated.apiKeyInfo.environmentId,
              apiKeyId: validated.apiKeyInfo.apiKeyId,
              routerRequestId,
            },
          };

          // Step 5: Proxy request to provider with error handling
          const proxyResult = yield* proxyToProvider(
            request,
            {
              ...PROVIDER_CONFIGS[validated.provider],
              apiKey: providerApiKey,
            },
            validated.provider,
          ).pipe(
            Effect.catchAll((error) => {
              // Handle proxy errors by updating request and releasing funds
              return Effect.gen(function* () {
                yield* handleRouterRequestFailure(
                  routerRequestId,
                  reservationId,
                  requestContext.request,
                  error instanceof Error ? error.message : String(error),
                );
                return yield* Effect.fail(error);
              });
            }),
          );

          // Step 6: Handle response (streaming or non-streaming)
          if (proxyResult.isStreaming) {
            const response = yield* handleStreamingResponse(
              proxyResult,
              requestContext,
              validated,
              {
                status: proxyResult.response.status,
                statusText: proxyResult.response.statusText,
                headers: proxyResult.response.headers,
              },
            );
            return rateLimiter.addRateLimitHeaders({
              response,
              result: rateLimitResult,
            });
          }

          const response = yield* handleNonStreamingResponse(
            proxyResult,
            requestContext,
            validated,
          );
          return rateLimiter.addRateLimitHeaders({
            response,
            result: rateLimitResult,
          });
        }).pipe(
          Effect.provide(
            Layer.unwrapEffect(
              Effect.gen(function* () {
                const settings = yield* Settings;
                return Layer.mergeAll(
                  Layer.succeed(Settings, settings),
                  Database.Live({
                    database: { connectionString: settings.databaseUrl },
                    payments: settings.stripe,
                  }),
                  routerMeteringQueueLayer,
                  rateLimiterLayer,
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
