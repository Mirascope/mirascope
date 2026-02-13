/**
 * @fileoverview Cloudflare Cron Trigger for billing reconciliation.
 *
 * Periodically detects and corrects billing state inconsistencies between
 * router requests and credit reservations. This ensures that all successful
 * requests are eventually charged and all failed requests have their
 * reservations released.
 *
 * ## Responsibilities
 *
 * 1. **Reconcile Successful Requests**: Retry charging for success + active/expired
 * 2. **Reconcile Failed Requests**: Release reservations for failure + active/expired
 * 3. **Handle Pending + Expired**: Mark as failure and release
 * 4. **Detect Stale Records**: Log warning for records older than 24 hours
 * 5. **Detect Invalid State**: Log warning for pending + released (should never happen)
 *
 * ## Trigger Configuration
 *
 * Configure in wrangler.jsonc with a cron expression like `*\/5 * * * *` (every 5 min).
 */

import { and, eq, gt, inArray, isNull, lte, or } from "drizzle-orm";
import { Effect, Layer } from "effect";

import { DrizzleORM } from "@/db/client";
import {
  creditReservations,
  organizationMemberships,
  organizations,
  routerRequests,
} from "@/db/schema";
import { DatabaseError } from "@/errors";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import { Settings } from "@/settings";
import {
  type ScheduledEvent,
  type BillingCronTriggerEnv,
} from "@/workers/config";

export type { BillingCronTriggerEnv as CronTriggerEnv };

// =============================================================================
// Constants
// =============================================================================

/**
 * Time threshold for DLQ (Dead Letter Queue) warning in milliseconds.
 * Records older than this are logged as warnings but not processed.
 */
const DLQ_THRESHOLD_MS = 24 * 60 * 60 * 1000; // 24 hours

/**
 * Maximum number of rows to process per cron invocation.
 * Prevents overwhelming the system.
 */
const BATCH_LIMIT = 100;

// =============================================================================
// Reconciliation Functions
// =============================================================================

/**
 * Reconciles successful requests that failed to settle.
 *
 * Finds reservations where:
 * - Reservation status is 'active' or 'expired'
 * - Router request status is 'success'
 * - Router request has a cost
 * - Record is within DLQ threshold (24 hours)
 *
 * For each, attempts to settle (charge + release).
 */
export const reconcileSuccessfulRequests = Effect.gen(function* () {
  const client = yield* DrizzleORM;
  const payments = yield* Payments;
  const now = new Date();
  const dlqThreshold = new Date(now.getTime() - DLQ_THRESHOLD_MS);

  // Find success + active/expired reservations within DLQ threshold
  const records = yield* client
    .select({
      reservationId: creditReservations.id,
      stripeCustomerId: creditReservations.stripeCustomerId,
      costCenticents: routerRequests.costCenticents,
    })
    .from(creditReservations)
    .innerJoin(
      routerRequests,
      eq(creditReservations.routerRequestId, routerRequests.id),
    )
    .where(
      and(
        inArray(creditReservations.status, ["active", "expired"]),
        eq(routerRequests.status, "success"),
        gt(creditReservations.createdAt, dlqThreshold),
      ),
    )
    .limit(BATCH_LIMIT)
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to query successful requests for reconciliation",
            cause: error,
          }),
      ),
    );

  if (records.length > 0) {
    console.log(
      `[billingReconciliationCron] Found ${records.length} successful requests to reconcile`,
    );
  }

  // Process each record
  for (const record of records) {
    if (record.costCenticents === null) {
      continue;
    }

    yield* payments.products.router
      .settleFunds(record.reservationId, record.costCenticents)
      .pipe(
        Effect.catchAll((error) => {
          console.error(
            `[billingReconciliationCron] Failed to settle reservation ${record.reservationId}:`,
            error,
          );
          return Effect.succeed(undefined);
        }),
      );
  }
});

/**
 * Reconciles failed requests that failed to release.
 *
 * Finds reservations where:
 * - Reservation status is 'active' or 'expired'
 * - Router request status is 'failure'
 *
 * For each, releases the reservation without charging.
 */
