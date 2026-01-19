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

const CreateFunctionRequestSchema = Schema.Struct({
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

export type CreateFunctionRequest = typeof CreateFunctionRequestSchema.Type;

const FunctionSchema = Schema.Struct({
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
  functions: Schema.Array(FunctionSchema),
  total: Schema.Number,
});

export type ListFunctionsResponse = typeof ListFunctionsResponseSchema.Type;

export class FunctionsApi extends HttpApiGroup.make("functions")
  .add(
    HttpApiEndpoint.get("list", "/functions")
      .addSuccess(ListFunctionsResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("listByName", "/functions/name/:name")
      .setPath(
        Schema.Struct({
          name: Schema.String,
        }),
      )
      .addSuccess(ListFunctionsResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("listLatestByName", "/functions/names/latest")
      .addSuccess(ListFunctionsResponseSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post("create", "/functions")
      .setPayload(CreateFunctionRequestSchema)
      .addSuccess(FunctionSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("get", "/functions/:id")
      .setPath(
        Schema.Struct({
          id: Schema.String,
        }),
      )
      .addSuccess(FunctionSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del("delete", "/functions/:id")
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
  )
  .add(
    HttpApiEndpoint.del("deleteByName", "/functions/name/:name")
      .setPath(
        Schema.Struct({
          name: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("findByHash", "/functions/hash/:hash")
      .setPath(
        Schema.Struct({
          hash: Schema.String,
        }),
      )
      .addSuccess(FunctionSchema)
      .addError(UnauthorizedError, { status: UnauthorizedError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
