import { Effect } from "effect";
import { and, eq, isNotNull } from "drizzle-orm";
import {
  BaseService,
  BaseAuthenticatedService,
  type PermissionTable,
} from "@/db/services/base";
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
  type NewProject,
  type PublicProject,
  type PublicProjectMembership,
  type Role,
} from "@/db/schema";

class ProjectBaseService extends BaseService<
  PublicProject,
  string,
  typeof projects
> {
  protected getTable() {
    return projects;
  }

  protected getResourceName() {
    return "project";
  }

  protected getPublicFields() {
    return {
      id: projects.id,
      name: projects.name,
      userOwnerId: projects.userOwnerId,
      orgOwnerId: projects.orgOwnerId,
    };
  }
}

/**
 * Input type for creating a project.
 * Exactly one of userOwnerId or orgOwnerId must be provided (enforced by database CHECK constraint).
 */
export class ProjectService extends BaseAuthenticatedService<
  PublicProject,
  string,
  typeof projects,
  NewProject,
  Role
> {
  protected initializeBaseService() {
    return new ProjectBaseService(this.db);
  }

  protected getPermissionTable(): PermissionTable<Role> {
    return {
      create: ["OWNER", "ADMIN"],
      read: ["OWNER", "ADMIN", "DEVELOPER", "ANNOTATOR"],
      update: ["OWNER", "ADMIN"],
      delete: ["OWNER"],
    };
  }

  /**
   * Get the user's role for a project from project_memberships.
   * Returns NotFoundError if user is not a member (hides project existence from non-members).
   */
  getRole({
    id,
    userId,
  }: {
    id: string;
    userId: string;
  }): Effect.Effect<Role, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const membership = yield* Effect.tryPromise({
        try: async () => {
          const [membership] = await this.db
            .select({ role: projectMemberships.role })
            .from(projectMemberships)
            .where(
              and(
                eq(projectMemberships.projectId, id),
                eq(projectMemberships.userId, userId),
              ),
            )
            .limit(1);
          return membership;
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to get project membership",
            cause: error,
          }),
      });

      if (!membership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Project not found",
            resource: this.baseService.resourceName,
          }),
        );
      }
      return membership.role;
    });
  }

  /**
   * Create a new project and add the creator as OWNER in project_memberships.
   * No permission check needed - any authenticated user can create a project.
   * Note: createdByUserId is set from the authenticated userId, not from data.
   *
   * Exactly one of userOwnerId or orgOwnerId must be provided.
   * Foreign key constraints ensure the owner exists.
   */
  create({
    data,
    userId,
  }: {
    data: Pick<NewProject, "name" | "userOwnerId" | "orgOwnerId">;
    userId: string;
  }): Effect.Effect<PublicProject, AlreadyExistsError | DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        return await this.db.transaction(async (tx) => {
          const [project] = await tx
            .insert(projects)
            .values({
              name: data.name,
              userOwnerId: data.userOwnerId ?? null,
              orgOwnerId: data.orgOwnerId ?? null,
              createdByUserId: userId,
            })
            .returning({
              id: projects.id,
              name: projects.name,
              userOwnerId: projects.userOwnerId,
              orgOwnerId: projects.orgOwnerId,
            });

          // Add creator to project_memberships as OWNER
          await tx.insert(projectMemberships).values({
            projectId: project.id,
            userId,
            role: "OWNER",
          });

          return project;
        });
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to create project",
          cause: error,
        }),
    });
  }

  /**
   * Find all projects the user has access to via project_memberships.
   */
  findAll({
    userId,
  }: {
    userId: string;
  }): Effect.Effect<PublicProject[], DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        return await this.db
          .select({
            id: projects.id,
            name: projects.name,
            userOwnerId: projects.userOwnerId,
            orgOwnerId: projects.orgOwnerId,
          })
          .from(projects)
          .innerJoin(
            projectMemberships,
            eq(projects.id, projectMemberships.projectId),
          )
          .where(eq(projectMemberships.userId, userId));
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to get user projects",
          cause: error,
        }),
    });
  }

  /**
   * Find a project by ID with permission check via project_memberships.
   */
  findById({
    id,
    userId,
  }: {
    id: string;
    userId: string;
  }): Effect.Effect<
    PublicProject,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ id, userId, action: "read" });
      return yield* this.baseService.findById({ id });
    });
  }

  /**
   * Update a project with permission check.
   */
  update({
    id,
    data,
    userId,
  }: {
    id: string;
    data: Partial<NewProject>;
    userId: string;
  }): Effect.Effect<
    PublicProject,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ id, userId, action: "update" });
      return yield* this.baseService.update({ id, data });
    });
  }

  /**
   * Delete a project with permission check.
   * Also deletes all project_memberships via cascade.
   */
  delete({
    id,
    userId,
  }: {
    id: string;
    userId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ id, userId, action: "delete" });
      yield* this.baseService.delete({ id });
    });
  }

  /**
   * Find all projects owned by an organization.
   * Requires the user to have access to at least one project in the organization
   * (or we could check org membership - keeping it simple for now by just filtering).
   */
  findByOrganization({
    organizationId,
    userId,
  }: {
    organizationId: string;
    userId: string;
  }): Effect.Effect<PublicProject[], DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        // Get projects owned by this organization that the user has access to
        return await this.db
          .select({
            id: projects.id,
            name: projects.name,
            userOwnerId: projects.userOwnerId,
            orgOwnerId: projects.orgOwnerId,
          })
          .from(projects)
          .innerJoin(
            projectMemberships,
            eq(projects.id, projectMemberships.projectId),
          )
          .where(
            and(
              isNotNull(projects.orgOwnerId),
              eq(projects.orgOwnerId, organizationId),
              eq(projectMemberships.userId, userId),
            ),
          );
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to get organization projects",
          cause: error,
        }),
    });
  }

  /**
   * Add a member to a project with a specified role.
   * Requires OWNER or ADMIN permission on the project.
   */
  addMember({
    id,
    memberUserId,
    role,
    userId,
  }: {
    id: string;
    memberUserId: string;
    role: Role;
    userId: string;
  }): Effect.Effect<
    PublicProjectMembership,
    NotFoundError | PermissionDeniedError | AlreadyExistsError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ id, userId, action: "update" });

      const membership = yield* Effect.tryPromise({
        try: async () => {
          const [membership] = await this.db
            .insert(projectMemberships)
            .values({
              projectId: id,
              userId: memberUserId,
              role,
            })
            .returning({
              id: projectMemberships.id,
              projectId: projectMemberships.projectId,
              userId: projectMemberships.userId,
              role: projectMemberships.role,
              createdAt: projectMemberships.createdAt,
            });
          return membership;
        },
        catch: (error) => {
          if (isUniqueConstraintError(error)) {
            return new AlreadyExistsError({
              message: "User is already a member of this project",
            });
          }
          return new DatabaseError({
            message: "Failed to add project member",
            cause: error,
          });
        },
      });

      return membership;
    });
  }

  /**
   * Remove a member from a project.
   * Requires OWNER or ADMIN permission on the project.
   */
  terminateMember({
    id,
    memberUserId,
    userId,
  }: {
    id: string;
    memberUserId: string;
    userId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ id, userId, action: "update" });

      const deleted = yield* Effect.tryPromise({
        try: async () => {
          const result = await this.db
            .delete(projectMemberships)
            .where(
              and(
                eq(projectMemberships.projectId, id),
                eq(projectMemberships.userId, memberUserId),
              ),
            )
            .returning({ id: projectMemberships.id });
          return result.length > 0;
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to remove project member",
            cause: error,
          }),
      });

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User is not a member of this project",
            resource: "project_membership",
          }),
        );
      }
    });
  }
}
