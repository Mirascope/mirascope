import { describe, it, expect } from "@effect/vitest";
import { Context, Effect, Layer } from "effect";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import { MockDrizzleORMLayer } from "@/tests/mock-drizzle";
import { NotFoundError, StripeError } from "@/errors";

describe("Spans Product", () => {
  describe("chargeMeter", () => {
    it.effect("charges the Cloud Spans meter with 1 unit", () => {
      let capturedParams: unknown = null;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.products.spans.chargeMeter({
          stripeCustomerId: "cus_123",
          spanId: "span-uuid-123",
        });

        // Verify meter event was created with correct parameters
        expect(capturedParams).toMatchObject({
          event_name: "ingest_span",
          payload: {
            stripe_customer_id: "cus_123",
            value: "1", // 1 span = 1 meter unit
          },
          identifier: "span-uuid-123", // Idempotency key
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          timestamp: expect.any(Number),
        });
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                billing: {
                  meterEvents: {
                    create: (params: unknown) => {
                      capturedParams = params;
                      return Effect.succeed({});
                    },
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test_mock",
                  routerMeterId: "meter_test_mock",
                  cloudSpansPriceId: "price_spans_test_mock",
                  cloudSpansMeterId: "meter_spans_test_mock",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      );
    });

    it.effect(
      "uses span ID as idempotency key to prevent double-metering",
      () => {
        let capturedParams: unknown = null;

        return Effect.gen(function* () {
          const payments = yield* Payments;

          const spanId = "unique-span-id-456";
          yield* payments.products.spans.chargeMeter({
            stripeCustomerId: "cus_456",
            spanId,
          });

          // Verify idempotency key is set to span ID
          expect(capturedParams).toMatchObject({
            identifier: spanId,
          });
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(MockDrizzleORMLayer),
              Layer.provide(
                Layer.succeed(Stripe, {
                  billing: {
                    meterEvents: {
                      create: (params: unknown) => {
                        capturedParams = params;
                        return Effect.succeed({});
                      },
                    },
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test_mock",
                    routerMeterId: "meter_test_mock",
                    cloudSpansPriceId: "price_spans_test_mock",
                    cloudSpansMeterId: "meter_spans_test_mock",
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        );
      },
    );
  });

  describe("getUsageMeterBalance", () => {
    it.effect("returns total spans metered in current billing period", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result =
          yield* payments.products.spans.getUsageMeterBalance("cus_test123");

        expect(result).toBe(150000n); // 150K spans
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                subscriptions: {
                  list: () =>
                    Effect.succeed({
                      data: [
                        {
                          id: "sub_123",
                          status: "active",
                          customer: "cus_test123",
                          current_period_start: 1700000000,
                          current_period_end: 1702592000,
                          items: {
                            data: [
                              {
                                id: "si_123",
                                price: { id: "price_cloudSpans" },
                              },
                            ],
                          },
                        },
                      ],
                    }),
                },
                billing: {
                  meters: {
                    listEventSummaries: () =>
                      Effect.succeed({
                        data: [
                          { aggregated_value: "100000" }, // 100K spans
                          { aggregated_value: "50000" }, // 50K spans
                        ],
                      }),
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test_mock",
                  routerMeterId: "meter_test_mock",
                  cloudSpansPriceId: "price_spans_test_mock",
                  cloudSpansMeterId: "meter_spans_test_mock",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("returns 0n when no meter events exist", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result =
          yield* payments.products.spans.getUsageMeterBalance("cus_test123");

        expect(result).toBe(0n);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                subscriptions: {
                  list: () =>
                    Effect.succeed({
                      data: [
                        {
                          id: "sub_123",
                          status: "active",
                          customer: "cus_test123",
                          current_period_start: 1700000000,
                          current_period_end: 1702592000,
                        },
                      ],
                    }),
                },
                billing: {
                  meters: {
                    listEventSummaries: () =>
                      Effect.succeed({
                        data: [], // No events
                      }),
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test_mock",
                  routerMeterId: "meter_test_mock",
                  cloudSpansPriceId: "price_spans_test_mock",
                  cloudSpansMeterId: "meter_spans_test_mock",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("returns NotFoundError when no active subscription exists", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.products.spans
          .getUsageMeterBalance("cus_test123")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "No active subscription found for customer",
        );
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                subscriptions: {
                  list: () =>
                    Effect.succeed({
                      data: [], // No subscriptions
                    }),
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test_mock",
                  routerMeterId: "meter_test_mock",
                  cloudSpansPriceId: "price_spans_test_mock",
                  cloudSpansMeterId: "meter_spans_test_mock",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect(
      "returns NotFoundError when only canceled subscriptions exist",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.products.spans
            .getUsageMeterBalance("cus_test123")
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(MockDrizzleORMLayer),
              Layer.provide(
                Layer.succeed(Stripe, {
                  subscriptions: {
                    list: () =>
                      Effect.succeed({
                        data: [
                          {
                            id: "sub_123",
                            status: "canceled", // Not active or past_due
                            customer: "cus_test123",
                          },
                        ],
                      }),
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test_mock",
                    routerMeterId: "meter_test_mock",
                    cloudSpansPriceId: "price_spans_test_mock",
                    cloudSpansMeterId: "meter_spans_test_mock",
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        ),
    );

    it.effect("returns StripeError when meter API fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.products.spans
          .getUsageMeterBalance("cus_test123")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                subscriptions: {
                  list: () =>
                    Effect.succeed({
                      data: [
                        {
                          id: "sub_123",
                          status: "active",
                          customer: "cus_test123",
                          current_period_start: 1700000000,
                          current_period_end: 1702592000,
                        },
                      ],
                    }),
                },
                billing: {
                  meters: {
                    listEventSummaries: () =>
                      Effect.fail(
                        new StripeError({
                          message: "Stripe API error",
                        }),
                      ),
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test_mock",
                  routerMeterId: "meter_test_mock",
                  cloudSpansPriceId: "price_spans_test_mock",
                  cloudSpansMeterId: "meter_spans_test_mock",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("handles large span counts (>1M)", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result =
          yield* payments.products.spans.getUsageMeterBalance("cus_test123");

        expect(result).toBe(2_500_000n); // 2.5M spans
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                subscriptions: {
                  list: () =>
                    Effect.succeed({
                      data: [
                        {
                          id: "sub_123",
                          status: "active",
                          customer: "cus_test123",
                          current_period_start: 1700000000,
                          current_period_end: 1702592000,
                        },
                      ],
                    }),
                },
                billing: {
                  meters: {
                    listEventSummaries: () =>
                      Effect.succeed({
                        data: [
                          { aggregated_value: "1000000" }, // 1M
                          { aggregated_value: "1000000" }, // 1M
                          { aggregated_value: "500000" }, // 500K
                        ],
                      }),
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test_mock",
                  routerMeterId: "meter_test_mock",
                  cloudSpansPriceId: "price_spans_test_mock",
                  cloudSpansMeterId: "meter_spans_test_mock",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("accepts past_due subscriptions as valid", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result =
          yield* payments.products.spans.getUsageMeterBalance("cus_test123");

        expect(result).toBe(75000n);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                subscriptions: {
                  list: () =>
                    Effect.succeed({
                      data: [
                        {
                          id: "sub_123",
                          status: "past_due", // Past due but still valid
                          customer: "cus_test123",
                          current_period_start: 1700000000,
                          current_period_end: 1702592000,
                        },
                      ],
                    }),
                },
                billing: {
                  meters: {
                    listEventSummaries: () =>
                      Effect.succeed({
                        data: [{ aggregated_value: "75000" }],
                      }),
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test_mock",
                  routerMeterId: "meter_test_mock",
                  cloudSpansPriceId: "price_spans_test_mock",
                  cloudSpansMeterId: "meter_spans_test_mock",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );
  });
});