export const reconcileFailedRequests = Effect.gen(function* () {
  const client = yield* DrizzleORM;
  const now = new Date();

  // Find failure + active/expired reservations and release them
  const result = yield* client
    .update(creditReservations)
    .set({
      status: "released",
      releasedAt: now,
    })
    .where(
      and(
        inArray(creditReservations.status, ["active", "expired"]),
        inArray(
          creditReservations.routerRequestId,
          client
            .select({ id: routerRequests.id })
            .from(routerRequests)
            .where(eq(routerRequests.status, "failure")),
        ),
      ),
    )
    .returning({ id: creditReservations.id })
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to release reservations for failed requests",
            cause: error,
          }),
      ),
    );

  if (result.length > 0) {
    console.log(
      `[billingReconciliationCron] Released ${result.length} reservations for failed requests`,
    );
  }
});

/**
 * Reconciles pending + expired states.
 *
 * Finds reservations where:
 * - Reservation status is 'expired'
 * - Router request status is 'pending'
 *
 * This indicates the request processing failed before completion.
 * Updates both to failure/released state.
 */
export const reconcilePendingExpiredRequests = Effect.gen(function* () {
  const client = yield* DrizzleORM;
  const now = new Date();

  // Find pending + expired records
  const records = yield* client
    .select({
      reservationId: creditReservations.id,
      routerRequestId: routerRequests.id,
    })
    .from(creditReservations)
    .innerJoin(
      routerRequests,
      eq(creditReservations.routerRequestId, routerRequests.id),
    )
    .where(
      and(
        eq(creditReservations.status, "expired"),
        eq(routerRequests.status, "pending"),
      ),
    )
    .limit(BATCH_LIMIT)
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to query pending + expired records",
            cause: error,
          }),
      ),
    );

  if (records.length === 0) {
    return;
  }

  console.log(
    `[billingReconciliationCron] Found ${records.length} pending + expired records to reconcile`,
  );

  // Update router requests to failure
  yield* client
    .update(routerRequests)
    .set({
      status: "failure",
      errorMessage: "Request timed out (reservation expired)",
      completedAt: now,
    })
    .where(
      inArray(
        routerRequests.id,
        records.map((r) => r.routerRequestId),
      ),
    )
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to update router requests to failure",
            cause: error,
          }),
      ),
    );

  // Release the reservations
  yield* client
    .update(creditReservations)
    .set({
      status: "released",
      releasedAt: now,
    })
    .where(
      inArray(
        creditReservations.id,
        records.map((r) => r.reservationId),
      ),
    )
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to release expired reservations",
            cause: error,
          }),
      ),
    );
});

/**
 * Detects stale records that have been unreconciled for too long.
 *
 * Logs a warning for records older than DLQ_THRESHOLD_MS (24 hours).
 * These require manual intervention.
 */
export const detectStaleReconciliation = Effect.gen(function* () {
  const client = yield* DrizzleORM;
  const dlqThreshold = new Date(Date.now() - DLQ_THRESHOLD_MS);

  // Find stale records
  const staleRecords = yield* client
    .select({
      reservationId: creditReservations.id,
      requestStatus: routerRequests.status,
      createdAt: creditReservations.createdAt,
    })
    .from(creditReservations)
    .innerJoin(
      routerRequests,
      eq(creditReservations.routerRequestId, routerRequests.id),
    )
    .where(
      and(
        inArray(creditReservations.status, ["active", "expired"]),
        lte(creditReservations.createdAt, dlqThreshold),
      ),
    )
    .limit(BATCH_LIMIT)
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to query stale records",
            cause: error,
          }),
      ),
    );

  if (staleRecords.length > 0) {
    console.warn(
      `[billingReconciliationCron] WARNING: Found ${staleRecords.length} stale records older than 24 hours. Manual intervention may be required.`,
      staleRecords.map((r) => ({
        reservationId: r.reservationId,
        requestStatus: r.requestStatus,
        createdAt: r.createdAt,
      })),
    );
  }
});

