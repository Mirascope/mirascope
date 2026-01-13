/**
 * @fileoverview Tests for span ingest queue consumer.
 */

import { describe, expect, it } from "@/tests/db";
import { Effect, Layer } from "effect";
import type { Message, MessageBatch } from "@cloudflare/workers-types";
import { vi } from "vitest";

import spanIngestQueue, {
  type SpansIngestMessage,
  SpansIngestQueueService,
  ingestSpansMessage,
} from "./spanIngestQueue";
import { ClickHouse } from "@/clickhouse/client";
import { RealtimeSpans } from "@/realtimeSpans";

// =============================================================================
// Test Helpers
// =============================================================================

function createMockMessage(
  body: SpansIngestMessage,
): Message<SpansIngestMessage> & {
  retryCalled: boolean;
  retryOptions?: { delaySeconds: number };
} {
  const mockMessage = {
    body,
    id: "test-message-id",
    timestamp: new Date(),
    attempts: 1,
    retryCalled: false,
    retryOptions: undefined as { delaySeconds: number } | undefined,
    ack: vi.fn(),
    retry: vi.fn(function (
      this: typeof mockMessage,
      options?: { delaySeconds: number },
    ) {
      this.retryCalled = true;
      this.retryOptions = options;
    }),
  };
  return mockMessage as unknown as Message<SpansIngestMessage> & {
    retryCalled: boolean;
    retryOptions?: { delaySeconds: number };
  };
}

function createMockBatch(
  messages: Message<SpansIngestMessage>[],
): MessageBatch<SpansIngestMessage> {
  return {
    messages,
    queue: "spans-ingest",
    ackAll: vi.fn(),
    retryAll: vi.fn(),
  } as unknown as MessageBatch<SpansIngestMessage>;
}

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
    resourceAttributes: { "service.name": "test-service" },
    spans: [
      {
        traceId: "0123456789abcdef0123456789abcdef",
        spanId: "0123456789abcdef",
        name: "test-span",
        startTimeUnixNano: "1704067200000000000",
        endTimeUnixNano: "1704067201000000000",
        attributes: { "test.attr": "value" },
      },
    ],
    ...overrides,
  };
}

// =============================================================================
// Tests
// =============================================================================

