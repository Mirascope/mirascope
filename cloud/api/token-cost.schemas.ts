import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

import { PricingUnavailableError, UnauthorizedError } from "@/errors";

/**
 * Provider schema - accepts any non-empty string.
 * Validation of supported providers happens in the handler with a helpful error message.
 */
export const ProviderSchema = Schema.String.pipe(Schema.nonEmptyString());

export type Provider = typeof ProviderSchema.Type;

/**
 * Token usage input for cost calculation.
 * Matches the TokenUsage type from router/pricing.ts
 */
export const TokenUsageSchema = Schema.Struct({
  inputTokens: Schema.Number.pipe(Schema.nonNegative()),
  outputTokens: Schema.Number.pipe(Schema.nonNegative()),
  cacheReadTokens: Schema.optional(Schema.Number.pipe(Schema.nonNegative())),
  cacheWriteTokens: Schema.optional(Schema.Number.pipe(Schema.nonNegative())),
  /**
   * Provider-specific cache write breakdown for accurate pricing.
   * Example for Anthropic: { ephemeral5m: 100, ephemeral1h: 50 }
   */
  cacheWriteBreakdown: Schema.optional(
    Schema.Record({ key: Schema.String, value: Schema.Number }),
  ),
});

export type TokenUsage = typeof TokenUsageSchema.Type;

/**
 * Request schema for token cost calculation.
 */
export const TokenCostRequestSchema = Schema.Struct({
  provider: ProviderSchema,
  model: Schema.String.pipe(Schema.nonEmptyString()),
  usage: TokenUsageSchema,
  /**
   * Whether the request is routed through Mirascope Router.
   * If true, a 5% gas fee is added to the total cost.
   */
  viaRouter: Schema.optional(Schema.Boolean),
});

export type TokenCostRequest = typeof TokenCostRequestSchema.Type;

/**
 * Response schema with costs in both centi-cents (precision) and dollars (display).
 *
 * Centi-cents: 1 = $0.0001 (10,000 centi-cents = $1.00)
 */
export const TokenCostResponseSchema = Schema.Struct({
  // Centi-cents values for precision (stored as Number for JSON serialization)
  inputCostCenticents: Schema.Number,
  outputCostCenticents: Schema.Number,
  cacheReadCostCenticents: Schema.optional(Schema.Number),
  cacheWriteCostCenticents: Schema.optional(Schema.Number),
  totalCostCenticents: Schema.Number,

  // Dollar amounts for display convenience
  inputCostDollars: Schema.Number,
  outputCostDollars: Schema.Number,
  cacheReadCostDollars: Schema.optional(Schema.Number),
  cacheWriteCostDollars: Schema.optional(Schema.Number),
  totalCostDollars: Schema.Number,
});

export type TokenCostResponse = typeof TokenCostResponseSchema.Type;

/**
 * Token Cost API group.
 *
 * Provides cost calculation for AI provider model usage.
 * Requires API key authentication.
 */
export class TokenCostApi extends HttpApiGroup.make("token-cost").add(
  HttpApiEndpoint.post("calculate", "/token-cost")
    .setPayload(TokenCostRequestSchema)
    .addSuccess(TokenCostResponseSchema)
    .addError(UnauthorizedError, { status: UnauthorizedError.status })
    .addError(PricingUnavailableError, {
      status: PricingUnavailableError.status,
    }),
) {}
