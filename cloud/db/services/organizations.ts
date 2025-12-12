import { Effect } from "effect";
import { and, eq } from "drizzle-orm";
import {
  BaseAuthenticatedService,
  BaseService,
  type PermissionTable,
} from "@/db/services/base";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { isUniqueConstraintError } from "@/db/utils";
import {
  organizations,
  organizationMemberships,
  type NewOrganization,
  type PublicOrganization,
  type PublicOrganizationWithMembership,
  type Role,
} from "@/db/schema";

class OrganizationBaseService extends BaseService<
  PublicOrganization,
  "organizations/:organizationId",
  typeof organizations
> {
  protected getTable() {
    return organizations;
  }

  protected getResourceName() {
    return "organization";
  }

  protected getIdParamName() {
    return "organizationId" as const;
  }

  protected getPublicFields() {
    return {
      id: organizations.id,
      name: organizations.name,
    };
  }
}

export class OrganizationService extends BaseAuthenticatedService<
  PublicOrganization,
  "organizations/:organizationId",
  typeof organizations,
  NewOrganization,
  Role
> {
  protected initializeBaseService() {
    return new OrganizationBaseService(this.db);
  }

  protected getPermissionTable(): PermissionTable<Role> {
    return {
      create: ["OWNER"], // Handled separately (no org exists yet)
      read: ["OWNER", "ADMIN", "DEVELOPER", "ANNOTATOR"], // All members can read
      update: ["OWNER", "ADMIN"],
      delete: ["OWNER"],
    };
  }

  /**
   * Get the user's role in an organization.
   * Returns NotFoundError if user is not a member (hides org existence from non-members).
   */
  getRole({
    organizationId,
    userId,
  }: {
    organizationId: string;
    userId: string;
  }): Effect.Effect<Role, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const membership = yield* Effect.tryPromise({
        try: async () => {
          const [membership] = await this.db
            .select({ role: organizationMemberships.role })
            .from(organizationMemberships)
            .where(
              and(
                eq(organizationMemberships.userId, userId),
                eq(organizationMemberships.organizationId, organizationId),
              ),
            )
            .limit(1);
          return membership;
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to get membership",
            cause: error,
          }),
      });

      if (!membership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Organization not found",
            resource: this.baseService.resourceName,
          }),
        );
      }
      return membership.role;
    });
  }

  create({
    userId,
    data,
  }: {
    userId: string;
    data: NewOrganization;
  }): Effect.Effect<
    PublicOrganizationWithMembership,
    AlreadyExistsError | DatabaseError
  > {
    return Effect.tryPromise({
      try: async () => {
        return await this.db.transaction(async (tx) => {
          const [organization] = await tx
            .insert(organizations)
            .values({ name: data.name })
            .returning({ id: organizations.id, name: organizations.name });

          await tx.insert(organizationMemberships).values({
            userId,
            organizationId: organization.id,
            role: "OWNER",
          });

          return {
            id: organization.id,
            name: organization.name,
            role: "OWNER" as Role,
          };
        });
      },
      catch: (error) => {
        if (isUniqueConstraintError(error)) {
          return new AlreadyExistsError({
            message: "An organization with this name already exists",
            resource: this.baseService.resourceName,
          });
        }
        return new DatabaseError({
          message: "Failed to create organization",
          cause: error,
        });
      },
    });
  }

  findAll({
    userId,
  }: {
    userId: string;
  }): Effect.Effect<PublicOrganizationWithMembership[], DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        return await this.db
          .select({
            id: organizations.id,
            name: organizations.name,
            role: organizationMemberships.role,
          })
          .from(organizationMemberships)
          .innerJoin(
            organizations,
            eq(organizationMemberships.organizationId, organizations.id),
          )
          .where(eq(organizationMemberships.userId, userId));
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to get user organizations",
          cause: error,
        }),
    });
  }

  findById({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    PublicOrganizationWithMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const role = yield* this.authorize({
        userId,
        organizationId,
        action: "read",
      });
      const organization = yield* this.baseService.findById({ organizationId });
      return { ...organization, role };
    });
  }

  update({
    userId,
    organizationId,
    data,
  }: {
    userId: string;
    organizationId: string;
    data: Partial<NewOrganization>;
  }): Effect.Effect<
    PublicOrganizationWithMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const role = yield* this.authorize({
        userId,
        organizationId,
        action: "update",
      });
      const organization = yield* this.baseService.update({
        organizationId,
        data,
      });
      return { ...organization, role };
    });
  }

  delete({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ userId, organizationId, action: "delete" });
      yield* Effect.tryPromise({
        try: async () => {
          await this.db.transaction(async (tx) => {
            await tx
              .delete(organizationMemberships)
              .where(
                eq(organizationMemberships.organizationId, organizationId),
              );
            await tx
              .delete(organizations)
              .where(eq(organizations.id, organizationId));
          });
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to delete organization",
            cause: error,
          }),
      });
    });
  }
}
