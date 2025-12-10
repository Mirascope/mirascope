import { Effect } from "effect";
import { eq } from "drizzle-orm";
import type { PgColumn } from "drizzle-orm/pg-core";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { isUniqueConstraintError } from "@/db/utils";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import type * as schema from "@/db/schema";
import type { DatabaseTable } from "@/db/schema";

/**
 * Base service class for CRUD operations on database entities.
 * Provides common database access and transaction support.
 * @template TEntity - The full entity type from the database (unused but kept for documentation)
 * @template TPublic - The public-facing type (what gets returned)
 * @template TId - The type of the entity ID
 * @template TTable - The Drizzle table type (constrained to actual database tables)
 */
export abstract class BaseService<
  TPublic,
  TId,
  TTable extends DatabaseTable = DatabaseTable,
> {
  protected readonly db: PostgresJsDatabase<typeof schema>;

  constructor(db: PostgresJsDatabase<typeof schema>) {
    this.db = db;
  }

  protected abstract getTable(): TTable;
  protected abstract getResourceName(): string;
  protected abstract getPublicFields(): Record<string, PgColumn>;

  get resourceName(): string {
    return this.getResourceName();
  }
  protected getIdColumn(): PgColumn {
    const table = this.getTable();
    return table.id;
  }

  /**
   * Execute operations within a transaction
   */
  // transaction<A, E>(
  //   effect: (tx: PostgresJsDatabase<typeof schema>) => Effect.Effect<A, E>,
  // ): Effect.Effect<A, E | DatabaseError> {
  //   return Effect.tryPromise({
  //     try: async () => {
  //       return await this.db.transaction(async (tx) => {
  //         // tx is already a PostgresJsDatabase instance, use it directly
  //         return await Effect.runPromise(effect(tx));
  //       });
  //     },
  //     catch: (error) =>
  //       new DatabaseError({
  //         message: "Transaction failed",
  //         cause: error,
  //       }),
  //   });
  // }

  create(
    data: TTable["$inferInsert"],
  ): Effect.Effect<TPublic, AlreadyExistsError | DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const table = this.getTable();
        const publicFields = this.getPublicFields();
        const [result] = await this.db
          .insert(table)
          // Type assertion needed: When TTable is a union type, Drizzle's .values()
          // can't narrow the type, but runtime behavior is correct
          // eslint-disable-next-line @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-explicit-any
          .values(data as any)
          .returning(publicFields);

        return result as TPublic;
      },
      catch: (error) => {
        if (isUniqueConstraintError(error)) {
          return new AlreadyExistsError({
            message: `${this.getResourceName()} already exists`,
            resource: this.getResourceName(),
          });
        }
        return new DatabaseError({
          message: `Failed to create ${this.getResourceName()}`,
          cause: error,
        });
      },
    });
  }

  findById(id: TId): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const [result] = await this.db
          .select(this.getPublicFields())
          // Type assertion needed: Drizzle's .from() has complex conditional types
          // (TableLikeHasEmptySelection) that don't work well with generic table types.
          // Runtime behavior is correct - this is purely a TypeScript limitation.
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          .from(this.getTable() as any)
          .where(eq(this.getIdColumn(), id))
          .limit(1);

        return result as TPublic | undefined;
      },
      catch: (error) =>
        new DatabaseError({
          message: `Failed to find ${this.getResourceName()}`,
          cause: error,
        }),
    }).pipe(
      Effect.flatMap((result) => {
        if (!result) {
          return Effect.fail(
            new NotFoundError({
              message: `${this.getResourceName()} with id ${String(id)} not found`,
              resource: this.getResourceName(),
            }),
          );
        }
        return Effect.succeed(result);
      }),
    );
  }

  update(
    id: TId,
    data: Partial<TTable["$inferInsert"]>,
  ): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        // Type safety: TTable is constrained to DatabaseTable, so updatedAt is guaranteed to exist
        const updateData = {
          ...data,
          updatedAt: new Date(),
        };
        const [result] = await this.db
          .update(this.getTable())
          // Type assertion needed: When TTable is a union type, Drizzle's .set()
          // can't narrow the type, but runtime behavior is correct
          // eslint-disable-next-line @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-explicit-any
          .set(updateData as any)
          .where(eq(this.getIdColumn(), id))
          .returning(this.getPublicFields());

        return result as TPublic | undefined;
      },
      catch: (error) =>
        new DatabaseError({
          message: `Failed to update ${this.getResourceName()}`,
          cause: error,
        }),
    }).pipe(
      Effect.flatMap((result) => {
        if (!result) {
          return Effect.fail(
            new NotFoundError({
              message: `${this.getResourceName()} with id ${String(id)} not found`,
              resource: this.getResourceName(),
            }),
          );
        }
        return Effect.succeed(result);
      }),
    );
  }

  delete(id: TId): Effect.Effect<void, NotFoundError | DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const table = this.getTable();
        const idColumn = this.getIdColumn();
        const [deleted] = await this.db
          .delete(table)
          .where(eq(idColumn, id))
          .returning({ id: idColumn });

        return deleted;
      },
      catch: (error) =>
        new DatabaseError({
          message: `Failed to delete ${this.getResourceName()}`,
          cause: error,
        }),
    }).pipe(
      Effect.flatMap((deleted) => {
        if (!deleted) {
          return Effect.fail(
            new NotFoundError({
              message: `${this.getResourceName()} with id ${String(id)} not found`,
              resource: this.getResourceName(),
            }),
          );
        }
        return Effect.succeed(undefined);
      }),
    );
  }

  findAll(): Effect.Effect<TPublic[], DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const table = this.getTable();
        const publicFields = this.getPublicFields();
        // Type assertion needed: Drizzle's .from() has complex conditional types
        // (TableLikeHasEmptySelection) that don't work well with generic table types.
        // Runtime behavior is correct - this is purely a TypeScript limitation.
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const results = await this.db.select(publicFields).from(table as any);

        return results as TPublic[];
      },
      catch: (error) =>
        new DatabaseError({
          message: `Failed to find all ${this.getResourceName()}s`,
          cause: error,
        }),
    });
  }
}

