import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

import {
  AlreadyExistsError,
  DatabaseError,
  ImmutableResourceError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
  StripeError,
} from "@/errors";

export const InvitationRoleSchema = Schema.Literal("ADMIN", "MEMBER");

export const InvitationStatusSchema = Schema.Literal(
  "pending",
  "accepted",
  "revoked",
);

export const OrganizationInvitationSchema = Schema.Struct({
  id: Schema.String,
  organizationId: Schema.String,
  senderId: Schema.String,
  recipientEmail: Schema.String,
  role: InvitationRoleSchema,
  status: InvitationStatusSchema,
  expiresAt: Schema.Date,
  createdAt: Schema.Date,
  updatedAt: Schema.Date,
  acceptedAt: Schema.NullOr(Schema.Date),
  revokedAt: Schema.NullOr(Schema.Date),
});

export const OrganizationInvitationWithMetadataSchema = Schema.Struct({
  id: Schema.String,
  organizationId: Schema.String,
  senderId: Schema.String,
  recipientEmail: Schema.String,
  role: InvitationRoleSchema,
  status: InvitationStatusSchema,
  token: Schema.String,
  expiresAt: Schema.Date,
  createdAt: Schema.Date,
  updatedAt: Schema.Date,
  acceptedAt: Schema.NullOr(Schema.Date),
  revokedAt: Schema.NullOr(Schema.Date),
  organizationName: Schema.String,
  senderName: Schema.String,
  senderEmail: Schema.String,
});

// Email validation
const EmailSchema = Schema.String.pipe(
  Schema.pattern(/^[^ \t\n\r\f\v@]+@[^ \t\n\r\f\v@]+[.][^ \t\n\r\f\v@]+$/, {
    message: () => "Invalid email format",
  }),
);

export const CreateInvitationRequestSchema = Schema.Struct({
  recipientEmail: EmailSchema,
  role: InvitationRoleSchema,
});

export const AcceptInvitationRequestSchema = Schema.Struct({
  token: Schema.String,
});

export const OrganizationMembershipSchema = Schema.Struct({
  memberId: Schema.String,
  organizationId: Schema.String,
  role: Schema.Literal("OWNER", "ADMIN", "MEMBER"),
  createdAt: Schema.NullOr(Schema.Date),
});

export type InvitationRole = typeof InvitationRoleSchema.Type;
export type InvitationStatus = typeof InvitationStatusSchema.Type;
export type OrganizationInvitation = typeof OrganizationInvitationSchema.Type;
export type OrganizationInvitationWithMetadata =
  typeof OrganizationInvitationWithMetadataSchema.Type;
export type CreateInvitationRequest = typeof CreateInvitationRequestSchema.Type;
export type AcceptInvitationRequest = typeof AcceptInvitationRequestSchema.Type;
export type OrganizationMembership = typeof OrganizationMembershipSchema.Type;

export class OrganizationInvitationsApi extends HttpApiGroup.make(
  "organization-invitations",
)
  .add(
    HttpApiEndpoint.get("list", "/organizations/:organizationId/invitations")
      .setPath(Schema.Struct({ organizationId: Schema.String }))
      .addSuccess(Schema.Array(OrganizationInvitationSchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post("create", "/organizations/:organizationId/invitations")
      .setPath(Schema.Struct({ organizationId: Schema.String }))
      .setPayload(CreateInvitationRequestSchema)
      .addSuccess(OrganizationInvitationSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(PlanLimitExceededError, {
        status: PlanLimitExceededError.status,
      })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get(
      "get",
      "/organizations/:organizationId/invitations/:invitationId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          invitationId: Schema.String,
        }),
      )
      .addSuccess(OrganizationInvitationSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "resend",
      "/organizations/:organizationId/invitations/:invitationId/resend",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          invitationId: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(ImmutableResourceError, {
        status: ImmutableResourceError.status,
      })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "revoke",
      "/organizations/:organizationId/invitations/:invitationId/revoke",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          invitationId: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(ImmutableResourceError, {
        status: ImmutableResourceError.status,
      })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post("accept", "/invitations/accept")
      .setPayload(AcceptInvitationRequestSchema)
      .addSuccess(OrganizationMembershipSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(ImmutableResourceError, {
        status: ImmutableResourceError.status,
      })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(PlanLimitExceededError, {
        status: PlanLimitExceededError.status,
      })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
