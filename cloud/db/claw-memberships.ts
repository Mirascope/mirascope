/**
 * @fileoverview Effect-native Claw Memberships service.
 *
 * Provides authenticated CRUD operations for claw memberships with
 * role-based access control. Memberships define the relationship between
 * users and claws within an organization.
 *
 * ## Claw Roles
 *
 * Claws support four roles:
 * - `ADMIN` - Can manage claw memberships (create, read, update, delete)
 * - `DEVELOPER` - Read-only access to membership info (read)
 * - `VIEWER` - Read-only access to membership info (read)
 * - `ANNOTATOR` - No access (will have access to the annotation queue)
 *
 * NOTE: At the claw level, the `DEVELOPER` and `VIEWER` roles are equivalent (read-only).
 * However, these roles will have more granular permissions for claw resources.
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all claws
 * within their organization, even without explicit claw membership.
 *
 * ## Organization Membership Requirement
 *
 * Users must already be a member of the organization that owns the claw to be
 * added as a claw member.
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Add a developer to a claw
 * const membership = yield* db.organizations.claws.memberships.create({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   clawId: "claw-789",
 *   data: { memberId: "new-user", role: "DEVELOPER" },
 * });
 *
 * // List all claw members
 * const members = yield* db.organizations.claws.memberships.findAll({
 *   userId: "admin-123",
 *   organizationId: "org-456",
 *   clawId: "claw-789",
 * });
 * ```
 */

import { and, eq, isNull } from "drizzle-orm";
import { Effect } from "effect";

import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { OrganizationMemberships } from "@/db/organization-memberships";
import {
  claws,
  clawMemberships,
  clawMembershipAudit,
  users,
  type PublicClawMembership,
  type PublicClawMembershipAudit,
  type ClawRole,
} from "@/db/schema";
import {
  isUniqueConstraintError,
  isForeignKeyConstraintError,
} from "@/db/utils";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";

/**
 * Public fields to select from the claw_memberships table.
 */
const publicFields = {
  memberId: clawMemberships.memberId,
  organizationId: clawMemberships.organizationId,
  clawId: clawMemberships.clawId,
  role: clawMemberships.role,
  createdAt: clawMemberships.createdAt,
};

/**
 * Public fields to select from the claw_membership_audit table.
 */
const auditPublicFields = {
  id: clawMembershipAudit.id,
  actorId: clawMembershipAudit.actorId,
  targetId: clawMembershipAudit.targetId,
  action: clawMembershipAudit.action,
  previousRole: clawMembershipAudit.previousRole,
  newRole: clawMembershipAudit.newRole,
  createdAt: clawMembershipAudit.createdAt,
};

// =============================================================================
// Audit Service (Internal, used by tests)
// =============================================================================

/**
 * Read-only service for claw membership audit logs.
 *
 * This service is used primarily in tests to verify that audit entries
 * were created correctly after membership operations.
 */
class ClawMembershipAudits {
  /**
   * Retrieves all audit entries for a specific member in a claw.
   */
  findAll({
    clawId,
    memberId,
  }: {
    clawId: string;
    memberId: string;
  }): Effect.Effect<PublicClawMembershipAudit[], DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      return yield* client
        .select(auditPublicFields)
        .from(clawMembershipAudit)
        .where(
          and(
            eq(clawMembershipAudit.clawId, clawId),
            eq(clawMembershipAudit.targetId, memberId),
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
    });
  }
}

/**
 * Insert type for creating claw memberships.
 */
type InsertMembership = { memberId: string; role: ClawRole };

/**
 * Update type for claw membership role changes.
 */
type UpdateMembership = { role: ClawRole };

/**
 * Effect-native Claw Memberships service.
 *
 * Provides CRUD operations with role-based access control for claw memberships.
 * Organization OWNER/ADMIN roles have implicit ADMIN access to all claws.
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓     | ✗         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✓      | ✓         |
 * | update   | ✓     | ✗         | ✗      | ✗         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 *
 * ## Security Model
 *
 * - Org OWNER/ADMIN have implicit claw ADMIN access
 * - Non-members cannot see that a claw exists (returns NotFoundError)
 * - ADMIN can modify their own membership; non-ADMIN cannot
 * - All roles can remove themselves from a claw
 * - Target must already be an org member
 */
