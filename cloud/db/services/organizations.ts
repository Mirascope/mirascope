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
  protected getTable() {
    return organizations;
  }

  protected getResourceName() {
    return "organization";
  }

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
  ): Effect.Effect<void, PermissionDeniedError | DatabaseError> {
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
    ): Effect.Effect<void, PermissionDeniedError> => {
      if (!membership) {
        return Effect.fail(
          new PermissionDeniedError({
            message: `You do not have permission to ${action} this organization`,
            resource: this.baseService.resourceName,
          }),
        );
      }

      const requiredRole = REQUIRED_ROLE_FOR_ACTION[action];
      const userRoleLevel = ROLE_HIERARCHY[membership.role];
      const requiredRoleLevel = ROLE_HIERARCHY[requiredRole];

      if (userRoleLevel < requiredRoleLevel) {
        return Effect.fail(
          new PermissionDeniedError({
            message: `You do not have permission to ${action} this organization`,
            resource: this.baseService.resourceName,
          }),
        );
      }

      return Effect.succeed(undefined);
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
    const fetchExistingOrganization = Effect.tryPromise({
      try: async () => {
        const [existing] = await this.db
          .select({ name: organizations.name })
          .from(organizations)
          .where(eq(organizations.name, data.name))
          .limit(1);
        return existing;
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to check for existing organization",
          cause: error,
        }),
    });

    const rejectIfExists = (
      existing: { name: string } | undefined,
    ): Effect.Effect<void, AlreadyExistsError> => {
      if (existing) {
        return Effect.fail(
          new AlreadyExistsError({
            message: "An organization with this name already exists",
            resource: this.baseService.resourceName,
          }),
        );
      }
      return Effect.succeed(undefined);
    };

    const createOrganizationWithOwner = Effect.tryPromise({
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
      catch: (error) =>
        new DatabaseError({
          message: "Failed to create organization",
          cause: error,
        }),
    });

    return fetchExistingOrganization.pipe(
      Effect.flatMap(rejectIfExists),
      Effect.andThen(createOrganizationWithOwner),
    );
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

  override delete(
    id: string,
    userId: string,
  ): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    const fetchOrganization = Effect.tryPromise({
      try: async () => {
        const [org] = await this.db
          .select({ id: organizations.id })
          .from(organizations)
          .where(eq(organizations.id, id))
          .limit(1);
        return org;
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to find organization",
          cause: error,
        }),
    });

    const rejectIfNotFound = (
      org: { id: string } | undefined,
    ): Effect.Effect<{ id: string }, NotFoundError> => {
      if (!org) {
        return Effect.fail(
          new NotFoundError({
            message: `Organization with id ${id} not found`,
            resource: this.baseService.resourceName,
          }),
        );
      }
      return Effect.succeed(org);
    };

    const deleteOrganizationWithMemberships = Effect.tryPromise({
      try: async () => {
        await this.db.transaction(async (tx) => {
          await tx
            .delete(organizationMemberships)
            .where(eq(organizationMemberships.organizationId, id));

          await tx.delete(organizations).where(eq(organizations.id, id));
        });
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to delete organization",
          cause: error,
        }),
    });

    return fetchOrganization.pipe(
      Effect.flatMap(rejectIfNotFound),
      Effect.andThen(this.checkPermission(userId, "delete", id)),
      Effect.andThen(deleteOrganizationWithMemberships),
    );
  }
}
