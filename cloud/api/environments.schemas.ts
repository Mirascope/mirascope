import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";

export const EnvironmentSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  projectId: Schema.String,
});

export const CreateEnvironmentRequestSchema = Schema.Struct({
  name: Schema.String,
});

export type Environment = typeof EnvironmentSchema.Type;
export type CreateEnvironmentRequest =
  typeof CreateEnvironmentRequestSchema.Type;

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
      .addError(PermissionDeniedError)
      .addError(DatabaseError),
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
      .addError(AlreadyExistsError)
      .addError(PermissionDeniedError)
      .addError(DatabaseError),
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
      .addError(NotFoundError)
      .addError(PermissionDeniedError)
      .addError(DatabaseError),
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
      .addError(NotFoundError)
      .addError(PermissionDeniedError)
      .addError(DatabaseError),
  ) {}
