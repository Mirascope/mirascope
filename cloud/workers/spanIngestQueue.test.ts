/**
 * @fileoverview Tests for span ingest queue consumer.
 */

import { describe, expect, it } from "@/tests/db";
import { Effect, Layer } from "effect";
import { afterEach, vi } from "vitest";

import spanIngestQueue, {
  SpansIngestQueue,
  ingestSpansMessage,
  spansIngestQueueLayer,
  setSpansIngestQueueLayer,
} from "./spanIngestQueue";
import { ClickHouse } from "@/db/clickhouse/client";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import { buildSpansIngestMessage } from "@/tests/clickhouse/fixtures";
import {
  createMockQueueBatch,
  createMockQueueMessage,
} from "@/tests/workers/fixtures";

/** Alias for shared fixture builder to match local naming convention. */
const createTestMessage = buildSpansIngestMessage;

// =============================================================================
// Tests
// =============================================================================

describe("spanIngestQueue", () => {
  const originalSpansIngestQueueLayer = spansIngestQueueLayer;

  afterEach(() => {
    setSpansIngestQueueLayer(originalSpansIngestQueueLayer);
  });

  describe("SpansIngestQueue", () => {
    it("Live method creates working service layer", async () => {
      const mockQueue = {
        send: vi.fn().mockResolvedValue(undefined),
      };

      const layer = SpansIngestQueue.Live(mockQueue);

      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueue;
        yield* queue.send(testMessage);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      expect(mockQueue.send).toHaveBeenCalledWith(testMessage);
    });

    it("Live method handles send failures", async () => {
      const mockQueue = {
        send: vi.fn().mockRejectedValue(new Error("Queue send failed")),
      };

      const layer = SpansIngestQueue.Live(mockQueue);

      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueue;
        yield* queue.send(testMessage);
      });

      await expect(
        Effect.runPromise(program.pipe(Effect.provide(layer))),
      ).rejects.toThrow("Failed to enqueue spans");
    });
  });

  describe("global layer", () => {
    it("fails when global layer is not initialized", async () => {
      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueue;
        yield* queue.send(testMessage);
      });

      const error = await Effect.runPromise(
        program.pipe(Effect.provide(spansIngestQueueLayer), Effect.flip),
      );

      expect(error.message).toBe("SpansIngestQueue not initialized");
    });

    it("setSpansIngestQueueLayer updates the global layer", async () => {
      const testMessage = createTestMessage();
      const send = vi.fn(() => Effect.void);
      const layer = Layer.succeed(SpansIngestQueue, { send });

      setSpansIngestQueueLayer(layer);

      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueue;
        yield* queue.send(testMessage);
      });

      await Effect.runPromise(
        program.pipe(Effect.provide(spansIngestQueueLayer)),
      );

      expect(send).toHaveBeenCalledWith(testMessage);
    });
  });

  describe("ingestSpansMessage", () => {
    it("writes to ClickHouse before DurableObject upsert", async () => {
      const callOrder: string[] = [];

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: vi.fn(() => {
          callOrder.push("clickhouse");
          return Effect.succeed(undefined);
        }),
        unsafeQuery: vi.fn(),
        command: vi.fn(),
      });

      const mockRealtimeLayer = Layer.succeed(RealtimeSpans, {
        upsert: vi.fn(() => {
          callOrder.push("realtime");
          return Effect.succeed(undefined);
        }),
        search: vi.fn(),
        getTraceDetail: vi.fn(),
        exists: vi.fn(),
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

    it("continues ClickHouse insert even when DurableObject upsert fails (best-effort)", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const clickhouseInsertMock = vi.fn(() => Effect.succeed(undefined));

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: clickhouseInsertMock,
        unsafeQuery: vi.fn(),
        command: vi.fn(),
      });

      const mockRealtimeLayer = Layer.succeed(RealtimeSpans, {
        upsert: vi.fn(() =>
          Effect.fail(new Error("DurableObject unavailable")),
        ),
        search: vi.fn(),
        getTraceDetail: vi.fn(),
        exists: vi.fn(),
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
        "[spanIngestQueue] DurableObject upsert failed (best-effort):",
        expect.any(Error),
      );

      consoleWarnSpy.mockRestore();
    });

    it("does not fail when DurableObject upsert fails (no queue retry)", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const mockClickHouseLayer = Layer.succeed(ClickHouse, {
        insert: vi.fn(() => Effect.succeed(undefined)),
        unsafeQuery: vi.fn(),
        command: vi.fn(),
      });

      const mockRealtimeLayer = Layer.succeed(RealtimeSpans, {
        upsert: vi.fn(() =>
          Effect.fail(new Error("DurableObject unavailable")),
        ),
        search: vi.fn(),
        getTraceDetail: vi.fn(),
        exists: vi.fn(),
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
        unsafeQuery: vi.fn(),
        command: vi.fn(),
      });

      const mockRealtimeLayer = Layer.succeed(RealtimeSpans, {
        upsert: vi.fn(() => Effect.succeed(undefined)),
        search: vi.fn(),
        getTraceDetail: vi.fn(),
        exists: vi.fn(),
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
        name: "LLM.Call",
        environment_id: "00000000-0000-0000-0000-000000000020",
        project_id: "00000000-0000-0000-0000-000000000030",
        organization_id: "00000000-0000-0000-0000-000000000040",
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

      const message = createMockQueueMessage(createTestMessage());
      const batch = createMockQueueBatch([message], "spans-ingest");
      const env = {
        ENVIRONMENT: "test",
        REALTIME_SPANS_DURABLE_OBJECT: {},
      };

      await spanIngestQueue.queue(batch, env as never);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[spanIngestQueue] Missing CLICKHOUSE_URL binding",
      );

      consoleErrorSpy.mockRestore();
    });

    it("logs error and retries when REALTIME_SPANS_DURABLE_OBJECT is missing", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const message = createMockQueueMessage(createTestMessage());
      const batch = createMockQueueBatch([message], "spans-ingest");
      const env = {
        ENVIRONMENT: "test",
        CLICKHOUSE_URL: "http://localhost:8123",
        CLICKHOUSE_USER: "default",
        CLICKHOUSE_PASSWORD: "",
        CLICKHOUSE_DATABASE: "default",
        // No REALTIME_SPANS_DURABLE_OBJECT - causes error when trying to create stub
      };

      await spanIngestQueue.queue(batch, env as never);

      // Missing DurableObject causes error during layer creation, caught by outer catchAll
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[spanIngestQueue] Error processing message:",
        expect.anything(),
      );
      expect(message.retryCalled).toBe(true);

      consoleErrorSpy.mockRestore();
    });

    it("does not warn when RECENT_SPANS_DURABLE_OBJECT is configured", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const message = createMockQueueMessage(createTestMessage());
      const batch = createMockQueueBatch([message], "spans-ingest");
      const env = {
        ENVIRONMENT: "test",
        CLICKHOUSE_URL: "http://localhost:8123",
        CLICKHOUSE_USER: "default",
        CLICKHOUSE_PASSWORD: "",
        CLICKHOUSE_DATABASE: "default",
        RECENT_SPANS_DURABLE_OBJECT: {
          idFromName: () => ({ toString: () => "test-id" }),
          get: () => ({
            fetch: () => Promise.resolve(new Response("ok")),
          }),
        },
      };

      await spanIngestQueue.queue(batch, env as never);

      expect(consoleWarnSpy).not.toHaveBeenCalledWith(
        "[spanIngestQueue] RECENT_SPANS_DURABLE_OBJECT not configured, skipping realtime cache",
      );

      consoleWarnSpy.mockRestore();
      consoleErrorSpy.mockRestore();
    });
  });

  describe("batch processing", () => {
    it("processes multiple messages in batch", async () => {
      const message1 = createMockQueueMessage(createTestMessage());
      const message2 = createMockQueueMessage(createTestMessage());
      const batch = createMockQueueBatch([message1, message2], "spans-ingest");

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

      const message = createMockQueueMessage(createTestMessage());
      const batch = createMockQueueBatch([message], "spans-ingest");

      const mockDurableObject = {
        idFromName: vi.fn().mockReturnValue({ toString: () => "test-id" }),
        get: vi.fn().mockReturnValue({
          fetch: vi.fn().mockRejectedValue(new Error("DurableObject error")),
        }),
      };

      const env = {
        ENVIRONMENT: "test",
        CLICKHOUSE_URL: "http://localhost:8123",
        CLICKHOUSE_USER: "default",
        CLICKHOUSE_PASSWORD: "",
        CLICKHOUSE_DATABASE: "default",
        RECENT_SPANS_DURABLE_OBJECT: mockDurableObject,
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
