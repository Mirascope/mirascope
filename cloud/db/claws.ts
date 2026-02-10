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

import { and, eq, isNull, sql } from "drizzle-orm";
import { Effect } from "effect";

import { decryptSecrets, encryptSecrets } from "@/claws/crypto";
import { generateClawApiKey, hashApiKey, getKeyPrefix } from "@/db/api-keys";
import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { ClawMemberships } from "@/db/claw-memberships";
import { DrizzleORM } from "@/db/client";
import { OrganizationMemberships } from "@/db/organization-memberships";
import {
  apiKeys,
  claws,
  clawMemberships,
  environments,
  organizationMemberships,
  projects,
  projectMemberships,
  users,
  type NewClaw,
  type PublicClaw,
  type ClawRole,
} from "@/db/schema";
import { isUniqueConstraintError } from "@/db/utils";
import {
  AlreadyExistsError,
  DatabaseError,
  EncryptionError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
  StripeError,
} from "@/errors";
import { Payments } from "@/payments";
import { Settings } from "@/settings";

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
  botUserId: claws.botUserId,
  homeProjectId: claws.homeProjectId,
  homeEnvironmentId: claws.homeEnvironmentId,
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
type CreateData = Pick<
  NewClaw,
  "slug" | "displayName" | "description" | "weeklySpendingGuardrailCenticents"