/**
 * Detects invalid state: pending + released.
 *
 * This state should never occur in normal operation.
 * Logs a critical warning if found.
 */
export const detectInvalidState = Effect.gen(function* () {
  const client = yield* DrizzleORM;

  // Find pending + released records (invalid state)
  const invalidRecords = yield* client
    .select({
      reservationId: creditReservations.id,
      routerRequestId: routerRequests.id,
    })
    .from(creditReservations)
    .innerJoin(
      routerRequests,
      eq(creditReservations.routerRequestId, routerRequests.id),
    )
    .where(
      and(
        eq(creditReservations.status, "released"),
        eq(routerRequests.status, "pending"),
      ),
    )
    .limit(BATCH_LIMIT)
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to query invalid state records",
            cause: error,
          }),
      ),
    );

  if (invalidRecords.length > 0) {
    console.error(
      `[billingReconciliationCron] CRITICAL: Found ${invalidRecords.length} records in invalid state (pending + released). This should never happen!`,
      invalidRecords,
    );
  }
});

// =============================================================================
// Auto-Reload
// =============================================================================

/**
 * Cooldown period between auto-reloads for the same organization (15 minutes).
 * Prevents duplicate reloads during rapid balance changes.
 */
const AUTO_RELOAD_COOLDOWN_MS = 15 * 60 * 1000;

/**
 * Maximum number of organizations to process for auto-reload per cron invocation.
 */
const AUTO_RELOAD_BATCH_LIMIT = 50;

/**
 * Processes auto-reload for eligible organizations.
 *
 * Finds organizations with auto-reload enabled that haven't been reloaded recently,
 * checks their balance against the configured threshold, and triggers a credit
 * purchase using their saved payment method if the balance is below threshold.
 */
export const processAutoReloads = Effect.gen(function* () {
  const client = yield* DrizzleORM;
  const payments = yield* Payments;
  const now = new Date();
  const cooldownThreshold = new Date(now.getTime() - AUTO_RELOAD_COOLDOWN_MS);

  // Find eligible organizations
  const eligibleOrgs = yield* client
    .select({
      id: organizations.id,
      stripeCustomerId: organizations.stripeCustomerId,
      thresholdCenticents: organizations.autoReloadThresholdCenticents,
      amountCenticents: organizations.autoReloadAmountCenticents,
    })
    .from(organizations)
    .where(
      and(
        eq(organizations.autoReloadEnabled, true),
        or(
          isNull(organizations.lastAutoReloadAt),
          lte(organizations.lastAutoReloadAt, cooldownThreshold),
        ),
      ),
    )
    .limit(AUTO_RELOAD_BATCH_LIMIT)
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to query eligible organizations for auto-reload",
            cause: error,
          }),
      ),
    );

  if (eligibleOrgs.length > 0) {
    console.log(
      `[billingReconciliationCron] Processing auto-reload for ${eligibleOrgs.length} organizations`,
    );
  }

  for (const org of eligibleOrgs) {
    yield* Effect.gen(function* () {
      // Check current balance
      const balanceInfo = yield* payments.products.router.getBalanceInfo(
        org.stripeCustomerId,
      );

      if (balanceInfo.availableBalance >= org.thresholdCenticents) {
        return;
      }

      // Get saved payment method
      const paymentMethod = yield* payments.paymentMethods.getDefault(
        org.stripeCustomerId,
      );

      if (!paymentMethod) {
        console.warn(
          `[billingReconciliationCron] Organization ${org.id} has auto-reload enabled but no saved payment method`,
        );
        return;
      }

      // Create payment intent for auto-reload
      const amountInDollars = Number(org.amountCenticents) / 10000;
      const result =
        yield* payments.paymentIntents.createRouterCreditsPurchaseIntent({
          stripeCustomerId: org.stripeCustomerId,
          amountInDollars,
          paymentMethodId: paymentMethod.id,
          metadata: {
            organizationId: org.id,
            autoReload: "true",
          },
        });

      if (result.status === "requires_action") {
        console.warn(
          `[billingReconciliationCron] Auto-reload for organization ${org.id} requires 3DS verification, skipping`,
        );
        return;
      }

      if (result.status === "succeeded") {
        // Update last auto-reload timestamp
        yield* client
          .update(organizations)
          .set({ lastAutoReloadAt: now })
          .where(eq(organizations.id, org.id))
          .pipe(
            Effect.mapError(
              (error) =>
                new DatabaseError({
                  message: "Failed to update last auto-reload timestamp",
                  cause: error,
                }),
            ),
          );

        console.log(
          `[billingReconciliationCron] Auto-reload succeeded for organization ${org.id}: $${amountInDollars}`,
        );
      }
    }).pipe(
      Effect.catchAll((error) => {
        console.error(
          `[billingReconciliationCron] Auto-reload failed for organization ${org.id}:`,
          error,
        );
        return Effect.succeed(undefined);
      }),
    );
  }
});

