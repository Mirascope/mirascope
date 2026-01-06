/**
 * @fileoverview ClickHouse client service for analytics data access.
 *
 * Provides Effect-based ClickHouse client implementations for both
 * Node.js and Cloudflare Workers environments.
 *
 * ## Architecture
 *
 * ```
 * ClickHouseClient (Effect Service Tag)
 *   ├── ClickHouseClientNodeLive (@clickhouse/client for Node.js)
 *   └── ClickHouseClientWorkersLive (fetch + HTTP API for Workers)
 * ```
 *
 * ## Usage
 *
 * - Node.js (local dev, API handlers): Use `ClickHouseClientNodeLive`
 * - Workers (Queue Consumer, Cron): Use `ClickHouseClientWorkersLive`
 *
 * ## TLS Constraints
 *
 * - Node.js: Full TLS configuration support (custom CA, hostname verify, etc.)
 * - Workers: System CA only (Cloudflare-managed), no custom CA support
 *
 * @example
 * ```ts
 * import { ClickHouseClient, ClickHouseClientNodeLive } from "@/clickhouse/client";
 *
 * const program = Effect.gen(function* () {
 *   const client = yield* ClickHouseClient;
 *   const spans = yield* client.query<SpanRow>("SELECT * FROM spans_analytics LIMIT 10");
 *   return spans;
 * });
 *
 * await Effect.runPromise(
 *   program.pipe(Effect.provide(ClickHouseClientNodeLive))
 * );
 * ```
 */

import { createClient, type ClickHouseClient as CHClient } from "@clickhouse/client";
import { Context, Effect, Layer } from "effect";
import * as fs from "node:fs";
import { ClickHouseError } from "@/errors";
import { SettingsService, type Settings } from "@/settings";

// =============================================================================
// Service Interface
// =============================================================================

/**
 * ClickHouseClient service interface.
 *
 * Provides query, insert, and command operations for ClickHouse.
 * Implementations differ between Node.js and Workers environments.
 */
export class ClickHouseClient extends Context.Tag("ClickHouseClient")<
  ClickHouseClient,
  {
    /** Execute a SELECT query and return typed results. */
    readonly query: <T>(
      sql: string,
      params?: Record<string, unknown>
    ) => Effect.Effect<T[], ClickHouseError>;
    /** Insert rows into a table in JSONEachRow format. */
    readonly insert: <T extends Record<string, unknown>>(
      table: string,
      rows: T[]
    ) => Effect.Effect<void, ClickHouseError>;
    /** Execute a DDL/DML command (CREATE, ALTER, etc.). */
    readonly command: (sql: string) => Effect.Effect<void, ClickHouseError>;
  }
>() {}

// =============================================================================
// Node.js Implementation (@clickhouse/client)
// =============================================================================

