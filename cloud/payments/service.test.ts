import { describe, it, expect } from "vitest";
import { Effect, Layer } from "effect";
import { Payments } from "@/payments/service";
import { MockStripe } from "@/tests/payments";
import { MockDrizzleORMLayer } from "@/tests/mock-drizzle";

describe("Payments", () => {
  describe("Default layer", () => {
    it("creates a Payments service with customers", async () => {
      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const payments = yield* Payments;

          // Verify customers service exists
          expect(payments.customers).toBeDefined();
          expect(typeof payments.customers.create).toBe("function");
          expect(typeof payments.customers.update).toBe("function");
          expect(typeof payments.customers.delete).toBe("function");
          expect(typeof payments.customers.subscriptions.cancel).toBe(
            "function",
          );

          return true;
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(Layer.merge(MockStripe, MockDrizzleORMLayer)),
            ),
          ),
        ),
      );

      expect(result).toBe(true);
    });

    it("creates a Payments service with products.router", async () => {
      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const payments = yield* Payments;

          // Verify products.router service exists
          expect(payments.products).toBeDefined();
          expect(payments.products.router).toBeDefined();
          expect(typeof payments.products.router.getUsageMeterBalance).toBe(
            "function",
          );
          expect(typeof payments.products.router.getBalanceInfo).toBe(
            "function",
          );
          expect(typeof payments.products.router.getCreditBalance).toBe(
            "function",
          );
          expect(typeof payments.products.router.chargeUsageMeter).toBe(
            "function",
          );
          expect(typeof payments.products.router.chargeForUsage).toBe(
            "function",
          );
          expect(typeof payments.products.router.reserveFunds).toBe("function");
          expect(typeof payments.products.router.settleFunds).toBe("function");
          expect(typeof payments.products.router.releaseFunds).toBe("function");

          return true;
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(Layer.merge(MockStripe, MockDrizzleORMLayer)),
            ),
          ),
        ),
      );

      expect(result).toBe(true);
    });

    it("supports spreading customers service properties", async () => {
      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const payments = yield* Payments;

          // Spread operator should work (triggers ownKeys and getOwnPropertyDescriptor)
          const {
            create,
            update,
            delete: del,
            subscriptions,
          } = payments.customers;

          expect(typeof create).toBe("function");
          expect(typeof update).toBe("function");
          expect(typeof del).toBe("function");
          expect(typeof subscriptions.cancel).toBe("function");

          return true;
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(Layer.merge(MockStripe, MockDrizzleORMLayer)),
            ),
          ),
        ),
      );

      expect(result).toBe(true);
    });

    it("supports Object.keys on customers service", async () => {
      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const payments = yield* Payments;

          // Object.keys should work (triggers ownKeys)
          const keys = Object.keys(payments.customers);

          // Should include method names from prototype
          expect(keys).toContain("create");
          expect(keys).toContain("update");
          expect(keys).toContain("delete");
          expect(keys).toContain("subscriptions");

          return true;
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(Layer.merge(MockStripe, MockDrizzleORMLayer)),
            ),
          ),
        ),
      );

      expect(result).toBe(true);
    });

    it("supports Object.getOwnPropertyDescriptor on customers service", async () => {
      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const payments = yield* Payments;

          // Object.getOwnPropertyDescriptor should work (triggers getOwnPropertyDescriptor)
          const descriptor = Object.getOwnPropertyDescriptor(
            payments.customers,
            "create",
          );

          expect(descriptor).toBeDefined();
          expect(descriptor?.configurable).toBe(true);
          expect(descriptor?.enumerable).toBe(true);
          expect(descriptor?.writable).toBe(true);
          expect(typeof descriptor?.value).toBe("function");

          return true;
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(Layer.merge(MockStripe, MockDrizzleORMLayer)),
            ),
          ),
        ),
      );

      expect(result).toBe(true);
    });
  });

  describe("Live layer", () => {
    it("creates a Payments layer from config", () => {
      const layer = Payments.Live({
        secretKey: "sk_test_key",
        webhookSecret: "whsec_test",
        routerPriceId: "price_test",
        routerMeterId: "meter_test",
        cloudFreePriceId: "price_cloud_free",
        cloudProPriceId: "price_cloud_pro",
        cloudTeamPriceId: "price_cloud_team",
        cloudSpansPriceId: "price_cloud_spans",
        cloudSpansMeterId: "meter_cloud_spans",
      });

      // Verify it returns a Layer
      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });
  });

  describe("makeReady nested object handling", () => {
    it("handles nested objects correctly", async () => {
      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const payments = yield* Payments;

          // Access customers property twice to test caching
          const customers1 = payments.customers;
          const customers2 = payments.customers;

          // Should return the same wrapped object (identity preserved)
          expect(customers1).toBe(customers2);

          return true;
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(Layer.merge(MockStripe, MockDrizzleORMLayer)),
            ),
          ),
        ),
      );

      expect(result).toBe(true);
    });

    it("wraps nested object properties recursively", async () => {
      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const payments = yield* Payments;

          // Access nested config property (triggers nested object wrapping)
          const config1 = payments.customers.config;
          const config2 = payments.customers.config;

          // Should return the same wrapped object (caching works)
          expect(config1).toBe(config2);
          expect(config1.version).toBe("1.0.0");

          return true;
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(Layer.merge(MockStripe, MockDrizzleORMLayer)),
            ),
          ),
        ),
      );

      expect(result).toBe(true);
    });

    it("handles getOwnPropertyDescriptor for non-method properties", async () => {
      const result = await Effect.runPromise(
        Effect.gen(function* () {
          const payments = yield* Payments;

          // Access a non-existent property to trigger the false branch of line 142
          const descriptor = Object.getOwnPropertyDescriptor(
            payments.customers,
            "nonExistentProperty",
          );

          // Should fall through to Object.getOwnPropertyDescriptor (line 151)
          expect(descriptor).toBeUndefined();

          return true;
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(Layer.merge(MockStripe, MockDrizzleORMLayer)),
            ),
          ),
        ),
      );

      expect(result).toBe(true);
    });
  });
});
