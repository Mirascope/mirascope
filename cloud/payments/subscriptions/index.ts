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
export {
  PLAN_TIERS,
  PLAN_TIER_ORDER,
  type PlanTier,
} from "@/payments/subscriptions/types";
export {
  PLAN_LIMITS,
  type PlanLimits,
} from "@/payments/subscriptions/plan-limits";

// Export services
// Note: Subscriptions service imports database code (DrizzleORM/pg).
// Client-side code should import types directly from @/payments/subscriptions/types
// to avoid pulling in Node.js-only dependencies.
export {
  Subscriptions,
  type SubscriptionDetails,
} from "@/payments/subscriptions/service";
