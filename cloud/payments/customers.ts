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
import { Subscriptions } from "@/payments/subscriptions";

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
  stripeCustomerId: string;
  /** Stripe subscription ID */
  subscriptionId: string;
}

/**
 * Parameters for updating a Stripe customer.
 */
export interface UpdateCustomerParams {
  /** Stripe customer ID */
  stripeCustomerId: string;
  /** Updated organization name (optional) */
  organizationName?: string;
  /** Updated organization slug (optional) */
  organizationSlug?: string;
}

/**
 * Customers service for managing Stripe customers.
 *
 * Provides methods for creating, updating, and deleting Stripe customers.
 * Subscription management is handled through the nested `subscriptions` property.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const payments = yield* Payments;
 *
 *   // Customer operations
 *   const result = yield* payments.customers.create({
 *     organizationId: "org_123",
 *     organizationName: "Acme Corp",
 *     organizationSlug: "acme-corp",
 *     email: "billing@acme.com",
 *   });
 *
 *   // Subscription operations
 *   const details = yield* payments.customers.subscriptions.get(result.stripeCustomerId);
 * });
 * ```
 */
export class Customers {
  // Test property for coverage - a nested config object
  readonly config = {
    version: "1.0.0",
  };

  /** Subscriptions service for managing customer subscriptions */
  readonly subscriptions: Subscriptions;

  constructor(subscriptions: Subscriptions) {
    this.subscriptions = subscriptions;
  }
  /**
   * Creates a Stripe customer and subscription for an organization.
   *
   * The price IDs for the subscription are automatically read from the Stripe
   * service configuration.
   *
   * This is a two-step process:
   * 1. Create a Stripe customer with the organization's details
   * 2. Create a subscription with multiple items:
   *    - Router usage-based credits (routerPriceId)
   *    - Cloud Free tier subscription (cloudFreePriceId)
   *    - Cloud Spans usage-based billing (cloudSpansPriceId)
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

      // Create subscription with multiple items:
      // - Router credits (metered)
      // - Cloud Free tier (subscription)
      // - Cloud Spans (metered with graduated tiers)
      const subscription = yield* stripe.subscriptions.create({
        customer: customer.id,
        items: [
          { price: stripe.config.routerPriceId },
          { price: stripe.config.cloudFreePriceId },
          { price: stripe.config.cloudSpansPriceId },
        ],
        metadata: {
          organizationId: params.organizationId,
          organizationName: params.organizationName,
        },
      });

      return {
        stripeCustomerId: customer.id,
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
        const customer = yield* stripe.customers.retrieve(
          params.stripeCustomerId,
        );
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
        yield* stripe.customers.update(params.stripeCustomerId, updateData);
      }
    });
  }

  /**
   * Deletes a Stripe customer (and all associated subscriptions).
   *
   * Use this for cleanup when organization creation fails after Stripe customer
   * has been created.
   *
   * @param stripeCustomerId - The Stripe customer ID to delete
   * @returns Effect that succeeds when customer is deleted
   * @throws StripeError - If deletion fails
   */
  delete(stripeCustomerId: string): Effect.Effect<void, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;
      yield* stripe.customers.del(stripeCustomerId);
    });
  }
}
