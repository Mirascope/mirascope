/**
 * @fileoverview Plan definitions, types, and limits for Mirascope Cloud pricing tiers.
 *
 * This module is CLIENT-SAFE and contains no server-only dependencies (no database, no Stripe service).
 * It provides:
 * - Plan tier types and constants (PlanTier, PLAN_TIERS, PLAN_TIER_ORDER)
 * - Plan limits for each tier (PLAN_LIMITS, PlanLimits)
 * - Validation types for plan downgrades (DowngradeValidationError, DowngradeValidationResult)
 *
 * ## Pricing Tiers
 *
 * - **Free**: 1 seat, 1 project, 1M spans/month (hard limit enforced), 100 req/min
 * - **Pro**: 5 seats, 5 projects, unlimited spans (+$5/M over 1M included), 1000 req/min
 * - **Team**: Unlimited seats/projects, unlimited spans (+$5/M over 1M included), 10000 req/min
 *
 * ## Usage
 *
 * ```ts
 * import { PLAN_LIMITS, PLAN_TIER_ORDER, type PlanTier } from "@/payments/plans";
 *
 * const freeLimits = PLAN_LIMITS.free;
 * console.log(freeLimits.seats); // 1
 * console.log(freeLimits.projects); // 1
 * console.log(freeLimits.spansPerMonth); // 1_000_000
 *
 * const isUpgrade = PLAN_TIER_ORDER.pro > PLAN_TIER_ORDER.free; // true
 * ```
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

/**
 * Limits for a specific pricing plan.
 *
 * @property seats - Maximum number of organization members (Infinity = unlimited)
 * @property projects - Maximum number of projects (Infinity = unlimited)
 * @property spansPerMonth - Monthly span quota (Free: hard limit, Pro/Team: Infinity with graduated pricing)
 * @property apiRequestsPerMinute - API rate limit per organization
 */
export interface PlanLimits {
  seats: number;
  projects: number;
  spansPerMonth: number;
  apiRequestsPerMinute: number;
}

/**
 * Plan limit constants for all pricing tiers.
 *
 * This is the authoritative source for plan limits used throughout the application.
 * Update these values to change plan limits across all enforcement points.
 */
export const PLAN_LIMITS: Record<PlanTier, PlanLimits> = {
  free: {
    seats: 1,
    projects: 1,
    spansPerMonth: 1_000_000, // Hard limit enforced - no overage allowed
    apiRequestsPerMinute: 100,
  },
  pro: {
    seats: 5,
    projects: 5,
    // Unlimited spans with graduated pricing via Stripe meter:
    // - First 1M spans included in base price
    // - $5 per additional 1M spans (billed automatically via meter)
    // Set to Infinity since we don't enforce a hard limit
    spansPerMonth: Infinity,
    apiRequestsPerMinute: 1000,
  },
  team: {
    seats: Infinity, // Unlimited
    projects: Infinity, // Unlimited
    // Unlimited spans with graduated pricing via Stripe meter:
    // - First 1M spans included in base price
    // - $5 per additional 1M spans (billed automatically via meter)
    // Set to Infinity since we don't enforce a hard limit
    spansPerMonth: Infinity,
    apiRequestsPerMinute: 10000,
  },
} as const;

/**
 * Validation error for plan downgrade.
 * Represents a single resource that exceeds the target plan's limit.
 */
export interface DowngradeValidationError {
  resource: "seats" | "projects";
  currentUsage: number;
  limit: number;
  message: string;
}

/**
 * Result of plan downgrade validation.
 * Used to determine if a downgrade is allowed and provide detailed feedback.
 */
export interface DowngradeValidationResult {
  canDowngrade: boolean;
  validationErrors: DowngradeValidationError[];
}
