import { Context, Effect, Layer } from "effect";
import { describe, expect } from "@effect/vitest";
import { createCustomIt } from "@/tests/shared";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";

// Re-export describe and expect for convenience
export { describe, expect };

/**
 * Creates a Stripe layer for tests.
 * This is a lazy function so it's created after vi.mock() has been set up.
 */
const getTestStripe = () =>
  Stripe.layer({
    apiKey: "sk_test_123",
    routerPriceId: "price_test_mock",
  });

/**
 * Services that are automatically provided to all `it.effect` tests.
 */
export type TestServices = Stripe;

/**
 * Wraps a test function to automatically provide TestStripe layer.
 */
const wrapEffectTest =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (original: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (name: any, fn: any, timeout?: any) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
      return original(
        name,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unnecessary-type-assertion
        () => (fn() as any).pipe(Effect.provide(getTestStripe())),
        timeout,
      );
    };

/**
 * Type-safe `it` with `it.effect` that automatically provides Stripe layer.
 *
 * Use this instead of importing directly from @effect/vitest.
 *
 * @example
 * ```ts
 * import { it, expect } from "@/tests/payments";
 * import { Effect } from "effect";
 * import { Stripe } from "@/payments";
 *
 * it.effect("creates a customer", () =>
 *   Effect.gen(function* () {
 *     const stripe = yield* Stripe;
 *     const customer = yield* stripe.customers.create({ email: "test@example.com" });
 *     expect(customer.email).toBe("test@example.com");
 *   })
 * );
 * ```
 */
export const it = createCustomIt<TestServices>(wrapEffectTest);

// =============================================================================
// Mock Stripe and Payments for Integration Testing
// =============================================================================

/**
 * Comprehensive credit grant test data that covers all branch cases.
 *
 * Includes valid grants (counted) and invalid grants (not counted) to ensure
 * full branch coverage in getBalance() implementation.
 */
const MOCK_CREDIT_GRANTS_DATA = [
  // Valid grant #1: USD, router price - SHOULD BE COUNTED ($7)
  {
    amount: {
      monetary: {
        value: 700, // $7.00 in cents
        currency: "usd",
      },
    },
    applicability_config: {
      scope: {
        prices: [{ id: "price_test_mock_for_testing" }, { id: "price_other" }],
      },
    },
  },
  // Valid grant #2: USD, router price - SHOULD BE COUNTED ($11)
  {
    amount: {
      monetary: {
        value: 1100, // $11.00 in cents
        currency: "usd",
      },
    },
    applicability_config: {
      scope: {
        prices: [{ id: "price_test_mock_for_testing" }],
      },
    },
  },
  // Invalid: EUR currency - should NOT be counted
  {
    amount: {
      monetary: {
        value: 500, // €5.00 in cents
        currency: "eur",
      },
    },
    applicability_config: {
      scope: {
        prices: [{ id: "price_test_mock_for_testing" }],
      },
    },
  },
  // Invalid: No monetary amount (null) - should NOT be counted (line 250 coverage)
  {
    amount: {
      monetary: null,
    },
    applicability_config: {
      scope: {
        prices: [{ id: "price_test_mock_for_testing" }],
      },
    },
  },
  // Invalid: Different price - should NOT be counted (line 259 coverage)
  {
    amount: {
      monetary: {
        value: 1900, // $19.00 in cents
        currency: "usd",
      },
    },
    applicability_config: {
      scope: {
        prices: [{ id: "price_different" }],
      },
    },
  },
  // Invalid: No scope - should NOT be counted (line 259 coverage)
  {
    amount: {
      monetary: {
        value: 2300, // $23.00 in cents
        currency: "usd",
      },
    },
    applicability_config: {},
  },
  // Invalid: Scope but no prices array - should NOT be counted (line 259 coverage)
  {
    amount: {
      monetary: {
        value: 3100, // $31.00 in cents
        currency: "usd",
      },
    },
    applicability_config: {
      scope: {},
    },
  },
];

/**
 * Builder for creating custom Payments layers with specific behaviors.
 *
 * Allows overriding individual Stripe methods for error testing scenarios.
 * Mirrors the structure of the Payments service (customers, subscriptions).
 *
 * @example Mock subscription list failure
 * ```ts
 * const mockPayments = new MockPayments()
 *   .subscriptions.list(() =>
 *     Effect.fail(new StripeError({ message: "Failed to list subscriptions" }))
 *   )
 *   .build();
 *
 * yield* db.organizations.delete({...}).pipe(
 *   Effect.provide(new MockDrizzleORM().select([...]).build(mockPayments))
 * );
 * ```
 */
export class MockPayments {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private customersCreateResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private customersRetrieveResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private customersUpdateResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private customersDelResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private subscriptionsCreateResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private subscriptionsListResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private subscriptionsCancelResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private billingCreditGrantsListResult?: any;

