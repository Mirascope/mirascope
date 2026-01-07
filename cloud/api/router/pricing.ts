/**
 * @fileoverview Pricing data management for AI model cost calculation.
 *
 * Fetches pricing data from models.dev/api.json and provides cost calculation
 * utilities for tracking usage costs across providers.
 */

import { Effect } from "effect";
import {
  getModelsDotDevProviderIds,
  type ProviderName,
} from "@/api/router/providers";

/**
 * Pricing information for a model.
 */
export interface ModelPricing {
  /** Cost per million input tokens in USD */
  input: number;
  /** Cost per million output tokens in USD */
  output: number;
  /** Optional: Cost per million cache read tokens in USD */
  cache_read?: number;
  /** Optional: Cost per million cache write tokens in USD */
  cache_write?: number;
}

/**
 * Provider API structure from models.dev
 */
interface ProviderData {
  id: string;
  name: string;
  models: Record<
    string,
    {
      id: string;
      name: string;
      cost?: ModelPricing;
    }
  >;
}

/**
 * Cache for models.dev pricing data
 */
let pricingCache: Record<string, ProviderData> | null = null;
let lastFetchTime: number = 0;
const CACHE_TTL_MS = 1000 * 60 * 60; // 1 hour

/**
 * Clears the pricing cache. Useful for testing.
 */
export function clearPricingCache(): void {
  pricingCache = null;
  lastFetchTime = 0;
}

/**
 * Fetches pricing data from models.dev/api.json
 */
export function fetchModelsDotDevPricingData() {
  return Effect.gen(function* () {
    const response = yield* Effect.tryPromise({
      try: async () => {
        return await fetch("https://models.dev/api.json");
      },
      catch: (error) =>
        new Error(
          `Error fetching pricing data: ${error instanceof Error ? error.message : /* v8 ignore next */ String(error)}`,
        ),
    });

    if (!response.ok) {
      return yield* Effect.fail(new Error("Failed to fetch pricing data"));
    }

    const data = yield* Effect.tryPromise({
      try: async () => await response.json<Record<string, ProviderData>>(),
      catch: (error) =>
        new Error(
          `Failed to parse JSON from response body: ${error instanceof Error ? error.message : /* v8 ignore next */ String(error)}`,
        ),
    });

    pricingCache = data;
    lastFetchTime = Date.now();
    return data;
  });
}

/**
 * Gets cached pricing data, fetching if stale or missing.
 */
export function getModelsDotDevPricingData() {
  return Effect.gen(function* () {
    const now = Date.now();

    // Return cache if fresh
    if (pricingCache && now - lastFetchTime < CACHE_TTL_MS) {
      return pricingCache;
    }

    // Fetch fresh data
    return yield* fetchModelsDotDevPricingData();
  });
}

/**
 * Looks up pricing for a specific model.
 *
 * This uses the data fetched from models.dev/api.json for accurate,
 * current pricing data.
 *
 * @param provider - Our provider name (openai, anthropic, google)
 * @param modelId - The model ID used in the request
 * @returns Pricing info or null if not found
 */
export function getModelPricing(
  provider: ProviderName,
  modelId: string,
): Effect.Effect<ModelPricing | null, Error> {
  return Effect.gen(function* () {
    const data = yield* getModelsDotDevPricingData();

    // Try each possible provider ID
    const providerIds = getModelsDotDevProviderIds(provider);

    for (const providerId of providerIds) {
      const providerData = data[providerId];
      const modelPricing = providerData?.models[modelId]?.cost;
      if (modelPricing) {
        return modelPricing;
      }
    }

    return null;
  });
}

/**
 * Usage data for cost calculation
 */
export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  cacheReadTokens?: number;
  cacheWriteTokens?: number;
}

/**
 * Calculated cost breakdown
 */
export interface CostBreakdown {
  inputCost: number;
  outputCost: number;
  cacheReadCost?: number;
  cacheWriteCost?: number;
  totalCost: number;
}

/**
 * Formatted cost breakdown with string representations
 */
export interface FormattedCostBreakdown {
  input: string;
  output: string;
  cacheRead?: string;
  cacheWrite?: string;
  total: string;
}

/**
 * Calculates the cost for a request based on usage and pricing.
 *
 * @param pricing - The model's pricing information
 * @param usage - Token usage from the response
 * @returns Cost breakdown in USD
 */
export function calculateCost(
  pricing: ModelPricing,
  usage: TokenUsage,
): CostBreakdown {
  // All costs in models.dev are per million tokens
  const inputCost = (usage.inputTokens / 1_000_000) * pricing.input;
  const outputCost = (usage.outputTokens / 1_000_000) * pricing.output;

  const cacheReadCost =
    usage.cacheReadTokens && pricing.cache_read
      ? (usage.cacheReadTokens / 1_000_000) * pricing.cache_read
      : undefined;

  const cacheWriteCost =
    usage.cacheWriteTokens && pricing.cache_write
      ? (usage.cacheWriteTokens / 1_000_000) * pricing.cache_write
      : undefined;

  const totalCost =
    inputCost + outputCost + (cacheReadCost || 0) + (cacheWriteCost || 0);

  return {
    inputCost,
    outputCost,
    cacheReadCost,
    cacheWriteCost,
    totalCost,
  };
}

/**
 * Formats a single cost value in USD as a string.
 */
function formatCostValue(cost: number): string {
  return `$${cost.toFixed(6)}`;
}

/**
 * Formats a cost breakdown into string representations.
 *
 * @param breakdown - The cost breakdown to format
 * @returns Formatted cost breakdown with all values as strings
 */
export function formatCostBreakdown(
  breakdown: CostBreakdown,
): FormattedCostBreakdown {
  return {
    input: formatCostValue(breakdown.inputCost),
    output: formatCostValue(breakdown.outputCost),
    cacheRead: breakdown.cacheReadCost
      ? formatCostValue(breakdown.cacheReadCost)
      : undefined,
    cacheWrite: breakdown.cacheWriteCost
      ? formatCostValue(breakdown.cacheWriteCost)
      : undefined,
    total: formatCostValue(breakdown.totalCost),
  };
}
