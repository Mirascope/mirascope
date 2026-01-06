/**
 * @fileoverview Cloudflare Queue Consumer for ClickHouse sync.
 *
 * Receives outbox events from Cloudflare Queue and syncs spans to ClickHouse.
 * Uses outbox table lock/status management to prevent duplicate processing.
 *
 * ## Architecture
 *
 * ```
 * Cloudflare Queue (spans-outbox)
 *   └── Queue Consumer (this file)
 *         ├── DrizzleORM (PostgreSQL via Hyperdrive)
 *         └── ClickHouseLive (HTTP API)
 * ```
 *
 * ## Message Format
 *
 * ```json
 * { "spanId": "uuid", "operation": "INSERT" }
 * ```
 *
 * ## Deduplication
 *
 * - Same spanId:operation may arrive multiple times in a batch
 * - We deduplicate locally before processing
 * - All duplicate messages are acked/retried together
 */

import { Effect, Layer } from "effect";
import { DrizzleORM } from "@/db/client";
import { ClickHouseLive } from "@/clickhouse/client";
import {
  processOutboxMessages,
  type OutboxMessage,
} from "@/workers/outboxProcessor";
import {
  SettingsService,
  getSettingsFromEnvironment,
  type CloudflareEnvironment,
} from "@/settings";

// =============================================================================
// Types
// =============================================================================

/**
 * Queue message body format.
 * Kept minimal to avoid hitting Cloudflare Queue's 128KB limit.
 */
type QueueMessageBody = {
  spanId: string;
  operation: "INSERT" | "UPDATE" | "DELETE";
};

/**
 * Cloudflare Queue Message type (subset of Cloudflare Workers types).
 */
interface QueueMessage<Body> {
  readonly id: string;
  readonly body: Body;
  ack(): void;
  retry(): void;
}

/**
 * Cloudflare Queue MessageBatch type.
 */
interface MessageBatch<Body> {
  readonly queue: string;
  readonly messages: readonly QueueMessage<Body>[];
}

/**
 * Extended Cloudflare environment bindings for Queue Consumer.
 *
 * Includes Hyperdrive for PostgreSQL connection from Workers.
 */
export interface QueueConsumerEnvironment extends CloudflareEnvironment {
  /** Hyperdrive binding for PostgreSQL connection pooling */
  readonly HYPERDRIVE?: {
    readonly connectionString: string;
  };
  /** Direct database URL (fallback when Hyperdrive is not configured) */
  readonly DATABASE_URL?: string;
}

// =============================================================================
// Worker ID Generation
// =============================================================================

/**
 * Generate a unique worker ID for lock identification.
 *
 * Format: workers-{queue}-{uuid8}
 * - workers: Environment identifier (Cloudflare Workers)
 * - queue: Queue name for context
 * - uuid8: First 8 characters of a UUID for uniqueness
 *
 * Note: In Workers environment, os.hostname() and process.pid are not available.
 */
const generateWorkerId = (queueName: string): string => {
  const uuid = crypto.randomUUID().slice(0, 8);
  return `workers-${queueName}-${uuid}`;
};

// =============================================================================
// Queue Consumer Handler
// =============================================================================

/**
 * Cloudflare Queue Consumer export.
 *
 * Processes outbox messages in batches, syncing spans to ClickHouse.
 * Uses Workers-compatible implementations for both PostgreSQL and ClickHouse.
 */
export default {
  /**
   * Queue handler entry point.
   *
   * @param batch - Batch of messages from Cloudflare Queue
   * @param env - Cloudflare Workers environment bindings
   */
  async queue(
    batch: MessageBatch<QueueMessageBody>,
    env: QueueConsumerEnvironment,
  ): Promise<void> {
    // Skip empty batches
    if (batch.messages.length === 0) return;

    // =======================================================================
    // 1. Deduplicate messages by spanId:operation key
    // =======================================================================
    // Same key may appear multiple times in a batch due to:
    // - Retry delivery
    // - Race conditions in message production
    // All messages with the same key are acked/retried together

    const messageMap = new Map<string, QueueMessage<QueueMessageBody>[]>();
    const outboxMessages: OutboxMessage[] = [];
    const seenKeys = new Set<string>();

    for (const queueMessage of batch.messages) {
      const messageKey = `${queueMessage.body.spanId}:${queueMessage.body.operation}`;

      // Store all messages with same key (for batch ack/retry)
      const existing = messageMap.get(messageKey) ?? [];
      existing.push(queueMessage);
      messageMap.set(messageKey, existing);

      // Only add to outboxMessages once per unique key
      if (!seenKeys.has(messageKey)) {
        seenKeys.add(messageKey);
        outboxMessages.push({
          spanId: queueMessage.body.spanId,
          operation: queueMessage.body.operation,
          messageKey,
        });
      }
    }

    // =======================================================================
    // 2. Build Effect program with callbacks
    // =======================================================================

    // Generate worker ID for lock ownership (Workers environment)
    const workerId = generateWorkerId(batch.queue);

    const program = processOutboxMessages(
      outboxMessages,
      // ack callback: ack all messages with the same key
      (messageKey) => {
        const relatedMessages = messageMap.get(messageKey) ?? [];
        for (const queueMessage of relatedMessages) queueMessage.ack();
      },
      // retry callback: retry all messages with the same key
      (messageKey) => {
        const relatedMessages = messageMap.get(messageKey) ?? [];
        for (const queueMessage of relatedMessages) queueMessage.retry();
      },
      workerId,
    );

    // =======================================================================
    // 3. Build and run Effect with proper layers
    // =======================================================================

    // Settings layer from Cloudflare env bindings
    const settingsLayer = Layer.succeed(
      SettingsService,
      getSettingsFromEnvironment(env),
    );

    // Database connection string from Hyperdrive or direct URL
    const databaseUrl = env.HYPERDRIVE?.connectionString ?? env.DATABASE_URL;
    if (!databaseUrl) {
      console.error(
        "No database connection available (HYPERDRIVE or DATABASE_URL required)",
      );
      // Retry all messages - database not configured
      for (const queueMessage of batch.messages) {
        queueMessage.retry();
      }
      return;
    }

    // DrizzleORM layer with Hyperdrive connection
    const drizzleLayer = DrizzleORM.layer({ connectionString: databaseUrl });

    // Combined layer: Settings -> ClickHouse + Drizzle
    const runtimeLayer = Layer.mergeAll(ClickHouseLive, drizzleLayer).pipe(
      Layer.provide(settingsLayer),
    );

    // Run the program
    await Effect.runPromise(
      program.pipe(
        Effect.provide(runtimeLayer),
        Effect.catchAll((error) => {
          // Log unhandled errors but don't throw
          // Individual message ack/retry is handled in processOutboxMessages
          console.error("Queue consumer error:", error);
          return Effect.void;
        }),
      ),
    );
  },
};
