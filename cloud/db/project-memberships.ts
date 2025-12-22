/**
 * @fileoverview Effect-native Project Memberships service.
 *
 * Provides authenticated CRUD operations for project memberships with
 * role-based access control. Memberships define the relationship between
 * users and projects within an organization.
 *
 * ## Project Roles
 *
 * Projects support four roles:
 * - `ADMIN` - Can manage project memberships (create, read, update, delete)
 * - `DEVELOPER` - Read-only access to membership info (read)
 * - `VIEWER` - Read-only access to membership info (read)
 * - `ANNOTATOR` - No access (will have access to the annotation queue)
 *
 * NOTE: At the project level, the `DEVELOPER` and `VIEWER` roles are equivalent (read-only).
 * However, these roles will have more granular permissions for project resources
 * (e.g. environments, API keys, traces, etc.).
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
 * @example
 * ```ts
 * const db = yield* EffectDatabase;
 *
 * // Add a developer to a project
 * const membership = yield* db.projects.memberships.create({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   data: { memberId: "new-user", role: "DEVELOPER" },
 * });
 *
 * // List all project members
 * const members = yield* db.projects.memberships.findAll({
 *   userId: "admin-123",
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
import { OrganizationMemberships } from "@/db/organization-memberships";
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
  type ProjectRole,
} from "@/db/schema";

/**
 * Public fields to select from the project_memberships table.
 */
const publicFields = {
  memberId: projectMemberships.memberId,
  projectId: projectMemberships.projectId,
  role: projectMemberships.role,
  createdAt: projectMemberships.createdAt,
};

/**
 * Public fields to select from the project_membership_audit table.
 */
const auditPublicFields = {
  id: projectMembershipAudit.id,
  actorId: projectMembershipAudit.actorId,
  targetId: projectMembershipAudit.targetId,
  action: projectMembershipAudit.action,
  previousRole: projectMembershipAudit.previousRole,
  newRole: projectMembershipAudit.newRole,
  createdAt: projectMembershipAudit.createdAt,
};

// =============================================================================
// Audit Service (Internal, used by tests)
// =============================================================================

/**
 * Read-only service for project membership audit logs.
 *
 * This service is used primarily in tests to verify that audit entries
 * were created correctly after membership operations.
 */
class ProjectMembershipAudits {
  /**
   * Retrieves all audit entries for a specific member in a project.
   */
  findAll({
    projectId,
    memberId,
  }: {
    projectId: string;
    memberId: string;
  }): Effect.Effect<PublicProjectMembershipAudit[], DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      return yield* client
        .select(auditPublicFields)
        .from(projectMembershipAudit)
        .where(
          and(
            eq(projectMembershipAudit.projectId, projectId),
            eq(projectMembershipAudit.targetId, memberId),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find audit entries",
                cause: e,
              }),
          ),
        );
    });
  }
}

/**
 * Insert type for creating project memberships.
 */
type InsertMembership = { memberId: string; role: ProjectRole };

/**
 * Update type for project membership role changes.
 */
type UpdateMembership = { role: ProjectRole };

/**
 * Effect-native Project Memberships service.
 *
 * Provides CRUD operations with role-based access control for project memberships.
 * Organization OWNER/ADMIN roles have implicit ADMIN access to all projects.
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
 * - ADMIN can modify their own membership; non-ADMIN cannot
 * - All roles can remove themselves from a project
 * - Target must already be an org member (TODO: external collaborators)
 */
export class ProjectMemberships extends BaseAuthenticatedEffectService<
  PublicProjectMembership,
  "organizations/:organizationId/projects/:projectId/members/:memberId",
  InsertMembership,
  UpdateMembership,
  ProjectRole
