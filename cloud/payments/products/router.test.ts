import { describe, it, expect } from "@effect/vitest";
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
import { assert } from "@/tests/db";
import { DrizzleORM } from "@/db/client";

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
        // Active reservations: 5000 centi-cents ($0.50)
        expect(balanceInfo.activeReservations).toBe(5000n);
        // Available: 100000 - 1000 = 99000 centi-cents ($9.90)
        expect(balanceInfo.availableBalance).toBe(99000n);
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            select: () => ({
              from: () => ({
                where: () => Effect.succeed([{ sum: "5000" }]), // Mock active reservations
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

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.products.router.settleFunds(
          "reservation_123",
          500n, // $0.05
        );

        // Should charge with gas fee: 500 centi-cents * 1.05 = 525 centi-cents
        // Meter value = 525 (since 1 meter unit = 1 centi-cent)
        expect(chargedAmount).toBe("525");
      }).pipe(
        Effect.provide(Payments.Default),
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            select: () => ({
              from: () => ({
                where: () => Effect.succeed([{ customerId: "cus_123" }]),
              }),
            }),
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
      "returns ReservationStateError when release fails (reservation not found)",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.products.router
            .settleFunds("reservation_123", 450n)
            .pipe(Effect.flip);

          assert(result instanceof ReservationStateError);
        }).pipe(
          Effect.provide(Payments.Default),
          Effect.provide(
            Layer.succeed(DrizzleORM, {
              select: () => ({
                from: () => ({
                  where: () => Effect.succeed([{ customerId: "cus_123" }]),
                }),
              }),
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

    it.effect("returns StripeError when meter charging fails", () =>
      Effect.gen(function* () {
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
                where: () => Effect.succeed([{ customerId: "cus_123" }]),
              }),
            }),
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
            billing: {
              meterEvents: {
                create: () =>
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
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );
  });
});
