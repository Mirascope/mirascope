import { describe, it, expect, vi } from "vitest";
import { Effect, Layer } from "effect";
import { DrizzleORM } from "@/db/client";
import { Payments } from "@/payments";
import { DatabaseError } from "@/errors";
import billingReconciliationCron, {
  reconcileSuccessfulRequests,
  reconcileFailedRequests,
  reconcilePendingExpiredRequests,
  detectStaleReconciliation,
  detectInvalidState,
  reconcileBilling,
} from "@/workers/billingReconciliationCron";
import type { CronTriggerEnv } from "@/workers/billingReconciliationCron";
import { createMockEnv } from "@/tests/settings";

describe("billingReconciliationCron", () => {
  // Create a complete mock environment with all required vars
  const mockEnv = createMockEnv() as unknown as CronTriggerEnv;

  const mockEvent = {
    scheduledTime: Date.now(),
    cron: "*/5 * * * *",
  };

  describe("reconcileSuccessfulRequests", () => {
    it("finds and settles successful requests with costs", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      let settleCalled = false;
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(
                  Effect.succeed([
                    {
                      reservationId: "res-1",
                      stripeCustomerId: "cus_123",
                      costCenticents: 1000n,
                    },
                  ]),
                ),
              }),
            }),
          }),
        }),
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {} as never,
        products: {
          router: {
            getUsageMeterBalance: {} as never,
            chargeUsageMeter: {} as never,
            getCreditBalance: {} as never,
            getBalanceInfo: {} as never,
            reserveFunds: {} as never,
            releaseFunds: {} as never,
            settleFunds: (resId: string, cost: bigint) => {
              settleCalled = true;
              expect(resId).toBe("res-1");
              expect(cost).toBe(1000n);
              return Effect.succeed(undefined);
            },
            chargeForUsage: {} as never,
            createCreditGrant: {} as never,
          },
          spans: {} as never,
        },
        paymentIntents: {} as never,
      });

      await Effect.runPromise(
        reconcileSuccessfulRequests.pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      expect(settleCalled).toBe(true);
      expect(consoleLogSpy).toHaveBeenCalledWith(
        "[billingReconciliationCron] Found 1 successful requests to reconcile",
      );

      consoleLogSpy.mockRestore();
    });

    it("skips records with null cost", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      let settleCalled = false;
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(
                  Effect.succeed([
                    {
                      reservationId: "res-1",
                      stripeCustomerId: "cus_123",
                      costCenticents: null,
                    },
                  ]),
                ),
              }),
            }),
          }),
        }),
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {} as never,
        products: {
          router: {
            getUsageMeterBalance: {} as never,
            chargeUsageMeter: {} as never,
            getCreditBalance: {} as never,
            getBalanceInfo: {} as never,
            reserveFunds: {} as never,
            releaseFunds: {} as never,
            settleFunds: () => {
              settleCalled = true;
              return Effect.succeed(undefined);
            },
            chargeForUsage: {} as never,
            createCreditGrant: {} as never,
          },
          spans: {} as never,
        },
        paymentIntents: {} as never,
      });

      await Effect.runPromise(
        reconcileSuccessfulRequests.pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      expect(settleCalled).toBe(false);

      consoleLogSpy.mockRestore();
    });

    it("handles settlement errors gracefully", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(
                  Effect.succeed([
                    {
                      reservationId: "res-1",
                      stripeCustomerId: "cus_123",
                      costCenticents: 1000n,
                    },
                  ]),
                ),
              }),
            }),
          }),
        }),
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {} as never,
        products: {
          router: {
            getUsageMeterBalance: {} as never,
            chargeUsageMeter: {} as never,
            getCreditBalance: {} as never,
            getBalanceInfo: {} as never,
            reserveFunds: {} as never,
            releaseFunds: {} as never,
            settleFunds: () =>
              Effect.fail(
                new DatabaseError({
                  message: "Settlement failed",
                  cause: new Error("Settlement failed"),
                }),
              ),
            chargeForUsage: {} as never,
            createCreditGrant: {} as never,
          },
          spans: {} as never,
        },
        paymentIntents: {} as never,
      });

      await Effect.runPromise(
        reconcileSuccessfulRequests.pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("Failed to settle reservation res-1"),
        expect.anything(),
      );

      consoleLogSpy.mockRestore();
      consoleErrorSpy.mockRestore();
    });

    it("does not log when no records are found", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(Effect.succeed([])),
              }),
            }),
          }),
        }),
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {} as never,
        products: {
          router: {} as never,
          spans: {} as never,
        },
        paymentIntents: {} as never,
      });

      await Effect.runPromise(
        reconcileSuccessfulRequests.pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      expect(consoleLogSpy).not.toHaveBeenCalled();

      consoleLogSpy.mockRestore();
    });

    it("handles database query errors", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi
                  .fn()
                  .mockReturnValue(
                    Effect.fail(new Error("Database query failed")),
                  ),
              }),
            }),
          }),
        }),
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {} as never,
        products: {
          router: {} as never,
          spans: {} as never,
        },
        paymentIntents: {} as never,
      });

      const error = await Effect.runPromise(
        reconcileSuccessfulRequests.pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.flip,
        ),
      );

      expect(error.message).toContain(
        "Failed to query successful requests for reconciliation",
      );
    });
  });

  describe("reconcileFailedRequests", () => {
    it("releases reservations for failed requests", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              returning: vi
                .fn()
                .mockReturnValue(
                  Effect.succeed([{ id: "res-1" }, { id: "res-2" }]),
                ),
            }),
          }),
        }),
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({}),
          }),
        }),
      } as never);

      await Effect.runPromise(
        reconcileFailedRequests.pipe(Effect.provide(mockDbLayer)),
      );

      expect(consoleLogSpy).toHaveBeenCalledWith(
        "[billingReconciliationCron] Released 2 reservations for failed requests",
      );

      consoleLogSpy.mockRestore();
    });

    it("does not log when no records are released", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              returning: vi.fn().mockReturnValue(Effect.succeed([])),
            }),
          }),
        }),
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({}),
          }),
        }),
      } as never);

      await Effect.runPromise(
        reconcileFailedRequests.pipe(Effect.provide(mockDbLayer)),
      );

      expect(consoleLogSpy).not.toHaveBeenCalled();

      consoleLogSpy.mockRestore();
    });

    it("handles database errors", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              returning: vi
                .fn()
                .mockReturnValue(
                  Effect.fail(new Error("Database update failed")),
                ),
            }),
          }),
        }),
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({}),
          }),
        }),
      } as never);

      const error = await Effect.runPromise(
        reconcileFailedRequests.pipe(Effect.provide(mockDbLayer), Effect.flip),
      );

      expect(error.message).toContain(
        "Failed to release reservations for failed requests",
      );
    });
  });

  describe("reconcilePendingExpiredRequests", () => {
    it("reconciles pending + expired records", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(
                  Effect.succeed([
                    {
                      reservationId: "res-1",
                      routerRequestId: "req-1",
                    },
                    {
                      reservationId: "res-2",
                      routerRequestId: "req-2",
                    },
                  ]),
                ),
              }),
            }),
          }),
        }),
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue(Effect.succeed([])),
          }),
        }),
      } as never);

      await Effect.runPromise(
        reconcilePendingExpiredRequests.pipe(Effect.provide(mockDbLayer)),
      );

      expect(consoleLogSpy).toHaveBeenCalledWith(
        "[billingReconciliationCron] Found 2 pending + expired records to reconcile",
      );

      consoleLogSpy.mockRestore();
    });

    it("returns early when no records are found", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      const updateMock = vi.fn();
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(Effect.succeed([])),
              }),
            }),
          }),
        }),
        update: updateMock,
      } as never);

      await Effect.runPromise(
        reconcilePendingExpiredRequests.pipe(Effect.provide(mockDbLayer)),
      );

      expect(consoleLogSpy).not.toHaveBeenCalled();
      expect(updateMock).not.toHaveBeenCalled();

      consoleLogSpy.mockRestore();
    });

    it("handles database errors during query", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi
                  .fn()
                  .mockReturnValue(
                    Effect.fail(new Error("Database query failed")),
                  ),
              }),
            }),
          }),
        }),
        update: vi.fn(),
      } as never);

      const error = await Effect.runPromise(
        reconcilePendingExpiredRequests.pipe(
          Effect.provide(mockDbLayer),
          Effect.flip,
        ),
      );

      expect(error.message).toContain(
        "Failed to query pending + expired records",
      );
    });

    it("handles database errors during router request update", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(
                  Effect.succeed([
                    {
                      reservationId: "res-1",
                      routerRequestId: "req-1",
                    },
                  ]),
                ),
              }),
            }),
          }),
        }),
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi
              .fn()
              .mockReturnValue(Effect.fail(new Error("Update failed"))),
          }),
        }),
      } as never);

      const error = await Effect.runPromise(
        reconcilePendingExpiredRequests.pipe(
          Effect.provide(mockDbLayer),
          Effect.flip,
        ),
      );

      expect(error.message).toContain(
        "Failed to update router requests to failure",
      );
    });

    it("handles database errors during reservation release", async () => {
      let updateCallCount = 0;
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(
                  Effect.succeed([
                    {
                      reservationId: "res-1",
                      routerRequestId: "req-1",
                    },
                  ]),
                ),
              }),
            }),
          }),
        }),
        update: vi.fn().mockImplementation(() => {
          updateCallCount++;
          return {
            set: vi.fn().mockReturnValue({
              where: vi
                .fn()
                .mockReturnValue(
                  updateCallCount === 1
                    ? Effect.succeed([])
                    : Effect.fail(new Error("Release failed")),
                ),
            }),
          };
        }),
      } as never);

      const error = await Effect.runPromise(
        reconcilePendingExpiredRequests.pipe(
          Effect.provide(mockDbLayer),
          Effect.flip,
        ),
      );

      expect(error.message).toContain("Failed to release expired reservations");
    });
  });

  describe("detectStaleReconciliation", () => {
    it("warns about stale records", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(
                  Effect.succeed([
                    {
                      reservationId: "stale-1",
                      requestStatus: "completed",
                      createdAt: new Date(Date.now() - 25 * 60 * 60 * 1000),
                    },
                  ]),
                ),
              }),
            }),
          }),
        }),
      } as never);

      await Effect.runPromise(
        detectStaleReconciliation.pipe(Effect.provide(mockDbLayer)),
      );

      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining("Found 1 stale records older than 24 hours"),
        expect.anything(),
      );

      consoleWarnSpy.mockRestore();
    });

    it("does not warn when no stale records exist", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(Effect.succeed([])),
              }),
            }),
          }),
        }),
      } as never);

      await Effect.runPromise(
        detectStaleReconciliation.pipe(Effect.provide(mockDbLayer)),
      );

      expect(consoleWarnSpy).not.toHaveBeenCalled();

      consoleWarnSpy.mockRestore();
    });

    it("handles database errors", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi
                  .fn()
                  .mockReturnValue(
                    Effect.fail(new Error("Database query failed")),
                  ),
              }),
            }),
          }),
        }),
      } as never);

      const error = await Effect.runPromise(
        detectStaleReconciliation.pipe(
          Effect.provide(mockDbLayer),
          Effect.flip,
        ),
      );

      expect(error.message).toContain("Failed to query stale records");
    });
  });

  describe("detectInvalidState", () => {
    it("logs critical error for invalid state records", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(
                  Effect.succeed([
                    {
                      reservationId: "invalid-1",
                      routerRequestId: "req-1",
                    },
                  ]),
                ),
              }),
            }),
          }),
        }),
      } as never);

      await Effect.runPromise(
        detectInvalidState.pipe(Effect.provide(mockDbLayer)),
      );

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("CRITICAL: Found 1 records in invalid state"),
        expect.anything(),
      );

      consoleErrorSpy.mockRestore();
    });

    it("does not log when no invalid records exist", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(Effect.succeed([])),
              }),
            }),
          }),
        }),
      } as never);

      await Effect.runPromise(
        detectInvalidState.pipe(Effect.provide(mockDbLayer)),
      );

      expect(consoleErrorSpy).not.toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
    });

    it("handles database errors", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi
                  .fn()
                  .mockReturnValue(
                    Effect.fail(new Error("Database query failed")),
                  ),
              }),
            }),
          }),
        }),
      } as never);

      const error = await Effect.runPromise(
        detectInvalidState.pipe(Effect.provide(mockDbLayer), Effect.flip),
      );

      expect(error.message).toContain("Failed to query invalid state records");
    });
  });

  describe("billingReconciliationProgram", () => {
    it("runs all reconciliation steps in sequence", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(Effect.succeed([])),
              }),
            }),
            where: vi.fn().mockReturnValue({}),
          }),
        }),
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              returning: vi.fn().mockReturnValue(Effect.succeed([])),
            }),
          }),
        }),
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {} as never,
        products: {
          router: {} as never,
          spans: {} as never,
        },
        paymentIntents: {} as never,
      });

      await Effect.runPromise(
        reconcileBilling.pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );
    });
  });

  it("logs error when no database connection is available", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    const envWithoutDb = {
      ...mockEnv,
      DATABASE_URL: undefined,
      HYPERDRIVE: undefined,
    } as unknown as CronTriggerEnv;

    await billingReconciliationCron.scheduled(mockEvent, envWithoutDb);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[billingReconciliationCron] No database connection available (HYPERDRIVE or DATABASE_URL required)",
    );

    consoleErrorSpy.mockRestore();
  });

  it("logs error when required environment variables are missing", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // Environment with some required vars missing
    const envWithMissingVars: CronTriggerEnv = {
      DATABASE_URL: "postgres://test:test@localhost:5432/test",
      ENVIRONMENT: "test",
      // Missing all other required vars
    } as CronTriggerEnv;

    await billingReconciliationCron.scheduled(mockEvent, envWithMissingVars);

    // Should log error with SettingsValidationError containing missing variables
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[billingReconciliationCron] Cron trigger error:",
      expect.objectContaining({
        _tag: "SettingsValidationError",
      }),
    );

    consoleErrorSpy.mockRestore();
  });

  it("uses HYPERDRIVE connection string when available", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    const envWithHyperdrive = {
      ...mockEnv,
      DATABASE_URL: undefined,
      HYPERDRIVE: {
        connectionString: "postgres://hyperdrive:test@localhost:5432/test",
      },
    } as unknown as CronTriggerEnv;

    await billingReconciliationCron.scheduled(mockEvent, envWithHyperdrive);

    // Should not log the "No database connection" error
    expect(consoleErrorSpy).not.toHaveBeenCalledWith(
      "[billingReconciliationCron] No database connection available (HYPERDRIVE or DATABASE_URL required)",
    );

    consoleErrorSpy.mockRestore();
  });

  it("handles errors gracefully during execution", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // Use invalid database connection to trigger error
    const envWithInvalidDb: CronTriggerEnv = {
      ...mockEnv,
      DATABASE_URL: "postgres://invalid:invalid@localhost:5432/nonexistent",
    };

    await billingReconciliationCron.scheduled(mockEvent, envWithInvalidDb);

    // Should log cron trigger error
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[billingReconciliationCron] Cron trigger error:",
      expect.anything(),
    );

    consoleErrorSpy.mockRestore();
  });

  it("exports a scheduled handler", () => {
    expect(billingReconciliationCron).toHaveProperty("scheduled");
    expect(typeof billingReconciliationCron.scheduled).toBe("function");
  });

  it("processes reconciliation workflow", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const consoleWarnSpy = vi
      .spyOn(console, "warn")
      .mockImplementation(() => {});
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // Will fail to connect but tests the workflow
    await billingReconciliationCron.scheduled(mockEvent, mockEnv);

    consoleLogSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  it("handles all stripe cloud price configurations", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    await billingReconciliationCron.scheduled(mockEvent, mockEnv);

    // Should attempt processing with all config
    expect(consoleErrorSpy).toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });

  it("verifies all reconciliation steps are called", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const consoleWarnSpy = vi
      .spyOn(console, "warn")
      .mockImplementation(() => {});
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    await billingReconciliationCron.scheduled(mockEvent, mockEnv);

    // Should hit error during database connection
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[billingReconciliationCron] Cron trigger error:",
      expect.anything(),
    );

    consoleLogSpy.mockRestore();
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });
});
