import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { authenticate } from "@/auth";
import { Database } from "@/db";
import { handleErrors, handleDefects } from "@/api/utils";
import { proxyToProvider } from "@/api/router/proxy";
import {
  PROVIDER_CONFIGS,
  isValidProvider,
  getProviderApiKey,
  getCostCalculator,
  extractModelId,
} from "@/api/router/providers";
import { InternalError } from "@/errors";
import { formatCostForDisplay } from "@/api/router/cost-utils";

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
        const databaseUrl = process.env.DATABASE_URL;
        const provider = params.provider.toLowerCase();

        const handler = Effect.gen(function* () {
          if (!databaseUrl) {
            return yield* new InternalError({
              message: "Database not configured",
            });
          }

          // Validate provider
          if (!isValidProvider(provider)) {
            return yield* new InternalError({
              message: `Unsupported provider: ${provider}`,
            });
          }

          // Authenticate user via Mirascope API key
          yield* authenticate(request);

          // Get provider-specific API key from environment
          const providerApiKey = getProviderApiKey(provider);

          if (!providerApiKey) {
            return yield* new InternalError({
              message: `${provider} API key not configured`,
            });
          }

          // Extract model ID using provider-specific logic
          const requestBody = yield* Effect.tryPromise({
            try: () => request.clone().text(),
            catch: () => null as string | null,
          });

          let parsedBody: unknown = null;
          if (requestBody) {
            try {
              parsedBody = JSON.parse(requestBody);
            } catch {
              // Not JSON, that's ok
            }
          }

          const modelId = extractModelId(provider, request, parsedBody);

          // Proxy to provider with internal API key
          const proxyResult = yield* proxyToProvider(
            request,
            {
              ...PROVIDER_CONFIGS[provider],
              apiKey: providerApiKey,
            },
            provider,
          );

          // Calculate usage and cost
          if (proxyResult.body && modelId) {
            const calculator = getCostCalculator(provider);
            if (calculator) {
              const result = yield* calculator
                .calculate(modelId, proxyResult.body)
                .pipe(Effect.catchAll(() => Effect.succeed(null)));

              if (result) {
                console.log({
                  provider,
                  model: modelId,
                  usage: {
                    inputTokens: result.usage.inputTokens,
                    outputTokens: result.usage.outputTokens,
                    cacheReadTokens: result.usage.cacheReadTokens || 0,
                    cacheWriteTokens: result.usage.cacheWriteTokens || 0,
                    totalTokens:
                      result.usage.inputTokens + result.usage.outputTokens,
                  },
                  cost: {
                    input: formatCostForDisplay(result.cost.inputCost),
                    output: formatCostForDisplay(result.cost.outputCost),
                    cacheRead: result.cost.cacheReadCost
                      ? formatCostForDisplay(result.cost.cacheReadCost)
                      : undefined,
                    cacheWrite: result.cost.cacheWriteCost
                      ? formatCostForDisplay(result.cost.cacheWriteCost)
                      : undefined,
                    total: formatCostForDisplay(result.cost.totalCost),
                  },
                });
              }
            }
          }

          return proxyResult.response;
        }).pipe(
          Effect.provide(
            Database.Live({
              database: { connectionString: databaseUrl },
              payments: {
                apiKey: process.env.STRIPE_SECRET_KEY || "",
                routerPriceId: process.env.STRIPE_ROUTER_PRICE_ID || "",
                routerMeterId: process.env.STRIPE_ROUTER_METER_ID || "",
              },
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