  get customers() {
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      create: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.customersCreateResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      retrieve: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.customersRetrieveResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      update: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.customersUpdateResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.customersDelResult = result;
        return this;
      },
    };
  }

  get subscriptions() {
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      create: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.subscriptionsCreateResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      list: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.subscriptionsListResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      cancel: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.subscriptionsCancelResult = result;
        return this;
      },
    };
  }

  get billing() {
    return {
      creditGrants: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        list: (result: any) => {
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          this.billingCreditGrantsListResult = result;
          return this;
        },
      },
    };
  }

  /**
   * Builds a Layer<Payments> with custom Stripe behaviors.
   */
  build(): Layer.Layer<Payments> {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const customersCreateResult = this.customersCreateResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const customersRetrieveResult = this.customersRetrieveResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const customersUpdateResult = this.customersUpdateResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const customersDelResult = this.customersDelResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const subscriptionsCreateResult = this.subscriptionsCreateResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const subscriptionsListResult = this.subscriptionsListResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const subscriptionsCancelResult = this.subscriptionsCancelResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const billingCreditGrantsListResult = this.billingCreditGrantsListResult;

    const customStripe = Layer.succeed(Stripe, {
      customers: {
        create: (params: {
          email?: string;
          name?: string;
          metadata?: Record<string, string>;
        }) => {
          if (customersCreateResult !== undefined) {
            if (typeof customersCreateResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = customersCreateResult(params);

              return Effect.isEffect(result) ? result : Effect.succeed(result);
            }

            return Effect.isEffect(customersCreateResult)
              ? customersCreateResult
              : Effect.succeed(customersCreateResult);
          }
          // Default from MockStripe
          return Effect.succeed({
            id: `cus_mock_${crypto.randomUUID()}`,
            object: "customer" as const,
            created: Date.now(),
            livemode: false,
            email: params.email || null,
            name: params.name || null,
            metadata: params.metadata || {},
          });
        },
        retrieve: (id: string) => {
          if (customersRetrieveResult !== undefined) {
            if (typeof customersRetrieveResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = customersRetrieveResult(id);

              return Effect.isEffect(result) ? result : Effect.succeed(result);
            }

            return Effect.isEffect(customersRetrieveResult)
              ? customersRetrieveResult
              : Effect.succeed(customersRetrieveResult);
          }
          return Effect.succeed({
            id,
            object: "customer" as const,
            created: Date.now(),
            livemode: false,
            email: "mock@example.com",
            name: "Mock Customer",
            metadata: {},
          });
        },
        update: (
          id: string,
          params: { name?: string; metadata?: Record<string, string> },
        ) => {
          if (customersUpdateResult !== undefined) {
            if (typeof customersUpdateResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = customersUpdateResult(id, params);

              return Effect.isEffect(result) ? result : Effect.succeed(result);
            }

            return Effect.isEffect(customersUpdateResult)
              ? customersUpdateResult
              : Effect.succeed(customersUpdateResult);
          }
          return Effect.succeed({
            id,
            object: "customer" as const,
            created: Date.now(),
            livemode: false,
            email: "mock@example.com",
            name: params.name || "Mock Customer",
            metadata: params.metadata || {},
          });
        },
        del: (id: string) => {
          if (customersDelResult !== undefined) {
            if (typeof customersDelResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = customersDelResult(id);

              return Effect.isEffect(result) ? result : Effect.succeed(result);
            }

            return Effect.isEffect(customersDelResult)
              ? customersDelResult
              : Effect.succeed(customersDelResult);
          }
          return Effect.succeed({
            id,
            object: "customer" as const,
            deleted: true,
          });
        },
      },
      subscriptions: {
        create: (params: {
          customer: string;
          items: Array<{ price: string }>;
          metadata?: Record<string, string>;
        }) => {
          if (subscriptionsCreateResult !== undefined) {
            if (typeof subscriptionsCreateResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionsCreateResult(params);

              return Effect.isEffect(result) ? result : Effect.succeed(result);
            }

            return Effect.isEffect(subscriptionsCreateResult)
              ? subscriptionsCreateResult
              : Effect.succeed(subscriptionsCreateResult);
          }
          return Effect.succeed({
            id: `sub_mock_${crypto.randomUUID()}`,
            object: "subscription" as const,
            created: Date.now(),
            customer: params.customer,
            items: {
              object: "list" as const,
              data: params.items.map((item) => ({
                id: `si_mock_${crypto.randomUUID()}`,
                object: "subscription_item" as const,
                price: { id: item.price },
              })),
            },
            status: "active" as const,
            metadata: params.metadata || {},
          });
        },
        list: (params?: { customer?: string; status?: string }) => {
          if (subscriptionsListResult !== undefined) {
            if (typeof subscriptionsListResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionsListResult(params);

              return Effect.isEffect(result) ? result : Effect.succeed(result);
            }

            return Effect.isEffect(subscriptionsListResult)
              ? subscriptionsListResult
              : Effect.succeed(subscriptionsListResult);
          }
          return Effect.succeed({
            object: "list" as const,
            data: [],
            has_more: false,
          });
        },
        cancel: (id: string) => {
          if (subscriptionsCancelResult !== undefined) {
            if (typeof subscriptionsCancelResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionsCancelResult(id);

              return Effect.isEffect(result) ? result : Effect.succeed(result);
            }

            return Effect.isEffect(subscriptionsCancelResult)
              ? subscriptionsCancelResult
              : Effect.succeed(subscriptionsCancelResult);
          }
          return Effect.succeed({
            id,
            object: "subscription" as const,
            status: "canceled" as const,
          });
        },
      },
      billing: {
        creditGrants: {
          list: (params?: { customer?: string }) => {
            if (billingCreditGrantsListResult !== undefined) {
              if (typeof billingCreditGrantsListResult === "function") {
                // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
                const result = billingCreditGrantsListResult(params);
                // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unsafe-member-access
                return result?._tag ? result : Effect.succeed(result);
              }

              return Effect.isEffect(billingCreditGrantsListResult)
                ? billingCreditGrantsListResult
                : Effect.succeed(billingCreditGrantsListResult);
            }
            // Default: use comprehensive test data
            return Effect.succeed({
              object: "list" as const,
              data: MOCK_CREDIT_GRANTS_DATA,
              has_more: false,
            });
          },
        },
      },
      config: {
        apiKey: "sk_test_mock",
        routerPriceId: "price_test_mock_for_testing",
      },
    } as unknown as Context.Tag.Service<typeof Stripe>);

    return Payments.Default.pipe(Layer.provide(customStripe));
  }
}

