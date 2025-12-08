import * as dotenv from "dotenv";
import { Effect } from "effect";
import { getDatabase, type Database } from "@/db/services";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "@/db/schema";

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
        try {
          await Effect.runPromise(testFn(txDb));
        } catch (err) {
          // If testFn fails, do not try to throw for rollback, just rethrow for test failure
          throw err;
        }
        // Always throw after test to cause rollback
        throw new Error("__ROLLBACK_TEST_DB__");
      })
      .catch((err) => {
        // Only suppress the rollback error; propagate all other errors
        if (err?.message !== "__ROLLBACK_TEST_DB__") {
          throw err;
        }
      });
  };
};
