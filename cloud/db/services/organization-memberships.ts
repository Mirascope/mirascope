/**
 * @fileoverview Organization membership service for managing user memberships in organizations.
 *
 * This module provides authenticated CRUD operations for organization memberships
 * with role-based access control. Memberships define the relationship between
 * users and organizations, including their roles.
 *
 * ## Role Hierarchy
 *
 * Organizations support four roles with descending permissions:
 * - `OWNER` - Full control, can manage all roles except other OWNERs
 * - `ADMIN` - Can manage DEVELOPER and VIEWER roles only
 * - `DEVELOPER` - Read-only access (read)
 * - `VIEWER` - Read-only access (read)
 *
 * Users can only create, update, or delete memberships for roles below their own level.
 * No one can add a new OWNER or modify/remove an existing OWNER.
 * No one can modify or remove themselves.
 *
 * ## Architecture
 *
 * ```
 * OrganizationMembershipService (authenticated)
 *   └── baseService: OrganizationMembershipBaseService
 *         └── CRUD on `organization_memberships` table (raw, no auth)
 * ```
 *
 * ## Usage
 *
 * ```ts
 * const membershipService = new OrganizationMembershipService(db);
 *
 * // Add a member to an organization (ADMIN adding a DEVELOPER)
 * const membership = yield* membershipService.create({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   data: { userId: "new-user-789", role: "DEVELOPER" },
 * });
 *
 * // List all members
 * const members = yield* membershipService.findAll({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 * });
 * ```
 */

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
import {
  organizationMemberships,
  type PublicOrganizationMembership,
  type NewOrganizationMembership,
  type Role,
} from "@/db/schema";

// =============================================================================
// Base Service (Internal)
// =============================================================================

/**
 * Low-level CRUD service for the organization_memberships table.
 *
 * This is an internal service used by `OrganizationMembershipService` for managing
 * the relationship between users and organizations, including their roles.
 *
 * Path pattern: `organizations/:organizationId/memberships/:targetUserId`
 * - Parent param: `organizationId` (scopes to organization)
 * - Resource ID: `targetUserId` (identifies the membership by the target user)
 */
class OrganizationMembershipBaseService extends BaseService<
  PublicOrganizationMembership,
  "organizations/:organizationId/users/:targetUserId",
  typeof organizationMemberships
> {
  protected getTable() {
    return organizationMemberships;
  }

  protected getResourceName() {
    return "organization membership";
  }

  protected getIdParamName() {
    return "targetUserId" as const;
  }

  /**
   * Override to use `userId` column instead of `id` for lookups.
   *
   * Memberships are uniquely identified by (organizationId, userId),
   * so we use `targetUserId` as the resource identifier in the path pattern,
   * which maps to the `userId` column in the database.
   */
  protected getIdColumn() {
    return organizationMemberships.userId;
  }

  protected getPublicFields() {
    return {
      id: organizationMemberships.id,
      role: organizationMemberships.role,
      createdAt: organizationMemberships.createdAt,
    };
  }
}

// =============================================================================
// Organization Membership Service (Public)
// =============================================================================

/**
 * Authenticated service for organization membership management.
 *
 * Provides CRUD operations with role-based access control for memberships.
 * Users can only operate on roles below their own level in the hierarchy.
 *
 * ## Permission Matrix
 *
 * | Action   | OWNER | ADMIN | DEVELOPER | VIEWER |
 * |----------|-------|-------|-----------|--------|
 * | create   | ✓*    | ✓**   | ✗         | ✗      |
 * | read     | ✓     | ✓     | ✓         | ✓      |
 * | update   | ✓*    | ✓**   | ✗         | ✗      |
 * | delete   | ✓*    | ✓**   | ✗         | ✗      |
 *
 * *OWNER can operate on ADMIN, DEVELOPER, VIEWER (not OWNER)
 * **ADMIN can only operate on DEVELOPER, VIEWER (not OWNER or ADMIN)
 *
 * ## Security Model
 *
 * - Non-members cannot see that an organization exists (returns NotFoundError)
 * - Cannot add a new OWNER (organizations have exactly one owner, set at creation)
 * - Cannot modify or remove an existing OWNER
 * - Cannot operate on roles at or above your own level (except read)
 * - Cannot modify or remove yourself
 */
export class OrganizationMembershipService extends BaseAuthenticatedService<
  PublicOrganizationMembership,
  "organizations/:organizationId/users/:targetUserId",
  typeof organizationMemberships,
  Pick<NewOrganizationMembership, "userId" | "role">,
  Role
