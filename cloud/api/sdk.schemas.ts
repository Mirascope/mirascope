/**
 * SDK Flat API Schemas
 *
 * These endpoints provide flat paths for SDK usage with API key authentication.
 * The organizationId, projectId, and environmentId are derived from the API key.
 */
import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  NotFoundError,
  PermissionDeniedError,
  DatabaseError,
  AlreadyExistsError,
  UnauthorizedError,
} from "@/errors";
import {
  CreateTraceRequestSchema,
  CreateTraceResponseSchema,
} from "@/api/traces.schemas";

// Re-export request/response types from traces module
export {
  CreateTraceRequestSchema,
  CreateTraceResponseSchema,
  type CreateTraceRequest,
  type CreateTraceResponse,
} from "@/api/traces.schemas";

// Re-export request/response types from functions module
export {
  type RegisterFunctionRequest,
  type FunctionResponse,
  type PublicFunction,
  type ListFunctionsResponse,
} from "@/api/functions.schemas";

// Function schemas (redeclared for SDK endpoints)
const DependencyInfoSchema = Schema.Struct({
  version: Schema.String,
  extras: Schema.NullOr(Schema.Array(Schema.String)),
});

const RegisterFunctionRequestSchema = Schema.Struct({
  code: Schema.String,
  hash: Schema.String,
  signature: Schema.String,
  signatureHash: Schema.String,
  name: Schema.String,
  description: Schema.optional(Schema.NullOr(Schema.String)),
  tags: Schema.optional(Schema.NullOr(Schema.Array(Schema.String))),
  metadata: Schema.optional(
    Schema.NullOr(Schema.Record({ key: Schema.String, value: Schema.String })),
  ),
  dependencies: Schema.optional(
    Schema.NullOr(
      Schema.Record({ key: Schema.String, value: DependencyInfoSchema }),
    ),
  ),
});

const FunctionResponseSchema = Schema.Struct({
  id: Schema.String,
  hash: Schema.String,
  signatureHash: Schema.String,
  name: Schema.String,
  description: Schema.NullOr(Schema.String),
  version: Schema.String,
  tags: Schema.NullOr(Schema.Array(Schema.String)),
  metadata: Schema.NullOr(
    Schema.Record({ key: Schema.String, value: Schema.String }),
  ),
  code: Schema.String,
  signature: Schema.String,
  dependencies: Schema.NullOr(
    Schema.Record({ key: Schema.String, value: DependencyInfoSchema }),
  ),
  environmentId: Schema.String,
  projectId: Schema.String,
  organizationId: Schema.String,
  createdAt: Schema.NullOr(Schema.String),
  updatedAt: Schema.NullOr(Schema.String),
  isNew: Schema.Boolean,
});

const PublicFunctionSchema = Schema.Struct({
  id: Schema.String,
  hash: Schema.String,
  signatureHash: Schema.String,
  name: Schema.String,
  description: Schema.NullOr(Schema.String),
  version: Schema.String,
  tags: Schema.NullOr(Schema.Array(Schema.String)),
  metadata: Schema.NullOr(
    Schema.Record({ key: Schema.String, value: Schema.String }),
  ),
  code: Schema.String,
  signature: Schema.String,
  dependencies: Schema.NullOr(
    Schema.Record({ key: Schema.String, value: DependencyInfoSchema }),
  ),
  environmentId: Schema.String,
  projectId: Schema.String,
  organizationId: Schema.String,
  createdAt: Schema.NullOr(Schema.String),
  updatedAt: Schema.NullOr(Schema.String),
});

const ListFunctionsResponseSchema = Schema.Struct({
  functions: Schema.Array(PublicFunctionSchema),
  total: Schema.Number,
});

/**
 * SDK Traces API - Flat paths for SDK usage
 */
export class SdkTracesApi extends HttpApiGroup.make("sdkTraces").add(
  HttpApiEndpoint.post("create", "/traces")
    .setPayload(CreateTraceRequestSchema)
    .addSuccess(CreateTraceResponseSchema)
    .addError(UnauthorizedError, { status: UnauthorizedError.status })
    .addError(NotFoundError, { status: NotFoundError.status })
    .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
    .addError(DatabaseError, { status: DatabaseError.status })
    .addError(AlreadyExistsError, { status: AlreadyExistsError.status }),
) {}

/**
 * SDK Functions API - Flat paths for SDK usage
 */
export class SdkFunctionsApi extends HttpApiGroup.make("sdkFunctions")
  .add(
    HttpApiEndpoint.post("register", "/functions")
      .setPayload(RegisterFunctionRequestSchema)
      .addSuccess(FunctionResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status }),
  )
  .add(
    HttpApiEndpoint.get("getByHash", "/functions/by-hash/:hash")
      .setPath(Schema.Struct({ hash: Schema.String }))
      .addSuccess(PublicFunctionSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("get", "/functions/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(PublicFunctionSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("list", "/functions")
      .setUrlParams(
        Schema.Struct({
          name: Schema.optional(Schema.String),
          tags: Schema.optional(Schema.String),
          limit: Schema.optional(Schema.NumberFromString),
          offset: Schema.optional(Schema.NumberFromString),
        }),
      )
      .addSuccess(ListFunctionsResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
