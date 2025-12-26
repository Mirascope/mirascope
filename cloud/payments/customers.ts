/**
 * @fileoverview Stripe customer utilities for organizations.
 *
 * Provides Effect-native utilities for creating and managing Stripe customers
 * that represent organizations in the billing system.
 */

import { Effect } from "effect";
import { Stripe } from "@/payments/client";
import { StripeError } from "@/errors";

/**
 * Parameters for creating a Stripe customer with subscription for an organization.
 */
export interface CreateCustomerParams {
  /** Organization UUID */
  organizationId: string;
  /** Organization name (used as business name in Stripe) */
  organizationName: string;
  /** Organization slug */
  organizationSlug: string;
  /** Primary contact email */
  email: string;
}

/**
 * Result of creating a Stripe customer with subscription.
 */
export interface CreateCustomerResult {
  /** Stripe customer ID */
  customerId: string;
  /** Stripe subscription ID */
  subscriptionId: string;
}

/**
 * Creates a Stripe customer and subscription for an organization.
 *
 * The price ID for the subscription is automatically read from the Stripe
 * service configuration (stripe.config.routerPriceId).
 *
 * This is a two-step process:
 * 1. Create a Stripe customer with the organization's details
 * 2. Create a subscription for usage-based credits using the configured price ID
 *
 * If subscription creation fails, the customer is NOT automatically deleted.
 * Caller is responsible for cleanup on failure.
 *
 * @param params - Organization details for customer and subscription creation
 * @returns Customer and subscription IDs
 * @throws StripeError - If Stripe API calls fail
 *
 * @example
 * ```ts
 * const result = yield* createCustomer({
 *   organizationId: "org_123",
 *   organizationName: "Acme Corp",
 *   organizationSlug: "acme-corp",
 *   email: "billing@acme.com",
 * });
 *
 * console.log(result.customerId); // "cus_123"
 * console.log(result.subscriptionId); // "sub_456"
 * ```
 */
export function createCustomer(
  params: CreateCustomerParams,
): Effect.Effect<CreateCustomerResult, StripeError, Stripe> {
  return Effect.gen(function* () {
    const stripe = yield* Stripe;

    // Create Stripe customer with organization as the business
    const customer = yield* stripe.customers.create({
      email: params.email,
      name: params.organizationName,
      metadata: {
        organizationId: params.organizationId,
        organizationName: params.organizationName,
        organizationSlug: params.organizationSlug,
      },
    });

    // Create subscription for usage-based credits using configured price ID
    const subscription = yield* stripe.subscriptions.create({
      customer: customer.id,
      items: [{ price: stripe.config.routerPriceId }],
      metadata: {
        organizationId: params.organizationId,
        organizationName: params.organizationName,
      },
    });

    return {
      customerId: customer.id,
      subscriptionId: subscription.id,
    };
  });
}

/**
 * Deletes a Stripe customer (and all associated subscriptions).
 *
 * Use this for cleanup when organization creation fails after Stripe customer
 * has been created.
 *
 * @param customerId - The Stripe customer ID to delete
 * @returns Effect that succeeds when customer is deleted
 * @throws StripeError - If deletion fails
 *
 * @example
 * ```ts
 * yield* deleteCustomer("cus_123");
 * ```
 */
export function deleteCustomer(
  customerId: string,
): Effect.Effect<void, StripeError, Stripe> {
  return Effect.gen(function* () {
    const stripe = yield* Stripe;
    yield* stripe.customers.del(customerId);
  });
}

/**
 * Gets the router credit balance for a Stripe customer from billing credit grants.
 *
 * Fetches all credit grants for the customer and filters for those that are
 * applicable to the router price (metered usage-based billing). Only counts
 * grants that either have no scope restrictions or explicitly include the
 * router price ID in their applicability scope.
 *
 * @param customerId - The Stripe customer ID
 * @returns The router credit balance in dollars (e.g., 10.00 for $10 credit)
 * @throws StripeError - If API call fails
 *
 * @example
 * ```ts
 * const balance = yield* getCustomerBalance("cus_123");
 * console.log(balance); // 10.00 (if customer has $10 in router credit grants)
 * ```
 */
export function getCustomerBalance(
  customerId: string,
): Effect.Effect<number, StripeError, Stripe> {
  return Effect.gen(function* () {
    const stripe = yield* Stripe;
    const credit_grants = yield* stripe.billing.creditGrants.list({
      customer: customerId,
    });

    return credit_grants.data
      .filter(
        (grant) =>
          grant.amount.monetary &&
          grant.applicability_config.scope?.prices?.some(
            (price) => price.id === stripe.config.routerPriceId,
          ),
      )
      .map((grant) => grant.amount.monetary!)
      .filter((monetary) => monetary.currency === "usd")
      .reduce((total, monetary) => total + monetary.value / 100, 0);
  });
}
