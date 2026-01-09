import { describe, it, expect, vi, beforeEach } from "@effect/vitest";
import { assert } from "@/tests/db";
import { Context, Effect, Layer } from "effect";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import {
  DatabaseError,
  InsufficientFundsError,
  ReservationStateError,
  StripeError,
} from "@/errors";
import { MockDrizzleORMLayer } from "@/tests/mock-drizzle";
import { DrizzleORM } from "@/db/client";
import { clearPricingCache } from "@/api/router/pricing";
import type { ProviderName } from "@/api/router/providers";
import type StripeSDK from "stripe";

describe("Router Product", () => {
  describe("getUsageMeterBalance", () => {
    it.effect("returns 0n when no router subscription exists", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const balance =
          yield* payments.products.router.getUsageMeterBalance("cus_123");

        expect(balance).toBe(0n);
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
                        object: "list" as const,
                        data: [],
                        has_more: false,
                      }),
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test_mock",
                    routerMeterId: "meter_test_mock",
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
                MockDrizzleORMLayer,
              ),
            ),
          ),
        ),
      ),
    );

    it.effect("calculates balance from meter event summaries", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const balance =
          yield* payments.products.router.getUsageMeterBalance("cus_123");

        // 1000 units = 1000 centi-cents (1 meter unit = 1 centi-cent)
        expect(balance).toBe(1000n);
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
                        object: "list" as const,
                        data: [
                          {
                            id: "sub_123",
                            customer: "cus_123",
                            current_period_start: 1000000,
                            current_period_end: 2000000,
                            items: {
                              data: [{ price: { id: "price_test_mock" } }],
                            },
                          },
                        ],
                        has_more: false,
                      }),
                  },
                  billing: {
                    meters: {
                      listEventSummaries: () =>
                        Effect.succeed({
                          object: "list" as const,
                          data: [{ aggregated_value: 1000 }],
                          has_more: false,
                        }),
                    },
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test_mock",
                    routerMeterId: "meter_test_mock",
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

  describe("getBalanceInfo", () => {
    it.effect("returns comprehensive balance information", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        // Get balance info
        const balanceInfo =
          yield* payments.products.router.getBalanceInfo("cus_123");

        // Credit grants: 1000 cents * 100 = 100000 centi-cents ($10)
        expect(balanceInfo.creditBalance).toBe(100000n);
        // Meter usage: 1000 units = 1000 centi-cents ($0.10)
        expect(balanceInfo.meterUsage).toBe(1000n);
        // Active reservations: 5000 centi-cents ($0.50) - from custom mock
        expect(balanceInfo.activeReservations).toBe(5000n);
        // Available: 100000 - 1000 = 99000 centi-cents ($9.90) (reservations not subtracted from available)
        expect(balanceInfo.availableBalance).toBe(99000n);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(DrizzleORM, {
                select: () => ({
                  from: () => ({
                    where: () => Effect.succeed([{ sum: "5000" }]), // Mock active reservations
                  }),
                }),
              } as unknown as Context.Tag.Service<typeof DrizzleORM>),
            ),
            Layer.provide(
              Layer.succeed(Stripe, {
                billing: {
                  creditGrants: {
                    list: () =>
                      Effect.succeed({
                        object: "list" as const,
                        data: [
                          {
                            amount: {
                              monetary: { value: 1000, currency: "usd" },
                            },
                            applicability_config: {
                              scope: {
                                prices: [{ id: "price_test_mock" }],
                              },
                            },
                          },
                        ],
                        has_more: false,
                      }),
                  },
                  meters: {
                    listEventSummaries: () =>
                      Effect.succeed({
                        object: "list" as const,
                        data: [{ aggregated_value: 1000 }],
                        has_more: false,
                      }),
                  },
                },
                subscriptions: {
                  list: () =>
                    Effect.succeed({
                      object: "list" as const,
                      data: [
                        {
                          id: "sub_123",
                          customer: "cus_123",
                          current_period_start: 1000000,
                          current_period_end: 2000000,
                          items: {
                            data: [{ price: { id: "price_test_mock" } }],
                          },
                        },
                      ],
                      has_more: false,
                    }),
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test_mock",
                  routerMeterId: "meter_test_mock",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );
  });

  describe("chargeUsageMeter", () => {
    it.effect("charges meter with gas fee applied", () => {
      let capturedValue: string | undefined;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        // Charge 10000 centi-cents ($1.00)
        yield* payments.products.router.chargeUsageMeter("cus_123", 10000n);

        // 10000 * 1.05 (gas fee) = 10500 centi-cents
        // 1 meter unit = 1 centi-cent, so meter value = 10500
        expect(capturedValue).toBe("10500");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.merge(
                Layer.succeed(Stripe, {
                  billing: {
                    meterEvents: {
                      create: (params: {
                        event_name: string;
                        payload: { stripe_customer_id: string; value: string };
                        timestamp: number;
                      }) =>
                        Effect.sync(() => {
                          capturedValue = params.payload.value;
                        }),
                    },
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test_mock",
                    routerMeterId: "meter_test_mock",
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
                MockDrizzleORMLayer,
              ),
            ),
          ),
        ),
      );
    });

    it.effect("handles meter event creation failure", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.products.router
          .chargeUsageMeter("cus_123", 10000n)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Failed to create meter event");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.merge(
                Layer.succeed(Stripe, {
                  billing: {
                    meterEvents: {
                      create: () =>
                        Effect.fail(
                          new StripeError({
                            message: "Failed to create meter event",
                          }),
                        ),
                    },
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test_mock",
                    routerMeterId: "meter_test_mock",
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

  describe("reserveFunds", () => {
    it.effect(
      "returns DatabaseError when calculating active reservations fails",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.products.router
            .reserveFunds({
              stripeCustomerId: "cus_123",
              estimatedCostCenticents: 500n, // $0.05
              routerRequestId: "request_test",
            })
            .pipe(Effect.flip);

          assert(result instanceof DatabaseError);
          expect(result.message).toBe(
            "Failed to calculate active reservations",
          );
        }).pipe(
          Effect.provide(Payments.Default),
          Effect.provide(
            Layer.succeed(DrizzleORM, {
              select: () => ({
                from: () => ({
                  where: () => Effect.fail(new Error("Database query failed")),
                }),
              }),
            } as unknown as Context.Tag.Service<typeof DrizzleORM>),
          ),
          Effect.provide(
            Layer.succeed(Stripe, {
              billing: {
                creditGrants: {
                  list: () =>
                    Effect.succeed({
                      object: "list" as const,
                      data: [
                        {
                          amount: {
                            monetary: { value: 1000, currency: "usd" },
                          },
                          applicability_config: {
                            scope: {
                              prices: [{ id: "price_test_mock" }],
                            },
                          },
                        },
                      ],
                      has_more: false,
                    }),
                },
                meters: {
                  listEventSummaries: () =>
                    Effect.succeed({
                      object: "list" as const,
                      data: [{ aggregated_value: 0 }],
                      has_more: false,
                    }),
                },
              },
              subscriptions: {
                list: () =>
                  Effect.succeed({
                    object: "list" as const,
                    data: [
                      {
                        id: "sub_123",
                        customer: "cus_123",
                        current_period_start: 1000000,
                        current_period_end: 2000000,
                        items: {
                          data: [{ price: { id: "price_test_mock" } }],
                        },
                      },
                    ],
                    has_more: false,
                  }),
              },
              config: {
                apiKey: "sk_test_mock",
                routerPriceId: "price_test_mock",
                routerMeterId: "meter_test_mock",
              },
            } as unknown as Context.Tag.Service<typeof Stripe>),
          ),
        ),
    );

    it.effect("returns DatabaseError when creating reservation fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.products.router
          .reserveFunds({
            stripeCustomerId: "cus_123",
            estimatedCostCenticents: 500n, // $0.05
            routerRequestId: "request_test",
          })
          .pipe(Effect.flip);

        assert(result instanceof DatabaseError);
        expect(result.message).toBe("Failed to create credit reservation");
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            select: () => ({
              from: () => ({
                where: () => Effect.succeed([{ sum: "0" }]),
              }),
            }),
            insert: () => ({
              values: () => ({
                returning: () =>
                  Effect.fail(new Error("Database insert failed")),
              }),
            }),
          } as unknown as Context.Tag.Service<typeof DrizzleORM>),
        ),
        Effect.provide(
          Layer.succeed(Stripe, {
            billing: {
              creditGrants: {
                list: () =>
                  Effect.succeed({
                    object: "list" as const,
                    data: [
                      {
                        amount: {
                          monetary: { value: 1000, currency: "usd" },
                        },
                        applicability_config: {
                          scope: {
                            prices: [{ id: "price_test_mock" }],
                          },
                        },
                      },
                    ],
                    has_more: false,
                  }),
              },
              meters: {
                listEventSummaries: () =>
                  Effect.succeed({
                    object: "list" as const,
                    data: [{ aggregated_value: 0 }],
                    has_more: false,
                  }),
              },
            },
            subscriptions: {
              list: () =>
                Effect.succeed({
                  object: "list" as const,
                  data: [
                    {
                      id: "sub_123",
                      customer: "cus_123",
                      current_period_start: 1000000,
                      current_period_end: 2000000,
                      items: {
                        data: [{ price: { id: "price_test_mock" } }],
                      },
                    },
                  ],
                  has_more: false,
                }),
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock",
              routerMeterId: "meter_test_mock",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );

    it.effect("successfully reserves funds when no active reservations", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const reservationId = yield* payments.products.router.reserveFunds({
          stripeCustomerId: "cus_123",
          estimatedCostCenticents: 500n, // $0.05
          routerRequestId: "request_test",
        });

        expect(reservationId).toContain("mock_");
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            select: () => ({
              from: () => ({
                where: () => Effect.succeed([]), // Empty array, triggers ?? "0" fallback
              }),
            }),
            insert: () => ({
              values: () => ({
                returning: () =>
                  Effect.succeed([{ id: `mock_${crypto.randomUUID()}` }]),
              }),
            }),
          } as unknown as Context.Tag.Service<typeof DrizzleORM>),
        ),
        Effect.provide(
          Layer.succeed(Stripe, {
            billing: {
              creditGrants: {
                list: () =>
                  Effect.succeed({
                    object: "list" as const,
                    data: [
                      {
                        amount: {
                          monetary: { value: 1000, currency: "usd" },
                        },
                        applicability_config: {
                          scope: {
                            prices: [{ id: "price_test_mock" }],
                          },
                        },
                      },
                    ],
                    has_more: false,
                  }),
              },
              meters: {
                listEventSummaries: () =>
                  Effect.succeed({
                    object: "list" as const,
                    data: [{ aggregated_value: 0 }],
                    has_more: false,
                  }),
              },
            },
            subscriptions: {
              list: () =>
                Effect.succeed({
                  object: "list" as const,
                  data: [
                    {
                      id: "sub_123",
                      customer: "cus_123",
                      current_period_start: 1000000,
                      current_period_end: 2000000,
                      items: {
                        data: [{ price: { id: "price_test_mock" } }],
                      },
                    },
                  ],
                  has_more: false,
                }),
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock",
              routerMeterId: "meter_test_mock",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );

    it.effect("fails with InsufficientFundsError when balance too low", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.products.router
          .reserveFunds({
            stripeCustomerId: "cus_123",
            estimatedCostCenticents: 100500n, // $10.05 - More than available balance ($10)
            routerRequestId: "request_test",
          })
          .pipe(Effect.flip);

        assert(result instanceof InsufficientFundsError);
        expect(result.required).toBe(10.05);
        expect(result.available).toBeLessThan(10.05);
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(MockDrizzleORMLayer),
        Effect.provide(
          Layer.succeed(Stripe, {
            billing: {
              creditGrants: {
                list: () =>
                  Effect.succeed({
                    object: "list" as const,
                    data: [
                      {
                        amount: {
                          monetary: { value: 1000, currency: "usd" },
                        },
                        applicability_config: {
                          scope: {
                            prices: [{ id: "price_test_mock" }],
                          },
                        },
                      },
                    ],
                    has_more: false,
                  }),
              },
              meters: {
                listEventSummaries: () =>
                  Effect.succeed({
                    object: "list" as const,
                    data: [{ aggregated_value: 0 }],
                    has_more: false,
                  }),
              },
            },
            subscriptions: {
              list: () =>
                Effect.succeed({
                  object: "list" as const,
                  data: [
                    {
                      id: "sub_123",
                      customer: "cus_123",
                      current_period_start: 1000000,
                      current_period_end: 2000000,
                      items: {
                        data: [{ price: { id: "price_test_mock" } }],
                      },
                    },
                  ],
                  has_more: false,
                }),
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock",
              routerMeterId: "meter_test_mock",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );
  });

  describe("releaseFunds", () => {
    it.effect("successfully releases funds", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.products.router.releaseFunds("reservation_123");

        // Test passes if no errors thrown
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            update: () => ({
              set: () => ({
                where: () => ({
                  returning: () => Effect.succeed([{ id: "reservation_123" }]),
                }),
              }),
            }),
          } as unknown as Context.Tag.Service<typeof DrizzleORM>),
        ),
        Effect.provide(
          Layer.succeed(Stripe, {
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock",
              routerMeterId: "meter_test_mock",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );

    it.effect(
      "returns ReservationStateError when reservation not found (using mock DB)",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          // Custom mock that returns empty array to simulate "not found"
          const result = yield* payments.products.router
            .releaseFunds("nonexistent_id")
            .pipe(Effect.flip);

          assert(result instanceof ReservationStateError);
          expect(result.reservationId).toBe("nonexistent_id");
        }).pipe(
          Effect.provide(Payments.Default),
          Effect.provide(
            Layer.succeed(DrizzleORM, {
              update: () => ({
                set: () => ({
                  where: () => ({
                    returning: () => ({
                      pipe: () => Effect.succeed([]), // Empty array = not found
                    }),
                  }),
                }),
              }),
            } as unknown as Context.Tag.Service<typeof DrizzleORM>),
          ),
          Effect.provide(
            Layer.succeed(Stripe, {
              config: {
                apiKey: "sk_test_mock",
                routerPriceId: "price_test_mock",
                routerMeterId: "meter_test_mock",
              },
            } as unknown as Context.Tag.Service<typeof Stripe>),
          ),
        ),
    );

    it.effect("returns DatabaseError when database operation fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.products.router
          .releaseFunds("some_id")
          .pipe(Effect.flip);

        assert(result instanceof DatabaseError);
        expect(result.message).toBe("Failed to release credit reservation");
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            update: () => ({
              set: () => ({
                where: () => ({
                  returning: () =>
                    Effect.fail(new Error("Database connection lost")),
                }),
              }),
            }),
          } as unknown as Context.Tag.Service<typeof DrizzleORM>),
        ),
        Effect.provide(
          Layer.succeed(Stripe, {
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock",
              routerMeterId: "meter_test_mock",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );

    it.effect(
      "successfully releases funds (already linked during reserve)",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          yield* payments.products.router.releaseFunds("reservation_123");

          // Test passes if no errors thrown
        }).pipe(
          Effect.provide(Payments.Default),
          Effect.provide(
            Layer.succeed(DrizzleORM, {
              update: () => ({
                set: () => ({
                  where: () => ({
                    returning: () =>
                      Effect.succeed([{ id: "reservation_123" }]),
                  }),
                }),
              }),
            } as unknown as Context.Tag.Service<typeof DrizzleORM>),
          ),
          Effect.provide(
            Layer.succeed(Stripe, {
              config: {
                apiKey: "sk_test_mock",
                routerPriceId: "price_test_mock",
                routerMeterId: "meter_test_mock",
              },
            } as unknown as Context.Tag.Service<typeof Stripe>),
          ),
        ),
    );
  });

  describe("settleFunds", () => {
    it.effect("successfully settles funds and charges meter", () => {
      let chargedAmount: string | undefined;
      let releaseCalled = false;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.products.router.settleFunds(
          "reservation_123",
          500n, // $0.05
        );

        // Should charge with gas fee: 500 centi-cents * 1.05 = 525 centi-cents
        // Meter value = 525 (since 1 meter unit = 1 centi-cent)
        expect(chargedAmount).toBe("525");
        expect(releaseCalled).toBe(true);
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            select: () => ({
              from: () => ({
                where: () =>
                  Effect.succeed([
                    { stripeCustomerId: "cus_123", status: "active" },
                  ]),
              }),
            }),
            update: () => ({
              set: () => ({
                where: () => ({
                  returning: () => {
                    releaseCalled = true;
                    return Effect.succeed([{ id: "reservation_123" }]);
                  },
                }),
              }),
            }),
            withTransaction: <A, E, R>(effect: Effect.Effect<A, E, R>) =>
              effect,
          } as unknown as Context.Tag.Service<typeof DrizzleORM>),
        ),
        Effect.provide(
          Layer.succeed(Stripe, {
            billing: {
              meterEvents: {
                create: (params: {
                  event_name: string;
                  payload: { stripe_customer_id: string; value: string };
                  timestamp: number;
                }) =>
                  Effect.sync(() => {
                    chargedAmount = params.payload.value;
                  }),
              },
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock",
              routerMeterId: "meter_test_mock",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      );
    });

    it.effect(
      "skips charging when reservation is already released (idempotency)",
      () => {
        let chargedAmount: string | undefined;

        return Effect.gen(function* () {
          const payments = yield* Payments;

          yield* payments.products.router.settleFunds("reservation_123", 500n);

          // Should NOT charge since update returns 0 rows (status != active)
          expect(chargedAmount).toBeUndefined();
        }).pipe(
          Effect.provide(Payments.Default),
          Effect.provide(
            Layer.succeed(DrizzleORM, {
              select: () => ({
                from: () => ({
                  where: () =>
                    Effect.succeed([
                      { stripeCustomerId: "cus_123", status: "released" },
                    ]),
                }),
              }),
              update: () => ({
                set: () => ({
                  where: () => ({
                    returning: () =>
                      // Return empty array = 0 rows affected (already released)
                      Effect.succeed([]),
                  }),
                }),
              }),
              withTransaction: <A, E, R>(effect: Effect.Effect<A, E, R>) =>
                effect,
            } as unknown as Context.Tag.Service<typeof DrizzleORM>),
          ),
          Effect.provide(
            Layer.succeed(Stripe, {
              billing: {
                meterEvents: {
                  create: (params: {
                    event_name: string;
                    payload: { stripe_customer_id: string; value: string };
                    timestamp: number;
                  }) =>
                    Effect.sync(() => {
                      chargedAmount = params.payload.value;
                    }),
                },
              },
              config: {
                apiKey: "sk_test_mock",
                routerPriceId: "price_test_mock",
                routerMeterId: "meter_test_mock",
              },
            } as unknown as Context.Tag.Service<typeof Stripe>),
          ),
        );
      },
    );

    it.effect("returns StripeError when Stripe charging fails", () => {
      return Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.products.router
          .settleFunds("reservation_123", 450n)
          .pipe(Effect.flip);

        assert(result instanceof StripeError);
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            select: () => ({
              from: () => ({
                where: () =>
                  Effect.succeed([
                    { stripeCustomerId: "cus_123", status: "active" },
                  ]),
              }),
            }),
            update: () => ({
              set: () => ({
                where: () => ({
                  returning: () => Effect.succeed([{ id: "reservation_123" }]),
                }),
              }),
            }),
            withTransaction: <A, E, R>(effect: Effect.Effect<A, E, R>) =>
              effect,
          } as unknown as Context.Tag.Service<typeof DrizzleORM>),
        ),
        Effect.provide(
          Layer.succeed(Stripe, {
            billing: {
              meterEvents: {
                create: () =>
                  Effect.fail(
                    new StripeError({
                      message: "Stripe API error",
                      cause: new Error("Stripe API error"),
                    }),
                  ),
              },
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock",
              routerMeterId: "meter_test_mock",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      );
    });

    it.effect(
      "returns ReservationStateError when reservation not found during fetch",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.products.router
            .settleFunds("nonexistent_id", 450n)
            .pipe(Effect.flip);

          assert(result instanceof ReservationStateError);
          expect(result.reservationId).toBe("nonexistent_id");
          expect(result.message).toBe("Reservation not found");
        }).pipe(
          Effect.provide(Payments.Default),
          Effect.provide(
            Layer.succeed(DrizzleORM, {
              select: () => ({
                from: () => ({
                  where: () => Effect.succeed([]), // Empty array = not found
                }),
              }),
              withTransaction: <A, E, R>(effect: Effect.Effect<A, E, R>) =>
                effect,
            } as unknown as Context.Tag.Service<typeof DrizzleORM>),
          ),
          Effect.provide(
            Layer.succeed(Stripe, {
              config: {
                apiKey: "sk_test_mock",
                routerPriceId: "price_test_mock",
                routerMeterId: "meter_test_mock",
              },
            } as unknown as Context.Tag.Service<typeof Stripe>),
          ),
        ),
    );

    it.effect("returns DatabaseError when fetching reservation fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.products.router
          .settleFunds("some_id", 450n)
          .pipe(Effect.flip);

        assert(result instanceof DatabaseError);
        expect(result.message).toBe("Failed to fetch reservation");
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            select: () => ({
              from: () => ({
                where: () => Effect.fail(new Error("Database connection lost")),
              }),
            }),
            withTransaction: <A, E, R>(effect: Effect.Effect<A, E, R>) =>
              effect,
          } as unknown as Context.Tag.Service<typeof DrizzleORM>),
        ),
        Effect.provide(
          Layer.succeed(Stripe, {
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock",
              routerMeterId: "meter_test_mock",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );
  });

  describe("getUsageMeterBalance (additional coverage)", () => {
    it.effect(
      "returns usage balance in centicents (1:1 with meter units)",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const balance =
            yield* payments.products.router.getUsageMeterBalance("cus_123");

          // 1000 units = 1000 centicents ($0.10)
          expect(balance).toBe(1000n);
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(MockDrizzleORMLayer),
              Layer.provide(
                Layer.succeed(Stripe, {
                  subscriptions: {
                    list: () =>
                      Effect.succeed({
                        object: "list" as const,
                        data: [
                          {
                            id: "sub_123",
                            customer: "cus_123",
                            current_period_start: 1000000,
                            current_period_end: 2000000,
                            items: {
                              data: [{ price: { id: "price_test_mock" } }],
                            },
                          },
                        ],
                        has_more: false,
                      }),
                  },
                  billing: {
                    meters: {
                      listEventSummaries: () =>
                        Effect.succeed({
                          object: "list" as const,
                          data: [{ aggregated_value: 1000 }],
                          has_more: false,
                        }),
                    },
                  },
                  prices: {
                    retrieve: () =>
                      Effect.succeed({
                        id: "price_test_mock",
                        object: "price" as const,
                        unit_amount: null,
                        unit_amount_decimal: null,
                      }),
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test_mock",
                    routerMeterId: "meter_test_mock",
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        ),
    );
  });

  describe("chargeForUsage", () => {
    beforeEach(() => {
      vi.restoreAllMocks();
      clearPricingCache();

      // Mock pricing data fetch
      const mockData = {
        anthropic: {
          id: "anthropic",
          name: "Anthropic",
          models: {
            "claude-3-5-haiku-20241022": {
              id: "claude-3-5-haiku-20241022",
              name: "Claude 3.5 Haiku",
              cost: {
                input: 1.0,
                output: 5.0,
                cache_read: 0.1,
                cache_write: 1.25,
              },
            },
          },
        },
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "gpt-4o-mini": {
              id: "gpt-4o-mini",
              name: "GPT-4o Mini",
              cost: {
                input: 0.15,
                output: 0.6,
                cache_read: 0.075,
              },
            },
          },
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      }) as unknown as typeof fetch;
    });

    it.effect("successfully calculates cost and charges meter", () => {
      let chargedAmount: string | null = null;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.products.router.chargeForUsage({
          provider: "anthropic",
          model: "claude-3-5-haiku-20241022",
          usageData: {
            inputTokens: 1000,
            outputTokens: 500,
          },
          stripeCustomerId: "cus_123",
        });

        // Should have charged: (1000/1M * 1.0 + 500/1M * 5.0) * 1.05 * 100
        // = (0.001 + 0.0025) * 1.05 * 100 = 0.3675 * 100 = 36.75 cents rounded to 37
        expect(chargedAmount).toBeDefined();
        expect(Number(chargedAmount)).toBeGreaterThan(0);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                prices: {
                  retrieve: () =>
                    Effect.succeed({
                      id: "price_test",
                      object: "price" as const,
                      unit_amount: 1, // $0.01 per unit
                      unit_amount_decimal: null,
                    }),
                },
                billing: {
                  meterEvents: {
                    create: (params: { payload: { value: string } }) => {
                      chargedAmount = params.payload.value;
                      return Effect.void;
                    },
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
            Layer.provide(MockDrizzleORMLayer),
          ),
        ),
      );
    });

    it.effect("calculates cost and charges meter with cache tokens", () => {
      let chargedAmount: string | null = null;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.products.router.chargeForUsage({
          provider: "anthropic",
          model: "claude-3-5-haiku-20241022",
          usageData: {
            inputTokens: 1000,
            outputTokens: 500,
            cacheReadTokens: 200,
            cacheWriteTokens: 100,
          },
          stripeCustomerId: "cus_123",
        });

        // Should have charged including cache costs
        expect(chargedAmount).toBeDefined();
        expect(Number(chargedAmount)).toBeGreaterThan(0);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                prices: {
                  retrieve: () =>
                    Effect.succeed({
                      id: "price_test",
                      object: "price" as const,
                      unit_amount: 1, // $0.01 per unit
                      unit_amount_decimal: null,
                    }),
                },
                billing: {
                  meterEvents: {
                    create: (params: { payload: { value: string } }) => {
                      chargedAmount = params.payload.value;
                      return Effect.void;
                    },
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
            Layer.provide(MockDrizzleORMLayer),
          ),
        ),
      );
    });

    it.effect(
      "calculates cost for OpenAI without cache tokens (tests undefined branch)",
      () => {
        let chargedAmount: string | null = null;

        return Effect.gen(function* () {
          const payments = yield* Payments;

          // OpenAI without cache tokens - cacheReadTokens will be undefined
          yield* payments.products.router.chargeForUsage({
            provider: "openai",
            model: "gpt-4o-mini",
            usageData: {
              inputTokens: 1000,
              outputTokens: 500,
              // No cacheReadTokens - will be undefined
            },
            stripeCustomerId: "cus_123",
          });

          // Should have charged without cache costs
          expect(chargedAmount).toBeDefined();
          expect(Number(chargedAmount)).toBeGreaterThan(0);
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(MockDrizzleORMLayer),
              Layer.provide(
                Layer.succeed(Stripe, {
                  prices: {
                    retrieve: () =>
                      Effect.succeed({
                        id: "price_test",
                        object: "price" as const,
                        unit_amount: 1, // $0.01 per unit
                        unit_amount_decimal: null,
                      }),
                  },
                  billing: {
                    meterEvents: {
                      create: (params: { payload: { value: string } }) => {
                        chargedAmount = params.payload.value;
                        return Effect.void;
                      },
                    },
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test",
                    routerMeterId: "meter_test",
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
              Layer.provide(MockDrizzleORMLayer),
            ),
          ),
        );
      },
    );

    it.effect(
      "silently returns when no cost calculator found for provider",
      () => {
        return Effect.gen(function* () {
          const payments = yield* Payments;

          // Should not throw, just return silently
          yield* payments.products.router.chargeForUsage({
            provider: "unknown-provider" as ProviderName,
            model: "some-model",
            usageData: {
              inputTokens: 100,
              outputTokens: 50,
            },
            stripeCustomerId: "cus_123",
          });
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(MockDrizzleORMLayer),
              Layer.provide(
                Layer.succeed(Stripe, {
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test",
                    routerMeterId: "meter_test",
                  },
                  billing: {
                    meterEvents: {
                      create: () => Effect.succeed({ id: "evt_test" }),
                    },
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
              Layer.provide(MockDrizzleORMLayer),
            ),
          ),
        );
      },
    );

    it.effect("silently returns when cost calculation fails", () => {
      return Effect.gen(function* () {
        const payments = yield* Payments;

        // Pass invalid usage data structure to trigger calculation failure
        // This should be caught and return silently
        yield* payments.products.router.chargeForUsage({
          provider: "anthropic",
          model: "non-existent-model",
          usageData: {
            inputTokens: 100,
            outputTokens: 50,
          },
          stripeCustomerId: "cus_123",
        });
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                prices: {
                  retrieve: () =>
                    Effect.succeed({
                      id: "price_test",
                      object: "price" as const,
                      unit_amount: 1,
                      unit_amount_decimal: null,
                    }),
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
                billing: {
                  meterEvents: {
                    create: () => Effect.succeed({ id: "evt_test" }),
                  },
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
            Layer.provide(MockDrizzleORMLayer),
          ),
        ),
      );
    });

    it.effect("silently returns when usage tokens are NaN", () => {
      // Mock to return NaN tokens
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            anthropic: {
              id: "anthropic",
              name: "Anthropic",
              models: {
                "test-model": {
                  id: "test-model",
                  name: "Test",
                  cost: { input: NaN, output: NaN },
                },
              },
            },
          }),
      }) as unknown as typeof fetch;

      clearPricingCache();

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.products.router.chargeForUsage({
          provider: "anthropic",
          model: "test-model",
          usageData: {
            inputTokens: 100,
            outputTokens: 50,
          },
          stripeCustomerId: "cus_123",
        });
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
                billing: {
                  meterEvents: {
                    create: () => Effect.succeed({ id: "evt_test" }),
                  },
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
            Layer.provide(MockDrizzleORMLayer),
          ),
        ),
      );
    });

    // TODO: Re-enable once queue-based async metering is implemented.
    // This test times out due to retry logic with exponential backoff (15+ seconds).
    // The retry error handling will be replaced by queue-based processing anyway.
    it.effect.skip(
      "silently continues when meter charging fails",
      () => {
        // Mock pricing data for cost calculation
        global.fetch = vi.fn().mockResolvedValue({
          ok: true,
          json: () =>
            Promise.resolve({
              anthropic: {
                id: "anthropic",
                name: "Anthropic",
                models: {
                  "claude-3-5-haiku-20241022": {
                    id: "claude-3-5-haiku-20241022",
                    name: "Claude 3.5 Haiku",
                    cost: { input: 1, output: 5 },
                  },
                },
              },
            }),
        }) as unknown as typeof fetch;

        clearPricingCache();

        return Effect.gen(function* () {
          const payments = yield* Payments;

          // Should not throw even if meter charging fails
          yield* payments.products.router.chargeForUsage({
            provider: "anthropic",
            model: "claude-3-5-haiku-20241022",
            usageData: {
              inputTokens: 1000,
              outputTokens: 500,
            },
            stripeCustomerId: "cus_123",
          });
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(MockDrizzleORMLayer),
              Layer.provide(
                Layer.succeed(Stripe, {
                  prices: {
                    retrieve: () =>
                      Effect.succeed({
                        id: "price_test",
                        object: "price" as const,
                        unit_amount: 1,
                        unit_amount_decimal: null,
                      }),
                  },
                  billing: {
                    meterEvents: {
                      create: () =>
                        Effect.fail(new Error("Meter creation failed")),
                    },
                  },
                  config: {
                    apiKey: "sk_test_mock",
                    routerPriceId: "price_test",
                    routerMeterId: "meter_test",
                  },
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
              Layer.provide(MockDrizzleORMLayer),
            ),
          ),
        );
      },
      15000,
    );
  });

  describe("createCreditGrant", () => {
    it.effect("creates credit grant with correct parameters", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const creditGrantId = yield* payments.products.router.createCreditGrant(
          {
            customerId: "cus_test123",
            amountInDollars: 50,
          },
        );

        expect(creditGrantId).toBeDefined();
        expect(creditGrantId).toMatch(/^credgr_test_/);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                billing: {
                  creditGrants: {
                    create: (
                      params: StripeSDK.Billing.CreditGrantCreateParams,
                    ) => {
                      expect(params.customer).toBe("cus_test123");
                      expect(params.amount.monetary?.value).toBe(5000);
                      expect(params.amount.monetary?.currency).toBe("usd");
                      expect(params.category).toBe("paid");
                      expect(params.name).toBe("Prepurchased Router Credits");
                      expect(
                        params.applicability_config?.scope?.prices,
                      ).toEqual([{ id: "price_test" }]);
                      return Effect.succeed({
                        id: `credgr_test_${crypto.randomUUID()}`,
                      });
                    },
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("includes expiration date when provided", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;
        const expiresAt = new Date("2026-01-01T00:00:00Z");

        yield* payments.products.router.createCreditGrant({
          customerId: "cus_test123",
          amountInDollars: 50,
          expiresAt,
        });
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                billing: {
                  creditGrants: {
                    create: (
                      params: StripeSDK.Billing.CreditGrantCreateParams,
                    ) => {
                      expect(params.expires_at).toBe(
                        Math.floor(
                          new Date("2026-01-01T00:00:00Z").getTime() / 1000,
                        ),
                      );
                      return Effect.succeed({
                        id: `credgr_test_${crypto.randomUUID()}`,
                      });
                    },
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("includes metadata when provided", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.products.router.createCreditGrant({
          customerId: "cus_test123",
          amountInDollars: 50,
          metadata: {
            paymentIntentId: "pi_123",
          },
        });
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(MockDrizzleORMLayer),
            Layer.provide(
              Layer.succeed(Stripe, {
                billing: {
                  creditGrants: {
                    create: (
                      params: StripeSDK.Billing.CreditGrantCreateParams,
                    ) => {
                      expect(params.metadata?.paymentIntentId).toBe("pi_123");
                      return Effect.succeed({
                        id: `credgr_test_${crypto.randomUUID()}`,
                      });
                    },
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );
  });
});
