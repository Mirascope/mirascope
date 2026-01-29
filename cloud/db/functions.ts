/**
 * @fileoverview Effect-native Functions service for function versioning.
 *
 * Provides authenticated CRUD operations for functions with role-based access
 * control. Functions belong to environments and inherit authorization from the
 * project's membership system.
 *
 * ## Architecture
 *
 * ```
 * Functions (authenticated)
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## Function Roles
 *
 * Functions use the project's role system:
 * - `ADMIN` - Full function management (create, read, delete)
 * - `DEVELOPER` - Can create and read functions
 * - `VIEWER` - Read-only access to functions
 * - `ANNOTATOR` - Read-only access to functions
 *
 * Note: Functions are immutable and cannot be updated once created.
 * Register a new version instead.
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * (and thus all environments and functions) within their organization.
 *
 * ## Versioning
 *
 * Functions are versioned using semantic versioning:
 * - Version increments automatically based on signature changes
 * - Same signature = minor version bump (e.g., 1.0 → 1.1)
 * - Different signature = major version bump (e.g., 1.1 → 2.0)
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Create a new function version
 * const fn = yield* db.organizations.projects.environments.functions.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 *   data: {
 *     hash: "abc123",
 *     signatureHash: "def456",
 *     name: "my_function",
 *     code: "def my_function(): ...",
 *     signature: "(x: int) -> str",
 *   },
 * });
 *
 * // Find by hash (returns NotFoundError if not found)
 * const existing = yield* db.organizations.projects.environments.functions.findByHash({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 *   hash: "abc123",
 * });
 * ```
 */

import { and, eq, desc } from "drizzle-orm";
import { Effect } from "effect";

import type { ProjectRole } from "@/db/schema";

import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { ProjectMemberships } from "@/db/project-memberships";
import {
  functions,
  type NewFunction,
  type PublicFunction,
  type DependencyInfo,
} from "@/db/schema/functions";
import { isUniqueConstraintError } from "@/db/utils";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  ImmutableResourceError,
} from "@/errors";

export type { PublicFunction, DependencyInfo };

export type FunctionCreateData = Pick<
  NewFunction,
  | "code"
  | "hash"
  | "signature"
  | "signatureHash"
  | "name"
  | "description"
  | "tags"
  | "metadata"
  | "dependencies"
>;

/**
 * Effect-native Functions service.
 *
 * Provides CRUD operations with role-based access control for functions.
 * Authorization is inherited from project membership via ProjectMemberships.getRole().
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓     | ✓         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✓      | ✓         |
 * | update   | ✗     | ✗         | ✗      | ✗         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 *
 * Note: Functions are immutable - update always fails with ImmutableResourceError.
 *
 * ## Security Model
 *
 * - Org OWNER/ADMIN have implicit project ADMIN access (and thus function access)
 * - Non-members cannot see that an environment/function exists (returns NotFoundError)
 * - Functions are identified by their content hash for deduplication
 */
export class Functions extends BaseAuthenticatedEffectService<
  PublicFunction,
  "organizations/:organizationId/projects/:projectId/environments/:environmentId/functions/:functionId",
  FunctionCreateData,
  never,
  ProjectRole
