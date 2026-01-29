import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

import { OrganizationRoleSchema } from "@/api/organizations.schemas";
import { DatabaseError, NotFoundError, PermissionDeniedError } from "@/errors";

// Re-export OrganizationRole for convenience
export type OrganizationRole = typeof OrganizationRoleSchema.Type;

/**
 * Roles that can be assigned via update operations (excludes OWNER).
 */
export const AssignableRoleSchema = Schema.Literal("ADMIN", "MEMBER");
export type AssignableRole = typeof AssignableRoleSchema.Type;

/**
 * Organization member with user info - used for displaying team members.
 */
export const OrganizationMemberWithUserSchema = Schema.Struct({
  memberId: Schema.String,
  email: Schema.String,
  name: Schema.NullOr(Schema.String),
  role: OrganizationRoleSchema,
  createdAt: Schema.NullOr(Schema.Date),
});
export type OrganizationMemberWithUser =
  typeof OrganizationMemberWithUserSchema.Type;

/**
 * Request to update a member's role.
 */
export const UpdateMemberRoleRequestSchema = Schema.Struct({
  role: AssignableRoleSchema,
});
export type UpdateMemberRoleRequest = typeof UpdateMemberRoleRequestSchema.Type;

/**
 * Response for membership update operations - basic membership info.
 */
export const MembershipResponseSchema = Schema.Struct({
  memberId: Schema.String,
  role: OrganizationRoleSchema,
  createdAt: Schema.NullOr(Schema.Date),
});
export type MembershipResponse = typeof MembershipResponseSchema.Type;

export class OrganizationMembershipsApi extends HttpApiGroup.make(
  "organization-memberships",
)
  .add(
    HttpApiEndpoint.get("list", "/organizations/:organizationId/members")
      .setPath(Schema.Struct({ organizationId: Schema.String }))
      .addSuccess(Schema.Array(OrganizationMemberWithUserSchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.patch(
      "update",
      "/organizations/:organizationId/members/:memberId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          memberId: Schema.String,
        }),
      )
      .setPayload(UpdateMemberRoleRequestSchema)
      .addSuccess(MembershipResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del(
      "delete",
      "/organizations/:organizationId/members/:memberId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          memberId: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
