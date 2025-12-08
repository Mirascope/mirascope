import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import { Schema } from "effect";
import {
  NotFoundErrorSchema,
  AlreadyExistsErrorSchema,
  PermissionDeniedErrorSchema,
  UnauthorizedErrorSchema,
  DatabaseErrorSchema,
} from "@/api/errors.schema";

// ============================================================================
// Schemas
// ============================================================================

export const OrganizationSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
});

export type Organization = typeof OrganizationSchema.Type;

export const OrganizationWithRoleSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  role: Schema.Literal("OWNER", "ADMIN", "DEVELOPER", "ANNOTATOR"),
});

export type OrganizationWithRole = typeof OrganizationWithRoleSchema.Type;

// Request schemas
export const CreateOrganizationRequestSchema = Schema.Struct({
  name: Schema.String.pipe(
    Schema.minLength(1, {
      message: () => "Organization name is required",
    }),
    Schema.maxLength(100, {
      message: () => "Organization name must be 100 characters or less",
    }),
  ),
});

export type CreateOrganizationRequest =
  typeof CreateOrganizationRequestSchema.Type;

// Response schemas
export const ListOrganizationsResponseSchema = Schema.Struct({
  organizations: Schema.Array(OrganizationWithRoleSchema),
});

export type ListOrganizationsResponse =
  typeof ListOrganizationsResponseSchema.Type;

// ============================================================================
// API Group
// ============================================================================

export class OrganizationsApi extends HttpApiGroup.make("organizations")
  .add(
    HttpApiEndpoint.get("list", "/organizations")
      .addSuccess(ListOrganizationsResponseSchema)
      .addError(UnauthorizedErrorSchema, { status: 401 })
      .addError(DatabaseErrorSchema, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.post("create", "/organizations")
      .setPayload(CreateOrganizationRequestSchema)
      .addSuccess(OrganizationWithRoleSchema, { status: 201 })
      .addError(UnauthorizedErrorSchema, { status: 401 })
      .addError(AlreadyExistsErrorSchema, { status: 409 })
      .addError(DatabaseErrorSchema, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.del("delete", "/organizations/:id")
      .setPath(
        Schema.Struct({
          id: Schema.String.pipe(
            Schema.annotations({ description: "Organization ID" }),
          ),
        }),
      )
      .addSuccess(Schema.Void, { status: 204 })
      .addError(UnauthorizedErrorSchema, { status: 401 })
      .addError(NotFoundErrorSchema, { status: 404 })
      .addError(PermissionDeniedErrorSchema, { status: 403 })
      .addError(DatabaseErrorSchema, { status: 500 }),
  ) {}
