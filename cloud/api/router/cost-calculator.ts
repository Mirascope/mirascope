/**
 * @fileoverview Base cost calculator and provider-specific implementations.
 *
 * Provides a unified interface for extracting usage from provider responses
 * and calculating costs using models.dev pricing data.
 *
 * All costs are calculated and returned in centi-cents (BIGINT).
 */

import { Effect } from "effect";

import type { ProviderName } from "@/api/router/providers";

import {
  getModelPricing,
  type TokenUsage,
  type CostBreakdown,
} from "@/api/router/pricing";

/**
 * Base cost calculator that handles shared logic for all providers.
 *
 * Subclasses implement provider-specific usage extraction and cache cost calculation.
 */
export abstract class BaseCostCalculator {
  protected readonly provider: ProviderName;

  constructor(provider: ProviderName) {
    this.provider = provider;
  }

  /**
   * Extracts token usage from a provider response.
   *
   * Must be implemented by each provider-specific calculator.
   *
   * @param body - The parsed provider response body
   * @returns Validated TokenUsage with non-negative numbers, or null if extraction fails
   */
  public abstract extractUsage(body: unknown): TokenUsage | null;

  /**
   * Calculates cache write cost from provider-specific breakdown.
   *
   * This allows each provider to handle their own cache pricing logic
   * without corrupting the actual token counts stored in the database.
   *
   * Must be implemented by each provider-specific calculator.
   *
   * @param cacheWriteTokens - Total cache write tokens
   * @param breakdown - Provider-specific cache write breakdown (for complex pricing)
   * @param cacheWritePrice - Cache write price per million tokens (in centicents)
   * @returns Cache write cost in centicents
   */
  protected calculateCacheWriteCost(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _cacheWriteTokens: number | undefined,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _breakdown: Record<string, number> | undefined,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _cacheWritePrice: bigint,
  ): CostBreakdown["cacheWriteCost"] {
    // Providers like Anthropic that charge for cache writes should overwrite this method
    return undefined;
  }

  /**
   * Extracts token usage from a streaming chunk.
   *
   * Must be implemented by each provider-specific calculator to handle
   * streaming-specific formats (e.g., OpenAI Responses API, Anthropic deltas).
   *
   * @param chunk - A parsed chunk from the streaming response
   * @returns Token usage if found, null otherwise
   */
  public abstract extractUsageFromStreamChunk(
    chunk: unknown,
  ): TokenUsage | null;

  /**
   * Calculates cost from TokenUsage using models.dev pricing data.
   *
   * @param modelId - The model ID
   * @param usage - Token usage data from the provider response
   * @returns Effect with cost breakdown (in centi-cents), or null if pricing unavailable
   */
  public calculate(
    modelId: string,
    usage: TokenUsage,
  ): Effect.Effect<CostBreakdown | null, never> {
    return Effect.gen(this, function* () {
      // Get pricing data (null if unavailable)
      const pricing = yield* getModelPricing(this.provider, modelId).pipe(
        Effect.catchAll(() => Effect.succeed(null)),
      );

      if (!pricing) {
        return null;
      }

      return yield* Effect.try(() => {
        const inputCost =
          (BigInt(usage.inputTokens) * pricing.input) / 1_000_000n;
        const outputCost =
          (BigInt(usage.outputTokens) * pricing.output) / 1_000_000n;

        const cacheReadCost =
          usage.cacheReadTokens && pricing.cache_read
            ? (BigInt(usage.cacheReadTokens) * pricing.cache_read) / 1_000_000n
            : undefined;

        // Use provider-specific cache write cost calculation
        const cacheWriteCost = this.calculateCacheWriteCost(
          usage.cacheWriteTokens,
          usage.cacheWriteBreakdown,
          pricing.cache_write || 0n,
        );

        const totalCost =
          inputCost +
          outputCost +
          (cacheReadCost || 0n) +
          (cacheWriteCost || 0n);

        return {
          inputCost,
          outputCost,
          cacheReadCost,
          cacheWriteCost,
          totalCost,
        };
      }).pipe(Effect.orElseSucceed(() => null));
    });
  }
}

