import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";

/**
 * Project role schema - matches database enum.
 */
export const ProjectRoleSchema = Schema.Literal(
  "ADMIN",
  "DEVELOPER",
  "VIEWER",
  "ANNOTATOR",
);
export type ProjectRole = typeof ProjectRoleSchema.Type;

/**
 * Project member with user info - used for displaying project members.
 */
export const ProjectMemberWithUserSchema = Schema.Struct({
  memberId: Schema.String,
  email: Schema.String,
  name: Schema.NullOr(Schema.String),
  role: ProjectRoleSchema,
  createdAt: Schema.NullOr(Schema.Date),
});
export type ProjectMemberWithUser = typeof ProjectMemberWithUserSchema.Type;

/**
 * Request to add a member to a project.
 */
export const AddProjectMemberRequestSchema = Schema.Struct({
  memberId: Schema.String,
  role: ProjectRoleSchema,
});
export type AddProjectMemberRequest = typeof AddProjectMemberRequestSchema.Type;

/**
 * Request to update a project member's role.
 */
export const UpdateProjectMemberRoleRequestSchema = Schema.Struct({
  role: ProjectRoleSchema,
});
export type UpdateProjectMemberRoleRequest =
  typeof UpdateProjectMemberRoleRequestSchema.Type;

/**
 * Response for project membership operations.
 */
export const ProjectMembershipResponseSchema = Schema.Struct({
  memberId: Schema.String,
  organizationId: Schema.String,
  projectId: Schema.String,
  role: ProjectRoleSchema,
  createdAt: Schema.NullOr(Schema.Date),
});
export type ProjectMembershipResponse =
  typeof ProjectMembershipResponseSchema.Type;

export class ProjectMembershipsApi extends HttpApiGroup.make(
  "project-memberships",
)
  .add(
    HttpApiEndpoint.get(
      "list",
      "/organizations/:organizationId/projects/:projectId/members",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
        }),
      )
      .addSuccess(Schema.Array(ProjectMemberWithUserSchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "create",
      "/organizations/:organizationId/projects/:projectId/members",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
        }),
      )
      .setPayload(AddProjectMemberRequestSchema)
      .addSuccess(ProjectMembershipResponseSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.patch(
      "update",
      "/organizations/:organizationId/projects/:projectId/members/:memberId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          memberId: Schema.String,
        }),
      )
      .setPayload(UpdateProjectMemberRoleRequestSchema)
      .addSuccess(ProjectMembershipResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del(
      "delete",
      "/organizations/:organizationId/projects/:projectId/members/:memberId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          memberId: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
