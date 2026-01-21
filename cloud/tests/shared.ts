import { Effect, Option } from "effect";
import { it as vitestIt } from "@effect/vitest";
import { SqlClient } from "@effect/sql";

type EffectTestFn<TServices> = <A, E, R extends TServices = TServices>(
  name: string,
  fn: () => Effect.Effect<A, E, R>,
  timeout?: number,
) => void;

type CustomIt<TServices> = typeof vitestIt & {
  effect: {
    <A, E, R extends TServices = TServices>(
      name: string,
      fn: () => Effect.Effect<A, E, R>,
      timeout?: number,
    ): void;
    skip: EffectTestFn<TServices>;
    only: EffectTestFn<TServices>;
    fails: EffectTestFn<TServices>;
    skipIf: (condition: unknown) => EffectTestFn<TServices>;
    runIf: (condition: unknown) => EffectTestFn<TServices>;
  };
};

/**
 * Factory for creating a custom `it` export with automatic layer provision.
 *
 * Takes a wrapper function that handles layer provision/transaction wrapping,
 * returns a Proxy-based `it` that works as both a regular test function and
 * provides `.effect` for Effect-based tests.
 *
 * @param wrapEffectTest - Function that wraps vitest's effect test with layer provision
 * @returns Custom `it` export with proper typing for the provided services
 *
 * @example
 * ```ts
 * const wrapEffectTest = (original: any) => (name: any, fn: any, timeout?: any) =>
 *   original(name, () => fn().pipe(Effect.provide(MyLayer)), timeout);
 *
 * export const it = createCustomIt<MyServices>(wrapEffectTest);
 * ```
 */
export function createCustomIt<TServices>(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  wrapEffectTest: (original: any) => EffectTestFn<TServices>,
): CustomIt<TServices> {
  return new Proxy(vitestIt, {
    get(target, prop) {
      if (prop === "effect") {
        return Object.assign(wrapEffectTest(vitestIt.effect), {
          skip: wrapEffectTest(vitestIt.effect.skip),
          only: wrapEffectTest(vitestIt.effect.only),
          fails: wrapEffectTest(vitestIt.effect.fails),
          skipIf: (condition: unknown) =>
            wrapEffectTest(vitestIt.effect.skipIf(condition)),
          runIf: (condition: unknown) =>
            wrapEffectTest(vitestIt.effect.runIf(condition)),
        });
      }
      // eslint-disable-next-line @typescript-eslint/no-unsafe-return
      return Reflect.get(target, prop);
    },
  }) as CustomIt<TServices>;
}

/**
 * Ensures a value is wrapped in an Effect.
 * If the value is already an Effect, returns it as-is.
 * Otherwise, wraps it with Effect.succeed.
 */
export const ensureEffect = <A, E = never, R = never>(
  value: A | Effect.Effect<A, E, R>,
): Effect.Effect<A, E, R> =>
  Effect.isEffect(value)
    ? value
    : (Effect.succeed(value) as Effect.Effect<A, E, R>);

// =============================================================================
// Rollback transaction wrapper
// =============================================================================

/**
 * Sentinel error used to force transaction rollback in tests.
 */
export class TestRollbackError {
  readonly _tag = "TestRollbackError";
}

/**
 * Wraps a test effect in a transaction that always rolls back.
 *
 * This ensures database changes made during tests are automatically cleaned up,
 * preventing data pollution across tests. If SqlClient is not available
 * (e.g., mock tests), the effect runs without transaction wrapping.
 *
 * @example
 * ```ts
 * const test = Effect.gen(function* () {
 *   const db = yield* Database;
 *   yield* db.users.create({ ... }); // Will be rolled back
 * }).pipe(withRollback);
 * ```
 */
export const withRollback = <A, E, R>(
  effect: Effect.Effect<A, E, R>,
): Effect.Effect<A, E, R> =>
  Effect.gen(function* () {
    // Check if SqlClient is available (won't be for mock tests)
    const sqlOption = yield* Effect.serviceOption(SqlClient.SqlClient);

    if (Option.isNone(sqlOption)) {
      // No SqlClient available (mock test), run without transaction
      return yield* effect;
    }

    const sql = sqlOption.value;
    let result: A;

    yield* sql
      .withTransaction(
        Effect.gen(function* () {
          // Run the test effect and capture its result
          result = yield* effect;
          // Always fail to trigger rollback
          return yield* Effect.fail(new TestRollbackError());
        }),
      )
      .pipe(
        // Catch the rollback error - this is expected
        Effect.catchIf(
          (e): e is TestRollbackError => e instanceof TestRollbackError,
          () => Effect.void,
        ),
      );

    // @ts-expect-error - result is assigned before we get here
    return result;
  }) as Effect.Effect<A, E, R>;
