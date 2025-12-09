import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";

export const ProjectSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  userOwnerId: Schema.NullOr(Schema.String),
  orgOwnerId: Schema.NullOr(Schema.String),
});

const ProjectNameSchema = Schema.String.pipe(
  Schema.minLength(1, { message: () => "Project name is required" }),
  Schema.maxLength(100, {
    message: () => "Project name must be at most 100 characters",
  }),
);

export const CreateProjectRequestSchema = Schema.Struct({
  name: ProjectNameSchema,
  userOwnerId: Schema.optional(Schema.String),
  orgOwnerId: Schema.optional(Schema.String),
});

export const UpdateProjectRequestSchema = Schema.Struct({
  name: ProjectNameSchema,
});

export type Project = typeof ProjectSchema.Type;
export type CreateProjectRequest = typeof CreateProjectRequestSchema.Type;
export type UpdateProjectRequest = typeof UpdateProjectRequestSchema.Type;

export class ProjectsApi extends HttpApiGroup.make("projects")
  .add(
    HttpApiEndpoint.get("list", "/projects")
      .addSuccess(Schema.Array(ProjectSchema))
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post("create", "/projects")
      .setPayload(CreateProjectRequestSchema)
      .addSuccess(ProjectSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("get", "/projects/:projectId")
      .setPath(Schema.Struct({ projectId: Schema.String }))
      .addSuccess(ProjectSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.put("update", "/projects/:projectId")
      .setPath(Schema.Struct({ projectId: Schema.String }))
      .setPayload(UpdateProjectRequestSchema)
      .addSuccess(ProjectSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del("delete", "/projects/:projectId")
      .setPath(Schema.Struct({ projectId: Schema.String }))
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
