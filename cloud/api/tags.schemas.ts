import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  NotFoundError,
  PermissionDeniedError,
  DatabaseError,
  AlreadyExistsError,
} from "@/errors";

export const TagNameSchema = Schema.String.pipe(
  Schema.minLength(1),
  Schema.maxLength(100),
);

export const TagSchema = Schema.Struct({
  id: Schema.String,
  name: TagNameSchema,
  projectId: Schema.String,
  organizationId: Schema.String,
  createdBy: Schema.NullOr(Schema.String),
  createdAt: Schema.NullOr(Schema.String),
  updatedAt: Schema.NullOr(Schema.String),
});

export const CreateTagRequestSchema = Schema.Struct({
  name: TagNameSchema,
});

export const UpdateTagRequestSchema = Schema.Struct({
  name: Schema.optional(TagNameSchema),
});

export const ListTagsResponseSchema = Schema.Struct({
  tags: Schema.Array(TagSchema),
  total: Schema.Number,
});

export type Tag = typeof TagSchema.Type;
export type CreateTagRequest = typeof CreateTagRequestSchema.Type;
export type UpdateTagRequest = typeof UpdateTagRequestSchema.Type;
export type ListTagsResponse = typeof ListTagsResponseSchema.Type;

export class TagsApi extends HttpApiGroup.make("tags")
  .add(
    HttpApiEndpoint.get(
      "list",
      "/organizations/:organizationId/projects/:projectId/tags",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
        }),
      )
      .addSuccess(ListTagsResponseSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post(
      "create",
      "/organizations/:organizationId/projects/:projectId/tags",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
        }),
      )
      .setPayload(CreateTagRequestSchema)
      .addSuccess(TagSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get(
      "get",
      "/organizations/:organizationId/projects/:projectId/tags/:tagId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          tagId: Schema.String,
        }),
      )
      .addSuccess(TagSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.put(
      "update",
      "/organizations/:organizationId/projects/:projectId/tags/:tagId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          tagId: Schema.String,
        }),
      )
      .setPayload(UpdateTagRequestSchema)
      .addSuccess(TagSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del(
      "delete",
      "/organizations/:organizationId/projects/:projectId/tags/:tagId",
    )
      .setPath(
        Schema.Struct({
          organizationId: Schema.String,
          projectId: Schema.String,
          tagId: Schema.String,
        }),
      )
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
