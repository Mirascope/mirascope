/**
 * @fileoverview Effect-native payment integration.
 *
 * This module provides an Effect-native wrapper around payment providers,
 * enabling seamless integration with Effect's ecosystem.
 *
 * ## Quick Start
 *
 * ```ts
 * import { Payments, type StripeConfig } from "@/payments";
 *
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
 *
 *   return result;
 * });
 *
 * // Provide the layer
 * program.pipe(
 *   Effect.provide(Payments.Live({ apiKey: "sk_...", routerPriceId: "price_..." }))
 * );
 * ```
 */

// Export the main service and its configuration type
export { Payments } from "@/payments/service";
export type { StripeConfig } from "@/payments/client";