export class ClawMemberships extends BaseAuthenticatedEffectService<
  PublicClawMembership,
  "organizations/:organizationId/claws/:clawId/members/:memberId",
  InsertMembership,
  UpdateMembership,
  ClawRole
> {
  /**
   * Audit log service for claw membership changes.
   * Used primarily in tests to verify audit entries.
   */
  public readonly audits = new ClawMembershipAudits();

  private readonly organizationMemberships: OrganizationMemberships;

  constructor(organizationMemberships: OrganizationMemberships) {
    super();
    this.organizationMemberships = organizationMemberships;
  }

  // ---------------------------------------------------------------------------
  // Base Implementation
  // ---------------------------------------------------------------------------

  protected getResourceName(): string {
    return "claw membership";
  }

  protected getPermissionTable(): PermissionTable<ClawRole> {
    return {
      create: ["ADMIN"],
      read: ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"],
      update: ["ADMIN"],
      delete: ["ADMIN"],
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Fetches a claw membership record from the database.
   *
   * @throws NotFoundError - If the user is not a member of the claw
   * @throws DatabaseError - If the database query fails
   */
  protected getMembership({
    memberId,
    organizationId,
    clawId,
  }: {
    memberId: string;
    organizationId: string;
    clawId: string;
  }): Effect.Effect<
    { role: ClawRole },
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const [membership] = yield* client
        .select({ role: clawMemberships.role })
        .from(clawMemberships)
        .innerJoin(claws, eq(clawMemberships.clawId, claws.id))
        .where(
          and(
            eq(claws.organizationId, organizationId),
            eq(claws.id, clawId),
            eq(clawMemberships.memberId, memberId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get claw membership",
                cause: e,
              }),
          ),
        );

      if (!membership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User is not a member of this claw",
            resource: this.getResourceName(),
          }),
        );
      }

      return membership;
    });
  }

  /**
   * Determines the user's effective role for a claw.
   *
   * Role resolution follows this priority:
   * 1. Org OWNER → treated as claw ADMIN
   * 2. Org ADMIN → treated as claw ADMIN
   * 3. Explicit claw membership role
   * 4. No access → NotFoundError (hides claw existence)
   */
  getRole({
    userId,
    organizationId,
    clawId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
    memberId?: string;
  }): Effect.Effect<
    ClawRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const { role: userOrganizationRole } =
        yield* this.organizationMemberships.findById({
          organizationId,
          userId,
          memberId: userId,
        });

      // Org OWNER/ADMIN have implicit claw ADMIN access
      if (
        userOrganizationRole === "OWNER" ||
        userOrganizationRole === "ADMIN"
      ) {
        yield* this.verifyClawExists(organizationId, clawId);
        return "ADMIN";
      }

      // Check explicit claw membership
      const { role } = yield* this.getMembership({
        memberId: userId,
        organizationId,
        clawId,
      }).pipe(
        Effect.catchTag("NotFoundError", () =>
          Effect.fail(
            new NotFoundError({
              message: "Claw not found",
              resource: this.getResourceName(),
            }),
          ),
        ),
      );

      return role;
    });
  }

  /**
   * Verifies that a claw exists within the specified organization.
   */
  private verifyClawExists(
    organizationId: string,
    clawId: string,
  ): Effect.Effect<void, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [claw] = yield* client
        .select({ id: claws.id })
        .from(claws)
        .where(
          and(eq(claws.id, clawId), eq(claws.organizationId, organizationId)),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to verify claw",
                cause: e,
              }),
          ),
        );

      if (!claw) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Claw not found",
            resource: "claw",
          }),
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new membership for a user in a claw.
   *
   * Requires ADMIN role (either via implicit org OWNER/ADMIN or explicit claw ADMIN).
   * The target user must already be a member of the organization.
   */
  create({
    userId,
    organizationId,
    clawId,
    data,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
    data: InsertMembership;
  }): Effect.Effect<
    PublicClawMembership,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const resourceName = this.getResourceName();

      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        clawId,
        memberId: userId,
      });

      return yield* client.withTransaction(
        Effect.gen(function* () {
          const [membership] = yield* client
            .insert(clawMemberships)
            .values({
              clawId,
              organizationId,
              memberId: data.memberId,
              role: data.role,
            })
            .returning(publicFields)
            .pipe(
              Effect.mapError(
                (
                  e,
                ):
                  | AlreadyExistsError
                  | PermissionDeniedError
                  | DatabaseError => {
                  if (isUniqueConstraintError(e.cause)) {
                    return new AlreadyExistsError({
                      message: "User is already a member of this claw",
                      resource: "claw membership",
                    });
                  }
                  if (isForeignKeyConstraintError(e.cause)) {
                    return new PermissionDeniedError({
                      message:
                        "User must be a member of the organization before being added to a claw",
                      resource: resourceName,
                    });
                  }
                  return new DatabaseError({
                    message: "Failed to create claw membership",
                    cause: e,
                  });
                },
              ),
            );

          yield* client
            .insert(clawMembershipAudit)
            .values({
              clawId,
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

          return membership as PublicClawMembership;
        }),
      );
    });
  }

  /**
   * Retrieves all memberships for a claw.
   */
  findAll({
    userId,
    organizationId,
    clawId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
  }): Effect.Effect<
    PublicClawMembership[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        clawId,
        memberId: userId,
      });

      return yield* client
        .select(publicFields)
        .from(clawMemberships)
        .where(eq(clawMemberships.clawId, clawId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all claw memberships",
                cause: e,
              }),
          ),
        );
    });
  }

  /**
   * Retrieves a specific membership by member ID.
   */
  findById({
    userId,
    organizationId,
    clawId,
    memberId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
    memberId: string;
  }): Effect.Effect<
    PublicClawMembership,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        clawId,
        memberId: userId,
      });

      const [membership] = yield* client
        .select(publicFields)
        .from(clawMemberships)
        .where(
          and(
            eq(clawMemberships.clawId, clawId),
            eq(clawMemberships.memberId, memberId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find claw membership",
                cause: e,
              }),
          ),
        );

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
   */
  update({
    userId,
    organizationId,
    clawId,
    memberId,
    data,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
    memberId: string;
    data: UpdateMembership;
  }): Effect.Effect<
    PublicClawMembership,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        clawId,
        memberId: userId,
      });

      const existing = yield* this.getMembership({
        memberId,
        organizationId,
        clawId,
      });

      return yield* client.withTransaction(
        Effect.gen(function* () {
          const [membership] = yield* client
            .update(clawMemberships)
            .set({ role: data.role })
            .where(
              and(
                eq(clawMemberships.clawId, clawId),
                eq(clawMemberships.memberId, memberId),
              ),
            )
            .returning(publicFields)
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to update claw membership",
                    cause: e,
                  }),
              ),
            );

          yield* client
            .insert(clawMembershipAudit)
            .values({
              clawId,
              actorId: userId,
              targetId: memberId,
              action: "CHANGE",
              previousRole: existing.role,
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

          return membership as PublicClawMembership;
        }),
      );
    });
  }

  /**
   * Removes a member from a claw.
   */
  delete({
    userId,
    organizationId,
    clawId,
    memberId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
    memberId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        clawId,
        memberId: userId,
      });

      const existing = yield* this.getMembership({
        memberId,
        organizationId,
        clawId,
      });

      yield* client.withTransaction(
        Effect.gen(function* () {
          yield* client
            .delete(clawMemberships)
            .where(
              and(
                eq(clawMemberships.clawId, clawId),
                eq(clawMemberships.memberId, memberId),
              ),
            )
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to delete claw membership",
                    cause: e,
                  }),
              ),
            );

          yield* client
            .insert(clawMembershipAudit)
            .values({
              clawId,
              actorId: userId,
              targetId: memberId,
              action: "REVOKE",
              previousRole: existing.role,
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

  /**
   * Retrieves all memberships for a claw with user information.
   */
  findAllWithUserInfo({
    userId,
    organizationId,
    clawId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
  }): Effect.Effect<
    Array<{
      memberId: string;
      email: string;
      name: string | null;
      role: ClawRole;
      createdAt: Date | null;
    }>,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        clawId,
        memberId: userId,
      });

      return yield* client
        .select({
          memberId: clawMemberships.memberId,
          email: users.email,
          name: users.name,
          role: clawMemberships.role,
          createdAt: clawMemberships.createdAt,
        })
        .from(clawMemberships)
        .innerJoin(users, eq(clawMemberships.memberId, users.id))
        .where(and(eq(clawMemberships.clawId, clawId), isNull(users.deletedAt)))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all claw memberships with user info",
                cause: e,
              }),
          ),
        );
    });
  }
}
