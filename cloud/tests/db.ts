import * as dotenv from "dotenv";
import { Effect, Layer } from "effect";
import { getDatabase, DatabaseService, type Database } from "@/db/services";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "@/db/schema";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";

dotenv.config({ path: ".env.local", override: true });

if (!process.env.TEST_DATABASE_URL) {
  throw new Error(
    "TEST_DATABASE_URL environment variable is required. Please set it in your .env file.",
  );
}

const TEST_DATABASE_URL: string = process.env.TEST_DATABASE_URL;

/**
 * A scoped Layer that provides a DatabaseService backed by a transaction that
 * automatically rolls back when the test completes. This ensures test isolation
 * without polluting the database.
 *
 * Usage with @effect/vitest:
 * ```ts
 * import { it } from "@effect/vitest";
 * import { Effect } from "effect";
 * import { DatabaseService } from "@/db/services";
 * import { TestDatabase } from "@/tests/db";
 *
 * it.effect("should do something", () =>
 *   Effect.gen(function* () {
 *     const db = yield* DatabaseService;
 *     // ... test code
 *   }).pipe(Effect.provide(TestDatabase))
 * );
 * ```
 */
export const TestDatabase: Layer.Layer<DatabaseService> = Layer.scoped(
  DatabaseService,
  Effect.gen(function* () {
    const sql = postgres(TEST_DATABASE_URL, {
      max: 5,
      fetch_types: false,
    });
    const db = drizzle(sql, { schema });

    // Create promise-based coordination for the transaction lifecycle
    let resolveReady!: (database: Database) => void;
    let resolveComplete!: () => void;

    const readyPromise = new Promise<Database>((resolve) => {
      resolveReady = resolve;
    });
    const completePromise = new Promise<void>((resolve) => {
      resolveComplete = resolve;
    });

    // Start the transaction - it will wait for completePromise before rolling back
    const transactionPromise = db
      .transaction(async (tx) => {
        const txDb = getDatabase(tx);
        resolveReady(txDb);
        // Wait for the test to complete
        await completePromise;
        // Always throw to trigger rollback
        throw new Error("__ROLLBACK_TEST_DB__");
      })
      .catch((err: unknown) => {
        // Only suppress the rollback error; propagate all other errors
        if (
          err &&
          typeof err === "object" &&
          "message" in err &&
          err.message !== "__ROLLBACK_TEST_DB__"
        ) {
          throw err;
        }
      })
      .finally(() => {
        void sql.end();
      });

    // Wait for the transaction to be ready and the database to be available
    const database = yield* Effect.promise(() => readyPromise);

    // Add finalizer to signal completion and wait for rollback
    yield* Effect.addFinalizer(() =>
      Effect.promise(() => {
        resolveComplete();
        return transactionPromise;
      }),
    );

    return database;
  }),
);

export const withTestDatabase = <A, E>(
  testFn: (db: Database) => Effect.Effect<A, E, never>,
) => {
  return async () => {
    const sql = postgres(TEST_DATABASE_URL, {
      max: 5,
      fetch_types: false,
    });
    const db = drizzle(sql, { schema });
    // Using db.transaction with a rollback: throw after testFn so the transaction ALWAYS rolls back, but
    // propagate errors from testFn for true test failures
    await db
      .transaction(async (tx) => {
        const txDb = getDatabase(tx);
        await Effect.runPromise(testFn(txDb));
        // Always throw after test to cause rollback
        throw new Error("__ROLLBACK_TEST_DB__");
      })
      .catch((err: unknown) => {
        // Only suppress the rollback error; propagate all other errors
        if (
          err &&
          typeof err === "object" &&
          "message" in err &&
          err.message !== "__ROLLBACK_TEST_DB__"
        ) {
          throw err;
        }
      });
  };
};

function createMockDatabase(error: Error): PostgresJsDatabase<typeof schema> {
  const createRejectingPromise = () => Promise.reject(error);

  return {
    select: () => ({
      from: () => {
        const promise = createRejectingPromise();
        return {
          where: () => ({
            limit: () => promise,
          }),
          innerJoin: () => ({
            where: () => ({
              limit: () => promise,
            }),
          }),
          then: promise.then.bind(promise),
          catch: promise.catch.bind(promise),
        };
      },
    }),
    delete: () => ({
      where: () => ({
        returning: () => createRejectingPromise(),
      }),
    }),
    insert: () => ({
      values: () => ({
        onConflictDoUpdate: () => ({
          returning: () => createRejectingPromise(),
        }),
        returning: () => createRejectingPromise(),
      }),
    }),
    update: () => ({
      set: () => ({
        where: () => ({
          returning: () => createRejectingPromise(),
        }),
      }),
    }),
  } as unknown as PostgresJsDatabase<typeof schema>;
}

export const withErroringService = <T, A, E>(
  ServiceClass: new (db: PostgresJsDatabase<typeof schema>) => T,
  testFn: (service: T) => Effect.Effect<A, E, never>,
) => {
  return async () => {
    const service = new ServiceClass(
      createMockDatabase(new Error("Database connection failed")),
    );
    await Effect.runPromise(testFn(service));
  };
};

/**
 * Creates a partial mock database for testing specific scenarios.
 * Operations not specified will throw an error by default.
 */
