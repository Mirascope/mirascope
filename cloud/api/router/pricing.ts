/**
 * @fileoverview Pricing data management for AI model cost calculation.
 *
 * Fetches pricing data from models.dev/api.json and provides cost calculation
 * utilities for tracking usage costs across providers.
 *
 * All costs are stored and calculated in centi-cents (BIGINT).
 * Pricing data from models.dev (in dollars) is converted to centi-cents immediately.
 */

import { Effect } from "effect";
import {
  getModelsDotDevProviderIds,
  type ProviderName,
} from "@/api/router/providers";
import {
  type CostInCenticents,
  dollarsToCenticents,
} from "@/api/router/cost-utils";

/**
 * Pricing information for a model (fetched from models.dev in dollars).
 * Internal use only - immediately converted to ModelPricingCenticents.
 */
interface ModelPricingDollars {
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
 * Pricing information for a model in centi-cents.
 * Use this type throughout the system.
 */
export interface ModelPricing {
  /** Cost per million input tokens in centi-cents */
  input: CostInCenticents;
  /** Cost per million output tokens in centi-cents */
  output: CostInCenticents;
  /** Optional: Cost per million cache read tokens in centi-cents */
  cache_read?: CostInCenticents;
  /** Optional: Cost per million cache write tokens in centi-cents */
  cache_write?: CostInCenticents;
}

/**
 * Provider API structure from models.dev (raw format with dollar pricing)
 */
interface ProviderData {
  id: string;
  name: string;
  models: Record<
    string,
    {
      id: string;
      name: string;
      cost?: ModelPricingDollars;
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
 * Converts dollar-based pricing to centi-cent pricing.
 * Returns null if pricing contains invalid values (NaN, negative, etc.).
 */
function convertPricingToCenticents(
  pricing: ModelPricingDollars,
): ModelPricing | null {
  // Validate input and output (required fields)
  if (
    !Number.isFinite(pricing.input) ||
    !Number.isFinite(pricing.output) ||
    pricing.input < 0 ||
    pricing.output < 0
  ) {
    return null;
  }

  // Validate optional cache fields if present
  if (
    (pricing.cache_read !== undefined &&
      (!Number.isFinite(pricing.cache_read) || pricing.cache_read < 0)) ||
    (pricing.cache_write !== undefined &&
      (!Number.isFinite(pricing.cache_write) || pricing.cache_write < 0))
  ) {
    return null;
  }

  return {
    input: dollarsToCenticents(pricing.input),
    output: dollarsToCenticents(pricing.output),
    cache_read: pricing.cache_read
      ? dollarsToCenticents(pricing.cache_read)
      : undefined,
    cache_write: pricing.cache_write
      ? dollarsToCenticents(pricing.cache_write)
      : undefined,
  };
}

/**
 * Looks up pricing for a specific model.
 *
 * This uses the data fetched from models.dev/api.json for accurate,
 * current pricing data. Pricing is immediately converted from dollars
 * to centi-cents for use throughout the system.
 *
 * @param provider - Our provider name (openai, anthropic, google)
 * @param modelId - The model ID used in the request
 * @returns Pricing info in centi-cents or null if not found
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
      const modelPricingDollars = providerData?.models[modelId]?.cost;
      if (modelPricingDollars) {
        // Convert from dollars to centi-cents immediately
        return convertPricingToCenticents(modelPricingDollars);
      }
    }

    return null;
  });
}

/**
 * Usage data for cost calculation.
 */
export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  cacheReadTokens?: number;
  cacheWriteTokens?: number;
  /**
   * Provider-specific cache write breakdown for accurate record-keeping.
   * Stored as JSONB in the database to support any provider's cache structure.
   *
   * Examples:
   * - Anthropic: { ephemeral5m: 100, ephemeral1h: 50 }
   * - OpenAI/Google: Not needed (no breakdown required)
   */
  cacheWriteBreakdown?: Record<string, number>;
}

/**
 * Calculated cost breakdown in centi-cents.
 */
export interface CostBreakdown {
  inputCost: CostInCenticents;
  outputCost: CostInCenticents;
  cacheReadCost?: CostInCenticents;
  cacheWriteCost?: CostInCenticents;
  totalCost: CostInCenticents;
}
