/**
 * @fileoverview Effect-native Project Tags service.
 *
 * Provides authenticated CRUD operations for project tags with role-based access
 * control. Tags belong to projects and inherit authorization from the
 * project's membership system.
 *
 * ## Architecture
 *
 * ```
 * ProjectTags (authenticated)
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## Tag Roles
 *
 * Project tags use the project's role system:
 * - `ADMIN` - Full tag management (create, read, update, delete)
 * - `DEVELOPER` - Read-only access to tags
 * - `VIEWER` - Read-only access to tags
 * - `ANNOTATOR` - Read-only access to tags
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * (and thus all tags) within their organization.
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * const tag = yield* db.organizations.projects.tags.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   data: { name: "Bug" },
 * });
 * ```
 */

import { Effect } from "effect";
import { and, eq, desc, inArray } from "drizzle-orm";
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
  projectTags,
  type NewProjectTag,
  type PublicProjectTag,
  type ProjectRole,
} from "@/db/schema";

/**
 * Public fields to select from the project_tags table.
 */
const publicFields = {
  id: projectTags.id,
  name: projectTags.name,
  projectId: projectTags.projectId,
  organizationId: projectTags.organizationId,
  createdBy: projectTags.createdBy,
  createdAt: projectTags.createdAt,
  updatedAt: projectTags.updatedAt,
};

export type ProjectTagCreateData = Pick<NewProjectTag, "name">;

/**
 * Effect-native Project Tags service.
 *
 * Provides CRUD operations with role-based access control for tags.
 * Authorization is inherited from project membership via ProjectMemberships.getRole().
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
 * - Org OWNER/ADMIN have implicit project ADMIN access (and thus tag access)
 * - Non-members cannot see that a project/tag exists (returns NotFoundError)
 * - Tag names are unique within a project
 */
export class ProjectTags extends BaseAuthenticatedEffectService<
  PublicProjectTag,
  "organizations/:organizationId/projects/:projectId/tags/:tagId",
  ProjectTagCreateData,
  Partial<ProjectTagCreateData>,
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
    return "tag";
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
   * Determines the user's effective role for a project tag.
   *
   * Delegates to `ProjectMemberships.getRole` which handles:
   * - Org OWNER → treated as project ADMIN
   * - Org ADMIN → treated as project ADMIN
   * - Explicit project membership role
   * - No access → NotFoundError (hides tag existence)
   */
  getRole({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    tagId?: string;
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
   * Creates a new tag within a project.
   *
   * Requires ADMIN role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project to create the tag in
   * @param args.data - Tag data
   * @returns The created tag
   * @throws AlreadyExistsError - If a tag with this name exists in the project
   * @throws PermissionDeniedError - If the user lacks create permission
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
    data: ProjectTagCreateData;
  }): Effect.Effect<
    PublicProjectTag,
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
        tagId: "",
      });

      const newTag: NewProjectTag = {
        name: data.name,
        projectId,
        organizationId,
        createdBy: userId,
      };

      const [tag] = yield* client
        .insert(projectTags)
        .values(newTag)
        .returning(publicFields)
        .pipe(
          Effect.mapError((e) => {
            if (isUniqueConstraintError(e)) {
              return new AlreadyExistsError({
                message: `Tag with name ${data.name} already exists in this project`,
                resource: "tag",
              });
            }
            return new DatabaseError({
              message: "Failed to create tag",
              cause: e,
            });
          }),
        );

      return tag;
    });
  }

  /**
   * Retrieves all tags in a project.
   *
   * Requires any role on the project (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
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
    PublicProjectTag[],
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
        tagId: "",
      });

      return yield* client
        .select(publicFields)
        .from(projectTags)
        .where(
          and(
            eq(projectTags.projectId, projectId),
            eq(projectTags.organizationId, organizationId),
          ),
        )
        .orderBy(desc(projectTags.createdAt))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to list tags",
                cause: e,
              }),
          ),
        );
    });
  }

  /**
   * Retrieves a tag by ID.
   *
   * Requires any role on the project (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   */
  findById({
    userId,
    organizationId,
    projectId,
    tagId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    tagId: string;
  }): Effect.Effect<
    PublicProjectTag,
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
        tagId,
      });

      const [tag] = yield* client
        .select(publicFields)
        .from(projectTags)
        .where(
          and(eq(projectTags.id, tagId), eq(projectTags.projectId, projectId)),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get tag",
                cause: e,
              }),
          ),
        );

      if (!tag) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Tag with id ${tagId} not found`,
            resource: "tag",
          }),
        );
      }

      return tag;
    });
  }

  /**
   * Updates a tag.
   *
   * Requires ADMIN role on the project.
   */
  update({
    userId,
    organizationId,
    projectId,
    tagId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    tagId: string;
    data: Partial<ProjectTagCreateData>;
  }): Effect.Effect<
    PublicProjectTag,
    NotFoundError | PermissionDeniedError | DatabaseError | AlreadyExistsError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        tagId,
      });

      const [updated] = yield* client
        .update(projectTags)
        .set({ ...data, updatedAt: new Date() })
        .where(
          and(eq(projectTags.id, tagId), eq(projectTags.projectId, projectId)),
        )
        .returning(publicFields)
        .pipe(
          Effect.mapError((e) => {
            if (isUniqueConstraintError(e)) {
              return new AlreadyExistsError({
                message: `Tag with name ${data.name ?? ""} already exists in this project`,
                resource: "tag",
              });
            }
            return new DatabaseError({
              message: "Failed to update tag",
              cause: e,
            });
          }),
        );

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Tag with id ${tagId} not found`,
            resource: "tag",
          }),
        );
      }

      return updated;
    });
  }

  /**
   * Deletes a tag.
   *
   * Requires ADMIN role on the project.
   */
  delete({
    userId,
    organizationId,
    projectId,
    tagId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    tagId: string;
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
        tagId,
      });

      const [deleted] = yield* client
        .delete(projectTags)
        .where(
          and(eq(projectTags.id, tagId), eq(projectTags.projectId, projectId)),
        )
        .returning({ id: projectTags.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete tag",
                cause: e,
              }),
          ),
        );

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Tag with id ${tagId} not found`,
            resource: "tag",
          }),
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  /**
   * Validates a list of tag names and returns the matching tags.
   *
   * @throws NotFoundError - If any tag names do not exist in the project
   */
  findByNames({
    userId,
    organizationId,
    projectId,
    names,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    names: string[];
  }): Effect.Effect<
    PublicProjectTag[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      if (names.length === 0) {
        return [];
      }

      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        tagId: "",
      });

      const uniqueNames = Array.from(new Set(names));

      const results: PublicProjectTag[] = yield* client
        .select(publicFields)
        .from(projectTags)
        .where(
          and(
            eq(projectTags.projectId, projectId),
            eq(projectTags.organizationId, organizationId),
            inArray(projectTags.name, uniqueNames),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to validate tags",
                cause: e,
              }),
          ),
        );

      const foundNames = new Set(results.map((tag) => tag.name));
      const missingNames = uniqueNames.filter((name) => !foundNames.has(name));

      if (missingNames.length > 0) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Tags not found: ${missingNames.join(", ")}`,
            resource: "tag",
          }),
        );
      }

      return results;
    });
  }
}
