/**
 * @fileoverview Effect-native Organizations service.
 *
 * Provides authenticated CRUD operations for organizations with role-based
 * access control. Organizations are the top-level tenant resource that users
 * can be members of with different roles.
 *
 * ## Role Hierarchy
 *
 * Organizations support three roles with descending permissions:
 * - `OWNER` - Full control (create, read, update, delete)
 * - `ADMIN` - Administrative access (read, update)
 * - `MEMBER` - Read-only access (read)
 *
 * ## Security Model
 *
 * - Non-members cannot see that an organization exists (returns NotFoundError)
 * - Creating an organization automatically makes the creator an OWNER
 * - Cascade deletes handle memberships and audit logs
 *
 * TODO: add support for a GUEST role for adding non-members to projects.
 *
 * @example
 * ```ts
 * const db = yield* EffectDatabase;
 *
 * // Create organization (user becomes OWNER)
 * const org = yield* db.organizations.create({
 *   userId: "user-123",
 *   data: { name: "My Organization" },
 * });
 *
 * // List user's organizations
 * const orgs = yield* db.organizations.findAll({ userId: "user-123" });
 *
 * // Update organization (requires OWNER or ADMIN)
 * yield* db.organizations.update({
 *   userId: "user-123",
 *   organizationId: org.id,
 *   data: { name: "New Name" },
 * });
 *
 * // Access memberships via nested service
 * const members = yield* db.organizations.memberships.findAll({
 *   userId: "user-123",
 *   organizationId: org.id,
 * });
 * ```
 */

import { Effect } from "effect";
import { eq } from "drizzle-orm";
import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { isUniqueConstraintError } from "@/db/utils";
import { OrganizationMemberships } from "@/db/organization-memberships";

import {
  organizations,
  organizationMemberships,
  organizationMembershipAudit,
  type NewOrganization,
  type PublicOrganization,
  type PublicOrganizationWithMembership,
  type OrganizationRole,
} from "@/db/schema";

/**
 * Public fields to select from the organizations table.
 */
const publicFields = {
  id: organizations.id,
  name: organizations.name,
};

/**
 * Effect-native Organizations service.
 *
 * Provides CRUD operations with role-based access control for organizations.
 * Users interact with organizations through memberships, and their role
 * determines what actions they can perform.
 *
 * ## Permission Matrix
 *
 * | Action   | OWNER | ADMIN | MEMBER |
 * |----------|-------|-------|--------|
 * | create   | ✓     | ✗     | ✗      |
 * | read     | ✓     | ✓     | ✓      |
 * | update   | ✓     | ✓     | ✗      |
 * | delete   | ✓     | ✗     | ✗      |
 */
export class Organizations extends BaseAuthenticatedEffectService<
  PublicOrganization,
  "organizations/:organizationId",
  NewOrganization,
  Partial<NewOrganization>,
  OrganizationRole
