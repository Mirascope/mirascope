/**
 * @fileoverview Effect-native Stripe service.
 *
 * This module provides the `Stripe` service which wraps the Stripe SDK with Effect,
 * enabling `yield*` semantics for Stripe API calls and proper typed error handling.
 *
 * ## Architecture
 *
 * ```
 * OriginalStripe (raw SDK from npm)
 *   └── wrapStripeClient (Proxy wrapper)
 *         └── Stripe (Effect-native service)
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { Stripe } from "@/payments";
 *
 * const createCustomer = (email: string) =>
 *   Effect.gen(function* () {
 *     const stripe = yield* Stripe;
 *
 *     const customer = yield* stripe.customers.create({
 *       email,
 *       metadata: { source: "app" }
 *     });
 *
 *     return customer;
 *   });
 * ```
 *
 * ## Error Handling
 *
 * All Stripe operations that fail will be converted to `StripeError`:
 *
 * ```ts
 * const result = yield* stripe.customers.create({ email: "..." }).pipe(
 *   Effect.catchTag("StripeError", (error) => {
 *     console.error("Stripe failed:", error.message);
 *     return Effect.succeed(null);
 *   })
 * );
 * ```
 */

import { Effect, Layer, Context } from "effect";
import OriginalStripe from "stripe";
import { StripeError, ConfigError } from "@/errors";

/**
 * Stripe service configuration options.
 */
export interface StripeConfig {
  /** Stripe secret API key (sk_test_... or sk_live_...) */
  apiKey: string;
  /** Stripe price ID for usage-based Router credits (metered billing) */
  routerPriceId: string;
  /** Stripe meter ID for tracking Router usage-based credits */
  routerMeterId: string;
  /** Stripe price ID for Cloud Free tier subscription */
  cloudFreePriceId: string;
  /** Stripe price ID for Cloud Pro tier subscription */
  cloudProPriceId: string;
  /** Stripe price ID for Cloud Team tier subscription */
  cloudTeamPriceId: string;
  /** Stripe price ID for Cloud Spans usage-based billing */
  cloudSpansPriceId: string;
  /** Stripe meter ID for tracking Cloud Spans usage */
  cloudSpansMeterId: string;
  /** Optional API version (defaults to Stripe SDK default) */
  apiVersion?: string;
}

/**
 * Type helper to convert a single Stripe resource method to an Effect-returning method.
 * Preserves all overloads by mapping each signature individually.
 */
type EffectifyMethod<T> = T extends {
  (...args: infer A1): Promise<infer R1>;
  (...args: infer A2): Promise<infer R2>;
  (...args: infer A3): Promise<infer R3>;
  (...args: infer A4): Promise<infer R4>;
}
  ? {
      (...args: A1): Effect.Effect<R1, StripeError>;
      (...args: A2): Effect.Effect<R2, StripeError>;
      (...args: A3): Effect.Effect<R3, StripeError>;
      (...args: A4): Effect.Effect<R4, StripeError>;
    }
  : T extends {
        (...args: infer A1): Promise<infer R1>;
        (...args: infer A2): Promise<infer R2>;
        (...args: infer A3): Promise<infer R3>;
      }
    ? {
        (...args: A1): Effect.Effect<R1, StripeError>;
        (...args: A2): Effect.Effect<R2, StripeError>;
        (...args: A3): Effect.Effect<R3, StripeError>;
      }
    : T extends {
          (...args: infer A1): Promise<infer R1>;
          (...args: infer A2): Promise<infer R2>;
        }
      ? {
          (...args: A1): Effect.Effect<R1, StripeError>;
          (...args: A2): Effect.Effect<R2, StripeError>;
        }
      : T extends (...args: infer A) => Promise<infer R>
        ? (...args: A) => Effect.Effect<R, StripeError>
        : T;

/**
 * Type helper to recursively convert Promise-returning methods to Effect-returning methods.
 *
 * This preserves:
 * - All method overloads (up to 4 overloads per method)
 * - Nested resource objects
 * - Primitive properties
 */
