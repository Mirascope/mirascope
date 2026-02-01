/**
 * @fileoverview Tests for config types.
 */

import { describe, it, expect } from "vitest";

import type {
  ScheduledEvent,
  CronTriggerEnv,
  BillingCronTriggerEnv,
  WorkerEnv,
} from "@/workers/config";

describe("config", () => {
  describe("ScheduledEvent", () => {
    it("has required fields", () => {
      const event: ScheduledEvent = {
        scheduledTime: Date.now(),
        cron: "*/5 * * * *",
      };

      expect(event.scheduledTime).toBeTypeOf("number");
      expect(event.cron).toBeTypeOf("string");
    });
  });

  describe("CronTriggerEnv", () => {
    it("extends CloudflareEnvironment", () => {
      const env: CronTriggerEnv = {
        ENVIRONMENT: "test",
        CLICKHOUSE_URL: "http://localhost:8123",
        DATABASE_URL: "postgres://test:test@localhost:5432/test",
      };

      expect(env.ENVIRONMENT).toBe("test");
      expect(env.DATABASE_URL).toBe("postgres://test:test@localhost:5432/test");
    });

    it("supports HYPERDRIVE binding", () => {
      const env: CronTriggerEnv = {
        ENVIRONMENT: "test",
        CLICKHOUSE_URL: "http://localhost:8123",
        HYPERDRIVE: {
          connectionString: "postgres://hyperdrive:test@localhost:5432/test",
        },
      };

      expect(env.HYPERDRIVE?.connectionString).toBe(
        "postgres://hyperdrive:test@localhost:5432/test",
      );
    });
  });

  describe("BillingCronTriggerEnv", () => {
    it("extends CronTriggerEnv with Stripe config", () => {
      const env: BillingCronTriggerEnv = {
        ENVIRONMENT: "test",
        CLICKHOUSE_URL: "http://localhost:8123",
        DATABASE_URL: "postgres://test:test@localhost:5432/test",
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_test",
        STRIPE_ROUTER_METER_ID: "meter_test",
        STRIPE_CLOUD_FREE_PRICE_ID: "price_free",
        STRIPE_CLOUD_PRO_PRICE_ID: "price_pro",
        STRIPE_CLOUD_TEAM_PRICE_ID: "price_team",
        STRIPE_CLOUD_SPANS_PRICE_ID: "price_spans",
        STRIPE_CLOUD_SPANS_METER_ID: "meter_spans",
      };

      expect(env.STRIPE_SECRET_KEY).toBe("sk_test_xxx");
      expect(env.STRIPE_ROUTER_PRICE_ID).toBe("price_test");
      expect(env.STRIPE_ROUTER_METER_ID).toBe("meter_test");
      expect(env.STRIPE_CLOUD_FREE_PRICE_ID).toBe("price_free");
      expect(env.STRIPE_CLOUD_PRO_PRICE_ID).toBe("price_pro");
      expect(env.STRIPE_CLOUD_TEAM_PRICE_ID).toBe("price_team");
      expect(env.STRIPE_CLOUD_SPANS_PRICE_ID).toBe("price_spans");
      expect(env.STRIPE_CLOUD_SPANS_METER_ID).toBe("meter_spans");
    });
  });

  describe("WorkerEnv", () => {
    it("extends BillingCronTriggerEnv with required bindings", () => {
      const mockRouterQueue = {
        send: async () => {},
      };

      const mockSpansIngestQueue = {
        send: async () => {},
      };

      const mockDurableObject = {
        get: () => ({}),
        idFromName: () => ({}),
        newUniqueId: () => ({}),
        idFromString: () => ({}),
        getByName: () => ({}),
        jurisdiction: () => ({}),
      };

      const environment = {
        ENVIRONMENT: "test",
        CLICKHOUSE_URL: "http://localhost:8123",
        DATABASE_URL: "postgres://test:test@localhost:5432/test",
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_test",
        STRIPE_ROUTER_METER_ID: "meter_test",
        STRIPE_CLOUD_FREE_PRICE_ID: "price_free",
        STRIPE_CLOUD_PRO_PRICE_ID: "price_pro",
        STRIPE_CLOUD_TEAM_PRICE_ID: "price_team",
        STRIPE_CLOUD_SPANS_PRICE_ID: "price_spans",
        STRIPE_CLOUD_SPANS_METER_ID: "meter_spans",
        ROUTER_METERING_QUEUE: mockRouterQueue,
        SPANS_INGEST_QUEUE: mockSpansIngestQueue,
        REALTIME_SPANS_DURABLE_OBJECT: mockDurableObject,
      } as unknown as WorkerEnv;

      expect(environment.ROUTER_METERING_QUEUE).toBe(mockRouterQueue);
      expect(environment.SPANS_INGEST_QUEUE).toBe(mockSpansIngestQueue);
      expect(environment.REALTIME_SPANS_DURABLE_OBJECT).toBe(mockDurableObject);
    });
  });
});