> & {
  /** If provided, use this existing project instead of creating a new one. */
  homeProjectId?: string;
};

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
   * Creates a full service account (claw-user) with:
   * - A bot user account (accountType='claw')
   * - Org membership as BOT
   * - A home project and environment
   * - Project membership as DEVELOPER
   * - An API key (mck_ prefix) owned by the claw-user
   *
   * Returns the created claw.
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

      // Use transaction to ensure all resources are created atomically
      return yield* client.withTransaction(
        Effect.gen(this, function* () {
          // 1. Insert claw
          const [claw] = yield* client
            .insert(claws)
            .values({
              slug: data.slug,
              displayName: data.displayName,
              description: data.description,
              weeklySpendingGuardrailCenticents:
                data.weeklySpendingGuardrailCenticents,
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

          // 2. Create claw-user (bot account)
          const clawDisplayName = data.displayName ?? data.slug;
          const [clawUser] = yield* client
            .insert(users)
            .values({
              email: `claw-${claw.id}@bot.mirascope.io`,
              name: `${clawDisplayName} (Bot)`,
              accountType: "claw",
            })
            .returning({ id: users.id })
            .pipe(
              /* v8 ignore next 4 */
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to create claw user",
                    cause: e,
                  }),
              ),
            );

          // 3. Add claw-user to org as BOT
          yield* client
            .insert(organizationMemberships)
            .values({
              memberId: clawUser.id,
              organizationId,
              role: "BOT",
            })
            .pipe(
              /* v8 ignore next 4 */
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to add claw user to organization",
                    cause: e,
                  }),
              ),
            );

          // 4. Create home project (or use existing one if provided)
          let projectId: string;
          if (data.homeProjectId) {
            const [project] = yield* client
              .select({ id: projects.id })
              .from(projects)
              .where(
                and(
                  eq(projects.id, data.homeProjectId),
                  eq(projects.organizationId, organizationId),
                ),
              )
              .pipe(
                Effect.mapError(
                  (e) =>
                    new DatabaseError({
                      message: "Failed to validate home project",
                      cause: e,
                    }),
                ),
              );

            if (!project) {
              return yield* Effect.fail(
                new NotFoundError({
                  message:
                    "Home project not found or does not belong to this organization",
                }),
              );
            }
            projectId = data.homeProjectId;
          } else {
            const [project] = yield* client
              .insert(projects)
              .values({
                name: `${clawDisplayName} Home`,
                slug: `${data.slug}-home`,
                organizationId,
                createdByUserId: userId,
              })
              .returning({ id: projects.id })
              .pipe(
                /* v8 ignore next 4 */
                Effect.mapError(
                  (e) =>
                    new DatabaseError({
                      message: "Failed to create claw home project",
                      cause: e,
                    }),
                ),
              );
            projectId = project.id;
          }

          // 5. Add claw-user to project as DEVELOPER
          yield* client
            .insert(projectMemberships)
            .values({
              memberId: clawUser.id,
              organizationId,
              projectId,
              role: "DEVELOPER",
            })
            .pipe(
              /* v8 ignore next 4 */
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to add claw user to project",
                    cause: e,
                  }),
              ),
            );

          // 6. Create environment
          const [environment] = yield* client
            .insert(environments)
            .values({
              name: data.slug,
              slug: data.slug,
              projectId,
            })
            .returning({ id: environments.id })
            .pipe(
              /* v8 ignore next 4 */
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to create claw environment",
                    cause: e,
                  }),
              ),
            );

          // 7. Generate and insert API key
          const plaintextKey = generateClawApiKey();
          const keyHash = hashApiKey(plaintextKey);
          const keyPrefix = getKeyPrefix(plaintextKey);

          yield* client
            .insert(apiKeys)
            .values({
              name: `${data.slug}-key`,
              keyHash,
              keyPrefix,
              environmentId: environment.id,
              ownerId: clawUser.id,
            })
            .pipe(
              /* v8 ignore next 4 */
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to create claw API key",
                    cause: e,
                  }),
              ),
            );

          // 8. Update claw with botUserId, homeProjectId, homeEnvironmentId
          const [updatedClaw] = yield* client
            .update(claws)
            .set({
              botUserId: clawUser.id,
              homeProjectId: projectId,
              homeEnvironmentId: environment.id,
              updatedAt: new Date(),
            })
            .where(eq(claws.id, claw.id))
            .returning(publicFields)
            .pipe(
              /* v8 ignore next 4 */
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to update claw with home resources",
                    cause: e,
                  }),
              ),
            );

          // 9. Add creator as explicit claw ADMIN with audit log
          yield* this.memberships.create({
            userId,
            organizationId,
            clawId: claw.id,
            data: { memberId: userId, role: "ADMIN" },
          });

          return updatedClaw as PublicClaw;
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
        .returning({ id: claws.id, botUserId: claws.botUserId })
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

      // Soft-delete the bot user if one was associated
      if (deleted.botUserId) {
        yield* client
          .update(users)
          .set({
            email: `deleted-${deleted.botUserId}@deleted.local`,
            name: null,
            deletedAt: new Date(),
            updatedAt: new Date(),
          })
          .where(and(eq(users.id, deleted.botUserId), isNull(users.deletedAt)))
          .pipe(
            Effect.mapError(
              (e) =>
                new DatabaseError({
                  message: "Failed to delete bot user",
                  cause: e,
                }),
            ),
          );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Usage Tracking
  // ---------------------------------------------------------------------------

  /**
   * Records usage for a claw, updating both weekly and burst windows.
   *
   * - Resets the weekly window if it has expired (7-day rolling window)
   * - Resets the burst window if it has expired (5-hour rolling window)
   * - Adds `amountCenticents` to both windows after any resets
   * - Checks per-claw weekly spending guardrail (if set)
   *
   * This is an internal method called by the system (router/deployment),
   * not by users. No user auth is required.
   */
  recordUsage({
    clawId,
    organizationId,
    amountCenticents,
  }: {
    clawId: string;
    organizationId: string;
    amountCenticents: bigint;
  }): Effect.Effect<
    void,
    DatabaseError | PlanLimitExceededError | NotFoundError | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const payments = yield* Payments;

      // Get current claw usage state
      const [claw] = yield* client
        .select({
          weeklyWindowStart: claws.weeklyWindowStart,
          weeklyUsageCenticents: claws.weeklyUsageCenticents,
          burstWindowStart: claws.burstWindowStart,
          burstUsageCenticents: claws.burstUsageCenticents,
          weeklySpendingGuardrailCenticents:
            claws.weeklySpendingGuardrailCenticents,
        })
        .from(claws)
        .where(
          and(eq(claws.id, clawId), eq(claws.organizationId, organizationId)),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get claw for usage recording",
                cause: e,
              }),
          ),
        );

      if (!claw) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Claw ${clawId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      // Get plan tier for error reporting
      const planTier =
        yield* payments.customers.subscriptions.getPlan(organizationId);

      const now = new Date();

      // Weekly window: reset if expired or never started (7-day rolling window)
      const weeklyDurationMs = 7 * 24 * 60 * 60 * 1000;

      let newWeeklyStart = claw.weeklyWindowStart;
      let newWeeklyUsage = claw.weeklyUsageCenticents ?? 0n;

      if (
        !newWeeklyStart ||
        now.getTime() - newWeeklyStart.getTime() >= weeklyDurationMs
      ) {
        newWeeklyStart = now;
        newWeeklyUsage = 0n;
      }
      newWeeklyUsage += amountCenticents;

      // Burst window: reset if expired or never started (5-hour rolling window)
      const burstDurationMs = 5 * 60 * 60 * 1000;

      let newBurstStart = claw.burstWindowStart;
      let newBurstUsage = claw.burstUsageCenticents ?? 0n;

      if (
        !newBurstStart ||
        now.getTime() - newBurstStart.getTime() >= burstDurationMs
      ) {
        newBurstStart = now;
        newBurstUsage = 0n;
      }
      newBurstUsage += amountCenticents;

      // Check per-claw spending guardrail
      if (
        claw.weeklySpendingGuardrailCenticents !== null &&
        newWeeklyUsage > claw.weeklySpendingGuardrailCenticents
      ) {
        return yield* Effect.fail(
          new PlanLimitExceededError({
            message: "Claw weekly spending guardrail exceeded",
            resource: "claw",
            limitType: "weeklySpendingGuardrail",
            currentUsage: Number(newWeeklyUsage),
            limit: Number(claw.weeklySpendingGuardrailCenticents),
            planTier,
          }),
        );
      }

      // Update claw usage
      yield* client
        .update(claws)
        .set({
          weeklyWindowStart: newWeeklyStart,
          weeklyUsageCenticents: newWeeklyUsage,
          burstWindowStart: newBurstStart,
          burstUsageCenticents: newBurstUsage,
          updatedAt: now,
        })
        .where(
          and(eq(claws.id, clawId), eq(claws.organizationId, organizationId)),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to record usage",
                cause: e,
              }),
          ),
        );
    });
  }

  /**
   * Gets the org-level pool usage by summing `weeklyUsageCenticents`
   * across all claws in the organization.
   *
   * Requires org membership (any role).
   */
  getPoolUsage({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    {
      totalUsageCenticents: bigint;
      limitCenticents: number;
      percentUsed: number;
    },
    NotFoundError | PermissionDeniedError | DatabaseError | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const payments = yield* Payments;

      // Verify org membership (any role can view pool usage)
      yield* this.organizationMemberships.findById({
        userId,
        organizationId,
        memberId: userId,
      });

      const [result] = yield* client
        .select({
          total: sql<string>`COALESCE(SUM(${claws.weeklyUsageCenticents}), 0)`,
        })
        .from(claws)
        .where(eq(claws.organizationId, organizationId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get pool usage",
                cause: e,
              }),
          ),
        );

      const totalUsageCenticents = BigInt(result.total);

      const planTier =
        yield* payments.customers.subscriptions.getPlan(organizationId);
      const limits =
        yield* payments.customers.subscriptions.getPlanLimits(planTier);

      const limitCenticents = limits.includedCreditsCenticents;
      const percentUsed =
        limitCenticents > 0
          ? (Number(totalUsageCenticents) / limitCenticents) * 100
          : /* v8 ignore next */ 0;

      return { totalUsageCenticents, limitCenticents, percentUsed };
    });
  }

  /**
   * Gets org-level pool usage without user authentication.
   *
   * Internal method for use by system processes (metering queue, cron jobs).
   * Returns whether the org's total claw usage is within included credits.
   */
  getInternalPoolUsage({
    organizationId,
  }: {
    organizationId: string;
  }): Effect.Effect<
    {
      totalUsageCenticents: bigint;
      limitCenticents: number;
    },
    DatabaseError | NotFoundError | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const payments = yield* Payments;

      const [result] = yield* client
        .select({
          total: sql<string>`COALESCE(SUM(${claws.weeklyUsageCenticents}), 0)`,
        })
        .from(claws)
        .where(eq(claws.organizationId, organizationId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get internal pool usage",
                cause: e,
              }),
          ),
        );

      const totalUsageCenticents = BigInt(result.total);

      const planTier =
        yield* payments.customers.subscriptions.getPlan(organizationId);
      const limits =
        yield* payments.customers.subscriptions.getPlanLimits(planTier);

      return {
        totalUsageCenticents,
        limitCenticents: limits.includedCreditsCenticents,
      };
    });
  }

  /**
   * Gets usage details for a specific claw, including pool usage info.
   *
   * Requires read access to the claw.
   */
  getClawUsage({
    userId,
    organizationId,
    clawId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
  }): Effect.Effect<
    {
      weeklyUsageCenticents: bigint;
      weeklyWindowStart: Date | null;
      burstUsageCenticents: bigint;
      burstWindowStart: Date | null;
      weeklySpendingGuardrailCenticents: bigint | null;
      poolUsageCenticents: bigint;
      poolLimitCenticents: number;
      poolPercentUsed: number;
    },
    NotFoundError | PermissionDeniedError | DatabaseError | StripeError,
    DrizzleORM | Payments
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const payments = yield* Payments;

      // Authorize read access
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        clawId,
      });

      // Get claw usage fields
      const [claw] = yield* client
        .select({
          weeklyUsageCenticents: claws.weeklyUsageCenticents,
          weeklyWindowStart: claws.weeklyWindowStart,
          burstUsageCenticents: claws.burstUsageCenticents,
          burstWindowStart: claws.burstWindowStart,
          weeklySpendingGuardrailCenticents:
            claws.weeklySpendingGuardrailCenticents,
        })
        .from(claws)
        .where(
          and(eq(claws.id, clawId), eq(claws.organizationId, organizationId)),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get claw usage",
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

      // Get pool usage (SUM across all claws in org)
      const [poolResult] = yield* client
        .select({
          total: sql<string>`COALESCE(SUM(${claws.weeklyUsageCenticents}), 0)`,
        })
        .from(claws)
        .where(eq(claws.organizationId, organizationId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get pool usage",
                cause: e,
              }),
          ),
        );

      const planTier =
        yield* payments.customers.subscriptions.getPlan(organizationId);
      const limits =
        yield* payments.customers.subscriptions.getPlanLimits(planTier);

      const poolUsageCenticents = BigInt(poolResult.total);
      const poolLimitCenticents = limits.includedCreditsCenticents;
      const poolPercentUsed =
        poolLimitCenticents > 0
          ? (Number(poolUsageCenticents) / poolLimitCenticents) * 100
          : /* v8 ignore next */ 0;

      return {
        /* v8 ignore next 1 */
        weeklyUsageCenticents: claw.weeklyUsageCenticents ?? 0n,
        weeklyWindowStart: claw.weeklyWindowStart,
        /* v8 ignore next 1 */
        burstUsageCenticents: claw.burstUsageCenticents ?? 0n,
        burstWindowStart: claw.burstWindowStart,
        weeklySpendingGuardrailCenticents:
          claw.weeklySpendingGuardrailCenticents,
        poolUsageCenticents,
        poolLimitCenticents,
        poolPercentUsed,
      };
    });
  }

  // ---------------------------------------------------------------------------
  // Secrets
  // ---------------------------------------------------------------------------

  /**
   * Gets the decrypted secrets for a claw.
   *
   * Requires read access.
   */
  getSecrets({
    userId,
    organizationId,
    clawId,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
  }): Effect.Effect<
    Record<string, string>,
    NotFoundError | PermissionDeniedError | DatabaseError | EncryptionError,
    DrizzleORM | Settings
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
        .select({
          secretsEncrypted: claws.secretsEncrypted,
          secretsKeyId: claws.secretsKeyId,
        })
        .from(claws)
        .where(
          and(eq(claws.id, clawId), eq(claws.organizationId, organizationId)),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get claw secrets",
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

      if (!claw.secretsEncrypted || !claw.secretsKeyId) {
        return {} as Record<string, string>;
      }

      return (yield* decryptSecrets(
        claw.secretsEncrypted,
        claw.secretsKeyId,
      )) as Record<string, string>;
    });
  }

  /**
   * Updates the secrets for a claw.
   *
   * Requires update access.
   */
  updateSecrets({
    userId,
    organizationId,
    clawId,
    secrets,
  }: {
    userId: string;
    organizationId: string;
    clawId: string;
    secrets: Record<string, string>;
  }): Effect.Effect<
    Record<string, string>,
    NotFoundError | PermissionDeniedError | DatabaseError | EncryptionError,
    DrizzleORM | Settings
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        clawId,
      });

      const { ciphertext, keyId } = yield* encryptSecrets(secrets);

      const [updated] = yield* client
        .update(claws)
        .set({
          secretsEncrypted: ciphertext,
          secretsKeyId: keyId,
          updatedAt: new Date(),
        })
        .where(
          and(eq(claws.id, clawId), eq(claws.organizationId, organizationId)),
        )
        .returning({ id: claws.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to update claw secrets",
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

      return secrets;
    });
  }
}
