/**
 * @fileoverview Subscriptions service for managing Stripe subscriptions.
 *
 * Provides an Effect-native service for managing subscription plans and billing.
 * This service handles subscription retrieval, updates, previews, and cancellations.
 */

import { Effect } from "effect";
import type StripeAPI from "stripe";
import { DrizzleORM } from "@/db/client";
import { organizations } from "@/db/schema/organizations";
import { eq } from "drizzle-orm";
import { Stripe as StripeService, type StripeConfig } from "@/payments/client";
import {
  DatabaseError,
  NotFoundError,
  StripeError,
  SubscriptionPastDueError,
} from "@/errors";
import { type PlanTier, PLAN_TIER_ORDER } from "@/payments/subscriptions/types";
import { PLAN_LIMITS, type PlanLimits } from "./plan-limits";

/**
 * Subscription details for an organization.
 */
export interface SubscriptionDetails {
  /** Current subscription ID */
  subscriptionId: string;
  /** Current plan tier */
  currentPlan: PlanTier;
  /** Subscription status */
  status: StripeAPI.Subscription.Status;
  /** Current billing period end date */
  currentPeriodEnd: Date;
  /** Whether customer has a default payment method */
  hasPaymentMethod: boolean;
  /** Payment method details (if any) */
  paymentMethod?: {
    brand: string;
    last4: string;
    expMonth: number;
    expYear: number;
  };
  /** Scheduled plan change details (if any) */
  scheduledChange?: {
    targetPlan: PlanTier;
    effectiveDate: Date;
    scheduleId: string;
  };
}

/**
 * Parameters for previewing a subscription change.
 */
export interface PreviewSubscriptionChangeParams {
  /** Stripe customer ID */
  stripeCustomerId: string;
  /** Target plan tier */
  targetPlan: PlanTier;
}

/**
 * Preview of a subscription change.
 */
export interface SubscriptionChangePreview {
  /** Whether this is an upgrade (true) or downgrade (false) */
  isUpgrade: boolean;
  /** Prorated amount to be charged immediately (for upgrades), in dollars */
  proratedAmountInDollars: number;
  /** Next billing date */
  nextBillingDate: Date;
  /** New recurring amount per billing period, in dollars */
  recurringAmountInDollars: number;
}

/**
 * Parameters for updating a subscription.
 */
export interface UpdateSubscriptionParams {
  /** Stripe customer ID */
  stripeCustomerId: string;
  /** Target plan tier */
  targetPlan: PlanTier;
}

/**
 * Result of updating a subscription.
 */
export interface UpdateSubscriptionResult {
  /** Whether payment is required from the frontend */
  requiresPayment: boolean;
  /** Client secret for payment confirmation (if requiresPayment is true) */
  clientSecret?: string;
  /** Scheduled change date (for downgrades) */
  scheduledFor?: Date;
  /** Schedule ID (for downgrades) */
  scheduleId?: string;
}

/**
 * Subscriptions service for managing Stripe subscription plans.
 *
 * This service specifically manages the Cloud plan tier (Free/Pro/Team)
 * within the customer's subscription. Each customer has ONE Stripe
 * subscription containing multiple items:
 * - Router usage-based credits (routerPriceId)
 * - Cloud plan tier (cloudFreePriceId/cloudProPriceId/cloudTeamPriceId)
 * - Cloud Spans usage-based billing (cloudSpansPriceId)
 *
 * The methods in this service focus on managing transitions between
 * plan tiers (upgrades/downgrades) and retrieving plan-specific details.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const payments = yield* Payments;
 *
 *   const details = yield* payments.customers.subscriptions.get("cus_123");
 *   console.log(details.currentPlan); // "free"
 * });
 * ```
 */
export class Subscriptions {
  // Note: Plan tier ordering is now imported from @/payments/subscriptions

  /**
   * Gets the current plan tier for an organization.
   *
   * Fetches the organization's Stripe customer ID from the database,
   * then queries Stripe subscriptions to determine the active plan tier.
   *
   * @param organizationId - The organization UUID
   * @returns The current plan tier ("free" | "pro" | "team")
   * @throws NotFoundError - If organization or subscription not found
   * @throws StripeError - If Stripe API call fails
   * @throws SqlError.SqlError - If database query fails
   */
  getPlan(
    organizationId: string,
  ): Effect.Effect<
    PlanTier,
    NotFoundError | StripeError | DatabaseError,
    StripeService | DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const db = yield* DrizzleORM;

