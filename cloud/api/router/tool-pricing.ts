/**
 * @fileoverview Native tool pricing data for AI providers.
 *
 * Tool pricing is maintained separately from models.dev since it's not
 * included in that dataset. Prices are stored in centi-cents (1 = $0.0001 USD).
 *
 * Pricing sources (as of 2025-01):
 * - Anthropic: https://platform.claude.com/docs/en/about-claude/pricing
 * - Google: https://ai.google.dev/gemini-api/docs/pricing
 * - OpenAI: https://platform.openai.com/docs/pricing
 */

import {
  type CostInCenticents,
  dollarsToCenticents,
} from "@/api/router/cost-utils";

/**
 * Tool types across providers that have separate pricing.
 *
 * Only includes tools with non-token-based pricing.
 * Tools that only charge for tokens (e.g., computer_use, text_editor) are not listed.
 */
export type ToolType =
  // Anthropic server tools
  | "anthropic_web_search"
  | "anthropic_code_execution"
  // Google built-in tools
  | "google_grounding_search"
  // OpenAI built-in tools
  | "openai_web_search"
  | "openai_code_interpreter"
  | "openai_file_search";

/**
 * Pricing configuration for a native tool.
 */
export interface ToolPricing {
  /** Cost per call/request in centi-cents (for per-call tools) */
  costPerCall?: CostInCenticents;
  /** Cost per hour in centi-cents (for time-based tools) */
  costPerHour?: CostInCenticents;
  /** Minimum billing increment in seconds (for time-based tools) */
  minBillingSeconds?: number;
}

/**
 * Hardcoded tool pricing data.
 *
 * These prices are sourced from provider documentation and should be
 * updated when providers change their pricing.
 *
 * Note: Mirascope consumes any provider free tiers (e.g., Anthropic's 1,550 free hours
 * for code execution), so Router users are charged for all usage.
 */
export const TOOL_PRICING: Record<ToolType, ToolPricing> = {
  // Anthropic: Web search - per search request
  // Source: https://platform.claude.com/docs/en/about-claude/pricing
  anthropic_web_search: {
    costPerCall: dollarsToCenticents(0.01), // $10/1,000 searches
  },

  // Anthropic: Code execution - per hour with 5 minute minimum
  // Source: https://platform.claude.com/docs/en/about-claude/pricing
  anthropic_code_execution: {
    costPerHour: dollarsToCenticents(0.05), // $0.05/hour
    minBillingSeconds: 300, // 5 minutes minimum
  },

  // Google: Grounding with Google Search - per query (Gemini 3+)
  // Source: https://ai.google.dev/gemini-api/docs/pricing
  google_grounding_search: {
    costPerCall: dollarsToCenticents(0.014), // $14/1,000 queries
  },

  // OpenAI: Web search - per tool call
  // Source: https://platform.openai.com/docs/pricing
  openai_web_search: {
    costPerCall: dollarsToCenticents(0.01), // $10/1,000 calls
  },

  // OpenAI: Code interpreter - per container hour
  // Source: https://platform.openai.com/docs/pricing
  openai_code_interpreter: {
    costPerHour: dollarsToCenticents(0.03), // $0.03/hour
    minBillingSeconds: 3600, // 1 hour per container session
  },

  // OpenAI: File search - per tool call
  // Note: Also has $0.10/GB/day storage cost which is not tracked per-request
  // Source: https://platform.openai.com/docs/pricing
  openai_file_search: {
    costPerCall: dollarsToCenticents(0.0025), // $2.50/1,000 calls
  },
};

/**
 * Gets pricing for a specific tool type.
 *
 * @param toolType - The tool type to look up
 * @returns Tool pricing or null if not found
 */
export function getToolPricing(toolType: ToolType): ToolPricing | null {
  return TOOL_PRICING[toolType] ?? null;
}

/**
 * Calculates cost for a tool usage.
 *
 * Handles both per-call and time-based pricing, applying minimum billing increments
 * where applicable.
 *
 * @param toolType - The tool type
 * @param callCount - Number of tool invocations
 * @param durationSeconds - Duration in seconds (for time-based tools)
 * @returns Cost in centi-cents, or null if tool type not found
 */
export function calculateToolCost(
  toolType: ToolType,
  callCount: number,
  durationSeconds?: number,
): CostInCenticents | null {
  const pricing = getToolPricing(toolType);
  if (!pricing) {
    return null;
  }

  let cost = 0n;

  // Per-call pricing
  if (pricing.costPerCall && callCount > 0) {
    cost = cost + pricing.costPerCall * BigInt(callCount);
  }

  // Time-based pricing
  if (pricing.costPerHour && (durationSeconds || pricing.minBillingSeconds)) {
    // Apply minimum billing increment
    const billableSeconds = Math.max(
      durationSeconds || 0,
      /* v8 ignore next 1 - minBillingSeconds always defined in tests */
      pricing.minBillingSeconds || 0,
    );
    // Convert to hours and calculate cost (with BigInt math)
    // costPerHour * (billableSeconds / 3600)
    // = costPerHour * billableSeconds / 3600
    const timeCost =
      (pricing.costPerHour * BigInt(billableSeconds)) / BigInt(3600);
    cost = cost + timeCost;
  }

  return cost;
}
