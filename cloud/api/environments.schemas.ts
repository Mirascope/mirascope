import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  AlreadyExistsError,
  ClickHouseError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import { createSlugSchema } from "@/db/slug";

export const EnvironmentSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  slug: Schema.String,
  projectId: Schema.String,
});

const EnvironmentNameSchema = Schema.String.pipe(
  Schema.minLength(1, { message: () => "Environment name is required" }),
  Schema.maxLength(100, {
    message: () => "Environment name must be at most 100 characters",
  }),
);

// Environment slug validation
const EnvironmentSlugSchema = createSlugSchema("Environment");

export const CreateEnvironmentRequestSchema = Schema.Struct({
  name: EnvironmentNameSchema,
  slug: EnvironmentSlugSchema,
});

export const UpdateEnvironmentRequestSchema = Schema.Struct({
  name: Schema.optional(EnvironmentNameSchema),
  slug: Schema.optional(EnvironmentSlugSchema),
});

// Analytics schemas
const TopModelSchema = Schema.Struct({
  model: Schema.String,
  count: Schema.Number,
});

const TopFunctionSchema = Schema.Struct({
  functionName: Schema.String,
  count: Schema.Number,
});

export const EnvironmentAnalyticsRequestSchema = Schema.Struct({
  startTime: Schema.String,
  endTime: Schema.String,
});

export const EnvironmentAnalyticsResponseSchema = Schema.Struct({
  totalSpans: Schema.Number,
  avgDurationMs: Schema.NullOr(Schema.Number),
  p50DurationMs: Schema.NullOr(Schema.Number),
  p95DurationMs: Schema.NullOr(Schema.Number),
  p99DurationMs: Schema.NullOr(Schema.Number),
  errorRate: Schema.Number,
  totalTokens: Schema.Number,
  totalCostUsd: Schema.Number,
  topModels: Schema.Array(TopModelSchema),
  topFunctions: Schema.Array(TopFunctionSchema),
});

export type Environment = typeof EnvironmentSchema.Type;
export type CreateEnvironmentRequest =
  typeof CreateEnvironmentRequestSchema.Type;
export type UpdateEnvironmentRequest =
  typeof UpdateEnvironmentRequestSchema.Type;
export type EnvironmentAnalyticsRequest =
  typeof EnvironmentAnalyticsRequestSchema.Type;
export type EnvironmentAnalyticsResponse =
  typeof EnvironmentAnalyticsResponseSchema.Type;

export class EnvironmentsApi extends HttpApiGroup.make("environments")
  .add(
    HttpApiEndpoint.get(
      "list",
      "/organizations/:organizationId/projects/:projectId/environments",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
        }),
      )
      .addSuccess(Schema.Array(EnvironmentSchema))
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "create",
      "/organizations/:organizationId/projects/:projectId/environments",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
        }),
      )
      .setPayload(CreateEnvironmentRequestSchema)
      .addSuccess(EnvironmentSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get(
      "get",
      "/organizations/:organizationId/projects/:projectId/environments/:environmentId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          environmentId: Schema.String,
        }),
      )
      .addSuccess(EnvironmentSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.put(
      "update",
      "/organizations/:organizationId/projects/:projectId/environments/:environmentId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          environmentId: Schema.String,
        }),
      )
      .setPayload(UpdateEnvironmentRequestSchema)
      .addSuccess(EnvironmentSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del(
      "delete",
      "/organizations/:organizationId/projects/:projectId/environments/:environmentId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          environmentId: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get(
      "getAnalytics",
      "/organizations/:organizationId/projects/:projectId/environments/:environmentId/analytics",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          environmentId: Schema.String,
        }),
      )
      .setUrlParams(EnvironmentAnalyticsRequestSchema)
      .addSuccess(EnvironmentAnalyticsResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(ClickHouseError, { status: ClickHouseError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
