import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { getRouterConfig, validateRouterConfig } from "./config";

describe("RouterConfig", () => {
  // Store original env vars
  const originalEnv = { ...process.env };

  beforeEach(() => {
    // Reset to clean state
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    // Restore original env
    process.env = originalEnv;
  });

  describe("getRouterConfig", () => {
    it("should return config when all env vars are set", () => {
      process.env.DATABASE_URL = "postgresql://test";
      process.env.STRIPE_SECRET_KEY = "sk_test_mock";
      process.env.STRIPE_ROUTER_PRICE_ID = "price_123";
      process.env.STRIPE_ROUTER_METER_ID = "meter_123";

      const config = getRouterConfig();

      expect(config).toEqual({
        databaseUrl: "postgresql://test",
        stripe: {
          apiKey: "sk_test_mock",
          routerPriceId: "price_123",
          routerMeterId: "meter_123",
        },
      });
    });

    it("should throw when DATABASE_URL is missing", () => {
      delete process.env.DATABASE_URL;
      process.env.STRIPE_SECRET_KEY = "sk_test_mock";
      process.env.STRIPE_ROUTER_PRICE_ID = "price_123";
      process.env.STRIPE_ROUTER_METER_ID = "meter_123";

      expect(() => getRouterConfig()).toThrow(
        "DATABASE_URL environment variable is required",
      );
    });

    it("should throw when STRIPE_SECRET_KEY is missing", () => {
      process.env.DATABASE_URL = "postgresql://test";
      delete process.env.STRIPE_SECRET_KEY;
      process.env.STRIPE_ROUTER_PRICE_ID = "price_123";
      process.env.STRIPE_ROUTER_METER_ID = "meter_123";

      expect(() => getRouterConfig()).toThrow(
        "Stripe environment variables (STRIPE_SECRET_KEY, STRIPE_ROUTER_PRICE_ID, STRIPE_ROUTER_METER_ID) are required",
      );
    });

    it("should throw when STRIPE_ROUTER_PRICE_ID is missing", () => {
      process.env.DATABASE_URL = "postgresql://test";
      process.env.STRIPE_SECRET_KEY = "sk_test_mock";
      delete process.env.STRIPE_ROUTER_PRICE_ID;
      process.env.STRIPE_ROUTER_METER_ID = "meter_123";

      expect(() => getRouterConfig()).toThrow(
        "Stripe environment variables (STRIPE_SECRET_KEY, STRIPE_ROUTER_PRICE_ID, STRIPE_ROUTER_METER_ID) are required",
      );
    });

    it("should throw when STRIPE_ROUTER_METER_ID is missing", () => {
      process.env.DATABASE_URL = "postgresql://test";
      process.env.STRIPE_SECRET_KEY = "sk_test_mock";
      process.env.STRIPE_ROUTER_PRICE_ID = "price_123";
      delete process.env.STRIPE_ROUTER_METER_ID;

      expect(() => getRouterConfig()).toThrow(
        "Stripe environment variables (STRIPE_SECRET_KEY, STRIPE_ROUTER_PRICE_ID, STRIPE_ROUTER_METER_ID) are required",
      );
    });
  });

  describe("validateRouterConfig", () => {
    it("should return null when all env vars are set", () => {
      process.env.DATABASE_URL = "postgresql://test";
      process.env.STRIPE_SECRET_KEY = "sk_test_mock";
      process.env.STRIPE_ROUTER_PRICE_ID = "price_123";
      process.env.STRIPE_ROUTER_METER_ID = "meter_123";

      expect(validateRouterConfig()).toBeNull();
    });

    it("should return error message when DATABASE_URL is missing", () => {
      delete process.env.DATABASE_URL;
      process.env.STRIPE_SECRET_KEY = "sk_test_mock";
      process.env.STRIPE_ROUTER_PRICE_ID = "price_123";
      process.env.STRIPE_ROUTER_METER_ID = "meter_123";

      expect(validateRouterConfig()).toBe("Database not configured");
    });

    it("should return error message when Stripe config is incomplete", () => {
      process.env.DATABASE_URL = "postgresql://test";
      delete process.env.STRIPE_SECRET_KEY;
      process.env.STRIPE_ROUTER_PRICE_ID = "price_123";
      process.env.STRIPE_ROUTER_METER_ID = "meter_123";

      expect(validateRouterConfig()).toBe("Stripe configuration incomplete");
    });
  });
});
