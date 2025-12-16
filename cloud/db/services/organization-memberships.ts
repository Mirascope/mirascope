/**
 * @fileoverview Organization membership service for managing user memberships in organizations.
 *
 * This module provides authenticated CRUD operations for organization memberships
 * with role-based access control. Memberships define the relationship between
 * users and organizations, including their roles.
 *
 * ## Role Hierarchy
 *
 * Organizations support three roles with descending permissions:
 * - `OWNER` - Full control, can manage all roles except other OWNERs
 * - `ADMIN` - Can manage MEMBER role only
 * - `MEMBER` - Read-only access (read)
 *
 * Users can only create, update, or delete memberships for roles below their own level.
 * No one can add a new OWNER or modify/remove an existing OWNER.
 * Users can remove themselves from an organization (except OWNERs).
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
 * // Add a member to an organization (ADMIN adding a MEMBER)
 * const membership = yield* membershipService.create({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   data: { memberId: "new-user-789", role: "MEMBER" },
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
import { isUniqueConstraintError } from "@/db/utils";
import {
  organizationMemberships,
  organizationMembershipAudit,
  type PublicOrganizationMembership,
  type PublicOrganizationMembershipAudit,
  type NewOrganizationMembership,
  type OrganizationRole,
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
 * Path pattern: `organizations/:organizationId/members/:memberId`
 * - Parent param: `organizationId` (scopes to organization)
 * - Resource ID: `memberId` (the user's ID who is a member)
 */
class OrganizationMembershipBaseService extends BaseService<
  PublicOrganizationMembership,
  "organizations/:organizationId/members/:memberId",
  typeof organizationMemberships
> {
  protected getTable() {
    return organizationMemberships;
  }

  protected getResourceName() {
    return "organization membership";
  }

  protected getIdParamName() {
    return "memberId" as const;
  }

  /**
   * Override since this table uses `memberId` instead of the default `id` column.
   */
  protected getIdColumn() {
    return organizationMemberships.memberId;
  }

  protected getPublicFields() {
    return {
      memberId: organizationMemberships.memberId,
      role: organizationMemberships.role,
      createdAt: organizationMemberships.createdAt,
    };
  }
}

/**
 * Low-level read service for the organization_membership_audit table.
 *
 * This is an internal service used for querying audit logs of membership changes.
 * It follows the same path pattern as memberships but adds an audit segment.
 *
 * Path pattern: `organizations/:organizationId/members/:memberId/audits/:id`
 * - Parent params: `organizationId`, `memberId` (maps to targetId column)
 * - Resource ID: `id` (the audit entry's own ID)
 */
class OrganizationMembershipAuditBaseService extends BaseService<
  PublicOrganizationMembershipAudit,
  "organizations/:organizationId/members/:memberId/audits/:id",
  typeof organizationMembershipAudit
