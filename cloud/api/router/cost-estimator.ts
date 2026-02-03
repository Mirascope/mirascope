/**
 * @fileoverview Cost estimation for router requests.
 *
 * Provides utilities for estimating the cost of AI provider requests before they're made.
 * This is used by the reservation system to lock sufficient funds for concurrent requests.
 *
 * All cost estimates are returned in centi-cents (BIGINT).
 */

import { Effect } from "effect";

import type { CostInCenticents } from "@/api/router/cost-utils";
import type { ProviderName } from "@/api/router/providers";

import { getModelPricing, type ModelPricing } from "@/api/router/pricing";
import { PricingUnavailableError } from "@/errors";

/**
 * Default estimate for output tokens when not specified.
 * Conservative estimate to avoid underestimating costs.
 */
const DEFAULT_OUTPUT_TOKENS_ESTIMATE = 1000;

/**
 * Rough heuristic for token counting: 4 characters per token.
 * This is an approximation used for input token estimation.
 */
const CHARS_PER_TOKEN = 4;

/**
 * Parameters for cost estimation.
 */
export interface EstimateCostParams {
  /** Provider name (openai, anthropic, google) */
  provider: ProviderName;
  /** Model ID */
  modelId: string;
  /** Parsed request body */
  requestBody: unknown;
}

/**
 * Result of cost estimation.
 */
export interface EstimatedCost {
  /** Estimated cost in centi-cents */
  cost: CostInCenticents;
  /** Estimated input tokens */
  inputTokens: number;
  /** Estimated output tokens */
  outputTokens: number;
  /** Pricing data used for estimation (cached for later use in cost calculation) */
  modelPricing: ModelPricing;
}

/**
 * Message-like structure with content and optional role.
 * Used internally to unify different provider message formats.
 */
interface MessageLike {
  content?: unknown;
  role?: unknown;
}

/**
 * Base cost estimator that handles shared logic for all providers.
 *
 * Subclasses implement provider-specific extraction of messages/contents arrays
 * and max token fields. All token counting logic is centralized in the base class.
 */
export abstract class BaseCostEstimator {
  protected readonly provider: ProviderName;

  constructor(provider: ProviderName) {
    this.provider = provider;
  }

  /**
   * Extracts messages from the request body in provider-specific format.
   *
   * Must be implemented by each provider-specific estimator.
   *
   * @param requestBody - Non-null object (validated by caller)
   * @returns Array of message-like objects, or null if not found
   */
  protected abstract extractMessages(
    requestBody: Record<string, unknown>,
  ): MessageLike[] | null;

  /**
   * Extracts the max output tokens from the request body in provider-specific format.
   *
   * Must be implemented by each provider-specific estimator.
   *
   * @param requestBody - Non-null object (validated by caller)
   * @returns Max output tokens if specified, or null to use default
   */
  protected abstract extractMaxOutputTokens(
    requestBody: Record<string, unknown>,
  ): number | null;

  /**
   * Counts characters from message content.
   *
   * Handles both string content and array content (multimodal):
   * - String content: counts characters directly
   * - Array content: extracts text from blocks and counts characters
   *
   * @private
   */
  private countContentChars(content: unknown): number {
    if (typeof content === "string") {
      return content.length;
    }

    if (Array.isArray(content)) {
      // Handle multimodal content (array of content blocks)
      let chars = 0;
      for (const block of content) {
        if (
          typeof block === "object" &&
          block !== null &&
          "text" in block &&
          typeof (block as { text?: unknown }).text === "string"
        ) {
          chars += (block as { text: string }).text.length;
        }
      }
      return chars;
    }

    return 0;
  }

  /**
   * Counts tokens from an array of messages.
   *
   * Sums up:
   * - Content characters (string or multimodal)
   * - Role overhead (if present)
   *
   * @private
   */
  private countMessageTokens(messages: MessageLike[]): number {
    let totalChars = 0;

    for (const message of messages) {
      // Count content
      totalChars += this.countContentChars(message.content);

      // Add role overhead
      if (typeof message.role === "string") {
        totalChars += message.role.length;
      }
    }

    return Math.ceil(totalChars / CHARS_PER_TOKEN);
  }

  /**
   * Extracts the number of input tokens from a request body.
   *
   * Uses provider-specific message extraction, then common token counting logic.
   */
  protected extractInputTokens(requestBody: unknown): number {
    if (typeof requestBody !== "object" || requestBody === null) {
      return 0;
    }

    const body = requestBody as Record<string, unknown>;
    const messages = this.extractMessages(body);
    if (messages) {
      return this.countMessageTokens(messages);
    }

    // Fallback: stringify and count characters
    return Math.ceil(JSON.stringify(body).length / CHARS_PER_TOKEN);
  }

  /**
   * Extracts the number of output tokens from a request body.
   *
   * Uses provider-specific max tokens extraction.
   */
  protected extractOutputTokens(requestBody: unknown): number {
    if (typeof requestBody !== "object" || requestBody === null) {
      return DEFAULT_OUTPUT_TOKENS_ESTIMATE;
    }

    const body = requestBody as Record<string, unknown>;
    const maxTokens = this.extractMaxOutputTokens(body);
    return maxTokens ?? DEFAULT_OUTPUT_TOKENS_ESTIMATE;
  }

