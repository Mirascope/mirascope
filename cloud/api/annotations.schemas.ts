import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  NotFoundError,
  AlreadyExistsError,
  DatabaseError,
  PermissionDeniedError,
  UnauthorizedError,
} from "@/errors";

const LabelSchema = Schema.Literal("pass", "fail");

const CreateAnnotationRequestSchema = Schema.Struct({
  otelSpanId: Schema.String,
  otelTraceId: Schema.String,
  label: Schema.optional(Schema.NullOr(LabelSchema)),
  reasoning: Schema.optional(Schema.NullOr(Schema.String)),
  metadata: Schema.optional(
    Schema.NullOr(Schema.Record({ key: Schema.String, value: Schema.Unknown })),
  ),
});

export type CreateAnnotationRequest = typeof CreateAnnotationRequestSchema.Type;

const UpdateAnnotationRequestSchema = Schema.Struct({
  label: Schema.optional(Schema.NullOr(LabelSchema)),
  reasoning: Schema.optional(Schema.NullOr(Schema.String)),
  metadata: Schema.optional(
    Schema.NullOr(Schema.Record({ key: Schema.String, value: Schema.Unknown })),
  ),
});

export type UpdateAnnotationRequest = typeof UpdateAnnotationRequestSchema.Type;

const AnnotationResponseSchema = Schema.Struct({
  id: Schema.String,
  label: Schema.NullOr(LabelSchema),
  reasoning: Schema.NullOr(Schema.String),
  metadata: Schema.NullOr(
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

export class AnnotationsApi extends HttpApiGroup.make("annotations")
  .add(
    HttpApiEndpoint.get("list", "/annotations")
      .setUrlParams(
        Schema.Struct({
          otelTraceId: Schema.optional(Schema.String),
          otelSpanId: Schema.optional(Schema.String),
          label: Schema.optional(LabelSchema),
          limit: Schema.optional(Schema.NumberFromString),
          offset: Schema.optional(Schema.NumberFromString),
        }),
      )
      .addSuccess(ListAnnotationsResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post("create", "/annotations")
      .setPayload(CreateAnnotationRequestSchema)
      .addSuccess(AnnotationResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("get", "/annotations/:id")
      .setPath(
        Schema.Struct({
          id: Schema.String,
        }),
      )
      .addSuccess(AnnotationResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.put("update", "/annotations/:id")
      .setPath(
        Schema.Struct({
          id: Schema.String,
        }),
      )
      .setPayload(UpdateAnnotationRequestSchema)
      .addSuccess(AnnotationResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del("delete", "/annotations/:id")
      .setPath(
        Schema.Struct({
          id: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
