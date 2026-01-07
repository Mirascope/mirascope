/**
 * @fileoverview Cost conversion and formatting utilities.
 *
 * This module defines the core cost type system and conversion utilities.
 * Throughout the codebase, all costs are represented in centi-cents (1/10,000th of a dollar)
 * using BIGINT storage. This provides:
 * - Precision for micro-pricing scenarios (LLM tokens)
 * - Fast, accurate integer arithmetic
 * - No floating-point errors
 *
 * IMPORTANT: Only convert to dollars at display boundaries (UI, logs, etc.)
 */

/**
 * Cost represented in centi-cents (1/10,000th of a dollar).
 *
 * Storage format: BIGINT where 1 = $0.0001 USD
 *
 * Examples:
 * - 10000n centi-cents = $1.00
 * - 1n centi-cent = $0.0001
 * - 12345n centi-cents = $1.2345
 *
 * Use this type for ALL monetary values throughout the system.
 */
export type CostInCenticents = bigint;

/**
 * Number of centi-cents in one dollar.
 */
const CENTICENTS_PER_DOLLAR = 10000n;

/**
 * Converts dollars to centi-cents.
 *
 * @param dollars - Cost in dollars (e.g., 1.2345)
 * @returns Cost in centi-cents as BIGINT (e.g., 12345n)
 *
 * @example
 * ```ts
 * dollarsToCenticents(1.0)     // 10000n
 * dollarsToCenticents(0.0001)  // 1n
 * dollarsToCenticents(1.2345)  // 12345n
 * ```
 */
export function dollarsToCenticents(dollars: number): CostInCenticents {
  // Multiply by 10000 to convert dollars to centi-cents
  // Use Math.round to handle floating-point precision issues
  return BigInt(Math.round(dollars * Number(CENTICENTS_PER_DOLLAR)));
}

/**
 * Converts centi-cents to dollars.
 *
 * IMPORTANT: Use this ONLY for display purposes (UI, logs, debugging).
 * Never use this for business logic or calculations.
 *
 * @param centicents - Cost in centi-cents (e.g., 12345n)
 * @returns Cost in dollars (e.g., 1.2345)
 *
 * @example
 * ```ts
 * centicentsToDollars(10000n)  // 1.0
 * centicentsToDollars(1n)      // 0.0001
 * centicentsToDollars(12345n)  // 1.2345
 * ```
 */
export function centicentsToDollars(centicents: CostInCenticents): number {
  return Number(centicents) / Number(CENTICENTS_PER_DOLLAR);
}

/**
 * Formats a cost in centi-cents as a dollar string for display.
 *
 * @param centicents - Cost in centi-cents
 * @returns Formatted string (e.g., "$1.2345")
 *
 * @example
 * ```ts
 * formatCostForDisplay(10000n)  // "$1.0000"
 * formatCostForDisplay(1n)      // "$0.0001"
 * formatCostForDisplay(12345n)  // "$1.2345"
 * ```
 */
export function formatCostForDisplay(centicents: CostInCenticents): string {
  const dollars = centicentsToDollars(centicents);
  return `$${dollars.toFixed(4)}`;
}