> {
  /**
   * Nested service for managing organization memberships.
   */
  public readonly memberships: OrganizationMemberships;

  constructor(memberships: OrganizationMemberships) {
    super();
    this.memberships = memberships;
  }

  // ---------------------------------------------------------------------------
  // Base Implementation
  // ---------------------------------------------------------------------------

  protected getResourceName(): string {
    return "organization";
  }

  protected getPermissionTable(): PermissionTable<OrganizationRole> {
    return {
      create: ["OWNER"], // Handled separately (no org exists yet)
      read: ["OWNER", "ADMIN", "MEMBER"],
      update: ["OWNER", "ADMIN"],
      delete: ["OWNER"],
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Determines the user's role in an organization.
   *
   * Delegates to the memberships service since the role is stored in the
   * organization_memberships table.
   *
   * @param args.organizationId - The organization to check membership in
   * @param args.userId - The user to check
   * @returns The user's role in the organization
   * @throws NotFoundError - If the user is not a member (hides org existence)
   * @throws DatabaseError - If the database query fails
   */
  protected getRole({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    OrganizationRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const { role } = yield* this.memberships.findById({
        userId,
        organizationId,
        memberId: userId,
      });
      return role;
    });
  }

  // ---------------------------------------------------------------------------
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new organization and assigns the creator as OWNER.
   *
   * This is a special case that doesn't require prior authorization since
   * no organization exists yet. The creating user automatically becomes
   * the organization's owner.
   *
   * Performs an atomic transaction:
   * 1. Insert the organization
   * 2. Create an OWNER membership for the user
   * 3. Create an audit log for the OWNER grant
   *
   * @param args.userId - The user creating the organization (becomes OWNER)
   * @param args.data - Organization data (name)
   * @returns The created organization with the user's role
   * @throws AlreadyExistsError - If an organization with this name exists
   * @throws DatabaseError - If the database operation fails
   */
  create({
    userId,
    data,
  }: {
    userId: string;
    data: NewOrganization;
  }): Effect.Effect<
    PublicOrganizationWithMembership,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      return yield* client.withTransaction(
        Effect.gen(function* () {
          // Insert the organization
          const results = yield* client
            .insert(organizations)
            .values({ name: data.name })
            .returning(publicFields)
            .pipe(
              Effect.mapError((e): AlreadyExistsError | DatabaseError =>
                isUniqueConstraintError(e.cause)
                  ? new AlreadyExistsError({
                      message: "An organization with this name already exists",
                      resource: "organization",
                    })
                  : new DatabaseError({
                      message: "Failed to create organization",
                      cause: e,
                    }),
              ),
            );

          const organization = results[0] as PublicOrganization;

          // Create OWNER membership
          yield* client
            .insert(organizationMemberships)
            .values({
              memberId: userId,
              organizationId: organization.id,
              role: "OWNER",
            })
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to create organization membership",
                    cause: e,
                  }),
              ),
            );

          // Create audit log for OWNER grant
          yield* client
            .insert(organizationMembershipAudit)
            .values({
              organizationId: organization.id,
              actorId: userId,
              targetId: userId,
              action: "GRANT",
              newRole: "OWNER",
            })
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to create audit log",
                    cause: e,
                  }),
              ),
            );

          return {
            ...organization,
            role: "OWNER" as OrganizationRole,
          };
        }),
      );
    });
  }

  /**
   * Retrieves all organizations the user is a member of.
   *
   * Returns organizations with the user's role in each. This is a membership-
   * scoped query that only returns organizations where the user has a role.
   *
   * @param args.userId - The user to get organizations for
   * @returns Array of organizations with the user's role in each
   * @throws DatabaseError - If the database query fails
   */
  findAll({
    userId,
  }: {
    userId: string;
  }): Effect.Effect<
    PublicOrganizationWithMembership[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const results = yield* client
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
        .where(eq(organizationMemberships.memberId, userId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get user organizations",
                cause: e,
              }),
          ),
        );

      return results as PublicOrganizationWithMembership[];
    });
  }

  /**
   * Retrieves an organization by ID.
   *
   * Requires the user to be a member of the organization (any role).
   * Returns the organization with the user's role.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization to retrieve
   * @returns The organization with the user's role
   * @throws NotFoundError - If the organization doesn't exist or user isn't a member
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findById({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    PublicOrganizationWithMembership,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize and get role
      const role = yield* this.authorize({
        userId,
        action: "read",
        organizationId,
      });

      // Fetch the organization
      const [organization] = yield* client
        .select(publicFields)
        .from(organizations)
        .where(eq(organizations.id, organizationId))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find organization",
                cause: e,
              }),
          ),
        );

      if (!organization) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Organization with organizationId ${organizationId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return { ...organization, role };
    });
  }

  /**
   * Updates an organization.
   *
   * Requires OWNER or ADMIN role.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization to update
   * @param args.data - Fields to update (name)
   * @returns The updated organization with the user's role
   * @throws NotFoundError - If the organization doesn't exist or user isn't a member
   * @throws PermissionDeniedError - If the user lacks update permission
   * @throws DatabaseError - If the database operation fails
   */
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
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize and get role
      const role = yield* this.authorize({
        userId,
        action: "update",
        organizationId,
      });

      // Update the organization
      const [updated] = yield* client
        .update(organizations)
        .set({ ...data, updatedAt: new Date() })
        .where(eq(organizations.id, organizationId))
        .returning(publicFields)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to update organization",
                cause: e,
              }),
          ),
        );

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `organization with organizationId ${organizationId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return { ...updated, role };
    });
  }

  /**
   * Deletes an organization and all its memberships.
   *
   * Requires OWNER role. This is a destructive operation that deletes
   * the organization and all related data via cascade.
   *
   * @param args.userId - The authenticated user (must be OWNER)
   * @param args.organizationId - The organization to delete
   * @throws NotFoundError - If the organization doesn't exist or user isn't a member
   * @throws PermissionDeniedError - If the user is not an OWNER
   * @throws DatabaseError - If the database operation fails
   */
  delete({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize (only OWNER can delete)
      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
      });

      // Delete the organization (cascade handles memberships and audits)
      yield* client
        .delete(organizations)
        .where(eq(organizations.id, organizationId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete organization",
                cause: e,
              }),
          ),
        );
    });
  }
}
