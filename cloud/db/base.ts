/**
 * @fileoverview Base Effect service classes for database operations.
 *
 * This module provides the abstract `BaseEffectService` class which defines
 * the CRUD interface using REST-style path parameters for type-safe routing.
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
 * ## Live Services
 *
 * Service methods return `Effect<T, E, DrizzleORM>` - they require the DrizzleORM
 * client. The `makeReady` helper wraps services to provide the client, producing
 * `Live<T>` where methods return `Effect<T, E>` with no requirements.
 *
 * @example
 * ```ts
 * class Users extends BaseEffectService<PublicUser, "users/:userId", NewUser, UpdateUser> {
 *   // Implement abstract methods...
 * }
 *
 * // In Database:
 * const client = yield* DrizzleORM;
 * return {
 *   users: makeReady(client, new Users()),
 * };
 * ```
 */

import { Effect } from "effect";
import { DrizzleORM } from "@/db/client";
import { Payments } from "@/payments";
import {
  type AlreadyExistsError,
  type DatabaseError,
  type DeletedUserError,
  type ImmutableResourceError,
  type NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
  StripeError,
  SubscriptionPastDueError,
} from "@/errors";

// =============================================================================
// Path Parameter Utility Types
// =============================================================================

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
 */
export type HasParentParams<T extends string> =
  keyof ParentParams<T> extends never ? false : true;

// =============================================================================
// Base Effect Service
// =============================================================================

/**
 * Abstract base class for Effect-native CRUD services.
 *
 * Services extend this class and implement all abstract methods using
 * `yield* DrizzleORM` for database operations. The DrizzleORM requirement
 * is then satisfied at the Database layer via `madeReady`.
 *
 * ## Type Parameters
 *
 * @template TPublic - The public type returned by queries (projected columns)
 * @template TPath - REST-style path pattern (e.g., "users/:userId")
 * @template TInsert - The type for create operations (usually table's insert type)
 * @template TUpdate - The type for update operations (subset of TInsert)
 *
 * ## Path Parameter Convention
 *
 * The path pattern determines method signatures:
 * - Top-level (`"users/:userId"`): `findAll()` needs no params
 * - Nested (`"orgs/:orgId/users/:userId"`): `findAll({ orgId })` needs parent params
 *
 * @example
 * ```ts
 * class Users extends BaseEffectService<
 *   PublicUser,
 *   "users/:userId",
 *   NewUser,
 *   UpdateUser
 * > {
 *   create({ data }) { ... }
 *   findAll() { ... }
 *   findById({ userId }) { ... }
 *   update({ userId, data }) { ... }
 *   delete({ userId }) { ... }
 * }
 * ```
 */
export abstract class BaseEffectService<
  TPublic,
  TPath extends string,
  TInsert,
  TUpdate = Partial<TInsert>,
