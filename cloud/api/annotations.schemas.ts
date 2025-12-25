import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  NotFoundError,
  AlreadyExistsError,
  DatabaseError,
  PermissionDeniedError,
  UnauthorizedError,
} from "@/errors";

const CreateAnnotationRequestSchema = Schema.Struct({
  spanId: Schema.String,
  traceId: Schema.String,
  label: Schema.optional(Schema.NullOr(Schema.String)),
  reasoning: Schema.optional(Schema.NullOr(Schema.String)),
  data: Schema.optional(
    Schema.NullOr(Schema.Record({ key: Schema.String, value: Schema.Unknown })),
  ),
});

export type CreateAnnotationRequest = typeof CreateAnnotationRequestSchema.Type;

const UpdateAnnotationRequestSchema = Schema.Struct({
  label: Schema.optional(Schema.NullOr(Schema.String)),
  reasoning: Schema.optional(Schema.NullOr(Schema.String)),
  data: Schema.optional(
    Schema.NullOr(Schema.Record({ key: Schema.String, value: Schema.Unknown })),
  ),
});

export type UpdateAnnotationRequest = typeof UpdateAnnotationRequestSchema.Type;

const AnnotationResponseSchema = Schema.Struct({
  id: Schema.String,
  spanDbId: Schema.String,
  traceDbId: Schema.String,
  spanId: Schema.String,
  traceId: Schema.String,
  label: Schema.NullOr(Schema.String),
  reasoning: Schema.NullOr(Schema.String),
  data: Schema.NullOr(
    Schema.Record({ key: Schema.String, value: Schema.Unknown }),
  ),
  environmentId: Schema.String,
  projectId: Schema.String,
  organizationId: Schema.String,
  createdBy: Schema.NullOr(Schema.String),
  createdAt: Schema.NullOr(Schema.String),
  updatedAt: Schema.NullOr(Schema.String),
});

export type AnnotationResponse = typeof AnnotationResponseSchema.Type;

const ListAnnotationsResponseSchema = Schema.Struct({
  annotations: Schema.Array(AnnotationResponseSchema),
  total: Schema.Number,
});

export type ListAnnotationsResponse = typeof ListAnnotationsResponseSchema.Type;

const AnnotationsPathParams = Schema.Struct({
  organizationId: Schema.String,
  projectId: Schema.String,
  environmentId: Schema.String,
});

const AnnotationsBasePath =
  "/organizations/:organizationId/projects/:projectId/environments/:environmentId/annotations";

export class AnnotationsApi extends HttpApiGroup.make("annotations")
  .add(
    HttpApiEndpoint.post("create", AnnotationsBasePath)
      .setPath(AnnotationsPathParams)
      .setPayload(CreateAnnotationRequestSchema)
      .addSuccess(AnnotationResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  )
  .add(
    HttpApiEndpoint.get("get", `${AnnotationsBasePath}/:id`)
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          environmentId: Schema.String,
          id: Schema.String,
        }),
      )
      .addSuccess(AnnotationResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  )
  .add(
    HttpApiEndpoint.put("update", `${AnnotationsBasePath}/:id`)
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          environmentId: Schema.String,
          id: Schema.String,
        }),
      )
      .setPayload(UpdateAnnotationRequestSchema)
      .addSuccess(AnnotationResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  )
  .add(
    HttpApiEndpoint.del("delete", `${AnnotationsBasePath}/:id`)
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          environmentId: Schema.String,
          id: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  )
  .add(
    HttpApiEndpoint.get("list", AnnotationsBasePath)
      .setPath(AnnotationsPathParams)
      .setUrlParams(
        Schema.Struct({
          traceId: Schema.optional(Schema.String),
          spanId: Schema.optional(Schema.String),
          label: Schema.optional(Schema.String),
          limit: Schema.optional(Schema.NumberFromString),
          offset: Schema.optional(Schema.NumberFromString),
        }),
      )
      .addSuccess(ListAnnotationsResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  ) {}

/**
 * SDK Annotations API - Flat paths for SDK usage with API key authentication
 * organizationId, projectId, and environmentId are derived from the API key
 */
export class SdkAnnotationsApi extends HttpApiGroup.make("sdkAnnotations")
  .add(
    HttpApiEndpoint.post("create", "/annotations")
      .setPayload(CreateAnnotationRequestSchema)
      .addSuccess(AnnotationResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  )
  .add(
    HttpApiEndpoint.get("get", "/annotations/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(AnnotationResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  )
  .add(
    HttpApiEndpoint.put("update", "/annotations/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .setPayload(UpdateAnnotationRequestSchema)
      .addSuccess(AnnotationResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  )
  .add(
    HttpApiEndpoint.del("delete", "/annotations/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(Schema.Void)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  )
  .add(
    HttpApiEndpoint.get("list", "/annotations")
      .setUrlParams(
        Schema.Struct({
          traceId: Schema.optional(Schema.String),
          spanId: Schema.optional(Schema.String),
          label: Schema.optional(Schema.String),
          limit: Schema.optional(Schema.NumberFromString),
          offset: Schema.optional(Schema.NumberFromString),
        }),
      )
      .addSuccess(ListAnnotationsResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(PermissionDeniedError, {
        status: PermissionDeniedError.status,
      }),
  ) {}
