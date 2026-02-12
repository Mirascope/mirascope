/**
 * @fileoverview Effect-native Projects service.
 *
 * Provides authenticated CRUD operations for projects with role-based access
 * control. Projects belong to organizations and have their own membership
 * system for fine-grained access control.
 *
 * ## Architecture
 *
 * ```
 * Projects (authenticated)
 *   └── memberships: ProjectMemberships
 *         └── CRUD on `project_memberships` table (authenticated)
 * ```
 *
 * ## Project Roles
 *
 * Projects support four roles:
 * - `ADMIN` - Full project management (create, read, update, delete)
 * - `DEVELOPER` - Read-only access to project info
 * - `VIEWER` - Read-only access to project info
 * - `ANNOTATOR` - Read-only access to project info
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * within their organization, even without explicit project membership.
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Create a project (creator becomes project ADMIN)
 * const project = yield* db.organizations.projects.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   data: { name: "My Project" },
 * });
 *
 * // List accessible projects
 * const projects = yield* db.organizations.projects.findAll({
 *   userId: "user-123",
 *   organizationId: "org-456",
 * });
 * ```
 */

import { and, eq, sql } from "drizzle-orm";
import { Effect } from "effect";

import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { OrganizationMemberships } from "@/db/organization-memberships";
import { ProjectMemberships } from "@/db/project-memberships";
import {
  claws,
  projects,
  projectMemberships,
  type NewProject,
  type PublicProject,
  type ProjectRole,
} from "@/db/schema";
import { isUniqueConstraintError } from "@/db/utils";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
  StripeError,
} from "@/errors";
import { Payments } from "@/payments";

/**
 * Public fields to select from the projects table.
 */
const publicFields = {
  id: projects.id,
  name: projects.name,
  slug: projects.slug,
  organizationId: projects.organizationId,
  createdByUserId: projects.createdByUserId,
  type: projects.type,
};

/**
 * Effect-native Projects service.
 *
 * Provides CRUD operations with role-based access control for projects.
 * Organization OWNER/ADMIN roles have implicit ADMIN access to all projects.
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓*    | ✗         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✓      | ✓        |
 * | update   | ✓     | ✗         | ✗      | ✗         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 *
 * *Create is a special case: requires org OWNER/ADMIN, creator becomes project ADMIN.
 *
 * ## Security Model
 *
 * - Org OWNER/ADMIN have implicit project ADMIN access
 * - Non-members cannot see that a project exists (returns NotFoundError)
 * - Creator is automatically added as project ADMIN
 */
export class Projects extends BaseAuthenticatedEffectService<
  PublicProject,
  "organizations/:organizationId/projects/:projectId",
  Pick<NewProject, "name" | "slug">,
  Partial<Pick<NewProject, "name" | "slug">>,
  ProjectRole