const createNodeClickHouseClient = (settings: Settings): CHClient => {
  // TLS CA certificate loading with explicit error handling
  let caCert: Buffer | undefined;
  if (settings.CLICKHOUSE_TLS_ENABLED && settings.CLICKHOUSE_TLS_CA) {
    try {
      caCert = fs.readFileSync(settings.CLICKHOUSE_TLS_CA);
    } catch (error) {
      throw new Error(
        `Failed to read ClickHouse TLS CA certificate: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  // Build TLS options only if explicitly enabled with CA cert
  const tlsOptions =
    settings.CLICKHOUSE_TLS_ENABLED && caCert
      ? { ca_cert: caCert }
      : undefined;

  return createClient({
    url: settings.CLICKHOUSE_URL,
    username: settings.CLICKHOUSE_USER,
    password: settings.CLICKHOUSE_PASSWORD,
    database: settings.CLICKHOUSE_DATABASE,
    tls: tlsOptions,
    max_open_connections: 10,
    request_timeout: 30000,
  });
};

/**
 * ClickHouseClient implementation for Node.js environment.
 *
 * Uses `@clickhouse/client` for native TCP/HTTP connections with
 * full TLS configuration support.
 */
export const ClickHouseClientNodeLive = Layer.effect(
  ClickHouseClient,
  Effect.gen(function* () {
    const settings = yield* SettingsService;
    const client = createNodeClickHouseClient(settings);

    return {
      query: <T>(sql: string, params?: Record<string, unknown>) =>
        Effect.tryPromise({
          try: async () => {
            const result = await client.query({
              query: sql,
              query_params: params,
              format: "JSONEachRow",
            });
            return await result.json<T[]>();
          },
          catch: (e) =>
            new ClickHouseError({
              message: `Query failed: ${e instanceof Error ? e.message : String(e)}`,
              cause: e,
            }),
        }),

      insert: <T extends Record<string, unknown>>(table: string, rows: T[]) =>
        Effect.tryPromise({
          try: async () => {
            if (rows.length === 0) return;
            await client.insert({
              table,
              values: rows,
              format: "JSONEachRow",
            });
          },
          catch: (e) =>
            new ClickHouseError({
              message: `Insert failed: ${e instanceof Error ? e.message : String(e)}`,
              cause: e,
            }),
        }),

      command: (sql: string) =>
        Effect.tryPromise({
          try: async () => {
            await client.command({ query: sql });
          },
          catch: (e) =>
            new ClickHouseError({
              message: `Command failed: ${e instanceof Error ? e.message : String(e)}`,
              cause: e,
            }),
        }),
    };
  })
);

// =============================================================================
// Cloudflare Workers Implementation (fetch + HTTP API)
// =============================================================================

/**
 * Internal Workers HTTP client for ClickHouse.
 *
 * Uses fetch API with ClickHouse HTTP interface.
 * TLS is handled by Cloudflare's system CA (no custom CA support).
 */
const createWorkersClickHouseClient = (settings: Settings) => {
  const baseUrl = settings.CLICKHOUSE_URL;

  // Production validation: require HTTPS
  if (settings.env === "production" && !baseUrl?.startsWith("https://")) {
    throw new Error(
      "CLICKHOUSE_URL must use https:// in production (Workers environment)"
    );
  }

  const database = settings.CLICKHOUSE_DATABASE ?? "default";
  const authHeader = `Basic ${btoa(`${settings.CLICKHOUSE_USER ?? "default"}:${settings.CLICKHOUSE_PASSWORD ?? ""}`)}`;

  return {
    query: async <T>(
      sql: string,
      params?: Record<string, unknown>
    ): Promise<T[]> => {
      const urlParams = new URLSearchParams({
        database,
        default_format: "JSONEachRow",
      });

      // Add query parameters
      if (params) {
        for (const [key, value] of Object.entries(params)) {
          urlParams.set(`param_${key}`, String(value));
        }
      }

      const response = await fetch(`${baseUrl}/?${urlParams}`, {
        method: "POST",
        headers: {
          Authorization: authHeader,
          "Content-Type": "text/plain",
        },
        body: sql,
      });

      if (!response.ok) {
        throw new Error(
          `ClickHouse query failed: ${response.status} ${await response.text()}`
        );
      }

      const text = await response.text();
      if (!text.trim()) return [];

      // Parse JSONEachRow format (one JSON object per line)
      return text
        .trim()
        .split("\n")
        .map((line) => JSON.parse(line) as T);
    },

    insert: async <T extends Record<string, unknown>>(
      table: string,
      rows: T[]
    ): Promise<void> => {
      if (rows.length === 0) return;

      const urlParams = new URLSearchParams({
        database,
        query: `INSERT INTO ${table} FORMAT JSONEachRow`,
      });

      const body = rows.map((row) => JSON.stringify(row)).join("\n");

      const response = await fetch(`${baseUrl}/?${urlParams}`, {
        method: "POST",
        headers: {
          Authorization: authHeader,
          "Content-Type": "text/plain",
        },
        body,
      });

      if (!response.ok) {
        throw new Error(
          `ClickHouse insert failed: ${response.status} ${await response.text()}`
        );
      }
    },

    command: async (sql: string): Promise<void> => {
      const urlParams = new URLSearchParams({ database });

      const response = await fetch(`${baseUrl}/?${urlParams}`, {
        method: "POST",
        headers: {
          Authorization: authHeader,
          "Content-Type": "text/plain",
        },
        body: sql,
      });

      if (!response.ok) {
        throw new Error(
          `ClickHouse command failed: ${response.status} ${await response.text()}`
        );
      }
    },
  };
};

/**
 * ClickHouseClient implementation for Cloudflare Workers environment.
 *
 * Uses fetch API with ClickHouse HTTP interface.
 *
 * TLS Constraints:
 * - System CA only (Cloudflare-managed root certificates)
 * - Custom CA certificates are NOT supported
 * - ClickHouse must have a public CA signed certificate in production
 */
export const ClickHouseClientWorkersLive = Layer.effect(
  ClickHouseClient,
  Effect.gen(function* () {
    const settings = yield* SettingsService;
    const client = createWorkersClickHouseClient(settings);

    return {
      query: <T>(sql: string, params?: Record<string, unknown>) =>
        Effect.tryPromise({
          try: () => client.query<T>(sql, params),
          catch: (e) =>
            new ClickHouseError({
              message: `Query failed: ${e instanceof Error ? e.message : String(e)}`,
              cause: e,
            }),
        }),

      insert: <T extends Record<string, unknown>>(table: string, rows: T[]) =>
        Effect.tryPromise({
          try: () => client.insert(table, rows),
          catch: (e) =>
            new ClickHouseError({
              message: `Insert failed: ${e instanceof Error ? e.message : String(e)}`,
              cause: e,
            }),
        }),

      command: (sql: string) =>
        Effect.tryPromise({
          try: () => client.command(sql),
          catch: (e) =>
            new ClickHouseError({
              message: `Command failed: ${e instanceof Error ? e.message : String(e)}`,
              cause: e,
            }),
        }),
    };
  })
);

// =============================================================================
// Default Export (Node.js)
// =============================================================================

/**
 * Default ClickHouseClient layer for local development and testing.
 * Uses Node.js implementation with `@clickhouse/client`.
 */
export const ClickHouseClientLive = ClickHouseClientNodeLive;
