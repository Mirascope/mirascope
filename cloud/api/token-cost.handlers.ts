import { Effect } from "effect";

import type { TokenUsage } from "@/api/router/pricing";
import type {
  TokenCostRequest,
  TokenCostResponse,
} from "@/api/token-cost.schemas";

import { centicentsToDollars } from "@/api/router/cost-utils";
import {
  getCostCalculator,
  isValidProvider,
  getSupportedProviders,
} from "@/api/router/providers";
import { PricingUnavailableError } from "@/errors";

export * from "@/api/token-cost.schemas";

/**
 * Calculates cost for a provider/model/usage combination.
 *
 * Uses the existing cost calculation infrastructure from the router.
 *
 * @param request - The cost calculation request containing provider, model, and usage
 * @returns Cost breakdown in both centi-cents (precision) and dollars (display)
 */
export const tokenCostHandler = (
  request: TokenCostRequest,
): Effect.Effect<TokenCostResponse, PricingUnavailableError> =>
  Effect.gen(function* () {
    // Validate provider is supported
    if (!isValidProvider(request.provider)) {
      const supported = getSupportedProviders().join(", ");
      return yield* Effect.fail(
        new PricingUnavailableError({
          message: `Provider '${request.provider}' is not supported. Supported providers: ${supported}. Request support for additional providers at https://github.com/Mirascope/mirascope/issues`,
          provider: request.provider,
        }),
      );
    }

    const calculator = getCostCalculator(request.provider);

    const usage: TokenUsage = {
      inputTokens: request.usage.inputTokens,
      outputTokens: request.usage.outputTokens,
      cacheReadTokens: request.usage.cacheReadTokens,
      cacheWriteTokens: request.usage.cacheWriteTokens,
      cacheWriteBreakdown: request.usage.cacheWriteBreakdown,
    };

    const costBreakdown = yield* calculator.calculate(request.model, usage);

    if (!costBreakdown) {
      return yield* Effect.fail(
        new PricingUnavailableError({
          message: `Pricing unavailable for ${request.provider}/${request.model}`,
          provider: request.provider,
          model: request.model,
        }),
      );
    }

    // Apply 5% router fee if request is via Mirascope Router
    const routerMultiplier = request.viaRouter ? 1.05 : 1.0;
    const applyRouterFee = (cost: bigint): bigint =>
      BigInt(Math.ceil(Number(cost) * routerMultiplier));

    const inputCost = applyRouterFee(costBreakdown.inputCost);
    const outputCost = applyRouterFee(costBreakdown.outputCost);
    const cacheReadCost = costBreakdown.cacheReadCost
      ? applyRouterFee(costBreakdown.cacheReadCost)
      : undefined;
    const cacheWriteCost = costBreakdown.cacheWriteCost
      ? applyRouterFee(costBreakdown.cacheWriteCost)
      : undefined;
    const totalCost = applyRouterFee(costBreakdown.totalCost);

    return {
      // Centi-cents values (convert bigint to number for JSON serialization)
      inputCostCenticents: Number(inputCost),
      outputCostCenticents: Number(outputCost),
      cacheReadCostCenticents: cacheReadCost
        ? Number(cacheReadCost)
        : undefined,
      cacheWriteCostCenticents: cacheWriteCost
        ? Number(cacheWriteCost)
        : undefined,
      totalCostCenticents: Number(totalCost),

      // Dollar amounts for display
      inputCostDollars: centicentsToDollars(inputCost),
      outputCostDollars: centicentsToDollars(outputCost),
      cacheReadCostDollars: cacheReadCost
        ? centicentsToDollars(cacheReadCost)
        : undefined,
      cacheWriteCostDollars: cacheWriteCost
        ? centicentsToDollars(cacheWriteCost)
        : undefined,
      totalCostDollars: centicentsToDollars(totalCost),
    };
  });