describe("spanIngestQueue", () => {
  describe("SpansIngestQueueService", () => {
    it("Live method creates working service layer", async () => {
      const mockQueue = {
        send: vi.fn().mockResolvedValue(undefined),
      };

      const layer = SpansIngestQueueService.Live(mockQueue);

      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueueService;
        yield* queue.send(testMessage);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      expect(mockQueue.send).toHaveBeenCalledWith(testMessage);
    });

    it("Live method handles send failures", async () => {
      const mockQueue = {
        send: vi.fn().mockRejectedValue(new Error("Queue send failed")),
      };

      const layer = SpansIngestQueueService.Live(mockQueue);

      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueueService;
        yield* queue.send(testMessage);
      });

      await expect(
        Effect.runPromise(program.pipe(Effect.provide(layer))),
      ).rejects.toThrow("Failed to enqueue spans");
    });
  });

  describe("ingestSpansMessage", () => {
    it("writes to ClickHouse before DO upsert", async () => {
      const callOrder: string[] = [];

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: vi.fn(() => {
          callOrder.push("clickhouse");
          return Effect.succeed(undefined);
        }),
        query: vi.fn(),
      } as never);

      const mockRealtimeLayer = Layer.succeed(RealtimeSpans, {
        upsert: vi.fn(() => {
          callOrder.push("realtime");
          return Effect.succeed(undefined);
        }),
        search: vi.fn(),
        getTraceDetail: vi.fn(),
        existsSpan: vi.fn(),
      });

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(
          Effect.provide(
            Layer.mergeAll(mockClickHouseLayer, mockRealtimeLayer),
          ),
        ),
      );

      expect(callOrder).toEqual(["clickhouse", "realtime"]);
    });

    it("continues ClickHouse insert even when DO upsert fails (best-effort)", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const clickhouseInsertMock = vi.fn(() => Effect.succeed(undefined));

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: clickhouseInsertMock,
        query: vi.fn(),
      } as never);

      const mockRealtimeLayer = Layer.succeed(RealtimeSpans, {
        upsert: vi.fn(() => Effect.fail(new Error("DO unavailable"))),
        search: vi.fn(),
        getTraceDetail: vi.fn(),
        existsSpan: vi.fn(),
      });

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(
          Effect.provide(
            Layer.mergeAll(mockClickHouseLayer, mockRealtimeLayer),
          ),
        ),
      );

      expect(clickhouseInsertMock).toHaveBeenCalledTimes(1);
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        "[spanIngestQueue] DO upsert failed (best-effort):",
        expect.any(Error),
      );

      consoleWarnSpy.mockRestore();
    });

    it("does not fail when DO upsert fails (no queue retry)", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: vi.fn(() => Effect.succeed(undefined)),
        query: vi.fn(),
      } as never);

      const mockRealtimeLayer = Layer.succeed(RealtimeSpans, {
        upsert: vi.fn(() => Effect.fail(new Error("DO unavailable"))),
        search: vi.fn(),
        getTraceDetail: vi.fn(),
        existsSpan: vi.fn(),
      });

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(
          Effect.provide(
            Layer.mergeAll(mockClickHouseLayer, mockRealtimeLayer),
          ),
        ),
      );

      consoleWarnSpy.mockRestore();
    });

    it("transforms spans for ClickHouse correctly", async () => {
      let insertedData: unknown[] = [];

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: vi.fn((_table: string, data: unknown[]) => {
          insertedData = data;
          return Effect.succeed(undefined);
        }),
        query: vi.fn(),
      } as never);

      const mockRealtimeLayer = Layer.succeed(RealtimeSpans, {
        upsert: vi.fn(() => Effect.succeed(undefined)),
        search: vi.fn(),
        getTraceDetail: vi.fn(),
        existsSpan: vi.fn(),
      });

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(
          Effect.provide(
            Layer.mergeAll(mockClickHouseLayer, mockRealtimeLayer),
          ),
        ),
      );

      expect(insertedData).toHaveLength(1);
      expect(insertedData[0]).toMatchObject({
        trace_id: "0123456789abcdef0123456789abcdef",
        span_id: "0123456789abcdef",
        name: "test-span",
        environment_id: "test-env-id",
        project_id: "test-project-id",
        organization_id: "test-org-id",
        service_name: "test-service",
        service_version: "1.0.0",
      });
    });
  });

  describe("configuration validation", () => {
    it("retries when CLICKHOUSE_URL is missing", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);
      const env = {
        ENVIRONMENT: "test",
        RECENT_SPANS_DO: {},
      };

      await spanIngestQueue.queue(batch, env as never);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[spanIngestQueue] Missing CLICKHOUSE_URL binding",
      );

      consoleErrorSpy.mockRestore();
    });

    it("warns but continues when RECENT_SPANS_DO is missing", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);
      const env = {
        ENVIRONMENT: "test",
        CLICKHOUSE_URL: "http://localhost:8123",
        CLICKHOUSE_USER: "default",
        CLICKHOUSE_PASSWORD: "",
        CLICKHOUSE_DATABASE: "default",
      };

      await spanIngestQueue.queue(batch, env as never);

      expect(consoleWarnSpy).toHaveBeenCalledWith(
        "[spanIngestQueue] RECENT_SPANS_DO not configured, skipping realtime cache",
      );
      // ClickHouse error causes retry (since no mock), but DO missing doesn't
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[spanIngestQueue] Error processing message:",
        expect.anything(),
      );

      consoleWarnSpy.mockRestore();
      consoleErrorSpy.mockRestore();
    });
  });

  describe("batch processing", () => {
    it("processes multiple messages in batch", async () => {
      const message1 = createMockMessage(createTestMessage());
      const message2 = createMockMessage(createTestMessage());
      const batch = createMockBatch([message1, message2]);

      const env = {
        ENVIRONMENT: "test",
      };

      await spanIngestQueue.queue(batch, env as never);

      expect(message1.retryCalled).toBe(true);
      expect(message2.retryCalled).toBe(true);
    });
  });

  describe("error handling", () => {
    it("logs error and retries on processing failure", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);

      const mockDO = {
        idFromName: vi.fn().mockReturnValue({ toString: () => "test-id" }),
        get: vi.fn().mockReturnValue({
          fetch: vi.fn().mockRejectedValue(new Error("DO error")),
        }),
      };

      const env = {
        ENVIRONMENT: "test",
        CLICKHOUSE_URL: "http://localhost:8123",
        CLICKHOUSE_USER: "default",
        CLICKHOUSE_PASSWORD: "",
        CLICKHOUSE_DATABASE: "default",
        RECENT_SPANS_DO: mockDO,
      };

      await spanIngestQueue.queue(batch, env as never);

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("[spanIngestQueue] Error processing message:"),
        expect.anything(),
      );
      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);

      consoleErrorSpy.mockRestore();
    });
  });
});
