import { describe, it, expect } from "@effect/vitest";
import { Context, Effect, Layer } from "effect";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import { MockDrizzleORMLayer } from "@/tests/mock-drizzle";

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
});
