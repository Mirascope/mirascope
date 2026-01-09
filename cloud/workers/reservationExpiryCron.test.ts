import { describe, it, expect, vi } from "vitest";
import reservationExpiryCron from "./reservationExpiryCron";
import type { CronTriggerEnv } from "./reservationExpiryCron";

describe("reservationExpiryCron", () => {
  const mockEnv: CronTriggerEnv = {
    DATABASE_URL: "postgres://test:test@localhost:5432/test",
    ENVIRONMENT: "test",
    CLICKHOUSE_URL: "http://localhost:8123",
  };

  const mockEvent = {
    scheduledTime: Date.now(),
    cron: "*/5 * * * *",
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

    await reservationExpiryCron.scheduled(mockEvent, envWithoutDb);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[reservationExpiryCron] No database connection available (HYPERDRIVE or DATABASE_URL required)",
    );

    consoleErrorSpy.mockRestore();
  });

  it("exports a scheduled handler", () => {
    expect(reservationExpiryCron).toHaveProperty("scheduled");
    expect(typeof reservationExpiryCron.scheduled).toBe("function");
  });
});
