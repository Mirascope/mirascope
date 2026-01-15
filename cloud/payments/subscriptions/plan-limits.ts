/**
 * @fileoverview Plan limit constants for Mirascope Cloud pricing tiers.
 *
 * This module defines the hard limits for each pricing plan (Free, Pro, Team).
 * These constants are the source of truth for all plan enforcement logic.
 *
 * ## Pricing Tiers
 *
 * - **Free**: 1 seat, 1 project, 1M spans/month (hard limit), 100 req/min
 * - **Pro**: 5 seats, 5 projects, 1M spans/month (+$5/M overage), 1000 req/min
 * - **Team**: Unlimited seats/projects, 1M spans/month (+$3/M overage), 10000 req/min
 *
 * ## Usage
 *
 * ```ts
 * import { PLAN_LIMITS, type PlanTier } from "@/payments/subscriptions/plan-limits";
 *
 * const freeLimits = PLAN_LIMITS.free;
 * console.log(freeLimits.seats); // 1
 * console.log(freeLimits.projects); // 1
 * console.log(freeLimits.spansPerMonth); // 1_000_000
 * ```
 */

import type { PlanTier } from "./types";

/**
 * Limits for a specific pricing plan.
 *
 * @property seats - Maximum number of organization members (Infinity = unlimited)
 * @property projects - Maximum number of projects (Infinity = unlimited)
 * @property spansPerMonth - Base span quota per month (overage allowed for Pro/Team)
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
    spansPerMonth: 1_000_000,
    apiRequestsPerMinute: 100,
  },
  pro: {
    seats: 5,
    projects: 5,
    spansPerMonth: 1_000_000, // Overage allowed at $5/M
    apiRequestsPerMinute: 1000,
  },
  team: {
    seats: Infinity, // Unlimited
    projects: Infinity, // Unlimited
    spansPerMonth: 1_000_000, // Overage allowed at $3/M
    apiRequestsPerMinute: 10000,
  },
} as const;
