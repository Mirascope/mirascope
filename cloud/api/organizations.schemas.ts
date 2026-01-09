import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  StripeError,
  SubscriptionPastDueError,
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

export const OrganizationRouterBalanceSchema = Schema.Struct({
  balance: Schema.BigInt.annotations({
    description: "Balance in centi-cents (1/10000 of a dollar)",
  }),
});

export const CreatePaymentIntentRequestSchema = Schema.Struct({
  amount: Schema.Number.pipe(
    Schema.positive({ message: () => "Amount must be positive" }),
  ),
});

export const CreatePaymentIntentResponseSchema = Schema.Struct({
  clientSecret: Schema.String,
  amount: Schema.Number,
});

export type Organization = typeof OrganizationSchema.Type;
export type OrganizationWithMembership =
  typeof OrganizationWithMembershipSchema.Type;
export type CreateOrganizationRequest =
  typeof CreateOrganizationRequestSchema.Type;
export type UpdateOrganizationRequest =
  typeof UpdateOrganizationRequestSchema.Type;
export type OrganizationRouterBalance =
  typeof OrganizationRouterBalanceSchema.Type;
export type CreatePaymentIntentRequest =
  typeof CreatePaymentIntentRequestSchema.Type;
export type CreatePaymentIntentResponse =
  typeof CreatePaymentIntentResponseSchema.Type;

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
      .addError(SubscriptionPastDueError, {
        status: SubscriptionPastDueError.status,
      })
      .addError(StripeError, { status: StripeError.status }),
  )
  .add(
    HttpApiEndpoint.get("routerBalance", "/organizations/:id/router-balance")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(OrganizationRouterBalanceSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "createPaymentIntent",
      "/organizations/:id/credits/payment-intent",
    )
      .setPath(Schema.Struct({ id: Schema.String }))
      .setPayload(CreatePaymentIntentRequestSchema)
      .addSuccess(CreatePaymentIntentResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
