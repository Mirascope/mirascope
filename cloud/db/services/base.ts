/**
 * @fileoverview Base service classes for database operations.
 *
 * This module provides two abstract base classes:
 *
 * 1. `BaseService` - Low-level CRUD operations with REST-style path parameter support.
 *    Handles database queries, error mapping, and parent/child resource scoping.
 *
 * 2. `BaseAuthenticatedService` - Wraps BaseService(s) with authentication and
 *    role-based permission checking. Composes one or more BaseServices internally.
 *
 * ## Path Parameter System
 *
 * Services use REST-style path patterns to define resource hierarchies:
 * - `"users/:userId"` - Top-level resource
 * - `"users/:userId/sessions/:sessionId"` - Nested resource
 *
 * The path pattern determines:
 * - Which parameters are required for each operation
 * - How queries are scoped (nested resources filter by parent ID)
 * - Type-safe parameter requirements at compile time
 *
 * @example
 * ```ts
 * // Top-level resource
 * class UserService extends BaseService<User, "users/:userId", typeof users> { ... }
 * userService.findAll();  // No params needed
 * userService.findById({ userId: "123" });
 *
 * // Nested resource
 * class SessionService extends BaseService<Session, "users/:userId/sessions/:sessionId", typeof sessions> { ... }
 * sessionService.findAll({ userId: "123" });  // Parent param required
 * sessionService.findById({ userId: "123", sessionId: "456" });
 * ```
 */

import { Effect } from "effect";
import { and, eq } from "drizzle-orm";
import type { SQL } from "drizzle-orm";
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
//
// These types extract and transform REST-style path patterns into TypeScript
// types for compile-time safety. The path pattern "users/:userId/sessions/:sessionId"
// becomes the type { userId: string; sessionId: string }.

/**
 * Extracts parameter names from a REST-style path pattern.
 *
 * Recursively parses path segments to find all `:paramName` patterns.
 *
 * @example
 * ```ts
 * type Params = ParsePathParams<"users/:userId/sessions/:sessionId">;
 * // Result: "userId" | "sessionId"
 * ```
 */
export type ParsePathParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ParsePathParams<Rest>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

/**
 * Converts a path pattern to an object type with string values.
 *
 * @example
 * ```ts
 * type Params = PathParams<"users/:userId/sessions/:sessionId">;
 * // Result: { userId: string; sessionId: string }
 * ```
 */
export type PathParams<T extends string> = {
  [K in ParsePathParams<T>]: string;
};

/**
 * Extracts the last (rightmost) parameter name from a path.
 *
 * This represents the resource's own ID in nested paths.
 *
 * @example
 * ```ts
 * type Id = LastPathParam<"users/:userId/sessions/:sessionId">;
 * // Result: "sessionId"
 *
 * type Id = LastPathParam<"users/:userId">;
 * // Result: "userId"
 * ```
 */
export type LastPathParam<T extends string> =
  T extends `${string}/${infer Rest}`
    ? LastPathParam<Rest>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

/**
 * Extracts parent path parameters (excludes the resource's own ID).
 *
 * Used for operations that scope by parent but don't reference the resource ID,
 * such as `findAll` on nested resources or `create` before an ID exists.
 *
 * @example
 * ```ts
 * type Parents = ParentParams<"users/:userId/sessions/:sessionId">;
 * // Result: { userId: string }
 *
 * type Parents = ParentParams<"users/:userId">;
 * // Result: {} (empty - no parent)
 * ```
 */
export type ParentParams<T extends string> = Omit<
  PathParams<T>,
  LastPathParam<T>
>;

/**
 * Boolean type indicating whether a path has parent parameters.
 *
 * - `true` for nested resources (e.g., sessions under users)
 * - `false` for top-level resources (e.g., users)
 *
 * Used to conditionally require parent params in method signatures.
 */
export type HasParentParams<T extends string> =
  keyof ParentParams<T> extends never ? false : true;

/**
 * Parameter type for authorization operations.
 *
 * - Top-level resources: Uses full PathParams (e.g., { organizationId: string })
 * - Nested resources: Uses ParentParams (e.g., { organizationId: string })
 *
 * This ensures authorization always has access to the "scope" identifier needed
 * to determine the user's role, regardless of resource nesting level.
 *
 * @example
 * ```ts
 * // OrganizationService: path = "organizations/:organizationId"
 * // AuthorizationParams = { organizationId: string }
 *
 * // OrganizationMembershipService: path = "organizations/:organizationId/users/:targetUserId"
 * // AuthorizationParams = { organizationId: string }
 * ```
 */
