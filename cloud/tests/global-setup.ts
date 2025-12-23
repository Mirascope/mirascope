import { Effect, Data, Scope } from "effect";
import {
  PostgreSqlContainer,
  type StartedPostgreSqlContainer,
} from "@testcontainers/postgresql";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import path from "path";
import fs from "fs";
import os from "os";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// File to store the connection URL between global setup and tests
export const CONNECTION_FILE = path.join(
  os.tmpdir(),
  "mirascope-test-db-url.txt",
);

// Custom error type for container failures
class ContainerError extends Data.TaggedError("ContainerError")<{
  cause: unknown;
}> {}

// Effect-based container acquisition
const acquireContainer = Effect.tryPromise({
  try: () => new PostgreSqlContainer("postgres:alpine").start(),
  catch: (cause) => new ContainerError({ cause }),
});

// Run migrations on the container
const runMigrations = (connectionUri: string) =>
  Effect.tryPromise({
    try: async () => {
      const sql = postgres(connectionUri, {
        max: 1,
        // Suppress PostgreSQL NOTICE messages (e.g., identifier truncation, type skipping)
        onnotice: () => {},
      });
      const db = drizzle(sql);
      await migrate(db, {
        migrationsFolder: path.resolve(__dirname, "../db/migrations"),
      });
      await sql.end();
    },
    catch: (cause) => new ContainerError({ cause }),
  });

// Store container reference for teardown
let container: StartedPostgreSqlContainer | null = null;

// Vitest global setup - runs once before all tests
export async function setup() {
  const scope = Effect.runSync(Scope.make());

  container = await Effect.runPromise(
    Effect.acquireRelease(acquireContainer, (c) =>
      Effect.promise(() => c.stop()),
    ).pipe(Scope.extend(scope)),
  );

  const connectionUri = container.getConnectionUri();

  // Run migrations
  await Effect.runPromise(runMigrations(connectionUri));

  // Write connection URL to a temp file for tests to read
  fs.writeFileSync(CONNECTION_FILE, connectionUri, "utf-8");

  // Store scope for teardown
  (globalThis as Record<string, unknown>).__TEST_SCOPE__ = scope;
}

// Vitest global teardown - runs once after all tests
export async function teardown() {
  // Clean up the temp file
  try {
    fs.unlinkSync(CONNECTION_FILE);
  } catch {
    // Ignore if file doesn't exist
  }

  // Stop the container
  if (container) {
    await container.stop();
  }
}
