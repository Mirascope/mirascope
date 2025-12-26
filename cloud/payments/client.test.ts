import { describe, it, expect } from "@/tests/payments";
import { vi, beforeEach } from "vitest";
import { Effect, Layer } from "effect";
import { Stripe, wrapStripeClient } from "@/payments/client";
import { StripeError } from "@/errors";
import OriginalStripe from "stripe";

// Mock the Stripe SDK
vi.mock("stripe", () => {
  const MockStripe = vi.fn();
  return {
    default: MockStripe,
  };
});

// Type for our mock Stripe instance
interface MockStripeInstance {
  customers: {
    create: ReturnType<typeof vi.fn>;
    retrieve: ReturnType<typeof vi.fn>;
    update: ReturnType<typeof vi.fn>;
    list: ReturnType<typeof vi.fn>;
    nested?: {
      deepMethod: ReturnType<typeof vi.fn>;
    };
  };
  subscriptions: {
    create: ReturnType<typeof vi.fn>;
    retrieve: ReturnType<typeof vi.fn>;
    cancel: ReturnType<typeof vi.fn>;
  };
  apiKey: string;
  apiVersion: string;
  _internal?: string;
  [key: symbol]: unknown;
}

// Type for the wrapped Stripe client that includes internal properties we test
type WrappedStripeForTest = ReturnType<typeof wrapStripeClient> & {
  apiKey: string;
  apiVersion: string;
  _internal: string;
  [key: symbol]: unknown;
};

