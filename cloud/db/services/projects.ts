/**
 * @fileoverview Project service for managing projects within organizations.
 *
 * This module provides authenticated CRUD operations for projects with
 * role-based access control. Projects belong to organizations and have
 * their own membership system for fine-grained access control.
 *
 * ## Architecture
 *
 * ```
 * ProjectService (authenticated)
 *   ├── baseService: ProjectBaseService
 *   │     └── CRUD on `projects` table (raw, no auth)
 *   └── memberships: ProjectMembershipService
 *         └── CRUD on `project_memberships` table (authenticated)
 * ```
 *
 * ## Usage
 *
 * ```ts
 * // Create a project
 * const project = yield* db.organizations.projects.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   data: { name: "My Project" },
 * });
 *
 * // Add a member to the project
 * yield* db.organizations.projects.memberships.create({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   projectId: project.id,
 *   data: { memberId: "new-member-789", role: "DEVELOPER" },
 * });
 * ```
 */

import { Effect } from "effect";
import { eq, and } from "drizzle-orm";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import {
  BaseService,
  BaseAuthenticatedService,
  type PermissionTable,
} from "@/db/services/base";
import type { OrganizationMembershipService } from "@/db/services/organization-memberships";
import { ProjectMembershipService } from "@/db/services/project-memberships";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import {
  projects,
  projectMemberships,
  projectMembershipAudit,
  type NewProject,
  type PublicProject,
  type ProjectRole,
} from "@/db/schema";
import type * as schema from "@/db/schema";
import { isUniqueConstraintError } from "@/db/utils";

// =============================================================================
// Base Service (Internal)
// =============================================================================

/**
 * Low-level CRUD service for the projects table.
 *
 * Path pattern: `organizations/:organizationId/projects/:projectId`
 * - Parent param: `organizationId` (scope to organization)
 * - Resource ID: `projectId`
 */
class ProjectBaseService extends BaseService<
  PublicProject,
  "organizations/:organizationId/projects/:projectId",
  typeof projects
> {
  protected getTable() {
    return projects;
  }

  protected getResourceName() {
    return "project";
  }

  protected getIdParamName() {
    return "projectId" as const;
  }

  protected getPublicFields() {
    return {
      id: projects.id,
      name: projects.name,
      organizationId: projects.organizationId,
      createdByUserId: projects.createdByUserId,
    };
  }

  protected getParentScopedWhere(params: { organizationId: string }) {
    return eq(projects.organizationId, params.organizationId);
  }
}

// =============================================================================
// Project Service (Public)
// =============================================================================

/**
 * Authenticated service for project management.
 *
 * Provides CRUD operations with role-based access control for projects.
 * Users interact with projects based on their effective role resolved by
 * ProjectMembershipService (implicit org OWNER/ADMIN → project ADMIN).
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓*    | ✗         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✓      | ✓         |
 * | update   | ✓     | ✗         | ✗      | ✗         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 *
 * *Create is a special case: it requires org OWNER/ADMIN and is handled separately.
 */
export class ProjectService extends BaseAuthenticatedService<
  PublicProject,
  "organizations/:organizationId/projects/:projectId",
  typeof projects,
  NewProject,
  ProjectRole
