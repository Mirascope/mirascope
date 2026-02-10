/**
 * @fileoverview Payment Intent service for managing Stripe PaymentIntents.
 *
 * Provides an Effect-native service for creating PaymentIntents to collect
 * payment information via embedded Stripe Elements in the application.
 */

import { Effect } from "effect";

import { StripeError } from "@/errors";
import { Stripe } from "@/payments/client";

/**
 * Parameters for creating a router credit purchase PaymentIntent.
 */
export interface CreateRouterCreditsPurchaseIntentParams {
  /** Stripe customer ID */
  stripeCustomerId: string;
  /** Credit amount in dollars (e.g., 50 for $50) */
  amountInDollars: number;
  /** Optional saved payment method ID for server-side confirmation */
  paymentMethodId?: string;
  /** Optional metadata to attach to the PaymentIntent */
  metadata?: Record<string, string>;
}

/**
 * Result of creating a PaymentIntent.
 */
export interface CreatePaymentIntentResult {
  /** Client secret for confirming payment on frontend (null when server-confirmed) */
  clientSecret: string | null;
  /** Credit amount in dollars (e.g., 50 for $50) */
  amountInDollars: number;
  /** Payment status */
  status: "requires_payment" | "requires_action" | "succeeded";
}

/**
 * Payment Intent service for managing Stripe PaymentIntents.
 *
 * Provides methods for creating payment intents for one-time purchases
 * like router credit top-ups. Returns client secret for use with Stripe Elements
 * to collect payment information directly in the application.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const payments = yield* Payments;
 *
 *   const result = yield* payments.paymentIntents.createRouterCreditsPurchaseIntent({
 *     stripeCustomerId: "cus_123",
 *     amountInDollars: 50,
 *   });
 *
 *   console.log(result.clientSecret); // Use with Stripe Elements
 * });
 * ```
 */
export class PaymentIntents {
  /**
   * Creates a Stripe PaymentIntent for purchasing router credits.
   *
   * Creates a PaymentIntent that can be confirmed on the frontend using
   * Stripe Elements. Metadata is attached to track the purchase for webhook processing.
   *
   * After successful payment confirmation, a webhook handler should create
   * the corresponding credit grant.
   *
   * @param params - PaymentIntent configuration including amount and metadata
   * @returns Client secret and amount for frontend payment confirmation
   * @throws StripeError - If PaymentIntent creation fails
   */
  createRouterCreditsPurchaseIntent(
    params: CreateRouterCreditsPurchaseIntentParams,
  ): Effect.Effect<CreatePaymentIntentResult, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      // Convert dollars to cents for Stripe
      const amountInCents = Math.round(params.amountInDollars * 100);

      const metadata = {
        stripeCustomerId: params.stripeCustomerId,
        creditAmountInCents: amountInCents.toString(),
        ...params.metadata,
      };

      // If a saved payment method is provided, confirm server-side
      if (params.paymentMethodId) {
        const paymentIntent = yield* stripe.paymentIntents.create({
          customer: params.stripeCustomerId,
          amount: amountInCents,
          currency: "usd",
          payment_method: params.paymentMethodId,
          confirm: true,
          off_session: true,
          description: `Mirascope Router Credits - $${params.amountInDollars.toFixed(2)}`,
          metadata,
        });

        if (paymentIntent.status === "succeeded") {
          return {
            clientSecret: null,
            amountInDollars: params.amountInDollars,
            status: "succeeded" as const,
          };
        }

        // 3DS or other action required
        if (!paymentIntent.client_secret) {
          return yield* Effect.fail(
            new StripeError({
              message:
                "PaymentIntent requires action but no client secret returned",
            }),
          );
        }

        return {
          clientSecret: paymentIntent.client_secret,
          amountInDollars: params.amountInDollars,
          status: "requires_action" as const,
        };
      }

      // No saved card — create PaymentIntent for frontend confirmation
      const paymentIntent = yield* stripe.paymentIntents.create({
        customer: params.stripeCustomerId,
        amount: amountInCents,
        currency: "usd",
        payment_method_types: ["card", "link"],
        setup_future_usage: "off_session",
        description: `Mirascope Router Credits - $${params.amountInDollars.toFixed(2)}`,
        metadata,
      });

      if (!paymentIntent.client_secret) {
        return yield* Effect.fail(
          new StripeError({
            message: "PaymentIntent created but no client secret returned",
          }),
        );
      }

      return {
        clientSecret: paymentIntent.client_secret,
        amountInDollars: params.amountInDollars,
        status: "requires_payment" as const,
      };
    });
  }
}
