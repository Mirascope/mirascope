import { Effect } from "effect";
import { it as vitestIt, describe, expect } from "@effect/vitest";
import { Stripe } from "@/payments/client";

// Re-export describe and expect for convenience
export { describe, expect };

/**
 * Creates a Stripe layer for tests.
 * This is a lazy function so it's created after vi.mock() has been set up.
 */
const getTestStripe = () =>
  Stripe.layer({
    apiKey: "sk_test_123",
  });

/**
 * Services that are automatically provided to all `it.effect` tests.
 */
export type TestServices = Stripe;

/**
 * Type for effect test functions that accept TestServices as dependencies.
 */
type EffectTestFn = <A, E>(
  name: string,
  fn: () => Effect.Effect<A, E, TestServices>,
  timeout?: number,
) => void;

/**
 * Type for vitest's effect test function (from @effect/vitest).
 */
type VitestEffectTestFn = <A, E, R>(
  name: string,
  fn: () => Effect.Effect<A, E, R>,
  timeout?: number,
) => void;

/**
 * Wraps a test function to automatically provide TestStripe layer.
 */
const wrapEffectTest =
  (original: VitestEffectTestFn): EffectTestFn =>
  (name, fn, timeout) =>
    original(name, () => fn().pipe(Effect.provide(getTestStripe())), timeout);

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
export const it = Object.assign(
  // Base callable function for regular tests
  ((name: string, fn: () => void) => vitestIt(name, fn)) as typeof vitestIt,
  {
    // Spread all properties from vitestIt (skip, only, etc.)
    ...vitestIt,
    // Override effect with our wrapped version
    effect: Object.assign(
      wrapEffectTest(vitestIt.effect as VitestEffectTestFn),
      {
        skip: wrapEffectTest(vitestIt.effect.skip as VitestEffectTestFn),
        only: wrapEffectTest(vitestIt.effect.only as VitestEffectTestFn),
        fails: wrapEffectTest(vitestIt.effect.fails as VitestEffectTestFn),
        skipIf: (condition: unknown) =>
          wrapEffectTest(
            vitestIt.effect.skipIf(condition) as VitestEffectTestFn,
          ),
        runIf: (condition: unknown) =>
          wrapEffectTest(
            vitestIt.effect.runIf(condition) as VitestEffectTestFn,
          ),
      },
    ),
  },
);
