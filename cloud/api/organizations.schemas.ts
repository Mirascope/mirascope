import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";

export const RoleSchema = Schema.Literal(
  "OWNER",
  "ADMIN",
  "DEVELOPER",
  "ANNOTATOR",
);

export const OrganizationSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
});

export const OrganizationWithMembershipSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  role: RoleSchema,
});

// Organization name must be 1-100 characters
const OrganizationNameSchema = Schema.String.pipe(
  Schema.minLength(1, { message: () => "Organization name is required" }),
  Schema.maxLength(100, {
    message: () => "Organization name must be at most 100 characters",
  }),
);

export const CreateOrganizationRequestSchema = Schema.Struct({
  name: OrganizationNameSchema,
});

export const UpdateOrganizationRequestSchema = Schema.Struct({
  name: OrganizationNameSchema,
});

export type Organization = typeof OrganizationSchema.Type;
export type OrganizationWithMembership =
  typeof OrganizationWithMembershipSchema.Type;
export type CreateOrganizationRequest =
  typeof CreateOrganizationRequestSchema.Type;
export type UpdateOrganizationRequest =
  typeof UpdateOrganizationRequestSchema.Type;

export class OrganizationsApi extends HttpApiGroup.make("organizations")
  .add(
    HttpApiEndpoint.get("list", "/organizations")
      .addSuccess(Schema.Array(OrganizationWithMembershipSchema))
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.post("create", "/organizations")
      .setPayload(CreateOrganizationRequestSchema)
      .addSuccess(OrganizationWithMembershipSchema)
      .addError(AlreadyExistsError, { status: AlreadyExistsError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.get("get", "/organizations/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(OrganizationWithMembershipSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.put("update", "/organizations/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .setPayload(UpdateOrganizationRequestSchema)
      .addSuccess(OrganizationWithMembershipSchema)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  )
  .add(
    HttpApiEndpoint.del("delete", "/organizations/:id")
      .setPath(Schema.Struct({ id: Schema.String }))
      .addSuccess(Schema.Void)
      .addError(NotFoundError, { status: NotFoundError.status })
      .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
      .addError(DatabaseError, { status: DatabaseError.status }),
  ) {}
