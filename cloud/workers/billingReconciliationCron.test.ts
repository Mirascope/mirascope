import { describe, it, expect, vi } from "vitest";
import billingReconciliationCron from "./billingReconciliationCron";
import type { CronTriggerEnv } from "./billingReconciliationCron";

describe("billingReconciliationCron", () => {
  const mockEnv: CronTriggerEnv = {
    DATABASE_URL: "postgres://test:test@localhost:5432/test",
    ENVIRONMENT: "test",
    CLICKHOUSE_URL: "http://localhost:8123",
    STRIPE_SECRET_KEY: "sk_test_mock",
    STRIPE_ROUTER_PRICE_ID: "price_test_mock",
    STRIPE_ROUTER_METER_ID: "meter_test_mock",
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

    await billingReconciliationCron.scheduled(mockEvent, envWithoutDb);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[billingReconciliationCron] No database connection available (HYPERDRIVE or DATABASE_URL required)",
    );

    consoleErrorSpy.mockRestore();
  });

  it("logs error when Stripe configuration is missing", async () => {
    const consoleErrorSpy = vi
      .spyOn(console, "error")
      .mockImplementation(() => {});

    const envWithoutStripe: CronTriggerEnv = {
      ...mockEnv,
      STRIPE_SECRET_KEY: undefined,
      STRIPE_ROUTER_PRICE_ID: undefined,
      STRIPE_ROUTER_METER_ID: undefined,
    };

    await billingReconciliationCron.scheduled(mockEvent, envWithoutStripe);

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      "[billingReconciliationCron] Missing Stripe configuration (STRIPE_SECRET_KEY, STRIPE_ROUTER_PRICE_ID, STRIPE_ROUTER_METER_ID required)",
    );

    consoleErrorSpy.mockRestore();
  });

  it("exports a scheduled handler", () => {
    expect(billingReconciliationCron).toHaveProperty("scheduled");
    expect(typeof billingReconciliationCron.scheduled).toBe("function");
  });
});
