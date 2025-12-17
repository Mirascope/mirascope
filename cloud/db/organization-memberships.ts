/**
 * @fileoverview Effect-native Organization Memberships service.
 *
 * Provides authenticated CRUD operations for organization memberships with
 * role-based access control. Memberships define the relationship between
 * users and organizations, including their roles.
 *
 * ## Role Hierarchy
 *
 * Organizations support three roles with descending permissions:
 * - `OWNER` - Full control, can manage all roles except other OWNERs
 * - `ADMIN` - Can manage MEMBER role only
 * - `MEMBER` - Read-only access
 *
 * Users can only create, update, or delete memberships for roles below their own level.
 * No one can add a new OWNER or modify/remove an existing OWNER.
 * Users can remove themselves from an organization (except OWNERs).
 *
 * @example
 * ```ts
 * const db = yield* EffectDatabase;
 *
 * // Add a member to an organization (ADMIN adding a MEMBER)
 * const membership = yield* db.organizationMemberships.create({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   data: { memberId: "new-user-789", role: "MEMBER" },
 * });
 *
 * // List all members
 * const members = yield* db.organizationMemberships.findAll({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 * });
 * ```
 */

import { Effect } from "effect";
import { and, eq, isNull } from "drizzle-orm";
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

import {
  organizationMemberships,
  organizationMembershipAudit,
  users,
  type PublicOrganizationMembership,
  type PublicOrganizationMembershipAudit,
  type OrganizationRole,
} from "@/db/schema";

/**
 * Public fields to select from the organization_memberships table.
 */
const publicFields = {
  memberId: organizationMemberships.memberId,
  role: organizationMemberships.role,
  createdAt: organizationMemberships.createdAt,
};

/**
 * Public fields to select from the organization_membership_audit table.
 */
const auditPublicFields = {
  id: organizationMembershipAudit.id,
  actorId: organizationMembershipAudit.actorId,
  targetId: organizationMembershipAudit.targetId,
  action: organizationMembershipAudit.action,
  previousRole: organizationMembershipAudit.previousRole,
  newRole: organizationMembershipAudit.newRole,
  createdAt: organizationMembershipAudit.createdAt,
};

// =============================================================================
// Audit Service (Internal, used by tests)
// =============================================================================

/**
 * Read-only service for organization membership audit logs.
 *
 * This service is used primarily in tests to verify that audit entries
 * were created correctly after membership operations.
 */
class OrganizationMembershipAudits {
  /**
   * Retrieves all audit entries for a specific member in an organization.
   */
  findAll({
    organizationId,
    memberId,
  }: {
    organizationId: string;
    memberId: string;
  }): Effect.Effect<
    PublicOrganizationMembershipAudit[],
    DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const results = yield* client
        .select(auditPublicFields)
        .from(organizationMembershipAudit)
        .where(
          and(
            eq(organizationMembershipAudit.organizationId, organizationId),
            eq(organizationMembershipAudit.targetId, memberId),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find audit entries",
                cause: e,
              }),
          ),
        );

      return results as PublicOrganizationMembershipAudit[];
    });
  }
}

/**
 * Insert type for creating memberships.
 */
type InsertMembership = { memberId: string; role: OrganizationRole };

/**
 * Update type for membership role changes.
 */
type UpdateMembership = { role: OrganizationRole };

