import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  NotFoundError,
  PermissionDeniedError,
  DatabaseError,
  AlreadyExistsError,
  UnauthorizedError,
} from "@/errors";

const DependencyInfoSchema = Schema.Struct({
  version: Schema.String,
  extras: Schema.NullOr(Schema.Array(Schema.String)),
});

export type DependencyInfo = typeof DependencyInfoSchema.Type;

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

export type RegisterFunctionRequest = typeof RegisterFunctionRequestSchema.Type;

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

export type FunctionResponse = typeof FunctionResponseSchema.Type;

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

export type PublicFunction = typeof PublicFunctionSchema.Type;

const ListFunctionsResponseSchema = Schema.Struct({
  functions: Schema.Array(PublicFunctionSchema),
  total: Schema.Number,
});

export type ListFunctionsResponse = typeof ListFunctionsResponseSchema.Type;

const FunctionsPathParams = Schema.Struct({
  organizationId: Schema.String,
  projectId: Schema.String,
  environmentId: Schema.String,
});

const FunctionsBasePath =
  "/organizations/:organizationId/projects/:projectId/environments/:environmentId/functions";

export class FunctionsApi extends HttpApiGroup.make("functions")
  .add(
    HttpApiEndpoint.post("register", FunctionsBasePath)
      .setPath(FunctionsPathParams)
      .setPayload(RegisterFunctionRequestSchema)
      .addSuccess(FunctionResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status }),
  )
  .add(
    HttpApiEndpoint.get("getByHash", `${FunctionsBasePath}/by-hash/:hash`)
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          environmentId: Schema.String,
          hash: Schema.String,
        }),
      )
      .addSuccess(PublicFunctionSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("get", `${FunctionsBasePath}/:id`)
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          environmentId: Schema.String,
          id: Schema.String,
        }),
      )
      .addSuccess(PublicFunctionSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("list", FunctionsBasePath)
      .setPath(FunctionsPathParams)
      .setUrlParams(
        Schema.Struct({
          name: Schema.optional(Schema.String),
          tags: Schema.optional(Schema.String),
          limit: Schema.optional(Schema.NumberFromString),
          offset: Schema.optional(Schema.NumberFromString),
        }),
      )
      .addSuccess(ListFunctionsResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}

/**
 * SDK Functions API - Flat paths for SDK usage with API key authentication
 * organizationId, projectId, and environmentId are derived from the API key
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