  /**
   * Estimates the cost of a router request before it's made.
   *
   * This function:
   * 1. Estimates input/output token counts from the request body
   * 2. Fetches pricing data for the model
   * 3. Calculates estimated cost in centi-cents
   *
   * The estimate is intentionally conservative (tends to overestimate) to ensure
   * sufficient funds are reserved. The actual cost will be charged on settlement.
   *
   * @param model - Model ID
   * @param requestBody - Parsed request body
   * @returns Estimated cost in centi-cents
   * @throws PricingUnavailableError if pricing data cannot be fetched
   *
   * @example
   * ```ts
   * const estimator = new OpenAICostEstimator();
   * const estimate = yield* estimator.estimate(
   *   "gpt-4",
   *   { messages: [...], max_tokens: 1024 }
   * );
   * console.log(`Estimated cost: ${estimate.cost} centi-cents`);
   * ```
   */
  public estimate(
    model: string,
    requestBody: unknown,
  ): Effect.Effect<EstimatedCost, PricingUnavailableError | Error> {
    return Effect.gen(this, function* () {
      const inputTokens = this.extractInputTokens(requestBody);
      const outputTokens = this.extractOutputTokens(requestBody);

      // Get pricing data - fail if unavailable
      const pricing = yield* getModelPricing(this.provider, model).pipe(
        Effect.flatMap((p) =>
          p === null
            ? Effect.fail(
                new PricingUnavailableError({
                  message: `Pricing unavailable for ${this.provider}/${model}`,
                  provider: this.provider,
                  model,
                }),
              )
            : Effect.succeed(p),
        ),
      );

      // Calculate cost in centi-cents
      // Pricing is in centi-cents per million tokens
      const inputCost = (BigInt(inputTokens) * pricing.input) / 1_000_000n;
      const outputCost = (BigInt(outputTokens) * pricing.output) / 1_000_000n;
      const totalCost = inputCost + outputCost;

      return {
        cost: totalCost,
        inputTokens,
        outputTokens,
        modelPricing: pricing,
      };
    });
  }
}

/**
 * OpenAI-specific cost estimator.
 *
 * Handles OpenAI format:
 * - messages array with content field
 * - max_tokens for output estimation
 */
export class OpenAICostEstimator extends BaseCostEstimator {
  constructor() {
    super("openai");
  }

  protected extractMessages(requestBody: unknown): MessageLike[] | null {
    const body = requestBody as Record<string, unknown>;
    if (Array.isArray(body.messages)) {
      return body.messages as MessageLike[];
    }
    return null;
  }

  protected extractMaxOutputTokens(requestBody: unknown): number | null {
    const body = requestBody as Record<string, unknown>;
    if (typeof body.max_tokens === "number" && body.max_tokens > 0) {
      return body.max_tokens;
    }
    return null;
  }
}

/**
 * Anthropic-specific cost estimator.
 *
 * Handles Anthropic format (same as OpenAI):
 * - messages array with content field
 * - max_tokens for output estimation
 */
export class AnthropicCostEstimator extends BaseCostEstimator {
  constructor() {
    super("anthropic");
  }

  protected extractMessages(
    requestBody: Record<string, unknown>,
  ): MessageLike[] | null {
    if (Array.isArray(requestBody.messages)) {
      return requestBody.messages as MessageLike[];
    }
    return null;
  }

  protected extractMaxOutputTokens(
    requestBody: Record<string, unknown>,
  ): number | null {
    if (
      typeof requestBody.max_tokens === "number" &&
      requestBody.max_tokens > 0
    ) {
      return requestBody.max_tokens;
    }
    return null;
  }
}

/**
 * Google AI-specific cost estimator.
 *
 * Handles Google format:
 * - contents array with parts (maps to message-like structure)
 * - generationConfig.maxOutputTokens for output estimation
 */
export class GoogleCostEstimator extends BaseCostEstimator {
  constructor() {
    super("google");
  }

  protected extractMessages(
    requestBody: Record<string, unknown>,
  ): MessageLike[] | null {
    if (Array.isArray(requestBody.contents)) {
      // Convert Google's contents format to message-like structure
      return (requestBody.contents as Array<Record<string, unknown>>).map(
        (content) => ({
          content: content.parts,
          role: content.role,
        }),
      );
    }
    return null;
  }

  protected extractMaxOutputTokens(
    requestBody: Record<string, unknown>,
  ): number | null {
    if (
      typeof requestBody.generationConfig === "object" &&
      requestBody.generationConfig !== null
    ) {
      const config = requestBody.generationConfig as Record<string, unknown>;
      if (
        typeof config.maxOutputTokens === "number" &&
        config.maxOutputTokens > 0
      ) {
        return config.maxOutputTokens;
      }
    }
    return null;
  }
}

/**
 * Factory function to get the appropriate cost estimator for a provider.
 */
function getCostEstimator(provider: ProviderName): BaseCostEstimator {
  switch (provider) {
    case "openai":
      return new OpenAICostEstimator();
    case "anthropic":
      return new AnthropicCostEstimator();
    case "google":
      return new GoogleCostEstimator();
    /* v8 ignore next 4 */
    default: {
      const exhaustiveCheck: never = provider;
      throw new Error(`Unsupported provider: ${exhaustiveCheck as string}`);
    }
  }
}

/**
 * Estimates the cost of a router request before it's made.
 *
 * @param params - Cost estimation parameters
 * @returns Estimated cost
 * @throws PricingUnavailableError if pricing data cannot be fetched
 */
/**
 * Estimates the cost of an AI provider request.
 *
 * @param params - Estimation parameters
 * @returns Effect that resolves to estimated cost
 * @throws PricingUnavailableError if pricing data cannot be fetched
 */
export function estimateCost({
  provider,
  modelId,
  requestBody,
}: EstimateCostParams): Effect.Effect<
  EstimatedCost,
  PricingUnavailableError | Error
> {
  const estimator = getCostEstimator(provider);
  return estimator.estimate(modelId, requestBody);
}
