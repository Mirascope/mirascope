/**
 * @fileoverview Effect-native Functions service for function versioning.
 *
 * Provides authenticated function management with role-based access control.
 * Functions belong to environments and inherit authorization from the project's
 * membership system.
 *
 * ## Architecture
 *
 * ```
 * Functions extends BaseAuthenticatedEffectService
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## Function Roles
 *
 * Functions use the project's role system:
 * - `ADMIN` - Full function management
 * - `DEVELOPER` - Can create/read functions
 * - `VIEWER` - Read-only access
 * - `ANNOTATOR` - Read-only access
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * (and thus all environments and functions) within their organization.
 *
 * ## Security
 *
 * - API key authentication provides environment context
 * - The API key owner's userId is used for authorization
 * - Authorization is delegated to ProjectMemberships
 */

import { Effect } from "effect";
import { and, eq, desc, sql } from "drizzle-orm";
import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { ProjectMemberships } from "@/db/project-memberships";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import {
  functions,
  type NewFunction,
  type PublicFunction,
  type DependencyInfo,
} from "@/db/schema/functions";
import type { ProjectRole } from "@/db/schema";

// =============================================================================
// Types
// =============================================================================

export type RegisterFunctionInput = {
  code: string;
  hash: string;
  signature: string;
  signatureHash: string;
  name: string;
  description?: string | null;
  tags?: string[] | null;
  metadata?: Record<string, string> | null;
  dependencies?: Record<string, DependencyInfo> | null;
};

export type FunctionResponse = PublicFunction & {
  isNew: boolean;
};

// =============================================================================
// Functions Service
// =============================================================================

/** Path pattern for function resources */
type FunctionPath =
  "organizations/:organizationId/projects/:projectId/environments/:environmentId/functions/:functionId";

/**
 * Effect-native Functions service for function versioning.
 *
 * Extends BaseAuthenticatedEffectService for standardized authorization.
 * Authorization is delegated to ProjectMemberships.getRole().
 *
 * ## Permission Matrix
 *
 * | Action        | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |---------------|-------|-----------|--------|-----------|
 * | create        | ✓     | ✓         | ✗      | ✗         |
 * | read          | ✓     | ✓         | ✓      | ✓         |
 * | update        | ✓     | ✓         | ✗      | ✗         |
 * | delete        | ✓     | ✗         | ✗      | ✗         |
 *
 * ## Security Model
 *
 * - API key authentication provides environment context and owner identity
 * - The API key owner's userId is used for authorization checks
 * - Organization OWNER/ADMIN have implicit project ADMIN access
 */
export class Functions extends BaseAuthenticatedEffectService<
  FunctionResponse,
  FunctionPath,
  RegisterFunctionInput,
  never,
  ProjectRole