> {
  private readonly organizationMemberships: OrganizationMembershipService;

  /**
   * Service for managing project memberships.
   *
   * Use this to add, update, or remove members from projects:
   * ```ts
   * // Add a member
   * yield* db.organizations.projects.memberships.create({
   *   userId, organizationId, projectId,
   *   data: { memberId: targetUserId, role: "DEVELOPER" },
   * });
   *
   * // List members
   * yield* db.organizations.projects.memberships.findAll({ userId, organizationId, projectId });
   * ```
   */
  public readonly memberships: ProjectMembershipService;

  constructor(
    db: PostgresJsDatabase<typeof schema>,
    organizationMemberships: OrganizationMembershipService,
  ) {
    super(db);
    this.organizationMemberships = organizationMemberships;
    this.memberships = new ProjectMembershipService(
      db,
      organizationMemberships,
    );
  }

  // ---------------------------------------------------------------------------
  // Base Service Implementation
  // ---------------------------------------------------------------------------

  protected initializeBaseService() {
    return new ProjectBaseService(this.db);
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN"], // org OWNER/ADMIN is cast to project ADMIN with create permission
      read: ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"],
      update: ["ADMIN"],
      delete: ["ADMIN"],
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Determines the user's effective role for a project.
   *
   * Delegates to `ProjectMembershipService.getRole` which handles:
   * - Org OWNER → treated as project OWNER
   * - Org ADMIN → treated as project ADMIN
   * - Explicit project membership role
   * - No access → NotFoundError (hides project existence)
   *
   * @param args.userId - The user to check
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to check membership in
   * @returns The user's effective role in the project
   * @throws NotFoundError - If the user has no access
   * @throws DatabaseError - If the database query fails
   */
  getRole({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
  }): Effect.Effect<ProjectRole, NotFoundError | DatabaseError> {
    return this.memberships.getRole({
      userId,
      organizationId,
      projectId,
    });
  }

  // ---------------------------------------------------------------------------
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new project within an organization.
   *
   * Requires org OWNER or ADMIN role. The creating user is automatically
   * added as an explicit project member with role ADMIN.
   *
   * Performs an atomic transaction:
   * 1. Insert the project
   * 2. Create an ADMIN membership for the creator
   * 3. Write a GRANT audit entry for the creator membership
   *
   * @param args.userId - The user creating the project (becomes project ADMIN)
   * @param args.organizationId - The organization to create the project in
   * @param args.data - Project data (name)
   * @returns The created project
   * @throws PermissionDeniedError - If user lacks org OWNER/ADMIN role
   * @throws AlreadyExistsError - If a project with this name exists in the org
   * @throws DatabaseError - If the database operation fails
   */
  create({
    userId,
    organizationId,
    data,
  }: {
    userId: string;
    organizationId: string;
    data: Pick<NewProject, "name">;
  }): Effect.Effect<
    PublicProject,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      // Must be org OWNER/ADMIN to create projects.
      // Note: org non-members get NotFoundError via org role resolution.
      const orgRole = yield* this.organizationMemberships.getRole({
        userId,
        organizationId,
      });
      if (orgRole !== "OWNER" && orgRole !== "ADMIN") {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message:
              "You do not have permission to create projects in this organization",
            resource: this.baseService.resourceName,
          }),
        );
      }

      return yield* Effect.tryPromise({
        try: async () => {
          return await this.db.transaction(async (tx) => {
            const [project] = await tx
              .insert(projects)
              .values({
                name: data.name,
                organizationId,
                createdByUserId: userId,
              })
              .returning({
                id: projects.id,
                name: projects.name,
                organizationId: projects.organizationId,
                createdByUserId: projects.createdByUserId,
              });

            // Add creator as explicit project ADMIN
            await tx.insert(projectMemberships).values({
              projectId: project.id,
              memberId: userId,
              role: "ADMIN",
            });

            // Audit the grant (creator granting themselves during creation)
            await tx.insert(projectMembershipAudit).values({
              projectId: project.id,
              actorId: userId,
              targetId: userId,
              action: "GRANT",
              previousRole: null,
              newRole: "ADMIN",
            });

            return project as PublicProject;
          });
        },
        catch: (error) => {
          if (isUniqueConstraintError(error)) {
            return new AlreadyExistsError({
              message: "A project with this name already exists",
              resource: this.baseService.resourceName,
            });
          }
          return new DatabaseError({
            message: "Failed to create project",
            cause: error,
          });
        },
      });
    });
  }

  /**
   * Retrieves all projects the user can access within an organization.
   *
   * - Org OWNER/ADMIN see all projects in the organization (implicit ADMIN)
   * - Others only see projects where they have explicit membership
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization to list projects for
   * @returns Array of accessible projects
   * @throws NotFoundError - If the organization doesn't exist
   * @throws DatabaseError - If the database query fails
   */
  findAll({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    PublicProject[],
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      // Get org role (also verifies org membership / hides org existence)
      const orgRole = yield* this.organizationMemberships.getRole({
        userId,
        organizationId,
      });

      // Note: We cannot use project-level authorization (`this.authorize` / membership role
      // resolution) here because `findAll` is not scoped to a single `projectId`.
      // Instead we do a single org-role check to:
      // - preserve "hide org existence" semantics for non-members, and
      // - avoid an N+1 per-project role check when listing projects.
      const isOrgPrivileged = orgRole === "OWNER" || orgRole === "ADMIN";

      if (isOrgPrivileged) {
        return yield* this.baseService.findAll({ organizationId });
      }

      // Others only see projects they're members of
      return yield* Effect.tryPromise({
        try: async () => {
          return await this.db
            .select({
              id: projects.id,
              name: projects.name,
              organizationId: projects.organizationId,
              createdByUserId: projects.createdByUserId,
            })
            .from(projects)
            .innerJoin(
              projectMemberships,
              eq(projects.id, projectMemberships.projectId),
            )
            .where(
              and(
                eq(projects.organizationId, organizationId),
                eq(projectMemberships.memberId, userId),
              ),
            );
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to find all projects",
            cause: error,
          }),
      });
    });
  }

  /**
   * Retrieves a project by ID.
   *
   * Requires membership in the project (any role) or org OWNER/ADMIN.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to retrieve
   * @returns The project
   * @throws NotFoundError - If the project doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findById({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
  }): Effect.Effect<
    PublicProject,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
      });
      return yield* this.baseService.findById({ organizationId, projectId });
    });
  }

  /**
   * Updates a project.
   *
   * Requires OWNER, ADMIN, or DEVELOPER role on the project (or org OWNER/ADMIN).
   * Only the name can be updated.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to update
   * @param args.data - Fields to update (only `name` allowed)
   * @returns The updated project
   * @throws NotFoundError - If the project doesn't exist
   * @throws PermissionDeniedError - If the user lacks update permission
   * @throws DatabaseError - If the database operation fails
   */
  update({
    userId,
    organizationId,
    projectId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    data: Partial<Pick<NewProject, "name">>;
  }): Effect.Effect<
    PublicProject,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
      });
      return yield* this.baseService.update({
        organizationId,
        projectId,
        data,
      });
    });
  }

  /**
   * Deletes a project.
   *
   * Requires OWNER or ADMIN role on the project (or org OWNER/ADMIN).
   * All project memberships are automatically deleted via CASCADE.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to delete
   * @throws NotFoundError - If the project doesn't exist
   * @throws PermissionDeniedError - If the user lacks delete permission
   * @throws DatabaseError - If the database operation fails
   */
  delete({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
      });
      yield* this.baseService.delete({ organizationId, projectId });
    });
  }
}
