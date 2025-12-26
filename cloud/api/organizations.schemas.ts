import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  StripeError,
} from "@/errors";
import { createSlugSchema } from "@/db/slug";

export const OrganizationRoleSchema = Schema.Literal(
  "OWNER",
  "ADMIN",
  "MEMBER",
);

export const OrganizationSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  slug: Schema.String,
  stripeCustomerId: Schema.String,
});

export const OrganizationWithMembershipSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  slug: Schema.String,
  stripeCustomerId: Schema.String,
  role: OrganizationRoleSchema,
});

// Organization name must be 1-100 characters
const OrganizationNameSchema = Schema.String.pipe(
  Schema.minLength(1, { message: () => "Organization name is required" }),
  Schema.maxLength(100, {
    message: () => "Organization name must be at most 100 characters",
  }),
);

// Organization slug validation
const OrganizationSlugSchema = createSlugSchema("Organization");

export const CreateOrganizationRequestSchema = Schema.Struct({
  name: OrganizationNameSchema,
  slug: OrganizationSlugSchema,
});

export const UpdateOrganizationRequestSchema = Schema.Struct({
  name: Schema.optional(OrganizationNameSchema),
  slug: Schema.optional(OrganizationSlugSchema),
});

export const OrganizationCreditsSchema = Schema.Struct({
  balance: Schema.Number,
});

export type Organization = typeof OrganizationSchema.Type;
export type OrganizationWithMembership =
  typeof OrganizationWithMembershipSchema.Type;
export type CreateOrganizationRequest =
  typeof CreateOrganizationRequestSchema.Type;
export type UpdateOrganizationRequest =
  typeof UpdateOrganizationRequestSchema.Type;
export type OrganizationCredits = typeof OrganizationCreditsSchema.Type;

export class OrganizationsApi extends HttpApiGroup.make("organizations")
  .add(
    HttpApiEndpoint.get("list", "/organizations")
      .addSuccess(Schema.Array(OrganizationWithMembershipSchema))
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post("create", "/organizations")
      .setPayload(CreateOrganizationRequestSchema)
      .addSuccess(OrganizationWithMembershipSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(StripeError, { status: StripeError.status }),
  )
  .add(
    HttpApiEndpoint.get("get", "/organizations/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(OrganizationWithMembershipSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.put("update", "/organizations/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .setPayload(UpdateOrganizationRequestSchema)
      .addSuccess(OrganizationWithMembershipSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(StripeError, { status: StripeError.status }),
  )
  .add(
    HttpApiEndpoint.del("delete", "/organizations/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(StripeError, { status: StripeError.status }),
  )
  .add(
    HttpApiEndpoint.get("credits", "/organizations/:id/credits")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(OrganizationCreditsSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
