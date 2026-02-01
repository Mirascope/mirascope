/**
 * @fileoverview Cloudflare Cron Trigger for enforcing trace data retention limits.
 *
 * Periodically deletes trace data in ClickHouse that exceeds the plan retention
 * window for each organization.
 *
 * ## Responsibilities
 *
 * 1. Resolve organization plan tiers
 * 2. Compute retention cutoffs per plan tier
 * 3. Delete expired spans and annotations from ClickHouse
 *
 * ## Trigger Configuration
 *
 * Configure in wrangler.jsonc with a cron expression like `0 10 * * *` (daily).
 */

import { and, inArray, lt } from "drizzle-orm";
import { Effect, Layer } from "effect";

import { ClickHouse } from "@/db/clickhouse/client";
import { formatDateTime64 } from "@/db/clickhouse/transform";
import { DrizzleORM } from "@/db/client";
import { annotations, organizations as organizationsTable } from "@/db/schema";
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

/** Maximum number of organizations to include per ClickHouse delete command. */
const ORGANIZATION_BATCH_SIZE = 100;

/** Maximum number of concurrent plan lookups per retention run. */
const PLAN_LOOKUP_CONCURRENCY = 10;

/** Milliseconds in a day (used to compute retention cutoffs). */
const MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000;

// =============================================================================
// Helpers
// =============================================================================

const chunkArray = <T>(items: readonly T[], size: number): T[][] => {
  if (items.length <= size) return [items.slice()];
  const chunks: T[][] = [];
  for (let index = 0; index < items.length; index += size) {
    chunks.push(items.slice(index, index + size));
  }
  return chunks;
};

const buildOrganizationFilter = (organizationIds: readonly string[]): string =>
  organizationIds.map((id) => `toUUID('${id}')`).join(", ");

const buildSpansDeleteQuery = ({
  organizationFilter,
  cutoffTimestamp,
}: {
  organizationFilter: string;
  cutoffTimestamp: string;
}): string =>
  `ALTER TABLE spans_analytics DELETE WHERE organization_id IN (${organizationFilter}) AND start_time < toDateTime64('${cutoffTimestamp}', 9, 'UTC')`;

const buildAnnotationsDeleteQuery = ({
  organizationFilter,
  cutoffTimestamp,
}: {
  organizationFilter: string;
  cutoffTimestamp: string;
}): string =>
  `ALTER TABLE annotations_analytics DELETE WHERE organization_id IN (${organizationFilter}) AND created_at < toDateTime64('${cutoffTimestamp}', 3, 'UTC')`;

// =============================================================================
// Retention Program
// =============================================================================

/**
 * Enforces data retention limits for trace data in ClickHouse.
 */
