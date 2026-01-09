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

import { Effect, Layer } from "effect";
import { DrizzleORM } from "@/db/client";
import { creditReservations, routerRequests } from "@/db/schema";
import { and, eq, gt, inArray, lte } from "drizzle-orm";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import { SettingsService, getSettingsFromEnvironment } from "@/settings";
import { DatabaseError } from "@/errors";
import { type ScheduledEvent, type BillingCronTriggerEnv } from "./cron-config";

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
const reconcileSuccessfulRequests = Effect.gen(function* () {
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
const reconcileFailedRequests = Effect.gen(function* () {
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
const reconcilePendingExpiredRequests = Effect.gen(function* () {
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
const detectStaleReconciliation = Effect.gen(function* () {
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
const detectInvalidState = Effect.gen(function* () {
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
   *
   * @param _event - Cloudflare scheduled event (unused, but required by interface)
   * @param env - Cloudflare Workers environment bindings
   */
  async scheduled(
    _event: ScheduledEvent,
    env: BillingCronTriggerEnv,
  ): Promise<void> {
    // Database connection string from Hyperdrive or direct URL
    const databaseUrl = env.HYPERDRIVE?.connectionString ?? env.DATABASE_URL;
    if (!databaseUrl) {
      console.error(
        "[billingReconciliationCron] No database connection available (HYPERDRIVE or DATABASE_URL required)",
      );
      return;
    }

    // Stripe configuration validation
    if (
      !env.STRIPE_API_KEY ||
      !env.STRIPE_ROUTER_PRICE_ID ||
      !env.STRIPE_ROUTER_METER_ID
    ) {
      console.error(
        "[billingReconciliationCron] Missing Stripe configuration (STRIPE_API_KEY, STRIPE_ROUTER_PRICE_ID, STRIPE_ROUTER_METER_ID required)",
      );
      return;
    }

    const program = Effect.gen(function* () {
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
    });

    // Build layers
    const settingsLayer = Layer.succeed(
      SettingsService,
      getSettingsFromEnvironment(env),
    );
    const drizzleLayer = DrizzleORM.layer({ connectionString: databaseUrl });
    const stripeLayer = Stripe.layer({
      apiKey: env.STRIPE_API_KEY,
      routerPriceId: env.STRIPE_ROUTER_PRICE_ID,
      routerMeterId: env.STRIPE_ROUTER_METER_ID,
    });
    const paymentsLayer = Payments.Default.pipe(
      Layer.provide(stripeLayer),
      Layer.provide(drizzleLayer),
    );

    // Run the program
    await Effect.runPromise(
      program.pipe(
        Effect.provide(paymentsLayer),
        Effect.provide(drizzleLayer),
        Effect.provide(settingsLayer),
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
