/**
 * @fileoverview Subscriptions module for managing Stripe subscription plans and plan limits.
 *
 * This module provides:
 * - Plan tier types and constants (PlanTier, PLAN_TIERS, PLAN_TIER_ORDER)
 * - Plan limits for each tier (PLAN_LIMITS, PlanLimits)
 * - Subscriptions service (Subscriptions) - manages subscription plans via Stripe
 *
 * ## Quick Start
 *
 * ```ts
 * import { Payments } from "@/payments";
 * import { PLAN_LIMITS, type PlanTier } from "@/payments/subscriptions";
 *
 * const program = Effect.gen(function* () {
 *   const payments = yield* Payments;
 *
 *   // Get organization's plan tier
 *   const planTier = yield* payments.customers.subscriptions.getPlan(organizationId);
 *
 *   // Get limits for that tier
 *   const limits = yield* payments.customers.subscriptions.getPlanLimits(planTier);
 *
 *   // Or directly access limits constants
 *   const freeLimits = PLAN_LIMITS.free;
 * });
 * ```
 */

// Export types and constants
// Note: All plan types, constants, and limits are now in @/payments/plans.
// That module is CLIENT-SAFE (no database/server dependencies).
// For convenience, we re-export them here, but client code can import directly from @/payments/plans.
export {
  PLAN_TIERS,
  PLAN_TIER_ORDER,
  PLAN_LIMITS,
  type PlanTier,
  type PlanLimits,
  type DowngradeValidationError,
  type DowngradeValidationResult,
} from "@/payments/plans";

// Export services
// Note: Subscriptions service imports database code (DrizzleORM/pg).
// Client-side code should import from @/payments/plans instead.
export {
  Subscriptions,
  type SubscriptionDetails,
} from "@/payments/subscriptions/service";