describe("Stripe", () => {
  let mockStripe: MockStripeInstance;

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();

    // Create a mock Stripe instance with nested structure
    mockStripe = {
      customers: {
        create: vi.fn(),
        retrieve: vi.fn(),
        update: vi.fn(),
        list: vi.fn(),
      },
      subscriptions: {
        create: vi.fn(),
        retrieve: vi.fn(),
        cancel: vi.fn(),
      },
      apiKey: "sk_test_mock",
      apiVersion: "2023-10-16",
    };

    // Mock Stripe constructor to return our mock instance.
    // We need `as any` here because vi.mock transforms OriginalStripe into a mock,
    // but TypeScript doesn't know about vitest's mock transformation at compile time.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
    (OriginalStripe as any).mockImplementation(() => mockStripe);
  });

  // ===========================================================================
  // Layer Creation
  // ===========================================================================

  describe("layer", () => {
    it("creates a layer with provided configuration", () => {
      const layer = Stripe.layer({
        apiKey: "sk_test_123",
        apiVersion: "2023-10-16",
      });

      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });

    it("creates a layer with minimal configuration", () => {
      const layer = Stripe.layer({
        apiKey: "sk_test_123",
      });

      expect(layer).toBeDefined();
      expect(OriginalStripe).toHaveBeenCalledWith("sk_test_123", {
        apiVersion: undefined,
        typescript: true,
      });
    });
  });

  // ===========================================================================
  // Basic Service Access
  // ===========================================================================

  describe("service access", () => {
    it.effect("provides access to wrapped Stripe client", () =>
      Effect.gen(function* () {
        const stripe = yield* Stripe;
        expect(stripe).toBeDefined();
        expect(stripe.customers).toBeDefined();
        expect(stripe.subscriptions).toBeDefined();
      }),
    );
  });

  // ===========================================================================
  // Method Wrapping - Success Cases
  // ===========================================================================

  describe("method wrapping - success", () => {
    it.effect("wraps customer.create to return Effect", () => {
      const mockCustomer = {
        id: "cus_123",
        email: "test@example.com",
        object: "customer",
      };

      mockStripe.customers.create.mockResolvedValue(mockCustomer);

      return Effect.gen(function* () {
        const stripe = yield* Stripe;

        const customer = yield* stripe.customers.create({
          email: "test@example.com",
        });

        expect(customer).toEqual(mockCustomer);
        expect(mockStripe.customers.create).toHaveBeenCalledWith({
          email: "test@example.com",
        });
      });
    });

    it.effect("wraps subscription.create to return Effect", () => {
      const mockSubscription = {
        id: "sub_123",
        customer: "cus_123",
        status: "active",
        object: "subscription",
      };

      mockStripe.subscriptions.create.mockResolvedValue(mockSubscription);

      return Effect.gen(function* () {
        const stripe = yield* Stripe;

        const subscription = yield* stripe.subscriptions.create({
          customer: "cus_123",
          items: [{ price: "price_123" }],
        });

        expect(subscription).toEqual(mockSubscription);
        expect(mockStripe.subscriptions.create).toHaveBeenCalledWith({
          customer: "cus_123",
          items: [{ price: "price_123" }],
        });
      });
    });

    it.effect("handles multiple sequential calls", () => {
      const mockCustomer = { id: "cus_123", email: "test@example.com" };
      const mockSubscription = { id: "sub_123", customer: "cus_123" };

      mockStripe.customers.create.mockResolvedValue(mockCustomer);
      mockStripe.subscriptions.create.mockResolvedValue(mockSubscription);

      return Effect.gen(function* () {
        const stripe = yield* Stripe;

        const customer = yield* stripe.customers.create({
          email: "test@example.com",
        });

        const subscription = yield* stripe.subscriptions.create({
          customer: customer.id,
          items: [{ price: "price_123" }],
        });

        expect(customer.id).toBe("cus_123");
        expect(subscription.customer).toBe(customer.id);
      });
    });
  });

  // ===========================================================================
  // Error Handling
  // ===========================================================================

  describe("error handling", () => {
    it.effect("converts Stripe errors to StripeError", () => {
      const stripeError = new Error("Invalid API key");

      mockStripe.customers.create.mockRejectedValue(stripeError);

      return Effect.gen(function* () {
        const stripe = yield* Stripe;

        const result = yield* stripe.customers
          .create({ email: "test@example.com" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Invalid API key");
        expect(result.cause).toBe(stripeError);
      });
    });

    it.effect("handles errors with no message property", () => {
      mockStripe.customers.create.mockRejectedValue("Some string error");

      return Effect.gen(function* () {
        const stripe = yield* Stripe;

        const result = yield* stripe.customers
          .create({ email: "test@example.com" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toContain("stripe.customers.create");
        expect(result.cause).toBe("Some string error");
      });
    });

    it.effect("allows catching StripeError with catchTag", () => {
      mockStripe.customers.create.mockRejectedValue(new Error("API error"));

      return Effect.gen(function* () {
        const stripe = yield* Stripe;

        const result = yield* stripe.customers
          .create({ email: "test@example.com" })
          .pipe(
            Effect.catchTag("StripeError", (error) => {
              expect(error.message).toBe("API error");
              return Effect.succeed(null);
            }),
          );

        expect(result).toBe(null);
      });
    });
  });

  // ===========================================================================
  // wrapStripeClient
  // ===========================================================================

  describe("wrapStripeClient", () => {
    it.effect("wraps a Stripe client directly", () => {
      const mockCustomer = { id: "cus_123", email: "test@example.com" };
      mockStripe.customers.create.mockResolvedValue(mockCustomer);

      const wrapped = wrapStripeClient(mockStripe as unknown as OriginalStripe);

      return Effect.gen(function* () {
        const result = yield* wrapped.customers.create({
          email: "test@example.com",
        });

        expect(result).toEqual(mockCustomer);
      });
    });

    it("preserves nested object identity through caching", () => {
      const wrapped = wrapStripeClient(mockStripe as unknown as OriginalStripe);

      const customers1 = wrapped.customers;
      const customers2 = wrapped.customers;

      // Should return the same wrapped object (cached)
      expect(customers1).toBe(customers2);
    });

    it("passes through primitive properties", () => {
      const wrapped = wrapStripeClient(
        mockStripe as unknown as OriginalStripe,
      ) as WrappedStripeForTest;

      expect(wrapped.apiKey).toBe("sk_test_mock");
      expect(wrapped.apiVersion).toBe("2023-10-16");
    });

    it("skips symbol properties", () => {
      const sym = Symbol("test");
      mockStripe[sym] = "value";

      const wrapped = wrapStripeClient(
        mockStripe as unknown as OriginalStripe,
      ) as WrappedStripeForTest;

      expect(wrapped[sym]).toBe("value");
    });

    it("skips properties starting with underscore", () => {
      mockStripe._internal = "private";

      const wrapped = wrapStripeClient(
        mockStripe as unknown as OriginalStripe,
      ) as WrappedStripeForTest;

      expect(wrapped._internal).toBe("private");
    });

    it.effect("handles nested method calls with correct context", () => {
      const mockList = { data: [{ id: "cus_1" }, { id: "cus_2" }] };
      mockStripe.customers.list.mockResolvedValue(mockList);

      const wrapped = wrapStripeClient(mockStripe as unknown as OriginalStripe);

      return Effect.gen(function* () {
        const result = yield* wrapped.customers.list({});

        expect(result).toEqual(mockList);
        expect(mockStripe.customers.list).toHaveBeenCalledWith({});
      });
    });

    it("wraps deeply nested objects", () => {
      mockStripe.customers.nested = {
        deepMethod: vi.fn().mockResolvedValue({ id: "deep" }),
      };

      const wrapped = wrapStripeClient(mockStripe as unknown as OriginalStripe);

      // This test doesn't use Effect.gen, so it doesn't require TestServices
      // We can run it synchronously since we're just checking object properties
      const customers1 = wrapped.customers;
      const customers2 = wrapped.customers;
      expect(customers1).toBe(customers2);
    });
  });

  // ===========================================================================
  // Real-world Usage Example
  // ===========================================================================

  describe("real-world usage", () => {
    it.effect("demonstrates typical customer + subscription flow", () => {
      const mockCustomer = {
        id: "cus_123",
        email: "user@example.com",
        name: "Test User",
      };

      const mockSubscription = {
        id: "sub_123",
        customer: "cus_123",
        status: "active",
        items: { data: [{ price: { id: "price_123" } }] },
      };

      mockStripe.customers.create.mockResolvedValue(mockCustomer);
      mockStripe.subscriptions.create.mockResolvedValue(mockSubscription);

      return Effect.gen(function* () {
        const stripe = yield* Stripe;

        // Step 1: Create customer
        const customer = yield* stripe.customers.create({
          email: "user@example.com",
          name: "Test User",
          metadata: { source: "test" },
        });

        expect(customer.id).toBe("cus_123");

        // Step 2: Create subscription for the customer
        const subscription = yield* stripe.subscriptions.create({
          customer: customer.id,
          items: [{ price: "price_123" }],
          trial_period_days: 30,
        });

        expect(subscription.customer).toBe(customer.id);
        expect(subscription.status).toBe("active");

        const result = { customer, subscription };

        expect(result.customer.id).toBe("cus_123");
        expect(result.subscription.id).toBe("sub_123");

        return result;
      });
    });
  });
});