/**
 * OpenAI-specific cost calculator.
 *
 * Supports both:
 * - Completions API: uses prompt_tokens/completion_tokens
 * - Responses API: uses input_tokens/output_tokens
 */
export class OpenAICostCalculator extends BaseCostCalculator {
  constructor() {
    super("openai");
  }

  public extractUsage(body: unknown): TokenUsage | null {
    if (typeof body !== "object" || body === null) return null;

    const bodyObj = body as Record<string, unknown>;
    const usage = bodyObj.usage as Record<string, unknown> | undefined;

    if (!usage) return null;

    // Check for Responses API format (input_tokens/output_tokens)
    if ("input_tokens" in usage && "output_tokens" in usage) {
      const inputTokensDetails = usage.input_tokens_details as
        | { cached_tokens?: number }
        | undefined;

      return {
        inputTokens: usage.input_tokens as number,
        outputTokens: usage.output_tokens as number,
        cacheReadTokens: inputTokensDetails?.cached_tokens,
      };
    }

    // Fall back to Completions API format (prompt_tokens/completion_tokens)
    if ("prompt_tokens" in usage && "completion_tokens" in usage) {
      const promptTokensDetails = usage.prompt_tokens_details as
        | { cached_tokens?: number }
        | undefined;

      return {
        inputTokens: usage.prompt_tokens as number,
        outputTokens: usage.completion_tokens as number,
        cacheReadTokens: promptTokensDetails?.cached_tokens,
      };
    }

    return null;
  }

  /**
   * Extracts usage from streaming chunks, handling OpenAI Responses API format.
   *
   * OpenAI Responses API sends usage in a special wrapper:
   * { type: "response.completed", response: { usage: { ... } } }
   */
  public extractUsageFromStreamChunk(chunk: unknown): TokenUsage | null {
    if (typeof chunk !== "object" || chunk === null) return null;

    const obj = chunk as Record<string, unknown>;

    // Handle OpenAI Responses API format
    if (obj.type === "response.completed" && obj.response) {
      const response = obj.response as Record<string, unknown>;
      if (response.usage) {
        // Extract from nested response.usage
        return this.extractUsage(response);
      }
    }

    // Fall back to standard extraction (handles Completions API)
    return this.extractUsage(chunk);
  }
}

/**
 * Anthropic-specific cost calculator.
 *
 * IMPORTANT: Anthropic's input_tokens does NOT include cache tokens.
 * Total input = input_tokens + cache_creation_input_tokens + cache_read_input_tokens
 *
 * CACHE PRICING:
 * Anthropic provides detailed cache breakdown via usage.cache_creation:
 * - ephemeral_5m_input_tokens: 5-minute TTL caches (cost 1.25x input price)
 * - ephemeral_1h_input_tokens: 1-hour TTL caches (cost 2.0x input price)
 *
 * We store the ACTUAL token counts (not normalized) in cacheWriteTokens and
 * cacheWriteBreakdown for accurate record-keeping. The cost calculation happens
 * in calculateCacheWriteCost() using the provider-specific pricing logic.
 */
export class AnthropicCostCalculator extends BaseCostCalculator {
  constructor() {
    super("anthropic");
  }

  // Pricing multiplier: 1h / 5m = 2.0 / 1.25 = 1.6
  static readonly EPHEMERAL_1H_MULTIPLIER = 1.6;

