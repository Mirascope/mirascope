/**
 * @fileoverview ClickHouse migration CLI using @effect/sql-clickhouse.
 *
 * This module provides migration management for ClickHouse using Effect's
 * sql-clickhouse package with the ClickhouseMigrator.
 *
 * ## Architecture
 *
 * ```
 * ClickhouseClient.layerConfig (connection)
 *   └── ClickhouseMigrator.run() (explicit migration execution)
 *         └── ClickhouseMigrator.fromFileSystem() (SQL file loader)
 * ```
 *
 * ## Usage
 *
 * ```bash
 * # Show all migration files
 * bun run clickhouse:plan
 *
 * # Apply migrations
 * bun run clickhouse:migrate
 * ```
 *
 * ## Migration Files
 *
 * Migrations are stored in `cloud/clickhouse/migrations/` with the naming convention:
 * - `00001_migration_name.sql`
 * - `00002_another_migration.sql`
 *
 * Each migration file contains raw SQL statements to execute.
 *
 * @example Migration file (00001_create_spans_analytics.sql)
 * ```sql
 * CREATE TABLE IF NOT EXISTS spans_analytics (
 *   id UUID,
 *   ...
 * ) ENGINE = ReplacingMergeTree(_version) ...;
 * ```
 */

import { Effect, Console, Config, Redacted } from "effect";
import { NodeContext, NodeRuntime } from "@effect/platform-node";
import { ClickhouseClient } from "@effect/sql-clickhouse";
import * as ClickhouseMigrator from "@effect/sql-clickhouse/ClickhouseMigrator";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Directory containing ClickHouse SQL migration files.
 */
const MIGRATIONS_DIRECTORY = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  "migrations",
);

/**
 * Table name for tracking applied migrations.
 */
const MIGRATIONS_TABLE = "clickhouse_migrations";

/**
 * Configuration for ClickHouse connection.
 *
 * Uses environment variables with sensible defaults for local development.
 */
const ClickHouseConnectionConfig = Config.all({
  url: Config.string("CLICKHOUSE_URL").pipe(
    Config.withDefault("http://localhost:8123"),
  ),
  database: Config.string("CLICKHOUSE_DATABASE").pipe(
    Config.withDefault("mirascope_analytics"),
  ),
  username: Config.string("CLICKHOUSE_USER").pipe(
    Config.withDefault("default"),
  ),
  password: Config.redacted("CLICKHOUSE_PASSWORD").pipe(
    Config.withDefault(Redacted.make("clickhouse")),
  ),
});

/**
 * ClickHouse client layer configured from environment variables.
 */
const ClickHouseClientLive = ClickhouseClient.layerConfig(
  Config.map(ClickHouseConnectionConfig, (config) => ({
    url: config.url,
    database: config.database,
    username: config.username,
    password: Redacted.value(config.password),
  })),
);

/**
 * Migration loader that reads SQL migration files from the migrations directory.
 */
const migrationLoader = ClickhouseMigrator.fromFileSystem(MIGRATIONS_DIRECTORY);

/**
 * Plan command - shows all migration files.
 *
 * This command displays all migration files found in the migrations directory.
 * Use 'clickhouse:migrate' to apply any pending migrations.
 */
const planCommand = Effect.gen(function* () {
  yield* Console.log("ClickHouse Migration Files");
  yield* Console.log("=".repeat(50));
  yield* Console.log(`Migrations directory: ${MIGRATIONS_DIRECTORY}`);
  yield* Console.log(`Migrations table: ${MIGRATIONS_TABLE}`);
  yield* Console.log("");

  // Load all migration files from directory
  const migrations = yield* migrationLoader;
  if (migrations.length === 0) {
    yield* Console.log("No migration files found.");
  } else {
    yield* Console.log(`Found ${migrations.length} migration file(s):`);
    for (const migration of migrations) {
      yield* Console.log(`  - ${migration[0]}`);
    }
  }
  yield* Console.log("");
  yield* Console.log(
    "Run 'bun run clickhouse:migrate' to apply pending migrations.",
  );
}).pipe(
  Effect.provide(ClickHouseClientLive),
  Effect.provide(NodeContext.layer),
);

/**
 * Migrate command - applies pending migrations.
 *
 * This command executes all pending migrations in order, updating the
 * migration tracking table to record which migrations have been applied.
 */
const migrateCommand = Effect.gen(function* () {
  yield* Console.log("ClickHouse Migration");
  yield* Console.log("=".repeat(50));
  yield* Console.log(`Migrations directory: ${MIGRATIONS_DIRECTORY}`);
  yield* Console.log(`Migrations table: ${MIGRATIONS_TABLE}`);
  yield* Console.log("");
  yield* Console.log("Running migrations...");

  // Run migrations using ClickhouseMigrator.run()
  const applied = yield* ClickhouseMigrator.run({
    loader: migrationLoader,
    table: MIGRATIONS_TABLE,
  });

  if (applied.length === 0) {
    yield* Console.log("No pending migrations to apply.");
  } else {
    yield* Console.log(`Applied ${applied.length} migration(s):`);
    for (const [id, name] of applied) {
      yield* Console.log(`  - ${id}: ${name}`);
    }
  }
  yield* Console.log("");
  yield* Console.log("Migrations completed successfully.");
}).pipe(
  Effect.provide(ClickHouseClientLive),
  Effect.provide(NodeContext.layer),
);

/**
 * Main entry point - parses CLI arguments and runs the appropriate command.
 */
const main = Effect.gen(function* () {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case "plan":
      yield* planCommand;
      break;
    case "migrate":
      yield* migrateCommand;
      break;
    default:
      yield* Console.log("Usage: bun run clickhouse/migrator.ts <command>");
      yield* Console.log("");
      yield* Console.log("Commands:");
      yield* Console.log("  plan     Show all migration files");
      yield* Console.log("  migrate  Apply pending migrations");
      yield* Effect.fail(new Error(`Unknown command: ${command}`));
  }
});

NodeRuntime.runMain(main);
