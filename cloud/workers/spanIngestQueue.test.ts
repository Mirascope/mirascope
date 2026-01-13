/**
 * @fileoverview Tests for spans ingest queue global layer and setter.
 */

import { describe, expect, it, vi } from "vitest";
import { Effect, Layer } from "effect";

import {
  SpansIngestQueue,
  spansIngestQueueLayer,
  setSpansIngestQueueLayer,
  ingestSpansMessage,
  type SpansIngestMessage,
} from "./spanIngestQueue";
import { ClickHouse } from "@/db/clickhouse/client";
import { RealtimeSpans } from "@/workers/realtimeSpans";

// =============================================================================
// Test Helpers
// =============================================================================

/**
 * Creates a valid test message.
 */
function createTestMessage(
  overrides: Partial<SpansIngestMessage> = {},
): SpansIngestMessage {
  return {
    environmentId: "test-env-id",
    projectId: "test-project-id",
    organizationId: "test-org-id",
    receivedAt: Date.now(),
    serviceName: "test-service",
    serviceVersion: "1.0.0",
    resourceAttributes: { key: "value" },
    spans: [
      {
        traceId: "test-trace-id",
        spanId: "test-span-id",
        name: "test-span",
        startTimeUnixNano: "1000000000",
        endTimeUnixNano: "2000000000",
      },
    ],
    ...overrides,
  };
}

// =============================================================================
// Tests
// =============================================================================

describe("SpansIngestQueue", () => {
  describe("global layer", () => {
    it("default layer returns error when not initialized", async () => {
      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueue;
        return yield* queue.send(createTestMessage());
      });

      const error = await Effect.runPromise(
        program.pipe(Effect.provide(spansIngestQueueLayer), Effect.flip),
      );

      expect(error.message).toBe("SpansIngestQueue not initialized");
    });

    it("setSpansIngestQueueLayer updates the global layer", async () => {
      const mockSend = vi.fn().mockReturnValue(Effect.void);
      const newLayer = Layer.succeed(SpansIngestQueue, {
        send: mockSend,
      });

      setSpansIngestQueueLayer(newLayer);

      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueue;
        return yield* queue.send(createTestMessage());
      });

      await Effect.runPromise(
        program.pipe(Effect.provide(spansIngestQueueLayer)),
      );

      expect(mockSend).toHaveBeenCalled();

      // Reset global layer to default
      setSpansIngestQueueLayer(
        Layer.succeed(SpansIngestQueue, {
          send: () =>
            Effect.fail(new Error("SpansIngestQueue not initialized")),
        }),
      );
    });
  });

  describe("ingestSpansMessage", () => {
    it("inserts spans to ClickHouse and upserts to RealtimeSpans", async () => {
      const insertMock = vi.fn().mockReturnValue(Effect.void);
      const upsertMock = vi.fn().mockReturnValue(Effect.void);

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: insertMock,
        unsafeQuery: vi.fn(),
        command: vi.fn(),
      });

      const mockRealtimeLayer = Layer.succeed(RealtimeSpans, {
        upsert: upsertMock,
        search: vi.fn(),
        getTraceDetail: vi.fn(),
        exists: vi.fn(),
      });

      const message = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(message).pipe(
          Effect.provide(Layer.merge(mockClickHouseLayer, mockRealtimeLayer)),
        ),
      );

      expect(insertMock).toHaveBeenCalledWith(
        "spans_analytics",
        expect.any(Array),
      );
      expect(upsertMock).toHaveBeenCalledWith(message);
    });
  });
});