type WrapWithEffect<T> =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  T extends (...args: any[]) => any
    ? EffectifyMethod<T>
    : T extends object
      ? { [K in keyof T]: WrapWithEffect<T[K]> }
      : T;

/**
 * Validates that all required Stripe config fields are non-empty strings.
 *
 * Accepts a partial config (e.g., from process.env) and validates that all
 * required fields are present and non-empty. Returns a fully-typed StripeConfig
 * if validation passes.
 *
 * @param config - Partial Stripe configuration to validate
 * @returns Effect that succeeds with validated StripeConfig or fails with ConfigError
 */
function validateStripeConfig(
  config: Partial<StripeConfig>,
): Effect.Effect<StripeConfig, ConfigError> {
  const errors: string[] = [];

  // Validate all required fields are present and non-empty
  if (!config.apiKey?.trim()) errors.push("apiKey");
  if (!config.routerPriceId?.trim()) errors.push("routerPriceId");
  if (!config.routerMeterId?.trim()) errors.push("routerMeterId");
  if (!config.cloudFreePriceId?.trim()) errors.push("cloudFreePriceId");
  if (!config.cloudProPriceId?.trim()) errors.push("cloudProPriceId");
  if (!config.cloudTeamPriceId?.trim()) errors.push("cloudTeamPriceId");
  if (!config.cloudSpansPriceId?.trim()) errors.push("cloudSpansPriceId");
  if (!config.cloudSpansMeterId?.trim()) errors.push("cloudSpansMeterId");

  if (errors.length > 0) {
    return Effect.fail(
      new ConfigError({
        message: `Invalid Stripe configuration. Missing or empty fields: ${errors.join(", ")}`,
      }),
    );
  }

  // All required fields are present and non-empty, safe to cast to StripeConfig
  return Effect.succeed(config as StripeConfig);
}

/**
 * Wraps a Stripe client to return Effects instead of Promises.
 *
 * Uses a Proxy to intercept method calls and property access:
 * - Async methods are wrapped with `Effect.tryPromise` to convert Promise → Effect
 * - Nested objects (customers, subscriptions, etc.) are recursively wrapped
 * - Wrapped objects are cached to preserve identity
 * - Stripe errors are converted to `StripeError` with proper error context
 *
 * @param stripe - The raw Stripe SDK client
 * @returns A proxied version where all async methods return Effects
 *
 * @example
 * ```ts
 * const originalStripe = new OriginalStripe("sk_test_...");
 * const stripe = wrapStripeClient(originalStripe);
 *
 * // Now methods return Effects
 * const customerEffect = stripe.customers.create({ email: "..." });
 * const customer = yield* customerEffect;
 * ```
 */
export const wrapStripeClient = (
  stripe: OriginalStripe,
): WrapWithEffect<OriginalStripe> => {
  // Cache wrapped objects to preserve identity across multiple accesses
  const wrappedObjects = new WeakMap<object, object>();

  /**
   * Recursively wraps an object, converting async methods to Effect-returning functions.
   *
   * We use `unknown` for runtime values and assert the final type is correct via the
   * return type of wrapStripeClient. The Proxy handles dynamic property access at runtime,
   * while TypeScript provides static type safety at compile time.
   */
  const wrapObject = (obj: unknown, path: string = "stripe"): unknown => {
    return new Proxy(obj as object, {
      get(target, prop) {
        // Access the property value - type is unknown at runtime
        const value: unknown = (target as Record<string | symbol, unknown>)[
          prop
        ];

        // Skip symbols and internal properties
        if (typeof prop === "symbol" || prop.startsWith("_")) {
          return value;
        }

        // Wrap async functions to return Effects
        if (typeof value === "function") {
          return (...args: unknown[]) => {
            const fullPath = `${path}.${String(prop)}`;

            return Effect.tryPromise({
              try: () => {
                // We know value is a function, call it with the target as context
                const result = (value as (...args: unknown[]) => unknown).apply(
                  target,
                  args,
                );
                // Stripe methods return Promises
                return result as Promise<unknown>;
              },
              catch: (error) => {
                // Extract error message from Stripe error or use generic message
                let message = `Stripe API call failed: ${fullPath}`;
                if (error && typeof error === "object" && "message" in error) {
                  message = String(error.message);
                }

                return new StripeError({
                  message,
                  cause: error,
                });
              },
            });
          };
        }

        // Recursively wrap nested objects (with caching to preserve identity)
        if (
          value !== null &&
          typeof value === "object" &&
          !Array.isArray(value)
        ) {
          const cached = wrappedObjects.get(value);
          if (cached) {
            return cached;
          }
          const wrapped = wrapObject(value, `${path}.${String(prop)}`);
          wrappedObjects.set(value, wrapped as object);
          return wrapped;
        }

        // Primitives and other values pass through unchanged
        return value;
      },
    });
  };

  return wrapObject(stripe) as WrapWithEffect<OriginalStripe>;
};

