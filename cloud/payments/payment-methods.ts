/**
 * @fileoverview Payment Methods service for managing saved payment methods.
 *
 * Provides an Effect-native service for creating SetupIntents (to save cards),
 * retrieving the default payment method, and removing payment methods.
 */

import { Effect } from "effect";

import { StripeError } from "@/errors";
import { Stripe } from "@/payments/client";

/**
 * Details of a saved payment method.
 */
export interface PaymentMethodDetails {
  id: string;
  brand: string;
  last4: string;
  expMonth: number;
  expYear: number;
}

/**
 * Payment Methods service for managing saved payment methods on Stripe customers.
 *
 * Provides methods for:
 * - Creating SetupIntents to save cards via Stripe Elements
 * - Retrieving the default payment method
 * - Removing (detaching) payment methods
 *
 * Default payment method is stored on the Stripe customer's
 * `invoice_settings.default_payment_method`, not in our database.
 */
export class PaymentMethods {
  /**
   * Creates a Stripe SetupIntent for saving a payment method.
   *
   * The returned client secret is used with Stripe Elements on the frontend
   * to collect and save card details.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @returns Client secret for frontend SetupElement
   * @throws StripeError - If SetupIntent creation fails
   */
  createSetupIntent(
    stripeCustomerId: string,
  ): Effect.Effect<{ clientSecret: string }, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      const setupIntent = yield* stripe.setupIntents.create({
        customer: stripeCustomerId,
        usage: "off_session",
        payment_method_types: ["card", "link"],
      });

      if (!setupIntent.client_secret) {
        return yield* Effect.fail(
          new StripeError({
            message: "SetupIntent created but no client secret returned",
          }),
        );
      }

      return { clientSecret: setupIntent.client_secret };
    });
  }

  /**
   * Creates a Stripe SetupIntent without a customer.
   *
   * Used during paid org creation: verifies the card and runs 3DS before
   * the org exists. The resulting payment method can be attached to the
   * new customer after org creation.
   *
   * @returns Client secret for frontend SetupElement
   * @throws StripeError - If SetupIntent creation fails
   */
  createSetupIntentWithoutCustomer(): Effect.Effect<
    { clientSecret: string },
    StripeError,
    Stripe
  > {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      const setupIntent = yield* stripe.setupIntents.create({
        usage: "off_session",
        payment_method_types: ["card", "link"],
      });

      if (!setupIntent.client_secret) {
        return yield* Effect.fail(
          new StripeError({
            message: "SetupIntent created but no client secret returned",
          }),
        );
      }

      return { clientSecret: setupIntent.client_secret };
    });
  }

  /**
   * Attaches a payment method to a customer and sets it as the default
   * for invoices.
   *
   * Used after org creation to attach a pre-verified payment method
   * from a customerless SetupIntent.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @param paymentMethodId - The verified payment method ID
   * @throws StripeError - If attaching or updating fails
   */
  attachAndSetDefault(
    stripeCustomerId: string,
    paymentMethodId: string,
  ): Effect.Effect<void, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      yield* stripe.paymentMethods.attach(paymentMethodId, {
        customer: stripeCustomerId,
      });

      yield* stripe.customers.update(stripeCustomerId, {
        invoice_settings: {
          default_payment_method: paymentMethodId,
        },
      });
    });
  }

  /**
   * Gets the default payment method for a customer.
   *
   * Priority:
   * 1. Customer's invoice_settings.default_payment_method
   * 2. First card from paymentMethods.list
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @returns Payment method details or null if none saved
   * @throws StripeError - If Stripe API calls fail
   */
  getDefault(
    stripeCustomerId: string,
  ): Effect.Effect<PaymentMethodDetails | null, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      const customer = yield* stripe.customers.retrieve(stripeCustomerId);

      if (customer.deleted) {
        return null;
      }

      // Check customer's default payment method
      let paymentMethodId: string | null = null;

      if (
        "invoice_settings" in customer &&
        customer.invoice_settings?.default_payment_method &&
        typeof customer.invoice_settings.default_payment_method === "string"
      ) {
        paymentMethodId = customer.invoice_settings.default_payment_method;
      }

      // Fall back to first card in list
      if (!paymentMethodId) {
        const paymentMethods = yield* stripe.paymentMethods.list({
          customer: stripeCustomerId,
          type: "card",
        });

        if (paymentMethods.data.length > 0) {
          paymentMethodId = paymentMethods.data[0].id;
        }
      }

      if (!paymentMethodId) {
        return null;
      }

      const paymentMethod =
        yield* stripe.paymentMethods.retrieve(paymentMethodId);

      if (!paymentMethod.card) {
        return null;
      }

      return {
        id: paymentMethod.id,
        brand: paymentMethod.card.brand,
        last4: paymentMethod.card.last4,
        expMonth: paymentMethod.card.exp_month,
        expYear: paymentMethod.card.exp_year,
      };
    });
  }

  /**
   * Removes a payment method from a customer.
   *
   * Detaches the payment method from the customer. If it was the default,
   * clears the customer's invoice_settings.default_payment_method.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @param paymentMethodId - The payment method ID to remove
   * @throws StripeError - If Stripe API calls fail
   */
  remove(
    stripeCustomerId: string,
    paymentMethodId: string,
  ): Effect.Effect<void, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      // Detach the payment method
      yield* stripe.paymentMethods.detach(paymentMethodId);

      // Check if it was the default and clear if so
      const customer = yield* stripe.customers.retrieve(stripeCustomerId);

      if (
        !customer.deleted &&
        "invoice_settings" in customer &&
        customer.invoice_settings?.default_payment_method === paymentMethodId
      ) {
        yield* stripe.customers.update(stripeCustomerId, {
          invoice_settings: { default_payment_method: "" },
        });
      }
    });
  }
}
