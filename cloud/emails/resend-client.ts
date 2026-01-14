/**
 * @fileoverview Effect-native Resend service.
 *
 * This module provides the `Resend` service which wraps the Resend SDK with Effect,
 * enabling `yield*` semantics for Resend API calls and proper typed error handling.
 *
 * ## Architecture
 *
 * ```
 * ResendAPI (raw SDK from npm)
 *   └── wrapResendClient (Proxy wrapper)
 *         └── Resend (Effect-native service)
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { Resend } from "@/email";
 *
 * const sendWelcomeEmail = (to: string) =>
 *   Effect.gen(function* () {
 *     const resend = yield* Resend;
 *
 *     const result = yield* resend.emails.send({
 *       from: "noreply@example.com",
 *       to,
 *       subject: "Welcome!",
 *       html: "<p>Welcome to our platform!</p>"
 *     });
 *
 *     return result;
 *   });
 * ```
 *
 * ## Error Handling
 *
 * All Resend operations that fail will be converted to `ResendError`:
 *
 * ```ts
 * const result = yield* resend.emails.send({ ... }).pipe(
 *   Effect.catchTag("ResendError", (error) => {
 *     console.error("Resend failed:", error.message);
 *     return Effect.succeed(null);
 *   })
 * );
 * ```
 */

import { Effect, Layer, Context } from "effect";
import { Resend as ResendAPI } from "resend";
import { ResendError, ConfigError } from "@/errors";

/**
 * Resend service configuration options.
 */
export interface ResendConfig {
  /** Resend API key (re_...) */
  apiKey: string;
}

/**
 * Validates that all required Resend config fields are non-empty strings.
 *
 * Accepts a partial config (e.g., from process.env) and validates that all
 * required fields are present and non-empty. Returns a fully-typed ResendConfig
 * if validation passes.
 *
 * @param config - Partial Resend configuration to validate
 * @returns Effect that succeeds with validated ResendConfig or fails with ConfigError
 */
function validateResendConfig(
  config: Partial<ResendConfig>,
): Effect.Effect<ResendConfig, ConfigError> {
  const errors: string[] = [];

  // Validate API key is present and non-empty
  if (!config.apiKey?.trim()) errors.push("apiKey");

  if (errors.length > 0) {
    return Effect.fail(
      new ConfigError({
        message: `Invalid Resend configuration. Missing or empty fields: ${errors.join(", ")}`,
      }),
    );
  }

  // All required fields are present and non-empty, safe to cast to ResendConfig
  return Effect.succeed(config as ResendConfig);
}

/**
 * Type helper to convert a single Resend resource method to an Effect-returning method.
 * Preserves all overloads by mapping each signature individually.
 */
type EffectifyMethod<T> = T extends {
  (...args: infer A1): Promise<infer R1>;
  (...args: infer A2): Promise<infer R2>;
  (...args: infer A3): Promise<infer R3>;
  (...args: infer A4): Promise<infer R4>;
}
  ? {
      (...args: A1): Effect.Effect<R1, ResendError>;
      (...args: A2): Effect.Effect<R2, ResendError>;
      (...args: A3): Effect.Effect<R3, ResendError>;
      (...args: A4): Effect.Effect<R4, ResendError>;
    }
  : T extends {
        (...args: infer A1): Promise<infer R1>;
        (...args: infer A2): Promise<infer R2>;
        (...args: infer A3): Promise<infer R3>;
      }
    ? {
        (...args: A1): Effect.Effect<R1, ResendError>;
        (...args: A2): Effect.Effect<R2, ResendError>;
        (...args: A3): Effect.Effect<R3, ResendError>;
      }
    : T extends {
          (...args: infer A1): Promise<infer R1>;
          (...args: infer A2): Promise<infer R2>;
        }
      ? {
          (...args: A1): Effect.Effect<R1, ResendError>;
          (...args: A2): Effect.Effect<R2, ResendError>;
        }
      : T extends (...args: infer A) => Promise<infer R>
        ? (...args: A) => Effect.Effect<R, ResendError>
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
 * Wraps a Resend client to return Effects instead of Promises.
 *
 * Uses a Proxy to intercept method calls and property access:
 * - Async methods are wrapped with `Effect.tryPromise` to convert Promise → Effect
 * - Resend's Response<T> format is unwrapped to return just T or throw ResendError
 * - Nested objects (emails, domains, etc.) are recursively wrapped
 * - Wrapped objects are cached to preserve identity
 * - Resend errors are converted to `ResendError` with proper error context
 *
 * @param resend - The raw Resend SDK client
 * @returns A proxied version where all async methods return Effects
 *
 * @example
 * ```ts
 * const originalResend = new ResendAPI("re_...");
 * const resend = wrapResendClient(originalResend);
 *
 * // Now methods return Effects with unwrapped data
 * const emailEffect = resend.emails.send({ ... });
 * const email = yield* emailEffect; // Returns just the data, not Response<T>
 * ```
 */
