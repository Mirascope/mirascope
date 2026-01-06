import {
  pgTable,
  uuid,
  text,
  integer,
  timestamp,
  pgEnum,
  index,
  unique,
} from "drizzle-orm/pg-core";
import { spans } from "./spans";

/**
 * Outbox status enum for tracking span sync state.
 *
 * - pending: Ready to be processed
 * - processing: Currently being processed (locked)
 * - completed: Successfully synced to ClickHouse
 * - failed: Max retries exceeded, requires manual intervention
 */
export const outboxStatusEnum = pgEnum("outbox_status", [
  "pending",
  "processing",
  "completed",
  "failed",
]);

/**
 * Outbox table for tracking spans to be synced to ClickHouse.
 *
 * Implements the Transactional Outbox pattern:
 * 1. Span is inserted into PostgreSQL
 * 2. Outbox row is created in the same transaction
 * 3. Worker polls outbox and syncs to ClickHouse
 * 4. On success, outbox status is updated to 'completed'
 *
 * ## v1 Limitations
 * - Only INSERT operations are supported
 * - UPDATE/DELETE support can be added by using the operation field
 *
 * ## Idempotency
 * - ClickHouse side: ReplacingMergeTree + _version column
 * - PostgreSQL side: (span_id, operation) unique constraint
 */
export const spansOutbox = pgTable(
  "spans_outbox",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    spanId: uuid("span_id")
      .notNull()
      .references(() => spans.id, { onDelete: "cascade" }),
    operation: text("operation").notNull().default("INSERT"),
    status: outboxStatusEnum("status").notNull().default("pending"),
    retryCount: integer("retry_count").notNull().default(0),
    lastError: text("last_error"),
    lockedAt: timestamp("locked_at"),
    lockedBy: text("locked_by"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    processAfter: timestamp("process_after").defaultNow().notNull(),
    processedAt: timestamp("processed_at"),
  },
  (table) => ({
    // Idempotency: prevent duplicate operations for the same span
    spanOperationUnique: unique().on(table.spanId, table.operation),
    // Efficient query for processable rows
    processableIdx: index("spans_outbox_processable_idx").on(
      table.status,
      table.processAfter,
      table.retryCount
    ),
    // Lookup by spanId
    spanIdIdx: index("spans_outbox_span_id_idx").on(table.spanId),
  })
);

// Internal types
export type SpansOutbox = typeof spansOutbox.$inferSelect;
export type NewSpansOutbox = typeof spansOutbox.$inferInsert;

// Public type (if needed for API responses)
export type PublicSpansOutbox = Pick<
  SpansOutbox,
  | "id"
  | "spanId"
  | "operation"
  | "status"
  | "retryCount"
  | "lastError"
  | "createdAt"
  | "processAfter"
  | "processedAt"
>;