export function createPartialMockDatabase(
  overrides: Partial<{
    select: () => unknown;
    insert: () => unknown;
    update: () => unknown;
    delete: () => unknown;
  }>,
): PostgresJsDatabase<typeof schema> {
  const defaultError = new Error("Database operation not mocked");
  const createRejectingPromise = () => Promise.reject(defaultError);

  return {
    select:
      overrides.select ??
      (() => ({
        from: () => ({
          where: () => ({
            limit: () => createRejectingPromise(),
          }),
          innerJoin: () => ({
            where: () => ({
              limit: () => createRejectingPromise(),
            }),
          }),
        }),
      })),
    insert:
      overrides.insert ??
      (() => ({
        values: () => ({
          onConflictDoUpdate: () => createRejectingPromise(),
          returning: () => createRejectingPromise(),
        }),
      })),
    update:
      overrides.update ??
      (() => ({
        set: () => ({
          where: () => ({
            returning: () => createRejectingPromise(),
          }),
        }),
      })),
    delete:
      overrides.delete ??
      (() => ({
        where: () => ({
          returning: () => createRejectingPromise(),
        }),
      })),
  } as unknown as PostgresJsDatabase<typeof schema>;
}

// ============================================================================
// Mock database builder
// ============================================================================

type MockResult = unknown[] | Error;

/**
 * Builder for creating mock databases with sequenced responses.
 *
 * Each call to select/insert/update/delete adds a response to a queue.
 * When the mock is used, responses are returned in order. Pass an array
 * for success, or an Error for failure.
 *
 * Example:
 * ```ts
 * const db = new MockDatabase()
 *   .select([{ role: "OWNER" }])           // 1st select succeeds
 *   .select(new Error("Connection lost"))  // 2nd select fails
 *   .build();
 *
 * const result = yield* db.projects.findById(...);
 * ```
 */
export class MockDatabase {
  private selectResults: MockResult[] = [];
  private insertResults: MockResult[] = [];
  private updateResults: MockResult[] = [];
  private deleteResults: MockResult[] = [];

  select(result: MockResult): this {
    this.selectResults.push(result);
    return this;
  }

  insert(result: MockResult): this {
    this.insertResults.push(result);
    return this;
  }

  update(result: MockResult): this {
    this.updateResults.push(result);
    return this;
  }

  delete(result: MockResult): this {
    this.deleteResults.push(result);
    return this;
  }

  build(): Database {
    let selectIndex = 0;
    let insertIndex = 0;
    let updateIndex = 0;
    let deleteIndex = 0;

    const makePromise = (
      results: MockResult[],
      index: number,
    ): Promise<unknown[]> => {
      const result = results[index];
      if (result === undefined) {
        return Promise.reject(new Error("No more mocked responses"));
      }
      if (result instanceof Error) {
        return Promise.reject(result);
      }
      return Promise.resolve(result);
    };

    // Create a terminal promise handler that works for all chain patterns
    const createTerminal = (results: MockResult[], getIndex: () => number) => {
      const promise = makePromise(results, getIndex());
      return {
        limit: () => promise,
        then: promise.then.bind(promise),
        catch: promise.catch.bind(promise),
      };
    };

    const drizzleMock = {
      select: () => {
        const idx = selectIndex++;
        return {
          from: () => {
            const terminal = createTerminal(this.selectResults, () => idx);
            return {
              where: () => terminal,
              innerJoin: () => ({
                where: () => terminal,
              }),
              limit: terminal.limit,
              then: terminal.then,
              catch: terminal.catch,
            };
          },
        };
      },
      insert: () => {
        const idx = insertIndex++;
        const promise = makePromise(this.insertResults, idx);
        return {
          values: () => ({
            onConflictDoUpdate: () => promise,
            returning: () => promise,
          }),
        };
      },
      update: () => {
        const idx = updateIndex++;
        const promise = makePromise(this.updateResults, idx);
        return {
          set: () => ({
            where: () => ({
              returning: () => promise,
            }),
          }),
        };
      },
      delete: () => {
        const idx = deleteIndex++;
        const promise = makePromise(this.deleteResults, idx);
        return {
          where: () => ({
            returning: () => promise,
            then: promise.then.bind(promise),
            catch: promise.catch.bind(promise),
          }),
        };
      },
    } as unknown as PostgresJsDatabase<typeof schema>;

    return getDatabase(drizzleMock);
  }
}

// ============================================================================
// Test fixture effects
// ============================================================================

/**
 * Creates a test organization with an owner and a non-member user.
 *
 * Returns { org, owner, nonMember } where:
 * - owner: a user who owns the organization
 * - nonMember: a user who is NOT a member (useful for permission tests)
 *
 * Requires DatabaseService - call `yield* DatabaseService` in your test
 * if you need to perform additional database operations.
 */
export const TestOrganizationFixture = Effect.gen(function* () {
  const db = yield* DatabaseService;

  const owner = yield* db.users.create({
    data: { email: "owner@example.com", name: "Owner" },
  });

  const org = yield* db.organizations.create({
    data: { name: "Test Organization" },
    userId: owner.id,
  });

  const nonMember = yield* db.users.create({
    data: { email: "nonmember@example.com", name: "Non Member" },
  });

  return { org, owner, nonMember };
});
