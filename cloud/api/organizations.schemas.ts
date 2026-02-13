import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

import { createSlugSchema, RESERVED_ORG_SLUGS } from "@/db/slug";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
  StripeError,
  SubscriptionPastDueError,
} from "@/errors";
import { PLAN_TIERS, type DowngradeValidationError } from "@/payments/plans";

export const OrganizationRoleSchema = Schema.Literal(
  "OWNER",
  "ADMIN",
  "MEMBER",
  "BOT",
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

// Organization slug validation (with reserved slug check for DNS safety)
const OrganizationSlugSchema = createSlugSchema("Organization").pipe(
  Schema.filter((slug) =>
    RESERVED_ORG_SLUGS.has(slug)
      ? `"${slug}" is a reserved slug and cannot be used as an organization slug`
      : undefined,
  ),
);

export const CreateOrganizationRequestSchema = Schema.Struct({
  name: OrganizationNameSchema,
  slug: OrganizationSlugSchema,
  planTier: Schema.optional(Schema.Literal(...PLAN_TIERS)),
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
  paymentMethodId: Schema.optional(Schema.String),
});

export const CreatePaymentIntentResponseSchema = Schema.Struct({
  clientSecret: Schema.NullOr(Schema.String),
  amount: Schema.Number,
  status: Schema.Literal("requires_payment", "requires_action", "succeeded"),
});

export const SetupIntentResponseSchema = Schema.Struct({
  clientSecret: Schema.String,
});

export const PaymentMethodDetailsSchema = Schema.Struct({
  id: Schema.String,
  brand: Schema.String,
  last4: Schema.String,
  expMonth: Schema.Number,
  expYear: Schema.Number,
});

// Subscription schemas
export const PlanTierSchema = Schema.Literal(...PLAN_TIERS);

export const SubscriptionDetailsSchema = Schema.Struct({
  subscriptionId: Schema.String,
  currentPlan: PlanTierSchema,
  status: Schema.String,
  currentPeriodEnd: Schema.Date,
  hasPaymentMethod: Schema.Boolean,
  paymentMethod: Schema.optional(
    Schema.Struct({
      brand: Schema.String,
      last4: Schema.String,
      expMonth: Schema.Number,
      expYear: Schema.Number,
    }),
  ),
  scheduledChange: Schema.optional(
    Schema.Struct({
      targetPlan: PlanTierSchema,
      effectiveDate: Schema.Date,
      scheduleId: Schema.String,
    }),
  ),
});

export const PreviewSubscriptionChangeRequestSchema = Schema.Struct({
  targetPlan: PlanTierSchema,
});

export const DowngradeValidationErrorSchema: Schema.Schema<
  DowngradeValidationError,
  DowngradeValidationError
> = Schema.Struct({
  resource: Schema.Literal("seats", "projects", "claws"),
  currentUsage: Schema.Number,
  limit: Schema.Number,
  message: Schema.String,
});

export const SubscriptionChangePreviewSchema = Schema.Struct({
  isUpgrade: Schema.Boolean,
  proratedAmountInDollars: Schema.Number,
  nextBillingDate: Schema.Date,
  recurringAmountInDollars: Schema.Number,
  canDowngrade: Schema.optional(Schema.Boolean),
  validationErrors: Schema.optional(
    Schema.Array(DowngradeValidationErrorSchema),
  ),
});

export const UpdateSubscriptionRequestSchema = Schema.Struct({
  targetPlan: PlanTierSchema,
});

export const UpdateSubscriptionResponseSchema = Schema.Struct({
  requiresPayment: Schema.Boolean,
  clientSecret: Schema.optional(Schema.String),
  scheduledFor: Schema.optional(Schema.Date),
  scheduleId: Schema.optional(Schema.String),
});

export const AutoReloadSettingsSchema = Schema.Struct({
  enabled: Schema.Boolean,
  thresholdCenticents: Schema.BigInt.annotations({
    description: "Balance threshold in centi-cents (1/10000 of a dollar)",
  }),
  amountCenticents: Schema.BigInt.annotations({
    description: "Reload amount in centi-cents (1/10000 of a dollar)",
  }),
});

export const UpdateAutoReloadSettingsRequestSchema = Schema.Struct({
  enabled: Schema.Boolean,
  thresholdCenticents: Schema.BigInt.pipe(
    Schema.greaterThanOrEqualToBigInt(0n),
  ),
  amountCenticents: Schema.BigInt.pipe(Schema.greaterThanBigInt(0n)),
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
export type SetupIntentResponse = typeof SetupIntentResponseSchema.Type;
export type PaymentMethodDetails = typeof PaymentMethodDetailsSchema.Type;
export type SubscriptionDetails = typeof SubscriptionDetailsSchema.Type;
export type PreviewSubscriptionChangeRequest =
  typeof PreviewSubscriptionChangeRequestSchema.Type;
export type { DowngradeValidationError } from "@/payments/plans";
export type SubscriptionChangePreview =
  typeof SubscriptionChangePreviewSchema.Type;
export type UpdateSubscriptionRequest =
  typeof UpdateSubscriptionRequestSchema.Type;
export type UpdateSubscriptionResponse =
  typeof UpdateSubscriptionResponseSchema.Type;
export type AutoReloadSettings = typeof AutoReloadSettingsSchema.Type;
export type UpdateAutoReloadSettingsRequest =
  typeof UpdateAutoReloadSettingsRequestSchema.Type;

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
      .addError(StripeError, { status: StripeError.status })
      .addError(PlanLimitExceededError, {
        status: PlanLimitExceededError.status,
      }),
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
  )
  .add(
    HttpApiEndpoint.get("subscription", "/organizations/:id/subscription")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(SubscriptionDetailsSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "previewSubscriptionChange",
      "/organizations/:id/subscription/preview",
    )
      .setPath(Schema.Struct({ id: Schema.String }))
      .setPayload(PreviewSubscriptionChangeRequestSchema)
      .addSuccess(SubscriptionChangePreviewSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "updateSubscription",
      "/organizations/:id/subscription/update",
    )
      .setPath(Schema.Struct({ id: Schema.String }))
      .setPayload(UpdateSubscriptionRequestSchema)
      .addSuccess(UpdateSubscriptionResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(PlanLimitExceededError, {
        status: PlanLimitExceededError.status,
      })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(StripeError, { status: StripeError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "cancelScheduledDowngrade",
      "/organizations/:id/subscription/cancel-downgrade",
    )
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "createSetupIntent",
      "/organizations/:id/payment-method/setup-intent",
    )
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(SetupIntentResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("getPaymentMethod", "/organizations/:id/payment-method")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(Schema.NullOr(PaymentMethodDetailsSchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del(
      "removePaymentMethod",
      "/organizations/:id/payment-method",
    )
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get(
      "getAutoReloadSettings",
      "/organizations/:id/auto-reload",
    )
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(AutoReloadSettingsSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.put(
      "updateAutoReloadSettings",
      "/organizations/:id/auto-reload",
    )
      .setPath(Schema.Struct({ id: Schema.String }))
      .setPayload(UpdateAutoReloadSettingsRequestSchema)
      .addSuccess(AutoReloadSettingsSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
