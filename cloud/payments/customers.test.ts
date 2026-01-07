import { describe, it, expect } from "@/tests/db";
import { Effect, Layer, Context } from "effect";
import { StripeError } from "@/errors";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import { DefaultMockPayments } from "@/tests/payments";

describe("customers", () => {
  describe("create", () => {
    it.effect("creates customer and subscription with correct parameters", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.create({
          organizationId: "org_123",
          organizationName: "Test Org",
          organizationSlug: "test-org",
          email: "test@example.com",
        });

        expect(result.customerId).toBeDefined();
        expect(result.customerId).toMatch(/^cus_mock_/);
        expect(result.subscriptionId).toBeDefined();
        expect(result.subscriptionId).toMatch(/^sub_mock_/);
      }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("returns StripeError when customer creation fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers
          .create({
            organizationId: "org_123",
            organizationName: "Test Org",
            organizationSlug: "test-org",
            email: "test@example.com",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Customer creation failed");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
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
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("returns StripeError when subscription creation fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers
          .create({
            organizationId: "org_123",
            organizationName: "Test Org",
            organizationSlug: "test-org",
            email: "test@example.com",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Subscription creation failed");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
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
                      new StripeError({
                        message: "Subscription creation failed",
                      }),
                    ),
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );
  });

  describe("delete", () => {
    it.effect("deletes customer successfully", () => {
      let deletedCustomerId: string | undefined;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.delete("cus_123");

        expect(deletedCustomerId).toBe("cus_123");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
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
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      );
    });

    it.effect("returns StripeError when deletion fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers
          .delete("cus_123")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Customer deletion failed");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
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
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );
  });

  describe("update", () => {
    it.effect("updates customer name and metadata", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.update({
          customerId: "cus_123",
          organizationName: "New Name",
          organizationSlug: "new-slug",
        });

        // Test passes if no errors thrown
      }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("updates only organization slug", () => {
      let updatedCustomer:
        | { name?: string; metadata?: Record<string, string> }
        | undefined;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.update({
          customerId: "cus_123",
          organizationSlug: "updated-slug-only",
        });

        // Should update metadata with new slug, preserving existing metadata
        expect(updatedCustomer?.metadata?.organizationSlug).toBe(
          "updated-slug-only",
        );
        expect(updatedCustomer?.metadata?.organizationId).toBe("org-123");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  create: () => Effect.void,
                  retrieve: (id: string) =>
                    Effect.succeed({
                      id,
                      object: "customer" as const,
                      created: Date.now(),
                      livemode: false,
                      email: "test@example.com",
                      name: "Existing Name",
                      metadata: {
                        organizationId: "org-123",
                        organizationName: "Existing Name",
                        organizationSlug: "old-slug",
                      },
                    }),
                  update: (
                    id: string,
                    params: {
                      name?: string;
                      metadata?: Record<string, string>;
                    },
                  ) => {
                    updatedCustomer = params;
                    return Effect.succeed({
                      id,
                      object: "customer" as const,
                      created: Date.now(),
                      livemode: false,
                      email: "test@example.com",
                      name: params.name || "Existing Name",
                      metadata: params.metadata || {},
                    });
                  },
                  del: () => Effect.void,
                },
                subscriptions: {
                  create: () => Effect.void,
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      );
    });

    it.effect("handles deleted customer when updating metadata", () => {
      let updatedMetadata: Record<string, string> | undefined;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.update({
          customerId: "cus_123",
          organizationSlug: "new-slug",
        });

        // Should create new metadata object when customer is deleted
        expect(updatedMetadata?.organizationSlug).toBe("new-slug");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  create: () => Effect.void,
                  retrieve: (id: string) =>
                    Effect.succeed({
                      id,
                      object: "customer" as const,
                      deleted: true,
                    }),
                  update: (
                    id: string,
                    params: {
                      name?: string;
                      metadata?: Record<string, string>;
                    },
                  ) => {
                    updatedMetadata = params.metadata;
                    return Effect.succeed({
                      id,
                      object: "customer" as const,
                      created: Date.now(),
                      livemode: false,
                      email: "test@example.com",
                      name: "Name",
                      metadata: params.metadata || {},
                    });
                  },
                  del: () => Effect.void,
                },
                subscriptions: {
                  create: () => Effect.void,
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      );
    });

    it.effect("does not update if no changes provided", () => {
      let updateCalled = false;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.update({
          customerId: "cus_123",
        });

        // Should not call update if nothing to change
        expect(updateCalled).toBe(false);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  create: () => Effect.void,
                  retrieve: () => Effect.void,
                  update: () => {
                    updateCalled = true;
                    return Effect.void;
                  },
                  del: () => Effect.void,
                },
                subscriptions: {
                  create: () => Effect.void,
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      );
    });
  });

  describe("cancelSubscriptions", () => {
    it.effect("cancels multiple active subscriptions", () => {
      const subscriptionIds: string[] = [];

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.cancelSubscriptions("cus_123");

        expect(subscriptionIds).toEqual(["sub_1", "sub_2"]);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  create: () => Effect.void,
                  del: () => Effect.void,
                },
                subscriptions: {
                  create: () => Effect.void,
                  list: () =>
                    Effect.succeed({
                      object: "list" as const,
                      data: [
                        {
                          id: "sub_1",
                          object: "subscription" as const,
                          status: "active" as const,
                        },
                        {
                          id: "sub_2",
                          object: "subscription" as const,
                          status: "active" as const,
                        },
                      ],
                      has_more: false,
                    }),
                  cancel: (id: string) => {
                    subscriptionIds.push(id);
                    return Effect.succeed({
                      id,
                      object: "subscription" as const,
                      status: "canceled" as const,
                    });
                  },
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      );
    });

    it.effect("handles customer with no active subscriptions", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.cancelSubscriptions("cus_123");

        // Test passes if no errors thrown
      }).pipe(Effect.provide(DefaultMockPayments)),
    );

    it.effect("returns StripeError when listing subscriptions fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers
          .cancelSubscriptions("cus_123")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Failed to list subscriptions");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  create: () => Effect.void,
                  del: () => Effect.void,
                },
                subscriptions: {
                  create: () => Effect.void,
                  list: () =>
                    Effect.fail(
                      new StripeError({
                        message: "Failed to list subscriptions",
                      }),
                    ),
                  cancel: () => Effect.void,
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("returns StripeError when cancelling subscription fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers
          .cancelSubscriptions("cus_123")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Failed to cancel subscription");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  create: () => Effect.void,
                  del: () => Effect.void,
                },
                subscriptions: {
                  create: () => Effect.void,
                  list: () =>
                    Effect.succeed({
                      object: "list" as const,
                      data: [
                        {
                          id: "sub_1",
                          object: "subscription" as const,
                          status: "active" as const,
                        },
                      ],
                      has_more: false,
                    }),
                  cancel: () =>
                    Effect.fail(
                      new StripeError({
                        message: "Failed to cancel subscription",
                      }),
                    ),
                },
                config: {
                  apiKey: "sk_test_mock",
                  routerPriceId: "price_test",
                  routerMeterId: "meter_test",
                },
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );
  });
});
