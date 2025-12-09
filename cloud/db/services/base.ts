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

  findById({
    id,
  }: {
    id: TId;
  }): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const result = yield* Effect.tryPromise({
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
      });

      if (!result) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `${this.getResourceName()} with id ${String(id)} not found`,
            resource: this.getResourceName(),
          }),
        );
      }
      return result;
    });
  }

  update({
    id,
    data,
  }: {
    id: TId;
    data: Partial<TTable["$inferInsert"]>;
  }): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const updated = yield* Effect.tryPromise({
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
      });

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `${this.getResourceName()} with id ${String(id)} not found`,
            resource: this.getResourceName(),
          }),
        );
      }
      return updated;
    });
  }

  delete({
    id,
  }: {
    id: TId;
  }): Effect.Effect<void, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const deleted = yield* Effect.tryPromise({
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
      });

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `${this.getResourceName()} with id ${String(id)} not found`,
            resource: this.getResourceName(),
          }),
        );
      }
    });
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
export type PermissionAction = "create" | "read" | "update" | "delete";

/**
 * Permission table mapping actions to allowed roles.
 * Each action maps to an array of roles that can perform that action.
 */
export type PermissionTable<TRole extends string> = Record<
  PermissionAction,
  readonly TRole[]
>;

/**
 * Abstract base class for services that require authentication.
 * Uses composition with an internal base service for raw CRUD operations.
 *
 * @template TPublic - The public-facing type (what gets returned)
 * @template TId - The type of the entity ID
 * @template TTable - The Drizzle table type
 * @template TInsert - The insert type for the table
 * @template TRole - The role type for permission checking
 */
export abstract class BaseAuthenticatedService<
  TPublic,
  TId,
  TTable extends DatabaseTable,
  TInsert = TTable["$inferInsert"],
  TRole extends string = string,
> {
  protected readonly db: PostgresJsDatabase<typeof schema>;
  protected readonly baseService: BaseService<TPublic, TId, TTable>;

  constructor(db: PostgresJsDatabase<typeof schema>) {
    this.db = db;
    this.baseService = this.initializeBaseService();
  }

  protected abstract initializeBaseService(): BaseService<TPublic, TId, TTable>;

  /**
   * Returns the permission table mapping actions to allowed roles.
   */
  protected abstract getPermissionTable(): PermissionTable<TRole>;

  /**
   * Returns the role of a user for a given entity.
   */
  abstract getRole(args: {
    id: string;
    userId: string;
  }): Effect.Effect<TRole, NotFoundError | DatabaseError>;

  /**
   * Verify that a role has permission to perform an action.
   */
  protected verifyPermission(
    role: TRole,
    action: PermissionAction,
  ): Effect.Effect<void, PermissionDeniedError> {
    const permissionTable = this.getPermissionTable();
    const allowedRoles = permissionTable[action];

    if (!allowedRoles.includes(role)) {
      return Effect.fail(
        new PermissionDeniedError({
          message: `You do not have permission to ${action} this ${this.baseService.resourceName}`,
          resource: this.baseService.resourceName,
        }),
      );
    }
    return Effect.succeed(undefined);
  }

  /**
   * Authorize a user to perform an action on an entity.
   */
  protected authorize({
    id,
    userId,
    action,
  }: {
    id: string;
    userId: string;
    action: PermissionAction;
  }): Effect.Effect<
    TRole,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const role = yield* this.getRole({ id, userId });
      yield* this.verifyPermission(role, action);
      return role;
    });
  }

  abstract create(args: {
    data: TInsert;
    userId: string;
  }): Effect.Effect<
    TPublic,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError
  >;

  abstract findAll(args: {
    userId: string;
  }): Effect.Effect<TPublic[], PermissionDeniedError | DatabaseError>;

  abstract findById(args: {
    id: TId;
    userId: string;
  }): Effect.Effect<
    TPublic,
    NotFoundError | PermissionDeniedError | DatabaseError
  >;

  abstract update(args: {
    id: TId;
    data: Partial<TInsert>;
    userId: string;
  }): Effect.Effect<
    TPublic,
    NotFoundError | PermissionDeniedError | DatabaseError
  >;

  abstract delete(args: {
    id: TId;
    userId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  >;
}
