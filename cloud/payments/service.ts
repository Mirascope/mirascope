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
 *       ├── router: Ready<Router>
 *       └── spans: Ready<Spans>
 *
 * Each service uses `yield* Stripe` internally. The `makeReady` wrapper
 * provides the Stripe client, so consumers see methods returning
 * Effect<T, E> with no additional dependencies.
 * ```
 */

import { Context, Layer, Effect } from "effect";
import { Stripe, type StripeConfig } from "@/payments/client";
import { Customers } from "@/payments/customers";
import { Subscriptions } from "@/payments/subscriptions";
import { Router } from "@/payments/products/router";
import { Spans } from "@/payments/products/spans";
import { PaymentIntents } from "@/payments/payment-intents";
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
      readonly spans: Ready<Spans>;
    };
    readonly paymentIntents: Ready<PaymentIntents>;
  }
>() {
  /**
   * Default layer that creates the Payments service.
   *
   * Requires Stripe and DrizzleORM to be provided. The dependency provider automatically
   * provides these dependencies to service methods, removing them from method signatures.
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

      const subscriptions = new Subscriptions();

      return {
        customers: provideDependencies(new Customers(subscriptions)),
        products: {
          router: provideDependencies(new Router(subscriptions)),
          spans: provideDependencies(new Spans(subscriptions)),
        },
        paymentIntents: provideDependencies(new PaymentIntents()),
      };
    }),
  );

  /**
   * Creates a fully configured layer with Stripe and database connections.
   *
   * This requires DrizzleORM to be provided externally (typically through Database.Live).
   * This design maintains separation between database connection management (owned by Database)
   * and payment operations (owned by Payments), while allowing Payments to use the database
   * for credit reservations.
   *
   * @param config - Partial Stripe configuration (validated by Stripe layer)
   * @returns A Layer providing Payments (requires DrizzleORM)
   *
   * @example
   * ```ts
   * // Typically used through Database.Live which provides both:
   * const DatabaseLive = Database.Live({
   *   database: { connectionString: process.env.DATABASE_URL },
   *   payments: {
   *     apiKey: process.env.STRIPE_SECRET_KEY,
   *     routerPriceId: process.env.STRIPE_ROUTER_PRICE_ID,
   *     // ... other fields from process.env
   *   },
   * });
   *
   * program.pipe(Effect.provide(DbLive));
   * ```
   */
  static Live = (config: Partial<StripeConfig>) => {
    const stripeLayer = Stripe.layer(config);

    return Payments.Default.pipe(Layer.provide(stripeLayer));
  };
}
