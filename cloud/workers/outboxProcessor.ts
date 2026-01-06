/**
 * @fileoverview Outbox processor for ClickHouse sync.
 *
 * Shared processing logic for the Queue Consumer.
 * Handles span extraction from PostgreSQL, transformation to ClickHouse format,
 * and batch insertion with retry logic.
 */

import { Duration, Effect, Schedule } from "effect";
import { and, eq, lte } from "drizzle-orm";
import { DrizzleORM } from "@/db/client";
import { ClickHouse } from "@/clickhouse/client";
import { spansOutbox, spans, traces } from "@/db/schema";
import type { Span } from "@/db/schema/spans";
import type { Trace } from "@/db/schema/traces";
import { DatabaseError } from "@/errors";

// =============================================================================
// Types
// =============================================================================

export type OutboxMessage = {
  spanId: string;
  operation: "INSERT" | "UPDATE" | "DELETE";
  messageKey: string;
};

export type SpanAnalyticsRow = {
  id: string;
  trace_db_id: string;
  trace_id: string;
  span_id: string;
  parent_span_id: string | null;
  environment_id: string;
  project_id: string;
  organization_id: string;
  start_time: string;
  end_time: string | null;
  duration_ms: number | null;
  name: string;
  name_lower: string;
  kind: number | null;
  status_code: number | null;
  status_message: string | null;
  model: string | null;
  provider: string | null;
  input_tokens: number | null;
  output_tokens: number | null;
  total_tokens: number | null;
  cost_usd: number | null;
  function_id: string | null;
  function_name: string | null;
  function_version: string | null;
  error_type: string | null;
  error_message: string | null;
  attributes: string;
  events: string | null;
  links: string | null;
  service_name: string | null;
  service_version: string | null;
  resource_attributes: string | null;
  created_at: string;
  synced_at: string;
  _version: number;
};

// =============================================================================
// Constants
// =============================================================================

const MAX_RETRIES = 5;
const MAX_ERROR_MESSAGE_LENGTH = 500;

// =============================================================================
// Utility Functions
// =============================================================================

const outboxRetrySchedule = Schedule.exponential(Duration.seconds(1)).pipe(
  Schedule.whileOutput((delay) =>
    Duration.lessThanOrEqualTo(delay, Duration.minutes(5)),
  ),
);

/**
 * Calculate exponential backoff delay for persisted outbox retries.
 */
const calculateBackoff = (retryCount: number) =>
  Effect.gen(function* () {
    const driver = yield* Schedule.driver(outboxRetrySchedule);
    let delay = Duration.millis(0);

    for (let attempt = 0; attempt <= retryCount; attempt += 1) {
      delay = yield* driver.next(undefined);
    }

    return new Date(Date.now() + Duration.toMillis(delay));
  });

const clickhouseInsertRetrySchedule = Schedule.addDelay(
  Schedule.recurs(2),
  (attempt) => `${2 ** attempt} second`,
);

/**
 * Sanitize error message to prevent excessive storage and credential leakage.
 *
 * - Masks ClickHouse DSN credentials (clickhouse://user:pass@host)
 * - Masks key-value patterns (password=, secret=)
 * - Truncates to MAX_ERROR_MESSAGE_LENGTH characters
 */
const sanitizeErrorMessage = (message: string): string => {
  const sanitized = message
    // ClickHouse DSN format (clickhouse://user:pass@host)
    .replace(/clickhouse:\/\/[^@]+@/gi, "clickhouse://***@")
    // Key-value patterns
    .replace(/password[=:][^\s&]+/gi, "password=***")
    .replace(/secret[=:][^\s&]+/gi, "secret=***");
  return sanitized.slice(0, MAX_ERROR_MESSAGE_LENGTH);
};

/**
 * Format Date as ClickHouse DateTime64 string.
 *
 * Example (precision=9): "2024-01-01 12:34:56.123000000"
 */
const formatDateTime64 = (date: Date, precision: number): string => {
  const iso = date.toISOString(); // YYYY-MM-DDTHH:MM:SS.mmmZ
  const [datePart, timePart] = iso.split("T");
  const timeWithoutZone = timePart?.replace("Z", "") ?? "00:00:00.000";
  const [time, milliseconds = ""] = timeWithoutZone.split(".");
  const paddedFraction = milliseconds
    .padEnd(precision, "0")
    .slice(0, precision);
  return `${datePart} ${time}.${paddedFraction}`;
};

/**
 * Extract attribute value from JSONB attributes.
 */
const getAttributeValue = (
  attributes: Record<string, unknown> | null,
  key: string,
): unknown => {
  if (!attributes) return null;
  return attributes[key] ?? null;
};

/**
 * Transform a span + trace into ClickHouse analytics format.
 */
