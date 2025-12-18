/**
 * @fileoverview Organization service for multi-tenant organization management.
 *
 * This module provides authenticated CRUD operations for organizations with
 * role-based access control. Organizations are the top-level tenant resource
 * that users can be members of with different roles.
 *
 * ## Role Hierarchy
 *
 * Organizations support three roles with descending permissions:
 * - `OWNER` - Full control (create, read, update, delete)
 * - `ADMIN` - Administrative access (read, update)
 * - `MEMBER` - Read-only access (read)
 *
 * ## Architecture
 *
 * ```
 * OrganizationService (authenticated)
 *   ├── baseService: OrganizationBaseService
 *   │     └── CRUD on `organizations` table (raw, no auth)
 *   └── memberships: OrganizationMembershipService
 *         └── CRUD on `organization_memberships` table (with auth)
 * ```
 *
 * ## Usage
 *
 * ```ts
 * const orgService = new OrganizationService(db);
 *
 * // Create organization (user becomes OWNER)
 * const org = yield* orgService.create({
 *   userId: "user-123",
 *   data: { name: "My Organization" },
 * });
 *
 * // List user's organizations
 * const orgs = yield* orgService.findAll({ userId: "user-123" });
 *
 * // Update organization (requires OWNER or ADMIN)
 * yield* orgService.update({
 *   userId: "user-123",
 *   organizationId: org.id,
 *   data: { name: "New Name" },
 * });
 *
 * // Access memberships via nested service
 * const members = yield* orgService.memberships.findAll({
 *   userId: "user-123",
 *   organizationId: org.id,
 * });
 * ```
 */

import { Effect } from "effect";
import { eq } from "drizzle-orm";
import {
  BaseAuthenticatedService,
  BaseService,
  type PermissionTable,
} from "@/db/services/base";
import { OrganizationMembershipService } from "@/db/services/organization-memberships";
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
  organizationMembershipAudit,
  type NewOrganization,
  type PublicOrganization,
  type PublicOrganizationWithMembership,
  type OrganizationRole,
} from "@/db/schema";

// =============================================================================
// Base Service (Internal)
// =============================================================================

/**
 * Low-level CRUD service for the organizations table.
 *
 * This is an internal service used by `OrganizationService`.
 * It provides raw database operations without authentication or authorization.
 */
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

// =============================================================================
// Organization Service (Public)
// =============================================================================

/**
 * Authenticated service for organization management.
 *
 * Provides CRUD operations with role-based access control for organizations.
 * Users interact with organizations through memberships, and their role
 * determines what actions they can perform.
 *
 * ## Permission Matrix
 *
 * | Action   | OWNER | ADMIN | MEMBER |
 * |----------|-------|-------|--------|
 * | create   | N/A (special handling - creator becomes owner) |
 * | read     | ✓     | ✓     | ✓      |
 * | update   | ✓     | ✓     | ✗      |
 * | delete   | ✓     | ✗     | ✗      |
 *
 * ## Security Model
 *
 * - Non-members cannot see that an organization exists (returns NotFoundError)
 * - Organization existence is hidden from unauthorized users
 * - Creating an organization automatically makes the creator an OWNER
 */
export class OrganizationService extends BaseAuthenticatedService<
  PublicOrganization,
  "organizations/:organizationId",
  typeof organizations,
  NewOrganization,
  OrganizationRole
> {
  /**
   * Nested service for managing organization memberships.
   *
   * Provides CRUD operations for adding, updating, and removing members
   * from an organization.
   *
   * @example
   * ```ts
   * // Add a member
   * yield* orgService.memberships.create({
   *   userId: owner.id,
   *   organizationId: org.id,
   *   targetUserId: newUser.id,
   *   role: "MEMBER",
   * });
   *
   * // List all members
   * yield* orgService.memberships.findAll({
   *   userId: owner.id,
   *   organizationId: org.id,
   * });
   * ```
   */
  public readonly memberships: OrganizationMembershipService;

  constructor(db: ConstructorParameters<typeof BaseAuthenticatedService>[0]) {
    super(db);
    this.memberships = new OrganizationMembershipService(db);
  }

  // ---------------------------------------------------------------------------
  // Base Service Implementation
  // ---------------------------------------------------------------------------

  protected initializeBaseService() {
    return new OrganizationBaseService(this.db);
  }

  protected getPermissionTable(): PermissionTable<OrganizationRole> {
    return {
      create: ["OWNER"], // Handled separately (no org exists yet)
      read: ["OWNER", "ADMIN", "MEMBER"], // All members can read
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
  getRole({
    userId,
    organizationId,
  }: {
    organizationId: string;
    userId: string;
  }): Effect.Effect<OrganizationRole, NotFoundError | DatabaseError> {
    return this.memberships.getRole({ userId, organizationId });
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
            memberId: userId,
            organizationId: organization.id,
            role: "OWNER",
          });

          // Log audit for OWNER membership grant
          await tx.insert(organizationMembershipAudit).values({
            organizationId: organization.id,
            actorId: userId,
            targetId: userId, // OWNER grants to self
            action: "GRANT",
            newRole: "OWNER",
          });

          return {
            id: organization.id,
            name: organization.name,
            role: "OWNER" as OrganizationRole,
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
          .where(eq(organizationMemberships.memberId, userId));
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to get user organizations",
          cause: error,
        }),
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
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const role = yield* this.authorize({
        userId,
        action: "read",
        organizationId,
      });
      const organization = yield* this.baseService.findById({ organizationId });
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
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const role = yield* this.authorize({
        userId,
        action: "update",
        organizationId,
      });
      const organization = yield* this.baseService.update({
        organizationId,
        data,
      });
      return { ...organization, role };
    });
  }

  /**
   * Deletes an organization and all its memberships.
   *
   * Requires OWNER role. This is a destructive operation that:
   * 1. Deletes all organization memberships
   * 2. Deletes the organization
   *
   * Performed as an atomic transaction.
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
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ userId, action: "delete", organizationId });
      // Cascade deletes handle: memberships, membership audits, projects,
      // project memberships, and project membership audits
      yield* Effect.tryPromise({
        try: async () => {
          await this.db
            .delete(organizations)
            .where(eq(organizations.id, organizationId));
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
