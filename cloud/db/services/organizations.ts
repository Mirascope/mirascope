import { Effect } from "effect";
import { and, eq } from "drizzle-orm";
import {
  BaseAuthenticatedService,
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

export class OrganizationService extends BaseAuthenticatedService<
  PublicOrganization,
  string,
  typeof organizations,
  NewOrganization,
  Role
> {
  getResourceName(): string {
    return "organization";
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
  getRole(
    userId: string,
    organizationId: string,
  ): Effect.Effect<Role, NotFoundError | DatabaseError> {
    const fetchMembership = Effect.tryPromise({
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

    const rejectIfNotMember = (
      membership: { role: Role } | undefined,
    ): Effect.Effect<Role, NotFoundError> => {
      if (!membership) {
        return Effect.fail(
          new NotFoundError({
            message: "Organization not found",
            resource: this.resourceName,
          }),
        );
      }
      return Effect.succeed(membership.role);
    };

    return fetchMembership.pipe(Effect.flatMap(rejectIfNotMember));
  }

  create(
    data: NewOrganization,
    userId: string,
  ): Effect.Effect<
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
            resource: this.resourceName,
          });
        }
        return new DatabaseError({
          message: "Failed to create organization",
          cause: error,
        });
      },
    });
  }

  findAll(
    userId: string,
  ): Effect.Effect<PublicOrganizationWithMembership[], DatabaseError> {
    const fetchUserOrganizationsWithRoles = Effect.tryPromise({
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

    return fetchUserOrganizationsWithRoles;
  }

  findById(
    organizationId: string,
    userId: string,
  ): Effect.Effect<
    PublicOrganizationWithMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    const fetchOrganization = Effect.tryPromise({
      try: async () => {
        const [result] = await this.db
          .select({
            id: organizations.id,
            name: organizations.name,
          })
          .from(organizations)
          .where(eq(organizations.id, organizationId))
          .limit(1);
        return result as PublicOrganization | undefined;
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to find organization",
          cause: error,
        }),
    });

    const rejectIfNotFound = (
      org: PublicOrganization | undefined,
    ): Effect.Effect<PublicOrganization, NotFoundError> => {
      if (!org) {
        return Effect.fail(
          new NotFoundError({
            message: `Organization with id ${organizationId} not found`,
            resource: this.resourceName,
          }),
        );
      }
      return Effect.succeed(org);
    };

    return this.getRole(userId, organizationId).pipe(
      Effect.flatMap((role) =>
        this.verifyPermission(role, "read").pipe(
          Effect.andThen(fetchOrganization),
          Effect.flatMap(rejectIfNotFound),
          Effect.map((org) => ({ ...org, role })),
        ),
      ),
    );
  }

  update(
    organizationId: string,
    data: Partial<NewOrganization>,
    userId: string,
  ): Effect.Effect<
    PublicOrganizationWithMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    const updateOrganization = Effect.tryPromise({
      try: async () => {
        const [updated] = await this.db
          .update(organizations)
          .set({ name: data.name })
          .where(eq(organizations.id, organizationId))
          .returning({ id: organizations.id, name: organizations.name });
        return updated as PublicOrganization | undefined;
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to update organization",
          cause: error,
        }),
    });

    const rejectIfNotFound = (
      org: PublicOrganization | undefined,
    ): Effect.Effect<PublicOrganization, NotFoundError> => {
      if (!org) {
        return Effect.fail(
          new NotFoundError({
            message: `Organization with id ${organizationId} not found`,
            resource: this.resourceName,
          }),
        );
      }
      return Effect.succeed(org);
    };

    return this.getRole(userId, organizationId).pipe(
      Effect.flatMap((role) =>
        this.verifyPermission(role, "update").pipe(
          Effect.andThen(updateOrganization),
          Effect.flatMap(rejectIfNotFound),
          Effect.map((org) => ({ ...org, role })),
        ),
      ),
    );
  }

  delete(
    organizationId: string,
    userId: string,
  ): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    const deleteOrganizationWithMemberships = Effect.tryPromise({
      try: async () => {
        await this.db.transaction(async (tx) => {
          await tx
            .delete(organizationMemberships)
            .where(eq(organizationMemberships.organizationId, organizationId));

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

    return this.getRole(userId, organizationId).pipe(
      Effect.flatMap((role) => this.verifyPermission(role, "delete")),
      Effect.andThen(deleteOrganizationWithMemberships),
    );
  }
}