export const transformSpanForClickHouse = (
  span: Span,
  trace: Trace,
): SpanAnalyticsRow => {
  const attributes = span.attributes as Record<string, unknown> | null;
  const status = span.status as { code?: number; message?: string } | null;

  // Calculate duration in milliseconds
  // Per plan: fallback to null if end_time < start_time (negative duration)
  let durationMs: number | null = null;
  if (span.startTimeUnixNano && span.endTimeUnixNano) {
    const startNs = BigInt(span.startTimeUnixNano);
    const endNs = BigInt(span.endTimeUnixNano);
    const calculatedMs = Number((endNs - startNs) / BigInt(1000000));
    // Only set if non-negative (negative indicates data inconsistency)
    durationMs = calculatedMs >= 0 ? calculatedMs : null;
  }

  // Convert Unix nano to ISO string
  const startTime = span.startTimeUnixNano
    ? new Date(Number(BigInt(span.startTimeUnixNano) / BigInt(1000000)))
    : new Date();
  const endTime = span.endTimeUnixNano
    ? new Date(Number(BigInt(span.endTimeUnixNano) / BigInt(1000000)))
    : null;

  return {
    id: span.id,
    trace_db_id: span.traceId,
    trace_id: span.otelTraceId,
    span_id: span.otelSpanId,
    parent_span_id: span.parentSpanId,
    environment_id: span.environmentId,
    project_id: span.projectId,
    organization_id: span.organizationId,
    start_time: formatDateTime64(startTime, 9),
    end_time: endTime ? formatDateTime64(endTime, 9) : null,
    duration_ms: durationMs,
    name: span.name,
    name_lower: span.name.toLowerCase(),
    kind: span.kind,
    status_code: status?.code ?? null,
    status_message: status?.message ?? null,
    // LLM-specific attributes
    model: getAttributeValue(attributes, "gen_ai.request.model") as
      | string
      | null,
    provider: getAttributeValue(attributes, "gen_ai.system") as string | null,
    input_tokens: getAttributeValue(attributes, "gen_ai.usage.input_tokens") as
      | number
      | null,
    output_tokens: getAttributeValue(
      attributes,
      "gen_ai.usage.output_tokens",
    ) as number | null,
    total_tokens: null, // Calculated if needed
    cost_usd: getAttributeValue(attributes, "gen_ai.usage.cost") as
      | number
      | null,
    function_id: getAttributeValue(attributes, "mirascope.function_id") as
      | string
      | null,
    function_name: getAttributeValue(attributes, "mirascope.function_name") as
      | string
      | null,
    function_version: getAttributeValue(
      attributes,
      "mirascope.function_version",
    ) as string | null,
    error_type: getAttributeValue(attributes, "exception.type") as
      | string
      | null,
    error_message: getAttributeValue(attributes, "exception.message") as
      | string
      | null,
    // Full JSON attributes
    attributes: JSON.stringify(attributes ?? {}),
    events: span.events ? JSON.stringify(span.events) : null,
    links: span.links ? JSON.stringify(span.links) : null,
    // Trace-level info
    service_name: trace.serviceName,
    service_version: trace.serviceVersion,
    resource_attributes: trace.resourceAttributes
      ? JSON.stringify(trace.resourceAttributes)
      : null,
    // Timestamps
    created_at: formatDateTime64(span.createdAt ?? new Date(), 3),
    synced_at: formatDateTime64(new Date(), 3),
    _version: Date.now(),
  };
};

// =============================================================================
// Main Processing Function
// =============================================================================

/**
 * Process a batch of outbox messages.
 *
 * Shared between Queue Consumer and outbox handling utilities.
 * Handles locking, transformation, ClickHouse insertion, and status updates.
 *
 * @param messages - Array of outbox messages to process
 * @param onAck - Callback when message is successfully processed or should not be retried
 * @param onRetry - Callback when message should be retried
 * @param workerId - Worker identifier for lock ownership (for debugging/collision analysis)
 */
