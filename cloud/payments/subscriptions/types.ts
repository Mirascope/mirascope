/**
 * @fileoverview Types and constants for subscription plan tiers.
 *
 * This is the source of truth for plan tier definitions, ordering, and types.
 * Used throughout the application for plan-related logic.
 */

/** Available pricing plan tier values (source of truth) */
export const PLAN_TIERS = ["free", "pro", "team"] as const;

/** Pricing plan tier types */
export type PlanTier = (typeof PLAN_TIERS)[number];

/**
 * Plan tier ordering for upgrade/downgrade determination.
 * Higher values = higher tier.
 */
export const PLAN_TIER_ORDER: Record<PlanTier, number> = {
  free: 0,
  pro: 1,
  team: 2,
} as const;
