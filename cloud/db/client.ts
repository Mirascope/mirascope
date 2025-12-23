/**
 * @fileoverview Effect-native Drizzle ORM service using @effect/sql-drizzle.
 *
 * This module provides the `DrizzleORM` service which wraps Drizzle ORM with Effect,
 * enabling `yield*` semantics for database queries and proper typed error handling.
 *
 * ## Architecture
 *
 * ```
 * PgClient.layerConfig (connection pool)
 *   └── PgDrizzle (Drizzle with Effect)
 *         └── DrizzleORM service (schema-aware + transactions)
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { DrizzleORM } from "@/db/client";
 *
 * const getUser = (userId: string) =>
 *   Effect.gen(function* () {
 *     const client = yield* DrizzleORM;
 *
 *     const [user] = yield* client
 *       .select()
 *       .from(users)
 *       .where(eq(users.id, userId))
 *       .limit(1);
 *
 *     return user;
 *   });
 * ```
 *
 * ## Transactions
 *
 * Use `client.transaction` for atomic operations with typed error channels:
 *
 * ```ts
 * import { DrizzleORM } from "@/db/client";
 *
 * const createOrgWithMembership = Effect.gen(function* () {
 *   const client = yield* DrizzleORM;
 *
 *   return yield* client.transaction(
 *     Effect.gen(function* () {
 *       const [org] = yield* client.insert(organizations).values({...}).returning();
 *       yield* client.insert(memberships).values({ organizationId: org.id, ... });
 *       return org;
 *     })
 *   );
 * });
 * ```
 */

import { Effect, Layer, Config, Context } from "effect";
import type { PgRemoteDatabase } from "drizzle-orm/pg-proxy";
import * as Pg from "@effect/sql-drizzle/Pg";
import { PgClient } from "@effect/sql-pg";
import { SqlClient, type SqlError } from "@effect/sql";
import * as schema from "@/db/schema";
import { DatabaseError } from "@/errors";

/**
 * Wraps an effect that may fail with SqlError and maps it to DatabaseError.
 *
 * Use this to convert SqlError (from @effect/sql) to DatabaseError for cleaner
 * error handling in service code.
 */
export const mapSqlError = <A, E, R>(
  effect: Effect.Effect<A, E | SqlError.SqlError, R>,
): Effect.Effect<A, Exclude<E, SqlError.SqlError> | DatabaseError, R> =>
  effect.pipe(
    Effect.mapError((e): Exclude<E, SqlError.SqlError> | DatabaseError =>
      e && typeof e === "object" && "_tag" in e && e._tag === "SqlError"
        ? new DatabaseError({
            message: "Database transaction failed",
            cause: e,
          })
        : (e as Exclude<E, SqlError.SqlError>),
    ),
  );

/**
 * DrizzleORM client configuration options.
 *
 * Either provide a `connectionString` or individual connection parameters.
 */
export interface DrizzleORMConfig {
  /** PostgreSQL connection string (e.g., postgresql://user:pass@host:port/db) */
  connectionString?: string;
  /** Database host */
  host?: string;
  /** Database port */
  port?: number;
  /** Database name */
  database?: string;
  /** Database username */
  username?: string;
  /** Database password */
  password?: string;
}

/**
 * The DrizzleORM client type - a schema-aware Drizzle instance with Effect transaction support.
 */
export interface DrizzleORMClient extends PgRemoteDatabase<typeof schema> {
  /**
   * Executes an Effect within a database transaction.
   *
   * If the Effect fails (via `Effect.fail` or throwing), the transaction
   * is automatically rolled back. On success, the transaction is committed.
   *
   * Nested transactions use savepoints automatically.
   *
   * SqlError from transaction management is automatically mapped to DatabaseError
   * for cleaner error handling in service code.
   *
   * @param effect - The Effect to run within the transaction
   * @returns The result of the Effect, with DatabaseError for transaction failures
   *
   * @example
   * ```ts
   * const client = yield* DrizzleORM;
   *
   * const result = yield* client.withTransaction(
   *   Effect.gen(function* () {
   *     const [user] = yield* client.insert(users).values({...}).returning();
   *     yield* client.insert(profiles).values({ userId: user.id, ... });
   *
   *     // Any failure here rolls back both inserts
   *     if (someCondition) {
   *       yield* Effect.fail(new MyError());
   *     }
   *
   *     return user;
   *   })
   * );
   * ```
   */
  withTransaction: <A, E, R>(
    effect: Effect.Effect<A, E, R>,
  ) => Effect.Effect<A, Exclude<E, SqlError.SqlError> | DatabaseError, R>;
}

/**
 * Schema-aware Effect-native Drizzle ORM service.
 *
 * This service provides a Drizzle ORM instance that returns Effects instead of
 * Promises, enabling seamless integration with Effect's ecosystem including:
 * - `yield*` syntax for database queries
 * - Typed error channels
 * - Automatic resource management
 * - Transaction support via `client.transaction()`
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const client = yield* DrizzleORM;
 *
 *   // Queries return Effects
 *   const users = yield* client
 *     .select()
 *     .from(schema.users)
 *     .where(isNull(schema.users.deletedAt));
 *
 *   return users;
 * });
 *
 * // Provide the DrizzleORM layer
 * program.pipe(
 *   Effect.provide(DrizzleORM.layer({ connectionString: "..." }))
 * );
 * ```
 */
export class DrizzleORM extends Context.Tag("DrizzleORM")<
  DrizzleORM,
  DrizzleORMClient
>() {
  /**
   * Default layer that creates the DrizzleORM service.
   *
   * Requires SqlClient to be provided (typically via PgClient.layer).
   */
  static Default = Layer.effect(
    DrizzleORM,
    Effect.gen(function* () {
      const sql = yield* SqlClient.SqlClient;

      const db: PgRemoteDatabase<typeof schema> = yield* Pg.make({ schema });

      return Object.assign(db, {
        withTransaction: <A, E, R>(
          effect: Effect.Effect<A, E, R>,
        ): Effect.Effect<A, Exclude<E, SqlError.SqlError> | DatabaseError, R> =>
          mapSqlError(sql.withTransaction(effect)),
      }) as DrizzleORMClient;
    }),
  );

  /**
   * Creates a Layer that provides the DrizzleORM service.
   *
   * @param config - Database connection configuration
   * @returns A Layer providing DrizzleORM (and its PgClient dependency)
   *
   * @example
   * ```ts
   * // Using connection string
   * const DrizzleLive = DrizzleORM.layer({
   *   connectionString: process.env.DATABASE_URL,
   * });
   *
   * // Using individual parameters
   * const DrizzleLive = DrizzleORM.layer({
   *   host: "localhost",
   *   port: 5432,
   *   database: "myapp",
   *   username: "postgres",
   *   password: "secret",
   * });
   * ```
   */
  static layer = (config: DrizzleORMConfig) => {
    const PgLive = config.connectionString
      ? PgClient.layerConfig({
          url: Config.redacted(Config.succeed(config.connectionString)),
        })
      : PgClient.layerConfig({
          host: Config.succeed(config.host!),
          port: Config.succeed(config.port!),
          database: Config.succeed(config.database!),
          username: Config.succeed(config.username!),
          password: Config.redacted(Config.succeed(config.password!)),
        });

    return DrizzleORM.Default.pipe(Layer.provideMerge(PgLive));
  };
}