> {
  /**
   * Creates a new resource.
   *
   * For nested resources, parent path parameters are required alongside data.
   *
   * @param args.data - The data to insert
   * @param args.[parentParams] - Parent path parameters for nested resources
   * @returns The created resource
   * @throws AlreadyExistsError - If a unique constraint is violated
   * @throws DatabaseError - If the database operation fails
   */
  abstract create(
    args: HasParentParams<TPath> extends true
      ? ParentParams<TPath> & { data: TInsert }
      : { data: TInsert },
  ): Effect.Effect<TPublic, AlreadyExistsError | DatabaseError, DrizzleORM>;

  /**
   * Retrieves all resources, optionally scoped by parent.
   *
   * For nested resources, parent path parameters are required to scope the query.
   *
   * @param args - Parent path parameters for nested resources (optional for top-level)
   * @returns Array of all matching resources
   * @throws DatabaseError - If the database operation fails
   */
  abstract findAll(
    args?: HasParentParams<TPath> extends true ? ParentParams<TPath> : void,
  ): Effect.Effect<TPublic[], DatabaseError, DrizzleORM>;

  /**
   * Retrieves a single resource by its path parameters.
   *
   * @param args - All path parameters including the resource ID
   * @returns The found resource
   * @throws NotFoundError - If the resource doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  abstract findById(
    args: PathParams<TPath>,
  ): Effect.Effect<TPublic, NotFoundError | DatabaseError, DrizzleORM>;

  /**
   * Updates a resource by its path parameters.
   *
   * @param args - Path parameters plus the data to update
   * @returns The updated resource
   * @throws NotFoundError - If the resource doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  abstract update(
    args: PathParams<TPath> & { data: TUpdate },
  ): Effect.Effect<TPublic, NotFoundError | DatabaseError, DrizzleORM>;

  /**
   * Deletes a resource by its path parameters.
   *
   * @param args - All path parameters including the resource ID
   * @throws NotFoundError - If the resource doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  abstract delete(
    args: PathParams<TPath>,
  ): Effect.Effect<void, NotFoundError | DatabaseError, DrizzleORM>;
}

// =============================================================================
// Authenticated Effect Service
// =============================================================================

/** CRUD action types used for permission checking. */
export type PermissionAction = "create" | "read" | "update" | "delete";

/**
 * Maps each CRUD action to the roles that can perform it.
 *
 * @example
 * ```ts
 * const permissions: PermissionTable<"OWNER" | "ADMIN" | "MEMBER"> = {
 *   create: ["OWNER", "ADMIN"],
 *   read: ["OWNER", "ADMIN", "MEMBER"],
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
 * Parameter type for authorization operations.
 *
 * Uses the full PathParams to ensure authorization always has access to the
 * scope identifier needed to determine the user's role.
 *
 * @example
 * ```ts
 * // OrganizationService: path = "organizations/:organizationId"
 * // AuthorizationParams = { organizationId: string }
 *
 * // OrganizationMembershipService: path = "organizations/:organizationId/members/:memberId"
 * // AuthorizationParams = { organizationId: string; memberId: string }
 * ```
 */
export type AuthorizationParams<T extends string> = PathParams<T>;

/**
 * Abstract base class for Effect-native services requiring authentication and authorization.
 *
 * This class adds role-based permission checking to the CRUD interface:
 * - `getRole({ userId, ...pathParams })` - Determine the user's role for a resource
 * - `getPermissionTable()` - Define which roles can perform which actions
 * - `authorize({ userId, action, ...pathParams })` - Combined role check + permission verification
 *
 * ## Architecture
 *
 * ```
 * ┌──────────────────────────────────────────────────────────┐
 * │          BaseAuthenticatedEffectService                  │
 * │                                                          │
 * │  Abstract Methods:                                       │
 * │  + getRole({ userId, ...pathParams })        [abstract]  │
 * │  + getPermissionTable()                      [abstract]  │
 * │  + getResourceName()                         [abstract]  │
 * │                                                          │
 * │  Authorization Helpers:                                  │
 * │  + verifyPermission(role, action)            [provided]  │
 * │  + authorize({ userId, action, ...path })    [provided]  │
 * │                                                          │
 * │  CRUD (abstract methods):                                │
 * │  + create({ userId, data, ...parentParams }) [abstract]  │
 * │  + findAll({ userId, ...parentParams })      [abstract]  │
 * │  + findById({ userId, ...pathParams })       [abstract]  │
 * │  + update({ userId, data, ...pathParams })   [abstract]  │
 * │  + delete({ userId, ...pathParams })         [abstract]  │
 * └──────────────────────────────────────────────────────────┘
 * ```
 *
 * ## Implementing an Authenticated Service
 *
 * Subclasses must implement:
 * - `getResourceName()` - Human-readable name for error messages
 * - `getPermissionTable()` - Define which roles can perform which actions
 * - `getRole({ userId, ...pathParams })` - Determine the user's role
 * - All CRUD methods (create, findAll, findById, update, delete)
 *
 * @template TPublic - The public-facing type returned by queries
 * @template TPath - REST path pattern (e.g., "organizations/:organizationId")
 * @template TInsert - The type for create operations
 * @template TUpdate - The type for update operations (defaults to Partial<TInsert>)
 * @template TRole - The role type for permission checking (e.g., "OWNER" | "ADMIN" | "MEMBER")
 * @template TExtraR - Additional service requirements beyond DrizzleORM (defaults to never)
 *
 * @example
 * ```ts
 * class Organizations extends BaseAuthenticatedEffectService<
 *   PublicOrg,
 *   "organizations/:organizationId",
 *   NewOrg,
 *   Partial<NewOrg>,
 *   OrganizationRole
 * > {
 *   protected getResourceName() { return "organization"; }
 *
 *   protected getPermissionTable() {
 *     return {
 *       create: ["OWNER"],
 *       read: ["OWNER", "ADMIN", "MEMBER"],
 *       update: ["OWNER", "ADMIN"],
 *       delete: ["OWNER"],
 *     };
 *   }
 *
 *   getRole({ userId, organizationId }) {
 *     return Effect.gen(this, function* () {
 *       const client = yield* DrizzleORM;
 *       // Query membership table...
 *     });
 *   }
 *
 *   create({ userId, data }) {
 *     // Create org and make user the owner
 *   }
 *   // ... other CRUD methods
 * }
 * ```
 */
export abstract class BaseAuthenticatedEffectService<
  TPublic,
  TPath extends string,
  TInsert,
  TUpdate = Partial<TInsert>,
  TRole extends string = string,
  TExtraR = never,
> {
  // ---------------------------------------------------------------------------
  // Abstract Methods (must be implemented by subclasses)
  // ---------------------------------------------------------------------------

  /**
   * Returns a human-readable resource name for error messages.
   *
   * @example "organization", "project", "membership"
   */
  protected abstract getResourceName(): string;

  /**
   * Returns the permission table defining which roles can perform which actions.
   *
   * @example
   * ```ts
   * protected getPermissionTable() {
   *   return {
   *     create: ["OWNER", "ADMIN"],
   *     read: ["OWNER", "ADMIN", "MEMBER"],
   *     update: ["OWNER", "ADMIN"],
   *     delete: ["OWNER"],
   *   };
   * }
   * ```
   */
  protected abstract getPermissionTable(): PermissionTable<TRole>;

  /**
   * Determines the authenticated user's role for the given resource.
   *
   * This is typically implemented by querying a membership table to find
   * the user's role in the organization/project/etc.
   *
   * @param args.userId - The authenticated user's ID
   * @param args.[pathParams] - Path parameters identifying the authorization scope
   * @returns The user's role
   * @throws NotFoundError - If the user has no role (not a member)
   * @throws DatabaseError - If the database query fails
   *
   * @example
   * ```ts
   * getRole({ userId, organizationId }) {
   *   return Effect.gen(this, function* () {
   *     const client = yield* DrizzleORM;
   *     const [membership] = yield* client
   *       .select({ role: organizationMemberships.role })
   *       .from(organizationMemberships)
   *       .where(and(
   *         eq(organizationMemberships.organizationId, organizationId),
   *         eq(organizationMemberships.memberId, userId),
   *       ));
   *
   *     if (!membership) {
   *       return yield* Effect.fail(new NotFoundError({ ... }));
   *     }
   *     return membership.role;
   *   });
   * }
   * ```
   */
  abstract getRole(
    args: { userId: string } & AuthorizationParams<TPath>,
  ): Effect.Effect<
    TRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  >;

  // ---------------------------------------------------------------------------
  // Authorization Helpers
  // ---------------------------------------------------------------------------

  /**
   * Verifies that a role has permission to perform an action.
   *
   * @param role - The user's role
   * @param action - The action to perform
   * @returns Effect that succeeds if permitted, fails with PermissionDeniedError otherwise
   *
   * @example
   * ```ts
   * yield* this.verifyPermission("MEMBER", "delete");
   * // Fails with PermissionDeniedError if MEMBER can't delete
   * ```
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
          message: `You do not have permission to ${action} this ${this.getResourceName()}`,
          resource: this.getResourceName(),
        }),
      );
    }
    return Effect.succeed(undefined);
  }

  /**
   * Authorizes an action by checking the user's role and permissions.
   *
   * Combines `getRole()` and `verifyPermission()` into a single call.
   * Returns the user's role on success (useful for including in responses).
   *
   * @param args.userId - The authenticated user's ID
   * @param args.action - The action to authorize
   * @param args.[pathParams] - Path parameters identifying the resource
   * @returns The user's role (if authorized)
   * @throws NotFoundError - If the user has no role for this resource
   * @throws PermissionDeniedError - If the role cannot perform the action
   * @throws DatabaseError - If the database query fails
   *
   * @example
   * ```ts
   * update({ userId, organizationId, data }) {
   *   return Effect.gen(this, function* () {
   *     const role = yield* this.authorize({
   *       userId,
   *       action: "update",
   *       organizationId,
   *     });
   *     // User is authorized - proceed with update
   *     // Can include `role` in response if needed
   *   });
   * }
   * ```
   */
  authorize(
    args: {
      userId: string;
      action: PermissionAction;
    } & AuthorizationParams<TPath>,
  ): Effect.Effect<
    TRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const { userId, action, ...pathParams } = args;
      const role = yield* this.getRole({
        userId,
        ...pathParams,
      } as { userId: string } & AuthorizationParams<TPath>);
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
   * For most authenticated resources, `create` has special handling:
   * - Organizations: No prior auth needed; creator becomes OWNER
   * - Nested resources: Requires parent membership/role
   *
   * @param args.userId - The authenticated user's ID
   * @param args.data - The data to insert
   * @param args.[parentParams] - Parent path parameters for nested resources
   * @returns The created resource
   * @throws AlreadyExistsError - If a unique constraint is violated
   * @throws NotFoundError - If parent resource doesn't exist or user has no access
   * @throws PermissionDeniedError - If user lacks create permission
   * @throws DatabaseError - If the database operation fails
   */
  abstract create(
    args: { userId: string } & (HasParentParams<TPath> extends true
      ? ParentParams<TPath> & { data: TInsert }
      : { data: TInsert }),
  ): Effect.Effect<
    TPublic,
    | AlreadyExistsError
    | NotFoundError
    | PermissionDeniedError
    | DeletedUserError
    | DatabaseError
    | StripeError
    | PlanLimitExceededError,
    DrizzleORM | Payments | TExtraR
  >;

  /**
   * Retrieves all resources accessible to the user (with authorization).
   *
   * Implementations typically filter by membership or ownership.
   *
   * @param args.userId - The authenticated user's ID
   * @param args.[parentParams] - Parent path parameters for nested resources
   * @returns Array of accessible resources
   * @throws NotFoundError - If parent resource doesn't exist or user has no access
   * @throws PermissionDeniedError - If user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  abstract findAll(
    args: { userId: string } & (HasParentParams<TPath> extends true
      ? ParentParams<TPath>
      : unknown),
  ): Effect.Effect<
    TPublic[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM | TExtraR
  >;

  /**
   * Retrieves a single resource by ID (with authorization).
   *
   * @param args.userId - The authenticated user's ID
   * @param args.[pathParams] - All path parameters including the resource ID
   * @returns The found resource
   * @throws NotFoundError - If resource doesn't exist or user has no access
   * @throws PermissionDeniedError - If user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  abstract findById(
    args: { userId: string } & PathParams<TPath>,
  ): Effect.Effect<
    TPublic,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM | TExtraR
  >;

  /**
   * Updates a resource by ID (with authorization).
   *
   * @param args.userId - The authenticated user's ID
   * @param args.[pathParams] - All path parameters including the resource ID
   * @param args.data - The fields to update
   * @returns The updated resource
   * @throws NotFoundError - If resource doesn't exist or user has no access
   * @throws PermissionDeniedError - If user lacks update permission
   * @throws ImmutableResourceError - If the resource cannot be modified after creation
   * @throws DatabaseError - If the database operation fails
   * @throws StripeError - If Stripe operations fail (for resources synced with Stripe)
   */
  abstract update(
    args: { userId: string } & PathParams<TPath> & { data: TUpdate },
  ): Effect.Effect<
    TPublic,
    | NotFoundError
    | PermissionDeniedError
    | ImmutableResourceError
    | AlreadyExistsError
    | DeletedUserError
    | DatabaseError
    | StripeError,
    DrizzleORM | Payments | TExtraR
  >;

  /**
   * Deletes a resource by ID (with authorization).
   *
   * @param args.userId - The authenticated user's ID
   * @param args.[pathParams] - All path parameters including the resource ID
   * @throws NotFoundError - If resource doesn't exist or user has no access
   * @throws PermissionDeniedError - If user lacks delete permission
   * @throws ImmutableResourceError - If the resource cannot be deleted (immutable)
   * @throws DatabaseError - If the database operation fails
   * @throws StripeError - If Stripe operations fail (for resources synced with Stripe)
   */
  abstract delete(
    args: { userId: string } & PathParams<TPath>,
  ): Effect.Effect<
    void,
    | NotFoundError
    | PermissionDeniedError
    | ImmutableResourceError
    | DatabaseError
    | SubscriptionPastDueError
    | StripeError,
    DrizzleORM | Payments | TExtraR
  >;
}
