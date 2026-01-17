/**
 * @fileoverview Spans product billing service.
 *
 * Provides Spans-specific billing operations for usage metering of OpenTelemetry spans.
 * Each span ingested is metered as 1 unit, charged to the Cloud Spans meter.
 */

import { Effect } from "effect";
import { Stripe } from "@/payments/client";
import { NotFoundError, StripeError } from "@/errors";
import { Subscriptions } from "@/payments/subscriptions";

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
  private readonly subscriptions: Subscriptions;

  constructor(subscriptions: Subscriptions) {
    this.subscriptions = subscriptions;
  }

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

  /**
   * Gets the accumulated span meter usage for the current billing period.
   *
   * Queries Stripe's meter event summaries to calculate total spans metered
   * in the customer's current billing cycle. This is used for enforcing
   * plan-based span limits (e.g., 1M spans/month on Free plan).
   *
   * Uses the shared Subscriptions.getActiveSubscription() method to avoid
   * code duplication.
   *
   * @param stripeCustomerId - The Stripe customer ID
   * @returns Total number of spans metered in current billing period
   * @throws NotFoundError - If no active subscription found
   * @throws StripeError - If Stripe API calls fail
   *
   * @example
   * ```ts
   * const spansUsed = yield* payments.products.spans.getUsageMeterBalance("cus_123");
   * if (spansUsed >= 1_000_000n) {
   *   // Free plan limit exceeded
   * }
   * ```
   */
  getUsageMeterBalance(
    stripeCustomerId: string,
  ): Effect.Effect<bigint, StripeError | NotFoundError, Stripe> {
    return Effect.gen(this, function* () {
      const stripe = yield* Stripe;

      // Get the active subscription using injected Subscriptions service
      const subscription =
        yield* this.subscriptions.getActiveSubscription(stripeCustomerId);

      // Get billing period from subscription
      const startTime = subscription.current_period_start;
      const endTime = subscription.current_period_end;

      // List meter event summaries for this billing period
      const summaries = yield* stripe.billing.meters.listEventSummaries(
        stripe.config.cloudSpansMeterId,
        {
          customer: stripeCustomerId,
          start_time: startTime,
          end_time: endTime,
        },
      );

      // Aggregate all event values (each summary has aggregated_value)
      let totalSpans = 0n;
      for (const summary of summaries.data) {
        totalSpans += BigInt(summary.aggregated_value);
      }

      return totalSpans;
    });
  }
}
