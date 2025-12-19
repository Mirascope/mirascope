/**
 * @fileoverview Project membership service for managing user memberships in projects.
 *
 * This module provides authenticated CRUD operations for project memberships
 * with role-based access control. Memberships define the relationship between
 * users and projects within an organization.
 *
 * ## Project Roles
 *
 * Projects support four roles:
 * - `ADMIN` - Can manage project memberships (create, read, update, delete)
 * - `DEVELOPER` - Read-only access to membership info (read)
 * - `VIEWER` - Read-only access to membership info (read)
 * - `ANNOTATOR` - Read-only access to membership info (read)
 *
 * NOTE: at the project level, the `DEVELOPER`, `VIEWER`, and `ANNOTATOR` roles are
 * equivalent (read-only). However, these roles will have more granular permissions
 * for project resources (e.g. environments, API keys, traces, etc.)
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * within their organization, even without explicit project membership.
 *
 * ## Organization Membership Requirement
 *
 * Users must already be a member of the organization that owns the project to be
 * added as a project member.
 *
 * TODO: Add support for external collaborators (non-org members) via an invite/collaborator model.
 *
 * ## Architecture
 *
 * ```
 * ProjectMembershipService (authenticated)
 *   ├── baseService: ProjectMembershipBaseService
 *   │     └── CRUD on `project_memberships` table (raw, no auth)
 *   └── audits: ProjectMembershipAuditBaseService (read-only)
 *         └── Query on `project_membership_audit` table (raw, no auth)
 * ```
 */

import { Effect } from "effect";
import { and, eq, type SQL } from "drizzle-orm";
import {
  BaseAuthenticatedService,
  BaseService,
  type PermissionTable,
  type ParentParams,
} from "@/db/services/base";
import type { OrganizationService } from "@/db/services/organizations";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { isUniqueConstraintError } from "@/db/utils";
import {
  projects,
  projectMemberships,
  projectMembershipAudit,
  type PublicProjectMembership,
  type PublicProjectMembershipAudit,
  type NewProjectMembership,
  type OrganizationRole,
  type ProjectRole,
} from "@/db/schema";
import type * as schema from "@/db/schema";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";

// =============================================================================
// Base Service (Internal)
// =============================================================================

/**
 * Low-level CRUD service for the project_memberships table.
 *
 * Path pattern: `organizations/:organizationId/projects/:projectId/members/:memberId`
 * - Parent params: `organizationId`, `projectId` (scope to org and project)
 * - Resource ID: `memberId` (identifies the membership by the target user's ID)
 */
class ProjectMembershipBaseService extends BaseService<
  PublicProjectMembership,
  "organizations/:organizationId/projects/:projectId/members/:memberId",
  typeof projectMemberships
> {
  protected getTable() {
    return projectMemberships;
  }

  protected getResourceName() {
    return "project membership";
  }

  protected getIdParamName() {
    return "memberId" as const;
  }

  /** Override: memberships are identified by (projectId, memberId). */
  protected getIdColumn() {
    return projectMemberships.memberId;
  }

  protected getPublicFields() {
    return {
      memberId: projectMemberships.memberId,
      projectId: projectMemberships.projectId,
      role: projectMemberships.role,
      createdAt: projectMemberships.createdAt,
    };
  }

  /**
   * Override to skip `organizationId` since it's not on the table.
   *
   * The path includes `organizationId` for authorization purposes,
   * but the actual table only has `projectId`. We filter by `projectId` only.
   */
  protected getParentScopedWhere(
    params: ParentParams<"organizations/:organizationId/projects/:projectId/members/:memberId">,
  ): SQL | undefined {
    // Only use projectId for scoping (organizationId is for auth only)
    return eq(projectMemberships.projectId, params.projectId);
  }
}

/**
 * Low-level read service for the project_membership_audit table.
 *
 * Path pattern: `organizations/:organizationId/projects/:projectId/members/:memberId/audits/:id`
 * - Parent params: `organizationId`, `projectId`, `memberId` (maps to targetId)
 * - Resource ID: `id` (audit entry ID)
 */
