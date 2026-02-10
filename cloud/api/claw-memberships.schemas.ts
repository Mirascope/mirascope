import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";

/**
 * Claw role schema - matches database enum.
 */
export const ClawRoleSchema = Schema.Literal(
  "ADMIN",
  "DEVELOPER",
  "VIEWER",
  "ANNOTATOR",
);
export type ClawRole = typeof ClawRoleSchema.Type;

/**
 * Claw member with user info - used for displaying claw members.
 */
export const ClawMemberWithUserSchema = Schema.Struct({
  memberId: Schema.String,
  email: Schema.String,
  name: Schema.NullOr(Schema.String),
  role: ClawRoleSchema,
  createdAt: Schema.NullOr(Schema.Date),
});
export type ClawMemberWithUser = typeof ClawMemberWithUserSchema.Type;

/**
 * Request to add a member to a claw.
 */
export const AddClawMemberRequestSchema = Schema.Struct({
  memberId: Schema.String,
  role: ClawRoleSchema,
});
export type AddClawMemberRequest = typeof AddClawMemberRequestSchema.Type;

/**
 * Request to update a claw member's role.
 */
export const UpdateClawMemberRoleRequestSchema = Schema.Struct({
  role: ClawRoleSchema,
});
export type UpdateClawMemberRoleRequest =
  typeof UpdateClawMemberRoleRequestSchema.Type;

/**
 * Response for claw membership operations.
 */
export const ClawMembershipResponseSchema = Schema.Struct({
  memberId: Schema.String,
  organizationId: Schema.String,
  clawId: Schema.String,
  role: ClawRoleSchema,
  createdAt: Schema.NullOr(Schema.Date),
});
export type ClawMembershipResponse = typeof ClawMembershipResponseSchema.Type;

export class ClawMembershipsApi extends HttpApiGroup.make("claw-memberships")
  .add(
    HttpApiEndpoint.get(
      "list",
      "/organizations/:organizationId/claws/:clawId/members",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          clawId: Schema.String,
        }),
      )
      .addSuccess(Schema.Array(ClawMemberWithUserSchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "create",
      "/organizations/:organizationId/claws/:clawId/members",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          clawId: Schema.String,
        }),
      )
      .setPayload(AddClawMemberRequestSchema)
      .addSuccess(ClawMembershipResponseSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get(
      "get",
      "/organizations/:organizationId/claws/:clawId/members/:memberId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          clawId: Schema.String,
          memberId: Schema.String,
        }),
      )
      .addSuccess(ClawMembershipResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.patch(
      "update",
      "/organizations/:organizationId/claws/:clawId/members/:memberId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          clawId: Schema.String,
          memberId: Schema.String,
        }),
      )
      .setPayload(UpdateClawMemberRoleRequestSchema)
      .addSuccess(ClawMembershipResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del(
      "delete",
      "/organizations/:organizationId/claws/:clawId/members/:memberId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          clawId: Schema.String,
          memberId: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