// =============================================================================
// Orphaned Organization Cleanup
// =============================================================================

/**
 * Grace period before cleaning up orphaned organizations (1 hour).
 * Gives users time to complete payment if the upgrade dialog was interrupted.
 */
const ORPHAN_GRACE_PERIOD_MS = 60 * 60 * 1000;

/**
 * Cleans up orphaned organizations from failed paid org creation.
 *
 * When a user creates a paid org but payment fails, the saga pattern in the
 * handler rolls back immediately. However, edge cases (crashes, timeouts) can
 * leave orphaned free-plan orgs that were intended to be paid.
 *
 * This detects users who own multiple free-plan orgs (which should never happen
 * under normal operation) and removes the newest ones, keeping only the oldest
 * free org per user.
 */
export const cleanupOrphanedOrganizations = Effect.gen(function* () {
  const client = yield* DrizzleORM;
  const payments = yield* Payments;
  const graceThreshold = new Date(Date.now() - ORPHAN_GRACE_PERIOD_MS);

  // Find users who own multiple organizations
  const ownerships = yield* client
    .select({
      userId: organizationMemberships.memberId,
      organizationId: organizations.id,
      stripeCustomerId: organizations.stripeCustomerId,
      createdAt: organizations.createdAt,
    })
    .from(organizationMemberships)
    .innerJoin(
      organizations,
      eq(organizationMemberships.organizationId, organizations.id),
    )
    .where(
      and(
        eq(organizationMemberships.role, "OWNER"),
        lte(organizations.createdAt, graceThreshold),
      ),
    )
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message:
              "Failed to query organization ownerships for orphan cleanup",
            cause: error,
          }),
      ),
    );

  // Group by user
  const byUser = new Map<
    string,
    {
      organizationId: string;
      stripeCustomerId: string;
      createdAt: Date | null;
    }[]
  >();
  for (const row of ownerships) {
    const list = byUser.get(row.userId) ?? [];
    list.push({
      organizationId: row.organizationId,
      stripeCustomerId: row.stripeCustomerId,
      createdAt: row.createdAt,
    });
    byUser.set(row.userId, list);
  }

  // For users with multiple orgs, check for multiple free-plan orgs
  for (const [userId, orgs] of byUser) {
    if (orgs.length < 2) continue;

    const freeOrgs: typeof orgs = [];
    for (const org of orgs) {
      const subscription = yield* payments.customers.subscriptions
        .get(org.stripeCustomerId)
        .pipe(
          Effect.map((s) => s.currentPlan),
          Effect.catchAll(() => Effect.succeed("free" as const)),
        );
      if (subscription === "free") {
        freeOrgs.push(org);
      }
    }

    if (freeOrgs.length <= 1) continue;

    // Keep the oldest free org, delete the rest
    freeOrgs.sort(
      (a, b) => (a.createdAt?.getTime() ?? 0) - (b.createdAt?.getTime() ?? 0),
    );
    const toDelete = freeOrgs.slice(1);

    for (const org of toDelete) {
      yield* Effect.gen(function* () {
        // Cancel subscriptions
        yield* payments.customers.subscriptions
          .cancel(org.stripeCustomerId)
          .pipe(Effect.catchAll(() => Effect.void));

        // Delete org from DB (cascade handles memberships/audit)
        yield* client
          .delete(organizations)
          .where(eq(organizations.id, org.organizationId))
          .pipe(
            Effect.mapError(
              (error) =>
                new DatabaseError({
                  message: `Failed to delete orphaned organization ${org.organizationId}`,
                  cause: error,
                }),
            ),
          );

        console.log(
          `[billingReconciliationCron] Cleaned up orphaned organization ${org.organizationId} for user ${userId}`,
        );
      }).pipe(
        Effect.catchAll((error) => {
          console.error(
            `[billingReconciliationCron] Failed to clean up orphaned org ${org.organizationId}:`,
            error,
          );
          return Effect.succeed(undefined);
        }),
      );
    }
  }
});