export const enforceDataRetentionLimits = Effect.gen(function* () {
  const client = yield* DrizzleORM;
  const payments = yield* Payments;
  const clickhouse = yield* ClickHouse;

  const organizations = yield* client
    .select({ id: organizationsTable.id })
    .from(organizationsTable)
    .pipe(
      Effect.mapError(
        (error) =>
          new DatabaseError({
            message: "Failed to list organizations for retention",
            cause: error,
          }),
      ),
    );

  if (organizations.length === 0) {
    return;
  }

  const retentionAssignments = yield* Effect.all(
    organizations.map((organization) =>
      payments.customers.subscriptions.getPlan(organization.id).pipe(
        Effect.flatMap((planTier) =>
          payments.customers.subscriptions.getPlanLimits(planTier),
        ),
        Effect.map((limits) => limits.dataRetentionDays),
        Effect.catchAll((error) => {
          console.error(
            `[dataRetentionCron] Failed to resolve plan for organization ${organization.id}:`,
            error,
          );
          console.warn(
            `[dataRetentionCron] Skipping retention for organization ${organization.id} due to plan lookup failure`,
          );
          return Effect.succeed(null);
        }),
        Effect.map((retentionDays) => ({
          organizationId: organization.id,
          retentionDays,
        })),
      ),
    ),
    { concurrency: PLAN_LOOKUP_CONCURRENCY },
  );

  const retentionGroups = new Map<number, string[]>();

  for (const assignment of retentionAssignments) {
    const { organizationId, retentionDays } = assignment;

    if (retentionDays === null) {
      continue;
    }

    if (!Number.isFinite(retentionDays) || retentionDays <= 0) {
      console.warn(
        `[dataRetentionCron] Skipping retention for organization ${organizationId} with invalid retention days: ${retentionDays}`,
      );
      continue;
    }

    const existingGroup = retentionGroups.get(retentionDays);
    if (existingGroup) {
      existingGroup.push(organizationId);
    } else {
      retentionGroups.set(retentionDays, [organizationId]);
    }
  }

  for (const [retentionDays, organizationIds] of retentionGroups) {
    const cutoffDate = new Date(
      Date.now() - retentionDays * MILLISECONDS_PER_DAY,
    );
    const spanCutoffTimestamp = formatDateTime64(cutoffDate, 9);
    const annotationCutoffTimestamp = formatDateTime64(cutoffDate, 3);

    const organizationChunks = chunkArray(
      organizationIds,
      ORGANIZATION_BATCH_SIZE,
    );

    for (const organizationChunk of organizationChunks) {
      const organizationFilter = buildOrganizationFilter(organizationChunk);

      const spansQuery = buildSpansDeleteQuery({
        organizationFilter,
        cutoffTimestamp: spanCutoffTimestamp,
      });
      const annotationsQuery = buildAnnotationsDeleteQuery({
        organizationFilter,
        cutoffTimestamp: annotationCutoffTimestamp,
      });

      const spansDeleted = yield* clickhouse.command(spansQuery).pipe(
        Effect.as(true),
        Effect.catchAll((error) => {
          console.error(
            "[dataRetentionCron] Failed to delete expired spans:",
            error,
          );
          return Effect.succeed(false);
        }),
      );

      const annotationsDeleted = yield* clickhouse
        .command(annotationsQuery)
        .pipe(
          Effect.as(true),
          Effect.catchAll((error) => {
            console.error(
              "[dataRetentionCron] Failed to delete expired annotations:",
              error,
            );
            return Effect.succeed(false);
          }),
        );

      if (!spansDeleted || !annotationsDeleted) {
        console.warn(
          "[dataRetentionCron] Skipping PostgreSQL annotation deletion because ClickHouse deletion failed",
        );
        continue;
      }

      yield* client
        .delete(annotations)
        .where(
          and(
            inArray(annotations.organizationId, organizationChunk),
            lt(annotations.createdAt, cutoffDate),
          ),
        )
        .returning({ id: annotations.id })
        .pipe(
          Effect.mapError(
            (error) =>
              new DatabaseError({
                message: "Failed to delete expired PostgreSQL annotations",
                cause: error,
              }),
          ),
          Effect.catchAll((error) => {
            console.error(
              "[dataRetentionCron] Failed to delete expired PostgreSQL annotations:",
              error,
            );
            return Effect.succeed([]);
          }),
        );
    }

    console.log(
      `[dataRetentionCron] Scheduled retention for ${organizationIds.length} organization${organizationIds.length === 1 ? "" : "s"} at ${retentionDays} day${retentionDays === 1 ? "" : "s"}`,
    );
  }
});

// =============================================================================
// Cron Handler
// =============================================================================

export default {
  /**
   * Scheduled event handler for data retention enforcement.
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
        "[dataRetentionCron] No database connection available (HYPERDRIVE or DATABASE_URL required)",
      );
      return;
    }

    const program = Effect.gen(function* () {
      const settings = yield* Settings;

      const drizzleLayer = DrizzleORM.layer({ connectionString: databaseUrl });
      const stripeLayer = Stripe.layer(settings.stripe);
      const paymentsLayer = Payments.Default.pipe(
        Layer.provide(stripeLayer),
        Layer.provide(drizzleLayer),
      );
      const clickhouseLayer = ClickHouse.layer(settings.clickhouse);

      yield* enforceDataRetentionLimits.pipe(
        Effect.provide(drizzleLayer),
        Effect.provide(paymentsLayer),
        Effect.provide(clickhouseLayer),
      );
    });

    await Effect.runPromise(
      program.pipe(
        Effect.provide(Settings.LiveFromEnvironment(env)),
        Effect.catchAll((error) => {
          console.error("[dataRetentionCron] Cron trigger error:", error);
          return Effect.void;
        }),
      ),
    );
  },
};