export const processOutboxMessages = (
  messages: OutboxMessage[],
  onAck: (messageKey: string) => void,
  onRetry: (messageKey: string) => void,
  workerId: string,
) =>
  Effect.gen(function* () {
    const client = yield* DrizzleORM;
    const clickhouse = yield* ClickHouse;

    const clickhouseRows: SpanAnalyticsRow[] = [];
    const processedMessages: OutboxMessage[] = [];

    for (const outboxMessage of messages) {
      // 0. Check if outbox row exists
      const [existingRow] = yield* client
        .select()
        .from(spansOutbox)
        .where(
          and(
            eq(spansOutbox.spanId, outboxMessage.spanId),
            eq(spansOutbox.operation, outboxMessage.operation),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to query outbox",
                cause: e,
              }),
          ),
        );

      if (!existingRow) {
        // Orphan message - ack and skip
        onAck(outboxMessage.messageKey);
        continue;
      }

      // 1. Try to lock the outbox row
      const now = new Date();
      const [outboxRow] = yield* client
        .update(spansOutbox)
        .set({ status: "processing", lockedAt: now, lockedBy: workerId })
        .where(
          and(
            eq(spansOutbox.spanId, outboxMessage.spanId),
            eq(spansOutbox.operation, outboxMessage.operation),
            eq(spansOutbox.status, "pending"),
            lte(spansOutbox.processAfter, now),
          ),
        )
        .returning()
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to lock outbox row",
                cause: e,
              }),
          ),
        );

      if (!outboxRow) {
        // Failed to acquire lock - already processing, completed, or not ready
        onAck(outboxMessage.messageKey);
        continue;
      }

      // 2. Get span with trace info from PostgreSQL
      const [spanWithTrace] = yield* client
        .select({
          span: spans,
          trace: traces,
        })
        .from(spans)
        .innerJoin(traces, eq(spans.traceId, traces.id))
        .where(eq(spans.id, outboxMessage.spanId))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to query span with trace",
                cause: e,
              }),
          ),
        );

      if (!spanWithTrace) {
        // Span not found - mark as completed
        yield* client
          .update(spansOutbox)
          .set({ status: "completed", processedAt: now })
          .where(
            and(
              eq(spansOutbox.spanId, outboxMessage.spanId),
              eq(spansOutbox.operation, outboxMessage.operation),
            ),
          )
          .pipe(
            Effect.mapError(
              (e) =>
                new DatabaseError({
                  message: "Failed to update outbox status",
                  cause: e,
                }),
            ),
          );
        onAck(outboxMessage.messageKey);
        continue;
      }

      // 3. Transform to ClickHouse format
      clickhouseRows.push(
        transformSpanForClickHouse(spanWithTrace.span, spanWithTrace.trace),
      );
      processedMessages.push(outboxMessage);
    }

    if (clickhouseRows.length === 0) return;

    // 4. Bulk insert to ClickHouse with small in-process retry
    // In-process retry smooths transient failures; outbox backoff handles longer delays.
    const insertEffect = clickhouse
      .insert("spans_analytics", clickhouseRows)
      .pipe(Effect.retry(clickhouseInsertRetrySchedule));

    yield* insertEffect.pipe(
      Effect.matchEffect({
        onSuccess: () =>
          Effect.gen(function* () {
            // 5. On success, mark as completed
            for (const processedMessage of processedMessages) {
              yield* client
                .update(spansOutbox)
                .set({ status: "completed", processedAt: new Date() })
                .where(
                  and(
                    eq(spansOutbox.spanId, processedMessage.spanId),
                    eq(spansOutbox.operation, processedMessage.operation),
                  ),
                )
                .pipe(
                  Effect.mapError(
                    (e) =>
                      new DatabaseError({
                        message: "Failed to update outbox status",
                        cause: e,
                      }),
                  ),
                );
              onAck(processedMessage.messageKey);
            }
          }),
        onFailure: (error) =>
          Effect.gen(function* () {
            // ClickHouse insert failed - retry with exponential backoff or fail
            for (const processedMessage of processedMessages) {
              const [current] = yield* client
                .select({ retryCount: spansOutbox.retryCount })
                .from(spansOutbox)
                .where(
                  and(
                    eq(spansOutbox.spanId, processedMessage.spanId),
                    eq(spansOutbox.operation, processedMessage.operation),
                  ),
                )
                .limit(1)
                .pipe(
                  Effect.mapError(
                    (e) =>
                      new DatabaseError({
                        message: "Failed to query retry count",
                        cause: e,
                      }),
                  ),
                );

              const newRetryCount = (current?.retryCount ?? 0) + 1;

              if (newRetryCount >= MAX_RETRIES) {
                // Max retries exceeded - mark as failed
                yield* client
                  .update(spansOutbox)
                  .set({
                    status: "failed",
                    retryCount: newRetryCount,
                    lastError: sanitizeErrorMessage(String(error)),
                    lockedAt: null,
                  })
                  .where(
                    and(
                      eq(spansOutbox.spanId, processedMessage.spanId),
                      eq(spansOutbox.operation, processedMessage.operation),
                    ),
                  )
                  .pipe(
                    Effect.mapError(
                      (e) =>
                        new DatabaseError({
                          message: "Failed to update outbox status",
                          cause: e,
                        }),
                    ),
                  );
                onAck(processedMessage.messageKey); // Failed is acked (no more retries)
              } else {
                // Schedule retry with exponential backoff
                const processAfter = yield* calculateBackoff(newRetryCount);

                yield* client
                  .update(spansOutbox)
                  .set({
                    status: "pending",
                    retryCount: newRetryCount,
                    processAfter,
                    lastError: sanitizeErrorMessage(String(error)),
                    lockedAt: null,
                  })
                  .where(
                    and(
                      eq(spansOutbox.spanId, processedMessage.spanId),
                      eq(spansOutbox.operation, processedMessage.operation),
                    ),
                  )
                  .pipe(
                    Effect.mapError(
                      (e) =>
                        new DatabaseError({
                          message: "Failed to update outbox status",
                          cause: e,
                        }),
                    ),
                  );
                onRetry(processedMessage.messageKey);
              }
            }
          }),
      }),
    );
  });
