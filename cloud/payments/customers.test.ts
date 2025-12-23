import { describe, it, expect, DefaultMockStripe } from "@/tests/db";
import { Effect, Layer, Context } from "effect";
import {
  createCustomer,
  deleteCustomer,
  getCustomerBalance,
} from "@/payments/customers";
import { StripeError } from "@/errors";
import { Stripe } from "@/payments/client";

describe("customers", () => {
  describe("createCustomer", () => {
    it.effect("creates customer and subscription with correct parameters", () =>
      Effect.gen(function* () {
        const result = yield* createCustomer({
          organizationId: "org_123",
          organizationName: "Test Org",
          organizationSlug: "test-org",
          email: "test@example.com",
        });

        expect(result.customerId).toBeDefined();
        expect(result.customerId).toMatch(/^cus_mock_/);
        expect(result.subscriptionId).toBeDefined();
        expect(result.subscriptionId).toMatch(/^sub_mock_/);
      }).pipe(Effect.provide(DefaultMockStripe)),
    );

    it.effect("returns StripeError when customer creation fails", () =>
      Effect.gen(function* () {
        const result = yield* createCustomer({
          organizationId: "org_123",
          organizationName: "Test Org",
          organizationSlug: "test-org",
          email: "test@example.com",
        }).pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Customer creation failed");
      }).pipe(
        Effect.provide(
          Layer.succeed(Stripe, {
            customers: {
              create: () =>
                Effect.fail(
                  new StripeError({ message: "Customer creation failed" }),
                ),
              del: () => Effect.void,
            },
            subscriptions: {
              create: () => Effect.void,
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );

    it.effect("returns StripeError when subscription creation fails", () =>
      Effect.gen(function* () {
        const result = yield* createCustomer({
          organizationId: "org_123",
          organizationName: "Test Org",
          organizationSlug: "test-org",
          email: "test@example.com",
        }).pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Subscription creation failed");
      }).pipe(
        Effect.provide(
          Layer.succeed(Stripe, {
            customers: {
              create: () =>
                Effect.succeed({
                  id: "cus_123",
                  object: "customer" as const,
                  created: Date.now(),
                  livemode: false,
                  email: "test@example.com",
                  name: "Test Org",
                  metadata: {},
                }),
              del: () => Effect.void,
            },
            subscriptions: {
              create: () =>
                Effect.fail(
                  new StripeError({ message: "Subscription creation failed" }),
                ),
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );
  });

  describe("deleteCustomer", () => {
    it.effect("deletes customer successfully", () =>
      Effect.gen(function* () {
        let deletedCustomerId: string | undefined;

        yield* deleteCustomer("cus_123").pipe(
          Effect.provide(
            Layer.succeed(Stripe, {
              customers: {
                create: () => Effect.void,
                del: (id: string) => {
                  deletedCustomerId = id;
                  return Effect.succeed({
                    id,
                    object: "customer" as const,
                    deleted: true,
                  });
                },
              },
              subscriptions: {
                create: () => Effect.void,
              },
              config: {
                apiKey: "sk_test_mock",
                routerPriceId: "price_test",
              },
            } as unknown as Context.Tag.Service<typeof Stripe>),
          ),
        );

        expect(deletedCustomerId).toBe("cus_123");
      }),
    );

    it.effect("returns StripeError when deletion fails", () =>
      Effect.gen(function* () {
        const result = yield* deleteCustomer("cus_123").pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Customer deletion failed");
      }).pipe(
        Effect.provide(
          Layer.succeed(Stripe, {
            customers: {
              create: () => Effect.void,
              del: () =>
                Effect.fail(
                  new StripeError({ message: "Customer deletion failed" }),
                ),
            },
            subscriptions: {
              create: () => Effect.void,
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );
  });

  describe("getCustomerBalance", () => {
    it.effect(
      "correctly filters and sums credits from various grant types",
      () =>
        Effect.gen(function* () {
          // MockStripe includes:
          // - Valid: $7 USD with router price ✓
          // - Valid: $11 USD with router price ✓
          // - Invalid: €5 EUR with router price (wrong currency) ✗
          // - Invalid: no monetary amount ✗
          // - Invalid: $19 USD with different price (wrong price) ✗
          // - Invalid: $23 USD with no scope (no explicit scope) ✗
          // Expected total: $7 + $11 = $18
          // No other combination of grants equals $18
          const balance = yield* getCustomerBalance("cus_123");

          expect(balance).toBe(18);
        }).pipe(Effect.provide(DefaultMockStripe)),
    );

    it.effect("returns 0 for customer with no credit grants", () =>
      Effect.gen(function* () {
        const balance = yield* getCustomerBalance("cus_123");

        expect(balance).toBe(0);
      }).pipe(
        Effect.provide(
          Layer.succeed(Stripe, {
            customers: {
              create: () => Effect.void,
              del: () => Effect.void,
            },
            subscriptions: {
              create: () => Effect.void,
            },
            billing: {
              creditGrants: {
                list: () =>
                  Effect.succeed({
                    object: "list" as const,
                    data: [],
                    has_more: false,
                  }),
              },
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock_for_testing",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );

    it.effect("returns StripeError when API call fails", () =>
      Effect.gen(function* () {
        const result = yield* getCustomerBalance("cus_123").pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Failed to fetch credit grants");
      }).pipe(
        Effect.provide(
          Layer.succeed(Stripe, {
            customers: {
              create: () => Effect.void,
              del: () => Effect.void,
            },
            subscriptions: {
              create: () => Effect.void,
            },
            billing: {
              creditGrants: {
                list: () =>
                  Effect.fail(
                    new StripeError({
                      message: "Failed to fetch credit grants",
                    }),
                  ),
              },
            },
            config: {
              apiKey: "sk_test_mock",
              routerPriceId: "price_test_mock_for_testing",
            },
          } as unknown as Context.Tag.Service<typeof Stripe>),
        ),
      ),
    );
  });
});
