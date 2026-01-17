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
import { DrizzleORM } from "@/db/client";
import { Payments } from "@/payments";
import { buildSpansIngestMessage } from "@/tests/db/clickhouse/fixtures";
import {
  createMockQueueBatch,
  createMockQueueMessage,
} from "@/tests/workers/fixtures";
import { createMockEnv } from "@/tests/settings";

/** Alias for shared fixture builder to match local naming convention. */
const createTestMessage = buildSpansIngestMessage;

// =============================================================================
// Mock Layer Helpers
// =============================================================================

/** Default mock ClickHouse layer for tests. */
const createMockClickHouseLayer = (
  overrides: Partial<{
    insert: ReturnType<typeof vi.fn>;
  }> = {},
) =>
  Layer.succeed(ClickHouse, {
    insert: overrides.insert ?? vi.fn(() => Effect.succeed(undefined)),
    unsafeQuery: vi.fn(),
    command: vi.fn(),
  } as never);

/** Default mock RealtimeSpans layer for tests. */
const createMockRealtimeLayer = (
  overrides: Partial<{
    upsert: ReturnType<typeof vi.fn>;
  }> = {},
) =>
  Layer.succeed(RealtimeSpans, {
    upsert: overrides.upsert ?? vi.fn(() => Effect.succeed(undefined)),
    search: vi.fn(),
    getTraceDetail: vi.fn(),
    exists: vi.fn(),
  } as never);

/** Default mock DrizzleORM layer for tests. */
const createMockDrizzleLayer = (
  organizationLookupResult: unknown[] = [{ stripeCustomerId: "cus_test" }],
  error?: Error,
) =>
  Layer.succeed(DrizzleORM, {
    select: vi.fn(() => ({
      from: vi.fn(() => ({
        where: vi.fn(() =>
          error ? Effect.fail(error) : Effect.succeed(organizationLookupResult),
        ),
      })),
    })),
  } as never);

/** Default mock Payments layer for tests. */
const createMockPaymentsLayer = (
  overrides: Partial<{
    chargeMeter: ReturnType<typeof vi.fn>;
  }> = {},
) =>
  Layer.succeed(Payments, {
    products: {
      spans: {
        chargeMeter:
          overrides.chargeMeter ?? vi.fn(() => Effect.succeed(undefined)),
      },
    },
  } as never);