> {
  protected getTable() {
    return organizationMembershipAudit;
  }

  /* v8 ignore start - we currently only use this service in testing for `.findAll` */
  protected getResourceName() {
    return "organization membership audit";
  }

  protected getIdParamName() {
    return "id" as const;
  }
  /* v8 ignore end */

  protected getPublicFields() {
    return {
      id: organizationMembershipAudit.id,
      actorId: organizationMembershipAudit.actorId,
      targetId: organizationMembershipAudit.targetId,
      action: organizationMembershipAudit.action,
      previousRole: organizationMembershipAudit.previousRole,
      newRole: organizationMembershipAudit.newRole,
      createdAt: organizationMembershipAudit.createdAt,
    };
  }

  /**
   * Override to map `memberId` param to `targetId` column.
   * The path uses `:memberId` to match the membership pattern, but the audit
   * table stores this as `targetId`.
   */
  protected getParentScopedWhere(params: {
    organizationId: string;
    memberId: string;
  }) {
    return and(
      eq(organizationMembershipAudit.organizationId, params.organizationId),
      eq(organizationMembershipAudit.targetId, params.memberId),
    );
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
 * | Action   | OWNER | ADMIN | MEMBER |
 * |----------|-------|-------|--------|
 * | create   | ✓*    | ✓**   | ✗      |
 * | read     | ✓     | ✓     | ✓      |
 * | update   | ✓*    | ✓**   | ✗      |
 * | delete   | ✓*    | ✓**   | ✗      |
 *
 * *OWNER can operate on ADMIN, MEMBER (not OWNER)
 * **ADMIN can only operate on MEMBER (not OWNER or ADMIN)
 *
 * ## Security Model
 *
 * - Non-members cannot see that an organization exists (returns NotFoundError)
 * - Cannot add a new OWNER (organizations have exactly one owner, set at creation)
 * - Cannot modify or remove an existing OWNER
 * - Cannot operate on roles at or above your own level (except read)
 * - Cannot modify yourself; can remove yourself (except OWNER)
 */
export class OrganizationMembershipService extends BaseAuthenticatedService<
  PublicOrganizationMembership,
  "organizations/:organizationId/members/:memberId",
  typeof organizationMemberships,
  { memberId: string; role: OrganizationRole },
  OrganizationRole
> {
  // ---------------------------------------------------------------------------
  // Base Service Implementation
  // ---------------------------------------------------------------------------

  /**
   * Service for querying audit logs of membership changes.
   * Use `audits.findAll({ organizationId, memberId })` to get audit entries for a member.
   */
  public readonly audits: OrganizationMembershipAuditBaseService;

  constructor(db: ConstructorParameters<typeof BaseAuthenticatedService>[0]) {
    super(db);
    this.audits = new OrganizationMembershipAuditBaseService(db);
  }

  protected initializeBaseService() {
    return new OrganizationMembershipBaseService(this.db);
  }

  protected getPermissionTable(): PermissionTable<OrganizationRole> {
    // Note: The permission table grants base access. Role hierarchy checks
    // (e.g., ADMIN can only operate on MEMBER) are enforced
    // in individual methods.
    return {
      create: ["OWNER", "ADMIN"],
      read: ["OWNER", "ADMIN", "MEMBER"],
      update: ["OWNER", "ADMIN"],
      delete: ["OWNER", "ADMIN", "MEMBER"], // MEMBER can delete themselves but cannot operate on anyone else
    };
  }

  // ---------------------------------------------------------------------------
  // Role Hierarchy Helpers
  // ---------------------------------------------------------------------------

  /**
   * Defines which roles each role can operate on (create, update, delete).
   *
   * | Actor Role | Can Operate On |
   * |------------|----------------|
   * | OWNER      | ADMIN, MEMBER  |
   * | ADMIN      | MEMBER         |
   * | MEMBER     | (none)         |
   *
   * TODO: Refactor `authorize` to better handle these types of more granular ACLs
   */
  private static readonly CAN_OPERATE_ON: Record<
    OrganizationRole,
    OrganizationRole[]
  > = {
    OWNER: ["ADMIN", "MEMBER"],
    ADMIN: ["MEMBER"],
    MEMBER: [],
  };

  /**
   * Checks if the user's role can operate on the target role.
   *
   * @param userOrganizationRole - The role of the authenticated user performing the action
   * @param targetOrganizationRole - The role being created, modified, or deleted
   * @returns true if the user can operate on the target role
   */
  private canOperateOnOrganizationRole(
    userOrganizationRole: OrganizationRole,
    targetOrganizationRole: OrganizationRole,
  ): boolean {
    return OrganizationMembershipService.CAN_OPERATE_ON[
      userOrganizationRole
    ].includes(targetOrganizationRole);
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
  }): Effect.Effect<{ role: OrganizationRole } | null, DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const [membership] = await this.db
          .select({ role: organizationMemberships.role })
          .from(organizationMemberships)
          .where(
            and(
              eq(organizationMemberships.memberId, userId),
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
  }): Effect.Effect<OrganizationRole, NotFoundError | DatabaseError> {
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
   * - OWNER can add ADMIN or MEMBER
   * - ADMIN can only add MEMBER
   * - Cannot add an OWNER (organizations have exactly one owner)
   * - Cannot add yourself
   *
   * Security: `organizationId` path param is authoritative and overwrites any
   * conflicting value in `data` to prevent injection attacks.
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization to add the member to (path param)
   * @param args.data.memberId - The user ID to add as a member
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
    data: { memberId: string; role: OrganizationRole };
  }): Effect.Effect<
    PublicOrganizationMembership,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const userOrganizationRole = yield* this.authorize({
        userId,
        action: "create",
        organizationId,
      });

      if (data.memberId === userId) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Cannot add yourself to an organization",
            resource: "organization membership",
          }),
        );
      }

      // Enforce role hierarchy: can only add roles you can operate on
      if (!this.canOperateOnOrganizationRole(userOrganizationRole, data.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot add a member with role ${data.role}`,
            resource: "organization membership",
          }),
        );
      }

      // Use transaction to ensure membership and audit log are created atomically
      return yield* Effect.tryPromise({
        try: async () => {
          return await this.db.transaction(async (tx) => {
            // Insert membership
            const [membership] = await tx
              .insert(organizationMemberships)
              .values({
                memberId: data.memberId,
                organizationId,
                role: data.role,
              })
              .returning({
                memberId: organizationMemberships.memberId,
                role: organizationMemberships.role,
                createdAt: organizationMemberships.createdAt,
              });

            // Log audit
            await tx.insert(organizationMembershipAudit).values({
              organizationId,
              actorId: userId,
              targetId: data.memberId,
              action: "GRANT",
              newRole: data.role,
            });

            return membership as PublicOrganizationMembership;
          });
        },
        catch: (error) => {
          if (isUniqueConstraintError(error)) {
            return new AlreadyExistsError({
              message: "User is already a member of this organization",
              resource: "organization membership",
            });
          }
          return new DatabaseError({
            message: "Failed to create organization membership",
            cause: error,
          });
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
   * Retrieves a specific membership by member ID.
   *
   * Requires membership in the organization (any role).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization
   * @param args.memberId - The user ID of the member to retrieve
   * @returns The membership with role and creation date
   * @throws NotFoundError - If the membership doesn't exist
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findById({
    userId,
    organizationId,
    memberId,
  }: {
    userId: string;
    organizationId: string;
    memberId: string;
  }): Effect.Effect<
    PublicOrganizationMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ userId, action: "read", organizationId });
      return yield* this.baseService.findById({
        organizationId,
        memberId,
      });
    });
  }

  /**
   * Updates a membership's role.
   *
   * Requires OWNER or ADMIN role. Role hierarchy is enforced:
   * - OWNER can change MEMBER to ADMIN or MEMBER (cannot affect OWNER)
   * - ADMIN can only change MEMBER to MEMBER (no-op) and cannot change ADMIN/OWNER
   * - Cannot change anyone's role to OWNER
   * - Cannot change an OWNER's role
   * - Cannot change your own role
   *
   * Security: Path params (`organizationId`, `memberId`) are authoritative.
   * The `data` type excludes these fields to prevent injection attacks.
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization (path param)
   * @param args.memberId - The user ID of the member to update (path param)
   * @param args.data - Fields to update (only `role` allowed, must be below actor's level)
   * @returns The updated membership
   * @throws PermissionDeniedError - If role hierarchy violation or self-modification
   * @throws NotFoundError - If the membership doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  update({
    userId,
    organizationId,
    memberId,
    data,
  }: {
    userId: string;
    organizationId: string;
    memberId: string;
    data: Pick<NewOrganizationMembership, "role">;
  }): Effect.Effect<
    PublicOrganizationMembership,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const userOrganizationRole = yield* this.authorize({
        userId,
        action: "update",
        organizationId,
      });

      if (memberId === userId) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Cannot modify your own membership",
            resource: "organization membership",
          }),
        );
      }

      const targetMembership = yield* this.getMembership({
        userId: memberId,
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
      if (
        !this.canOperateOnOrganizationRole(
          userOrganizationRole,
          targetMembership.role,
        )
      ) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot modify a member with role ${targetMembership.role}`,
            resource: "organization membership",
          }),
        );
      }

      // Enforce role hierarchy: can only assign roles you can operate on
      if (!this.canOperateOnOrganizationRole(userOrganizationRole, data.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot change a member's role to ${data.role}`,
            resource: "organization membership",
          }),
        );
      }

      const previousRole = targetMembership.role;

      // Use transaction to ensure membership update and audit log are atomic
      return yield* Effect.tryPromise({
        try: async () => {
          return await this.db.transaction(async (tx) => {
            // Update membership
            const [membership] = await tx
              .update(organizationMemberships)
              .set({ role: data.role })
              .where(
                and(
                  eq(organizationMemberships.memberId, memberId),
                  eq(organizationMemberships.organizationId, organizationId),
                ),
              )
              .returning({
                memberId: organizationMemberships.memberId,
                role: organizationMemberships.role,
                createdAt: organizationMemberships.createdAt,
              });

            // Log audit
            await tx.insert(organizationMembershipAudit).values({
              organizationId,
              actorId: userId,
              targetId: memberId,
              action: "CHANGE",
              previousRole,
              newRole: data.role,
            });

            return membership as PublicOrganizationMembership;
          });
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to update organization membership",
            cause: error,
          }),
      });
    });
  }

  /**
   * Removes a member from an organization.
   *
   * Requires OWNER or ADMIN role. Role hierarchy is enforced:
   * - OWNER can remove ADMIN or MEMBER
   * - ADMIN can only remove MEMBER
   * - Cannot remove an OWNER
   *
   * Self-removal is allowed for ADMIN and MEMBER roles (leaving the organization),
   * but OWNERs can never remove themselves.
   *
   * @param args.userId - The authenticated user performing the action
   * @param args.organizationId - The organization
   * @param args.memberId - The user ID of the member to remove
   * @throws PermissionDeniedError - If role hierarchy violation or OWNER self-removal
   * @throws NotFoundError - If the membership doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  delete({
    userId,
    organizationId,
    memberId,
  }: {
    userId: string;
    organizationId: string;
    memberId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const userOrganizationRole = yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
      });

      const targetMembership = yield* this.getMembership({
        userId: memberId,
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

      // ADMIN and MEMBER roles can delete themselves
      const allowedSelfDeletion =
        memberId === userId &&
        ["ADMIN", "MEMBER"].includes(targetMembership.role);

      // Enforce role hierarchy: can only remove roles you can operate on (or yourself)
      if (
        !this.canOperateOnOrganizationRole(
          userOrganizationRole,
          targetMembership.role,
        ) &&
        !allowedSelfDeletion
      ) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot remove a member with role ${targetMembership.role}`,
            resource: "organization membership",
          }),
        );
      }

      // Use transaction to ensure membership deletion and audit log are atomic
      yield* Effect.tryPromise({
        try: async () => {
          await this.db.transaction(async (tx) => {
            // Delete membership
            await tx
              .delete(organizationMemberships)
              .where(
                and(
                  eq(organizationMemberships.memberId, memberId),
                  eq(organizationMemberships.organizationId, organizationId),
                ),
              );

            // Log audit
            await tx.insert(organizationMembershipAudit).values({
              organizationId,
              actorId: userId,
              targetId: memberId,
              action: "REVOKE",
              previousRole: targetMembership.role,
            });
          });
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to delete organization membership",
            cause: error,
          }),
      });
    });
  }
}
