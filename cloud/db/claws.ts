/**
 * @fileoverview Effect-native Claws service.
 *
 * Provides authenticated CRUD operations for claws with role-based access
 * control. Claws belong to organizations and have their own membership
 * system for fine-grained access control.
 *
 * ## Architecture
 *
 * ```
 * Claws (authenticated)
 *   └── memberships: ClawMemberships
 *         └── CRUD on `claw_memberships` table (authenticated)
 * ```
 *
 * ## Claw Roles
 *
 * Claws support four roles:
 * - `ADMIN` - Full claw management (create, read, update, delete)
 * - `DEVELOPER` - Read-only access to claw info
 * - `VIEWER` - Read-only access to claw info
 * - `ANNOTATOR` - Read-only access to claw info
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all claws
 * within their organization, even without explicit claw membership.
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Create a claw (creator becomes claw ADMIN)
 * const claw = yield* db.organizations.claws.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   data: { slug: "my-claw", displayName: "My Claw" },
 * });
 *
 * // List accessible claws
 * const claws = yield* db.organizations.claws.findAll({
 *   userId: "user-123",
 *   organizationId: "org-456",
 * });
 * ```
 */

import { and, eq, sql } from "drizzle-orm";
import { Effect } from "effect";

import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { ClawMemberships } from "@/db/claw-memberships";
import { DrizzleORM } from "@/db/client";
import { OrganizationMemberships } from "@/db/organization-memberships";
import {
  claws,
  clawMemberships,
  type NewClaw,
  type PublicClaw,
  type ClawRole,
} from "@/db/schema";
import { isUniqueConstraintError } from "@/db/utils";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
  StripeError,
} from "@/errors";
import { Payments } from "@/payments";

/**
 * Public fields to select from the claws table.
 */
const publicFields = {
  id: claws.id,
  slug: claws.slug,
  displayName: claws.displayName,
  description: claws.description,
  organizationId: claws.organizationId,
  createdByUserId: claws.createdByUserId,
  status: claws.status,
  instanceType: claws.instanceType,
  lastDeployedAt: claws.lastDeployedAt,
  lastError: claws.lastError,
  secretsEncrypted: claws.secretsEncrypted,
  secretsKeyId: claws.secretsKeyId,
  bucketName: claws.bucketName,
  weeklySpendingGuardrailCenticents: claws.weeklySpendingGuardrailCenticents,
  weeklyWindowStart: claws.weeklyWindowStart,
  weeklyUsageCenticents: claws.weeklyUsageCenticents,
  burstWindowStart: claws.burstWindowStart,
  burstUsageCenticents: claws.burstUsageCenticents,
  createdAt: claws.createdAt,
  updatedAt: claws.updatedAt,
};

/**
 * Insert type for creating claws.
 */
type CreateData = Pick<NewClaw, "slug" | "displayName" | "description">;

/**
 * Update type for claws.
 */
type UpdateData = Partial<
  Pick<
    NewClaw,
    "displayName" | "description" | "weeklySpendingGuardrailCenticents"
  >
>;

/**
 * Effect-native Claws service.
 *
 * Provides CRUD operations with role-based access control for claws.
 * Organization OWNER/ADMIN roles have implicit ADMIN access to all claws.
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓*    | ✗         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✓      | ✓        |
 * | update   | ✓     | ✗         | ✗      | ✗         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 *
 * *Create is a special case: requires org OWNER/ADMIN, creator becomes claw ADMIN.
 *
 * ## Security Model
 *
 * - Org OWNER/ADMIN have implicit claw ADMIN access
 * - Non-members cannot see that a claw exists (returns NotFoundError)
 * - Creator is automatically added as claw ADMIN
 */
export class Claws extends BaseAuthenticatedEffectService<
  PublicClaw,
  "organizations/:organizationId/claws/:clawId",
  CreateData,
  UpdateData,
  ClawRole