/** Creates all mock layers needed for ingestSpansMessage tests. */
const createAllMockLayers = (
  overrides: {
    clickhouse?: Partial<{ insert: ReturnType<typeof vi.fn> }>;
    realtime?: Partial<{ upsert: ReturnType<typeof vi.fn> }>;
    drizzle?: { result?: unknown[]; error?: Error };
    payments?: Partial<{ chargeMeter: ReturnType<typeof vi.fn> }>;
  } = {},
) =>
  Layer.mergeAll(
    createMockClickHouseLayer(overrides.clickhouse),
    createMockRealtimeLayer(overrides.realtime),
    createMockDrizzleLayer(overrides.drizzle?.result, overrides.drizzle?.error),
    createMockPaymentsLayer(overrides.payments),
  );

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

    it("Live method handles non-Error send failures", async () => {
      const mockQueue = {
        send: vi.fn().mockRejectedValue("string error"),
      };

      const layer = SpansIngestQueue.Live(mockQueue);

      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueue;
        yield* queue.send(testMessage);
      });

      await expect(
        Effect.runPromise(program.pipe(Effect.provide(layer))),
      ).rejects.toThrow("string error");
    });
  });

  describe("spansIngestQueueLayer", () => {
    it("uses the default layer and allows updates", async () => {
      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* SpansIngestQueue;
        yield* queue.send(testMessage);
      });

      await expect(
        Effect.runPromise(program.pipe(Effect.provide(spansIngestQueueLayer))),
      ).rejects.toThrow("SpansIngestQueue not initialized");

      const send = vi.fn(() => Effect.void);
      const layer = Layer.succeed(SpansIngestQueue, { send });
      setSpansIngestQueueLayer(layer);

      await Effect.runPromise(
        program.pipe(Effect.provide(spansIngestQueueLayer)),
      );

      expect(send).toHaveBeenCalledWith(testMessage);
    });
  });

  describe("ingestSpansMessage", () => {
    it("writes to ClickHouse before metering and DurableObject upsert", async () => {
      const callOrder: string[] = [];

      const layers = Layer.mergeAll(
        createMockClickHouseLayer({
          insert: vi.fn(() => {
            callOrder.push("clickhouse");
            return Effect.succeed(undefined);
          }),
        }),
        createMockRealtimeLayer({
          upsert: vi.fn(() => {
            callOrder.push("realtime");
            return Effect.succeed(undefined);
          }),
        }),
        createMockDrizzleLayer(),
        createMockPaymentsLayer({
          chargeMeter: vi.fn(() => {
            callOrder.push("meter");
            return Effect.succeed(undefined);
          }),
        }),
      );

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(Effect.provide(layers)),
      );

      expect(callOrder).toEqual(["clickhouse", "meter", "realtime"]);
    });

    it("continues ClickHouse insert even when DurableObject upsert fails (best-effort)", async () => {
      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const clickhouseInsertMock = vi.fn(() => Effect.succeed(undefined));

      const layers = createAllMockLayers({
        clickhouse: { insert: clickhouseInsertMock },
        realtime: {
          upsert: vi.fn(() =>
            Effect.fail(new Error("DurableObject unavailable")),
          ),
        },
      });

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(Effect.provide(layers)),
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

      const layers = createAllMockLayers({
        realtime: {
          upsert: vi.fn(() =>
            Effect.fail(new Error("DurableObject unavailable")),
          ),
        },
      });

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(Effect.provide(layers)),
      );

      consoleWarnSpy.mockRestore();
    });

    it("transforms spans for ClickHouse correctly", async () => {
      let insertedData: unknown[] = [];

      const layers = createAllMockLayers({
        clickhouse: {
          insert: vi.fn((_table: string, data: unknown[]) => {
            insertedData = data;
            return Effect.succeed(undefined);
          }),
        },
      });

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(Effect.provide(layers)),
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

    it("continues when metering fails (best-effort)", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});
      const realtimeUpsertMock = vi.fn(() => Effect.succeed(undefined));
      const chargeMeterMock = vi.fn(() =>
        Effect.fail(new Error("Stripe error")),
      );

      const layers = Layer.mergeAll(
        createMockClickHouseLayer(),
        createMockRealtimeLayer({ upsert: realtimeUpsertMock }),
        createMockDrizzleLayer(),
        createMockPaymentsLayer({ chargeMeter: chargeMeterMock }),
      );

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(Effect.provide(layers)),
      );

      expect(chargeMeterMock).toHaveBeenCalledTimes(1);
      expect(realtimeUpsertMock).toHaveBeenCalledTimes(1);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        `[spanIngestQueue] Failed to meter span ${testMessage.spans[0].spanId}:`,
        expect.any(Error),
      );

      consoleErrorSpy.mockRestore();
    });

    it("skips metering when organization lookup fails", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});
      const chargeMeterMock = vi.fn(() => Effect.succeed(undefined));

      const layers = Layer.mergeAll(
        createMockClickHouseLayer(),
        createMockRealtimeLayer(),
        createMockDrizzleLayer([], new Error("DB error")),
        createMockPaymentsLayer({ chargeMeter: chargeMeterMock }),
      );

      const testMessage = createTestMessage();

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(Effect.provide(layers)),
      );

      expect(chargeMeterMock).not.toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        `[spanIngestQueue] Failed to fetch organization ${testMessage.organizationId} for span metering:`,
        expect.any(Error),
      );
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        `[spanIngestQueue] Organization ${testMessage.organizationId} not found for span metering`,
      );

      consoleErrorSpy.mockRestore();
    });

    it("does not attempt metering when no spans are present", async () => {
      const selectMock = vi.fn(() => ({
        from: vi.fn(() => ({
          where: vi.fn(() =>
            Effect.succeed([{ stripeCustomerId: "cus_test" }]),
          ),
        })),
      }));
      const chargeMeterMock = vi.fn(() => Effect.succeed(undefined));

      const layers = Layer.mergeAll(
        createMockClickHouseLayer(),
        createMockRealtimeLayer(),
        Layer.succeed(DrizzleORM, { select: selectMock } as never),
        createMockPaymentsLayer({ chargeMeter: chargeMeterMock }),
      );

      const testMessage = { ...createTestMessage(), spans: [] };

      await Effect.runPromise(
        ingestSpansMessage(testMessage).pipe(Effect.provide(layers)),
      );

      expect(selectMock).not.toHaveBeenCalled();
      expect(chargeMeterMock).not.toHaveBeenCalled();
    });
  });

  describe("configuration validation", () => {
    it("retries when CLICKHOUSE_URL is missing", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const message = createMockQueueMessage(createTestMessage());
      const batch = createMockQueueBatch([message], "spans-ingest");
      const environment = {
        ENVIRONMENT: "test",
        REALTIME_SPANS_DURABLE_OBJECT: {},
      };

      await spanIngestQueue.queue(batch, environment as never);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[spanIngestQueue] Missing CLICKHOUSE_URL binding",
      );

      consoleErrorSpy.mockRestore();
    });

    it("retries when DATABASE_URL is missing", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const message = createMockQueueMessage(createTestMessage());
      const batch = createMockQueueBatch([message], "spans-ingest");
      const environment = createMockEnv({ DATABASE_URL: undefined });

      await spanIngestQueue.queue(batch, environment as never);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[spanIngestQueue] Missing DATABASE_URL binding",
      );

      consoleErrorSpy.mockRestore();
    });
  });

  describe("batch processing", () => {
    it("processes multiple messages in batch", async () => {
      const message1 = createMockQueueMessage(createTestMessage());
      const message2 = createMockQueueMessage(createTestMessage());
      const batch = createMockQueueBatch([message1, message2], "spans-ingest");

      const environment = {
        ENVIRONMENT: "test",
      };

      await spanIngestQueue.queue(batch, environment as never);

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

      const environment = {
        ...createMockEnv(),
        REALTIME_SPANS_DURABLE_OBJECT: mockDurableObject,
      };

      await spanIngestQueue.queue(batch, environment as never);

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[spanIngestQueue] Error processing message:",
        expect.anything(),
      );
      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);

      consoleErrorSpy.mockRestore();
    });
  });
});