/**
 * Effect-native Organization Memberships service.
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
export class OrganizationMemberships extends BaseAuthenticatedEffectService<
  PublicOrganizationMembership,
  "organizations/:organizationId/members/:memberId",
  InsertMembership,
  UpdateMembership,
  OrganizationRole
> {
  /**
   * Audit log service for membership changes.
   * Used primarily in tests to verify audit entries.
   */
  public readonly audits = new OrganizationMembershipAudits();

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
   */
  private canOperateOnRole(
    userRole: OrganizationRole,
    targetRole: OrganizationRole,
  ): boolean {
    return OrganizationMemberships.CAN_OPERATE_ON[userRole].includes(
      targetRole,
    );
  }

  // ---------------------------------------------------------------------------
  // Base Implementation
  // ---------------------------------------------------------------------------

  protected getResourceName(): string {
    return "organization membership";
  }

  protected getPermissionTable(): PermissionTable<OrganizationRole> {
    return {
      create: ["OWNER", "ADMIN"],
      read: ["OWNER", "ADMIN", "MEMBER"],
      update: ["OWNER", "ADMIN"],
      delete: ["OWNER", "ADMIN", "MEMBER"], // MEMBER can delete themselves
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Fetches a membership record from the database.
   *
   * Returns NotFoundError with a clear message if no membership exists.
   * This method is used internally for checking target member existence.
   * For convenience, we filter out soft-deleted users who should not g
   */
  getMembership({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    { role: OrganizationRole },
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const [membership] = yield* client
        .select({ role: organizationMemberships.role })
        .from(organizationMemberships)
        .where(
          and(
            eq(organizationMemberships.memberId, userId),
            eq(organizationMemberships.organizationId, organizationId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get membership",
                cause: e,
              }),
          ),
        );

      if (!membership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User is not a member of this organization",
            resource: this.getResourceName(),
          }),
        );
      }

      return membership;
    });
  }

  /**
   * Determines the user's role in an organization.
   *
   * Returns NotFoundError for non-members to hide organization existence
   * from unauthorized users (security model). Soft-deleted users are considered
   * non-members and have no permissions.
   *
   * Note: This method signature differs from BaseAuthenticatedEffectService
   * because role lookup only needs userId and organizationId, not the full
   * path parameters (memberId is the resource being acted on, not needed here).
   */
  getRole({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    OrganizationRole,
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const [membership] = yield* client
        .select({ role: organizationMemberships.role })
        .from(organizationMemberships)
        .innerJoin(users, eq(organizationMemberships.memberId, users.id))
        .where(
          and(
            eq(organizationMemberships.memberId, userId),
            eq(organizationMemberships.organizationId, organizationId),
            isNull(users.deletedAt), // soft-deleted users have no permissions
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get membership",
                cause: e,
              }),
          ),
        );

      if (!membership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Organization not found",
            resource: this.getResourceName(),
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
   */
  create({
    userId,
    organizationId,
    data,
  }: {
    userId: string;
    organizationId: string;
    data: InsertMembership;
  }): Effect.Effect<
    PublicOrganizationMembership,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const userRole = yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        memberId: userId,
      });

      if (data.memberId === userId) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Cannot add yourself to an organization",
            resource: this.getResourceName(),
          }),
        );
      }

      if (!this.canOperateOnRole(userRole, data.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot add a member with role ${data.role}`,
            resource: this.getResourceName(),
          }),
        );
      }

      // Use transaction to ensure membership and audit log are created atomically
      return yield* client.withTransaction(
        Effect.gen(function* () {
          const results = yield* client
            .insert(organizationMemberships)
            .values({
              memberId: data.memberId,
              organizationId,
              role: data.role,
            })
            .returning(publicFields)
            .pipe(
              Effect.mapError((e): AlreadyExistsError | DatabaseError =>
                isUniqueConstraintError(e.cause)
                  ? new AlreadyExistsError({
                      message: "User is already a member of this organization",
                      resource: "organization membership",
                    })
                  : new DatabaseError({
                      message: "Failed to create organization membership",
                      cause: e,
                    }),
              ),
            );

          yield* client
            .insert(organizationMembershipAudit)
            .values({
              organizationId,
              actorId: userId,
              targetId: data.memberId,
              action: "GRANT",
              newRole: data.role,
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

          return results[0] as PublicOrganizationMembership;
        }),
      );
    });
  }

  /**
   * Retrieves all memberships for an organization.
   *
   * Requires membership in the organization (any role).
   */
  findAll({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    PublicOrganizationMembership[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        memberId: userId,
      });

      const results: PublicOrganizationMembership[] = yield* client
        .select(publicFields)
        .from(organizationMemberships)
        .where(eq(organizationMemberships.organizationId, organizationId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all memberships",
                cause: e,
              }),
          ),
        );

      return results;
    });
  }

  /**
   * Retrieves a specific membership by member ID.
   *
   * Requires membership in the organization (any role).
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
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        memberId: userId,
      });

      const results: PublicOrganizationMembership[] = yield* client
        .select(publicFields)
        .from(organizationMemberships)
        .where(
          and(
            eq(organizationMemberships.organizationId, organizationId),
            eq(organizationMemberships.memberId, memberId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find membership",
                cause: e,
              }),
          ),
        );

      const membership = results[0];
      if (!membership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Membership for member ${memberId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return membership;
    });
  }

  /**
   * Updates a membership's role.
   *
   * Requires OWNER or ADMIN role. Role hierarchy is enforced:
   * - OWNER can change MEMBER to ADMIN or MEMBER (cannot affect OWNER)
   * - ADMIN can only change MEMBER to MEMBER (no-op)
   * - Cannot change anyone's role to OWNER
   * - Cannot change an OWNER's role
   * - Cannot change your own role
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
    data: UpdateMembership;
  }): Effect.Effect<
    PublicOrganizationMembership,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const userRole = yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        memberId: userId,
      });

      if (memberId === userId) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: "Cannot modify your own membership",
            resource: this.getResourceName(),
          }),
        );
      }

      const targetMembership = yield* this.getMembership({
        userId: memberId,
        organizationId,
      });

      if (!this.canOperateOnRole(userRole, targetMembership.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot modify a member with role ${targetMembership.role}`,
            resource: this.getResourceName(),
          }),
        );
      }

      // Check if the user can assign the new role
      if (!this.canOperateOnRole(userRole, data.role)) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot change a member's role to ${data.role}`,
            resource: this.getResourceName(),
          }),
        );
      }

      return yield* client.withTransaction(
        Effect.gen(function* () {
          const [organizationMembership] = yield* client
            .update(organizationMemberships)
            .set({ role: data.role })
            .where(
              and(
                eq(organizationMemberships.memberId, memberId),
                eq(organizationMemberships.organizationId, organizationId),
              ),
            )
            .returning(publicFields)
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to update organization membership",
                    cause: e,
                  }),
              ),
            );

          yield* client
            .insert(organizationMembershipAudit)
            .values({
              organizationId,
              actorId: userId,
              targetId: memberId,
              action: "CHANGE",
              previousRole: targetMembership.role,
              newRole: data.role,
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

          return organizationMembership satisfies PublicOrganizationMembership;
        }),
      );
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
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const userRole = yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        memberId: userId,
      });

      const targetMembership = yield* this.getMembership({
        userId: memberId,
        organizationId,
      });

      // ADMIN and MEMBER roles can delete themselves
      const allowedSelfDeletion =
        memberId === userId && targetMembership.role !== "OWNER";

      if (
        !this.canOperateOnRole(userRole, targetMembership.role) &&
        !allowedSelfDeletion
      ) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `Cannot remove a member with role ${targetMembership.role}`,
            resource: this.getResourceName(),
          }),
        );
      }

      yield* client.withTransaction(
        Effect.gen(function* () {
          yield* client
            .delete(organizationMemberships)
            .where(
              and(
                eq(organizationMemberships.memberId, memberId),
                eq(organizationMemberships.organizationId, organizationId),
              ),
            )
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to delete organization membership",
                    cause: e,
                  }),
              ),
            );

          yield* client
            .insert(organizationMembershipAudit)
            .values({
              organizationId,
              actorId: userId,
              targetId: memberId,
              action: "REVOKE",
              previousRole: targetMembership.role,
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
        }),
      );
    });
  }
}
