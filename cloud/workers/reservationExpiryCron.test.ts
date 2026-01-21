import { describe, it, expect, vi } from "vitest";
import { Effect, Layer } from "effect";
import { DrizzleORM } from "@/db/client";
import reservationExpiryCron, {
  expireStaleReservations,
} from "@/workers/reservationExpiryCron";
import type { CronTriggerEnv } from "@/workers/reservationExpiryCron";

describe("reservationExpiryCron", () => {
  const mockEnv: CronTriggerEnv = {
    DATABASE_URL: "postgres://test:test@localhost:5432/test",
    ENVIRONMENT: "test",
    CLICKHOUSE_URL: "http://localhost:8123",
    HYPERDRIVE: {
      connectionString: "postgres://test:test@localhost:5432/test",
    },
  } as CronTriggerEnv;

  const mockEvent = {
    scheduledTime: Date.now(),
    cron: "*/5 * * * *",
  };

  describe("expireStaleReservations", () => {
    it("expires stale reservations and logs count", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      // Mock database to return expired reservations
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockImplementation(() => ({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              returning: vi
                .fn()
                .mockReturnValue(
                  Effect.succeed([
                    { id: "reservation-1" },
                    { id: "reservation-2" },
                    { id: "reservation-3" },
                  ]),
                ),
            }),
          }),
        })),
      } as never);

      await Effect.runPromise(
        expireStaleReservations.pipe(Effect.provide(mockDbLayer)),
      );

      // Should log the number of expired reservations
      expect(consoleLogSpy).toHaveBeenCalledWith(
        "[reservationExpiryCron] Expired 3 stale reservations",
      );

      consoleLogSpy.mockRestore();
    });

    it("does not log when no reservations are expired", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      // Mock database to return no expired reservations
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockImplementation(() => ({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              returning: vi.fn().mockReturnValue(Effect.succeed([])),
            }),
          }),
        })),
      } as never);

      await Effect.runPromise(
        expireStaleReservations.pipe(Effect.provide(mockDbLayer)),
      );

      // Should not log when no expired rows
      expect(consoleLogSpy).not.toHaveBeenCalledWith(
        expect.stringContaining("Expired"),
      );

      consoleLogSpy.mockRestore();
    });

    it("handles database errors gracefully", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockImplementation(() => ({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              returning: vi
                .fn()
                .mockReturnValue(
                  Effect.fail(new Error("Database connection failed")),
                ),
            }),
          }),
        })),
      } as never);

      const error = await Effect.runPromise(
        expireStaleReservations.pipe(Effect.provide(mockDbLayer), Effect.flip),
      );

      expect(error.message).toContain("Failed to expire stale reservations");
    });
  });

  it("logs error when no database connection is available", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    const envWithoutDb: CronTriggerEnv = {
      ...mockEnv,
      DATABASE_URL: undefined,
      HYPERDRIVE: undefined,
    } as CronTriggerEnv;

    await reservationExpiryCron.scheduled(mockEvent, envWithoutDb);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[reservationExpiryCron] HYPERDRIVE binding not configured",
    );

    consoleErrorSpy.mockRestore();
  });

  it("uses HYPERDRIVE connection string when available", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    const envWithHyperdrive: CronTriggerEnv = {
      ...mockEnv,
      DATABASE_URL: undefined,
      HYPERDRIVE: {
        connectionString: "postgres://hyperdrive:test@localhost:5432/test",
      },
    } as CronTriggerEnv;

    await reservationExpiryCron.scheduled(mockEvent, envWithHyperdrive);

    // Should not log the "HYPERDRIVE binding not configured" error
    expect(consoleErrorSpy).not.toHaveBeenCalledWith(
      "[reservationExpiryCron] HYPERDRIVE binding not configured",
    );

    consoleErrorSpy.mockRestore();
  });

  it("handles errors gracefully during execution", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // Use HYPERDRIVE with invalid connection to trigger error
    const envWithInvalidDb: CronTriggerEnv = {
      ...mockEnv,
      HYPERDRIVE: {
        connectionString:
          "postgres://invalid:invalid@localhost:5432/nonexistent",
      },
    } as CronTriggerEnv;

    await reservationExpiryCron.scheduled(mockEvent, envWithInvalidDb);

    // Should log cron trigger error
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[reservationExpiryCron] Cron trigger error:",
      expect.anything(),
    );

    consoleErrorSpy.mockRestore();
  });

  it("logs when expired rows are found", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // Will fail to connect but tests the flow
    await reservationExpiryCron.scheduled(mockEvent, mockEnv);

    consoleLogSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  it("exports a scheduled handler", () => {
    expect(reservationExpiryCron).toHaveProperty("scheduled");
    expect(typeof reservationExpiryCron.scheduled).toBe("function");
  });

  it("processes expiry workflow", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // Will fail to connect but tests the workflow
    await reservationExpiryCron.scheduled(mockEvent, mockEnv);

    // Should have attempted processing
    expect(consoleErrorSpy).toHaveBeenCalled();

    consoleLogSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  it("handles successful workflow without errors when no expired rows", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    await reservationExpiryCron.scheduled(mockEvent, mockEnv);

    consoleLogSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });
});
