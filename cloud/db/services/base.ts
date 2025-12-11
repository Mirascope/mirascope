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

// =============================================================================
// Path Parameter Utility Types
// =============================================================================

/**
 * Extracts parameter names from a path string.
 * @example
 * ParsePathParams<"users/:userId/sessions/:sessionId"> // "userId" | "sessionId"
 */
export type ParsePathParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ParsePathParams<Rest>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

/**
 * Converts path parameter names to an object type.
 * @example
 * PathParams<"users/:userId"> // { userId: string }
 * PathParams<"users/:userId/sessions/:sessionId"> // { userId: string; sessionId: string }
 */
export type PathParams<T extends string> = {
  [K in ParsePathParams<T>]: string;
};

/**
 * Extracts the last parameter name from a path (the resource's own ID).
 * @example
 * LastPathParam<"users/:userId/sessions/:sessionId"> // "sessionId"
 * LastPathParam<"users/:userId"> // "userId"
 */
export type LastPathParam<T extends string> =
  T extends `${string}/${infer Rest}`
    ? LastPathParam<Rest>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

/**
 * Parent path params (all except the resource's own ID).
 * Used for create operations where the resource ID doesn't exist yet.
 * @example
 * ParentParams<"users/:userId/sessions/:sessionId"> // { userId: string }
 * ParentParams<"users/:userId"> // {}
 */
export type ParentParams<T extends string> = Omit<
  PathParams<T>,
  LastPathParam<T>
>;

/**
 * Helper type to check if ParentParams is empty (i.e., top-level resource).
 */
export type HasParentParams<T extends string> =
  keyof ParentParams<T> extends never ? false : true;

/**
 * Create params type - includes parent params and data.
 * For top-level resources, this is just { data }.
 * For nested resources, this includes parent path params.
 */
export type CreateParams<T extends string, TData> =
  HasParentParams<T> extends true
    ? ParentParams<T> & { data: TData }
    : { data: TData };

// =============================================================================
// Base Service
// =============================================================================

/**
 * Base service class for CRUD operations on database entities.
 * Provides common database access and transaction support with REST-style path parameters.
 *
 * @template TPublic - The public-facing type (what gets returned)
 * @template TPath - The REST path pattern (e.g., "users/:userId" or "users/:userId/sessions/:sessionId")
 * @template TTable - The Drizzle table type (constrained to actual database tables)
 */
export abstract class BaseService<
  TPublic,
  TPath extends string,
  TTable extends DatabaseTable = DatabaseTable,
> {
  protected readonly db: PostgresJsDatabase<typeof schema>;

  constructor(db: PostgresJsDatabase<typeof schema>) {
    this.db = db;
  }

  protected abstract getTable(): TTable;
  protected abstract getResourceName(): string;
  protected abstract getPublicFields(): Record<string, PgColumn>;

  /**
   * Returns the name of the ID parameter for this resource.
   * @example "userId" for users, "sessionId" for sessions
   */
  protected abstract getIdParamName(): LastPathParam<TPath>;

  get resourceName(): string {
    return this.getResourceName();
  }

  protected getIdColumn(): PgColumn {
    const table = this.getTable();
    return table.id;
  }

  /**
   * Extracts the resource's own ID from path params.
   */
  protected getIdFromParams(params: PathParams<TPath>): string {
    const idParamName = this.getIdParamName();
    // Type assertion needed: LastPathParam<TPath> is always a key of PathParams<TPath>
    // but TypeScript can't prove this at the type level due to the recursive nature
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    return (params as any)[idParamName] as string;
  }

  create(
    params: CreateParams<TPath, TTable["$inferInsert"]>,
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
          .values(params.data as any)
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

  findById(
    params: PathParams<TPath>,
  ): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const id = this.getIdFromParams(params);
      const idParamName = this.getIdParamName();

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
            message: `${this.getResourceName()} with ${idParamName} ${id} not found`,
            resource: this.getResourceName(),
          }),
        );
      }
      return result;
    });
  }

  update(
    params: PathParams<TPath> & { data: Partial<TTable["$inferInsert"]> },
  ): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const id = this.getIdFromParams(params);
      const idParamName = this.getIdParamName();

      const updated = yield* Effect.tryPromise({
        try: async () => {
          // Type safety: TTable is constrained to DatabaseTable, so updatedAt is guaranteed to exist
          const updateData = {
            ...params.data,
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
            message: `${this.getResourceName()} with ${idParamName} ${id} not found`,
            resource: this.getResourceName(),
          }),
        );
      }
      return updated;
    });
  }

  delete(
    params: PathParams<TPath>,
  ): Effect.Effect<void, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const id = this.getIdFromParams(params);
      const idParamName = this.getIdParamName();

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
            message: `${this.getResourceName()} with ${idParamName} ${id} not found`,
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
 * @template TPath - The REST path pattern (e.g., "organizations/:organizationId")
 * @template TTable - The Drizzle table type
 * @template TInsert - The insert type for the table
 * @template TRole - The role type for permission checking
 */
export abstract class BaseAuthenticatedService<
  TPublic,
  TPath extends string,
  TTable extends DatabaseTable,
  TInsert = TTable["$inferInsert"],
  TRole extends string = string,
> {
  protected readonly db: PostgresJsDatabase<typeof schema>;
  protected readonly baseService: BaseService<TPublic, TPath, TTable>;

  constructor(db: PostgresJsDatabase<typeof schema>) {
    this.db = db;
    this.baseService = this.initializeBaseService();
  }

  protected abstract initializeBaseService(): BaseService<
    TPublic,
    TPath,
    TTable
  >;

  /**
   * Returns the permission table mapping actions to allowed roles.
   */
  protected abstract getPermissionTable(): PermissionTable<TRole>;

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

  abstract create(args: {
    userId: string;
    data: TInsert;
  }): Effect.Effect<
    TPublic,
    AlreadyExistsError | PermissionDeniedError | DatabaseError
  >;

  abstract findAll(args: {
    userId: string;
  }): Effect.Effect<TPublic[], PermissionDeniedError | DatabaseError>;

  abstract findById(
    args: { userId: string } & PathParams<TPath>,
  ): Effect.Effect<
    TPublic,
    NotFoundError | PermissionDeniedError | DatabaseError
  >;

  abstract update(
    args: { userId: string } & PathParams<TPath> & { data: Partial<TInsert> },
  ): Effect.Effect<
    TPublic,
    NotFoundError | PermissionDeniedError | DatabaseError
  >;

  abstract delete(
    args: { userId: string } & PathParams<TPath>,
  ): Effect.Effect<void, NotFoundError | PermissionDeniedError | DatabaseError>;
}