export const wrapResendClient = (
  resend: ResendAPI,
): WrapWithEffect<ResendAPI> => {
  // Cache wrapped objects to preserve identity across multiple accesses
  const wrappedObjects = new WeakMap<object, object>();

  /**
   * Recursively wraps an object, converting async methods to Effect-returning functions.
   *
   * We use `unknown` for runtime values and assert the final type is correct via the
   * return type of wrapResendClient. The Proxy handles dynamic property access at runtime,
   * while TypeScript provides static type safety at compile time.
   */
  const wrapObject = (obj: unknown, path: string = "resend"): unknown => {
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
              try: async () => {
                // We know value is a function, call it with the target as context
                const result = (value as (...args: unknown[]) => unknown).apply(
                  target,
                  args,
                );
                // Resend methods return Promises of Response<T>
                const response = (await result) as
                  | { data: unknown; error: null }
                  | { data: null; error: { message: string; name: string } };

                // Check if response follows the Resend Response<T> format
                if (
                  response &&
                  typeof response === "object" &&
                  "data" in response &&
                  "error" in response
                ) {
                  // If there's an error in the response, throw it
                  if (response.error !== null) {
                    throw new Error(response.error.message);
                  }
                  // Return just the data, unwrapping Response<T> → T
                  return response.data;
                }

                // For methods that don't return Response<T> (like verify), return as-is
                return response;
              },
              catch: (error) => {
                // Extract error message from Resend error or use generic message
                let message = `Resend API call failed: ${fullPath}`;
                if (error && typeof error === "object" && "message" in error) {
                  message = String(error.message);
                }

                return new ResendError({
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

  return wrapObject(resend) as WrapWithEffect<ResendAPI>;
};

/**
 * Effect-native Resend service.
 *
 * This service provides a Resend SDK instance that returns Effects instead of
 * Promises, enabling seamless integration with Effect's ecosystem including:
 * - `yield*` syntax for Resend API calls
 * - Typed error channels (all errors become ResendError)
 * - Automatic resource management
 * - Composability with other Effect-based services
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const resend = yield* Resend;
 *
 *   // Send an email
 *   const email = yield* resend.emails.send({
 *     from: "noreply@example.com",
 *     to: "user@example.com",
 *     subject: "Welcome!",
 *     html: "<p>Welcome to our platform!</p>"
 *   });
 *
 *   return email;
 * });
 *
 * // Provide the Resend layer
 * program.pipe(
 *   Effect.provide(Resend.layer({ apiKey: "re_..." }))
 * );
 * ```
 */
/**
 * Resend service interface that includes both the wrapped client and configuration.
 */
export interface ResendClient extends WrapWithEffect<ResendAPI> {
  /** Resend configuration */
  config: ResendConfig;
}

export class Resend extends Context.Tag("Resend")<Resend, ResendClient>() {
  /**
   * Creates a Layer that provides the Resend service.
   *
   * This layer initializes the Resend SDK with the provided configuration
   * and wraps it to return Effects instead of Promises. The config is validated
   * to ensure all required fields are present and non-empty.
   *
   * @param config - Partial Resend configuration (e.g., from process.env)
   * @returns A Layer providing Resend, or fails with ConfigError if validation fails
   *
   * @example
   * ```ts
   * const ResendLive = Resend.layer({
   *   apiKey: process.env.RESEND_API_KEY,
   * });
   *
   * program.pipe(Effect.provide(ResendLive));
   * ```
   */
  static layer = (config: Partial<ResendConfig>) => {
    return Layer.effect(
      Resend,
      Effect.gen(function* () {
        // Validate config first
        const validatedConfig = yield* validateResendConfig(config);

        // Create Resend client with validated config
        const originalResend = new ResendAPI(validatedConfig.apiKey);

        const wrappedResend = wrapResendClient(originalResend);

        return {
          ...wrappedResend,
          config: validatedConfig,
        };
      }),
    );
  };
}