/**
 * Effect-native Stripe service.
 *
 * This service provides a Stripe SDK instance that returns Effects instead of
 * Promises, enabling seamless integration with Effect's ecosystem including:
 * - `yield*` syntax for Stripe API calls
 * - Typed error channels (all errors become StripeError)
 * - Automatic resource management
 * - Composability with other Effect-based services
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const stripe = yield* Stripe;
 *
 *   // Create a customer
 *   const customer = yield* stripe.customers.create({
 *     email: "user@example.com",
 *     name: "Test User"
 *   });
 *
 *   // Create a subscription
 *   const subscription = yield* stripe.subscriptions.create({
 *     customer: customer.id,
 *     items: [{ price: "price_123" }]
 *   });
 *
 *   return { customer, subscription };
 * });
 *
 * // Provide the Stripe layer
 * program.pipe(
 *   Effect.provide(Stripe.layer({ apiKey: "sk_test_..." }))
 * );
 * ```
 */
/**
 * Stripe service interface that includes both the wrapped client and configuration.
 */
export interface StripeClient extends WrapWithEffect<OriginalStripe> {
  /** Stripe configuration (includes routerPriceId for metered billing) */
  config: StripeConfig;
}

export class Stripe extends Context.Tag("Stripe")<Stripe, StripeClient>() {
  /**
   * Creates a Layer that provides the Stripe service.
   *
   * This layer initializes the Stripe SDK with the provided configuration
   * and wraps it to return Effects instead of Promises. The config is validated
   * to ensure all required fields are present and non-empty.
   *
   * @param config - Partial Stripe configuration (e.g., from process.env)
   * @returns A Layer providing Stripe, or fails with ConfigError if validation fails
   *
   * @example
   * ```ts
   * const StripeLive = Stripe.layer({
   *   apiKey: process.env.STRIPE_SECRET_KEY,
   *   routerPriceId: process.env.STRIPE_ROUTER_PRICE_ID,
   *   routerMeterId: process.env.STRIPE_ROUTER_METER_ID,
   *   cloudFreePriceId: process.env.STRIPE_CLOUD_FREE_PRICE_ID,
   *   cloudProPriceId: process.env.STRIPE_CLOUD_PRO_PRICE_ID,
   *   cloudTeamPriceId: process.env.STRIPE_CLOUD_TEAM_PRICE_ID,
   *   cloudSpansPriceId: process.env.STRIPE_CLOUD_SPANS_PRICE_ID,
   *   cloudSpansMeterId: process.env.STRIPE_CLOUD_SPANS_METER_ID,
   * });
   *
   * program.pipe(Effect.provide(StripeLive));
   * ```
   */
  static layer = (config: Partial<StripeConfig>) => {
    return Layer.effect(
      Stripe,
      Effect.gen(function* () {
        // Validate config first
        const validatedConfig = yield* validateStripeConfig(config);

        // Create Stripe client with validated config
        const originalStripe = new OriginalStripe(validatedConfig.apiKey, {
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-explicit-any
          apiVersion: validatedConfig.apiVersion as any,
          typescript: true,
        });

        const wrappedStripe = wrapStripeClient(originalStripe);

        return {
          ...wrappedStripe,
          config: validatedConfig,
        };
      }),
    );
  };
}
