/**
 * @fileoverview Spans product billing service.
 *
 * Provides Spans-specific billing operations for usage metering of OpenTelemetry spans.
 * Each span ingested is metered as 1 unit, charged to the Cloud Spans meter.
 */

import { Effect } from "effect";
import { Stripe } from "@/payments/client";
import { StripeError } from "@/errors";

/**
 * Spans product billing service.
 *
 * Handles Cloud Spans metering for OpenTelemetry span ingestion.
 * Each span is metered as 1 unit against the Cloud Spans meter, which uses
 * graduated tier pricing in Stripe.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const payments = yield* Payments;
 *
 *   // Meter a span (charges 1 unit to Cloud Spans meter)
 *   yield* payments.products.spans.chargeMeter({
 *     stripeCustomerId: "cus_123",
 *     spanId: "span-uuid-123",
 *   });
 * });
 * ```
 */
export class Spans {
  /**
   * Charges the Cloud Spans meter for a single span.
   *
   * Records a meter event for the customer's span ingestion. Each span
   * is charged as 1 unit to the Cloud Spans meter.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @param spanId - The span UUID for idempotency key
   * @returns Effect that succeeds when meter is charged
   * @throws StripeError - If meter event creation fails
   */
  chargeMeter({
    stripeCustomerId,
    spanId,
  }: {
    stripeCustomerId: string;
    spanId: string;
  }): Effect.Effect<void, StripeError, Stripe> {
    return Effect.gen(function* () {
      const stripe = yield* Stripe;

      // Create meter event for 1 span
      yield* stripe.billing.meterEvents.create({
        event_name: "ingest_span",
        payload: {
          stripe_customer_id: stripeCustomerId,
          value: "1", // 1 span = 1 meter unit
        },
        identifier: spanId, // Idempotency: prevent double-metering same span
        timestamp: Math.floor(Date.now() / 1000),
      });
    });
  }
}
