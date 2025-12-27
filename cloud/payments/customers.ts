/**
 * @fileoverview Customers service for managing Stripe customers.
 *
 * Provides an Effect-native service for creating and managing Stripe customers
 * that represent organizations in the billing system. This service wraps Stripe
 * operations and provides a clean interface for customer management.
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
 * Parameters for updating a Stripe customer.
 */
export interface UpdateCustomerParams {
  /** Stripe customer ID */
  customerId: string;
  /** Updated organization name (optional) */
  organizationName?: string;
  /** Updated organization slug (optional) */
  organizationSlug?: string;
}

/**
 * Customers service for managing Stripe customers.
 *
 * Provides methods for creating, updating, and deleting Stripe customers,
 * as well as managing subscriptions and retrieving credit balances.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const payments = yield* Payments;
 *
 *   const result = yield* payments.customers.create({
 *     organizationId: "org_123",
 *     organizationName: "Acme Corp",
 *     organizationSlug: "acme-corp",
 *     email: "billing@acme.com",
 *   });
 *
 *   console.log(result.customerId); // "cus_123"
 * });
 * ```
 */
export class Customers {
  // Test property for coverage - a nested config object
  readonly config = {
    version: "1.0.0",
  };
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
   */
  create(
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
   * Updates a Stripe customer's name and metadata to match organization changes.
   *
   * Updates both the customer's display name and metadata fields when organization
   * details change. This ensures Stripe records stay in sync with the organization.
   *
   * @param params - Customer ID and optional organization details to update
   * @returns Effect that succeeds when customer is updated
   * @throws StripeError - If update fails
   */
  update(
    params: UpdateCustomerParams,
  ): Effect.Effect<void, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      // Build update object with name and metadata
      const updateData: {
        name?: string;
        metadata?: Record<string, string>;
      } = {};

      // Update name if provided
      if (params.organizationName !== undefined) {
        updateData.name = params.organizationName;
      }

      // Update metadata if any org details changed
      if (
        params.organizationName !== undefined ||
        params.organizationSlug !== undefined
      ) {
        // Fetch current metadata to preserve organizationId
        const customer = yield* stripe.customers.retrieve(params.customerId);
        const currentMetadata = "metadata" in customer ? customer.metadata : {};

        updateData.metadata = {
          ...currentMetadata,
          ...(params.organizationName !== undefined && {
            organizationName: params.organizationName,
          }),
          ...(params.organizationSlug !== undefined && {
            organizationSlug: params.organizationSlug,
          }),
        };
      }

      // Only update if there's something to change
      if (Object.keys(updateData).length > 0) {
        yield* stripe.customers.update(params.customerId, updateData);
      }
    });
  }

  /**
   * Cancels all active subscriptions for a Stripe customer.
   *
   * Used when deleting an organization to properly clean up billing.
   * Cancels subscriptions immediately without proration.
   *
   * @param customerId - The Stripe customer ID
   * @returns Effect that succeeds when all subscriptions are cancelled
   * @throws StripeError - If cancellation fails
   */
  cancelSubscriptions(
    customerId: string,
  ): Effect.Effect<void, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      // List all active subscriptions for the customer
      const subscriptions = yield* stripe.subscriptions.list({
        customer: customerId,
        status: "active",
      });

      // Cancel each subscription immediately
      for (const subscription of subscriptions.data) {
        yield* stripe.subscriptions.cancel(subscription.id);
      }
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
   */
  delete(customerId: string): Effect.Effect<void, StripeError, Stripe> {
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
   * grants that explicitly include the router price ID in their applicability
   * scope.
   *
   * @param customerId - The Stripe customer ID
   * @returns The router credit balance in dollars (e.g., 10.00 for $10 credit)
   * @throws StripeError - If API call fails
   */
  getBalance(customerId: string): Effect.Effect<number, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      const credit_grants = yield* stripe.billing.creditGrants.list({
        customer: customerId,
      });

      let totalCredits = 0;

      for (const grant of credit_grants.data) {
        if (!grant.amount.monetary) continue;

        const config = grant.applicability_config;
        if (
          !config.scope ||
          !config.scope.prices?.some(
            (price) => price.id === stripe.config.routerPriceId,
          )
        )
          continue;

        const { value, currency } = grant.amount.monetary;
        if (currency === "usd") {
          totalCredits += value / 100;
        }
      }

      return totalCredits;
    });
  }
}