class ProjectMembershipAuditBaseService extends BaseService<
  PublicProjectMembershipAudit,
  "organizations/:organizationId/projects/:projectId/members/:memberId/audits/:id",
  typeof projectMembershipAudit
> {
  protected getTable() {
    return projectMembershipAudit;
  }

  protected getResourceName() {
    return "project membership audit";
  }

  protected getIdParamName() {
    return "id" as const;
  }

  protected getPublicFields() {
    return {
      id: projectMembershipAudit.id,
      actorId: projectMembershipAudit.actorId,
      targetId: projectMembershipAudit.targetId,
      action: projectMembershipAudit.action,
      previousRole: projectMembershipAudit.previousRole,
      newRole: projectMembershipAudit.newRole,
      createdAt: projectMembershipAudit.createdAt,
    };
  }

  protected getParentScopedWhere(params: {
    organizationId: string;
    projectId: string;
    memberId: string;
  }) {
    // organizationId is for auth only; projectId scopes the table. memberId maps to targetId.
    return and(
      eq(projectMembershipAudit.projectId, params.projectId),
      eq(projectMembershipAudit.targetId, params.memberId),
    );
  }
}

// =============================================================================
// Project Membership Service (Public)
// =============================================================================

/**
 * Authenticated service for project membership management.
 *
 * Provides CRUD operations with role-based access control for memberships.
 * Users interact with memberships based on their role in the project or
 * their implicit role from the organization.
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓     | ✗         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✓      | ✓         |
 * | update   | ✓     | ✗         | ✗      | ✗         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 *
 * ## Security Model
 *
 * - Org OWNER/ADMIN have implicit project ADMIN access
 * - Non-members cannot see that a project exists (returns NotFoundError)
 * - Cannot modify your own membership
 * - Cannot remove yourself from a project
 * - Target must already be an org member (TODO external collaborators)
 */
export class ProjectMembershipService extends BaseAuthenticatedService<
  PublicProjectMembership,
  "organizations/:organizationId/projects/:projectId/members/:memberId",
  typeof projectMemberships,
  Pick<NewProjectMembership, "memberId" | "role">,
  ProjectRole