> {
  /**
   * Audit log service for project membership changes.
   * Used primarily in tests to verify audit entries.
   */
  public readonly audits = new ProjectMembershipAudits();

  private readonly organizationMemberships: OrganizationMemberships;

  constructor(organizationMemberships: OrganizationMemberships) {
    super();
    this.organizationMemberships = organizationMemberships;
  }

  // ---------------------------------------------------------------------------
  // Base Implementation
  // ---------------------------------------------------------------------------

  protected getResourceName(): string {
    return "project membership";
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN"],
      read: ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"],
      update: ["ADMIN"],
      delete: ["ADMIN"],
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Fetches a project membership record from the database.
   *
   * @throws NotFoundError - If the user is not a member of the project
   * @throws DatabaseError - If the database query fails
   */
  protected getMembership({
    memberId,
    organizationId,
    projectId,
  }: {
    memberId: string;
    organizationId: string;
    projectId: string;
  }): Effect.Effect<
    { role: ProjectRole },
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const [membership] = yield* client
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
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get project membership",
                cause: e,
              }),
          ),
        );

      if (!membership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User is not a member of this project",
            resource: this.getResourceName(),
          }),
        );
      }

      return membership;
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
  protected getRole({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    memberId?: string;
  }): Effect.Effect<
    ProjectRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // If the user is not part of the organization, then they couldn't
      // be a member of the project and will get rejected.
      const { role: userOrganizationRole } =
        yield* this.organizationMemberships.findById({
          organizationId,
          userId,
          memberId: userId,
        });

      // Org OWNER/ADMIN have implicit project ADMIN access
      if (
        userOrganizationRole === "OWNER" ||
        userOrganizationRole === "ADMIN"
      ) {
        yield* this.verifyProjectExists(organizationId, projectId);
        return "ADMIN";
      }

      // Check explicit project membership
      const { role } = yield* this.getMembership({
        memberId: userId,
        organizationId,
        projectId,
      }).pipe(
        Effect.catchTag("NotFoundError", () =>
          Effect.fail(
            new NotFoundError({
              message: "Project not found",
              resource: this.getResourceName(),
            }),
          ),
        ),
      );

      return role;
    });
  }

  /**
   * Verifies that a project exists within the specified organization.
   */
  private verifyProjectExists(
    organizationId: string,
    projectId: string,
  ): Effect.Effect<void, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [project] = yield* client
        .select({ id: projects.id })
        .from(projects)
        .where(
          and(
            eq(projects.id, projectId),
            eq(projects.organizationId, organizationId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to verify project",
                cause: e,
              }),
          ),
        );

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
   * The target user must already be a member of the organization.
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to add the member to
   * @param args.data.memberId - The user to add as a member
   * @param args.data.role - The project role to assign
   * @returns The created membership
   * @throws PermissionDeniedError - If target is not an org member or lacks permission
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
    data: InsertMembership;
  }): Effect.Effect<
    PublicProjectMembership,
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
        memberId: userId,
      });

      // NOTE: We do not need to block on self-invite because the user is either
      // already a project level ADMIN or they are an org OWNER/ADMIN, meaning
      // they can add themselves to the project.

      // Enforce organization membership before project membership
      yield* this.organizationMemberships
        .findById({
          userId,
          organizationId,
          memberId: data.memberId,
        })
        .pipe(
          Effect.catchTag("NotFoundError", () =>
            Effect.fail(
              new PermissionDeniedError({
                message:
                  "User must be a member of the organization before being added to a project",
                resource: this.getResourceName(),
              }),
            ),
          ),
        );

      // Use transaction to ensure membership and audit log are created atomically
      return yield* client.withTransaction(
        Effect.gen(function* () {
          const [membership] = yield* client
            .insert(projectMemberships)
            .values({
              projectId,
              memberId: data.memberId,
              role: data.role,
            })
            .returning(publicFields)
            .pipe(
              Effect.mapError((e): AlreadyExistsError | DatabaseError =>
                isUniqueConstraintError(e.cause)
                  ? new AlreadyExistsError({
                      message: "User is already a member of this project",
                      resource: "project membership",
                    })
                  : new DatabaseError({
                      message: "Failed to create project membership",
                      cause: e,
                    }),
              ),
            );

          yield* client
            .insert(projectMembershipAudit)
            .values({
              projectId,
              actorId: userId,
              targetId: data.memberId,
              action: "GRANT",
              newRole: data.role,
            })
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to create audit log",
                    cause: e,
                  }),
              ),
            );

          return membership as PublicProjectMembership;
        }),
      );
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
        memberId: userId,
      });

      return yield* client
        .select(publicFields)
        .from(projectMemberships)
        .where(eq(projectMemberships.projectId, projectId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all project memberships",
                cause: e,
              }),
          ),
        );
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
        memberId: userId,
      });

      const [membership] = yield* client
        .select(publicFields)
        .from(projectMemberships)
        .where(
          and(
            eq(projectMemberships.projectId, projectId),
            eq(projectMemberships.memberId, memberId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find project membership",
                cause: e,
              }),
          ),
        );

      if (!membership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Membership for member ${memberId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return membership;
    });
  }

  /**
   * Updates a membership's role.
   *
   * Requires ADMIN role (implicit org OWNER/ADMIN or explicit project ADMIN).
   * ADMIN roles can modify their own membership. Non-ADMIN roles cannot modify their own membership.
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project
   * @param args.memberId - The user ID of the member to update
   * @param args.data - Fields to update (only `role` allowed)
   * @returns The updated membership
   * @throws PermissionDeniedError - If non-ADMIN tries to modify their own membership
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
    data: UpdateMembership;
  }): Effect.Effect<
    PublicProjectMembership,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        memberId: userId,
      });

      // NOTE: at this point the user is an ADMIN, so we don't need to
      // do anything special around self-updates since ADMIN is allowed

      const existing = yield* this.getMembership({
        memberId,
        organizationId,
        projectId,
      });

      return yield* client.withTransaction(
        Effect.gen(function* () {
          const [membership] = yield* client
            .update(projectMemberships)
            .set({ role: data.role })
            .where(
              and(
                eq(projectMemberships.projectId, projectId),
                eq(projectMemberships.memberId, memberId),
              ),
            )
            .returning(publicFields)
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to update project membership",
                    cause: e,
                  }),
              ),
            );

          yield* client
            .insert(projectMembershipAudit)
            .values({
              projectId,
              actorId: userId,
              targetId: memberId,
              action: "CHANGE",
              previousRole: existing.role,
              newRole: data.role,
            })
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to create audit log",
                    cause: e,
                  }),
              ),
            );

          return membership as PublicProjectMembership;
        }),
      );
    });
  }

  /**
   * Removes a member from a project.
   *
   * Requires ADMIN role (implicit org OWNER/ADMIN or explicit project ADMIN).
   * All roles, including ADMIN, can remove themselves from a project.
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project
   * @param args.memberId - The user ID of the member to remove
   * @throws NotFoundError - If the membership doesn't exist
   * @throws PermissionDeniedError - If the user lacks delete permission
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
        memberId: userId,
      });

      const existing = yield* this.getMembership({
        memberId,
        organizationId,
        projectId,
      });

      yield* client.withTransaction(
        Effect.gen(function* () {
          yield* client
            .delete(projectMemberships)
            .where(
              and(
                eq(projectMemberships.projectId, projectId),
                eq(projectMemberships.memberId, memberId),
              ),
            )
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to delete project membership",
                    cause: e,
                  }),
              ),
            );

          yield* client
            .insert(projectMembershipAudit)
            .values({
              projectId,
              actorId: userId,
              targetId: memberId,
              action: "REVOKE",
              previousRole: existing.role,
            })
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to create audit log",
                    cause: e,
                  }),
              ),
            );
        }),
      );
    });
  }
}
