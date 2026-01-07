/**
 * @fileoverview Payments service layer.
 *
 * This module provides the `Payments` service which aggregates payment-related
 * services (Customers, etc.) and provides them through Effect's dependency
 * injection system.
 *
 * ## Usage
 *
 * ```ts
 * import { Payments } from "@/payments";
 *
 * const createCustomer = Effect.gen(function* () {
 *   const payments = yield* Payments;
 *
 *   const result = yield* payments.customers.create({
 *     organizationId: "org_123",
 *     organizationName: "Acme Corp",
 *     organizationSlug: "acme-corp",
 *     email: "billing@acme.com",
 *   });
 *
 *   return result;
 * });
 *
 * // Provide the Payments layer
 * createCustomer.pipe(
 *   Effect.provide(Payments.Live({ apiKey: "sk_...", routerPriceId: "price_..." }))
 * );
 * ```
 *
 * ## Architecture
 *
 * ```
 * Payments (service layer)
 *   ├── customers: Ready<Customers>
 *   └── products
 *       └── router: Ready<Router>
 *
 * Each service uses `yield* Stripe` internally. The `makeReady` wrapper
 * provides the Stripe client, so consumers see methods returning
 * Effect<T, E> with no additional dependencies.
 * ```
 */

import { Context, Layer, Effect } from "effect";
import { Stripe, type StripeConfig } from "@/payments/client";
import { Customers } from "@/payments/customers";
import { Router } from "@/payments/products/router";
import { DrizzleORM } from "@/db/client";
import { dependencyProvider, type Ready } from "@/utils";

/**
 * Payments service layer.
 *
 * Provides aggregated access to all payment services through Effect's
 * dependency injection system. The Stripe dependency is provided
 * internally, so consumers don't need to manage it.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const payments = yield* Payments;
 *
 *   // Create a customer - no Stripe requirement leaked!
 *   const result = yield* payments.customers.create({
 *     organizationId: "org_123",
 *     organizationName: "Acme Corp",
 *     organizationSlug: "acme-corp",
 *     email: "billing@acme.com",
 *   });
 *
 *   return result;
 * });
 *
 * // Provide the Payments layer
 * program.pipe(Effect.provide(Payments.Live({ apiKey: "sk_...", routerPriceId: "price_..." })));
 * ```
 */
export class Payments extends Context.Tag("Payments")<
  Payments,
  {
    readonly customers: Ready<Customers>;
    readonly products: {
      readonly router: Ready<Router>;
    };
  }
>() {
  /**
   * Default layer that creates the Payments service.
   *
   * Requires Stripe to be provided. The dependency provider automatically
   * provides Stripe to service methods, removing it from method signatures.
   */
  static Default = Layer.effect(
    Payments,
    Effect.gen(function* () {
      const stripe = yield* Stripe;
      const db = yield* DrizzleORM;
      const provideDependencies = dependencyProvider([
        { tag: Stripe, instance: stripe },
        { tag: DrizzleORM, instance: db },
      ]);

      return {
        customers: provideDependencies(new Customers()),
        products: {
          router: provideDependencies(new Router()),
        },
      };
    }),
  );

  /**
   * Creates a fully configured layer with Stripe connection.
   *
   * This is the standard way to use Payments. Provide Stripe configuration
   * and get back a layer that provides the Payments service with no dependencies.
   *
   * @param config - Stripe configuration
   * @returns A Layer providing Payments with no dependencies
   *
   * @example
   * ```ts
   * const PaymentsLive = Payments.Live({
   *   apiKey: process.env.STRIPE_SECRET_KEY!,
   *   routerPriceId: process.env.STRIPE_ROUTER_PRICE_ID!,
   * });
   *
   * program.pipe(Effect.provide(PaymentsLive));
   * ```
   */
  static Live = (config: StripeConfig) => {
    const stripeLayer = Stripe.layer(config);

    return Payments.Default.pipe(Layer.provide(stripeLayer));
  };
}