/**
 * Action types for permission checking
 */
export type PermissionAction = "read" | "update" | "delete";

/**
 * Abstract base class for services that require authentication.
 * Uses composition with an internal base service for raw CRUD operations.
 *
 * @template TPublic - The public-facing type (what gets returned)
 * @template TId - The type of the entity ID
 * @template TTable - The Drizzle table type
 * @template TInsert - The insert type for the table
 */
export abstract class BaseAuthenticatedService<
  TPublic,
  TId,
  TTable extends DatabaseTable,
  TInsert = TTable["$inferInsert"],
> {
  protected readonly db: PostgresJsDatabase<typeof schema>;
  protected abstract readonly baseService: BaseService<TPublic, TId, TTable>;

  constructor(db: PostgresJsDatabase<typeof schema>) {
    this.db = db;
  }

  protected abstract checkPermission(
    userId: string,
    action: PermissionAction,
    resourceId: TId,
  ): Effect.Effect<void, NotFoundError | PermissionDeniedError | DatabaseError>;

  abstract create(
    data: TInsert,
    userId: string,
  ): Effect.Effect<
    TPublic,
    AlreadyExistsError | PermissionDeniedError | DatabaseError
  >;

  abstract findAll(
    userId: string,
  ): Effect.Effect<TPublic[], PermissionDeniedError | DatabaseError>;

  // TODO: include in coverage once we have a service that doesn't override this
  /* v8 ignore start */
  findById(
    id: TId,
    userId: string,
  ): Effect.Effect<
    TPublic,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return this.checkPermission(userId, "read", id).pipe(
      Effect.andThen(this.baseService.findById(id)),
    );
  }
  /* v8 ignore end */

  update(
    id: TId,
    data: Partial<TInsert>,
    userId: string,
  ): Effect.Effect<
    TPublic,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return this.checkPermission(userId, "update", id).pipe(
      // eslint-disable-next-line @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-explicit-any
      Effect.andThen(this.baseService.update(id, data as any)),
    );
  }

  // TODO: include in coverage once we have a service that doesn't override this
  /* v8 ignore start */
  delete(
    id: TId,
    userId: string,
  ): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return this.checkPermission(userId, "delete", id).pipe(
      Effect.andThen(this.baseService.delete(id)),
    );
  }
  /* v8 ignore end */
}