export type AuthorizationParams<T extends string> =
  HasParentParams<T> extends true ? ParentParams<T> : PathParams<T>;

/**
 * Parameter type for create operations.
 *
 * - Top-level resources: `{ data: TData }`
 * - Nested resources: `{ parentId: string, ..., data: TData }`
 *
 * Note: Parent params should also be included in `data` for database insertion.
 */
export type CreateParams<T extends string, TData> =
  HasParentParams<T> extends true
    ? ParentParams<T> & { data: TData }
    : { data: TData };

// =============================================================================
// Base Service
// =============================================================================

/**
 * Abstract base class for low-level CRUD operations on database entities.
 *
 * Provides type-safe database operations with automatic:
 * - Parent/child resource scoping via path parameters
 * - Error mapping to domain-specific error types
 * - Public field projection (only returns specified columns)
 *
 * ## Implementing a BaseService
 *
 * Subclasses must implement four abstract methods:
 * - `getTable()` - Returns the Drizzle table object
 * - `getResourceName()` - Human-readable name for error messages
 * - `getPublicFields()` - Columns to include in query results
 * - `getIdParamName()` - The path parameter name for this resource's ID
 *
 * ## Path Parameter Convention
 *
 * Parent path parameters (e.g., `userId` in `users/:userId/sessions/:sessionId`)
 * must correspond to columns of the same name on the table. This enables
 * automatic query scoping for nested resources.
 *
 * @template TPublic - The public-facing return type
 * @template TPath - REST path pattern (e.g., `"users/:userId"`)
 * @template TTable - Drizzle table type (must extend DatabaseTable)
 *
 * @example
 * ```ts
 * class SessionBaseService extends BaseService<
 *   PublicSession,
 *   "users/:userId/sessions/:sessionId",
 *   typeof sessions
 * > {
 *   protected getTable() { return sessions; }
 *   protected getResourceName() { return "session"; }
 *   protected getIdParamName() { return "sessionId" as const; }
 *   protected getPublicFields() {
 *     return { id: sessions.id, createdAt: sessions.createdAt };
 *   }
 * }
 * ```
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

  // ---------------------------------------------------------------------------
  // Abstract Methods (must be implemented by subclasses)
  // ---------------------------------------------------------------------------

  /** Returns the Drizzle table object for this resource. */
  protected abstract getTable(): TTable;

  /** Returns a human-readable resource name for error messages (e.g., "session"). */
  protected abstract getResourceName(): string;

  /** Returns the columns to include in query results. */
  protected abstract getPublicFields(): Record<string, PgColumn>;

  /** Returns the path parameter name for this resource's ID (e.g., "sessionId"). */
  protected abstract getIdParamName(): LastPathParam<TPath>;

  // ---------------------------------------------------------------------------
  // Public Accessors
  // ---------------------------------------------------------------------------

  /** Public accessor for the resource name (used by authenticated services). */
  get resourceName(): string {
    return this.getResourceName();
  }

  // ---------------------------------------------------------------------------
  // Protected Helpers
  // ---------------------------------------------------------------------------

  /**
   * Returns the primary key column. Override if the table doesn't use `id`.
   *
   * Default implementation assumes the table has a column named `id`.
   * Tables with composite primary keys or non-standard ID columns (e.g., `memberId`)
   * should override this method.
   */
  protected getIdColumn(): PgColumn {
    const table = this.getTable();
    // Type assertion: Most tables have `id`, subclasses override for exceptions
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    return (table as any).id as PgColumn;
  }

  /** Extracts the resource's own ID value from path params. */
  protected getIdFromParams(params: PathParams<TPath>): string {
    const idParamName = this.getIdParamName();
    // Type assertion: LastPathParam<TPath> is always a key of PathParams<TPath>,
    // but TypeScript can't prove this due to the recursive type definition.
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    return (params as any)[idParamName] as string;
  }

  /**
   * Builds a WHERE clause from parent path params only.
   *
   * Used by `findAll` to scope queries to a parent resource without
   * filtering by the resource's own ID.
   *
   * @returns SQL condition, or `undefined` if no parent params exist
   */
  protected getParentScopedWhere(params: ParentParams<TPath>): SQL | undefined {
    const table = this.getTable() as unknown as Record<string, PgColumn>;
    const conditions: SQL[] = [];

    for (const [key, value] of Object.entries(params)) {
      if (typeof value !== "string") continue;

      const column = table[key];
      if (!column) {
        throw new Error(
          `BaseService misconfiguration: table '${this.getResourceName()}' is missing column '${key}' for path param scoping. ` +
            `Ensure the column name matches the path parameter name.`,
        );
      }

      conditions.push(eq(column, value));
    }

    if (conditions.length === 0) return undefined;
    /* v8 ignore next 1 -- multiple parent params branch covered when we add nested resources (e.g., projects) */
    return conditions.length > 1 ? and(...conditions)! : conditions[0];
  }

  /**
   * Builds a WHERE clause from all path params (resource ID + parent params).
   *
   * Used by `findById`, `update`, and `delete` to uniquely identify a resource
   * while also verifying parent ownership.
   *
   * @example
   * ```ts
   * // Path: "users/:userId/sessions/:sessionId"
   * // Params: { userId: "u1", sessionId: "s1" }
   * // Result: WHERE sessions.id = 's1' AND sessions.userId = 'u1'
   * ```
   */
  protected getScopedWhere(params: PathParams<TPath>): SQL {
    const idParamName = this.getIdParamName() as unknown as string;

    // Build condition for the resource's own ID
    const id = this.getIdFromParams(params);
    const idCondition = eq(this.getIdColumn(), id);

    // Build conditions for parent params
    const parentParams = Object.fromEntries(
      Object.entries(params).filter(([key]) => key !== idParamName),
    ) as ParentParams<TPath>;
    const parentWhere = this.getParentScopedWhere(parentParams);

    return parentWhere ? and(idCondition, parentWhere)! : idCondition;
  }

  // ---------------------------------------------------------------------------
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new resource in the database.
   *
   * @param params.data - The data to insert (must include parent foreign keys for nested resources)
   * @returns The created resource with public fields only
   * @throws AlreadyExistsError - If a unique constraint is violated
   * @throws DatabaseError - If the database operation fails
   */
  create(
    params: CreateParams<TPath, TTable["$inferInsert"]>,
  ): Effect.Effect<TPublic, AlreadyExistsError | DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const table = this.getTable();
        const publicFields = this.getPublicFields();
        const [result] = await this.db
          .insert(table)
          // Type assertion: Drizzle's .values() can't narrow union table types
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

  /**
   * Retrieves all resources, scoped by parent params for nested resources.
   *
   * The method signature adapts based on the path pattern:
   * - Top-level resources (e.g., `users/:userId`): No params required
   * - Nested resources (e.g., `users/:userId/sessions/:sessionId`): Parent params required
   *
   * @param params - Parent path params (required for nested resources)
   * @returns Array of resources with public fields only
   * @throws DatabaseError - If the database operation fails
   *
   * @example
   * ```ts
   * // Top-level: no params
   * userService.findAll();
   *
   * // Nested: parent params required
   * sessionService.findAll({ userId: "123" });
   * ```
   */
  findAll(
    ...args: HasParentParams<TPath> extends true
      ? [params: ParentParams<TPath>]
      : [params?: undefined]
  ): Effect.Effect<TPublic[], DatabaseError> {
    const params = args[0];

    return Effect.tryPromise({
      try: async () => {
        const table = this.getTable();
        const publicFields = this.getPublicFields();
        // Type assertion: Drizzle's .from() has complex conditional types that
        // don't work well with generic table types
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const query = this.db.select(publicFields).from(table as any);

        const whereClause = params
          ? this.getParentScopedWhere(params)
          : undefined;
        const results = whereClause
          ? await query.where(whereClause)
          : await query;

        return results as TPublic[];
      },
      catch: (error) =>
        new DatabaseError({
          message: `Failed to find all ${this.getResourceName()}s`,
          cause: error,
        }),
    });
  }

  /**
   * Retrieves a single resource by its ID.
   *
   * For nested resources, also verifies parent ownership via path params.
   *
   * @param params - All path params (resource ID + parent IDs)
   * @returns The resource with public fields only
   * @throws NotFoundError - If the resource doesn't exist or parent mismatch
   * @throws DatabaseError - If the database operation fails
   */
  findById(
    params: PathParams<TPath>,
  ): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const id = this.getIdFromParams(params);
      const idParamName = this.getIdParamName();
      const scopedWhere = this.getScopedWhere(params);

      const result = yield* Effect.tryPromise({
        try: async () => {
          const [result] = await this.db
            .select(this.getPublicFields())
            // Type assertion: Drizzle's .from() complex conditional types
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            .from(this.getTable() as any)
            .where(scopedWhere)
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

  /**
   * Updates a resource by its ID.
   *
   * Automatically sets `updatedAt` to the current timestamp.
   * For nested resources, also verifies parent ownership via path params.
   *
   * @param params - Path params + data to update
   * @returns The updated resource with public fields only
   * @throws NotFoundError - If the resource doesn't exist or parent mismatch
   * @throws DatabaseError - If the database operation fails
   */
  update(
    params: PathParams<TPath> & { data: Partial<TTable["$inferInsert"]> },
  ): Effect.Effect<TPublic, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const pathParams = params as unknown as PathParams<TPath>;
      const id = this.getIdFromParams(pathParams);
      const idParamName = this.getIdParamName();
      const scopedWhere = this.getScopedWhere(pathParams);

      const updated = yield* Effect.tryPromise({
        try: async () => {
          const updateData = {
            ...params.data,
            updatedAt: new Date(),
          };
          const [result] = await this.db
            .update(this.getTable())
            // Type assertion: Drizzle's .set() can't narrow union table types
            // eslint-disable-next-line @typescript-eslint/no-unsafe-argument, @typescript-eslint/no-explicit-any
            .set(updateData as any)
            .where(scopedWhere)
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

  /**
   * Deletes a resource by its ID.
   *
   * For nested resources, also verifies parent ownership via path params.
   *
   * @param params - All path params (resource ID + parent IDs)
   * @throws NotFoundError - If the resource doesn't exist or parent mismatch
   * @throws DatabaseError - If the database operation fails
   */
  delete(
    params: PathParams<TPath>,
  ): Effect.Effect<void, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const id = this.getIdFromParams(params);
      const idParamName = this.getIdParamName();
      const scopedWhere = this.getScopedWhere(params);

      const deleted = yield* Effect.tryPromise({
        try: async () => {
          const table = this.getTable();
          const idColumn = this.getIdColumn();
          const [deleted] = await this.db
            .delete(table)
            .where(scopedWhere)
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
}

// =============================================================================
// Authenticated Service
// =============================================================================

/** CRUD action types used for permission checking. */
export type PermissionAction = "create" | "read" | "update" | "delete";

/**
 * Maps each CRUD action to the roles that can perform it.
 *
 * @example
 * ```ts
 * const permissions: PermissionTable<"OWNER" | "ADMIN" | "DEVELOPER" | "VIEWER"> = {
 *   create: ["OWNER", "ADMIN"],
 *   read: ["OWNER", "ADMIN", "DEVELOPER", "VIEWER"],
 *   update: ["OWNER", "ADMIN"],
 *   delete: ["OWNER"],
 * };
 * ```
 */
export type PermissionTable<TRole extends string> = Record<
  PermissionAction,
  readonly TRole[]
>;

/**
 * Abstract base class for services requiring authentication and authorization.
 *
 * This class wraps a single `BaseService` instance and adds:
 * - Role-based permission checking before operations
 * - Automatic authorization via the `authorize({ userId, action, ...pathParams })` helper
 *
 * ## Architecture
 *
 * ```
 * ┌────────────────────────────────────────────────────────┐
 * │              BaseAuthenticatedService                  │
 * │  ┌──────────────────────────────────────────────────┐  │
 * │  │   baseService: BaseService<...>                  │  │
 * │  └──────────────────────────────────────────────────┘  │
 * │                                                        │
 * │  + getRole({ userId, ...pathParams })                  │
 * │  + getPermissionTable()                                │
 * │  + authorize({ userId, action, ...pathParams })        │
 * └────────────────────────────────────────────────────────┘
 * ```
 *
 * ## Implementing an Authenticated Service
 *
 * Subclasses must implement:
 * - `initializeBaseService()` - Create and return the BaseService instance
 * - `getPermissionTable()` - Define which roles can perform which actions
 * - `getRole({ userId, ...pathParams })` - Determine the authenticated user's role for a resource
 * - All abstract CRUD methods (create, findAll, findById, update, delete)
 *
 * @template TPublic - The public-facing type (what gets returned)
 * @template TPath - The REST path pattern (e.g., "organizations/:organizationId")
 * @template TTable - The Drizzle table type
 * @template TInsert - The insert type for the table
 * @template TRole - The role type for permission checking
 *
 * @example
 * ```ts
 * class OrganizationService extends BaseAuthenticatedService<
 *   PublicOrg, "orgs/:orgId", typeof orgs, NewOrg, Role
 * > {
 *   protected initializeBaseService() {
 *     return new OrganizationBaseService(this.db);
 *   }
 *
 *   protected getPermissionTable() {
 *     return {
 *       create: ["OWNER"],
 *       read: ["OWNER", "ADMIN", "DEVELOPER", "VIEWER"],
 *       update: ["OWNER", "ADMIN"],
 *       delete: ["OWNER"],
 *     };
 *   }
 *
 *   getRole({ userId, orgId }) {
 *     // Query membership table to get user's role
 *   }
 * }
 * ```
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

  // ---------------------------------------------------------------------------
  // Abstract Methods (must be implemented by subclasses)
  // ---------------------------------------------------------------------------

  /**
   * Creates and returns the base BaseService instance used by this service.
   */
  protected abstract initializeBaseService(): BaseService<
    TPublic,
    TPath,
    TTable
  >;

  /**
   * Returns the permission table defining which roles can perform which actions.
   */
  protected abstract getPermissionTable(): PermissionTable<TRole>;

  /**
   * Determines the authenticated user's role for the given resource.
   *
   * @param args.userId - The authenticated user's ID
   * @param args.[pathParams] - Path parameters identifying the authorization scope
   * @returns The user's role
   * @throws NotFoundError - If the user has no role (not a member)
   */
  protected abstract getRole(
    args: { userId: string } & AuthorizationParams<TPath>,
  ): Effect.Effect<TRole, NotFoundError | DatabaseError>;

  // ---------------------------------------------------------------------------
  // Authorization Helpers
  // ---------------------------------------------------------------------------

  /**
   * Verifies that a role has permission to perform an action.
   *
   * @param role - The user's role
   * @param action - The action to perform
   * @throws PermissionDeniedError - If the role cannot perform the action
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
   * Authorizes an action by checking the user's role and permissions.
   *
   * Combines `getRole({ userId, ...pathParams })` and `verifyPermission(role, action)` into a single call.
   * Returns the user's role on success (useful for conditional logic).
   *
   * @param args.userId - The authenticated user's ID
   * @param args.action - The action to authorize
   * @param args.[pathParams] - Path parameters identifying the resource
   * @returns The user's role (if authorized)
   * @throws NotFoundError - If the user has no role for this resource
   * @throws PermissionDeniedError - If the role cannot perform the action
   *
   * @example
   * ```ts
   * const role = yield* this.authorize({
   *   userId,
   *   organizationId,
   *   action: "update",
   * });
   * // User is authorized - role contains their actual role
   * ```
   */
  protected authorize(
    args: {
      userId: string;
      action: PermissionAction;
    } & AuthorizationParams<TPath>,
  ): Effect.Effect<
    TRole,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const { userId, action, ...pathParams } = args;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-argument
      const role = yield* this.getRole({ userId, ...(pathParams as any) });
      yield* this.verifyPermission(role, action);
      return role;
    });
  }

  // ---------------------------------------------------------------------------
  // Abstract CRUD Methods (must be implemented by subclasses)
  // ---------------------------------------------------------------------------

  /**
   * Creates a new resource (with authorization).
   *
   * For nested resources, parent path params are required and are authoritative.
   * Implementations should overwrite any conflicting values in `data` with path params
   * to prevent injection attacks.
   *
   * Subclasses should call `authorize({ userId, action, ...pathParams })` before delegating to `baseService.create()`.
   */
  abstract create(
    args: { userId: string } & (HasParentParams<TPath> extends true
      ? ParentParams<TPath>
      : unknown) & { data: TInsert },
  ): Effect.Effect<
    TPublic,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError
  >;

  /**
   * Retrieves all resources accessible to the user (with authorization).
   *
   * Subclasses typically filter by membership or ownership.
   */
  abstract findAll(
    args: { userId: string } & (HasParentParams<TPath> extends true
      ? ParentParams<TPath>
      : unknown),
  ): Effect.Effect<
    TPublic[],
    NotFoundError | PermissionDeniedError | DatabaseError
  >;

  /**
   * Retrieves a single resource by ID (with authorization).
   *
   * Subclasses should call `authorize({ userId, action, ...pathParams })` before delegating to `baseService.findById()`.
   */
  abstract findById(
    args: { userId: string } & PathParams<TPath>,
  ): Effect.Effect<
    TPublic,
    NotFoundError | PermissionDeniedError | DatabaseError
  >;

  /**
   * Updates a resource by ID (with authorization).
   *
   * Subclasses should call `authorize({ userId, action, ...pathParams })` before delegating to `baseService.update()`.
   */
  abstract update(
    args: { userId: string } & PathParams<TPath> & { data: Partial<TInsert> },
  ): Effect.Effect<
    TPublic,
    NotFoundError | PermissionDeniedError | DatabaseError
  >;

  /**
   * Deletes a resource by ID (with authorization).
   *
   * Subclasses should call `authorize({ userId, action, ...pathParams })` before delegating to `baseService.delete()`.
   */
  abstract delete(
    args: { userId: string } & PathParams<TPath>,
  ): Effect.Effect<void, NotFoundError | PermissionDeniedError | DatabaseError>;
}
