import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  AlreadyExistsError,
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

export type Environment = typeof EnvironmentSchema.Type;
export type CreateEnvironmentRequest =
  typeof CreateEnvironmentRequestSchema.Type;
export type UpdateEnvironmentRequest =
  typeof UpdateEnvironmentRequestSchema.Type;

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
  ) {}