> {
  private readonly projectMemberships: ProjectMemberships;

  constructor(projectMemberships: ProjectMemberships) {
    super();
    this.projectMemberships = projectMemberships;
  }

  // ---------------------------------------------------------------------------
  // Base Implementation
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

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Determines the user's effective role for a function.
   *
   * Delegates to `ProjectMemberships.getRole` which handles:
   * - Org OWNER → treated as project ADMIN
   * - Org ADMIN → treated as project ADMIN
   * - Explicit project membership role
   * - No access → NotFoundError (hides function existence)
   */
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
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new function version.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   * Functions are deduplicated by hash - attempting to create a function
   * with an existing hash will fail with AlreadyExistsError.
   *
   * Version is automatically calculated based on existing functions with
   * the same name:
   * - New function: starts at version "1.0"
   * - Same signature: minor version bump (e.g., 1.0 → 1.1)
   * - Different signature: major version bump (e.g., 1.1 → 2.0)
   *
   * @param args.userId - The user creating the function
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to create the function in
   * @param args.data - Function data including code, hash, and signature
   * @returns The created function
   * @throws AlreadyExistsError - If a function with this hash already exists
   * @throws PermissionDeniedError - If user lacks create permission
   * @throws NotFoundError - If the environment doesn't exist or user lacks access
   * @throws DatabaseError - If the database operation fails
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
    data: FunctionCreateData;
  }): Effect.Effect<
    PublicFunction,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      // Calculate version based on existing functions with same name
      const version = yield* this.calculateVersion(
        client,
        environmentId,
        data.name,
        data.signatureHash,
      );

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

      const [inserted] = yield* client
        .insert(functions)
        .values(newFunction)
        .returning()
        .pipe(
          Effect.mapError((e) =>
            isUniqueConstraintError(e.cause)
              ? new AlreadyExistsError({
                  message: `Function with hash ${data.hash} already exists`,
                  resource: "functions",
                })
              : new DatabaseError({
                  message: "Failed to create function",
                  cause: e,
                }),
          ),
        );

      return inserted;
    });
  }

  /**
   * Retrieves all functions in an environment.
   *
   * Requires any role on the project (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to list functions for
   * @returns Array of functions in the environment
   * @throws NotFoundError - If the environment doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
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
    PublicFunction[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      return yield* client
        .select()
        .from(functions)
        .where(eq(functions.environmentId, environmentId))
        .orderBy(desc(functions.createdAt))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to list functions",
                cause: e,
              }),
          ),
        );
    });
  }

  /**
   * Retrieves a function by ID.
   *
   * Requires any role on the project (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the function
   * @param args.functionId - The function to retrieve
   * @returns The function
   * @throws NotFoundError - If the function doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
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
    PublicFunction,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

      const [row] = yield* client
        .select()
        .from(functions)
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
                message: "Failed to get function",
                cause: e,
              }),
          ),
        );

      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Function ${functionId} not found`,
            resource: "functions",
          }),
        );
      }

      return row;
    });
  }

  /**
   * Updates a function (not supported - functions are immutable).
   *
   * Always fails with ImmutableResourceError because functions cannot be
   * modified after creation. Register a new version instead.
   *
   * @throws ImmutableResourceError - Always (functions are immutable)
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
    PublicFunction,
    | NotFoundError
    | PermissionDeniedError
    | ImmutableResourceError
    | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

      return yield* Effect.fail(
        new ImmutableResourceError({
          message:
            "Functions are immutable. Register a new version instead of updating.",
          resource: "functions",
        }),
      );
    });
  }

  /**
   * Deletes a function.
   *
   * Requires ADMIN role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the function
   * @param args.functionId - The function to delete
   * @throws NotFoundError - If the function doesn't exist
   * @throws PermissionDeniedError - If the user lacks delete permission
   * @throws DatabaseError - If the database operation fails
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
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

      const [row] = yield* client
        .delete(functions)
        .where(
          and(
            eq(functions.id, functionId),
            eq(functions.environmentId, environmentId),
          ),
        )
        .returning({ id: functions.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete function",
                cause: e,
              }),
          ),
        );

      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Function ${functionId} not found`,
            resource: "functions",
          }),
        );
      }
    });
  }

  // ===========================================================================
  // Custom Methods
  // ===========================================================================

  /**
   * Retrieves a function by its content hash.
   *
   * Requires any role on the project (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the function
   * @param args.hash - The content hash of the function
   * @returns The function
   * @throws NotFoundError - If no function with this hash exists
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findByHash({
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
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      const [row] = yield* client
        .select()
        .from(functions)
        .where(
          and(
            eq(functions.hash, hash),
            eq(functions.environmentId, environmentId),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get function by hash",
                cause: e,
              }),
          ),
        );

      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Function with hash ${hash} not found`,
            resource: "functions",
          }),
        );
      }

      return row;
    });
  }

  // ===========================================================================
  // Private Helpers
  // ===========================================================================

  /**
   * Calculates the next version for a function based on existing versions.
   */
  private calculateVersion(
    client: DrizzleORM["Type"],
    environmentId: string,
    name: string,
    signatureHash: string,
  ): Effect.Effect<string, DatabaseError, never> {
    return Effect.gen(function* () {
      const [latest] = yield* client
        .select({
          version: functions.version,
          signatureHash: functions.signatureHash,
        })
        .from(functions)
        .where(
          and(
            eq(functions.name, name),
            eq(functions.environmentId, environmentId),
          ),
        )
        .orderBy(desc(functions.createdAt))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get latest version",
                cause: e,
              }),
          ),
        );

      if (!latest) {
        return "1.0";
      }

      const [major, minor] = latest.version.split(".").map(Number);

      if (latest.signatureHash !== signatureHash) {
        return `${major + 1}.0`;
      }

      return `${major}.${minor + 1}`;
    });
  }
}