> {
  /**
   * Service for managing project memberships.
   */
  public readonly memberships: ProjectMemberships;

  private readonly organizationMemberships: OrganizationMemberships;

  constructor(
    organizationMemberships: OrganizationMemberships,
    projectMemberships: ProjectMemberships,
  ) {
    super();
    this.organizationMemberships = organizationMemberships;
    this.memberships = projectMemberships;
  }

  // ---------------------------------------------------------------------------
  // Project Limit Enforcement
  // ---------------------------------------------------------------------------

  /**
   * Checks if creating a new project would exceed the organization's plan limits.
   *
   * @param organizationId - The organization to check limits for
   * @returns Effect that succeeds if under limit, fails with PlanLimitExceededError if at/over limit
   */
  private checkProjectLimit({
    organizationId,
  }: {
    organizationId: string;
  }): Effect.Effect<
    void,
    PlanLimitExceededError | DatabaseError | NotFoundError | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const payments = yield* Payments;

      // Get current plan and limits
      const planTier =
        yield* payments.customers.subscriptions.getPlan(organizationId);
      const limits =
        yield* payments.customers.subscriptions.getPlanLimits(planTier);

      // Count active projects (exclude claw_home projects)
      const [projectCount] = yield* client
        .select({ count: sql<number>`count(*)::int` })
        .from(projects)
        .where(
          and(
            eq(projects.organizationId, organizationId),
            eq(projects.type, "standard"),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to count projects",
                cause: e,
              }),
          ),
        );

      if (projectCount.count >= limits.projects) {
        return yield* Effect.fail(
          new PlanLimitExceededError({
            message: `Cannot create project: ${planTier} plan limit is ${limits.projects} project(s)`,
            resource: "projects",
            limitType: "projects",
            currentUsage: projectCount.count,
            limit: limits.projects,
            planTier,
          }),
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Base Implementation
  // ---------------------------------------------------------------------------

  protected getResourceName(): string {
    return "project";
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN"], // Org OWNER/ADMIN is cast to project ADMIN
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
   * Delegates to `ProjectMemberships.getRole` which handles:
   * - Org OWNER → treated as project ADMIN
   * - Org ADMIN → treated as project ADMIN
   * - Explicit project membership role
   * - No access → NotFoundError (hides project existence)
   */
  getRole({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
  }): Effect.Effect<
    ProjectRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const { role } = yield* this.memberships.findById({
        userId,
        organizationId,
        projectId,
        memberId: userId,
      });
      return role;
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
   * @param args.data - Project data
   * @returns The created project
   * @throws PermissionDeniedError - If user lacks org OWNER/ADMIN role
   * @throws DatabaseError - If the database operation fails
   */
  create({
    userId,
    organizationId,
    data,
  }: {
    userId: string;
    organizationId: string;
    data: Pick<NewProject, "name" | "slug">;
  }): Effect.Effect<
    PublicProject,
    | NotFoundError
    | PermissionDeniedError
    | AlreadyExistsError
    | DatabaseError
    | PlanLimitExceededError
    | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Must be org OWNER/ADMIN to create projects.
      // Note: org non-members get NotFoundError via org role resolution.
      const { role: orgRole } = yield* this.organizationMemberships.findById({
        userId,
        organizationId,
        memberId: userId,
      });

      if (orgRole !== "OWNER" && orgRole !== "ADMIN") {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message:
              "You do not have permission to create projects in this organization",
            resource: this.getResourceName(),
          }),
        );
      }

      // Check project limit before creating
      yield* this.checkProjectLimit({ organizationId });

      // Use transaction to ensure project, membership, and audit are created atomically
      return yield* client.withTransaction(
        Effect.gen(this, function* () {
          const [project] = yield* client
            .insert(projects)
            .values({
              name: data.name,
              slug: data.slug,
              organizationId,
              createdByUserId: userId,
            })
            .returning(publicFields)
            .pipe(
              Effect.mapError((e): AlreadyExistsError | DatabaseError =>
                isUniqueConstraintError(e.cause)
                  ? new AlreadyExistsError({
                      message:
                        "A project with this slug already exists in this organization",
                      resource: "project",
                    })
                  : new DatabaseError({
                      message: "Failed to create project",
                      cause: e,
                    }),
              ),
            );

          // Add creator as explicit project ADMIN with audit log
          yield* this.memberships.create({
            userId,
            organizationId,
            projectId: project.id,
            data: { memberId: userId, role: "ADMIN" },
          });

          return project as PublicProject;
        }),
      );
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
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Get org role (also verifies org membership / hides org existence)
      const { role: orgRole } = yield* this.organizationMemberships.findById({
        userId,
        organizationId,
        memberId: userId,
      });

      // Org OWNER/ADMIN see all projects
      const isOrgPrivileged = orgRole === "OWNER" || orgRole === "ADMIN";

      if (isOrgPrivileged) {
        const results: PublicProject[] = yield* client
          .select(publicFields)
          .from(projects)
          .where(eq(projects.organizationId, organizationId))
          .pipe(
            Effect.mapError(
              (e) =>
                new DatabaseError({
                  message: "Failed to find all projects",
                  cause: e,
                }),
            ),
          );

        return results;
      }

      // Others only see projects they're members of
      const results: PublicProject[] = yield* client
        .select(publicFields)
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
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all projects",
                cause: e,
              }),
          ),
        );

      return results;
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
      });

      const [project] = yield* client
        .select(publicFields)
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
                message: "Failed to find project",
                cause: e,
              }),
          ),
        );

      if (!project) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Project with projectId ${projectId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return project;
    });
  }

  /**
   * Updates a project.
   *
   * Requires ADMIN role on the project (or org OWNER/ADMIN).
   * Only the name can be updated.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to update
   * @param args.data - Fields to update
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
    data: Partial<Pick<NewProject, "name" | "slug">>;
  }): Effect.Effect<
    PublicProject,
    NotFoundError | PermissionDeniedError | AlreadyExistsError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
      });

      const [updated] = yield* client
        .update(projects)
        .set({ ...data, updatedAt: new Date() })
        .where(
          and(
            eq(projects.id, projectId),
            eq(projects.organizationId, organizationId),
          ),
        )
        .returning(publicFields)
        .pipe(
          Effect.mapError((e): AlreadyExistsError | DatabaseError =>
            isUniqueConstraintError(e.cause)
              ? new AlreadyExistsError({
                  message:
                    "A project with this slug already exists in this organization",
                  resource: "project",
                })
              : new DatabaseError({
                  message: "Failed to update project",
                  cause: e,
                }),
          ),
        );

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Project with projectId ${projectId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return updated;
    });
  }

  /**
   * Deletes a project.
   *
   * Requires ADMIN role on the project (or org OWNER/ADMIN).
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
      });

      // Prevent direct deletion of claw_home projects that still have an
      // active claw. These should only be deleted via the claw deletion
      // cascade. Orphaned claw_home projects (where the claw has already
      // been deleted) can be cleaned up directly.
      const [project] = yield* client
        .select({ id: projects.id, type: projects.type })
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
                message: "Failed to fetch project",
                cause: e,
              }),
          ),
        );

      if (!project) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Project with projectId ${projectId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      if (project.type === "claw_home") {
        // Check if a claw still references this project
        const [activeClaw] = yield* client
          .select({ id: claws.id })
          .from(claws)
          .where(eq(claws.homeProjectId, projectId))
          .limit(1)
          .pipe(
            Effect.mapError(
              (e) =>
                new DatabaseError({
                  message: "Failed to check claw association",
                  cause: e,
                }),
            ),
          );

        if (activeClaw) {
          return yield* Effect.fail(
            new PermissionDeniedError({
              message:
                "Cannot delete a claw home project directly. Delete the claw instead.",
            }),
          );
        }
      }

      const [deleted] = yield* client
        .delete(projects)
        .where(
          and(
            eq(projects.id, projectId),
            eq(projects.organizationId, organizationId),
          ),
        )
        .returning({ id: projects.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete project",
                cause: e,
              }),
          ),
        );

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Project with projectId ${projectId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }
    });
  }
}
