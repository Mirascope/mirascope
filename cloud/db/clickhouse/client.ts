/**
 * @fileoverview ClickHouse client service for analytics data access.
 *
 * Provides an Effect-based ClickHouse client using @clickhouse/client-web
 * (Fetch + Web Streams) compatible with Cloudflare Workers.
 *
 * ## Architecture
 *
 * ```
 * ClickHouse.layer (HTTP connection)
 *   └── ClickHouse (Effect Service)
 * ```
 *
 * ## Usage
 *
 * - Local dev / CI: Use `ClickHouseLive`
 * - Workers (production): Use `ClickHouseLive`
 *
 * ## TLS Constraints
 *
 * - System CA only (no custom CA support)
 *
 * @example
 * ```ts
 * import { ClickHouse, ClickHouseLive } from "@/db/clickhouse/client";
 *
 * const program = Effect.gen(function* () {
 *   const client = yield* ClickHouse;
 *   const spans = yield* client.unsafeQuery<SpanRow>(
 *     "SELECT * FROM spans_analytics LIMIT 10"
 *   );
 *   return spans;
 * });
 *
 * await Effect.runPromise(
 *   program.pipe(Effect.provide(ClickHouseLive))
 * );
 * ```
 */

import { Context, Effect, Layer } from "effect";
import {
  createClient,
  type ClickHouseClient as WebClickHouseClient,
} from "@clickhouse/client-web";
import { ClickHouseError } from "@/errors";
import { SettingsService, type Settings } from "@/settings";

// =============================================================================
// Service Interface
// =============================================================================

/**
 * ClickHouse configuration options.
 */
export interface ClickHouseConfig {
  /** ClickHouse HTTP URL (e.g., http://localhost:8123) */
  url: string;

  /** ClickHouse username */
  user: string;

  /** ClickHouse password */
  password?: string;

  /** ClickHouse database name */
  database: string;
}

/**
 * ClickHouse service interface type.
 *
 * Provides convenience methods for query, insert, and command operations.
 */
export interface ClickHouseClient {
  /**
   * Execute a raw SQL query without parameterization.
   * WARNING: This method is unsafe and should only be used for trusted SQL.
   */
  readonly unsafeQuery: <T extends object>(
    sql: string,
    params?: Record<string, unknown>,
  ) => Effect.Effect<readonly T[], ClickHouseError>;

  /** Insert rows into a table in JSONEachRow format. */
  readonly insert: <T extends Record<string, unknown>>(
    table: string,
    rows: T[],
  ) => Effect.Effect<void, ClickHouseError>;

  /** Execute a DDL/DML command (CREATE, ALTER, etc.). */
  readonly command: (sql: string) => Effect.Effect<void, ClickHouseError>;
}

/**
 * ClickHouse service.
 */
export class ClickHouse extends Context.Tag("ClickHouse")<
  ClickHouse,
  ClickHouseClient