  public extractUsage(body: unknown): TokenUsage | null {
    if (typeof body !== "object" || body === null) return null;

    const usage = (
      body as {
        usage?: {
          input_tokens: number;
          output_tokens: number;
          cache_creation_input_tokens?: number;
          cache_read_input_tokens?: number;
          cache_creation?: {
            ephemeral_5m_input_tokens?: number;
            ephemeral_1h_input_tokens?: number;
          };
        };
      }
    ).usage;

    if (!usage) return null;

    const cacheReadTokens = usage.cache_read_input_tokens || 0;

    // Extract raw token counts and breakdown
    const ephemeral5m = usage.cache_creation?.ephemeral_5m_input_tokens || 0;
    const ephemeral1h = usage.cache_creation?.ephemeral_1h_input_tokens || 0;

    // Store ACTUAL total tokens (no normalization)
    // If detailed breakdown is available, use it; otherwise fall back to aggregate field
    const cacheWriteTokens =
      ephemeral5m + ephemeral1h || usage.cache_creation_input_tokens || 0;

    // Store breakdown for accurate cost calculation (only if detailed breakdown exists)
    const cacheWriteBreakdown =
      ephemeral5m > 0 || ephemeral1h > 0
        ? { ephemeral5m, ephemeral1h }
        : undefined;

    return {
      inputTokens: usage.input_tokens,
      outputTokens: usage.output_tokens,
      cacheReadTokens: cacheReadTokens > 0 ? cacheReadTokens : undefined,
      cacheWriteTokens: cacheWriteTokens > 0 ? cacheWriteTokens : undefined,
      cacheWriteBreakdown,
    };
  }

  protected override calculateCacheWriteCost(
    cacheWriteTokens: number | undefined,
    breakdown: Record<string, number> | undefined,
    cacheWritePrice: bigint,
  ): CostBreakdown["cacheWriteCost"] {
    // Try to use detailed breakdown first (preferred for accuracy)
    if (breakdown) {
      // At this point, we know one or the other is >0 since breakdown would otherwise be undefined
      const { ephemeral5m, ephemeral1h } = breakdown;
      // Anthropic cache pricing:
      // - 5m ephemeral: 1.25x input price (which is what cacheWritePrice represents from models.dev)
      // - 1h ephemeral: 2.0x input price
      // Cost calculation:
      //   cost_5m = ephemeral5m * cacheWritePrice / 1M
      //   cost_1h = ephemeral1h * cacheWritePrice * 1.6 / 1M  (because 2.0 / 1.25 = 1.6)

      const cost5m = (BigInt(ephemeral5m) * cacheWritePrice) / 1_000_000n;
      const cost1h =
        (BigInt(ephemeral1h) *
          cacheWritePrice *
          BigInt(
            Math.round(AnthropicCostCalculator.EPHEMERAL_1H_MULTIPLIER * 10),
          )) /
        (1_000_000n * 10n);

      return cost5m + cost1h;
    }

    // Fallback to simple token count (for older API versions or missing breakdown)
    if (!cacheWriteTokens) {
      return undefined;
    }
    // Defensive: fallback for API versions without detailed breakdown
    return (BigInt(cacheWriteTokens) * cacheWritePrice) / 1_000_000n;
  }

  /**
   * Extracts usage from streaming chunks.
   *
   * Anthropic streams usage in the final message_stop or message_delta event.
   */
  public extractUsageFromStreamChunk(chunk: unknown): TokenUsage | null {
    // Delegate to standard extraction - Anthropic format is the same for streaming
    return this.extractUsage(chunk);
  }
}

/**
 * Google AI-specific cost calculator.
 */
export class GoogleCostCalculator extends BaseCostCalculator {
  constructor() {
    super("google");
  }

  public extractUsage(body: unknown): TokenUsage | null {
    if (typeof body !== "object" || body === null) return null;

    const bodyObj = body as Record<string, unknown>;

    if (!bodyObj.usageMetadata) {
      return null;
    }

    const metadata = bodyObj.usageMetadata as
      | {
          promptTokenCount?: number;
          candidatesTokenCount?: number;
          totalTokenCount?: number;
          cachedContentTokenCount?: number;
        }
      | undefined;

    if (
      !metadata ||
      metadata.promptTokenCount === undefined ||
      metadata.candidatesTokenCount === undefined
    ) {
      return null;
    }

    return {
      inputTokens: metadata.promptTokenCount,
      outputTokens: metadata.candidatesTokenCount,
      cacheReadTokens: metadata.cachedContentTokenCount,
    };
  }

  /**
   * Extracts usage from streaming chunks.
   *
   * Google streams usage in the final chunk with usageMetadata.
   */
  public extractUsageFromStreamChunk(chunk: unknown): TokenUsage | null {
    // Delegate to standard extraction - Google format is the same for streaming
    return this.extractUsage(chunk);
  }
}
