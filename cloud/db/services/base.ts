import { Effect } from "effect";
import { eq } from "drizzle-orm";
import type { PgColumn } from "drizzle-orm/pg-core";
import { DatabaseError, NotFoundError } from "@/db/errors";
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

  /**
   * Get the table for this service
   */
  protected abstract getTable(): TTable;

  /**
   * Get the resource name for error messages (e.g., "user", "session")
   */
  protected abstract getResourceName(): string;

  /**
   * Get the selector for public fields to return
   * This should return a Drizzle select object that matches TPublic
   */
  protected abstract getPublicFields(): Record<string, PgColumn>;

  /**
   * Get the ID column from the table
   * With TTable constrained to DatabaseTable, we can access table.id directly
   */
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

  /**
   * Create a new entity
   */
  create(data: TTable["$inferInsert"]): Effect.Effect<TPublic, DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const table = this.getTable();
        const publicFields = this.getPublicFields();
        // Type assertion needed: When TTable is a union type, Drizzle's .values()
        // can't narrow the type, but runtime behavior is correct
        const [result] = await this.db
          .insert(table)
          // eslint-disable-next-line @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-explicit-any
          .values(data as any)
          .returning(publicFields);

        return result as TPublic;
      },
      catch: (error) =>
        new DatabaseError({
          message: `Failed to create ${this.getResourceName()}`,
          cause: error,
        }),
    });
  }

  /**
   * Find an entity by its ID
   */
  findById(id: TId): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const table = this.getTable();
        const idColumn = this.getIdColumn();
        const publicFields = this.getPublicFields();
        // Type assertion needed: Drizzle's .from() has complex conditional types
        // (TableLikeHasEmptySelection) that don't work well with generic table types.
        // Runtime behavior is correct - this is purely a TypeScript limitation.
        const [result] = await this.db
          .select(publicFields)
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          .from(table as any)
          .where(eq(idColumn, id))
          .limit(1);

        if (!result) {
          throw new NotFoundError({
            message: `${this.getResourceName()} with id ${String(id)} not found`,
            resource: this.getResourceName(),
          });
        }

        return result as TPublic;
      },
      catch: (error) => {
        if (error instanceof NotFoundError) {
          return error;
        }
        return new DatabaseError({
          message: `Failed to find ${this.getResourceName()}`,
          cause: error,
        });
      },
    });
  }

  /**
   * Update an entity by its ID
   */
  update(
    id: TId,
    data: Partial<TTable["$inferInsert"]>,
  ): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const table = this.getTable();
        const idColumn = this.getIdColumn();
        const publicFields = this.getPublicFields();
        // Construct update data with updatedAt timestamp
        // Type safety: TTable is constrained to DatabaseTable, so updatedAt is guaranteed to exist
        const updateData = {
          ...data,
          updatedAt: new Date(),
        };
        // Type assertion needed: When TTable is a union type, Drizzle's .set()
        // can't narrow the type, but runtime behavior is correct
        const [result] = await this.db
          .update(table)
          // eslint-disable-next-line @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-explicit-any
          .set(updateData as any)
          .where(eq(idColumn, id))
          .returning(publicFields);

        if (!result) {
          throw new NotFoundError({
            message: `${this.getResourceName()} with id ${String(id)} not found`,
            resource: this.getResourceName(),
          });
        }

        return result as TPublic;
      },
      catch: (error) => {
        if (error instanceof NotFoundError) {
          return error;
        }
        return new DatabaseError({
          message: `Failed to update ${this.getResourceName()}`,
          cause: error,
        });
      },
    });
  }

  /**
   * Delete an entity by its ID
   */
  delete(id: TId): Effect.Effect<void, NotFoundError | DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const table = this.getTable();
        const idColumn = this.getIdColumn();
        const [deleted] = await this.db
          .delete(table)
          .where(eq(idColumn, id))
          .returning({ id: idColumn });

        if (!deleted) {
          throw new NotFoundError({
            message: `${this.getResourceName()} with id ${String(id)} not found`,
            resource: this.getResourceName(),
          });
        }
      },
      catch: (error) => {
        if (error instanceof NotFoundError) {
          return error;
        }
        return new DatabaseError({
          message: `Failed to delete ${this.getResourceName()}`,
          cause: error,
        });
      },
    });
  }

  /**
   * Find all entities
   */
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
