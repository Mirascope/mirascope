/**
 * @fileoverview Cloudflare Cron Trigger for expiring stale credit reservations.
 *
 * Periodically marks active reservations as expired when they exceed their
 * expiration time. This is a safety net for orphaned reservations from
 * server crashes or bugs.
 *
 * ## Responsibilities
 *
 * 1. **Expire Stale Reservations**: Finds active reservations where expiresAt < NOW()
 *    and marks them as 'expired'
 *
 * ## Trigger Configuration
 *
 * Configure in wrangler.jsonc with a cron expression like `*\/5 * * * *` (every 5 min).
 */

import { Effect, Layer } from "effect";
import { DrizzleORM } from "@/db/client";
import { creditReservations } from "@/db/schema";
import { and, eq, lt } from "drizzle-orm";
import { SettingsService, getSettingsFromEnvironment } from "@/settings";
import { DatabaseError } from "@/errors";
import { type ScheduledEvent, type CronTriggerEnv } from "@/workers/config";

export type { CronTriggerEnv };

// =============================================================================
// Expiry Program
// =============================================================================

/**
 * Expires stale active reservations.
 *
 * Finds all active reservations where expiresAt < NOW() and marks them as 'expired'.
 * This is the core Effect program, exported for testing.
 */
export const expireStaleReservations = Effect.gen(function* () {
  const client = yield* DrizzleORM;
  const now = new Date();

  // Find and expire stale active reservations
  const expiredRows = yield* client
    .update(creditReservations)
    .set({ status: "expired" })
    .where(
      and(
        eq(creditReservations.status, "active"),
        lt(creditReservations.expiresAt, now),
      ),
    )
    .returning({ id: creditReservations.id })
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to expire stale reservations",
            cause: error,
          }),
      ),
    );

  if (expiredRows.length > 0) {
    console.log(
      `[reservationExpiryCron] Expired ${expiredRows.length} stale reservations`,
    );
  }
});

// =============================================================================
// Cron Handler
// =============================================================================

export default {
  /**
   * Scheduled event handler for expiring stale reservations.
   *
   * Finds all active reservations that have exceeded their expiration time
   * and marks them as 'expired'. This frees up the reserved funds and allows
   * the billing reconciliation cron to handle them appropriately.
   *
   * @param _event - Cloudflare scheduled event (unused, but required by interface)
   * @param env - Cloudflare Workers environment bindings
   */
  async scheduled(_event: ScheduledEvent, env: CronTriggerEnv): Promise<void> {
    // Database connection string from Hyperdrive or direct URL
    const databaseUrl = env.HYPERDRIVE?.connectionString ?? env.DATABASE_URL;
    if (!databaseUrl) {
      console.error(
        "[reservationExpiryCron] No database connection available (HYPERDRIVE or DATABASE_URL required)",
      );
      return;
    }

    // Build layers
    const settingsLayer = Layer.succeed(
      SettingsService,
      getSettingsFromEnvironment(env),
    );
    const drizzleLayer = DrizzleORM.layer({ connectionString: databaseUrl });

    // Run the program
    await Effect.runPromise(
      expireStaleReservations.pipe(
        Effect.provide(drizzleLayer),
        Effect.provide(settingsLayer),
        Effect.catchAll((error) => {
          console.error("[reservationExpiryCron] Cron trigger error:", error);
          return Effect.void;
        }),
      ),
    );
  },
};
