/**
 * @fileoverview Effect-native payment integration.
 *
 * This module provides an Effect-native wrapper around payment providers,
 * enabling seamless integration with Effect's ecosystem.
 *
 * ## Quick Start
 *
 * ```ts
 * import { Payments } from "@/payments";
 *
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
 *   return result;
 * });
 *
 * // Provide the layer
 * program.pipe(
 *   Effect.provide(Payments.Live({ apiKey: "sk_...", routerPriceId: "price_..." }))
 * );
 * ```
 */

export * from "@/payments/client";
export * from "@/payments/customers";
export * from "@/payments/service";