      // Get organization's Stripe customer ID
      const [org] = yield* db
        .select({ stripeCustomerId: organizations.stripeCustomerId })
        .from(organizations)
        .where(eq(organizations.id, organizationId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to fetch organization for plan",
                cause: e,
              }),
          ),
        );

      if (!org) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Organization not found: ${organizationId}`,
            resource: "organizations",
          }),
        );
      }

      // Get subscription details from Stripe
      const subscriptionDetails = yield* this.get(org.stripeCustomerId);

      return subscriptionDetails.currentPlan;
    });
  }

  /**
   * Gets the plan limits for a specific plan tier.
   *
   * This is a pure function that returns the limits constant for the given tier.
   * No side effects or database/API calls.
   *
   * @param planTier - The plan tier to get limits for
   * @returns The limits for the specified plan tier
   */
  getPlanLimits(planTier: PlanTier): Effect.Effect<PlanLimits> {
    return Effect.succeed(PLAN_LIMITS[planTier]);
  }

  /**
   * Determines plan tier from Stripe price ID.
   */
  private getPlanFromPriceId(priceId: string, config: StripeConfig): PlanTier {
    if (priceId === config.cloudProPriceId) return "pro";
    if (priceId === config.cloudTeamPriceId) return "team";
    return "free"; // default fallback
  }

  /**
   * Gets price ID from plan tier.
   */
  private getPriceIdFromPlan(plan: PlanTier, config: StripeConfig): string {
    if (plan === "free") return config.cloudFreePriceId;
    if (plan === "pro") return config.cloudProPriceId;
    return config.cloudTeamPriceId;
  }

  /**
   * Finds the plan subscription item from subscription items.
   */
  private findPlanItem(
    items: Array<{ id: string; price: { id: string } }>,
    config: StripeConfig,
  ): { id: string; price: { id: string } } | undefined {
    return items.find((item) => {
      const priceId = item.price.id;
      return (
        priceId === config.cloudFreePriceId ||
        priceId === config.cloudProPriceId ||
        priceId === config.cloudTeamPriceId
      );
    });
  }

  /**
   * Determines if a plan change is an upgrade.
   */
  private isUpgrade(currentPlan: PlanTier, targetPlan: PlanTier): boolean {
    return PLAN_TIER_ORDER[targetPlan] > PLAN_TIER_ORDER[currentPlan];
  }

  /**
   * Gets the active or past_due subscription for a customer.
   *
   * Under normal circumstances, each customer has exactly ONE subscription
   * (containing multiple items: Router, Plan, Spans). This method fetches
   * all subscriptions and filters for active or past_due status.
   *
   * Defensively handles edge cases: if multiple active subscriptions exist
   * (data inconsistency), returns the first one found (Stripe returns them
   * sorted by created date descending, so most recent first).
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @returns Active subscription
   * @throws NotFoundError - If no active subscription found
   * @throws StripeError - If Stripe API calls fail
   */
  getActiveSubscription(
    stripeCustomerId: string,
  ): Effect.Effect<
    StripeAPI.Subscription,
    StripeError | NotFoundError,
    StripeService
  > {
    return Effect.gen(function* () {
      const stripe = yield* StripeService;

      // Get subscriptions for customer (Stripe returns them sorted by created date descending)
      const subscriptions = yield* stripe.subscriptions.list({
        customer: stripeCustomerId,
      });

      // Filter for active or past_due subscriptions (past_due means payment is required)
      const validSubscription = subscriptions.data.find(
        (sub) => sub.status === "active" || sub.status === "past_due",
      );

      if (!validSubscription) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "No active subscription found for customer",
            resource: stripeCustomerId,
          }),
        );
      }

      return validSubscription;
    });
  }

  /**
   * Gets payment method details for a customer.
   *
   * Checks for payment methods in priority order:
   * 1. Subscription's default payment method (highest priority)
   * 2. Customer's invoice settings default payment method
   * 3. First payment method in customer's payment methods list (most recent)
   *
   * This prioritization ensures we use explicitly set defaults before
   * falling back to the most recently added payment method.
   *
   * Fetches all payment methods to handle edge case of multiple payment methods.
   * If multiple exist, we use the first one (most recent) after checking defaults.
   *
   * @param subscription - The subscription to check
   * @param customer - The customer to check
   * @param stripeCustomerId - The Stripe customer ID (for listing payment methods)
   * @returns Payment method status and details
   * @throws StripeError - If Stripe API calls fail
   */
  private getPaymentMethodDetails(
    subscription: StripeAPI.Subscription,
    customer: StripeAPI.Customer | StripeAPI.DeletedCustomer,
    stripeCustomerId: string,
  ): Effect.Effect<
    {
      hasPaymentMethod: boolean;
      paymentMethod?: SubscriptionDetails["paymentMethod"];
    },
    StripeError,
    StripeService
  > {
    return Effect.gen(function* () {
      const stripe = yield* StripeService;

      // List payment methods to see if customer has any on file (sorted by created date descending)
      const paymentMethods = yield* stripe.paymentMethods.list({
        customer: stripeCustomerId,
        type: "card",
      });

      // Check for payment method on subscription, customer, or in payment methods list
      const hasPaymentMethod =
        (subscription.default_payment_method !== null &&
          subscription.default_payment_method !== undefined) ||
        ("invoice_settings" in customer &&
          customer.invoice_settings?.default_payment_method !== null) ||
        paymentMethods.data.length > 0;

      // Get payment method details if available
      let paymentMethodDetails:
        | SubscriptionDetails["paymentMethod"]
        | undefined;

      if (hasPaymentMethod) {
        // Determine which payment method ID to use
        let paymentMethodId: string | null = null;

        if (
          subscription.default_payment_method &&
          typeof subscription.default_payment_method === "string"
        ) {
          paymentMethodId = subscription.default_payment_method;
        } else if (
          "invoice_settings" in customer &&
          customer.invoice_settings?.default_payment_method &&
          typeof customer.invoice_settings.default_payment_method === "string"
        ) {
          paymentMethodId = customer.invoice_settings.default_payment_method;
        } else if (paymentMethods.data.length > 0) {
          paymentMethodId = paymentMethods.data[0].id;
        }

        // Retrieve full payment method details
        if (paymentMethodId) {
          const paymentMethod =
            yield* stripe.paymentMethods.retrieve(paymentMethodId);

          /* v8 ignore start -- Defensive: card payment methods should always have card details */
          if (paymentMethod.card) {
            paymentMethodDetails = {
              brand: paymentMethod.card.brand,
              last4: paymentMethod.card.last4,
              expMonth: paymentMethod.card.exp_month,
              expYear: paymentMethod.card.exp_year,
            };
          }
          /* v8 ignore stop */
        }
      }

      return {
        hasPaymentMethod,
        paymentMethod: paymentMethodDetails,
      };
    });
  }

  /**
   * Gets scheduled subscription change for a customer.
   *
   * Fetches all subscription schedules for the customer and filters for active schedules.
   * If multiple active schedules exist, uses the most recent one (Stripe returns them
   * sorted by created date descending).
   *
   * Returns undefined if no scheduled changes are found.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @param config - Stripe configuration for price ID lookups
   * @returns Scheduled change details or undefined
   * @throws StripeError - If Stripe API calls fail
   */
  private getScheduledChange(
    stripeCustomerId: string,
    config: StripeConfig,
  ): Effect.Effect<
    SubscriptionDetails["scheduledChange"],
    StripeError,
    StripeService
  > {
    return Effect.gen(this, function* () {
      const stripe = yield* StripeService;

      // Get subscription schedules for customer (sorted by created date descending)
      const schedules = yield* stripe.subscriptionSchedules.list({
        customer: stripeCustomerId,
      });

      // Filter for active schedules
      const activeSchedule = schedules.data.find(
        (schedule) => schedule.status === "active",
      );

      if (!activeSchedule) {
        return undefined;
      }

      // Check if schedule has multiple phases (indicating a scheduled change)
      if (!activeSchedule.phases || activeSchedule.phases.length <= 1) {
        return undefined;
      }

      const nextPhase = activeSchedule.phases[1];
      const nextPlanItem = nextPhase.items.find((item) => {
        const priceId =
          typeof item.price === "string" ? item.price : item.price.id;
        return (
          priceId === config.cloudFreePriceId ||
          priceId === config.cloudProPriceId ||
          priceId === config.cloudTeamPriceId
        );
      });

      /* v8 ignore start -- Defensive: schedule phases should contain a known plan price */
      if (!nextPlanItem) {
        return undefined;
      }
      /* v8 ignore stop */

      return {
        targetPlan: this.getPlanFromPriceId(
          typeof nextPlanItem.price === "string"
            ? nextPlanItem.price
            : nextPlanItem.price.id,
          config,
        ),
        effectiveDate: new Date(nextPhase.start_date * 1000),
        scheduleId: activeSchedule.id,
      };
    });
  }

  /**
   * Gets subscription details for a customer.
   *
   * Retrieves the active subscription and determines the current plan tier,
   * billing period, payment method status, and any scheduled changes.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @returns Subscription details including current plan and billing info
   * @throws NotFoundError - If no active subscription found
   * @throws StripeError - If Stripe API calls fail
   */
  get(
    stripeCustomerId: string,
  ): Effect.Effect<
    SubscriptionDetails,
    StripeError | NotFoundError,
    StripeService
  > {
    return Effect.gen(this, function* () {
      const stripe = yield* StripeService;

      // Get the active subscription for the customer
      const subscription = yield* this.getActiveSubscription(stripeCustomerId);

      // Get customer details
      const customer = yield* stripe.customers.retrieve(stripeCustomerId);

      // Get payment method details
      const { hasPaymentMethod, paymentMethod } =
        yield* this.getPaymentMethodDetails(
          subscription,
          customer,
          stripeCustomerId,
        );

      // Find the cloud plan price item
      const planItem = this.findPlanItem(
        subscription.items.data,
        stripe.config,
      );

      if (!planItem) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Could not determine plan tier from subscription items",
            resource: stripeCustomerId,
          }),
        );
      }

      const currentPlan = this.getPlanFromPriceId(
        planItem.price.id,
        stripe.config,
      );

      // Get scheduled change details
      const scheduledChange = yield* this.getScheduledChange(
        stripeCustomerId,
        stripe.config,
      );

      return {
        subscriptionId: subscription.id,
        currentPlan,
        status: subscription.status,
        currentPeriodEnd: new Date(subscription.current_period_end * 1000),
        hasPaymentMethod,
        paymentMethod,
        scheduledChange,
      };
    });
  }

  /**
   * Previews a subscription change to calculate prorated amount.
   *
   * Uses Stripe's upcoming invoice API to preview the charges that would
   * be applied for a plan change.
   *
   * @param params - Customer ID and target plan
   * @returns Preview with proration details and billing info
   * @throws NotFoundError - If no active subscription found
   * @throws StripeError - If preview fails
   */
  previewChange({
    stripeCustomerId,
    targetPlan,
  }: PreviewSubscriptionChangeParams): Effect.Effect<
    SubscriptionChangePreview,
    StripeError | NotFoundError,
    StripeService
  > {
    return Effect.gen(this, function* () {
      const stripe = yield* StripeService;

      // Get current subscription
      const subscriptionDetails = yield* this.get(stripeCustomerId);

      // Determine if upgrade or downgrade
      const isUpgrade = this.isUpgrade(
        subscriptionDetails.currentPlan,
        targetPlan,
      );

      // Get target price ID
      const targetPriceId = this.getPriceIdFromPlan(targetPlan, stripe.config);

      // Retrieve subscription
      const subscription = yield* stripe.subscriptions.retrieve(
        subscriptionDetails.subscriptionId,
      );

      // Find the current plan item
      const currentPlanItem = this.findPlanItem(
        subscription.items.data,
        stripe.config,
      );

      if (!currentPlanItem) {
        return yield* Effect.fail(
          new StripeError({
            message: "Could not find current plan item",
          }),
        );
      }

      // Get the target price to show recurring amount
      const targetPrice = yield* stripe.prices.retrieve(targetPriceId);

      // Preview invoice with the change to get prorated amount
      const upcomingInvoice = yield* stripe.invoices.retrieveUpcoming({
        customer: stripeCustomerId,
        subscription: subscriptionDetails.subscriptionId,
        subscription_items: [
          {
            id: currentPlanItem.id,
            price: targetPriceId,
          },
        ],
        subscription_proration_behavior: isUpgrade ? "always_invoice" : "none",
      });

      return {
        isUpgrade,
        proratedAmountInDollars: upcomingInvoice.amount_due / 100,
        nextBillingDate: new Date(upcomingInvoice.period_end * 1000),
        /* v8 ignore next 1 -- Defensive: subscription prices should always have unit_amount */
        recurringAmountInDollars: (targetPrice.unit_amount || 0) / 100,
      };
    });
  }

  /**
   * Updates a customer's subscription to a new plan.
   *
   * Handles both upgrades and downgrades:
   * - Upgrades: Immediate change with proration, may require payment
   * - Downgrades: Scheduled at period end, no refunds
   *
   * @param params - Customer ID and target plan
   * @returns Update result with payment requirements or scheduled change info
   * @throws NotFoundError - If no active subscription found
   * @throws StripeError - If update fails
   */
  update({
    stripeCustomerId,
    targetPlan,
  }: UpdateSubscriptionParams): Effect.Effect<
    UpdateSubscriptionResult,
    StripeError | NotFoundError,
    StripeService
  > {
    return Effect.gen(this, function* () {
      const stripe = yield* StripeService;

      // Get current subscription
      const subscriptionDetails = yield* this.get(stripeCustomerId);

      // Determine if upgrade or downgrade
      const isUpgrade = this.isUpgrade(
        subscriptionDetails.currentPlan,
        targetPlan,
      );

      // Get target price ID
      const targetPriceId = this.getPriceIdFromPlan(targetPlan, stripe.config);

      if (isUpgrade) {
        return yield* this.upgrade(
          subscriptionDetails.subscriptionId,
          targetPriceId,
        );
      } else {
        return yield* this.downgrade(
          subscriptionDetails.subscriptionId,
          targetPriceId,
        );
      }
    });
  }

  /**
   * Processes subscription upgrade with immediate proration.
   */
  private upgrade(
    subscriptionId: string,
    targetPriceId: string,
  ): Effect.Effect<UpdateSubscriptionResult, StripeError, StripeService> {
    return Effect.gen(this, function* () {
      const stripe = yield* StripeService;

      // Retrieve subscription
      const subscription = yield* stripe.subscriptions.retrieve(subscriptionId);

      // Find the current plan item
      const currentPlanItem = this.findPlanItem(
        subscription.items.data,
        stripe.config,
      );

      if (!currentPlanItem) {
        return yield* Effect.fail(
          new StripeError({
            message: "Could not find current plan item",
          }),
        );
      }

      // Update subscription with new price
      const updatedSubscription = yield* stripe.subscriptions.update(
        subscriptionId,
        {
          items: [
            {
              id: currentPlanItem.id,
              price: targetPriceId,
            },
          ],
          proration_behavior: "always_invoice",
          payment_behavior: "default_incomplete",
          expand: ["latest_invoice.payment_intent"],
        },
      );

      // Check if payment is required
      if (
        updatedSubscription.latest_invoice &&
        typeof updatedSubscription.latest_invoice === "object"
      ) {
        const invoice = updatedSubscription.latest_invoice;
        if (
          invoice.payment_intent &&
          typeof invoice.payment_intent === "object"
        ) {
          const paymentIntent = invoice.payment_intent;
          const requiresPaymentStatuses = [
            "requires_payment_method",
            "requires_confirmation",
            "requires_action",
          ];
          if (
            requiresPaymentStatuses.includes(paymentIntent.status) &&
            paymentIntent.client_secret
          ) {
            return {
              requiresPayment: true,
              clientSecret: paymentIntent.client_secret,
            };
          }
        }
      }

      return {
        requiresPayment: false,
      };
    });
  }

  /**
   * Processes subscription downgrade by scheduling change at period end.
   *
   * Releases any existing schedule before creating a new one to ensure
   * only one scheduled change exists at a time. This prevents conflicts
   * and makes the scheduled change behavior predictable.
   */
  private downgrade(
    subscriptionId: string,
    targetPriceId: string,
  ): Effect.Effect<UpdateSubscriptionResult, StripeError, StripeService> {
    return Effect.gen(this, function* () {
      const stripe = yield* StripeService;

      // Retrieve subscription
      const subscription = yield* stripe.subscriptions.retrieve(
        subscriptionId,
        {
          expand: ["schedule"],
        },
      );

      // Build current and new subscription items
      const currentItems = subscription.items.data.map((item) => {
        const itemData: { price: string; quantity?: number } = {
          price: item.price.id,
        };
        if (item.quantity !== null && item.quantity !== undefined) {
          itemData.quantity = item.quantity;
        }
        return itemData;
      });

      // Replace the plan item with the target plan
      const newItems = currentItems.map((item) => {
        const isPlanItem =
          item.price === stripe.config.cloudFreePriceId ||
          item.price === stripe.config.cloudProPriceId ||
          item.price === stripe.config.cloudTeamPriceId;

        if (isPlanItem) {
          return {
            price: targetPriceId,
            ...(item.quantity && { quantity: item.quantity }),
          };
        }
        return item;
      });

      // Release existing schedule if present
      if (subscription.schedule) {
        const existingScheduleId =
          typeof subscription.schedule === "string"
            ? subscription.schedule
            : subscription.schedule.id;
        yield* stripe.subscriptionSchedules.release(existingScheduleId);
      }

      // Create new subscription schedule
      const schedule = yield* stripe.subscriptionSchedules.create({
        from_subscription: subscriptionId,
      });

      // Update schedule with two phases: current and future
      const updatedSchedule = yield* stripe.subscriptionSchedules.update(
        schedule.id,
        {
          phases: [
            {
              items: currentItems,
              start_date: subscription.current_period_start,
              end_date: subscription.current_period_end,
            },
            {
              items: newItems,
              start_date: subscription.current_period_end,
              proration_behavior: "none",
            },
          ],
        },
      );

      return {
        requiresPayment: false,
        scheduledFor: new Date(subscription.current_period_end * 1000),
        scheduleId: updatedSchedule.id,
      };
    });
  }

  /**
   * Cancels a scheduled subscription downgrade.
   *
   * Releases the subscription schedule, reverting to the normal subscription.
   *
   * @param validateStripeConfigustomerId - The Stripe customer ID
   * @returns Effect that succeeds when schedule is cancelled
   * @throws StripeError - If cancellation fails
   */
  cancelScheduledDowngrade(
    stripeCustomerId: string,
  ): Effect.Effect<void, StripeError, StripeService> {
    return Effect.gen(function* () {
      const stripe = yield* StripeService;

      // Find active schedule
      const schedules = yield* stripe.subscriptionSchedules.list({
        customer: stripeCustomerId,
        limit: 1,
      });

      if (schedules.data.length === 0) {
        return yield* Effect.fail(
          new StripeError({
            message: "No scheduled changes found",
          }),
        );
      }

      // Release the schedule
      yield* stripe.subscriptionSchedules.release(schedules.data[0].id);
    });
  }

  /**
   * Cancels all active subscriptions for a customer.
   *
   * Used when deleting an organization to properly clean up billing.
   * Cancels subscriptions immediately without proration.
   *
   * Throws SubscriptionPastDueError if any past_due subscriptions exist,
   * as these represent outstanding debt that must be resolved before
   * allowing cancellation. This prevents users from deleting their org
   * while owing money, which would cause them to accrue more debt without
   * service access.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @returns Effect that succeeds when all active subscriptions are cancelled
   * @throws SubscriptionPastDueError - If any past_due subscriptions exist
   * @throws StripeError - If cancellation fails
   */
  cancel(
    stripeCustomerId: string,
  ): Effect.Effect<
    void,
    StripeError | SubscriptionPastDueError,
    StripeService
  > {
    return Effect.gen(function* () {
      const stripe = yield* StripeService;

      // List all subscriptions for the customer
      const allSubscriptions = yield* stripe.subscriptions.list({
        customer: stripeCustomerId,
      });

      // Check for past_due subscriptions (outstanding debt)
      const pastDueSubscriptions = allSubscriptions.data.filter(
        (sub) => sub.status === "past_due",
      );

      if (pastDueSubscriptions.length > 0) {
        return yield* Effect.fail(
          // TODO: update organization deletion flow to handle this gracefully,
          // ideally with a "settle up" flow where a user can pay their past_due
          // invoice as part of deletion.
          new SubscriptionPastDueError({
            message: `Cannot cancel subscriptions - ${pastDueSubscriptions.length} subscription(s) have past_due payments that must be resolved first`,
            stripeCustomerId,
            pastDueSubscriptionIds: pastDueSubscriptions.map((sub) => sub.id),
          }),
        );
      }

      // Filter for active subscriptions only
      const activeSubscriptions = allSubscriptions.data.filter(
        (sub) => sub.status === "active",
      );

      // Cancel each active subscription
      for (const subscription of activeSubscriptions) {
        yield* stripe.subscriptions.cancel(subscription.id);
      }
    });
  }
}