/**
 * Mock Stripe layer for testing that provides only the Stripe service.
 *
 * Use this when testing code that directly requires Stripe (like Payments.Default).
 * For most tests, use DefaultMockPayments instead which provides the full Payments service.
 */
export const MockStripe = Layer.succeed(Stripe, {
  customers: {
    create: (params: {
      email?: string;
      name?: string;
      metadata?: Record<string, string>;
    }) =>
      Effect.succeed({
        id: `cus_mock_${crypto.randomUUID()}`,
        object: "customer" as const,
        created: Date.now(),
        livemode: false,
        email: params.email || null,
        name: params.name || null,
        metadata: params.metadata || {},
      }),
    retrieve: (id: string) =>
      Effect.succeed({
        id,
        object: "customer" as const,
        created: Date.now(),
        livemode: false,
        email: "mock@example.com",
        name: "Mock Customer",
        metadata: {},
      }),
    update: (
      id: string,
      params: { name?: string; metadata?: Record<string, string> },
    ) =>
      Effect.succeed({
        id,
        object: "customer" as const,
        created: Date.now(),
        livemode: false,
        email: "mock@example.com",
        name: params.name || "Mock Customer",
        metadata: params.metadata || {},
      }),
    del: (id: string) =>
      Effect.succeed({
        id,
        object: "customer" as const,
        deleted: true,
      }),
  },
  subscriptions: {
    create: (params: {
      customer: string;
      items: Array<{ price: string }>;
      metadata?: Record<string, string>;
    }) =>
      Effect.succeed({
        id: `sub_mock_${crypto.randomUUID()}`,
        object: "subscription" as const,
        created: Date.now(),
        customer: params.customer,
        items: {
          object: "list" as const,
          data: params.items.map((item) => ({
            id: `si_mock_${crypto.randomUUID()}`,
            object: "subscription_item" as const,
            price: { id: item.price },
          })),
        },
        status: "active" as const,
        metadata: params.metadata || {},
      }),
    list: () =>
      Effect.succeed({
        object: "list" as const,
        data: [],
        has_more: false,
      }),
    cancel: (id: string) =>
      Effect.succeed({
        id,
        object: "subscription" as const,
        status: "canceled" as const,
      }),
  },
  billing: {
    creditGrants: {
      list: () =>
        Effect.succeed({
          object: "list" as const,
          data: MOCK_CREDIT_GRANTS_DATA,
          has_more: false,
        }),
    },
  },
  config: {
    apiKey: "sk_test_mock",
    routerPriceId: "price_test_mock_for_testing",
  },
} as unknown as Context.Tag.Service<typeof Stripe>);

/**
 * Default MockPayments layer for testing.
 *
 * Provides a fully functional Payments service backed by MockStripe.
 * Use this in tests that need to interact with payment services without
 * making real API calls.
 *
 * @example
 * ```ts
 * import { DefaultMockPayments } from "@/tests/payments";
 *
 * it.effect("creates a customer", () =>
 *   Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const result = yield* payments.customers.create({
 *       organizationId: "org_123",
 *       organizationName: "Test Org",
 *       organizationSlug: "test-org",
 *       email: "test@example.com",
 *     });
 *     expect(result.customerId).toMatch(/^cus_mock_/);
 *   }).pipe(Effect.provide(DefaultMockPayments))
 * );
 * ```
 */
export const DefaultMockPayments = new MockPayments().build();
