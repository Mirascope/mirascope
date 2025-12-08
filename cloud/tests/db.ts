import * as dotenv from "dotenv";
import { Effect } from "effect";
import { getDatabase, type Database } from "@/db/services";
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