>() {
  /**
   * Default layer using SettingsService for configuration.
   * Requires SettingsService to be provided.
   *
   * Uses @clickhouse/client-web over the ClickHouse HTTP interface.
   */
  static Default = Layer.effect(
    ClickHouse,
    Effect.gen(function* () {
      const settings = yield* SettingsService;
      const client = createWebClickHouseClient(settings);

      const toClickHouseError = (error: unknown): ClickHouseError => {
        if (error instanceof ClickHouseError) return error;
        if (
          error &&
          typeof error === "object" &&
          "_tag" in error &&
          error._tag === "SqlError"
        ) {
          return new ClickHouseError({
            message: "ClickHouse operation failed",
            cause: error,
          });
        }
        return new ClickHouseError({
          message: `ClickHouse operation failed: ${
            error instanceof Error ? error.message : String(error)
          }`,
          cause: error instanceof Error ? error : undefined,
        });
      };

      const mapClickHouseError = <A, E, R>(
        effect: Effect.Effect<A, E, R>,
      ): Effect.Effect<A, ClickHouseError, R> =>
        effect.pipe(Effect.mapError((error) => toClickHouseError(error)));

      return {
        unsafeQuery: <T extends object>(
          query: string,
          params?: Record<string, unknown>,
        ): Effect.Effect<readonly T[], ClickHouseError> =>
          mapClickHouseError(
            Effect.tryPromise({
              try: async () => {
                const result = await client.query({
                  query,
                  format: "JSONEachRow",
                  query_params: params,
                });
                return result.json<T>();
              },
              catch: (error) => error,
            }),
          ),
        insert: <T extends Record<string, unknown>>(
          table: string,
          rows: T[],
        ): Effect.Effect<void, ClickHouseError> => {
          if (rows.length === 0) return Effect.void;
          return mapClickHouseError(
            Effect.tryPromise({
              try: async () => {
                await client.insert({
                  table,
                  values: rows,
                  format: "JSONEachRow",
                });
              },
              catch: (error) => error,
            }),
          );
        },
        command: (query: string): Effect.Effect<void, ClickHouseError> =>
          mapClickHouseError(
            Effect.tryPromise({
              try: async () => {
                await client.command({ query });
              },
              catch: (error) => error,
            }),
          ),
      };
    }),
  );

  /**
   * Creates a layer with direct configuration.
   * Does not require SettingsService.
   *
   * @param config - ClickHouse connection configuration
   */
  static layer = (config: ClickHouseConfig, env: Settings["env"] = "local") => {
    const settings: Settings = {
      env,

      CLICKHOUSE_URL: config.url,

      CLICKHOUSE_USER: config.user,

      CLICKHOUSE_PASSWORD: config.password,

      CLICKHOUSE_DATABASE: config.database,
    };

    return ClickHouse.Default.pipe(
      Layer.provide(Layer.succeed(SettingsService, settings)),
    );
  };
}

/**
 * Validates TLS settings for compatibility with @clickhouse/client-web.
 *
 * @param settings - Application settings including ClickHouse configuration
 * @throws Error if unsupported TLS settings are configured
 */
const validateTLSSettings = (settings: Settings): void => {
  if (settings.CLICKHOUSE_TLS_ENABLED) {
    if (settings.CLICKHOUSE_TLS_SKIP_VERIFY) {
      throw new Error(
        "CLICKHOUSE_TLS_SKIP_VERIFY=true is not supported by @clickhouse/client-web. " +
          "The client always verifies certificates when TLS is enabled.",
      );
    }

    if (settings.CLICKHOUSE_TLS_HOSTNAME_VERIFY === false) {
      throw new Error(
        "CLICKHOUSE_TLS_HOSTNAME_VERIFY=false is not supported by @clickhouse/client-web. " +
          "The client always performs hostname verification.",
      );
    }

    if (settings.CLICKHOUSE_TLS_CA) {
      throw new Error(
        "CLICKHOUSE_TLS_CA is not supported by @clickhouse/client-web. " +
          "Custom CA certificates are not available in Fetch-based environments.",
      );
    }

    if (
      settings.CLICKHOUSE_TLS_MIN_VERSION &&
      settings.CLICKHOUSE_TLS_MIN_VERSION !== "TLSv1.2"
    ) {
      console.warn(
        `CLICKHOUSE_TLS_MIN_VERSION=${settings.CLICKHOUSE_TLS_MIN_VERSION} is not supported by @clickhouse/client-web.`,
      );
      throw new Error(
        "CLICKHOUSE_TLS_MIN_VERSION is not supported by @clickhouse/client-web.",
      );
    }
  }
};

/**
 * Creates a ClickHouse web client from Settings.
 *
 * @param settings - Application settings including ClickHouse configuration
 * @returns ClickHouse web client
 */
const createWebClickHouseClient = (settings: Settings): WebClickHouseClient => {
  validateTLSSettings(settings);

  if (
    settings.env === "production" &&
    !settings.CLICKHOUSE_URL?.startsWith("https://")
  ) {
    throw new Error(
      "CLICKHOUSE_URL must use https:// in production (Workers environment)",
    );
  }

  return createClient({
    url: settings.CLICKHOUSE_URL,

    username: settings.CLICKHOUSE_USER,

    password: settings.CLICKHOUSE_PASSWORD,

    database: settings.CLICKHOUSE_DATABASE,

    request_timeout: 30000,

    max_open_connections: 10,
  });
};

// =============================================================================
// Default Export
// =============================================================================

/**
 * Default ClickHouse layer for local development and testing.
 */
export const ClickHouseLive = ClickHouse.Default;
