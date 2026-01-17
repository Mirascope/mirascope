/**
 * @fileoverview Cloudflare Cron Trigger for outbox re-enqueue.
 *
 * Periodically processes pending outbox rows that failed to be
 * synced or were not processed within the timeout.
 *
 * ## Responsibilities
 *
 * 1. **Lock Recovery**: Reclaims stale processing rows where the worker
 *    died mid-processing (lockedAt > LOCK_TIMEOUT)
 *
 * 2. **Process**: Polls pending rows and syncs them to ClickHouse
 *
 * ## Trigger Configuration
 *
 * Configure in wrangler.jsonc with a cron expression like "0/5 * * * *" (every 5 min).
 */

import { Effect, Layer } from "effect";
import { DrizzleORM } from "@/db/client";
import { spansOutbox } from "@/db/schema";
import { and, eq, lt, or, isNull, lte } from "drizzle-orm";
import { ClickHouse } from "@/clickhouse/client";
import { Settings, type CloudflareEnvironment } from "@/settings";
import { DatabaseError } from "@/errors";
import { processOutboxMessages } from "@/workers/outboxProcessor";

// =============================================================================
// Constants
// =============================================================================

/**
 * Lock timeout in milliseconds.
 * If a row has been in 'processing' state longer than this, it's considered stale.
 */
const LOCK_TIMEOUT_MS = 30000; // 30 seconds

/**
 * Maximum retry count before a row is marked as failed.
 */
const MAX_RETRIES = 5;

/**
 * Maximum number of rows to process per cron invocation.
 * Prevents overwhelming the queue.
 */
const BATCH_LIMIT = 500;

// =============================================================================
// Types
// =============================================================================

/**
 * Cloudflare Scheduled Event type.
 */
interface ScheduledEvent {
  readonly scheduledTime: number;
  readonly cron: string;
}

/**
 * Extended Cloudflare environment bindings for Cron Trigger.
 */
export interface CronTriggerEnv extends CloudflareEnvironment {
  /** Hyperdrive binding for PostgreSQL connection pooling */
  readonly HYPERDRIVE?: {
    readonly connectionString: string;
  };
  /** Direct database URL (fallback when Hyperdrive is not configured) */
  readonly DATABASE_URL?: string;
}

// =============================================================================
// Main Processing Program
// =============================================================================

/**
 * Main ClickHouse cron processing program.
 *
 * Performs the following operations:
 * 1. Reclaims stale processing rows
 * 2. Queries pending rows ready for processing
 * 3. Processes pending rows via processOutboxMessages
 */
export const clickhouseCronProgram = (workerId: string) =>
  Effect.gen(function* () {
    const client = yield* DrizzleORM;
    const staleTime = new Date(Date.now() - LOCK_TIMEOUT_MS);
    const now = new Date();

    // =====================================================================
    // 1. Reclaim stale processing rows
    // =====================================================================
    // Rows that have been in 'processing' state longer than LOCK_TIMEOUT
    // are likely from a worker that crashed. Reset them to 'pending'.

    yield* client
      .update(spansOutbox)
      .set({
        status: "pending",
        lockedAt: null,
        lockedBy: null,
      })
      .where(
        and(
          eq(spansOutbox.status, "processing"),
          lt(spansOutbox.lockedAt, staleTime),
        ),
      )
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to reclaim stale locks",
              cause: e,
            }),
        ),
      );

    // =====================================================================
    // 2. Query pending rows ready for processing
    // =====================================================================
    // Conditions:
    // - status = 'pending'
    // - processAfter <= now (backoff expired)
    // - retryCount < MAX_RETRIES
    // - not currently locked (lockedAt is null or stale)

    const pendingRows = yield* client
      .select({
        spanId: spansOutbox.spanId,
        operation: spansOutbox.operation,
      })
      .from(spansOutbox)
      .where(
        and(
          eq(spansOutbox.status, "pending"),
          lte(spansOutbox.processAfter, now),
          lt(spansOutbox.retryCount, MAX_RETRIES),
          or(isNull(spansOutbox.lockedAt), lt(spansOutbox.lockedAt, staleTime)),
        ),
      )
      .orderBy(spansOutbox.createdAt)
      .limit(BATCH_LIMIT)
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to query pending rows",
              cause: e,
            }),
        ),
      );

    if (pendingRows.length === 0) {
      return;
    }

    console.log(`Processing ${pendingRows.length} pending outbox rows`);

    const messages = pendingRows.map((row) => ({
      spanId: row.spanId,
      operation: row.operation as "INSERT" | "UPDATE" | "DELETE",
      messageKey: `${row.spanId}:${row.operation}`,
    }));

    yield* processOutboxMessages(
      messages,
      () => {},
      () => {},
      workerId,
    );
  });

// =============================================================================
// Cron Handler
// =============================================================================

export default {
  /**
   * Scheduled event handler.
   *
   * @param _event - Cloudflare scheduled event (unused, but required by interface)
   * @param env - Cloudflare Workers environment bindings
   */
  async scheduled(_event: ScheduledEvent, env: CronTriggerEnv): Promise<void> {
    // Database connection string from Hyperdrive or direct URL
    const databaseUrl = env.HYPERDRIVE?.connectionString ?? env.DATABASE_URL;
    if (!databaseUrl) {
      console.error(
        "No database connection available (HYPERDRIVE or DATABASE_URL required)",
      );
      return;
    }

    const workerId = `workers-cron-${Date.now()}`;

    // Build layers
    const settingsLayer = Settings.LiveFromEnvironment(env);
    const drizzleLayer = DrizzleORM.layer({ connectionString: databaseUrl });
    const clickhouseLayer = ClickHouse.Default.pipe(
      Layer.provide(settingsLayer),
    );

    // Run the program
    await Effect.runPromise(
      clickhouseCronProgram(workerId).pipe(
        Effect.provide(drizzleLayer),
        Effect.provide(clickhouseLayer),
        Effect.provide(settingsLayer),
        Effect.catchAll((error) => {
          console.error("Cron trigger error:", error);
          return Effect.void;
        }),
      ),
    );
  },
};
