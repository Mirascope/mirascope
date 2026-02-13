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

import type { StripeConfig } from "@/settings";

import { DrizzleORM } from "@/db/client";
import { Stripe } from "@/payments/client";
import { Customers } from "@/payments/customers";
import { PaymentIntents } from "@/payments/payment-intents";
import { PaymentMethods } from "@/payments/payment-methods";
import { Router } from "@/payments/products/router";
import { Spans } from "@/payments/products/spans";
import { Subscriptions } from "@/payments/subscriptions";
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
    readonly paymentMethods: Ready<PaymentMethods>;
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
        paymentMethods: provideDependencies(new PaymentMethods()),
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
   * Note: Config validation is handled by Settings at startup. The config
   * passed here is guaranteed to be complete and valid.
   *
   * @param config - Validated Stripe configuration from Settings
   * @returns A Layer providing Payments (requires DrizzleORM)
   *
   * @example
   * ```ts
   * // Typically used through Database.Live which provides both:
   * const settings = yield* Settings;
   * const DatabaseLive = Database.Live({
   *   database: { connectionString: settings.databaseUrl },
   *   payments: settings.stripe,
   * });
   *
   * program.pipe(Effect.provide(DbLive));
   * ```
   */
  static Live = (config: StripeConfig) => {
    const stripeLayer = Stripe.layer(config);

    return Payments.Default.pipe(Layer.provide(stripeLayer));
  };

  /**
   * Development layer that creates a no-op Payments service.
   *
   * Construction succeeds without a Stripe connection. Any method call
   * returns `Effect.die` so handlers must catch errors gracefully
   * (see dev fallbacks in organizations.handlers.ts).
   */
  static Dev = Layer.succeed(Payments, {
    customers: devProxy("Payments.customers"),
    products: {
      router: devProxy("Payments.products.router"),
      spans: devProxy("Payments.products.spans"),
    },
    paymentIntents: devProxy("Payments.paymentIntents"),
    paymentMethods: devProxy("Payments.paymentMethods"),
  } as Context.Tag.Service<Payments>);
}

/** Returns a proxy where any method call returns Effect.die with a descriptive message. */
function devProxy(label: string): unknown {
  return new Proxy(
    {},
    {
      get:
        (_target, prop) =>
        (..._args: unknown[]) =>
          Effect.die(
            new Error(`${label}.${String(prop)} not available in dev mode`),
          ),
    },
  );
}