> {
  /**
   * Service for managing claw memberships.
   */
  public readonly memberships: ClawMemberships;

  private readonly organizationMemberships: OrganizationMemberships;

  constructor(
    organizationMemberships: OrganizationMemberships,
    clawMemberships: ClawMemberships,
  ) {
    super();
    this.organizationMemberships = organizationMemberships;
    this.memberships = clawMemberships;
  }

  // ---------------------------------------------------------------------------
  // Claw Limit Enforcement
  // ---------------------------------------------------------------------------

  /**
   * Checks if creating a new claw would exceed the organization's plan limits.
   */
  private checkClawLimit({
    organizationId,
  }: {
    organizationId: string;
  }): Effect.Effect<
    void,
    PlanLimitExceededError | DatabaseError | NotFoundError | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const payments = yield* Payments;

      const planTier =
        yield* payments.customers.subscriptions.getPlan(organizationId);
      const limits =
        yield* payments.customers.subscriptions.getPlanLimits(planTier);

      const [clawCount] = yield* client
        .select({ count: sql<number>`count(*)::int` })
        .from(claws)
        .where(eq(claws.organizationId, organizationId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to count claws",
                cause: e,
              }),
          ),
        );

      if (clawCount.count >= limits.claws) {
        return yield* Effect.fail(
          new PlanLimitExceededError({
            message: `Cannot create claw: ${planTier} plan limit is ${limits.claws} claw(s)`,
            resource: "claws",
            limitType: "claws",
            currentUsage: clawCount.count,
            limit: limits.claws,
            planTier,
          }),
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Base Implementation
  // ---------------------------------------------------------------------------

  protected getResourceName(): string {
    return "claw";
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
   * Determines the user's effective role for a claw.
   *
   * Delegates to `ClawMemberships.getRole` which handles:
   * - Org OWNER → treated as claw ADMIN
   * - Org ADMIN → treated as claw ADMIN
   * - Explicit claw membership role
   * - No access → NotFoundError (hides claw existence)
   */
  getRole({
    userId,
    organizationId,
    clawId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
  }): Effect.Effect<
    ClawRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const { role } = yield* this.memberships.findById({
        userId,
        organizationId,
        clawId,
        memberId: userId,
      });
      return role;
    });
  }

  // ---------------------------------------------------------------------------
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Creates a new claw within an organization.
   *
   * Requires org OWNER or ADMIN role. The creating user is automatically
   * added as an explicit claw member with role ADMIN.
   *
   * Uses the plan's default instanceType for the new claw.
   */
  create({
    userId,
    organizationId,
    data,
  }: {
    userId: string;
    organizationId: string;
    data: CreateData;
  }): Effect.Effect<
    PublicClaw,
    | NotFoundError
    | PermissionDeniedError
    | AlreadyExistsError
    | DatabaseError
    | PlanLimitExceededError
    | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const payments = yield* Payments;

      // Must be org OWNER/ADMIN to create claws.
      const { role: orgRole } = yield* this.organizationMemberships.findById({
        userId,
        organizationId,
        memberId: userId,
      });

      if (orgRole !== "OWNER" && orgRole !== "ADMIN") {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message:
              "You do not have permission to create claws in this organization",
            resource: this.getResourceName(),
          }),
        );
      }

      // Check claw limit before creating
      yield* this.checkClawLimit({ organizationId });

      // Get plan defaults for instanceType
      const planTier =
        yield* payments.customers.subscriptions.getPlan(organizationId);
      const limits =
        yield* payments.customers.subscriptions.getPlanLimits(planTier);

      // Use transaction to ensure claw, membership, and audit are created atomically
      return yield* client.withTransaction(
        Effect.gen(this, function* () {
          const [claw] = yield* client
            .insert(claws)
            .values({
              slug: data.slug,
              displayName: data.displayName,
              description: data.description,
              organizationId,
              createdByUserId: userId,
              instanceType: limits.clawInstanceType,
            })
            .returning(publicFields)
            .pipe(
              Effect.mapError((e): AlreadyExistsError | DatabaseError =>
                isUniqueConstraintError(e.cause)
                  ? new AlreadyExistsError({
                      message:
                        "A claw with this slug already exists in this organization",
                      resource: "claw",
                    })
                  : new DatabaseError({
                      message: "Failed to create claw",
                      cause: e,
                    }),
              ),
            );

          // Add creator as explicit claw ADMIN with audit log
          yield* this.memberships.create({
            userId,
            organizationId,
            clawId: claw.id,
            data: { memberId: userId, role: "ADMIN" },
          });

          return claw as PublicClaw;
        }),
      );
    });
  }

  /**
   * Retrieves all claws the user can access within an organization.
   *
   * - Org OWNER/ADMIN see all claws in the organization (implicit ADMIN)
   * - Others only see claws where they have explicit membership
   */
  findAll({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    PublicClaw[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Get org role (also verifies org membership / hides org existence)
      const { role: orgRole } = yield* this.organizationMemberships.findById({
        userId,
        organizationId,
        memberId: userId,
      });

      // Org OWNER/ADMIN see all claws
      const isOrgPrivileged = orgRole === "OWNER" || orgRole === "ADMIN";

      if (isOrgPrivileged) {
        const results: PublicClaw[] = yield* client
          .select(publicFields)
          .from(claws)
          .where(eq(claws.organizationId, organizationId))
          .pipe(
            Effect.mapError(
              (e) =>
                new DatabaseError({
                  message: "Failed to find all claws",
                  cause: e,
                }),
            ),
          );

        return results;
      }

      // Others only see claws they're members of
      const results: PublicClaw[] = yield* client
        .select(publicFields)
        .from(claws)
        .innerJoin(clawMemberships, eq(claws.id, clawMemberships.clawId))
        .where(
          and(
            eq(claws.organizationId, organizationId),
            eq(clawMemberships.memberId, userId),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all claws",
                cause: e,
              }),
          ),
        );

      return results;
    });
  }

  /**
   * Retrieves a claw by ID.
   */
  findById({
    userId,
    organizationId,
    clawId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
  }): Effect.Effect<
    PublicClaw,
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
      });

      const [claw] = yield* client
        .select(publicFields)
        .from(claws)
        .where(
          and(eq(claws.id, clawId), eq(claws.organizationId, organizationId)),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find claw",
                cause: e,
              }),
          ),
        );

      if (!claw) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Claw with clawId ${clawId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return claw;
    });
  }

  /**
   * Updates a claw.
   */
  update({
    userId,
    organizationId,
    clawId,
    data,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
    data: UpdateData;
  }): Effect.Effect<
    PublicClaw,
    NotFoundError | PermissionDeniedError | AlreadyExistsError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        clawId,
      });

      const [updated] = yield* client
        .update(claws)
        .set({ ...data, updatedAt: new Date() })
        .where(
          and(eq(claws.id, clawId), eq(claws.organizationId, organizationId)),
        )
        .returning(publicFields)
        .pipe(
          Effect.mapError((e): AlreadyExistsError | DatabaseError =>
            isUniqueConstraintError(e.cause)
              ? new AlreadyExistsError({
                  message:
                    "A claw with this slug already exists in this organization",
                  resource: "claw",
                })
              : new DatabaseError({
                  message: "Failed to update claw",
                  cause: e,
                }),
          ),
        );

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Claw with clawId ${clawId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return updated;
    });
  }

  /**
   * Deletes a claw.
   *
   * All claw memberships are automatically deleted via CASCADE.
   */
  delete({
    userId,
    organizationId,
    clawId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
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
      });

      const [deleted] = yield* client
        .delete(claws)
        .where(
          and(eq(claws.id, clawId), eq(claws.organizationId, organizationId)),
        )
        .returning({ id: claws.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete claw",
                cause: e,
              }),
          ),
        );

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Claw with clawId ${clawId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }
    });
  }
}
