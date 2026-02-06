import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

import { createSlugSchema } from "@/db/slug";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
  StripeError,
} from "@/errors";

export const ClawSchema = Schema.Struct({
  id: Schema.String,
  slug: Schema.String,
  displayName: Schema.NullOr(Schema.String),
  description: Schema.NullOr(Schema.String),
  organizationId: Schema.String,
  createdByUserId: Schema.String,
  status: Schema.Literal(
    "pending",
    "provisioning",
    "active",
    "paused",
    "error",
  ),
  instanceType: Schema.Literal(
    "lite",
    "basic",
    "standard-1",
    "standard-2",
    "standard-3",
    "standard-4",
  ),
  lastDeployedAt: Schema.NullOr(Schema.Date),
  lastError: Schema.NullOr(Schema.String),
  secretsEncrypted: Schema.NullOr(Schema.String),
  secretsKeyId: Schema.NullOr(Schema.String),
  bucketName: Schema.NullOr(Schema.String),
  botUserId: Schema.NullOr(Schema.String),
  homeProjectId: Schema.NullOr(Schema.String),
  homeEnvironmentId: Schema.NullOr(Schema.String),
  weeklySpendingGuardrailCenticents: Schema.NullOr(Schema.BigInt),
  weeklyWindowStart: Schema.NullOr(Schema.Date),
  weeklyUsageCenticents: Schema.NullOr(Schema.BigInt),
  burstWindowStart: Schema.NullOr(Schema.Date),
  burstUsageCenticents: Schema.NullOr(Schema.BigInt),
  createdAt: Schema.NullOr(Schema.Date),
  updatedAt: Schema.NullOr(Schema.Date),
});

const ClawNameSchema = Schema.String.pipe(
  Schema.minLength(1, { message: () => "Claw name is required" }),
  Schema.maxLength(100, {
    message: () => "Claw name must be at most 100 characters",
  }),
);

const ClawSlugSchema = createSlugSchema("Claw");

export const CreateClawRequestSchema = Schema.Struct({
  name: ClawNameSchema,
  slug: ClawSlugSchema,
  description: Schema.optional(Schema.String),
  model: Schema.optional(
    Schema.Literal("claude-haiku-4-5", "claude-sonnet-4-5", "claude-opus-4-6"),
  ),
  weeklySpendingGuardrailCenticents: Schema.optional(
    Schema.NullOr(Schema.BigInt),
  ),
});

export const UpdateClawRequestSchema = Schema.Struct({
  name: Schema.optional(ClawNameSchema),
  description: Schema.optional(Schema.String),
  weeklySpendingGuardrailCenticents: Schema.optional(
    Schema.NullOr(Schema.BigInt),
  ),
});

export const ClawUsageSchema = Schema.Struct({
  weeklyUsageCenticents: Schema.BigInt,
  weeklyWindowStart: Schema.NullOr(Schema.Date),
  burstUsageCenticents: Schema.BigInt,
  burstWindowStart: Schema.NullOr(Schema.Date),
  weeklySpendingGuardrailCenticents: Schema.NullOr(Schema.BigInt),
  poolUsageCenticents: Schema.BigInt,
  poolLimitCenticents: Schema.Number,
  poolPercentUsed: Schema.Number,
});

export type Claw = typeof ClawSchema.Type;
export type CreateClawRequest = typeof CreateClawRequestSchema.Type;
export type UpdateClawRequest = typeof UpdateClawRequestSchema.Type;
export type ClawUsage = typeof ClawUsageSchema.Type;

export class ClawsApi extends HttpApiGroup.make("claws")
  .add(
    HttpApiEndpoint.get("list", "/organizations/:organizationId/claws")
      .setPath(Schema.Struct({ organizationId: Schema.String }))
      .addSuccess(Schema.Array(ClawSchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post("create", "/organizations/:organizationId/claws")
      .setPath(Schema.Struct({ organizationId: Schema.String }))
      .setPayload(CreateClawRequestSchema)
      .addSuccess(ClawSchema)
      .addError(PlanLimitExceededError, {
        status: PlanLimitExceededError.status,
      })
      .addError(StripeError, { status: StripeError.status })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("get", "/organizations/:organizationId/claws/:clawId")
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          clawId: Schema.String,
        }),
      )
      .addSuccess(ClawSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.put(
      "update",
      "/organizations/:organizationId/claws/:clawId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          clawId: Schema.String,
        }),
      )
      .setPayload(UpdateClawRequestSchema)
      .addSuccess(ClawSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del(
      "delete",
      "/organizations/:organizationId/claws/:clawId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          clawId: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get(
      "getUsage",
      "/organizations/:organizationId/claws/:clawId/usage",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          clawId: Schema.String,
        }),
      )
      .addSuccess(ClawUsageSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(StripeError, { status: StripeError.status }),
  ) {}