// =============================================================================
// Main Reconciliation Program
// =============================================================================

/**
 * Main billing reconciliation program.
 *
 * Runs all reconciliation steps in sequence:
 * 1. Reconcile successful requests (charge + release)
 * 2. Reconcile failed requests (release only)
 * 3. Handle pending + expired (mark failure + release)
 * 4. Detect stale records (log warning)
 * 5. Detect invalid state (log critical warning)
 * 6. Process auto-reloads for eligible organizations
 * 7. Clean up orphaned organizations from failed paid creation
 */
export const reconcileBilling = Effect.gen(function* () {
  // Step 1: Reconcile successful requests (charge + release)
  yield* reconcileSuccessfulRequests;

  // Step 2: Reconcile failed requests (release only)
  yield* reconcileFailedRequests;

  // Step 3: Handle pending + expired (mark failure + release)
  yield* reconcilePendingExpiredRequests;

  // Step 4: Detect stale records (log warning)
  yield* detectStaleReconciliation;

  // Step 5: Detect invalid state (log critical warning)
  yield* detectInvalidState;

  // Step 6: Process auto-reloads for eligible organizations
  yield* processAutoReloads;

  // Step 7: Clean up orphaned organizations from failed paid creation
  yield* cleanupOrphanedOrganizations;
});

// =============================================================================
// Cron Handler
// =============================================================================

export default {
  /**
   * Scheduled event handler for billing reconciliation.
   *
   * Runs all reconciliation steps in sequence:
   * 1. Reconcile successful requests (charge + release)
   * 2. Reconcile failed requests (release only)
   * 3. Handle pending + expired (mark failure + release)
   * 4. Detect stale records (log warning)
   * 5. Detect invalid state (log critical warning)
   * 6. Process auto-reloads for eligible organizations
   *
   * @param _event - Cloudflare scheduled event (unused, but required by interface)
   * @param env - Cloudflare Workers environment bindings
   */
  async scheduled(
    _event: ScheduledEvent,
    env: BillingCronTriggerEnv,
  ): Promise<void> {
    // Database connection string from Hyperdrive
    const databaseUrl = env.HYPERDRIVE?.connectionString;
    if (!databaseUrl) {
      console.error(
        "[billingReconciliationCron] HYPERDRIVE binding not configured",
      );
      return;
    }

    // Build layers using Settings for validated configuration
    const program = Effect.gen(function* () {
      const settings = yield* Settings;

      const drizzleLayer = DrizzleORM.layer({ connectionString: databaseUrl });
      const stripeLayer = Stripe.layer(settings.stripe);
      const paymentsLayer = Payments.Default.pipe(
        Layer.provide(stripeLayer),
        Layer.provide(drizzleLayer),
      );

      yield* reconcileBilling.pipe(
        Effect.provide(paymentsLayer),
        Effect.provide(drizzleLayer),
      );
    });

    // Run with Settings layer from environment
    await Effect.runPromise(
      program.pipe(
        Effect.provide(Settings.LiveFromEnvironment(env)),
        Effect.catchAll((error) => {
          console.error(
            "[billingReconciliationCron] Cron trigger error:",
            error,
          );
          return Effect.void;
        }),
      ),
    );
  },
};
