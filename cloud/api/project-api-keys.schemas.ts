import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";

import {
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
  StripeError,
} from "@/errors";

const ProviderSchema = Schema.Literal("anthropic", "openai", "google");

export const ProjectApiKeySchema = Schema.Struct({
  provider: Schema.String,
  keySuffix: Schema.String,
  updatedAt: Schema.String,
});

export const SetProjectApiKeyRequestSchema = Schema.Struct({
  key: Schema.String.pipe(
    Schema.minLength(1, { message: () => "API key is required" }),
  ),
});

export type SetProjectApiKeyRequest = typeof SetProjectApiKeyRequestSchema.Type;

export class ProjectApiKeysApi extends HttpApiGroup.make("projectApiKeys")
  .add(
    HttpApiEndpoint.get(
      "list",
      "/organizations/:organizationId/projects/:projectId/api-keys",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
        }),
      )
      .addSuccess(Schema.Array(ProjectApiKeySchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(PlanLimitExceededError, {
        status: PlanLimitExceededError.status,
      })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.put(
      "set",
      "/organizations/:organizationId/projects/:projectId/api-keys/:provider",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          provider: ProviderSchema,
        }),
      )
      .setPayload(SetProjectApiKeyRequestSchema)
      .addSuccess(ProjectApiKeySchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(PlanLimitExceededError, {
        status: PlanLimitExceededError.status,
      })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del(
      "delete",
      "/organizations/:organizationId/projects/:projectId/api-keys/:provider",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          provider: ProviderSchema,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(PlanLimitExceededError, {
        status: PlanLimitExceededError.status,
      })
      .addError(StripeError, { status: StripeError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .prefix("/api/v2") {}
