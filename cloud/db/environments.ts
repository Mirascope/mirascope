/**
 * @fileoverview Effect-native Environments service.
 *
 * Provides authenticated CRUD operations for environments with role-based access
 * control. Environments belong to projects and inherit authorization from the
 * project's membership system.
 *
 * ## Architecture
 *
 * ```
 * Environments (authenticated)
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## Environment Roles
 *
 * Environments use the project's role system:
 * - `ADMIN` - Full environment management (create, read, update, delete)
 * - `DEVELOPER` - Can create, read, and update environments
 * - `VIEWER` - Read-only access to environments
 * - `ANNOTATOR` - No access to environments
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * (and thus all environments) within their organization.
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Create an environment
 * const env = yield* db.organizations.projects.environments.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   data: { name: "production" },
 * });
 *
 * // List environments in a project
 * const envs = yield* db.organizations.projects.environments.findAll({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 * });
 * ```
 */

import { Effect } from "effect";
import { and, eq } from "drizzle-orm";
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
import { isUniqueConstraintError } from "@/db/utils";
import {
  environments,
  type NewEnvironment,
  type PublicEnvironment,
  type ProjectRole,
} from "@/db/schema";

/**
 * Public fields to select from the environments table.
 */
const publicFields = {
  id: environments.id,
  name: environments.name,
  projectId: environments.projectId,
};

/**
 * Effect-native Environments service.
 *
 * Provides CRUD operations with role-based access control for environments.
 * Authorization is inherited from project membership via ProjectMemberships.getRole().
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓     | ✓         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✓      | ✗         |
 * | update   | ✓     | ✓         | ✗      | ✗         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 *
 * ## Security Model
 *
 * - Org OWNER/ADMIN have implicit project ADMIN access (and thus environment access)
 * - Non-members cannot see that a project/environment exists (returns NotFoundError)
 * - Environment names must be unique within a project
 */
export class Environments extends BaseAuthenticatedEffectService<
  PublicEnvironment,
  "organizations/:organizationId/projects/:projectId/environments/:environmentId",
  Pick<NewEnvironment, "name">,
  Partial<Pick<NewEnvironment, "name">>,
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
    return "environment";
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN", "DEVELOPER"],
      read: ["ADMIN", "DEVELOPER", "VIEWER"],
      update: ["ADMIN", "DEVELOPER"],
      delete: ["ADMIN"],
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Determines the user's effective role for an environment.
   *
   * Delegates to `ProjectMemberships.authorize` which handles:
   * - Org OWNER → treated as project ADMIN
   * - Org ADMIN → treated as project ADMIN
   * - Explicit project membership role
   * - No access → NotFoundError (hides environment existence)
   *
   * We use authorize with action "read" since all project members can read
   * the project, and we get their role back from the authorization.
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
  }): Effect.Effect<
    ProjectRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return this.projectMemberships.getRole({
      userId,
      organizationId,
      projectId,
      memberId: userId,
    });
  }

  // ---------------------------------------------------------------------------
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new environment within a project.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   *
   * @param args.userId - The user creating the environment
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to create the environment in
   * @param args.data - Environment data (name)
   * @returns The created environment
   * @throws PermissionDeniedError - If user lacks create permission
   * @throws AlreadyExistsError - If an environment with this name exists in the project
   * @throws NotFoundError - If the project doesn't exist or user lacks access
   * @throws DatabaseError - If the database operation fails
   */
  create({
    userId,
    organizationId,
    projectId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    data: Pick<NewEnvironment, "name">;
  }): Effect.Effect<
    PublicEnvironment,
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
        environmentId: "", // Not used for create
      });

      // Insert the environment
      const [environment] = yield* client
        .insert(environments)
        .values({
          name: data.name,
          projectId,
        })
        .returning(publicFields)
        .pipe(
          Effect.mapError((e): AlreadyExistsError | DatabaseError =>
            isUniqueConstraintError(e.cause)
              ? new AlreadyExistsError({
                  message: `An environment with name "${data.name}" already exists in this project`,
                  resource: this.getResourceName(),
                })
              : new DatabaseError({
                  message: "Failed to create environment",
                  cause: e,
                }),
          ),
        );

      return environment as PublicEnvironment;
    });
  }

  /**
   * Retrieves all environments in a project.
   *
   * Requires ADMIN, DEVELOPER, or VIEWER role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to list environments for
   * @returns Array of environments in the project
   * @throws NotFoundError - If the project doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findAll({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
  }): Effect.Effect<
    PublicEnvironment[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize via project membership
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId: "", // Not used for findAll
      });

      const results: PublicEnvironment[] = yield* client
        .select(publicFields)
        .from(environments)
        .where(eq(environments.projectId, projectId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all environments",
                cause: e,
              }),
          ),
        );

      return results;
    });
  }

  /**
   * Retrieves an environment by ID.
   *
   * Requires ADMIN, DEVELOPER, or VIEWER role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to retrieve
   * @returns The environment
   * @throws NotFoundError - If the environment doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findById({
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
    PublicEnvironment,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize via project membership
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
      });

      const [environment] = yield* client
        .select(publicFields)
        .from(environments)
        .where(
          and(
            eq(environments.id, environmentId),
            eq(environments.projectId, projectId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find environment",
                cause: e,
              }),
          ),
        );

      if (!environment) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Environment with environmentId ${environmentId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return environment;
    });
  }

  /**
   * Updates an environment.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   * Only the name can be updated.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to update
   * @param args.data - Fields to update (only `name` allowed)
   * @returns The updated environment
   * @throws NotFoundError - If the environment doesn't exist
   * @throws PermissionDeniedError - If the user lacks update permission
   * @throws AlreadyExistsError - If the new name conflicts with existing environment
   * @throws DatabaseError - If the database operation fails
   */
  update({
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
    data: Partial<Pick<NewEnvironment, "name">>;
  }): Effect.Effect<
    PublicEnvironment,
    NotFoundError | PermissionDeniedError | AlreadyExistsError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize via project membership
      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        environmentId,
      });

      const [updated] = yield* client
        .update(environments)
        .set({ ...data, updatedAt: new Date() })
        .where(
          and(
            eq(environments.id, environmentId),
            eq(environments.projectId, projectId),
          ),
        )
        .returning(publicFields)
        .pipe(
          Effect.mapError((e): AlreadyExistsError | DatabaseError =>
            isUniqueConstraintError(e.cause)
              ? new AlreadyExistsError({
                  message: `An environment with name "${data.name}" already exists in this project`,
                  resource: this.getResourceName(),
                })
              : new DatabaseError({
                  message: "Failed to update environment",
                  cause: e,
                }),
          ),
        );

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Environment with environmentId ${environmentId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return updated;
    });
  }

  /**
   * Deletes an environment.
   *
   * Requires ADMIN role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to delete
   * @throws NotFoundError - If the environment doesn't exist
   * @throws PermissionDeniedError - If the user lacks delete permission
   * @throws DatabaseError - If the database operation fails
   */
  delete({
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
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize via project membership
      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
      });

      const [deleted] = yield* client
        .delete(environments)
        .where(
          and(
            eq(environments.id, environmentId),
            eq(environments.projectId, projectId),
          ),
        )
        .returning({ id: environments.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete environment",
                cause: e,
              }),
          ),
        );

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Environment with environmentId ${environmentId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }
    });
  }
}
