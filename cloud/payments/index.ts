/**
 * @fileoverview Effect-native payment integration.
 *
 * This module provides an Effect-native wrapper around payment providers,
 * enabling seamless integration with Effect's ecosystem.
 *
 * ## Quick Start
 *
 * ```ts
 * import { Stripe } from "@/payments";
 * import { StripeError } from "@/errors";
 *
 * const program = Effect.gen(function* () {
 *   const stripe = yield* Stripe;
 *
 *   const customer = yield* stripe.customers.create({
 *     email: "user@example.com"
 *   });
 *
 *   return customer;
 * });
 *
 * // Provide the layer
 * program.pipe(
 *   Effect.provide(Stripe.layer({ apiKey: "sk_test_..." }))
 * );
 * ```
 */

export * from "@/payments/client";
export * from "@/payments/customers";
