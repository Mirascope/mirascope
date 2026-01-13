import { readFileSync } from "node:fs";

const migrationStatements = [
  readFileSync(
    new URL(
      "../../db/clickhouse/migrations/00001_create_spans_analytics.up.sql",
      import.meta.url,
    ),
    "utf8",
  ),
  readFileSync(
    new URL(
      "../../db/clickhouse/migrations/00002_drop_span_db_ids.up.sql",
      import.meta.url,
    ),
    "utf8",
  ),
];

const renderMigrationStatements = (databaseName: string) =>
  migrationStatements
    .map((statement) => statement.replaceAll("{{database}}", databaseName))
    .join("\n");

const splitStatements = (statementText: string): string[] =>
  statementText
    .split(";")
    .map((statement) => statement.trim())
    .filter((statement) => statement.length > 0);

/**
 * Returns the ClickHouse migration statements for search tests.
 */
export const getSearchMigrationStatements = (databaseName: string): string[] =>
  splitStatements(renderMigrationStatements(databaseName));
