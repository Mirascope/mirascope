import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { Database } from "@/db";
import { handleErrors, handleDefects } from "@/api/utils";
import { InternalError } from "@/errors";
import { getRouterConfig, validateRouterConfig } from "@/api/router/config";
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

/**
 * Unified Provider Proxy Route
 *
 * Catches all requests to `/router/v0/{provider}/*` and proxies them to the respective
 * AI provider's API. Authenticates users via Mirascope API key, uses internal provider
 * API keys, extracts usage data, and calculates costs.
 *
 * Supported providers: openai, anthropic, google
 *
 * Base URL examples:
 * - OpenAI: `base_url="https://mirascope.com/router/v0/openai/v1"`
 * - Anthropic: `base_url="https://mirascope.com/router/v0/anthropic"`
 * - Google: `base_url="https://mirascope.com/router/v0/google/v1beta"`
 *
 * Request examples:
 * - `/router/v0/openai/v1/chat/completions` → `https://api.openai.com/v1/chat/completions`
 * - `/router/v0/anthropic/v1/messages` → `https://api.anthropic.com/v1/messages`
 * - `/router/v0/google/v1beta/models/{model}:generateContent` → Google API
 */
export const Route = createFileRoute("/router/v0/$provider/$")({
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

        // Validate configuration early
        const configError = validateRouterConfig();
        if (configError) {
          return Effect.runPromise(
            Effect.fail(new InternalError({ message: configError })).pipe(
              handleErrors,
              handleDefects,
            ),
          );
        }

        const config = getRouterConfig();

        const handler = Effect.gen(function* () {
          // Step 1: Validate request and authenticate user
          const validated = yield* validateRouterRequest(request, provider);

          // Get database service
          const db = yield* Database;

          // Get the organization for this API key
          const organization = yield* db.organizations.findById({
            organizationId: validated.apiKeyInfo.organizationId,
            userId: validated.user.id,
          });

          // Get provider-specific API key from environment
          const providerApiKey = getProviderApiKey(validated.provider);
          if (!providerApiKey) {
            return yield* new InternalError({
              message: `${validated.provider} API key not configured`,
            });
          }

          // Step 2: Create pending router request
          const routerRequestId = yield* createPendingRouterRequest(validated);

          // Step 3: Reserve funds
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

          // Step 4: Proxy request to provider with error handling
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

          // Step 5: Handle response (streaming or non-streaming)
          if (proxyResult.isStreaming) {
            return yield* handleStreamingResponse(
              proxyResult,
              requestContext,
              validated,
              {
                status: proxyResult.response.status,
                statusText: proxyResult.response.statusText,
                headers: proxyResult.response.headers,
              },
              config.databaseUrl,
              config.stripe,
            );
          }

          return yield* handleNonStreamingResponse(
            proxyResult,
            requestContext,
            validated,
          );
        }).pipe(
          Effect.provide(
            Database.Live({
              database: { connectionString: config.databaseUrl },
              payments: config.stripe,
            }),
          ),
          handleErrors,
          handleDefects,
        );

        return Effect.runPromise(handler);
      },
    },
  },
});
