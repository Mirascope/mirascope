/**
 * @fileoverview ClickHouse Effect-native service.
 *
 * This module provides the `ClickHouse` service which wraps the ClickHouse
 * web client (@clickhouse/client-web) for use in Edge runtimes like Cloudflare Workers.
 *
 * @clickhouse/client-web uses Fetch API under the hood, making it compatible with
 * Cloudflare Workers, Deno, and other edge environments that don't support TCP sockets.
 *
 * ## Usage
 *
 * ```ts
 * import { ClickHouse } from "@/clickhouse/client";
 *
 * const querySpans = Effect.gen(function* () {
 *   const ch = yield* ClickHouse;
 *
 *   const spans = yield* ch.unsafeQuery<Span>(`SELECT * FROM spans`);
 *   return spans;
 * });
 *
 * // Provide with Settings (uses ClickHouse config from settings)
 * querySpans.pipe(Effect.provide(ClickHouse.Default), Effect.provide(Settings.Live));
 * ```
 *
 * ## Error Handling
 *
 * All operations wrap ClickHouse errors in `ClickHouseError`:
 *
 * ```ts
 * const result = yield* ch.unsafeQuery(`SELECT ...`).pipe(
 *   Effect.catchTag("ClickHouseError", (error) => {
 *     console.error("ClickHouse failed:", error.message);
 *     return Effect.succeed([]);
 *   })
 * );
 * ```
 */

import { Context, Effect, Layer } from "effect";
import {
  createClient,
  type ClickHouseClient as WebClickHouseClient,
} from "@clickhouse/client-web";
import { ClickHouseError } from "@/errors";
import { Settings, type ClickHouseConfig } from "@/settings";

// =============================================================================
// Service Interface
// =============================================================================

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
   * Default layer using Settings for configuration.
   * Requires Settings to be provided.
   *
   * Uses @clickhouse/client-web over the ClickHouse HTTP interface.
   * TLS configuration is validated by Settings at startup.
   */
  static Default = Layer.effect(
    ClickHouse,
    Effect.gen(function* () {
      const settings = yield* Settings;
      const client = createWebClickHouseClient(settings.clickhouse);

      return createClickHouseService(client);
    }),
  );

  /**
   * Creates a layer with direct configuration.
   * Does not require Settings.
   *
   * Note: TLS configuration is NOT validated here. When using this method,
   * ensure the config has valid TLS settings for @clickhouse/client-web.
   * For production use, prefer ClickHouse.Default with Settings.
   *
   * @param config - ClickHouse connection configuration
   */
  static layer = (config: ClickHouseConfig) => {
    const client = createWebClickHouseClient(config);
    return Layer.succeed(ClickHouse, createClickHouseService(client));
  };
}

/**
 * Creates a ClickHouse web client from config.
 * TLS validation is performed by Settings at startup.
 *
 * @param config - ClickHouse configuration (validated by Settings)
 * @returns ClickHouse web client
 */
const createWebClickHouseClient = (
  config: ClickHouseConfig,
): WebClickHouseClient =>
  createClient({
    url: config.url,
    username: config.user,
    password: config.password,
    database: config.database,
  });

/**
 * Creates the ClickHouse service implementation.
 *
 * @param client - ClickHouse web client
 * @returns ClickHouse service implementation
 */
const createClickHouseService = (
  client: WebClickHouseClient,
): ClickHouseClient => {
  const toClickHouseError = (error: unknown): ClickHouseError => {
    if (error instanceof ClickHouseError) return error;
    if (
      error &&
      typeof error === "object" &&
      "_tag" in error &&
      error._tag === "ClickHouseError"
    ) {
      return error as ClickHouseError;
    }
    return new ClickHouseError({
      message: error instanceof Error ? error.message : String(error),
      cause: error,
    });
  };

  return {
    unsafeQuery: <T extends object>(
      sql: string,
      params?: Record<string, unknown>,
    ) =>
      Effect.tryPromise({
        try: async () => {
          const result = await client.query({
            query: sql,
            format: "JSONEachRow",
            query_params: params,
          });
          return result.json<T>();
        },
        catch: (error) => toClickHouseError(error),
      }),

    insert: <T extends Record<string, unknown>>(table: string, rows: T[]) =>
      Effect.tryPromise({
        try: async () => {
          await client.insert({
            table,
            values: rows,
            format: "JSONEachRow",
          });
        },
        catch: (error) => toClickHouseError(error),
      }),

    command: (query: string) =>
      Effect.tryPromise({
        try: async () => {
          await client.command({ query });
        },
        catch: (error) => toClickHouseError(error),
      }),
  };
};
