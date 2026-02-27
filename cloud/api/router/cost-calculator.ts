/**
 * @fileoverview Base cost calculator and provider-specific implementations.
 *
 * Provides a unified interface for extracting usage from provider responses
 * and calculating costs using models.dev pricing data.
 *
 * All costs are calculated and returned in centi-cents (BIGINT).
 */

import { Effect } from "effect";

import type { CostInCenticents } from "@/api/router/cost-utils";
import type { ProviderName } from "@/api/router/providers";

import {
  type TokenUsage,
  type CostBreakdown,
  type NativeToolUsage,
  type ModelPricing,
} from "@/api/router/pricing";
import { calculateToolCost, type ToolType } from "@/api/router/tool-pricing";

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
   * Extracts native tool usage from a provider response.
   *
   * Identifies usage of server-side tools that have separate pricing
   * (e.g., web search, code execution).
   *
   * Must be implemented by each provider-specific calculator.
   *
   * @param body - The parsed provider response body
   * @returns Array of tool usage data, or empty array if none
   */
  public abstract extractToolUsage(body: unknown): NativeToolUsage[];

  /**
   * Adjusts tool usage based on model-specific pricing rules.
   *
   * Override this method in provider-specific calculators to handle
   * model-specific pricing variations (e.g., Gemini 2.5 vs 3+ pricing).
   *
   * @param modelId - The model ID
   * @param toolUsage - The original tool usage array
   * @returns Adjusted tool usage array
   */
  protected adjustToolUsageForModel(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _modelId: string,
    toolUsage: NativeToolUsage[],
  ): NativeToolUsage[] {
    // Default: no adjustment
    return toolUsage;
  }

  /**
   * Calculates cost from TokenUsage using pre-fetched pricing data.
   *
   * The pricing data is required and must be provided from the estimation phase.
   * This ensures we never need to make an HTTP call to models.dev during cost
   * calculation, eliminating the possibility of transient fetch failures causing
   * metering to be silently skipped.
   *
   * @param modelId - The model ID (for tool pricing lookups)
   * @param usage - Token usage data from the provider response
   * @param modelPricing - Pricing data from the estimation phase (required)
   * @returns Effect with cost breakdown (in centi-cents)
   */
  public calculate(
    modelId: string,
    usage: TokenUsage,
    modelPricing: ModelPricing,
  ): Effect.Effect<CostBreakdown, never> {
    return Effect.sync(() => {
      // Helper to safely convert tokens to BigInt (handles decimals and non-finite values)
      const tokensToBigInt = (tokens: number): bigint => {
        if (!Number.isFinite(tokens) || tokens < 0) return 0n;
        return BigInt(Math.floor(tokens));
      };

      const inputCost =
        (tokensToBigInt(usage.inputTokens) * modelPricing.input) / 1_000_000n;
      const outputCost =
        (tokensToBigInt(usage.outputTokens) * modelPricing.output) / 1_000_000n;

      const cacheReadCost =
        usage.cacheReadTokens && modelPricing.cache_read
          ? (tokensToBigInt(usage.cacheReadTokens) * modelPricing.cache_read) /
            1_000_000n
          : undefined;

      // Use provider-specific cache write cost calculation
      const cacheWriteCost = this.calculateCacheWriteCost(
        usage.cacheWriteTokens,
        usage.cacheWriteBreakdown,
        modelPricing.cache_write || 0n,
      );

      // Calculate tool costs
      let toolCost: CostInCenticents | undefined;
      let toolCostBreakdown: Record<string, CostInCenticents> | undefined;

      if (usage.toolUsage && usage.toolUsage.length > 0) {
        // Apply model-specific adjustments to tool usage
        const adjustedToolUsage = this.adjustToolUsageForModel(
          modelId,
          usage.toolUsage,
        );

        toolCostBreakdown = {};
        let totalToolCost = 0n;

        for (const tool of adjustedToolUsage) {
          const cost = calculateToolCost(
            tool.toolType as ToolType,
            tool.callCount,
            tool.durationSeconds,
          );
          if (cost && cost > 0n) {
            toolCostBreakdown[tool.toolType] = cost;
            totalToolCost += cost;
          }
        }

        if (totalToolCost > 0n) {
          toolCost = totalToolCost;
        } else {
          toolCostBreakdown = undefined;
        }
      }

      // Token cost is sum of input, output, and cache costs (excludes tool costs)
      const tokenCost =
        inputCost + outputCost + (cacheReadCost || 0n) + (cacheWriteCost || 0n);

      const totalCost = tokenCost + (toolCost || 0n);

      return {
        inputCost,
        outputCost,
        cacheReadCost,
        cacheWriteCost,
        tokenCost,
        toolCost,
        toolCostBreakdown,
        totalCost,
      };
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

    let tokenUsage: TokenUsage | null = null;

    // Check for Responses API format (input_tokens/output_tokens)
    if ("input_tokens" in usage && "output_tokens" in usage) {
      const inputTokensDetails = usage.input_tokens_details as
        | { cached_tokens?: number }
        | undefined;

      tokenUsage = {
        inputTokens: usage.input_tokens as number,
        outputTokens: usage.output_tokens as number,
        cacheReadTokens: inputTokensDetails?.cached_tokens,
      };
    }
    // Fall back to Completions API format (prompt_tokens/completion_tokens)
    else if ("prompt_tokens" in usage && "completion_tokens" in usage) {
      const promptTokensDetails = usage.prompt_tokens_details as
        | { cached_tokens?: number }
        | undefined;

      tokenUsage = {
        inputTokens: usage.prompt_tokens as number,
        outputTokens: usage.completion_tokens as number,
        cacheReadTokens: promptTokensDetails?.cached_tokens,
      };
    }

    if (!tokenUsage) return null;

    // Extract tool usage and include in the result
    const toolUsage = this.extractToolUsage(body);
    if (toolUsage.length > 0) {
      tokenUsage.toolUsage = toolUsage;
    }

    return tokenUsage;
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

  /**
   * Extracts native tool usage from OpenAI responses.
   *
   * OpenAI Responses API reports web search calls in the output array:
   * { output: [{ type: "web_search_call", ... }, ...] }
   */
  public extractToolUsage(body: unknown): NativeToolUsage[] {
    if (typeof body !== "object" || body === null) return [];

    const bodyObj = body as Record<string, unknown>;
    const tools: NativeToolUsage[] = [];

    // Check for Responses API format - count web_search_call items in output
    if (Array.isArray(bodyObj.output)) {
      const output = bodyObj.output as Array<{ type?: string }>;
      const webSearchCalls = output.filter(
        (item) => item.type === "web_search_call",
      ).length;

      if (webSearchCalls > 0) {
        tools.push({
          toolType: "openai_web_search",
          callCount: webSearchCalls,
        });
      }

      // Count code_interpreter_call items
      const codeInterpreterCalls = output.filter(
        (item) => item.type === "code_interpreter_call",
      ).length;

      if (codeInterpreterCalls > 0) {
        // Use minimum billing increment (1 hour per container session)
        tools.push({
          toolType: "openai_code_interpreter",
          callCount: codeInterpreterCalls,
          durationSeconds: 3600, // 1 hour minimum
        });
      }

      // Count file_search_call items
      const fileSearchCalls = output.filter(
        (item) => item.type === "file_search_call",
      ).length;

      if (fileSearchCalls > 0) {
        tools.push({
          toolType: "openai_file_search",
          callCount: fileSearchCalls,
        });
      }
    }

    return tools;
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

    const tokenUsage: TokenUsage = {
      inputTokens: usage.input_tokens,
      outputTokens: usage.output_tokens,
      cacheReadTokens: cacheReadTokens > 0 ? cacheReadTokens : undefined,
      cacheWriteTokens: cacheWriteTokens > 0 ? cacheWriteTokens : undefined,
      cacheWriteBreakdown,
    };

    // Extract tool usage and include in the result
    const toolUsage = this.extractToolUsage(body);
    if (toolUsage.length > 0) {
      tokenUsage.toolUsage = toolUsage;
    }

    return tokenUsage;
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

  /**
   * Extracts native tool usage from Anthropic responses.
   *
   * Anthropic reports server tool usage in the usage object:
   * { usage: { server_tool_use: { web_search_requests: N } } }
   */
  public extractToolUsage(body: unknown): NativeToolUsage[] {
    if (typeof body !== "object" || body === null) return [];

    const usage = (
      body as {
        usage?: {
          server_tool_use?: {
            web_search_requests?: number;
          };
        };
      }
    ).usage;

    if (!usage?.server_tool_use) return [];

    const tools: NativeToolUsage[] = [];
    const serverToolUse = usage.server_tool_use;

    // Web search
    if (
      serverToolUse.web_search_requests &&
      serverToolUse.web_search_requests > 0
    ) {
      tools.push({
        toolType: "anthropic_web_search",
        callCount: serverToolUse.web_search_requests,
      });
    }

    // Note: Code execution duration is not currently reported in Anthropic's usage object.
    // When it becomes available, we can extract it here and use the 5 minute minimum.

    return tools;
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

    const tokenUsage: TokenUsage = {
      inputTokens: metadata.promptTokenCount,
      outputTokens: metadata.candidatesTokenCount,
      cacheReadTokens: metadata.cachedContentTokenCount,
    };

    // Extract tool usage and include in the result
    const toolUsage = this.extractToolUsage(body);
    if (toolUsage.length > 0) {
      tokenUsage.toolUsage = toolUsage;
    }

    return tokenUsage;
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

  /**
   * Adjusts tool usage for Gemini 2.5 models.
   *
   * Gemini 2.5 charges $35/1000 prompts for grounding, while Gemini 3+ charges
   * $14/1000 queries. To handle this without changing the pricing interface,
   * we detect 2.5 models and set callCount to 2.5 (since $14 * 2.5 = $35).
   *
   * This effectively charges $0.035 per prompt for 2.5 models instead of
   * per-query pricing.
   */
  protected override adjustToolUsageForModel(
    modelId: string,
    toolUsage: NativeToolUsage[],
  ): NativeToolUsage[] {
    // Check if this is a Gemini 2.5 model (e.g., "gemini-2.5-pro", "gemini-2.5-flash")
    if (!modelId.includes("2.5")) {
      return toolUsage;
    }

    // For 2.5 models, adjust google_grounding_search callCount to 2.5
    // This makes the cost calculation work out: $14/1000 * 2.5 = $35/1000
    return toolUsage.map((tool) => {
      if (tool.toolType === "google_grounding_search") {
        return {
          ...tool,
          callCount: 2.5,
        };
      }
      return tool;
    });
  }

  /**
   * Extracts native tool usage from Google Gemini responses.
   *
   * Google reports grounding with Google Search usage in groundingMetadata:
   * { groundingMetadata: { webSearchQueries: [...], groundingSupports: [...] } }
   *
   * Only charges when grounding results are actually returned (groundingSupports present).
   */
  public extractToolUsage(body: unknown): NativeToolUsage[] {
    if (typeof body !== "object" || body === null) return [];

    const bodyObj = body as Record<string, unknown>;
    const groundingMetadata = bodyObj.groundingMetadata as
      | {
          webSearchQueries?: string[];
          groundingSupports?: unknown[];
        }
      | undefined;

    if (!groundingMetadata) return [];

    const tools: NativeToolUsage[] = [];

    // Google Search grounding - only charged when grounding supports are present
    // (meaning the search actually returned results used in the response)
    if (
      groundingMetadata.webSearchQueries &&
      groundingMetadata.webSearchQueries.length > 0 &&
      groundingMetadata.groundingSupports &&
      groundingMetadata.groundingSupports.length > 0
    ) {
      tools.push({
        toolType: "google_grounding_search",
        callCount: groundingMetadata.webSearchQueries.length,
        metadata: {
          queries: groundingMetadata.webSearchQueries,
        },
      });
    }

    return tools;
  }
}
