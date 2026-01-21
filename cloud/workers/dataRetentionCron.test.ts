import { describe, it, expect, vi } from "vitest";
import { Effect, Layer } from "effect";
import { DrizzleORM } from "@/db/client";
import { ClickHouse } from "@/db/clickhouse/client";
import { Payments } from "@/payments";
import { ClickHouseError, DatabaseError } from "@/errors";
import dataRetentionCron, {
  enforceDataRetentionLimits,
} from "@/workers/dataRetentionCron";
import type { CronTriggerEnv } from "@/workers/dataRetentionCron";
import { createMockEnv } from "@/tests/settings";

describe("dataRetentionCron", () => {
  const mockEnvironment = createMockEnv() as unknown as CronTriggerEnv;

  const mockEvent = {
    scheduledTime: Date.now(),
    cron: "0 10 * * *",
  };

  describe("enforceDataRetentionLimits", () => {
    it("deletes expired data for each retention group", async () => {
      const organizationFreeOne = "11111111-1111-1111-1111-111111111111";
      const organizationFreeTwo = "22222222-2222-2222-2222-222222222222";
      const organizationTeam = "33333333-3333-3333-3333-333333333333";

      const deleteSpy = vi.fn().mockImplementation(() => ({
        where: vi.fn().mockReturnValue({
          returning: vi.fn().mockReturnValue(Effect.succeed([])),
        }),
      }));

      const mockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi
            .fn()
            .mockReturnValue(
              Effect.succeed([
                { id: organizationFreeOne },
                { id: organizationFreeTwo },
                { id: organizationTeam },
              ]),
            ),
        }),
        delete: deleteSpy,
      } as never);

      const getPlan = vi.fn((organizationId: string) =>
        Effect.succeed(organizationId === organizationTeam ? "team" : "free"),
      );

      const getPlanLimits = vi.fn((planTier: "free" | "pro" | "team") =>
        Effect.succeed({
          seats: planTier === "free" ? 1 : 5,
          projects: planTier === "free" ? 1 : 5,
          spansPerMonth: planTier === "free" ? 1_000_000 : Infinity,
          apiRequestsPerMinute: planTier === "free" ? 100 : 1000,
          dataRetentionDays: planTier === "team" ? 180 : 30,
        }),
      );

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan,
            getPlanLimits,
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
      });

      const executedQueries: string[] = [];
      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        unsafeQuery: () => Effect.succeed([]),
        insert: () => Effect.succeed(undefined),
        command: (query: string) => {
          executedQueries.push(query);
          return Effect.succeed(undefined);
        },
      } as never);

      await Effect.runPromise(
        enforceDataRetentionLimits.pipe(
          Effect.provide(mockDrizzleLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.provide(mockClickHouseLayer),
        ),
      );

      const spanQueries = executedQueries.filter((query) =>
        query.includes("spans_analytics"),
      );
      const annotationQueries = executedQueries.filter((query) =>
        query.includes("annotations_analytics"),
      );

      expect(spanQueries).toHaveLength(2);
      expect(annotationQueries).toHaveLength(2);

      expect(
        spanQueries.some(
          (query) =>
            query.includes(`toUUID('${organizationFreeOne}')`) &&
            query.includes(`toUUID('${organizationFreeTwo}')`),
        ),
      ).toBe(true);

      expect(
        spanQueries.some((query) =>
          query.includes(`toUUID('${organizationTeam}')`),
        ),
      ).toBe(true);

      expect(
        annotationQueries.some(
          (query) =>
            query.includes(`toUUID('${organizationFreeOne}')`) &&
            query.includes(`toUUID('${organizationFreeTwo}')`),
        ),
      ).toBe(true);

      expect(
        annotationQueries.some((query) =>
          query.includes(`toUUID('${organizationTeam}')`),
        ),
      ).toBe(true);

      expect(deleteSpy).toHaveBeenCalledTimes(2);
    });

    it("batches deletions when organizations exceed the batch size", async () => {
      const organizationIds = Array.from(
        { length: 101 },
        (_value, index) =>
          `00000000-0000-0000-0000-${String(index + 1).padStart(12, "0")}`,
      );

      const deleteSpy = vi.fn().mockImplementation(() => ({
        where: vi.fn().mockReturnValue({
          returning: vi.fn().mockReturnValue(Effect.succeed([])),
        }),
      }));

      const mockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi
            .fn()
            .mockReturnValue(
              Effect.succeed(organizationIds.map((id) => ({ id }))),
            ),
        }),
        delete: deleteSpy,
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () => Effect.succeed("free"),
            getPlanLimits: () =>
              Effect.succeed({
                seats: 1,
                projects: 1,
                spansPerMonth: 1_000_000,
                apiRequestsPerMinute: 100,
                dataRetentionDays: 30,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
      });

      const executedQueries: string[] = [];
      const commandSpy = vi.fn((query: string) => {
        executedQueries.push(query);
        return Effect.succeed(undefined);
      });

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        unsafeQuery: () => Effect.succeed([]),
        insert: () => Effect.succeed(undefined),
        command: commandSpy,
      } as never);

      await Effect.runPromise(
        enforceDataRetentionLimits.pipe(
          Effect.provide(mockDrizzleLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.provide(mockClickHouseLayer),
        ),
      );

      expect(commandSpy).toHaveBeenCalledTimes(4);
      expect(deleteSpy).toHaveBeenCalledTimes(2);
      expect(
        executedQueries.some((query) => query.includes("spans_analytics")),
      ).toBe(true);
      expect(
        executedQueries.some((query) =>
          query.includes("annotations_analytics"),
        ),
      ).toBe(true);
    });

    it("logs singular day retention when retention is one day", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      const deleteSpy = vi.fn().mockImplementation(() => ({
        where: vi.fn().mockReturnValue({
          returning: vi.fn().mockReturnValue(Effect.succeed([])),
        }),
      }));

      const mockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi
            .fn()
            .mockReturnValue(
              Effect.succeed([{ id: "88888888-8888-8888-8888-888888888888" }]),
            ),
        }),
        delete: deleteSpy,
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () => Effect.succeed("free"),
            getPlanLimits: () =>
              Effect.succeed({
                seats: 1,
                projects: 1,
                spansPerMonth: 1_000_000,
                apiRequestsPerMinute: 100,
                dataRetentionDays: 1,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
      });

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        unsafeQuery: () => Effect.succeed([]),
        insert: () => Effect.succeed(undefined),
        command: () => Effect.succeed(undefined),
      } as never);

      await Effect.runPromise(
        enforceDataRetentionLimits.pipe(
          Effect.provide(mockDrizzleLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.provide(mockClickHouseLayer),
        ),
      );

      expect(consoleLogSpy).toHaveBeenCalledWith(
        expect.stringContaining("1 day"),
      );

      consoleLogSpy.mockRestore();
    });

    it("skips organizations with invalid retention days", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const deleteSpy = vi.fn().mockImplementation(() => ({
        where: vi.fn().mockReturnValue({
          returning: vi.fn().mockReturnValue(Effect.succeed([])),
        }),
      }));

      const mockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi
            .fn()
            .mockReturnValue(
              Effect.succeed([{ id: "44444444-4444-4444-4444-444444444444" }]),
            ),
        }),
        delete: deleteSpy,
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () => Effect.succeed("team"),
            getPlanLimits: () =>
              Effect.succeed({
                seats: Infinity,
                projects: Infinity,
                spansPerMonth: Infinity,
                apiRequestsPerMinute: 10000,
                dataRetentionDays: Infinity,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
      });

      const commandSpy = vi.fn(() => Effect.succeed(undefined));
      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        unsafeQuery: () => Effect.succeed([]),
        insert: () => Effect.succeed(undefined),
        command: commandSpy,
      } as never);

      await Effect.runPromise(
        enforceDataRetentionLimits.pipe(
          Effect.provide(mockDrizzleLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.provide(mockClickHouseLayer),
        ),
      );

      expect(commandSpy).not.toHaveBeenCalled();
      expect(deleteSpy).not.toHaveBeenCalled();
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining("invalid retention days"),
      );

      consoleWarnSpy.mockRestore();
    });

    it("logs errors when plan lookup fails", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const deleteSpy = vi.fn().mockImplementation(() => ({
        where: vi.fn().mockReturnValue({
          returning: vi.fn().mockReturnValue(Effect.succeed([])),
        }),
      }));

      const mockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi
            .fn()
            .mockReturnValue(
              Effect.succeed([{ id: "55555555-5555-5555-5555-555555555555" }]),
            ),
        }),
        delete: deleteSpy,
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () => Effect.fail(new Error("Stripe unavailable")),
            getPlanLimits: () =>
              Effect.succeed({
                seats: 1,
                projects: 1,
                spansPerMonth: 1_000_000,
                apiRequestsPerMinute: 100,
                dataRetentionDays: 30,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
      });

      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const commandSpy = vi.fn(() => Effect.succeed(undefined));
      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        unsafeQuery: () => Effect.succeed([]),
        insert: () => Effect.succeed(undefined),
        command: commandSpy,
      } as never);

      await Effect.runPromise(
        enforceDataRetentionLimits.pipe(
          Effect.provide(mockDrizzleLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.provide(mockClickHouseLayer),
        ),
      );

      expect(commandSpy).not.toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("Failed to resolve plan for organization"),
        expect.anything(),
      );
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining("Skipping retention for organization"),
      );
      expect(deleteSpy).not.toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
      consoleWarnSpy.mockRestore();
    });

    it("logs errors when ClickHouse deletion fails", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const deleteSpy = vi.fn().mockImplementation(() => ({
        where: vi.fn().mockReturnValue({
          returning: vi.fn().mockReturnValue(Effect.succeed([])),
        }),
      }));

      const mockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi
            .fn()
            .mockReturnValue(
              Effect.succeed([{ id: "66666666-6666-6666-6666-666666666666" }]),
            ),
        }),
        delete: deleteSpy,
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () => Effect.succeed("free"),
            getPlanLimits: () =>
              Effect.succeed({
                seats: 1,
                projects: 1,
                spansPerMonth: 1_000_000,
                apiRequestsPerMinute: 100,
                dataRetentionDays: 30,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
      });

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        unsafeQuery: () => Effect.succeed([]),
        insert: () => Effect.succeed(undefined),
        command: () =>
          Effect.fail(
            new ClickHouseError({
              message: "ClickHouse down",
              cause: new Error("ClickHouse down"),
            }),
          ),
      } as never);

      await Effect.runPromise(
        enforceDataRetentionLimits.pipe(
          Effect.provide(mockDrizzleLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.provide(mockClickHouseLayer),
        ),
      );

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[dataRetentionCron] Failed to delete expired spans:",
        expect.anything(),
      );
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[dataRetentionCron] Failed to delete expired annotations:",
        expect.anything(),
      );
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        "[dataRetentionCron] Skipping PostgreSQL annotation deletion because ClickHouse deletion failed",
      );
      expect(deleteSpy).not.toHaveBeenCalled();

      consoleErrorSpy.mockRestore();
      consoleWarnSpy.mockRestore();
    });

    it("returns early when no organizations exist", async () => {
      const deleteSpy = vi.fn().mockImplementation(() => ({
        where: vi.fn().mockReturnValue({
          returning: vi.fn().mockReturnValue(Effect.succeed([])),
        }),
      }));

      const mockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue(Effect.succeed([])),
        }),
        delete: deleteSpy,
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () => Effect.succeed("free"),
            getPlanLimits: () =>
              Effect.succeed({
                seats: 1,
                projects: 1,
                spansPerMonth: 1_000_000,
                apiRequestsPerMinute: 100,
                dataRetentionDays: 30,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
      });

      const commandSpy = vi.fn(() => Effect.succeed(undefined));
      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        unsafeQuery: () => Effect.succeed([]),
        insert: () => Effect.succeed(undefined),
        command: commandSpy,
      } as never);

      await Effect.runPromise(
        enforceDataRetentionLimits.pipe(
          Effect.provide(mockDrizzleLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.provide(mockClickHouseLayer),
        ),
      );

      expect(commandSpy).not.toHaveBeenCalled();
      expect(deleteSpy).not.toHaveBeenCalled();
    });

    it("fails when organization query fails", async () => {
      const mockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue(Effect.fail(new Error("DB down"))),
        }),
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: vi.fn(),
            getPlanLimits: vi.fn(),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
      });

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        unsafeQuery: () => Effect.succeed([]),
        insert: () => Effect.succeed(undefined),
        command: () => Effect.succeed(undefined),
      } as never);

      const error = await Effect.runPromise(
        enforceDataRetentionLimits.pipe(
          Effect.provide(mockDrizzleLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.provide(mockClickHouseLayer),
          Effect.flip,
        ),
      );

      expect(error).toBeInstanceOf(DatabaseError);
      expect(error.message).toContain(
        "Failed to list organizations for retention",
      );
    });

    it("logs errors when PostgreSQL annotation deletion fails", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const deleteSpy = vi.fn().mockImplementation(() => ({
        where: vi.fn().mockReturnValue({
          returning: vi
            .fn()
            .mockReturnValue(Effect.fail(new Error("Delete failed"))),
        }),
      }));

      const mockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: vi.fn().mockReturnValue({
          from: vi
            .fn()
            .mockReturnValue(
              Effect.succeed([{ id: "77777777-7777-7777-7777-777777777777" }]),
            ),
        }),
        delete: deleteSpy,
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        customers: {
          subscriptions: {
            getPlan: () => Effect.succeed("free"),
            getPlanLimits: () =>
              Effect.succeed({
                seats: 1,
                projects: 1,
                spansPerMonth: 1_000_000,
                apiRequestsPerMinute: 100,
                dataRetentionDays: 30,
              }),
          },
        } as never,
        products: {} as never,
        paymentIntents: {} as never,
      });

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        unsafeQuery: () => Effect.succeed([]),
        insert: () => Effect.succeed(undefined),
        command: () => Effect.succeed(undefined),
      } as never);

      await Effect.runPromise(
        enforceDataRetentionLimits.pipe(
          Effect.provide(mockDrizzleLayer),
          Effect.provide(mockPaymentsLayer),
          Effect.provide(mockClickHouseLayer),
        ),
      );

      expect(deleteSpy).toHaveBeenCalledTimes(1);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[dataRetentionCron] Failed to delete expired PostgreSQL annotations:",
        expect.anything(),
      );

      consoleErrorSpy.mockRestore();
    });
  });

  it("logs error when no database connection is available", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    const environmentWithoutDatabase: CronTriggerEnv = {
      ...mockEnvironment,
      DATABASE_URL: undefined,
      HYPERDRIVE: undefined,
    } as CronTriggerEnv;

    await dataRetentionCron.scheduled(mockEvent, environmentWithoutDatabase);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[dataRetentionCron] No database connection available (HYPERDRIVE or DATABASE_URL required)",
    );

    consoleErrorSpy.mockRestore();
  });

  it("logs error when required environment variables are missing", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    const environmentWithMissingVariables: CronTriggerEnv = {
      DATABASE_URL: "postgres://test:test@localhost:5432/test",
      ENVIRONMENT: "test",
    } as CronTriggerEnv;

    await dataRetentionCron.scheduled(
      mockEvent,
      environmentWithMissingVariables,
    );

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[dataRetentionCron] Cron trigger error:",
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

    const environmentWithHyperdrive: CronTriggerEnv = {
      ...mockEnvironment,
      DATABASE_URL: undefined,
      HYPERDRIVE: {
        connectionString: "postgres://hyperdrive:test@localhost:5432/test",
      },
    } as CronTriggerEnv;

    await dataRetentionCron.scheduled(mockEvent, environmentWithHyperdrive);

    expect(consoleErrorSpy).not.toHaveBeenCalledWith(
      "[dataRetentionCron] No database connection available (HYPERDRIVE or DATABASE_URL required)",
    );

    consoleErrorSpy.mockRestore();
  });

  it("exports a scheduled handler", () => {
    expect(dataRetentionCron).toHaveProperty("scheduled");
    expect(typeof dataRetentionCron.scheduled).toBe("function");
  });

  it("processes retention workflow", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    await dataRetentionCron.scheduled(mockEvent, mockEnvironment);

    expect(consoleErrorSpy).toHaveBeenCalled();

    consoleErrorSpy.mockRestore();
  });
});
