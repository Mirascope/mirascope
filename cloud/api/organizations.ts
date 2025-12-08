import { Effect } from "effect";
import { DatabaseService } from "@/db";
import { AuthenticatedUser } from "@/auth/context";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import {
  type OrganizationWithRole,
  type ListOrganizationsResponse,
} from "@/api/organizations.schema";

// Re-export schema types for convenience
export * from "@/api/organizations.schema";

// ============================================================================
// Handler Effects
// ============================================================================

export const listOrganizationsHandler = Effect.gen(function* () {
  const user = yield* AuthenticatedUser;
  const db = yield* DatabaseService;

  const organizations = yield* db.organizations.findAll(user.id).pipe(
    Effect.mapError(
      (error) =>
        new DatabaseError({
          message: error.message,
          cause: error,
        }),
    ),
  );

  return { organizations } as ListOrganizationsResponse;
});

export const createOrganizationHandler = (payload: { name: string }) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* DatabaseService;

    const organization = yield* db.organizations
      .create({ name: payload.name }, user.id)
      .pipe(
        Effect.mapError((error) => {
          if (error._tag === "AlreadyExistsError") {
            return new AlreadyExistsError({
              message: error.message,
              resource: error.resource,
            });
          }
          return new DatabaseError({
            message: error.message,
            cause: error,
          });
        }),
      );

    return organization as OrganizationWithRole;
  });

export const deleteOrganizationHandler = (path: { id: string }) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* DatabaseService;

    yield* db.organizations.delete(path.id, user.id).pipe(
      Effect.mapError((error) => {
        if (error._tag === "NotFoundError") {
          return new NotFoundError({
            message: error.message,
            resource: error.resource,
          });
        }
        if (error._tag === "PermissionDeniedError") {
          return new PermissionDeniedError({
            message: error.message,
            resource: error.resource,
          });
        }
        return new DatabaseError({
          message: error.message,
          cause: error,
        });
      }),
    );
  });
