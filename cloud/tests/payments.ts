import { SqlClient } from "@effect/sql";
import { describe, expect, it as vitestIt } from "@effect/vitest";
import { Context, Effect, Layer } from "effect";
import StripeSDK from "stripe";
import { assert } from "vitest";

import type { PlanTier } from "@/payments/subscriptions";

import { DrizzleORM } from "@/db/client";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import { TestDrizzleORM } from "@/tests/db";
import { MockDrizzleORMLayer } from "@/tests/mock-drizzle";
import { createCustomIt, ensureEffect, withRollback } from "@/tests/shared";

// Re-export describe and expect for convenience
export { describe, expect, assert };

/**
 * Creates a Stripe layer for tests.
 * This is a lazy function so it's created after vi.mock() has been set up.
 */
const getTestStripe = () =>
  Stripe.layer({
    secretKey: "sk_test_mock",
    webhookSecret: "whsec_test_mock",
    routerPriceId: "price_test_mock",
    routerMeterId: "meter_test_mock",
    cloudFreePriceId: "price_cloud_free_mock",
    cloudProPriceId: "price_cloud_pro_mock",
    cloudTeamPriceId: "price_cloud_team_mock",
    cloudSpansPriceId: "price_cloud_spans_mock",
    cloudSpansMeterId: "meter_cloud_spans_mock",
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
 * Wraps a test function to automatically provide TestStripe AND TestDrizzleORM layers,
 * AND wrap in rollback transaction.
 *
 * IMPORTANT: TestDrizzleORM must be provided so that `withRollback` can see the SqlClient.
 * Tests using this wrapper should NOT provide their own database layer via Effect.provide(),
 * as that would create a separate database connection that bypasses the transaction rollback.
 * Instead, use TestPaymentsMockFixture which only provides Payments mocks.
 */
const wrapEffectTestWithRollback =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (original: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (name: any, fn: any, timeout?: any) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
      return original(
        name,
        () =>
          // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unsafe-call
          fn()
            // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
            .pipe(withRollback)
            // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
            .pipe(Effect.provide(Layer.merge(getTestStripe(), TestDrizzleORM))),
        timeout,
      );
    };

/**
 * Type-safe `it` with `it.effect` and `it.rollback` that automatically provides Stripe layer.
 *
 * Use this instead of importing directly from @effect/vitest.
 *
 * - `it.effect`: Provides Stripe layer for tests
 * - `it.rollback`: Provides Stripe layer AND wraps in transaction rollback for DB isolation
 *
 * @example
 * ```ts
 * import { it, expect } from "@/tests/payments";
 * import { Effect } from "effect";
 * import { Stripe } from "@/payments";
 *
 * // Mock test (no DB)
 * it.effect("creates a customer", () =>
 *   Effect.gen(function* () {
 *     const stripe = yield* Stripe;
 *     const customer = yield* stripe.customers.create({ email: "test@example.com" });
 *     expect(customer.email).toBe("test@example.com");
 *   })
 * );
 *
 * // Real DB test with rollback
 * it.rollback("creates user without polluting DB", () =>
 *   Effect.gen(function* () {
 *     const db = yield* Database;
 *     const user = yield* db.users.create({ ... });
 *     // User will be rolled back after test
 *   })
 * );
 * ```
 */
export const it = Object.assign(createCustomIt<TestServices>(wrapEffectTest), {
  rollback: Object.assign(wrapEffectTestWithRollback(vitestIt.effect), {
    skip: wrapEffectTestWithRollback(vitestIt.effect.skip),
    only: wrapEffectTestWithRollback(vitestIt.effect.only),
    fails: wrapEffectTestWithRollback(vitestIt.effect.fails),
    skipIf: (condition: unknown) =>
      wrapEffectTestWithRollback(vitestIt.effect.skipIf(condition)),
    runIf: (condition: unknown) =>
      wrapEffectTestWithRollback(vitestIt.effect.runIf(condition)),
  }),
});

// =============================================================================
// Shared Test Constants
// =============================================================================

/** Default test IDs */
export const TEST_IDS = {
  customer: "cus_test_mock",
  subscription: "sub_test_mock",
  subscriptionItem: "si_test_mock",
  paymentMethod: "pm_test_mock",
  invoice: "in_test_mock",
  paymentIntent: "pi_test_mock",
  schedule: "sub_sched_123",
} as const;

/** Default test card data */
export const DEFAULT_TEST_CARD = {
  brand: "visa" as const,
  last4: "4242",
  exp_month: 12,
  exp_year: 2025,
} as const;

/** Time calculation constants */
export const TIME_CONSTANTS = {
  DAY_IN_SECONDS: 24 * 3600,
  BILLING_PERIOD_DAYS: 30,
  get BILLING_PERIOD_SECONDS() {
    return this.BILLING_PERIOD_DAYS * this.DAY_IN_SECONDS;
  },
} as const;

/** Price ID mapping */
export const MOCK_PRICE_IDS = {
  free: "price_cloud_free_mock",
  pro: "price_cloud_pro_mock",
  team: "price_cloud_team_mock",
  spans: "price_cloud_spans_mock",
  router: "price_test_mock_for_testing",
} as const;

// =============================================================================
// Shared Test Helpers
// =============================================================================

/** Maps plan type to mock price ID */
export function getPriceIdForPlan(plan: PlanTier): string {
  return MOCK_PRICE_IDS[plan];
}

/** Gets current Unix timestamp (seconds since epoch) */
export function getTestTimestamp(): number {
  return Math.floor(Date.now() / 1000);
}

/** Creates default time values for test subscriptions */
export function getTestPeriodTimes() {
  const now = getTestTimestamp();
  const periodEnd = now + TIME_CONSTANTS.BILLING_PERIOD_SECONDS;
  return { now, periodEnd };
}

/** Creates a test payment method object */
export function createTestPaymentMethod(
  id: string = TEST_IDS.paymentMethod,
  card: Partial<{
    brand?: string;
    last4?: string;
    exp_month?: number;
    exp_year?: number;
  }> = {},
): StripeSDK.PaymentMethod {
  // Filter out undefined values to prevent overwriting defaults
  const definedCardProps = Object.fromEntries(
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    Object.entries(card).filter(([_, value]) => value !== undefined),
  );

  return {
    id,
    object: "payment_method" as const,
    card: { ...DEFAULT_TEST_CARD, ...definedCardProps },
    type: "card" as const,
  } as StripeSDK.PaymentMethod;
}

/** Creates a test customer object */
export function createTestCustomer(params: {
  id?: string;
  paymentMethodId?: string | null;
  includePaymentMethod?: boolean;
  email?: string | null;
  name?: string | null;
  metadata?: Record<string, string>;
}): StripeSDK.Customer {
  const {
    id = TEST_IDS.customer,
    paymentMethodId = TEST_IDS.paymentMethod,
    includePaymentMethod = false,
    email = null,
    name = null,
    metadata = {},
  } = params;

  return {
    id,
    object: "customer" as const,
    created: Date.now(),
    livemode: false,
    email,
    name,
    metadata,
    ...(includePaymentMethod &&
      paymentMethodId && {
        invoice_settings: {
          default_payment_method: paymentMethodId,
        },
      }),
  } as StripeSDK.Customer;
}

/** Creates a Stripe list response object */
export function createListResponse<T>(data: T[]): {
  object: "list";
  data: T[];
  has_more: boolean;
} {
  return {
    object: "list" as const,
    data,
    has_more: false,
  };
}

/** Creates a test subscription object */
export function createTestSubscription(params: {
  id?: string;
  status?: string;
  priceId: string;
  paymentMethodId?: string | null;
  periodEnd?: number;
  periodStart?: number;
  additionalItems?: Array<{ id: string; priceId: string; quantity?: number }>;
}): StripeSDK.Subscription {
  const {
    id = TEST_IDS.subscription,
    status = "active",
    priceId,
    paymentMethodId = null,
    periodEnd,
    periodStart,
    additionalItems = [],
  } = params;

  const times =
    periodEnd && periodStart
      ? { periodEnd, periodStart }
      : (() => {
          const { now, periodEnd: end } = getTestPeriodTimes();
          return { periodEnd: end, periodStart: now };
        })();

  return {
    id,
    object: "subscription" as const,
    status,
    current_period_end: times.periodEnd,
    current_period_start: times.periodStart,
    ...(paymentMethodId && {
      default_payment_method: paymentMethodId,
    }),
    items: {
      data: [
        {
          id: TEST_IDS.subscriptionItem,
          price: { id: priceId },
        },
        ...additionalItems.map((item) => ({
          id: item.id,
          price: { id: item.priceId },
          ...(item.quantity !== undefined && { quantity: item.quantity }),
        })),
      ],
    },
  } as StripeSDK.Subscription;
}

/** Creates a test invoice object */
export function createTestInvoice(params: {
  id?: string;
  amountDue?: number;
  total?: number;
  periodEnd?: number;
  paymentIntentId?: string | null;
  paymentIntentStatus?: string;
  clientSecret?: string | null;
}): StripeSDK.Invoice {
  const {
    id = TEST_IDS.invoice,
    amountDue = 5000,
    total = 10000,
    periodEnd,
    paymentIntentId = null,
    paymentIntentStatus,
    clientSecret = null,
  } = params;

  const invoice: StripeSDK.Invoice = {
    id,
    object: "invoice" as const,
    amount_due: amountDue,
    total,
    period_end:
      periodEnd ?? getTestTimestamp() + TIME_CONSTANTS.BILLING_PERIOD_SECONDS,
  } as StripeSDK.Invoice;

  if (paymentIntentId) {
    invoice.payment_intent = {
      id: paymentIntentId,
      status: paymentIntentStatus,
      client_secret: clientSecret,
    } as StripeSDK.PaymentIntent;
  }

  return invoice;
}

/** Creates a test deleted customer object */
export function createTestDeletedCustomer(
  id: string = TEST_IDS.customer,
): StripeSDK.DeletedCustomer {
  return {
    id,
    object: "customer" as const,
    deleted: true,
  } as StripeSDK.DeletedCustomer;
}

/** Creates a test payment intent object */
export function createTestPaymentIntent(params: {
  id?: string;
  status?: string;
  clientSecret?: string;
}): StripeSDK.PaymentIntent {
  const {
    id = TEST_IDS.paymentIntent,
    status = "requires_payment_method",
    clientSecret = "pi_secret_mock",
  } = params;

  return {
    id,
    object: "payment_intent" as const,
    status,
    client_secret: clientSecret,
  } as StripeSDK.PaymentIntent;
}

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
  private subscriptionsRetrieveResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private subscriptionsUpdateResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private subscriptionSchedulesListResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private subscriptionSchedulesCreateResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private subscriptionSchedulesUpdateResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private subscriptionSchedulesReleaseResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private paymentMethodsListResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private paymentMethodsRetrieveResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private invoicesRetrieveUpcomingResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private pricesRetrieveResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private billingCreditGrantsListResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private billingCreditGrantsCreateResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private billingMetersListEventSummariesResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private paymentIntentsCreateResult?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private stripeConfig?: any;

  config(config: unknown) {
    this.stripeConfig = config;
    return this;
  }

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
      retrieve: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.subscriptionsRetrieveResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      update: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.subscriptionsUpdateResult = result;
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

  get subscriptionSchedules() {
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      list: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.subscriptionSchedulesListResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      create: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.subscriptionSchedulesCreateResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      update: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.subscriptionSchedulesUpdateResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      release: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.subscriptionSchedulesReleaseResult = result;
        return this;
      },
    };
  }

  get paymentMethods() {
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      list: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.paymentMethodsListResult = result;
        return this;
      },
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      retrieve: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.paymentMethodsRetrieveResult = result;
        return this;
      },
    };
  }

  get invoices() {
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      retrieveUpcoming: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.invoicesRetrieveUpcomingResult = result;
        return this;
      },
    };
  }

  get prices() {
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      retrieve: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.pricesRetrieveResult = result;
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
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        create: (result: any) => {
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          this.billingCreditGrantsCreateResult = result;
          return this;
        },
      },
      meters: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        listEventSummaries: (result: any) => {
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          this.billingMetersListEventSummariesResult = result;
          return this;
        },
      },
    };
  }

  get paymentIntents() {
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      create: (result: any) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        this.paymentIntentsCreateResult = result;
        return this;
      },
    };
  }

  /**
   * Builds a Layer<Stripe> with custom behaviors.
   * Use this when you need to provide a custom Stripe layer directly.
   */
  buildStripe(): Layer.Layer<Stripe> {
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
    const subscriptionsRetrieveResult = this.subscriptionsRetrieveResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const subscriptionsUpdateResult = this.subscriptionsUpdateResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const subscriptionsCancelResult = this.subscriptionsCancelResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const subscriptionSchedulesListResult =
      this.subscriptionSchedulesListResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const subscriptionSchedulesCreateResult =
      this.subscriptionSchedulesCreateResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const subscriptionSchedulesUpdateResult =
      this.subscriptionSchedulesUpdateResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const subscriptionSchedulesReleaseResult =
      this.subscriptionSchedulesReleaseResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const paymentMethodsListResult = this.paymentMethodsListResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const paymentMethodsRetrieveResult = this.paymentMethodsRetrieveResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const invoicesRetrieveUpcomingResult = this.invoicesRetrieveUpcomingResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const pricesRetrieveResult = this.pricesRetrieveResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const billingCreditGrantsListResult = this.billingCreditGrantsListResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const billingCreditGrantsCreateResult =
      this.billingCreditGrantsCreateResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const billingMetersListEventSummariesResult =
      this.billingMetersListEventSummariesResult;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    const paymentIntentsCreateResult = this.paymentIntentsCreateResult;

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

              return ensureEffect(result);
            }

            return Effect.isEffect(customersCreateResult)
              ? customersCreateResult
              : Effect.succeed(customersCreateResult);
          }
          // Default from MockStripe
          return Effect.succeed(
            createTestCustomer({
              id: `cus_mock_${crypto.randomUUID()}`,
              email: params.email || null,
              name: params.name || null,
              metadata: params.metadata || {},
            }),
          );
        },
        retrieve: (id: string) => {
          if (customersRetrieveResult !== undefined) {
            if (typeof customersRetrieveResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = customersRetrieveResult(id);

              return ensureEffect(result);
            }

            return Effect.isEffect(customersRetrieveResult)
              ? customersRetrieveResult
              : Effect.succeed(customersRetrieveResult);
          }
          return Effect.succeed(
            createTestCustomer({
              id,
              email: "mock@example.com",
              name: "Mock Customer",
              metadata: {},
            }),
          );
        },
        update: (
          id: string,
          params: { name?: string; metadata?: Record<string, string> },
        ) => {
          if (customersUpdateResult !== undefined) {
            if (typeof customersUpdateResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = customersUpdateResult(id, params);

              return ensureEffect(result);
            }

            return Effect.isEffect(customersUpdateResult)
              ? customersUpdateResult
              : Effect.succeed(customersUpdateResult);
          }
          return Effect.succeed(
            createTestCustomer({
              id,
              email: "mock@example.com",
              name: params.name || "Mock Customer",
              metadata: params.metadata || {},
            }),
          );
        },
        del: (id: string) => {
          if (customersDelResult !== undefined) {
            if (typeof customersDelResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = customersDelResult(id);

              return ensureEffect(result);
            }

            return Effect.isEffect(customersDelResult)
              ? customersDelResult
              : Effect.succeed(customersDelResult);
          }
          return Effect.succeed(createTestDeletedCustomer(id));
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

              return ensureEffect(result);
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

              return ensureEffect(result);
            }

            return Effect.isEffect(subscriptionsListResult)
              ? subscriptionsListResult
              : Effect.succeed(subscriptionsListResult);
          }
          return Effect.succeed({
            object: "list" as const,
            data: [
              createTestSubscription({
                id: "sub_mock_default",
                status: "active",
                priceId: "price_cloud_free_mock",
              }),
            ],
            has_more: false,
          });
        },
        retrieve: (id: string) => {
          if (subscriptionsRetrieveResult !== undefined) {
            if (typeof subscriptionsRetrieveResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionsRetrieveResult(id);

              return ensureEffect(result);
            }

            return ensureEffect(subscriptionsRetrieveResult);
          }
          return Effect.succeed(
            createTestSubscription({
              id,
              status: "active",
              priceId: "price_cloud_free_mock",
            }),
          );
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        update: (id: string, params: any) => {
          if (subscriptionsUpdateResult !== undefined) {
            if (typeof subscriptionsUpdateResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionsUpdateResult(id, params);

              return ensureEffect(result);
            }

            return Effect.isEffect(subscriptionsUpdateResult)
              ? subscriptionsUpdateResult
              : Effect.succeed(subscriptionsUpdateResult);
          }
          return Effect.succeed({
            id,
            object: "subscription" as const,
            status: "active" as const,
            current_period_end:
              getTestTimestamp() + TIME_CONSTANTS.BILLING_PERIOD_SECONDS,
            current_period_start: getTestTimestamp(),
            // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-assignment
            items: params.items || {
              data: [
                {
                  id: "si_mock_default",
                  price: {
                    id: "price_cloud_pro_mock",
                  },
                },
              ],
            },
            latest_invoice: null,
          });
        },
        cancel: (id: string) => {
          if (subscriptionsCancelResult !== undefined) {
            if (typeof subscriptionsCancelResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionsCancelResult(id);

              return ensureEffect(result);
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
      subscriptionSchedules: {
        list: (params?: { customer?: string }) => {
          if (subscriptionSchedulesListResult !== undefined) {
            if (typeof subscriptionSchedulesListResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionSchedulesListResult(params);

              return ensureEffect(result);
            }

            return Effect.isEffect(subscriptionSchedulesListResult)
              ? subscriptionSchedulesListResult
              : Effect.succeed(subscriptionSchedulesListResult);
          }
          return Effect.succeed({
            object: "list" as const,
            data: [],
            has_more: false,
          });
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        create: (params: any) => {
          if (subscriptionSchedulesCreateResult !== undefined) {
            if (typeof subscriptionSchedulesCreateResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionSchedulesCreateResult(params);

              return ensureEffect(result);
            }

            return Effect.isEffect(subscriptionSchedulesCreateResult)
              ? subscriptionSchedulesCreateResult
              : Effect.succeed(subscriptionSchedulesCreateResult);
          }
          return Effect.succeed({
            id: `sched_mock_${crypto.randomUUID()}`,
            object: "subscription_schedule" as const,
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
            subscription: params.from_subscription || "sub_mock_default",
          });
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        update: (id: string, params: any) => {
          if (subscriptionSchedulesUpdateResult !== undefined) {
            if (typeof subscriptionSchedulesUpdateResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionSchedulesUpdateResult(id, params);

              return ensureEffect(result);
            }

            return Effect.isEffect(subscriptionSchedulesUpdateResult)
              ? subscriptionSchedulesUpdateResult
              : Effect.succeed(subscriptionSchedulesUpdateResult);
          }
          return Effect.succeed({
            id,
            object: "subscription_schedule" as const,
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
            phases: params.phases,
          });
        },
        release: (id: string) => {
          if (subscriptionSchedulesReleaseResult !== undefined) {
            if (typeof subscriptionSchedulesReleaseResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = subscriptionSchedulesReleaseResult(id);

              return ensureEffect(result);
            }

            return Effect.isEffect(subscriptionSchedulesReleaseResult)
              ? subscriptionSchedulesReleaseResult
              : Effect.succeed(subscriptionSchedulesReleaseResult);
          }
          return Effect.succeed({
            id: "sub_mock_released",
            object: "subscription" as const,
          });
        },
      },
      paymentMethods: {
        list: (params?: { customer?: string; type?: string }) => {
          if (paymentMethodsListResult !== undefined) {
            if (typeof paymentMethodsListResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = paymentMethodsListResult(params);

              return ensureEffect(result);
            }

            return Effect.isEffect(paymentMethodsListResult)
              ? paymentMethodsListResult
              : Effect.succeed(paymentMethodsListResult);
          }
          return Effect.succeed({
            object: "list" as const,
            data: [],
            has_more: false,
          });
        },
        retrieve: (id: string) => {
          if (paymentMethodsRetrieveResult !== undefined) {
            if (typeof paymentMethodsRetrieveResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = paymentMethodsRetrieveResult(id);

              return ensureEffect(result);
            }

            return Effect.isEffect(paymentMethodsRetrieveResult)
              ? paymentMethodsRetrieveResult
              : Effect.succeed(paymentMethodsRetrieveResult);
          }
          return Effect.succeed(createTestPaymentMethod(id));
        },
      },
      invoices: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        retrieveUpcoming: (params: any) => {
          if (invoicesRetrieveUpcomingResult !== undefined) {
            if (typeof invoicesRetrieveUpcomingResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = invoicesRetrieveUpcomingResult(params);

              return ensureEffect(result);
            }

            return Effect.isEffect(invoicesRetrieveUpcomingResult)
              ? invoicesRetrieveUpcomingResult
              : Effect.succeed(invoicesRetrieveUpcomingResult);
          }
          return Effect.succeed({
            id: "in_upcoming",
            object: "invoice" as const,
            amount_due: 5000,
            total: 10000,
            period_end:
              getTestTimestamp() + TIME_CONSTANTS.BILLING_PERIOD_SECONDS,
          });
        },
      },
      prices: {
        retrieve: () => {
          if (pricesRetrieveResult !== undefined) {
            if (typeof pricesRetrieveResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = pricesRetrieveResult();

              return ensureEffect(result);
            }

            return Effect.isEffect(pricesRetrieveResult)
              ? pricesRetrieveResult
              : Effect.succeed(pricesRetrieveResult);
          }
          return Effect.succeed({
            id: "price_default",
            object: "price" as const,
            unit_amount: 1000,
            currency: "usd",
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
          create: (params: StripeSDK.Billing.CreditGrantCreateParams) => {
            if (billingCreditGrantsCreateResult !== undefined) {
              if (typeof billingCreditGrantsCreateResult === "function") {
                // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
                const result = billingCreditGrantsCreateResult(params);
                return Effect.isEffect(result)
                  ? result
                  : Effect.succeed(result);
              }

              return Effect.isEffect(billingCreditGrantsCreateResult)
                ? billingCreditGrantsCreateResult
                : Effect.succeed(billingCreditGrantsCreateResult);
            }
            // Default mock
            return Effect.succeed({
              id: `credgr_test_${crypto.randomUUID()}`,
            });
          },
        },
        meters: {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          listEventSummaries: (params?: any) => {
            if (billingMetersListEventSummariesResult !== undefined) {
              if (typeof billingMetersListEventSummariesResult === "function") {
                // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
                const result = billingMetersListEventSummariesResult(params);
                return ensureEffect(result);
              }

              return Effect.isEffect(billingMetersListEventSummariesResult)
                ? billingMetersListEventSummariesResult
                : Effect.succeed(billingMetersListEventSummariesResult);
            }
            // Default: return zero usage
            return Effect.succeed({
              object: "list" as const,
              data: [{ aggregated_value: 0 }],
              has_more: false,
            });
          },
        },
        meterEvents: {
          create: () =>
            Effect.succeed({
              id: `evt_mock_${crypto.randomUUID()}`,
              object: "billing.meter_event" as const,
              created: Date.now(),
              event_name: "use_credits",
              livemode: false,
            }),
        },
      },
      paymentIntents: {
        create: (params: StripeSDK.PaymentIntentCreateParams) => {
          if (paymentIntentsCreateResult !== undefined) {
            if (typeof paymentIntentsCreateResult === "function") {
              // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-call
              const result = paymentIntentsCreateResult(params);
              return ensureEffect(result);
            }

            return Effect.isEffect(paymentIntentsCreateResult)
              ? paymentIntentsCreateResult
              : Effect.succeed(paymentIntentsCreateResult);
          }
          // Default mock
          return Effect.succeed({
            id: `pi_test_${crypto.randomUUID()}`,
            client_secret: `pi_test_${crypto.randomUUID()}_secret_${crypto.randomUUID()}`,
          });
        },
      },
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      config: this.stripeConfig ?? {
        apiKey: "sk_test_mock",
        routerPriceId: "price_test_mock_for_testing",
        routerMeterId: "meter_test_mock",
        cloudFreePriceId: "price_cloud_free_mock",
        cloudProPriceId: "price_cloud_pro_mock",
        cloudTeamPriceId: "price_cloud_team_mock",
        cloudSpansPriceId: "price_cloud_spans_mock",
        cloudSpansMeterId: "meter_cloud_spans_mock",
      },
    } as unknown as Context.Tag.Service<typeof Stripe>);

    return customStripe;
  }

  /**
   * Builds a Layer<Payments> with custom Stripe behaviors.
   */
  build(): Layer.Layer<Payments> {
    return Payments.Default.pipe(
      Layer.provide(this.buildStripe()),
      Layer.provide(MockDrizzleORMLayer),
    );
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
      Effect.succeed(
        createTestCustomer({
          id: `cus_mock_${crypto.randomUUID()}`,
          email: params.email || null,
          name: params.name || null,
          metadata: params.metadata || {},
        }),
      ),
    retrieve: (id: string) =>
      Effect.succeed(
        createTestCustomer({
          id,
          email: "mock@example.com",
          name: "Mock Customer",
          metadata: {},
          includePaymentMethod: true,
        }),
      ),
    update: (
      id: string,
      params: { name?: string; metadata?: Record<string, string> },
    ) =>
      Effect.succeed(
        createTestCustomer({
          id,
          email: "mock@example.com",
          name: params.name || "Mock Customer",
          metadata: params.metadata || {},
        }),
      ),
    del: (id: string) => Effect.succeed(createTestDeletedCustomer(id)),
  },
  subscriptions: {
    create: (params: {
      customer: string;
      items: Array<{ price: string }>;
      metadata?: Record<string, string>;
    }) =>
      Effect.succeed({
        ...createTestSubscription({
          id: `sub_mock_${crypto.randomUUID()}`,
          status: "active",
          priceId: "price_cloud_team_mock", // Always use team plan for tests to avoid seat limits
        }),
        customer: params.customer,
        metadata: params.metadata || {},
      }),
    list: (params?: { customer?: string }) =>
      Effect.succeed({
        object: "list" as const,
        data: [
          {
            ...createTestSubscription({
              id: "sub_mock_default",
              status: "active",
              priceId: "price_cloud_team_mock",
            }),
            customer: params?.customer || "cus_mock_default",
          },
        ],
        has_more: false,
      }),
    retrieve: (id: string) =>
      Effect.succeed(
        createTestSubscription({
          id,
          status: "active",
          priceId: "price_cloud_team_mock",
        }),
      ),
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    update: (id: string, params: any) =>
      Effect.succeed({
        id,
        object: "subscription" as const,
        status: "active" as const,
        current_period_end:
          getTestTimestamp() + TIME_CONSTANTS.BILLING_PERIOD_SECONDS,
        current_period_start: getTestTimestamp(),
        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-assignment
        items: params.items || {
          data: [
            {
              id: "si_mock_default",
              price: {
                id: "price_cloud_pro_mock",
              },
            },
          ],
        },
        latest_invoice: null,
      }),
    cancel: (id: string) =>
      Effect.succeed({
        id,
        object: "subscription" as const,
        status: "canceled" as const,
      }),
  },
  subscriptionSchedules: {
    list: () =>
      Effect.succeed({
        object: "list" as const,
        data: [],
        has_more: false,
      }),
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    create: (params: any) =>
      Effect.succeed({
        id: `sched_mock_${crypto.randomUUID()}`,
        object: "subscription_schedule" as const,
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
        subscription: params.from_subscription || "sub_mock_default",
      }),
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    update: (id: string, params: any) =>
      Effect.succeed({
        id,
        object: "subscription_schedule" as const,
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
        phases: params.phases,
      }),
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    release: (_id: string) =>
      Effect.succeed({
        id: "sub_mock_released",
        object: "subscription" as const,
      }),
  },
  setupIntents: {
    create: (params: { customer: string }) =>
      Effect.succeed({
        id: `seti_mock_${crypto.randomUUID()}`,
        object: "setup_intent" as const,
        client_secret: `seti_mock_${crypto.randomUUID()}_secret_${crypto.randomUUID()}`,
        customer: params.customer,
      }),
  },
  paymentMethods: {
    list: () =>
      Effect.succeed({
        object: "list" as const,
        data: [createTestPaymentMethod()],
        has_more: false,
      }),
    retrieve: (id: string) =>
      Effect.succeed({
        id,
        object: "payment_method" as const,
        card: DEFAULT_TEST_CARD,
        type: "card" as const,
      }),
    detach: (id: string) =>
      Effect.succeed({
        id,
        object: "payment_method" as const,
      }),
  },
  invoices: {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars
    retrieveUpcoming: (_params: any) =>
      Effect.succeed({
        id: "in_upcoming",
        object: "invoice" as const,
        amount_due: 5000,
        total: 10000,
        period_end: getTestTimestamp() + TIME_CONSTANTS.BILLING_PERIOD_SECONDS,
      }),
  },
  prices: {
    retrieve: (priceId: string) =>
      Effect.succeed({
        id: priceId,
        object: "price" as const,
        unit_amount: 1000, // $10.00 in cents (default test price)
        currency: "usd",
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
      create: () =>
        Effect.succeed({
          id: `credgr_test_${crypto.randomUUID()}`,
        }),
    },
    meters: {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      listEventSummaries: (_meterId: string, _params?: unknown) =>
        Effect.succeed({
          object: "list" as const,
          data: [{ aggregated_value: 0 }],
          has_more: false,
        }),
    },
    meterEvents: {
      create: () =>
        Effect.succeed({
          id: `evt_mock_${crypto.randomUUID()}`,
          object: "billing.meter_event" as const,
          created: Date.now(),
          event_name: "use_credits",
          livemode: false,
        }),
    },
  },
  paymentIntents: {
    create: () =>
      Effect.succeed({
        id: `pi_test_${crypto.randomUUID()}`,
        client_secret: `pi_test_${crypto.randomUUID()}_secret_${crypto.randomUUID()}`,
      }),
  },
  config: {
    apiKey: "sk_test_mock",
    routerPriceId: MOCK_PRICE_IDS.router,
    routerMeterId: "meter_test_mock",
    cloudFreePriceId: MOCK_PRICE_IDS.free,
    cloudProPriceId: MOCK_PRICE_IDS.pro,
    cloudTeamPriceId: MOCK_PRICE_IDS.team,
    cloudSpansPriceId: MOCK_PRICE_IDS.spans,
    cloudSpansMeterId: "meter_cloud_spans_mock",
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
 *     expect(result.stripeCustomerId).toMatch(/^cus_mock_/);
 *   }).pipe(Effect.provide(DefaultMockPayments))
 * );
 * ```
 */
export const DefaultMockPayments = new MockPayments().build();
/**
 * Parameters for TestSubscriptionFixture.
 */
export interface TestSubscriptionFixtureParams {
  /** Plan tier (defaults to "free") */
  plan?: PlanTier;
  /** Subscription status (defaults to "active") */
  status?: "active" | "canceled" | "past_due";
  /** Whether customer has a payment method (defaults to false) */
  hasPaymentMethod?: boolean;
  /** Stripe customer ID (defaults to "TEST_IDS.customer") */
  stripeCustomerId?: string;
  /** Subscription ID (defaults to "TEST_IDS.subscription") */
  subscriptionId?: string;
  /** Payment method ID (defaults to "TEST_IDS.paymentMethod") */
  paymentMethodId?: string;
  /** Where to attach payment method: "subscription" (default) | "customer" | "list" */
  paymentMethodLocation?: "subscription" | "customer" | "list";
  /** Custom payment method data */
  customPaymentMethod?: {
    id?: string;
    brand?: string;
    last4?: string;
    expMonth?: number;
    expYear?: number;
  };
  /** If true, payment method will be an expanded object instead of string ID (defaults to false) */
  expandedPaymentMethod?: boolean;
  /** Current billing meter usage (defaults to "0" for zero usage) */
  meterBalance?: string;
}

/**
 * Creates a test subscription scenario with customer and optional payment method.
 *
 * This is the foundational fixture for subscription testing. It mocks:
 * - A Stripe customer (customers.retrieve)
 * - An active subscription on the specified plan (subscriptions.list)
 * - Optional payment method (paymentMethods.retrieve)
 *
 * @param params - Configuration parameters for the subscription fixture
 * @returns MockPayments layer ready to use in Effect.provide
 *
 * @example
 * ```ts
 * it.effect("tests pro subscription", () => {
 *   const mockLayer = TestSubscriptionFixture({
 *     plan: "pro",
 *     hasPaymentMethod: true,
 *     stripeCustomerId: "cus_123",
 *   });
 *
 *   return Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const result = yield* payments.customers.subscriptions.get("cus_123");
 *
 *     expect(result.currentPlan).toBe("pro");
 *   }).pipe(Effect.provide(mockLayer));
 * });
 * ```
 */
export function TestSubscriptionFixture(
  params: TestSubscriptionFixtureParams = {},
): Layer.Layer<Payments> {
  const {
    plan = "free",
    status = "active",
    hasPaymentMethod = false,
    stripeCustomerId = TEST_IDS.customer,
    subscriptionId = TEST_IDS.subscription,
    paymentMethodId = TEST_IDS.paymentMethod,
    paymentMethodLocation = "subscription",
    customPaymentMethod,
    expandedPaymentMethod = false,
  } = params;

  const { now, periodEnd } = getTestPeriodTimes();

  // Determine price ID from plan
  const priceId = getPriceIdForPlan(plan);

  // Determine payment method attachment based on location
  const pmId = customPaymentMethod?.id ?? paymentMethodId;
  const attachToSubscription =
    hasPaymentMethod && paymentMethodLocation === "subscription";
  const attachToCustomer =
    hasPaymentMethod && paymentMethodLocation === "customer";
  const attachToList = hasPaymentMethod && paymentMethodLocation === "list";

  // Build customer mock
  const customerData = createTestCustomer({
    id: stripeCustomerId,
    paymentMethodId: pmId,
    includePaymentMethod: attachToCustomer,
  });

  // Build subscription mock
  const subscriptionData = {
    id: subscriptionId,
    object: "subscription" as const,
    status,
    current_period_end: periodEnd,
    current_period_start: now,
    ...(attachToSubscription && {
      default_payment_method: expandedPaymentMethod
        ? { id: pmId, object: "payment_method" as const }
        : pmId,
    }),
    ...(attachToList && {
      default_payment_method: null,
    }),
    items: {
      data: [
        {
          id: TEST_IDS.subscriptionItem,
          price: { id: priceId },
        },
      ],
    },
  };

  // Build payment method mock (if needed)
  const paymentMethodData = hasPaymentMethod
    ? createTestPaymentMethod(pmId, {
        brand: customPaymentMethod?.brand,
        last4: customPaymentMethod?.last4,
        exp_month: customPaymentMethod?.expMonth,
        exp_year: customPaymentMethod?.expYear,
      })
    : undefined;

  // Create MockPayments layer
  let mockBuilder = new MockPayments().customers
    .retrieve(() => Effect.succeed(customerData))
    .subscriptions.list(() =>
      Effect.succeed(createListResponse([subscriptionData])),
    );

  // Add payment method mocks based on location
  if (hasPaymentMethod && paymentMethodData) {
    if (attachToList) {
      // For "list" location, mock both list and retrieve
      mockBuilder = mockBuilder.paymentMethods
        .list(() =>
          Effect.succeed({
            object: "list" as const,
            data: [
              {
                id: pmId,
                object: "payment_method" as const,
                type: "card" as const,
              },
            ],
            has_more: false,
          }),
        )
        .paymentMethods.retrieve(() => Effect.succeed(paymentMethodData));
    } else {
      // For "subscription" and "customer" locations, only mock retrieve
      mockBuilder = mockBuilder.paymentMethods.retrieve(() =>
        Effect.succeed(paymentMethodData),
      );
    }
  }

  return mockBuilder.build();
}

/**
 * Creates a test fixture with real database access for testing methods that
 * require both database operations and Stripe mocking.
 *
 * Unlike TestSubscriptionFixture which provides MockDrizzleORMLayer, this
 * fixture provides TestDrizzleORM (real database), allowing tests to perform
 * actual database operations (like inserting organizations).
 *
 * Use this when testing code paths that need to:
 * - Insert/query real test data in the database
 * - Mock Stripe API calls
 *
 * @param params - Subscription fixture parameters
 * @param dbLayer - Database layer to use (typically TestDrizzleORM from @/tests/db)
 * @returns Layer providing Payments and DrizzleORM
 *
 * @example
 * ```ts
 * import { TestDrizzleORM } from "@/tests/db";
 *
 * it.effect("gets plan for organization", () =>
 *   Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const db = yield* DrizzleORM;
 *
 *     const [org] = yield* db.insert(organizations).values({...}).returning();
 *     const plan = yield* payments.customers.subscriptions.getPlan(org.id);
 *
 *     expect(plan).toBe("pro");
 *   }).pipe(
 *     Effect.provide(
 *       TestSubscriptionWithRealDatabaseFixture({ plan: "pro" }, TestDrizzleORM)
 *     )
 *   )
 * );
 * ```
 */
export function TestSubscriptionWithRealDatabaseFixture(
  params: TestSubscriptionFixtureParams = {},
  dbLayer: Layer.Layer<DrizzleORM | SqlClient.SqlClient>,
): Layer.Layer<Payments | DrizzleORM | SqlClient.SqlClient> {
  const {
    plan = "free",
    status = "active",
    hasPaymentMethod = false,
    stripeCustomerId = TEST_IDS.customer,
    subscriptionId = TEST_IDS.subscription,
    paymentMethodId = TEST_IDS.paymentMethod,
    paymentMethodLocation = "subscription",
    customPaymentMethod,
    expandedPaymentMethod = false,
    meterBalance = "0",
  } = params;

  const { now, periodEnd } = getTestPeriodTimes();

  // Determine price ID from plan
  const priceId = getPriceIdForPlan(plan);

  // Determine payment method attachment based on location
  const pmId = customPaymentMethod?.id ?? paymentMethodId;
  const attachToSubscription =
    hasPaymentMethod && paymentMethodLocation === "subscription";
  const attachToCustomer =
    hasPaymentMethod && paymentMethodLocation === "customer";
  const attachToList = hasPaymentMethod && paymentMethodLocation === "list";

  // Build customer mock
  const customerData = createTestCustomer({
    id: stripeCustomerId,
    paymentMethodId: pmId,
    includePaymentMethod: attachToCustomer,
  });

  // Build subscription mock
  const subscriptionData = {
    id: subscriptionId,
    object: "subscription" as const,
    status,
    current_period_end: periodEnd,
    current_period_start: now,
    ...(attachToSubscription && {
      default_payment_method: expandedPaymentMethod
        ? { id: pmId, object: "payment_method" as const }
        : pmId,
    }),
    ...(attachToList && {
      default_payment_method: null,
    }),
    items: {
      data: [
        {
          id: TEST_IDS.subscriptionItem,
          price: { id: priceId },
        },
      ],
    },
  };

  // Build payment method mock (if needed)
  const paymentMethodData = hasPaymentMethod
    ? createTestPaymentMethod(pmId, {
        brand: customPaymentMethod?.brand,
        last4: customPaymentMethod?.last4,
        exp_month: customPaymentMethod?.expMonth,
        exp_year: customPaymentMethod?.expYear,
      })
    : undefined;

  // Create MockPayments layer with Stripe mocks
  let mockBuilder = new MockPayments().customers
    .retrieve(() => Effect.succeed(customerData))
    .subscriptions.list(() =>
      Effect.succeed(createListResponse([subscriptionData])),
    );

  // Add payment method mocks based on location
  if (hasPaymentMethod && paymentMethodData) {
    if (attachToList) {
      // For "list" location, mock both list and retrieve
      mockBuilder = mockBuilder.paymentMethods
        .list(() =>
          Effect.succeed({
            object: "list" as const,
            data: [
              {
                id: pmId,
                object: "payment_method" as const,
                type: "card" as const,
              },
            ],
            has_more: false,
          }),
        )
        .paymentMethods.retrieve(() => Effect.succeed(paymentMethodData));
    } else {
      // For "subscription" and "customer" locations, only mock retrieve
      mockBuilder = mockBuilder.paymentMethods.retrieve(() =>
        Effect.succeed(paymentMethodData),
      );
    }
  } else {
    // No payment method - mock empty list
    mockBuilder = mockBuilder.paymentMethods.list(() =>
      Effect.succeed(createListResponse([])),
    );
  }

  // Add billing meters mock for usage tracking
  mockBuilder = mockBuilder.billing.meters.listEventSummaries(() =>
    Effect.succeed({
      object: "list" as const,
      data: [{ aggregated_value: meterBalance }],
      has_more: false,
    }),
  );

  return Layer.merge(
    Payments.Default.pipe(
      Layer.provide(mockBuilder.buildStripe()),
      Layer.provide(dbLayer),
    ),
    dbLayer,
  );
}

/**
 * Creates a test fixture that provides only Payments mocks, WITHOUT its own database layer.
 *
 * Use this with `it.rollback` when you need:
 * - Stripe API mocking
 * - Real database operations with transaction rollback
 *
 * Unlike TestSubscriptionWithRealDatabaseFixture, this fixture does NOT provide
 * its own database layer. It relies on the outer context (provided by `it.rollback`)
 * to supply DrizzleORM and SqlClient. This ensures that the database connection used
 * by your test is the SAME one wrapped by the rollback transaction.
 *
 * @param params - Subscription fixture parameters
 * @returns Layer providing only Payments (requires DrizzleORM from outer context)
 *
 * @example
 * ```ts
 * // The correct way to use it.rollback with database + Stripe mocking:
 * it.rollback("test with db rollback", () =>
 *   Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const db = yield* DrizzleORM;
 *
 *     // Database operations will be rolled back after test
 *     const [org] = yield* db.insert(organizations).values({...}).returning();
 *     const plan = yield* payments.customers.subscriptions.getPlan(org.id);
 *
 *     expect(plan).toBe("pro");
 *   }).pipe(
 *     Effect.provide(TestPaymentsMockFixture({ plan: "pro" }))
 *   )
 * );
 * ```
 */
export function TestPaymentsMockFixture(
  params: TestSubscriptionFixtureParams = {},
): Layer.Layer<Payments, never, DrizzleORM | SqlClient.SqlClient> {
  const {
    plan = "free",
    status = "active",
    hasPaymentMethod = false,
    stripeCustomerId = TEST_IDS.customer,
    subscriptionId = TEST_IDS.subscription,
    paymentMethodId = TEST_IDS.paymentMethod,
    paymentMethodLocation = "subscription",
    customPaymentMethod,
    expandedPaymentMethod = false,
    meterBalance = "0",
  } = params;

  const { now, periodEnd } = getTestPeriodTimes();

  // Determine price ID from plan
  const priceId = getPriceIdForPlan(plan);

  // Determine payment method attachment based on location
  const pmId = customPaymentMethod?.id ?? paymentMethodId;
  const attachToSubscription =
    hasPaymentMethod && paymentMethodLocation === "subscription";
  const attachToCustomer =
    hasPaymentMethod && paymentMethodLocation === "customer";
  const attachToList = hasPaymentMethod && paymentMethodLocation === "list";

  // Build customer mock
  const customerData = createTestCustomer({
    id: stripeCustomerId,
    paymentMethodId: pmId,
    includePaymentMethod: attachToCustomer,
  });

  // Build subscription mock
  const subscriptionData = {
    id: subscriptionId,
    object: "subscription" as const,
    status,
    current_period_end: periodEnd,
    current_period_start: now,
    ...(attachToSubscription && {
      default_payment_method: expandedPaymentMethod
        ? { id: pmId, object: "payment_method" as const }
        : pmId,
    }),
    ...(attachToList && {
      default_payment_method: null,
    }),
    items: {
      data: [
        {
          id: TEST_IDS.subscriptionItem,
          price: { id: priceId },
        },
      ],
    },
  };

  // Build payment method mock (if needed)
  const paymentMethodData = hasPaymentMethod
    ? createTestPaymentMethod(pmId, {
        brand: customPaymentMethod?.brand,
        last4: customPaymentMethod?.last4,
        exp_month: customPaymentMethod?.expMonth,
        exp_year: customPaymentMethod?.expYear,
      })
    : undefined;

  // Create MockPayments layer with Stripe mocks
  let mockBuilder = new MockPayments().customers
    .retrieve(() => Effect.succeed(customerData))
    .subscriptions.list(() =>
      Effect.succeed(createListResponse([subscriptionData])),
    );

  // Add payment method mocks based on location
  if (hasPaymentMethod && paymentMethodData) {
    if (attachToList) {
      // For "list" location, mock both list and retrieve
      mockBuilder = mockBuilder.paymentMethods
        .list(() =>
          Effect.succeed({
            object: "list" as const,
            data: [
              {
                id: pmId,
                object: "payment_method" as const,
                type: "card" as const,
              },
            ],
            has_more: false,
          }),
        )
        .paymentMethods.retrieve(() => Effect.succeed(paymentMethodData));
    } else {
      // For "subscription" and "customer" locations, only mock retrieve
      mockBuilder = mockBuilder.paymentMethods.retrieve(() =>
        Effect.succeed(paymentMethodData),
      );
    }
  } else {
    // No payment method - mock empty list
    mockBuilder = mockBuilder.paymentMethods.list(() =>
      Effect.succeed(createListResponse([])),
    );
  }

  // Add billing meters mock for usage tracking
  mockBuilder = mockBuilder.billing.meters.listEventSummaries(() =>
    Effect.succeed({
      object: "list" as const,
      data: [{ aggregated_value: meterBalance }],
      has_more: false,
    }),
  );

  // Return Payments layer that requires DrizzleORM from outer context
  // (does NOT provide its own database layer - relies on it.rollback wrapper)
  return Payments.Default.pipe(Layer.provide(mockBuilder.buildStripe()));
}

/**
 * Parameters for TestErrorScenarioFixture.
 */
export interface TestErrorScenarioFixtureParams {
  /** Type of error to simulate */
  errorType:
    | "customerNotFound"
    | "subscriptionNotFound"
    | "stripeFailed"
    | "noActiveSubscription"
    | "missingConfig";
  /** Stripe customer ID (defaults to "cus_test_error") */
  stripeCustomerId?: string;
  /** Custom error message (optional) */
  errorMessage?: string;
}

/**
 * Creates a test scenario for error handling.
 *
 * This fixture mocks various error scenarios for testing error handling paths.
 *
 * @param params - Configuration parameters for the error scenario
 * @returns MockPayments layer with error mocks
 *
 * @example
 * ```ts
 * it.effect("handles customer not found", () => {
 *   const mockLayer = TestErrorScenarioFixture({
 *     errorType: "customerNotFound",
 *     stripeCustomerId: "cus_404",
 *   });
 *
 *   return Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const result = yield* payments.customers.subscriptions.get("cus_404");
 *
 *     expect(Effect.isFailure(result)).toBe(true);
 *   }).pipe(Effect.provide(mockLayer));
 * });
 * ```
 */
export function TestErrorScenarioFixture(
  params: TestErrorScenarioFixtureParams,
): Layer.Layer<Payments> {
  const {
    errorType,
    stripeCustomerId = "cus_test_error",
    errorMessage,
  } = params;

  let mockBuilder = new MockPayments();

  switch (errorType) {
    case "customerNotFound":
      mockBuilder = mockBuilder.customers.retrieve(() =>
        Effect.fail(
          new Error(errorMessage || "No such customer: " + stripeCustomerId),
        ),
      );
      break;

    case "subscriptionNotFound":
      mockBuilder = mockBuilder.customers
        .retrieve(() =>
          Effect.succeed(createTestCustomer({ id: stripeCustomerId })),
        )
        .subscriptions.list(() =>
          Effect.fail(
            new Error(errorMessage || "Failed to list subscriptions"),
          ),
        );
      break;

    case "noActiveSubscription":
      mockBuilder = mockBuilder.customers
        .retrieve(() =>
          Effect.succeed(createTestCustomer({ id: stripeCustomerId })),
        )
        .subscriptions.list(() =>
          Effect.succeed({
            object: "list" as const,
            data: [], // No active subscriptions
            has_more: false,
          }),
        );
      break;

    case "stripeFailed":
      mockBuilder = mockBuilder.customers.retrieve(() =>
        Effect.fail(
          new Error(errorMessage || "Stripe API error: Connection timed out"),
        ),
      );
      break;

    case "missingConfig":
      mockBuilder = mockBuilder.customers
        .retrieve(() =>
          Effect.succeed(createTestCustomer({ id: stripeCustomerId })),
        )
        .subscriptions.list(() =>
          Effect.succeed({
            object: "list" as const,
            data: [
              {
                id: "sub_123",
                object: "subscription" as const,
                customer: stripeCustomerId,
                status: "active" as const,
                items: {
                  object: "list" as const,
                  data: [
                    {
                      id: "si_1",
                      object: "subscription_item" as const,
                      price: {
                        id: "price_cloud_free_mock",
                        object: "price" as const,
                        active: true,
                        currency: "usd",
                        unit_amount: 0,
                        recurring: {
                          interval: "month" as const,
                          interval_count: 1,
                        },
                        product: "prod_1",
                        type: "recurring" as const,
                      },
                      subscription: "sub_123",
                    },
                  ],
                },
                current_period_end: getTestTimestamp(),
              },
            ],
            has_more: false,
          }),
        )
        .config({
          apiKey: "sk_test_mock",
          routerPriceId: "price_test",
          routerMeterId: "meter_test",
          // Missing cloud price IDs to trigger config error
          cloudSpansPriceId: "price_cloud_spans_mock",
          cloudSpansMeterId: "meter_cloud_spans_mock",
        });
      break;
  }

  return mockBuilder.build();
}

/**
 * Parameters for TestSubscriptionWithScheduleFixture.
 */
export interface TestSubscriptionWithScheduleFixtureParams extends TestSubscriptionFixtureParams {
  /** Target plan for the scheduled change */
  targetPlan: PlanTier;
  /** Schedule ID (defaults to "sched_test_123") */
  scheduleId?: string;
  /** Schedule status (defaults to "active") */
  scheduleStatus?: "active" | "canceled" | "completed";
  /** Effective date for the schedule in seconds (defaults to 30 days from now) */
  effectiveDate?: number;
  /** Use expanded price object instead of string ID (defaults to false) */
  useExpandedPriceObject?: boolean;
  /** Include non-plan items (e.g., spans meter) in schedule (defaults to true) */
  includeNonPlanItems?: boolean;
  /** Set to true to test schedule with empty items in next phase (defaults to false) */
  emptyNextPhase?: boolean;
}

/**
 * Creates a subscription with a scheduled plan change (upgrade/downgrade).
 *
 * This fixture extends TestSubscriptionFixture by adding a subscription schedule.
 * Useful for testing upgrade/downgrade scenarios with scheduled changes.
 *
 * @param params - Configuration parameters including base subscription and schedule params
 * @returns MockPayments layer with subscription schedule mocks
 *
 * @example
 * ```ts
 * it.effect("tests scheduled downgrade", () => {
 *   const mockLayer = TestSubscriptionWithScheduleFixture({
 *     plan: "pro",
 *     targetPlan: "free",
 *     stripeCustomerId: "cus_123",
 *   });
 *
 *   return Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const result = yield* payments.customers.subscriptions.get("cus_123");
 *
 *     expect(result.scheduledChange).toBeDefined();
 *     expect(result.scheduledChange?.targetPlan).toBe("free");
 *   }).pipe(Effect.provide(mockLayer));
 * });
 * ```
 */
export function TestSubscriptionWithScheduleFixture(
  params: TestSubscriptionWithScheduleFixtureParams,
): Layer.Layer<Payments> {
  const {
    targetPlan,
    scheduleId = "sched_test_123",
    scheduleStatus = "active",
    effectiveDate = getTestTimestamp() + TIME_CONSTANTS.BILLING_PERIOD_SECONDS,
    plan = "free",
    status = "active",
    hasPaymentMethod = false,
    stripeCustomerId = TEST_IDS.customer,
    subscriptionId = TEST_IDS.subscription,
    paymentMethodId = TEST_IDS.paymentMethod,
    paymentMethodLocation = "subscription",
    customPaymentMethod,
    useExpandedPriceObject = false,
    includeNonPlanItems = true,
    emptyNextPhase = false,
  } = params;

  const { now, periodEnd } = getTestPeriodTimes();

  // Determine price IDs
  const currentPriceId = getPriceIdForPlan(plan);
  const targetPriceId = getPriceIdForPlan(targetPlan);

  // Determine payment method attachment based on location
  const pmId = customPaymentMethod?.id ?? paymentMethodId;
  const attachToSubscription =
    hasPaymentMethod && paymentMethodLocation === "subscription";
  const attachToCustomer =
    hasPaymentMethod && paymentMethodLocation === "customer";
  const attachToList = hasPaymentMethod && paymentMethodLocation === "list";

  // Build customer mock
  const customerData = createTestCustomer({
    id: stripeCustomerId,
    paymentMethodId: pmId,
    includePaymentMethod: attachToCustomer,
  });

  // Build subscription mock
  const subscriptionData = {
    id: subscriptionId,
    object: "subscription" as const,
    status,
    current_period_end: periodEnd,
    current_period_start: now,
    ...(attachToSubscription && {
      default_payment_method: pmId,
    }),
    ...(attachToList && {
      default_payment_method: null,
    }),
    items: {
      data: [
        {
          id: TEST_IDS.subscriptionItem,
          price: { id: currentPriceId },
        },
      ],
    },
  };

  // Build payment method mock (if needed)
  const paymentMethodData = hasPaymentMethod
    ? createTestPaymentMethod(pmId, {
        brand: customPaymentMethod?.brand,
        last4: customPaymentMethod?.last4,
        exp_month: customPaymentMethod?.expMonth,
        exp_year: customPaymentMethod?.expYear,
      })
    : undefined;

  // Build price items for schedule phases
  const buildPhaseItem = (priceId: string) => {
    if (useExpandedPriceObject) {
      return {
        price: {
          id: priceId,
          object: "price" as const,
          active: true,
          currency: "usd",
          unit_amount: priceId.includes("team")
            ? 20000
            : priceId.includes("pro")
              ? 10000
              : 0,
        },
      };
    }
    return { price: priceId };
  };

  // Build schedule phase items
  const currentPhaseItems = [buildPhaseItem(currentPriceId)];
  const targetPhaseItems = emptyNextPhase
    ? [] // Empty items for testing edge case
    : includeNonPlanItems
      ? [
          { price: "price_cloud_spans_mock" }, // Include spans meter
          buildPhaseItem(targetPriceId),
        ]
      : [buildPhaseItem(targetPriceId)];

  // Build subscription schedule mock
  const scheduleData = {
    id: scheduleId,
    object: "subscription_schedule" as const,
    status: scheduleStatus,
    customer: stripeCustomerId,
    subscription: subscriptionId,
    phases: emptyNextPhase
      ? [
          {
            start_date: now,
            end_date: effectiveDate,
            items: [], // Single phase with no items (edge case)
          },
        ]
      : [
          {
            start_date: now,
            items: currentPhaseItems,
          },
          {
            start_date: effectiveDate,
            items: targetPhaseItems,
          },
        ],
  };

  // Create MockPayments layer
  let mockBuilder = new MockPayments().customers
    .retrieve(() => Effect.succeed(customerData))
    .subscriptions.list(() =>
      Effect.succeed(createListResponse([subscriptionData])),
    )
    .subscriptionSchedules.list(() =>
      Effect.succeed({
        object: "list" as const,
        data: scheduleStatus === "active" ? [scheduleData] : [],
        has_more: false,
      }),
    );

  // Add payment method mocks based on location
  if (hasPaymentMethod && paymentMethodData) {
    if (attachToList) {
      // For "list" location, mock both list and retrieve
      mockBuilder = mockBuilder.paymentMethods
        .list(() =>
          Effect.succeed({
            object: "list" as const,
            data: [
              {
                id: pmId,
                object: "payment_method" as const,
                type: "card" as const,
              },
            ],
            has_more: false,
          }),
        )
        .paymentMethods.retrieve(() => Effect.succeed(paymentMethodData));
    } else {
      // For "subscription" and "customer" locations, only mock retrieve
      mockBuilder = mockBuilder.paymentMethods.retrieve(() =>
        Effect.succeed(paymentMethodData),
      );
    }
  }

  return mockBuilder.build();
}
/**
 * Parameters for TestPaymentIntentScenarioFixture.
 */
export interface TestPaymentIntentScenarioFixtureParams extends TestSubscriptionFixtureParams {
  /** Target plan for the upgrade */
  targetPlan: PlanTier;
  /** Whether this upgrade requires payment (defaults to true) */
  requiresPayment?: boolean;
  /** Invoice ID (defaults to "TEST_IDS.invoice") */
  invoiceId?: string;
  /** Payment intent ID (defaults to "TEST_IDS.paymentIntent") */
  paymentIntentId?: string;
  /** Payment intent client secret (defaults to "pi_client_secret_mock") */
  clientSecret?: string;
  /** Payment intent status (defaults to "requires_payment_method") */
  paymentIntentStatus?: string;
}

/**
 * Creates a subscription upgrade scenario with payment intent.
 *
 * This fixture mocks an upgrade flow that requires payment, including:
 * - Retrieving the current subscription
 * - Updating the subscription to a new plan
 * - Creating a payment intent for the prorated charge
 *
 * @param params - Configuration parameters including subscription and payment intent details
 * @returns MockPayments layer with payment intent mocks
 *
 * @example
 * ```ts
 * it.effect("tests upgrade requiring payment", () => {
 *   const mockLayer = TestPaymentIntentScenarioFixture({
 *     plan: "free",
 *     targetPlan: "pro",
 *     stripeCustomerId: "cus_123",
 *   });
 *
 *   return Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const result = yield* payments.customers.subscriptions.update({
 *       stripeCustomerId: "cus_123",
 *       targetPlan: "pro",
 *     });
 *
 *     expect(result.requiresPayment).toBe(true);
 *     expect(result.clientSecret).toBeDefined();
 *   }).pipe(Effect.provide(mockLayer));
 * });
 * ```
 */
export function TestPaymentIntentScenarioFixture(
  params: TestPaymentIntentScenarioFixtureParams,
): Layer.Layer<Payments> {
  const {
    targetPlan,
    requiresPayment = true,
    invoiceId = TEST_IDS.invoice,
    paymentIntentId = TEST_IDS.paymentIntent,
    clientSecret = "pi_client_secret_mock",
    paymentIntentStatus = "requires_payment_method",
    plan = "free",
    status = "active",
    hasPaymentMethod = false,
    stripeCustomerId = TEST_IDS.customer,
    subscriptionId = TEST_IDS.subscription,
    paymentMethodId = TEST_IDS.paymentMethod,
  } = params;

  const { now, periodEnd } = getTestPeriodTimes();

  // Determine price IDs
  const currentPriceId = getPriceIdForPlan(plan);
  const targetPriceId = getPriceIdForPlan(targetPlan);

  // Build customer mock
  const customerData = createTestCustomer({
    id: stripeCustomerId,
    paymentMethodId: hasPaymentMethod ? paymentMethodId : null,
    includePaymentMethod: hasPaymentMethod,
  });

  // Build current subscription mock
  const subscriptionData = createTestSubscription({
    id: subscriptionId,
    status,
    priceId: currentPriceId,
    paymentMethodId: hasPaymentMethod ? paymentMethodId : null,
    periodEnd,
    periodStart: now,
  });

  // Build updated subscription mock (after update)
  const updatedSubscriptionData = {
    ...subscriptionData,
    items: {
      data: [
        {
          id: TEST_IDS.subscriptionItem,
          price: { id: targetPriceId },
        },
      ],
    },
    ...(requiresPayment && {
      latest_invoice: {
        id: invoiceId,
        payment_intent: {
          id: paymentIntentId,
          status: paymentIntentStatus,
          client_secret: clientSecret,
        },
      },
    }),
  };

  // Build payment method mock (if needed)
  const paymentMethodData = hasPaymentMethod
    ? createTestPaymentMethod(paymentMethodId)
    : undefined;

  // Create MockPayments layer
  let mockBuilder = new MockPayments().customers
    .retrieve(() => Effect.succeed(customerData))
    .subscriptions.list(() =>
      Effect.succeed(createListResponse([subscriptionData])),
    )
    .subscriptions.retrieve(() => Effect.succeed(subscriptionData))
    .subscriptions.update(() => Effect.succeed(updatedSubscriptionData));

  if (hasPaymentMethod && paymentMethodData) {
    mockBuilder = mockBuilder.paymentMethods.retrieve(() =>
      Effect.succeed(paymentMethodData),
    );
  }

  return mockBuilder.build();
}

/**
 * Creates a subscription upgrade scenario with payment intent handling.
 *
 * This fixture mocks an upgrade flow including payment method and payment intent states.
 * Useful for testing upgrade scenarios that require payment confirmation.
 *
 * @param params - Configuration for upgrade scenario
 * @returns MockPayments layer with upgrade and payment intent mocks
 *
 * @example
 * ```ts
 * it.effect("upgrades without payment method", () =>
 *   Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const result = yield* payments.customers.subscriptions.update({
 *       stripeCustomerId: "cus_123",
 *       targetPlan: "pro",
 *     });
 *
 *     expect(result.requiresPaymentMethod).toBe(true);
 *   }).pipe(
 *     Effect.provide(
 *       TestUpgradeWithPaymentIntentFixture({
 *         currentPlan: "free",
 *         targetPlan: "pro",
 *         requiresPayment: true,
 *         hasPaymentMethod: false,
 *       })
 *     )
 *   )
 * );
 * ```
 */
export function TestUpgradeWithPaymentIntentFixture(params: {
  /** Current subscription plan */
  currentPlan: PlanTier;
  /** Target plan for upgrade */
  targetPlan: PlanTier;
  /** Stripe customer ID (defaults to "cus_test_123") */
  stripeCustomerId?: string;
  /** Whether upgrade requires payment (defaults to false) */
  requiresPayment?: boolean;
  /** Payment intent status if requires payment */
  paymentIntentStatus?:
    | "requires_payment_method"
    | "succeeded"
    | "requires_confirmation"
    | null;
  /** Whether customer has payment method (defaults to false) */
  hasPaymentMethod?: boolean;
  /** Optional override for subscription items returned by retrieve (for edge case testing) */
  retrieveSubscriptionItems?: Array<{
    id: string;
    priceId: string;
    quantity?: number;
  }>;
  /** Optional custom price ID for current plan (for testing unknown prices) */
  customCurrentPriceId?: string;
  /** Client secret for payment intent (defaults to "pi_client_secret_mock") */
  clientSecret?: string;
}): Layer.Layer<Payments> {
  const {
    currentPlan,
    targetPlan,
    stripeCustomerId = TEST_IDS.customer,
    requiresPayment = false,
    paymentIntentStatus = "requires_payment_method",
    hasPaymentMethod = false,
    retrieveSubscriptionItems,
    customCurrentPriceId,
    clientSecret = "pi_client_secret_mock",
  } = params;

  const { now, periodEnd } = getTestPeriodTimes();

  const currentPriceId = customCurrentPriceId ?? getPriceIdForPlan(currentPlan);
  const targetPriceId = getPriceIdForPlan(targetPlan);

  const customerData = createTestCustomer({
    id: stripeCustomerId,
    paymentMethodId: hasPaymentMethod ? TEST_IDS.paymentMethod : null,
    includePaymentMethod: hasPaymentMethod,
  });

  const subscriptionData = createTestSubscription({
    id: TEST_IDS.subscription,
    status: "active",
    priceId: currentPriceId,
    paymentMethodId: hasPaymentMethod ? TEST_IDS.paymentMethod : null,
    periodEnd,
    periodStart: now,
  });

  // If retrieveSubscriptionItems is provided, create a different subscription data for retrieve()
  const retrieveSubscriptionData = retrieveSubscriptionItems
    ? {
        id: TEST_IDS.subscription,
        object: "subscription" as const,
        status: "active" as const,
        current_period_end: periodEnd,
        current_period_start: now,
        ...(hasPaymentMethod && {
          default_payment_method: TEST_IDS.paymentMethod,
        }),
        items: {
          data: retrieveSubscriptionItems.map((item) => ({
            id: item.id,
            price: { id: item.priceId },
            ...(item.quantity !== undefined && { quantity: item.quantity }),
          })),
        },
      }
    : subscriptionData;

  const paymentMethodData = hasPaymentMethod
    ? createTestPaymentMethod()
    : undefined;

  const updatedSubscriptionData = {
    id: TEST_IDS.subscription,
    object: "subscription" as const,
    status: "active" as const,
    current_period_end: periodEnd,
    current_period_start: now,
    items: {
      data: [
        {
          id: TEST_IDS.subscriptionItem,
          price: { id: targetPriceId },
        },
      ],
    },
    ...(requiresPayment && {
      latest_invoice: {
        id: TEST_IDS.invoice,
        object: "invoice" as const,
        amount_due: 10000,
        payment_intent:
          paymentIntentStatus === null
            ? null
            : {
                id: TEST_IDS.paymentIntent,
                object: "payment_intent" as const,
                status: paymentIntentStatus,
                client_secret: clientSecret,
              },
      },
    }),
  };

  let mockBuilder = new MockPayments().customers
    .retrieve(() => Effect.succeed(customerData))
    .subscriptions.list(() =>
      Effect.succeed({
        object: "list" as const,
        data: [subscriptionData],
        has_more: false,
      }),
    )
    .subscriptions.retrieve(() => Effect.succeed(retrieveSubscriptionData))
    .subscriptions.update(() => Effect.succeed(updatedSubscriptionData));

  if (hasPaymentMethod && paymentMethodData) {
    mockBuilder = mockBuilder.paymentMethods.retrieve(() =>
      Effect.succeed(paymentMethodData),
    );
  }

  return mockBuilder.build();
}

/**
 * Creates a subscription change preview scenario.
 *
 * This fixture mocks the preview flow for plan changes including proration calculations.
 * Useful for testing preview upgrade/downgrade endpoints.
 *
 * @param params - Configuration for preview scenario
 * @returns MockPayments layer with preview mocks
 *
 * @example
 * ```ts
 * it.effect("previews downgrade to free", () =>
 *   Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const result = yield* payments.customers.subscriptions.previewChange({
 *       stripeCustomerId: "cus_123",
 *       targetPlan: "free",
 *     });
 *
 *     expect(result.proratedAmountInCents).toBe(-50);
 *     expect(result.recurringAmountInCents).toBe(0);
 *   }).pipe(
 *     Effect.provide(
 *       TestPreviewChangeFixture({
 *         currentPlan: "pro",
 *         targetPlan: "free",
 *         proratedAmountInCents: -5000,
 *         recurringAmountInCents: 0,
 *       })
 *     )
 *   )
 * );
 * ```
 */
export function TestPreviewChangeFixture(params: {
  /** Current subscription plan */
  currentPlan: PlanTier;
  /** Target plan for change */
  targetPlan: PlanTier;
  /** Stripe customer ID (defaults to "cus_test_123") */
  stripeCustomerId?: string;
  /** Prorated amount for immediate charge/credit (in cents, as Stripe uses) */
  proratedAmountInCents?: number;
  /** Recurring amount for next period (in cents, as Stripe uses) */
  recurringAmountInCents?: number;
  /** Whether customer has payment method (defaults to false) */
  hasPaymentMethod?: boolean;
  /** Optional override for subscription items returned by retrieve (for edge case testing) */
  retrieveSubscriptionItems?: Array<{
    id: string;
    priceId: string;
    quantity?: number;
  }>;
  /** Optional custom price ID for current plan (for testing unknown prices) */
  customCurrentPriceId?: string;
  /** Optional override for upcoming invoice total (use null to test price retrieval fallback) */
  upcomingInvoiceTotalOverride?: number | null;
}): Layer.Layer<Payments> {
  const {
    currentPlan,
    targetPlan,
    stripeCustomerId = TEST_IDS.customer,
    proratedAmountInCents = 0,
    recurringAmountInCents = 10000,
    hasPaymentMethod = false,
    retrieveSubscriptionItems,
    customCurrentPriceId,
    upcomingInvoiceTotalOverride,
  } = params;

  const { now, periodEnd } = getTestPeriodTimes();

  const currentPriceId = customCurrentPriceId ?? getPriceIdForPlan(currentPlan);

  const customerData = createTestCustomer({
    id: stripeCustomerId,
    paymentMethodId: hasPaymentMethod ? TEST_IDS.paymentMethod : null,
    includePaymentMethod: hasPaymentMethod,
  });

  const subscriptionData = createTestSubscription({
    id: TEST_IDS.subscription,
    status: "active",
    priceId: currentPriceId,
    paymentMethodId: hasPaymentMethod ? TEST_IDS.paymentMethod : null,
    periodEnd,
    periodStart: now,
  });

  // If retrieveSubscriptionItems is provided, create a different subscription data for retrieve()
  const retrieveSubscriptionData = retrieveSubscriptionItems
    ? {
        id: TEST_IDS.subscription,
        object: "subscription" as const,
        status: "active" as const,
        current_period_end: periodEnd,
        current_period_start: now,
        ...(hasPaymentMethod && {
          default_payment_method: TEST_IDS.paymentMethod,
        }),
        items: {
          data: retrieveSubscriptionItems.map((item) => ({
            id: item.id,
            price: { id: item.priceId },
            ...(item.quantity !== undefined && { quantity: item.quantity }),
          })),
        },
      }
    : subscriptionData;

  const upcomingInvoiceData = {
    id: "in_upcoming",
    object: "invoice" as const,
    amount_due: proratedAmountInCents,
    total:
      upcomingInvoiceTotalOverride !== undefined
        ? upcomingInvoiceTotalOverride
        : recurringAmountInCents,
    period_end: periodEnd,
    lines: {
      data: [
        {
          id: "il_proration",
          amount: proratedAmountInCents,
          proration: true,
        },
        {
          id: "il_recurring",
          amount: recurringAmountInCents,
          proration: false,
        },
      ],
    },
  };

  const paymentMethodData = hasPaymentMethod
    ? createTestPaymentMethod()
    : undefined;

  // Determine target price for prices.retrieve mock
  const targetPriceId = getPriceIdForPlan(targetPlan);

  let mockBuilder = new MockPayments().customers
    .retrieve(() => Effect.succeed(customerData))
    .subscriptions.list(() =>
      Effect.succeed({
        object: "list" as const,
        data: [subscriptionData],
        has_more: false,
      }),
    )
    .subscriptions.retrieve(() => Effect.succeed(retrieveSubscriptionData))
    .invoices.retrieveUpcoming(() => Effect.succeed(upcomingInvoiceData))
    .prices.retrieve(() =>
      Effect.succeed({
        id: targetPriceId,
        object: "price" as const,
        unit_amount: recurringAmountInCents, // Use the recurring amount as the price
        currency: "usd",
      }),
    );

  if (hasPaymentMethod && paymentMethodData) {
    mockBuilder = mockBuilder.paymentMethods.retrieve(() =>
      Effect.succeed(paymentMethodData),
    );
  }

  return mockBuilder.build();
}

/**
 * Parameters for TestMultipleSubscriptionItemsFixture.
 */
export interface TestMultipleSubscriptionItemsFixtureParams {
  /** Stripe customer ID (defaults to "TEST_IDS.customer") */
  stripeCustomerId?: string;
  /** Subscription ID (defaults to "TEST_IDS.subscription") */
  subscriptionId?: string;
  /** Subscription status (defaults to "active") */
  status?: "active" | "canceled" | "past_due";
  /** Whether customer has a payment method (defaults to false) */
  hasPaymentMethod?: boolean;
  /** Payment method ID (defaults to "TEST_IDS.paymentMethod") */
  paymentMethodId?: string;
  /** Array of subscription items with custom price IDs */
  items: Array<{ id: string; priceId: string }>;
}

/**
 * Creates a subscription with multiple subscription items.
 *
 * This fixture is useful for testing edge cases where a subscription has
 * multiple items (e.g., plan + spans meter, or legacy price IDs).
 *
 * @param params - Configuration parameters with custom subscription items
 * @returns MockPayments layer with multiple subscription items
 *
 * @example
 * ```ts
 * it.effect("falls back to free for unknown price ID", () =>
 *   Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const result = yield* payments.customers.subscriptions.get("cus_123");
 *
 *     expect(result.currentPlan).toBe("free"); // Falls back when unknown ID found
 *   }).pipe(
 *     Effect.provide(
 *       TestMultipleSubscriptionItemsFixture({
 *         stripeCustomerId: "cus_123",
 *         subscriptionId: "sub_123",
 *         items: [
 *           { id: "si_123", priceId: "price_cloud_legacy_mock" },
 *           { id: "si_124", priceId: "price_cloud_free_mock" },
 *         ],
 *       }),
 *     ),
 *   ),
 * );
 * ```
 */
export function TestMultipleSubscriptionItemsFixture(
  params: TestMultipleSubscriptionItemsFixtureParams,
): Layer.Layer<Payments> {
  const {
    stripeCustomerId = TEST_IDS.customer,
    subscriptionId = TEST_IDS.subscription,
    status = "active",
    hasPaymentMethod = false,
    paymentMethodId = TEST_IDS.paymentMethod,
    items,
  } = params;

  const { now, periodEnd } = getTestPeriodTimes();

  // Build customer mock
  const customerData = createTestCustomer({
    id: stripeCustomerId,
    paymentMethodId: hasPaymentMethod ? paymentMethodId : null,
    includePaymentMethod: hasPaymentMethod,
  });

  // Build subscription mock with multiple items
  const subscriptionData = {
    id: subscriptionId,
    object: "subscription" as const,
    status,
    current_period_end: periodEnd,
    current_period_start: now,
    ...(hasPaymentMethod && {
      default_payment_method: paymentMethodId,
    }),
    items: {
      data: items.map((item) => ({
        id: item.id,
        price: { id: item.priceId },
      })),
    },
  };

  // Build payment method mock (if needed)
  const paymentMethodData = hasPaymentMethod
    ? createTestPaymentMethod(paymentMethodId)
    : undefined;

  // Create MockPayments layer
  let mockBuilder = new MockPayments().customers
    .retrieve(() => Effect.succeed(customerData))
    .subscriptions.list(() =>
      Effect.succeed(createListResponse([subscriptionData])),
    );

  if (hasPaymentMethod && paymentMethodData) {
    mockBuilder = mockBuilder.paymentMethods.retrieve(() =>
      Effect.succeed(paymentMethodData),
    );
  }

  return mockBuilder.build();
}

/**
 * Creates a subscription downgrade scenario with schedule handling.
 *
 * This fixture mocks the downgrade flow including schedule creation/update
 * and handles existing schedules that need to be released.
 *
 * @param params - Configuration for downgrade scenario
 * @returns MockPayments layer with downgrade and schedule mocks
 *
 * @example
 * ```ts
 * it.effect("releases existing schedule before downgrade", () => {
 *   let releaseWasCalled = false;
 *
 *   return Effect.gen(function* () {
 *     const payments = yield* Payments;
 *     const result = yield* payments.customers.subscriptions.update({
 *       stripeCustomerId: "cus_123",
 *       targetPlan: "free",
 *     });
 *
 *     expect(result.scheduledFor).toBeDefined();
 *     expect(releaseWasCalled).toBe(true);
 *   }).pipe(
 *     Effect.provide(
 *       TestDowngradeWithScheduleFixture({
 *         currentPlan: "pro",
 *         targetPlan: "free",
 *         stripeCustomerId: "cus_123",
 *         existingScheduleId: "sched_existing",
 *         onScheduleRelease: () => { releaseWasCalled = true; },
 *       })
 *     )
 *   );
 * });
 * ```
 */
export function TestDowngradeWithScheduleFixture(params: {
  /** Current subscription plan */
  currentPlan: PlanTier;
  /** Target plan for downgrade */
  targetPlan: PlanTier;
  /** Stripe customer ID (defaults to "cus_test_123") */
  stripeCustomerId?: string;
  /** Subscription ID (defaults to "TEST_IDS.subscription") */
  subscriptionId?: string;
  /** Existing schedule ID on subscription (if any) */
  existingScheduleId?: string;
  /** Whether existing schedule is expanded object (defaults to false) */
  existingScheduleAsObject?: boolean;
  /** New schedule ID after creation (defaults to "sub_sched_new") */
  newScheduleId?: string;
  /** Updated schedule ID (defaults to "sub_sched_updated") */
  updatedScheduleId?: string;
  /** Callback invoked when schedule is released */
  onScheduleRelease?: () => void;
  /** Additional subscription items (e.g., non-plan items like spans) */
  additionalItems?: Array<{ id: string; priceId: string; quantity?: number }>;
  /** If true, items will not have quantity field (defaults to false) */
  omitQuantity?: boolean;
}): Layer.Layer<Payments> {
  const {
    currentPlan,
    stripeCustomerId = TEST_IDS.customer,
    subscriptionId = TEST_IDS.subscription,
    existingScheduleId,
    existingScheduleAsObject = false,
    newScheduleId = "sub_sched_new",
    updatedScheduleId = "sub_sched_updated",
    onScheduleRelease,
    additionalItems = [],
    omitQuantity = false,
  } = params;

  const { now } = getTestPeriodTimes();

  const currentPriceId = getPriceIdForPlan(currentPlan);

  const customerData = createTestCustomer({
    id: stripeCustomerId,
    includePaymentMethod: false,
  });

  const planItem = {
    id: "si_1",
    object: "subscription_item" as const,
    price: {
      id: currentPriceId,
      object: "price" as const,
      active: true,
      currency: "usd",
      unit_amount: 1000,
      recurring: {
        interval: "month" as const,
        interval_count: 1,
      },
      product: "prod_1",
      type: "recurring" as const,
    },
    subscription: subscriptionId,
  };

  const additionalItemsData = additionalItems.map((item) => ({
    id: item.id,
    object: "subscription_item" as const,
    price: {
      id: item.priceId,
      object: "price" as const,
      active: true,
      currency: "usd",
      unit_amount: 1000,
      recurring: {
        interval: "month" as const,
        interval_count: 1,
      },
      product: "prod_1",
      type: "recurring" as const,
    },
    subscription: subscriptionId,
  }));

  const subscriptionData = {
    id: subscriptionId,
    object: "subscription" as const,
    customer: stripeCustomerId,
    status: "active" as const,
    items: {
      object: "list" as const,
      data: [planItem, ...additionalItemsData],
    },
    current_period_end: now,
    current_period_start: now - 86400,
  };

  // Subscription retrieve data with optional schedule reference
  const planItemWithQuantity = omitQuantity
    ? planItem
    : { ...planItem, quantity: 1 };
  const additionalItemsWithQuantity = additionalItems.map((item) => {
    const baseItem = {
      id: item.id,
      object: "subscription_item" as const,
      price: {
        id: item.priceId,
        object: "price" as const,
        active: true,
        currency: "usd",
        unit_amount: 1000,
        recurring: {
          interval: "month" as const,
          interval_count: 1,
        },
        product: "prod_1",
        type: "recurring" as const,
      },
      subscription: subscriptionId,
    };
    return omitQuantity
      ? baseItem
      : { ...baseItem, quantity: item.quantity ?? 1 };
  });

  const subscriptionRetrieveData = {
    ...subscriptionData,
    items: {
      object: "list" as const,
      data: [planItemWithQuantity, ...additionalItemsWithQuantity],
    },
    ...(existingScheduleId &&
      (existingScheduleAsObject
        ? {
            schedule: {
              id: existingScheduleId,
              object: "subscription_schedule" as const,
              status: "active" as const,
              customer: stripeCustomerId,
              subscription: subscriptionId,
            },
          }
        : { schedule: existingScheduleId })),
  };

  let mockBuilder = new MockPayments().customers
    .retrieve(() => Effect.succeed(customerData))
    .subscriptions.list(() =>
      Effect.succeed({
        object: "list" as const,
        data: [subscriptionData],
        has_more: false,
      }),
    )
    .subscriptions.retrieve(() => Effect.succeed(subscriptionRetrieveData))
    .subscriptionSchedules.create(() =>
      Effect.succeed({
        id: newScheduleId,
        object: "subscription_schedule" as const,
        status: "active" as const,
        customer: stripeCustomerId,
        subscription: subscriptionId,
      }),
    )
    .subscriptionSchedules.update(() =>
      Effect.succeed({
        id: updatedScheduleId,
        object: "subscription_schedule" as const,
        status: "active" as const,
        customer: stripeCustomerId,
        subscription: subscriptionId,
      }),
    );

  // Add schedule release mock if there's an existing schedule
  if (existingScheduleId) {
    mockBuilder = mockBuilder.subscriptionSchedules.release(
      (scheduleId: string) => {
        if (onScheduleRelease) onScheduleRelease();
        return Effect.succeed({
          id: scheduleId,
          object: "subscription" as const,
          customer: stripeCustomerId,
          status: "active" as const,
        });
      },
    );
  }

  return mockBuilder.build();
}

/**
 * Creates a fixture for testing cancelScheduledDowngrade scenarios.
 * Mocks subscription schedule list and optional release.
 *
 * Example usage:
 * ```typescript
 * TestCancelScheduleFixture({
 *   schedules: [{ id: "sched_123" }],
 *   onScheduleRelease: () => { releaseWasCalled = true; }
 * })
 * ```
 */
export function TestCancelScheduleFixture(params: {
  /** Schedules to return from list (empty array for "no schedules found" test) */
  schedules?: Array<{ id: string }>;
  /** Callback invoked when schedule is released */
  onScheduleRelease?: () => void;
}): Layer.Layer<Payments> {
  const { schedules = [], onScheduleRelease } = params;

  let mockBuilder = new MockPayments().subscriptionSchedules.list(() =>
    Effect.succeed({
      object: "list" as const,
      data: schedules.map((schedule) => ({
        id: schedule.id,
        object: "subscription_schedule" as const,
      })),
      has_more: false,
    }),
  );

  // Only add release mock if there are schedules
  if (schedules.length > 0) {
    mockBuilder = mockBuilder.subscriptionSchedules.release(() => {
      if (onScheduleRelease) onScheduleRelease();
      return Effect.succeed({
        id: "sub_123",
        object: "subscription" as const,
      });
    });
  }

  return mockBuilder.build();
}

/**
 * Creates a fixture for testing subscription cancellation scenarios.
 * Mocks subscription list with active and/or past_due subscriptions.
 *
 * Example usage:
 * ```typescript
 * TestCancelSubscriptionsFixture({
 *   subscriptions: [
 *     { id: "sub_123", status: "active" },
 *     { id: "sub_456", status: "past_due" }
 *   ]
 * })
 * ```
 */
export function TestCancelSubscriptionsFixture(params: {
  /** Subscriptions to return from list */
  subscriptions: Array<{ id: string; status: "active" | "past_due" }>;
  /** Callback invoked when subscription is cancelled */
  onSubscriptionCancel?: (subscriptionId: string) => void;
}): Layer.Layer<Payments> {
  const { subscriptions, onSubscriptionCancel } = params;

  let mockBuilder = new MockPayments().subscriptions.list(() =>
    Effect.succeed({
      object: "list" as const,
      data: subscriptions.map((sub) => ({
        id: sub.id,
        object: "subscription" as const,
        status: sub.status,
        customer: "cus_123",
        items: {
          object: "list" as const,
          data: [],
        },
        current_period_start: Date.now(),
        current_period_end: Date.now() + 30 * 24 * 60 * 60 * 1000,
        created: Date.now(),
        livemode: false,
      })),
      has_more: false,
    }),
  );

  // Add cancel mock for active subscriptions
  const activeSubscriptions = subscriptions.filter(
    (s) => s.status === "active",
  );
  if (activeSubscriptions.length > 0) {
    mockBuilder = mockBuilder.subscriptions.cancel((subscriptionId: string) => {
      if (onSubscriptionCancel) onSubscriptionCancel(subscriptionId);
      return Effect.succeed({
        id: subscriptionId,
        object: "subscription" as const,
        status: "canceled" as const,
      });
    });
  }

  return mockBuilder.build();
}
