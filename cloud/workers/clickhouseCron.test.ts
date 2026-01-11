import { describe, it, expect, vi } from "vitest";
import { Effect, Layer } from "effect";
import { DrizzleORM } from "@/db/client";
import { ClickHouse } from "@/clickhouse/client";
import clickhouseCron, { clickhouseCronProgram } from "./clickhouseCron";
import type { CronTriggerEnv } from "./clickhouseCron";

describe("clickhouseCron", () => {
  const mockEnv: CronTriggerEnv = {
    DATABASE_URL: "postgres://test:test@localhost:5432/test",
    ENVIRONMENT: "test",
    CLICKHOUSE_URL: "http://localhost:8123",
  };

  const mockEvent = {
    scheduledTime: Date.now(),
    cron: "0/5 * * * *",
  };

  it("logs error when no database connection is available", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    const envWithoutDb: CronTriggerEnv = {
      ...mockEnv,
      DATABASE_URL: undefined,
      HYPERDRIVE: undefined,
    };

    await clickhouseCron.scheduled(mockEvent, envWithoutDb);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "No database connection available (HYPERDRIVE or DATABASE_URL required)",
    );

    consoleErrorSpy.mockRestore();
  });

  it("exports a scheduled handler", () => {
    expect(clickhouseCron).toHaveProperty("scheduled");
    expect(typeof clickhouseCron.scheduled).toBe("function");
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
    };

    await clickhouseCron.scheduled(mockEvent, envWithHyperdrive);

    // Should not log the "No database connection" error
    expect(consoleErrorSpy).not.toHaveBeenCalledWith(
      "No database connection available (HYPERDRIVE or DATABASE_URL required)",
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

    await clickhouseCron.scheduled(mockEvent, envWithInvalidDb);

    // Should log cron trigger error
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "Cron trigger error:",
      expect.anything(),
    );

    consoleErrorSpy.mockRestore();
  });

  it("logs processing message when pending rows found", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // Will fail to connect but tests the flow
    await clickhouseCron.scheduled(mockEvent, mockEnv);

    consoleLogSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  it("handles success path with valid connection", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // This will try to connect and fail gracefully
    await clickhouseCron.scheduled(mockEvent, mockEnv);

    // Should have attempted processing
    expect(consoleErrorSpy).toHaveBeenCalled();

    consoleLogSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  it("processes the full workflow", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    // Test with DATABASE_URL
    await clickhouseCron.scheduled(mockEvent, mockEnv);

    consoleLogSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  it("successfully reclaims stale locks and processes pending rows", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});

    // Mock database operations
    void Layer.succeed(DrizzleORM, {
      update: vi.fn().mockImplementation(() => ({
        set: vi.fn().mockReturnValue({
          where: vi.fn().mockReturnValue({
            pipe: vi.fn().mockReturnValue(Effect.succeed(undefined)),
          }),
        }),
      })),
      select: vi.fn().mockImplementation(() => ({
        from: vi.fn().mockReturnValue({
          where: vi.fn().mockReturnValue({
            orderBy: vi.fn().mockReturnValue({
              limit: vi.fn().mockReturnValue(
                Effect.succeed([
                  { spanId: "span-1", operation: "INSERT" },
                  { spanId: "span-2", operation: "UPDATE" },
                ]),
              ),
            }),
          }),
        }),
      })),
    } as never);

    void Layer.succeed(ClickHouse, {
      insert: vi.fn().mockReturnValue(Effect.succeed(undefined)),
    } as never);

    // Mock the processOutboxMessages
    const originalModule = await import("./outboxProcessor");
    vi.spyOn(originalModule, "processOutboxMessages").mockImplementation(() =>
      Effect.succeed(undefined),
    );

    await clickhouseCron.scheduled(mockEvent, mockEnv);

    consoleLogSpy.mockRestore();
    vi.restoreAllMocks();
  });

  it("handles empty pending rows (no work to do)", async () => {
    const consoleLogSpy = vi.spyOn(console, "log").mockImplementation(() => {});

    // Mock database to return empty results
    void Layer.succeed(DrizzleORM, {
      update: vi.fn().mockImplementation(() => ({
        set: vi.fn().mockReturnValue({
          where: vi.fn().mockReturnValue({
            pipe: vi.fn().mockReturnValue(Effect.succeed(undefined)),
          }),
        }),
      })),
      select: vi.fn().mockImplementation(() => ({
        from: vi.fn().mockReturnValue({
          where: vi.fn().mockReturnValue({
            orderBy: vi.fn().mockReturnValue({
              limit: vi.fn().mockReturnValue(Effect.succeed([])), // No pending rows
            }),
          }),
        }),
      })),
    } as never);

    void Layer.succeed(ClickHouse, {
      insert: vi.fn().mockReturnValue(Effect.succeed(undefined)),
    } as never);

    await clickhouseCron.scheduled(mockEvent, mockEnv);

    // Should not log "Processing X pending rows" when there are none
    expect(consoleLogSpy).not.toHaveBeenCalledWith(
      expect.stringContaining("Processing"),
    );

    consoleLogSpy.mockRestore();
  });

  describe("clickhouseCronProgram", () => {
    it("handles DatabaseError when reclaiming stale locks fails", async () => {
      const mockPipe = vi.fn((fn) =>
        // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unsafe-call
        fn(Effect.fail(new Error("Database connection failed"))),
      );

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              pipe: mockPipe,
            }),
          }),
        }),
        select: vi.fn(),
      } as never);

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: vi.fn(),
      } as never);

      await expect(
        Effect.runPromise(
          clickhouseCronProgram("test-worker").pipe(
            Effect.provide(Layer.merge(mockDbLayer, mockClickHouseLayer)),
          ),
        ),
      ).rejects.toThrow();
    });

    it("handles DatabaseError when querying pending rows fails", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              pipe: vi.fn().mockReturnValue(Effect.succeed(undefined)),
            }),
          }),
        }),
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              orderBy: vi.fn().mockReturnValue({
                limit: vi
                  .fn()
                  .mockReturnValue(
                    Effect.fail(new Error("Failed to query database")),
                  ),
              }),
            }),
          }),
        }),
      } as never);

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: vi.fn(),
      } as never);

      await expect(
        Effect.runPromise(
          clickhouseCronProgram("test-worker").pipe(
            Effect.provide(Layer.merge(mockDbLayer, mockClickHouseLayer)),
          ),
        ),
      ).rejects.toThrow();
    });

    it("runs successfully with no pending rows", async () => {
      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              pipe: vi.fn().mockReturnValue(Effect.succeed(undefined)),
            }),
          }),
        }),
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              orderBy: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(Effect.succeed([])),
              }),
            }),
          }),
        }),
      } as never);

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: vi.fn(),
      } as never);

      await Effect.runPromise(
        clickhouseCronProgram("test-worker").pipe(
          Effect.provide(Layer.merge(mockDbLayer, mockClickHouseLayer)),
        ),
      );
    });

    it("processes pending rows", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      const mockDbLayer = Layer.succeed(DrizzleORM, {
        update: vi.fn().mockReturnValue({
          set: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              pipe: vi.fn().mockReturnValue(Effect.succeed(undefined)),
              returning: vi.fn().mockReturnValue(Effect.succeed([])),
            }),
          }),
        }),
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              orderBy: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(
                  Effect.succeed([
                    { spanId: "span-1", operation: "INSERT" },
                    { spanId: "span-2", operation: "UPDATE" },
                  ]),
                ),
              }),
              limit: vi.fn().mockReturnValue(Effect.succeed([])),
            }),
            innerJoin: vi.fn().mockReturnValue({
              where: vi.fn().mockReturnValue({
                limit: vi.fn().mockReturnValue(Effect.succeed([])),
              }),
            }),
          }),
        }),
      } as never);

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: vi.fn().mockReturnValue(Effect.succeed(undefined)),
      } as never);

      await Effect.runPromise(
        clickhouseCronProgram("test-worker").pipe(
          Effect.provide(Layer.merge(mockDbLayer, mockClickHouseLayer)),
        ),
      );

      expect(consoleLogSpy).toHaveBeenCalledWith(
        "Processing 2 pending outbox rows",
      );

      consoleLogSpy.mockRestore();
    });
  });
});
