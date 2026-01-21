import { describe, it, expect } from "@effect/vitest";
import { Context, Effect, Layer } from "effect";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import { DrizzleORM } from "@/db/client";
import { MockDrizzleORMLayer } from "@/tests/mock-drizzle";
import { TestDrizzleORM } from "@/tests/db";
import {
  TestSubscriptionWithRealDatabaseFixture,
  MockPayments,
} from "@/tests/payments";
import { NotFoundError, StripeError, PlanLimitExceededError } from "@/errors";
import { organizations } from "@/db/schema/organizations";
import type { PlanTier } from "@/payments/plans";

// Test constants
const TEST_CUSTOMER_IDS = {
  underLimit: "cus_spans_under_limit",
  atLimitMinusOne: "cus_spans_at_limit_minus_one",
  atLimit: "cus_spans_at_limit",
  overLimit: "cus_spans_over_limit",
  cacheTest: "cus_spans_cache_test",
  proPlan: "cus_spans_pro",
  teamPlan: "cus_spans_team",
  stripeError: "cus_spans_error",
};

/**
 * Helper to create a test organization with unique slug.
 */
function* createTestOrg(customerId: string) {
  const db = yield* DrizzleORM;
  const [org] = yield* db
    .insert(organizations)
    .values({
      name: "Test Organization",
      slug: `test-org-${crypto.randomUUID()}`,
      stripeCustomerId: customerId,
    })
    .returning();
  return org;
}

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

        expect(capturedParams).toMatchObject({
          event_name: "ingest_span",
          payload: {
            stripe_customer_id: "cus_123",
            value: "1",
          },
          identifier: "span-uuid-123",
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

        expect(result).toBe(150000n);
      }).pipe(
        Effect.provide(
          new MockPayments().subscriptions
            .list(() =>
              Effect.succeed({
                data: [
                  {
                    id: "sub_test",
                    status: "active",
                    customer: "cus_test123",
                    current_period_start: 1700000000,
                    current_period_end: 1702592000,
                    items: {
                      data: [{ price: { id: "price_cloudSpans" } }],
                    },
                  },
                ],
              }),
            )
            .billing.meters.listEventSummaries(() =>
              Effect.succeed({
                data: [
                  { aggregated_value: "100000" },
                  { aggregated_value: "50000" },
                ],
              }),
            )
            .build(),
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
          new MockPayments().subscriptions
            .list(() =>
              Effect.succeed({
                data: [
                  {
                    id: "sub_test",
                    status: "active",
                    customer: "cus_test123",
                    current_period_start: 1700000000,
                    current_period_end: 1702592000,
                    items: {
                      data: [{ price: { id: "price_cloudSpans" } }],
                    },
                  },
                ],
              }),
            )
            .billing.meters.listEventSummaries(() =>
              Effect.succeed({
                data: [],
              }),
            )
            .build(),
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
              Layer.merge(
                Layer.succeed(Stripe, {
                  subscriptions: {
                    list: () =>
                      Effect.succeed({
                        data: [],
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
                MockDrizzleORMLayer,
              ),
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
                Layer.merge(
                  Layer.succeed(Stripe, {
                    subscriptions: {
                      list: () =>
                        Effect.succeed({
                          data: [
                            {
                              id: "sub_123",
                              status: "canceled",
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
                  MockDrizzleORMLayer,
                ),
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
          new MockPayments().subscriptions
            .list(() =>
              Effect.succeed({
                data: [
                  {
                    id: "sub_test",
                    status: "active",
                    customer: "cus_test123",
                    current_period_start: 1700000000,
                    current_period_end: 1702592000,
                    items: {
                      data: [{ price: { id: "price_cloudSpans" } }],
                    },
                  },
                ],
              }),
            )
            .billing.meters.listEventSummaries(() =>
              Effect.fail(new StripeError({ message: "Stripe API error" })),
            )
            .build(),
        ),
      ),
    );

    it.effect("handles large span counts (>1M)", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result =
          yield* payments.products.spans.getUsageMeterBalance("cus_test123");

        expect(result).toBe(2_500_000n);
      }).pipe(
        Effect.provide(
          new MockPayments().subscriptions
            .list(() =>
              Effect.succeed({
                data: [
                  {
                    id: "sub_test",
                    status: "active",
                    customer: "cus_test123",
                    current_period_start: 1700000000,
                    current_period_end: 1702592000,
                    items: {
                      data: [{ price: { id: "price_cloudSpans" } }],
                    },
                  },
                ],
              }),
            )
            .billing.meters.listEventSummaries(() =>
              Effect.succeed({
                data: [
                  { aggregated_value: "1000000" },
                  { aggregated_value: "1000000" },
                  { aggregated_value: "500000" },
                ],
              }),
            )
            .build(),
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
              Layer.merge(
                Layer.succeed(Stripe, {
                  subscriptions: {
                    list: () =>
                      Effect.succeed({
                        data: [
                          {
                            id: "sub_123",
                            status: "past_due",
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
                MockDrizzleORMLayer,
              ),
            ),
          ),
        ),
      ),
    );
  });

  describe("checkSpanLimit", () => {
    it.effect("succeeds when usage is under limit", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;
        const org = yield* createTestOrg(TEST_CUSTOMER_IDS.underLimit);

        yield* payments.products.spans.checkSpanLimit({
          organizationId: org.id,
          stripeCustomerId: TEST_CUSTOMER_IDS.underLimit,
        });
      }).pipe(
        Effect.provide(
          TestSubscriptionWithRealDatabaseFixture(
            {
              plan: "free",
              stripeCustomerId: TEST_CUSTOMER_IDS.underLimit,
              meterBalance: "500000",
            },
            TestDrizzleORM,
          ),
        ),
      ),
    );

    it.effect("succeeds when usage is exactly at limit minus 1", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;
        const org = yield* createTestOrg(TEST_CUSTOMER_IDS.atLimitMinusOne);

        yield* payments.products.spans.checkSpanLimit({
          organizationId: org.id,
          stripeCustomerId: TEST_CUSTOMER_IDS.atLimitMinusOne,
        });
      }).pipe(
        Effect.provide(
          TestSubscriptionWithRealDatabaseFixture(
            {
              plan: "free",
              stripeCustomerId: TEST_CUSTOMER_IDS.atLimitMinusOne,
              meterBalance: "999999",
            },
            TestDrizzleORM,
          ),
        ),
      ),
    );

    it.effect("throws PlanLimitExceededError when at limit", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;
        const org = yield* createTestOrg(TEST_CUSTOMER_IDS.atLimit);

        const result = yield* payments.products.spans
          .checkSpanLimit({
            organizationId: org.id,
            stripeCustomerId: TEST_CUSTOMER_IDS.atLimit,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PlanLimitExceededError);
        if (result instanceof PlanLimitExceededError) {
          expect(result.message).toContain(
            "Cannot ingest spans: free plan limit is 1,000,000 spans/month",
          );
          expect(result.currentUsage).toBe(1000000);
          expect(result.limit).toBe(1000000);
          expect(result.limitType).toBe("spansPerMonth");
        }
      }).pipe(
        Effect.provide(
          TestSubscriptionWithRealDatabaseFixture(
            {
              plan: "free",
              stripeCustomerId: TEST_CUSTOMER_IDS.atLimit,
              meterBalance: "1000000",
            },
            TestDrizzleORM,
          ),
        ),
      ),
    );

    it.effect("throws PlanLimitExceededError when over limit", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;
        const org = yield* createTestOrg(TEST_CUSTOMER_IDS.overLimit);

        const result = yield* payments.products.spans
          .checkSpanLimit({
            organizationId: org.id,
            stripeCustomerId: TEST_CUSTOMER_IDS.overLimit,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PlanLimitExceededError);
        if (result instanceof PlanLimitExceededError) {
          expect(result.currentUsage).toBe(1500000);
          expect(result.limit).toBe(1000000);
        }
      }).pipe(
        Effect.provide(
          TestSubscriptionWithRealDatabaseFixture(
            {
              plan: "free",
              stripeCustomerId: TEST_CUSTOMER_IDS.overLimit,
              meterBalance: "1500000",
            },
            TestDrizzleORM,
          ),
        ),
      ),
    );

    it.effect("uses cache on second call within TTL", () => {
      let stripeCallCount = 0;

      return Effect.gen(function* () {
        const payments = yield* Payments;
        const org = yield* createTestOrg(TEST_CUSTOMER_IDS.cacheTest);

        // First call - should query Stripe
        yield* payments.products.spans.checkSpanLimit({
          organizationId: org.id,
          stripeCustomerId: TEST_CUSTOMER_IDS.cacheTest,
        });

        expect(stripeCallCount).toBe(1);

        // Second call - should use cache
        yield* payments.products.spans.checkSpanLimit({
          organizationId: org.id,
          stripeCustomerId: TEST_CUSTOMER_IDS.cacheTest,
        });

        expect(stripeCallCount).toBe(1);
      }).pipe(
        Effect.provide(
          Layer.merge(
            Payments.Default.pipe(
              Layer.provide(TestDrizzleORM),
              Layer.provide(
                Layer.succeed(Stripe, {
                  customers: {
                    retrieve: () =>
                      Effect.succeed({
                        id: TEST_CUSTOMER_IDS.cacheTest,
                        object: "customer",
                        email: "test@example.com",
                        name: "Test Customer",
                      }),
                  },
                  subscriptions: {
                    list: () =>
                      Effect.succeed({
                        data: [
                          {
                            id: "sub_test",
                            status: "active",
                            customer: TEST_CUSTOMER_IDS.cacheTest,
                            current_period_start: 1700000000,
                            current_period_end: 1702592000,
                            items: {
                              data: [{ price: { id: "price_cloudFree" } }],
                            },
                          },
                        ],
                      }),
                  },
                  subscriptionSchedules: {
                    list: () =>
                      Effect.succeed({
                        data: [],
                        has_more: false,
                      }),
                  },
                  paymentMethods: {
                    list: () =>
                      Effect.succeed({
                        data: [],
                        has_more: false,
                      }),
                  },
                  billing: {
                    meters: {
                      listEventSummaries: () => {
                        stripeCallCount++;
                        return Effect.succeed({
                          data: [{ aggregated_value: "500000" }],
                        });
                      },
                    },
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    cloudFreePriceId: "price_cloudFree",
                    cloudSpansPriceId: "price_cloudSpans",
                    cloudSpansMeterId: "meter_cloudSpans",
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
            TestDrizzleORM,
          ),
        ),
      );
    });

    // Tests for paid plans with unlimited spans (Infinity)
    const unlimitedPlanScenarios: Array<{
      plan: PlanTier;
      customerId: string;
      usage: string;
      description: string;
    }> = [
      {
        plan: "pro",
        customerId: TEST_CUSTOMER_IDS.proPlan,
        usage: "1000000",
        description: "at 1M spans",
      },
      {
        plan: "pro",
        customerId: "cus_pro_over_limit",
        usage: "5000000",
        description: "at 5M spans (overage billed)",
      },
      {
        plan: "team",
        customerId: TEST_CUSTOMER_IDS.teamPlan,
        usage: "1000000",
        description: "at 1M spans",
      },
      {
        plan: "team",
        customerId: "cus_team_over_limit",
        usage: "10000000",
        description: "at 10M spans (overage billed)",
      },
    ];

    unlimitedPlanScenarios.forEach(
      ({ plan, customerId, usage, description }) => {
        it.effect(
          `allows unlimited spans for ${plan} plan ${description}`,
          () =>
            Effect.gen(function* () {
              const payments = yield* Payments;
              const org = yield* createTestOrg(customerId);

              // Should succeed without throwing PlanLimitExceededError
              yield* payments.products.spans.checkSpanLimit({
                organizationId: org.id,
                stripeCustomerId: customerId,
              });
            }).pipe(
              Effect.provide(
                TestSubscriptionWithRealDatabaseFixture(
                  { plan, stripeCustomerId: customerId, meterBalance: usage },
                  TestDrizzleORM,
                ),
              ),
            ),
        );
      },
    );

    it.effect("throws NotFoundError when no active subscription", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.products.spans
          .checkSpanLimit({
            organizationId: "00000000-0000-0000-0000-000000000000",
            stripeCustomerId: "cus_test123",
          })
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
                      data: [],
                    }),
                },
                billing: {
                  meters: {
                    listEventSummaries: () =>
                      Effect.succeed({
                        data: [],
                      }),
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test_mock",
                  routerMeterId: "meter_test_mock",
                  cloudSpansPriceId: "price_spans_test_mock",
                  cloudSpansMeterId: "meter_spans_test_mock",
                  cloudFreePriceId: "price_cloudFree",
                  cloudProPriceId: "price_cloudPro",
                  cloudTeamPriceId: "price_cloudTeam",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("throws StripeError when Stripe API fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;
        const org = yield* createTestOrg(TEST_CUSTOMER_IDS.stripeError);

        const result = yield* payments.products.spans
          .checkSpanLimit({
            organizationId: org.id,
            stripeCustomerId: TEST_CUSTOMER_IDS.stripeError,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
      }).pipe(
        Effect.provide(
          Layer.merge(
            Payments.Default.pipe(
              Layer.provide(TestDrizzleORM),
              Layer.provide(
                Layer.succeed(Stripe, {
                  customers: {
                    retrieve: () =>
                      Effect.succeed({
                        id: TEST_CUSTOMER_IDS.stripeError,
                        object: "customer",
                        email: "test@example.com",
                        name: "Test Customer",
                      }),
                  },
                  subscriptions: {
                    list: () =>
                      Effect.succeed({
                        data: [
                          {
                            id: "sub_test",
                            status: "active",
                            customer: TEST_CUSTOMER_IDS.stripeError,
                            current_period_start: 1700000000,
                            current_period_end: 1702592000,
                            items: {
                              data: [{ price: { id: "price_cloudFree" } }],
                            },
                          },
                        ],
                      }),
                  },
                  subscriptionSchedules: {
                    list: () =>
                      Effect.succeed({
                        data: [],
                        has_more: false,
                      }),
                  },
                  paymentMethods: {
                    list: () =>
                      Effect.succeed({
                        data: [],
                        has_more: false,
                      }),
                  },
                  billing: {
                    meters: {
                      listEventSummaries: () =>
                        Effect.fail(
                          new StripeError({ message: "Stripe API error" }),
                        ),
                    },
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    cloudFreePriceId: "price_cloudFree",
                    cloudSpansPriceId: "price_cloudSpans",
                    cloudSpansMeterId: "meter_cloudSpans",
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
            TestDrizzleORM,
          ),
        ),
      ),
    );
  });
});