> {
  // ---------------------------------------------------------------------------
  // Base Service Implementation
  // ---------------------------------------------------------------------------

  protected initializeBaseService() {
    return new OrganizationMembershipBaseService(this.db);
  }

  protected getPermissionTable(): PermissionTable<Role> {
    // Note: The permission table grants base access. Role hierarchy checks
    // (e.g., ADMIN can only operate on DEVELOPER/VIEWER) are enforced
    // in individual methods.
    return {
      create: ["OWNER", "ADMIN"],
      read: ["OWNER", "ADMIN", "DEVELOPER", "VIEWER"],
      update: ["OWNER", "ADMIN"],
      delete: ["OWNER", "ADMIN"],
    };
  }

  // ---------------------------------------------------------------------------
  // Role Hierarchy Helpers
  // ---------------------------------------------------------------------------

  /**
   * Defines which roles each role can operate on (create, update, delete).
   *
   * | Actor Role | Can Operate On                |
   * |------------|-------------------------------|
   * | OWNER      | ADMIN, DEVELOPER, VIEWER      |
   * | ADMIN      | DEVELOPER, VIEWER             |
   * | DEVELOPER  | (none)                        |
   * | VIEWER     | (none)                        |
   *
   * TODO: Refactor `authorize` to better handle these types of more granular ACLs
   */
  private static readonly CAN_OPERATE_ON: Record<Role, Role[]> = {
    OWNER: ["ADMIN", "DEVELOPER", "VIEWER"],
    ADMIN: ["DEVELOPER", "VIEWER"],
    DEVELOPER: [],
    VIEWER: [],
  };

  /**
   * Checks if the user's role can operate on the target role.
   *
   * @param userRole - The role of the authenticated user performing the action
   * @param targetRole - The role being created, modified, or deleted
   * @returns true if the user can operate on the target role
   */
  private canOperateOn(userRole: Role, targetRole: Role): boolean {
    return OrganizationMembershipService.CAN_OPERATE_ON[userRole].includes(
      targetRole,
    );
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Fetches a membership record from the database.
   *
   * This is a low-level helper that returns null if no membership exists,
   * allowing callers to handle the "not found" case with appropriate error messages.
   *
   * @param args.userId - The user to look up
   * @param args.organizationId - The organization to check membership in
   * @returns The membership with role, or null if not found
   * @throws DatabaseError - If the database query fails
   */
  protected getMembership({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<{ role: Role } | null, DatabaseError> {
    return Effect.tryPromise({
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
        return membership ?? null;
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to get membership",
          cause: error,
        }),
    });
  }

  /**
   * Determines the user's role in an organization.
   *
   * This method is called by `authorize()` to check permissions before
   * performing operations. It intentionally returns `NotFoundError` for
   * non-members to hide organization existence from unauthorized users.
   *
   * @param args.organizationId - The organization to check membership in
   * @param args.userId - The user to check (the authenticated user, not the target)
   * @returns The user's role in the organization
   * @throws NotFoundError - If the user is not a member (hides org existence)
   * @throws DatabaseError - If the database query fails
   */
  getRole({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<Role, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const membership = yield* this.getMembership({ userId, organizationId });

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

  // ---------------------------------------------------------------------------
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new membership for a user in an organization.
   *
   * Requires OWNER or ADMIN role. Role hierarchy is enforced:
   * - OWNER can add ADMIN, DEVELOPER, or VIEWER
   * - ADMIN can only add DEVELOPER or VIEWER
   * - Cannot add an OWNER (organizations have exactly one owner)
   * - Cannot add yourself
   *
   * Security: `organizationId` path param is authoritative and overwrites any
   * conflicting value in `data` to prevent injection attacks.
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization to add the member to (path param)
   * @param args.data.userId - The user to add as a member
   * @param args.data.role - The role to assign (must be below actor's role level)
   * @returns The created membership
   * @throws PermissionDeniedError - If role hierarchy violation or self-invite
   * @throws AlreadyExistsError - If the user is already a member
   * @throws NotFoundError - If the organization doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  create({
    userId,
    organizationId,
    data,
  }: {
    userId: string;
    organizationId: string;
    data: Pick<NewOrganizationMembership, "userId" | "role">;
  }): Effect.Effect<
    PublicOrganizationMembership,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const userRole = yield* this.authorize({
        userId,
        action: "create",
        organizationId,
      });

      if (data.userId === userId) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Cannot add yourself to an organization",
            resource: "organization membership",
          }),
        );
      }

      // Enforce role hierarchy: can only add roles you can operate on
      if (!this.canOperateOn(userRole, data.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot add a member with role ${data.role}`,
            resource: "organization membership",
          }),
        );
      }

      return yield* this.baseService.create({
        organizationId,
        data: {
          ...data,
          organizationId,
        },
      });
    });
  }

  /**
   * Retrieves all memberships for an organization.
   *
   * Requires membership in the organization (any role).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization to list memberships for
   * @returns Array of memberships with role and creation date
   * @throws NotFoundError - If the organization doesn't exist or user isn't a member
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findAll({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    PublicOrganizationMembership[],
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ userId, action: "read", organizationId });
      return yield* this.baseService.findAll({ organizationId });
    });
  }

  /**
   * Retrieves a specific membership by target user ID.
   *
   * Requires membership in the organization (any role).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization
   * @param args.targetUserId - The user whose membership to retrieve
   * @returns The membership with role and creation date
   * @throws NotFoundError - If the membership doesn't exist
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findById({
    userId,
    organizationId,
    targetUserId,
  }: {
    userId: string;
    organizationId: string;
    targetUserId: string;
  }): Effect.Effect<
    PublicOrganizationMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ userId, action: "read", organizationId });
      return yield* this.baseService.findById({
        organizationId,
        targetUserId,
      });
    });
  }

  /**
   * Updates a membership's role.
   *
   * Requires OWNER or ADMIN role. Role hierarchy is enforced:
   * - OWNER can change ADMIN/DEVELOPER/VIEWER to ADMIN/DEVELOPER/VIEWER
   * - ADMIN can only change DEVELOPER/VIEWER to DEVELOPER/VIEWER
   * - Cannot change anyone's role to OWNER
   * - Cannot change an OWNER's role
   * - Cannot change your own role
   *
   * Security: Path params (`organizationId`, `targetUserId`) are authoritative.
   * The `data` type excludes these fields to prevent injection attacks.
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization (path param)
   * @param args.targetUserId - The user whose membership to update (path param)
   * @param args.data - Fields to update (only `role` allowed, must be below actor's level)
   * @returns The updated membership
   * @throws PermissionDeniedError - If role hierarchy violation or self-modification
   * @throws NotFoundError - If the membership doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  update({
    userId,
    organizationId,
    targetUserId,
    data,
  }: {
    userId: string;
    organizationId: string;
    targetUserId: string;
    data: Pick<NewOrganizationMembership, "role">;
  }): Effect.Effect<
    PublicOrganizationMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const userRole = yield* this.authorize({
        userId,
        action: "update",
        organizationId,
      });

      if (targetUserId === userId) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Cannot modify your own membership",
            resource: "organization membership",
          }),
        );
      }

      const targetMembership = yield* this.getMembership({
        userId: targetUserId,
        organizationId,
      });

      if (!targetMembership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User is not a member of this organization",
            resource: "organization membership",
          }),
        );
      }

      // Enforce role hierarchy: can only modify roles you can operate on
      if (!this.canOperateOn(userRole, targetMembership.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot modify a member with role ${targetMembership.role}`,
            resource: "organization membership",
          }),
        );
      }

      // Enforce role hierarchy: can only assign roles you can operate on
      if (!this.canOperateOn(userRole, data.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot change a member's role to ${data.role}`,
            resource: "organization membership",
          }),
        );
      }

      return yield* this.baseService.update({
        organizationId,
        targetUserId,
        data: { role: data.role },
      });
    });
  }

  /**
   * Removes a member from an organization.
   *
   * Requires OWNER or ADMIN role. Role hierarchy is enforced:
   * - OWNER can remove ADMIN, DEVELOPER, or VIEWER
   * - ADMIN can only remove DEVELOPER or VIEWER
   * - Cannot remove an OWNER
   * - Cannot remove yourself
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization
   * @param args.targetUserId - The user to remove
   * @throws PermissionDeniedError - If role hierarchy violation or self-removal
   * @throws NotFoundError - If the membership doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  delete({
    userId,
    organizationId,
    targetUserId,
  }: {
    userId: string;
    organizationId: string;
    targetUserId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const userRole = yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
      });

      if (targetUserId === userId) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Cannot remove yourself from an organization",
            resource: "organization membership",
          }),
        );
      }

      const targetMembership = yield* this.getMembership({
        userId: targetUserId,
        organizationId,
      });

      if (!targetMembership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User is not a member of this organization",
            resource: "organization membership",
          }),
        );
      }

      // Enforce role hierarchy: can only remove roles you can operate on
      if (!this.canOperateOn(userRole, targetMembership.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot remove a member with role ${targetMembership.role}`,
            resource: "organization membership",
          }),
        );
      }

      return yield* this.baseService.delete({
        organizationId,
        targetUserId,
      });
    });
  }
}
