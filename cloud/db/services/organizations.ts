import { Effect } from "effect";
import { and, eq } from "drizzle-orm";
import type { PgColumn } from "drizzle-orm/pg-core";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import {
  BaseService,
  BaseAuthenticatedService,
  type PermissionAction,
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
import type * as schema from "@/db/schema";

/**
 * Minimum role required for each action.
 * Role hierarchy: OWNER > ADMIN > DEVELOPER > ANNOTATOR
 */
const ROLE_HIERARCHY: Record<Role, number> = {
  OWNER: 4,
  ADMIN: 3,
  DEVELOPER: 2,
  ANNOTATOR: 1,
};

const REQUIRED_ROLE_FOR_ACTION: Record<PermissionAction, Role> = {
  read: "ANNOTATOR",
  update: "ADMIN",
  delete: "OWNER",
};

class BaseOrganizationService extends BaseService<
  PublicOrganization,
  string,
  typeof organizations
> {
  /* v8 ignore next 3 */
  protected getTable() {
    return organizations;
  }

  protected getResourceName() {
    return "organization";
  }

  /* v8 ignore next 6 */
  protected getPublicFields(): Record<string, PgColumn> {
    return {
      id: organizations.id,
      name: organizations.name,
    };
  }
}

export class OrganizationService extends BaseAuthenticatedService<
  PublicOrganization,
  string,
  typeof organizations
> {
  protected readonly baseService: BaseOrganizationService;

  constructor(db: PostgresJsDatabase<typeof schema>) {
    super(db);
    this.baseService = new BaseOrganizationService(db);
  }

  protected checkPermission(
    userId: string,
    action: PermissionAction,
    organizationId: string,
  ): Effect.Effect<
    Role,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
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
          message: "Failed to check membership",
          cause: error,
        }),
    });

    const verifyMembershipAndRole = (
      membership: { role: Role } | undefined,
    ): Effect.Effect<Role, NotFoundError | PermissionDeniedError> => {
      // No membership = user is not a member, return NotFoundError to hide existence
      if (!membership) {
        return Effect.fail(
          new NotFoundError({
            message: "Organization not found",
            resource: this.baseService.resourceName,
          }),
        );
      }

      const requiredRole = REQUIRED_ROLE_FOR_ACTION[action];
      const userRoleLevel = ROLE_HIERARCHY[membership.role];
      const requiredRoleLevel = ROLE_HIERARCHY[requiredRole];

      // User is a member but lacks required role
      if (userRoleLevel < requiredRoleLevel) {
        return Effect.fail(
          new PermissionDeniedError({
            message: `You do not have permission to ${action} this organization`,
            resource: this.baseService.resourceName,
          }),
        );
      }

      return Effect.succeed(membership.role);
    };

    return fetchMembership.pipe(Effect.flatMap(verifyMembershipAndRole));
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

  override findById(
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
            resource: this.baseService.resourceName,
          }),
        );
      }
      return Effect.succeed(org);
    };

    return this.checkPermission(userId, "read", organizationId).pipe(
      Effect.flatMap((role) =>
        fetchOrganization.pipe(
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
            resource: this.baseService.resourceName,
          }),
        );
      }
      return Effect.succeed(org);
    };

    return this.checkPermission(userId, "update", organizationId).pipe(
      Effect.flatMap((role) =>
        updateOrganization.pipe(
          Effect.flatMap(rejectIfNotFound),
          Effect.map((org) => ({ ...org, role })),
        ),
      ),
    );
  }

  override delete(
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

    return this.checkPermission(userId, "delete", organizationId).pipe(
      Effect.andThen(deleteOrganizationWithMemberships),
    );
  }
}
