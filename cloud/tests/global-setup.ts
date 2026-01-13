import { Effect, Data, Scope } from "effect";
import {
  PostgreSqlContainer,
  type StartedPostgreSqlContainer,
} from "@testcontainers/postgresql";
import {
  GenericContainer,
  type StartedTestContainer,
  Wait,
} from "testcontainers";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import path from "path";
import fs from "fs";
import os from "os";
import { fileURLToPath } from "url";
import { execFileSync } from "node:child_process";
import { randomUUID } from "node:crypto";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// File to store the connection URL between global setup and tests
export const CONNECTION_FILE = path.join(
  os.tmpdir(),
  "mirascope-test-db-url.txt",
);
export const CLICKHOUSE_CONNECTION_FILE = path.join(
  os.tmpdir(),
  "mirascope-test-clickhouse-connection.json",
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
let clickhouseContainer: StartedTestContainer | null = null;

const clickhouseImage = "clickhouse/clickhouse-server:24.10";
const clickhouseUser = process.env.TEST_CLICKHOUSE_USER ?? "default";
const clickhousePassword = process.env.TEST_CLICKHOUSE_PASSWORD ?? randomUUID();
const clickhouseDatabase = "mirascope_analytics";

const acquireClickhouseContainer = Effect.tryPromise({
  try: () =>
    new GenericContainer(clickhouseImage)
      .withExposedPorts(8123, 9000)
      .withEnvironment({
        CLICKHOUSE_DB: clickhouseDatabase,
        CLICKHOUSE_USER: clickhouseUser,
        CLICKHOUSE_PASSWORD: clickhousePassword,
        CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT: "1",
      })
      .withWaitStrategy(Wait.forHttp("/ping", 8123))
      .start(),
  catch: (cause) => new ContainerError({ cause }),
});

const runClickhouseMigrations = (clickhouseUrl: string, nativePort: number) =>
  Effect.try({
    try: () => {
      execFileSync("bash", ["db/clickhouse/migrate.sh", "migrate"], {
        cwd: path.resolve(__dirname, ".."),
        env: {
          ...process.env,
          TZ: "UTC",
          CLICKHOUSE_URL: clickhouseUrl,
          CLICKHOUSE_USER: clickhouseUser,
          CLICKHOUSE_PASSWORD: clickhousePassword,
          CLICKHOUSE_DATABASE: clickhouseDatabase,
          CLICKHOUSE_MIGRATE_NATIVE_PORT: String(nativePort),
        },
        stdio: "inherit",
      });
    },
    catch: (cause) => new ContainerError({ cause }),
  });

// Vitest global setup - runs once before all tests
export async function setup() {
  const scope = Effect.runSync(Scope.make());

  clickhouseContainer = await Effect.runPromise(
    Effect.acquireRelease(acquireClickhouseContainer, (c) =>
      Effect.promise(() => c.stop()),
    ).pipe(Scope.extend(scope)),
  );

  const clickhouseHttpPort = clickhouseContainer.getMappedPort(8123);
  const clickhouseNativePort = clickhouseContainer.getMappedPort(9000);
  const clickhouseUrl = `http://127.0.0.1:${clickhouseHttpPort}`;

  process.env.CLICKHOUSE_URL = clickhouseUrl;
  process.env.CLICKHOUSE_USER = clickhouseUser;
  process.env.CLICKHOUSE_PASSWORD = clickhousePassword;
  process.env.CLICKHOUSE_DATABASE = clickhouseDatabase;
  process.env.CLICKHOUSE_MIGRATE_NATIVE_PORT = String(clickhouseNativePort);

  Effect.runSync(runClickhouseMigrations(clickhouseUrl, clickhouseNativePort));

  fs.writeFileSync(
    CLICKHOUSE_CONNECTION_FILE,
    JSON.stringify(
      {
        url: clickhouseUrl,
        user: clickhouseUser,
        password: clickhousePassword,
        database: clickhouseDatabase,
        nativePort: clickhouseNativePort,
      },
      null,
      2,
    ),
    "utf-8",
  );

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
  try {
    fs.unlinkSync(CLICKHOUSE_CONNECTION_FILE);
  } catch {
    // Ignore if file doesn't exist
  }

  // Stop the container
  if (container) {
    await container.stop();
  }

  if (clickhouseContainer) {
    await clickhouseContainer.stop();
  }
}