> {
  private readonly projectMemberships: ProjectMemberships;

  constructor(projectMemberships: ProjectMemberships) {
    super();
    this.projectMemberships = projectMemberships;
  }

  // ---------------------------------------------------------------------------
  // BaseAuthenticatedEffectService Implementation
  // ---------------------------------------------------------------------------

  protected getResourceName(): string {
    return "function";
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN", "DEVELOPER"],
      read: ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"],
      update: ["ADMIN", "DEVELOPER"],
      delete: ["ADMIN"],
    };
  }

  getRole({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId?: string;
    functionId?: string;
  }): Effect.Effect<
    ProjectRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return this.projectMemberships.getRole({
      userId,
      organizationId,
      projectId,
    });
  }

  // ---------------------------------------------------------------------------
  // CRUD Methods (BaseAuthenticatedEffectService interface)
  // ---------------------------------------------------------------------------

  /**
   * Create (register) a function with authorization.
   *
   * This is the main entry point for function registration.
   */
  create({
    userId,
    organizationId,
    projectId,
    environmentId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    data: RegisterFunctionInput;
  }): Effect.Effect<
    FunctionResponse,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // Authorize using base class method
      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      // Perform the actual registration
      return yield* this.registerOrGet({
        environmentId,
        projectId,
        organizationId,
        data,
      });
    });
  }

  /**
   * List all functions in an environment.
   *
   * Requires read access (any project role).
   */
  findAll({
    userId,
    organizationId,
    projectId,
    environmentId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
  }): Effect.Effect<
    FunctionResponse[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      const result = yield* this.listInternal(environmentId);
      return result.functions.map((f) => ({ ...f, isNew: false }));
    });
  }

  /**
   * Get a function by ID.
   *
   * Requires read access (any project role).
   */
  findById({
    userId,
    organizationId,
    projectId,
    environmentId,
    functionId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    functionId: string;
  }): Effect.Effect<
    FunctionResponse,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

      const fn = yield* this.getByIdInternal(functionId, environmentId);
      return { ...fn, isNew: false };
    });
  }

  /**
   * Update is not supported for functions (immutable by design).
   */
  update({
    userId,
    organizationId,
    projectId,
    environmentId,
    functionId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    functionId: string;
    data: never;
  }): Effect.Effect<
    FunctionResponse,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // Check authorization before returning error
      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

      // Functions are immutable - new versions are created instead
      return yield* Effect.fail(
        new PermissionDeniedError({
          message:
            "Functions are immutable. Register a new version instead of updating.",
          resource: "function",
        }),
      );
    });
  }

  /**
   * Delete a function.
   *
   * Requires ADMIN role.
   */
  delete({
    userId,
    organizationId,
    projectId,
    environmentId,
    functionId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    functionId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

      const client = yield* DrizzleORM;

      // First verify function exists in this environment
      yield* this.getByIdInternal(functionId, environmentId);

      // Delete the function
      yield* client
        .delete(functions)
        .where(
          and(
            eq(functions.id, functionId),
            eq(functions.environmentId, environmentId),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to delete function: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );
    });
  }

  // ---------------------------------------------------------------------------
  // Function Registration (Internal)
  // ---------------------------------------------------------------------------

  /**
   * Internal registration logic - does NOT perform authorization.
   * Use `create` for authorized access.
   */
  private registerOrGet({
    organizationId,
    projectId,
    environmentId,
    data,
  }: {
    organizationId: string;
    projectId: string;
    environmentId: string;
    data: RegisterFunctionInput;
  }): Effect.Effect<FunctionResponse, DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      // First, check if function with same hash already exists
      const existing: PublicFunction[] = yield* client
        .select()
        .from(functions)
        .where(
          and(
            eq(functions.hash, data.hash),
            eq(functions.environmentId, environmentId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to check existing function: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );

      if (existing[0]) {
        return {
          ...existing[0],
          isNew: false,
        };
      }

      // Compute version and insert in same transaction to prevent race conditions
      return yield* client.withTransaction(
        Effect.gen(function* () {
          // Get the latest version for this function name with lock
          const latestVersions: { version: string; signatureHash: string }[] =
            yield* client
              .select({
                version: functions.version,
                signatureHash: functions.signatureHash,
              })
              .from(functions)
              .where(
                and(
                  eq(functions.name, data.name),
                  eq(functions.environmentId, environmentId),
                ),
              )
              .orderBy(desc(functions.createdAt))
              .limit(1)
              .for("update")
              .pipe(
                Effect.mapError(
                  (e) =>
                    new DatabaseError({
                      message: `Failed to get latest version: ${e instanceof Error ? e.message : "Unknown error"}`,
                      cause: e,
                    }),
                ),
              );

          let version: string;
          if (latestVersions.length === 0) {
            // No existing version for this name, start at 1.0
            version = "1.0";
          } else {
            const latest = latestVersions[0];
            const [major, minor] = latest.version.split(".").map(Number);

            if (latest.signatureHash !== data.signatureHash) {
              // Signature changed -> major version bump
              version = `${major + 1}.0`;
            } else {
              // Same signature, different implementation -> minor version bump
              version = `${major}.${minor + 1}`;
            }
          }

          // Insert new function within the same transaction
          const newFunction: NewFunction = {
            hash: data.hash,
            signatureHash: data.signatureHash,
            name: data.name,
            description: data.description ?? null,
            version,
            tags: data.tags ?? null,
            metadata: data.metadata ?? null,
            code: data.code,
            signature: data.signature,
            dependencies: data.dependencies ?? null,
            environmentId,
            projectId,
            organizationId,
          };

          const insertResult: PublicFunction[] = yield* client
            .insert(functions)
            .values(newFunction)
            .onConflictDoNothing({
              target: [functions.hash, functions.environmentId],
            })
            .returning()
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: `Failed to insert function: ${e instanceof Error ? e.message : "Unknown error"}`,
                    cause: e,
                  }),
              ),
            );

          const inserted = insertResult[0];

          // If conflict occurred (race condition on hash), fetch the existing one
          if (!inserted) {
            const existingAfterConflict: PublicFunction[] = yield* client
              .select()
              .from(functions)
              .where(
                and(
                  eq(functions.hash, data.hash),
                  eq(functions.environmentId, environmentId),
                ),
              )
              .limit(1)
              .pipe(
                Effect.mapError(
                  (e) =>
                    new DatabaseError({
                      message: `Failed to fetch after conflict: ${e instanceof Error ? e.message : "Unknown error"}`,
                      cause: e,
                    }),
                ),
              );

            return {
              ...existingAfterConflict[0],
              isNew: false,
            };
          }

          return {
            ...inserted,
            isNew: true,
          };
        }),
      );
    });
  }

  // ---------------------------------------------------------------------------
  // Function Retrieval (Authorized)
  // ---------------------------------------------------------------------------

  /**
   * Get function by hash within environment scope.
   *
   * Requires read access (any project role).
   */
  getByHash({
    userId,
    organizationId,
    projectId,
    environmentId,
    hash,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    hash: string;
  }): Effect.Effect<
    PublicFunction,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // Authorize using base class method
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      return yield* this.getByHashInternal(hash, environmentId);
    });
  }

  /**
   * Internal getByHash - does NOT perform authorization.
   */
  private getByHashInternal(
    hash: string,
    environmentId: string,
  ): Effect.Effect<PublicFunction, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result: PublicFunction[] = yield* client
        .select()
        .from(functions)
        .where(
          and(
            eq(functions.hash, hash),
            eq(functions.environmentId, environmentId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to get function by hash: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );

      const row = result[0];
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Function with hash ${hash} not found`,
            resource: "function",
          }),
        );
      }

      return row;
    });
  }

  /**
   * Get function by ID.
   *
   * Requires read access (any project role).
   */
  getById({
    userId,
    organizationId,
    projectId,
    environmentId,
    id,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    id: string;
  }): Effect.Effect<
    PublicFunction,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // Authorize using base class method
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      return yield* this.getByIdInternal(id, environmentId);
    });
  }

  /**
   * Internal getById - does NOT perform authorization.
   */
  private getByIdInternal(
    id: string,
    environmentId: string,
  ): Effect.Effect<PublicFunction, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result: PublicFunction[] = yield* client
        .select()
        .from(functions)
        .where(
          and(eq(functions.id, id), eq(functions.environmentId, environmentId)),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to get function by id: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );

      const row = result[0];
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Function with id ${id} not found`,
            resource: "function",
          }),
        );
      }

      return row;
    });
  }

  /**
   * List functions with filters.
   *
   * Requires read access (any project role).
   */
  list({
    userId,
    organizationId,
    projectId,
    environmentId,
    filters,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    filters?: {
      name?: string;
      tags?: string[];
      limit?: number;
      offset?: number;
    };
  }): Effect.Effect<
    { functions: PublicFunction[]; total: number },
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // Authorize using base class method
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      return yield* this.listInternal(environmentId, filters);
    });
  }

  /**
   * Internal list - does NOT perform authorization.
   */
  private listInternal(
    environmentId: string,
    filters?: {
      name?: string;
      tags?: string[];
      limit?: number;
      offset?: number;
    },
  ): Effect.Effect<
    { functions: PublicFunction[]; total: number },
    DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const conditions = [eq(functions.environmentId, environmentId)];

      if (filters?.name) {
        conditions.push(eq(functions.name, filters.name));
      }

      if (filters?.tags && filters.tags.length > 0) {
        // Check if all requested tags are present in the function's tags array
        conditions.push(
          sql`${functions.tags} @> ${JSON.stringify(filters.tags)}::jsonb`,
        );
      }

      const whereClause = and(...conditions);

      // Get total count
      const countResult: { count: number }[] = yield* client
        .select({ count: sql<number>`count(*)::int` })
        .from(functions)
        .where(whereClause)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to count functions: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );

      const total = countResult[0]?.count ?? 0;

      // Build query
      let query = client
        .select()
        .from(functions)
        .where(whereClause)
        .orderBy(desc(functions.createdAt));

      if (filters?.limit) {
        query = query.limit(filters.limit) as typeof query;
      }

      if (filters?.offset) {
        query = query.offset(filters.offset) as typeof query;
      }

      const results: PublicFunction[] = yield* query.pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: `Failed to list functions: ${e instanceof Error ? e.message : "Unknown error"}`,
              cause: e,
            }),
        ),
      );

      return {
        functions: results,
        total,
      };
    });
  }
}