> {
  private readonly organizations: OrganizationService;
  public readonly audits: ProjectMembershipAuditBaseService;

  constructor(
    db: PostgresJsDatabase<typeof schema>,
    organizations: OrganizationService,
  ) {
    super(db);
    this.organizations = organizations;
    this.audits = new ProjectMembershipAuditBaseService(db);
  }

  // ---------------------------------------------------------------------------
  // Base Service Implementation
  // ---------------------------------------------------------------------------

  protected initializeBaseService() {
    return new ProjectMembershipBaseService(this.db);
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN"],
      read: ["ADMIN", "DEVELOPER", "VIEWER"],
      update: ["ADMIN"],
      delete: ["ADMIN"],
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  protected getMembership({
    memberId,
    organizationId,
    projectId,
  }: {
    memberId: string;
    organizationId: string;
    projectId: string;
  }): Effect.Effect<{ role: ProjectRole } | null, DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const [membership] = await this.db
          .select({ role: projectMemberships.role })
          .from(projectMemberships)
          .innerJoin(projects, eq(projectMemberships.projectId, projects.id))
          .where(
            and(
              eq(projects.organizationId, organizationId),
              eq(projects.id, projectId),
              eq(projectMemberships.memberId, memberId),
            ),
          )
          .limit(1);
        return (membership as { role: ProjectRole }) ?? null;
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to get project membership",
          cause: error,
        }),
    });
  }

  /**
   * Determines the user's effective role for a project.
   *
   * Role resolution follows this priority:
   * 1. Org OWNER → treated as project ADMIN
   * 2. Org ADMIN → treated as project ADMIN
   * 3. Explicit project membership role
   * 4. No access → NotFoundError (hides project existence)
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
    return Effect.gen(this, function* () {
      // Check org role first for implicit access
      const userOrganizationRole = yield* this.organizations
        .getRole({ organizationId, userId })
        .pipe(
          Effect.catchTag("NotFoundError", () =>
            Effect.succeed(null as OrganizationRole | null),
          ),
        );

      // Org OWNER/ADMIN have implicit project ADMIN access
      if (
        userOrganizationRole === "OWNER" ||
        userOrganizationRole === "ADMIN"
      ) {
        yield* this.verifyProjectExists(organizationId, projectId);
        return "ADMIN";
      }

      // Check explicit project membership
      const projectMembership = yield* this.getMembership({
        memberId: userId,
        organizationId,
        projectId,
      });

      if (!projectMembership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Project not found",
            resource: this.baseService.resourceName,
          }),
        );
      }

      return projectMembership.role;
    });
  }

  /**
   * Verifies that a project exists within the specified organization.
   */
  private verifyProjectExists(
    organizationId: string,
    projectId: string,
  ): Effect.Effect<void, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const project = yield* Effect.tryPromise({
        try: async () => {
          const [result] = await this.db
            .select({ id: projects.id })
            .from(projects)
            .where(
              and(
                eq(projects.id, projectId),
                eq(projects.organizationId, organizationId),
              ),
            )
            .limit(1);
          return result;
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to verify project",
            cause: error,
          }),
      });

      if (!project) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Project not found",
            resource: "project",
          }),
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new membership for a user in a project.
   *
   * Requires ADMIN role (either via implicit org OWNER/ADMIN or explicit project ADMIN).
   *
   * Requires: The target user must already be a member of the organization.
   * TODO: Add support for external collaborators (non-org members) later.
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to add the member to
   * @param args.data.memberId - The user to add as a member
   * @param args.data.role - The project role to assign
   * @returns The created membership
   * @throws PermissionDeniedError - If target is not an org member or self-invite (unless you are an org OWNER/ADMIN)
   * @throws AlreadyExistsError - If the user is already a member
   * @throws NotFoundError - If the project doesn't exist
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
    data: Pick<NewProjectMembership, "memberId" | "role">;
  }): Effect.Effect<
    PublicProjectMembership,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        projectId,
      });

      // NOTE: we do not need to block on self-invite because the user is either
      // already a project level ADMIN or they are an org OWNER/ADMIN, meaning
      // they can add themselves to the project.

      // Enforce organization membership before project membership
      // TODO: Support external collaborators via invite/collaborator model.
      const targetOrganizationMembership =
        yield* this.organizations.memberships.getMembership({
          userId: data.memberId,
          organizationId,
        });
      if (!targetOrganizationMembership) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message:
              "User must be a member of the organization before being added to a project",
            resource: "project membership",
          }),
        );
      }

      // TODO: Refactor Effect + Drizzle to reduce this boilerplate
      return yield* Effect.tryPromise({
        try: async () => {
          // Ensure audit log is created atomically with a transaction
          return await this.db.transaction(async (tx) => {
            const [membership] = await tx
              .insert(projectMemberships)
              .values({
                projectId,
                memberId: data.memberId,
                role: data.role,
              })
              .returning({
                projectId: projectMemberships.projectId,
                memberId: projectMemberships.memberId,
                role: projectMemberships.role,
                createdAt: projectMemberships.createdAt,
              });

            await tx.insert(projectMembershipAudit).values({
              projectId,
              actorId: userId,
              targetId: data.memberId,
              action: "GRANT",
              previousRole: null,
              newRole: data.role,
            });
            return membership as PublicProjectMembership;
          });
        },
        catch: (error) => {
          if (isUniqueConstraintError(error)) {
            return new AlreadyExistsError({
              message: "User is already a member of this project",
              resource: this.baseService.resourceName,
            });
          }
          return new DatabaseError({
            message: "Failed to create project membership",
            cause: error,
          });
        },
      });
    });
  }

  /**
   * Retrieves all memberships for a project.
   *
   * Requires project membership (any role) or implicit access from org OWNER/ADMIN.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to list memberships for
   * @returns Array of memberships with role and creation date
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
    PublicProjectMembership[],
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
      });
      return yield* this.baseService.findAll({ organizationId, projectId });
    });
  }

  /**
   * Retrieves a specific membership by member ID.
   *
   * Requires project membership (any role) or implicit access from org OWNER/ADMIN.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project
   * @param args.memberId - The user ID of the member to retrieve
   * @returns The membership with role and creation date
   * @throws NotFoundError - If the membership doesn't exist
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findById({
    userId,
    organizationId,
    projectId,
    memberId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    memberId: string;
  }): Effect.Effect<
    PublicProjectMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
      });
      return yield* this.baseService.findById({
        organizationId,
        projectId,
        memberId,
      });
    });
  }

  /**
   * Updates a membership's role.
   *
   * Requires ADMIN role (implicit org OWNER/ADMIN or explicit project ADMIN).
   * Cannot be used to:
   * - Change your own role (no self-modification)
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project
   * @param args.memberId - The user ID of the member to update
   * @param args.data - Fields to update (only `role` allowed)
   * @returns The updated membership
   * @throws PermissionDeniedError - If violating owner/self constraints
   * @throws NotFoundError - If the membership doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  update({
    userId,
    organizationId,
    projectId,
    memberId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    memberId: string;
    data: Pick<NewProjectMembership, "role">;
  }): Effect.Effect<
    PublicProjectMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
      });

      if (memberId === userId) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Cannot modify your own membership",
            resource: "project membership",
          }),
        );
      }

      const existing = yield* this.getMembership({
        memberId,
        organizationId,
        projectId,
      });
      if (!existing) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `User with id ${memberId} is not a member of this project`,
            resource: "project membership",
          }),
        );
      }

      return yield* Effect.tryPromise({
        try: async () => {
          return await this.db.transaction(async (tx) => {
            const [updated] = await tx
              .update(projectMemberships)
              .set({ role: data.role })
              .where(
                and(
                  eq(projectMemberships.projectId, projectId),
                  eq(projectMemberships.memberId, memberId),
                ),
              )
              .returning({
                projectId: projectMemberships.projectId,
                memberId: projectMemberships.memberId,
                role: projectMemberships.role,
                createdAt: projectMemberships.createdAt,
              });

            await tx.insert(projectMembershipAudit).values({
              projectId,
              actorId: userId,
              targetId: memberId,
              action: "CHANGE",
              previousRole: existing.role,
              newRole: data.role,
            });

            return updated as PublicProjectMembership;
          });
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to update project membership",
            cause: error,
          }),
      });
    });
  }

  /**
   * Removes a member from a project.
   *
   * Requires ADMIN role (implicit org OWNER/ADMIN or explicit project ADMIN).
   * Cannot be used to:
   * - Remove yourself (no self-removal)
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project
   * @param args.memberId - The user ID of the member to remove
   * @throws PermissionDeniedError - If trying to remove owner or self
   * @throws NotFoundError - If the membership doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  delete({
    userId,
    organizationId,
    projectId,
    memberId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    memberId: string;
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

      const existing = yield* this.getMembership({
        memberId,
        organizationId,
        projectId,
      });

      if (!existing) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `User with id ${memberId} is not a member of this project`,
            resource: "project membership",
          }),
        );
      }

      // DEVELOPER, VIEWER, and ANNOTATOR roles can delete themselves
      const cannotSelfDelete = memberId === userId && existing.role === "ADMIN";

      if (cannotSelfDelete) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Cannot remove yourself from a project",
            resource: "project membership",
          }),
        );
      }

      yield* Effect.tryPromise({
        try: async () => {
          await this.db.transaction(async (tx) => {
            await tx
              .delete(projectMemberships)
              .where(
                and(
                  eq(projectMemberships.projectId, projectId),
                  eq(projectMemberships.memberId, memberId),
                ),
              );

            await tx.insert(projectMembershipAudit).values({
              projectId,
              actorId: userId,
              targetId: memberId,
              action: "REVOKE",
              previousRole: existing.role,
              newRole: null,
            });
          });
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to delete project membership",
            cause: error,
          }),
      });
    });
  }
}
