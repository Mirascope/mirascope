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
 * - **Free**: 1 seat, 1 project, 1 claw (basic), $1/week credits, 1M spans/month (hard limit), 100 req/min, 30 day retention
 * - **Pro**: 5 seats, 5 projects, 1 claw (standard-2), $5/week credits, unlimited spans (+$5/M over 1M), 1000 req/min, 90 day retention
 * - **Team**: Unlimited seats/projects, 3 claws (standard-3), $25/week credits, unlimited spans (+$5/M over 1M), 10000 req/min, 180 day retention
 *
 * ## Credit Resets & Burst Limits
 *
 * All credit pools reset **weekly**. Each plan also defines a per-burst credit limit
 * (burst window = 5 hours). Burst limits are set to 20% of the weekly pool, requiring
 * users to spread usage across at least ~5 burst windows (~25 hours) to exhaust their
 * weekly quota.
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
 * console.log(freeLimits.claws); // 1
 *
 * const isUpgrade = PLAN_TIER_ORDER.pro > PLAN_TIER_ORDER.free; // true
 * ```
 */

import type { ClawInstanceType } from "@/claws/deployment/types";

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

export type { ClawInstanceType };

/**
 * Limits for a specific pricing plan.
 *
 * All credit pools reset weekly.
 *
 * @property seats - Maximum number of organization members (Infinity = unlimited)
 * @property projects - Maximum number of projects (Infinity = unlimited)
 * @property spansPerMonth - Monthly span quota (Free: hard limit, Pro/Team: Infinity with graduated pricing)
 * @property apiRequestsPerMinute - API rate limit per organization
 * @property dataRetentionDays - Number of days to retain trace data
 * @property claws - Maximum number of claws
 * @property clawInstanceType - Instance type for claws on this plan
 * @property includedCreditsCenticents - Org-level weekly credit pool (centicents, shared across all claws)
 * @property burstCreditsCenticents - Max credits per 5-hour burst window (centicents)
 * @property estimatedRequestsPerDay - Display-only estimated requests/day
 */
export interface PlanLimits {
  seats: number;
  projects: number;
  spansPerMonth: number;
  apiRequestsPerMinute: number;
  dataRetentionDays: number;
  claws: number;
  clawInstanceType: ClawInstanceType;
  includedCreditsCenticents: number;
  burstCreditsCenticents: number;
  estimatedRequestsPerDay: number;
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
    dataRetentionDays: 30,
    claws: 1,
    clawInstanceType: "basic",
    includedCreditsCenticents: 10_000, // $1/week org pool
    burstCreditsCenticents: 2_000, // $0.20/burst (20% of weekly)
    estimatedRequestsPerDay: 70, // ~500 req/week with haiku
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
    dataRetentionDays: 90,
    claws: 1,
    clawInstanceType: "standard-2",
    includedCreditsCenticents: 500_000, // $5/week org pool
    burstCreditsCenticents: 100_000, // $1/burst (20% of weekly)
    estimatedRequestsPerDay: 50, // ~350 req/week with sonnet
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
    dataRetentionDays: 180,
    claws: 3,
    clawInstanceType: "standard-3",
    includedCreditsCenticents: 2_500_000, // $25/week org pool
    burstCreditsCenticents: 500_000, // $5/burst (20% of weekly)
    estimatedRequestsPerDay: 300, // ~2,100 req/week with sonnet across 3 claws
  },
} as const;

/**
 * Validation error for plan downgrade.
 * Represents a single resource that exceeds the target plan's limit.
 */
export interface DowngradeValidationError {
  resource: "seats" | "projects" | "claws";
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
