/**
 * @fileoverview Tests for router metering queue consumer.
 */

import { describe, expect, it, TEST_DATABASE_URL } from "@/tests/db";
import { Effect, Layer } from "effect";
import { Database } from "@/db";
import { Payments } from "@/payments";
import type { Message, MessageBatch } from "@cloudflare/workers-types";
import type { WorkerEnv } from "@/workers/config";
import { vi, afterEach } from "vitest";
import { createMockEnv } from "@/tests/settings";

// Import the queue handler and types
import routerMeteringQueue, {
  type RouterMeteringMessage,
  RouterMeteringQueueService,
  routerMeteringQueueLayer,
  setRouterMeteringQueueLayer,
  updateAndSettleRouterRequest,
} from "./routerMeteringQueue";

// =============================================================================
// Test Helpers
// =============================================================================

/**
 * Creates a mock message with retry tracking.
 */
function createMockMessage(
  body: RouterMeteringMessage,
): Message<RouterMeteringMessage> & {
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
  return mockMessage as unknown as Message<RouterMeteringMessage> & {
    retryCalled: boolean;
    retryOptions?: { delaySeconds: number };
  };
}

/**
 * Creates a mock message batch.
 */
function createMockBatch(
  messages: Message<RouterMeteringMessage>[],
): MessageBatch<RouterMeteringMessage> {
  return {
    messages,
    queue: "router-metering",
    ackAll: vi.fn(),
    retryAll: vi.fn(),
  } as MessageBatch<RouterMeteringMessage>;
}

/**
 * Creates a valid test metering message.
 */
function createTestMessage(
  overrides: Partial<RouterMeteringMessage> = {},
): RouterMeteringMessage {
  return {
    routerRequestId: "test-router-request-id",
    reservationId: "test-reservation-id",
    request: {
      userId: "test-user-id",
      organizationId: "test-org-id",
      projectId: "test-project-id",
      environmentId: "test-env-id",
      apiKeyId: "test-api-key-id",
      routerRequestId: "test-router-request-id",
    },
    usage: {
      inputTokens: 100,
      outputTokens: 50,
    },
    costCenticents: 150,
    timestamp: Date.now(),
    ...overrides,
  };
}

// =============================================================================
// Tests
// =============================================================================

describe("routerMeteringQueue", () => {
  const originalRouterMeteringQueueLayer = routerMeteringQueueLayer;

  afterEach(() => {
    setRouterMeteringQueueLayer(originalRouterMeteringQueueLayer);
  });

  describe("routerMeteringQueueLayer", () => {
    it("uses the default layer and allows updates", async () => {
      const originalLayer = routerMeteringQueueLayer;
      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* RouterMeteringQueueService;
        yield* queue.send(testMessage);
      });

      await expect(
        Effect.runPromise(
          program.pipe(Effect.provide(routerMeteringQueueLayer)),
        ),
      ).rejects.toThrow("RouterMeteringQueue not initialized");

      const testLayer = Layer.succeed(RouterMeteringQueueService, {
        send: () => Effect.void,
      });
      setRouterMeteringQueueLayer(testLayer);
      expect(routerMeteringQueueLayer).toBe(testLayer);

      setRouterMeteringQueueLayer(originalLayer);
    });
  });

  describe("updateAndSettleRouterRequest", () => {
    it("successfully updates router request and settles funds", async () => {
      const message = createTestMessage();

      // Mock the update and settleFunds functions
      const updateMock = vi.fn().mockReturnValue(Effect.succeed(undefined));
      const settleFundsMock = vi
        .fn()
        .mockReturnValue(Effect.succeed(undefined));

      // Create proper mock layers using Layer.succeed with partial implementations
      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            settleFunds: settleFundsMock,
          },
        },
      } as never);

      await Effect.runPromise(
        updateAndSettleRouterRequest(message, 150n).pipe(
          Effect.provide(Layer.merge(mockDbLayer, mockPaymentsLayer)),
        ),
      );

      // Verify database update was called
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: message.request.userId,
          organizationId: message.request.organizationId,
          routerRequestId: message.routerRequestId,
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          data: expect.objectContaining({
            inputTokens: 100n,
            outputTokens: 50n,
            costCenticents: 150n,
            status: "success",
          }),
        }),
      );

      // Verify settleFunds was called
      expect(settleFundsMock).toHaveBeenCalledWith(message.reservationId, 150n);
    });

    it("handles undefined token fields by setting them to null", async () => {
      const message = createTestMessage({
        usage: {
          inputTokens: 100,
          // @ts-expect-error checking an error case that goes against the type hints
          outputTokens: undefined,
          cacheReadTokens: undefined,
          cacheWriteTokens: undefined,
        },
      });

      // Mock the update and settleFunds functions
      const updateMock = vi.fn().mockReturnValue(Effect.succeed(undefined));
      const settleFundsMock = vi
        .fn()
        .mockReturnValue(Effect.succeed(undefined));

      // Create proper mock layers using Layer.succeed with partial implementations
      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            settleFunds: settleFundsMock,
          },
        },
      } as never);

      await Effect.runPromise(
        updateAndSettleRouterRequest(message, 150n).pipe(
          Effect.provide(Layer.merge(mockDbLayer, mockPaymentsLayer)),
        ),
      );

      // Verify database update was called with null for undefined fields
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: message.request.userId,
          organizationId: message.request.organizationId,
          routerRequestId: message.routerRequestId,
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          data: expect.objectContaining({
            inputTokens: 100n,
            outputTokens: null,
            cacheReadTokens: null,
            cacheWriteTokens: null,
            costCenticents: 150n,
            status: "success",
          }),
        }),
      );

      // Verify settleFunds was called
      expect(settleFundsMock).toHaveBeenCalledWith(message.reservationId, 150n);
    });

    it("handles all token fields as undefined by setting them to null", async () => {
      const message = createTestMessage({
        usage: {
          // @ts-expect-error checking an error case that goes against the type hints
          inputTokens: undefined,
          // @ts-expect-error checking an error case that goes against the type hints
          outputTokens: undefined,
          cacheReadTokens: undefined,
          cacheWriteTokens: undefined,
        },
        costCenticents: 0,
      });

      // Mock the update and settleFunds functions
      const updateMock = vi.fn().mockReturnValue(Effect.succeed(undefined));
      const settleFundsMock = vi
        .fn()
        .mockReturnValue(Effect.succeed(undefined));

      // Create proper mock layers using Layer.succeed with partial implementations
      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            settleFunds: settleFundsMock,
          },
        },
      } as never);

      await Effect.runPromise(
        updateAndSettleRouterRequest(message, 0n).pipe(
          Effect.provide(Layer.merge(mockDbLayer, mockPaymentsLayer)),
        ),
      );

      // Verify database update was called with all null token fields
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: message.request.userId,
          organizationId: message.request.organizationId,
          routerRequestId: message.routerRequestId,
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          data: expect.objectContaining({
            inputTokens: null,
            outputTokens: null,
            cacheReadTokens: null,
            cacheWriteTokens: null,
            costCenticents: 0n,
            status: "success",
          }),
        }),
      );

      // Verify settleFunds was called
      expect(settleFundsMock).toHaveBeenCalledWith(message.reservationId, 0n);
    });

    it("handles cache token fields when present", async () => {
      const message = createTestMessage({
        usage: {
          inputTokens: 100,
          outputTokens: 50,
          cacheReadTokens: 20,
          cacheWriteTokens: 10,
          cacheWriteBreakdown: { foo: 5, bar: 5 },
        },
      });

      // Mock the update and settleFunds functions
      const updateMock = vi.fn().mockReturnValue(Effect.succeed(undefined));
      const settleFundsMock = vi
        .fn()
        .mockReturnValue(Effect.succeed(undefined));

      // Create proper mock layers using Layer.succeed with partial implementations
      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            settleFunds: settleFundsMock,
          },
        },
      } as never);

      await Effect.runPromise(
        updateAndSettleRouterRequest(message, 150n).pipe(
          Effect.provide(Layer.merge(mockDbLayer, mockPaymentsLayer)),
        ),
      );

      // Verify database update was called with cache tokens as bigints
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          userId: message.request.userId,
          organizationId: message.request.organizationId,
          routerRequestId: message.routerRequestId,
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          data: expect.objectContaining({
            inputTokens: 100n,
            outputTokens: 50n,
            cacheReadTokens: 20n,
            cacheWriteTokens: 10n,
            cacheWriteBreakdown: { foo: 5, bar: 5 },
            costCenticents: 150n,
            status: "success",
          }),
        }),
      );

      // Verify settleFunds was called
      expect(settleFundsMock).toHaveBeenCalledWith(message.reservationId, 150n);
    });
  });

  describe("RouterMeteringQueueService", () => {
    it("Live method creates working service layer", async () => {
      const mockQueue = {
        send: vi.fn().mockResolvedValue(undefined),
      };

      const layer = RouterMeteringQueueService.Live(mockQueue);

      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* RouterMeteringQueueService;
        yield* queue.send(testMessage);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      expect(mockQueue.send).toHaveBeenCalledWith(testMessage);
    });

    it("Live method handles send failures", async () => {
      const mockQueue = {
        send: vi.fn().mockRejectedValue(new Error("Queue send failed")),
      };

      const layer = RouterMeteringQueueService.Live(mockQueue);

      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* RouterMeteringQueueService;
        yield* queue.send(testMessage);
      });

      await expect(
        Effect.runPromise(program.pipe(Effect.provide(layer))),
      ).rejects.toThrow("Failed to enqueue metering");
    });
  });

  describe("global layer", () => {
    it("fails when global layer is not initialized", async () => {
      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* RouterMeteringQueueService;
        yield* queue.send(testMessage);
      });

      const error = await Effect.runPromise(
        program.pipe(Effect.provide(routerMeteringQueueLayer), Effect.flip),
      );

      expect(error).toBeInstanceOf(Error);
      expect(error.message).toBe("RouterMeteringQueue not initialized");
    });

    it("setRouterMeteringQueueLayer updates the global layer", async () => {
      const testMessage = createTestMessage();
      const send = vi.fn(() => Effect.void);
      const layer = Layer.succeed(RouterMeteringQueueService, { send });

      setRouterMeteringQueueLayer(layer);

      const program = Effect.gen(function* () {
        const queue = yield* RouterMeteringQueueService;
        yield* queue.send(testMessage);
      });

      await Effect.runPromise(
        program.pipe(Effect.provide(routerMeteringQueueLayer)),
      );

      expect(send).toHaveBeenCalledWith(testMessage);
    });
  });

  describe("configuration validation", () => {
    it("retries when DATABASE_URL is missing", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);
      const env = {
        ENVIRONMENT: "test",
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
        // DATABASE_URL is missing
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
    });

    it("retries when STRIPE_SECRET_KEY is missing", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);
      const env = {
        ENVIRONMENT: "test",
        DATABASE_URL: "postgresql://test:test@localhost:5432/test",
        // STRIPE_SECRET_KEY is missing
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
    });

    it("retries when STRIPE_ROUTER_PRICE_ID is missing", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);
      const env = {
        ENVIRONMENT: "test",
        DATABASE_URL: "postgresql://test:test@localhost:5432/test",
        STRIPE_SECRET_KEY: "sk_test_xxx",
        // STRIPE_ROUTER_PRICE_ID is missing
        STRIPE_ROUTER_METER_ID: "meter_xxx",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
    });

    it("retries when STRIPE_ROUTER_METER_ID is missing", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);
      const env = {
        ENVIRONMENT: "test",
        DATABASE_URL: "postgresql://test:test@localhost:5432/test",
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        // STRIPE_ROUTER_METER_ID is missing
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
    });

    it("processes message with minimal config (undefined optional cloud env vars)", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);
      const env = {
        ENVIRONMENT: "test",
        DATABASE_URL: "postgresql://test:test@localhost:5432/test",
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);
    });
  });

  describe("batch processing", () => {
    it("processes multiple messages in batch", async () => {
      const message1 = createMockMessage(createTestMessage());
      const message2 = createMockMessage(createTestMessage());
      const batch = createMockBatch([message1, message2]);

      // Create env without DB - will trigger retry for config validation
      const env = {
        ENVIRONMENT: "test",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      // Both messages should have retry called due to missing config
      expect(message1.retryCalled).toBe(true);
      expect(message2.retryCalled).toBe(true);
    });

    it("logs batch size when processing", async () => {
      const consoleLogSpy = vi
        .spyOn(console, "log")
        .mockImplementation(() => {});

      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);
      const env = {
        ENVIRONMENT: "test",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      expect(consoleLogSpy).toHaveBeenCalledWith(
        "[routerMeteringQueue] Processing 1 messages",
      );

      consoleLogSpy.mockRestore();
    });
  });

  describe("HYPERDRIVE support", () => {
    it("uses HYPERDRIVE connection string when available", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);
      const env = {
        ENVIRONMENT: "test",
        HYPERDRIVE: {
          connectionString: "postgresql://hyperdrive:xxx@localhost:5432/test",
        },
        // DATABASE_URL not needed when HYPERDRIVE is present
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      // Should not log "No database connection available" error
      expect(consoleErrorSpy).not.toHaveBeenCalledWith(
        expect.stringContaining("No database connection available"),
      );

      // Should have retried due to DB connection error (not config error)
      expect(message.retryCalled).toBe(true);

      consoleErrorSpy.mockRestore();
    });
  });

  describe("message processing with database", () => {
    it("processes message with complete Settings environment", async () => {
      // Test with complete Settings to cover the Settings success path (lines 175-184)
      const meteringMessage = createTestMessage({
        usage: {
          inputTokens: 100,
          outputTokens: 50,
        },
        costCenticents: 150,
      });

      const message = createMockMessage(meteringMessage);
      const batch = createMockBatch([message]);

      // Use createMockEnv to get a complete environment that passes Settings validation
      const completeEnv = createMockEnv({
        DATABASE_URL: TEST_DATABASE_URL,
      });
      const env = completeEnv as unknown as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      // Will retry due to DB error (router request not found), but Settings validation passes
      expect(message.retryCalled).toBe(true);
    });

    it("processes message with all token fields", async () => {
      // Test with all token fields populated to cover more branches
      const meteringMessage = createTestMessage({
        usage: {
          inputTokens: 100,
          outputTokens: 50,
          cacheReadTokens: 20,
          cacheWriteTokens: 10,
          cacheWriteBreakdown: { foo: 5, bar: 5 },
        },
        costCenticents: 150,
      });

      const message = createMockMessage(meteringMessage);
      const batch = createMockBatch([message]);

      const env = {
        ENVIRONMENT: "test",
        DATABASE_URL: TEST_DATABASE_URL,
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      // Will retry due to missing data in worker's separate DB connection
      expect(message.retryCalled).toBe(true);
    });

    it("processes message with costCenticents as bigint", async () => {
      // Test with costCenticents as bigint to cover that branch
      const meteringMessage = createTestMessage({
        usage: {
          inputTokens: 100,
          outputTokens: 50,
        },
        costCenticents: 150,
      });

      // Override costCenticents to be a bigint
      (
        meteringMessage as unknown as { costCenticents: bigint }
      ).costCenticents = 150n;

      const message = createMockMessage(meteringMessage);
      const batch = createMockBatch([message]);

      const env = {
        ENVIRONMENT: "test",
        DATABASE_URL: TEST_DATABASE_URL,
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      // Will retry due to missing data in worker's separate DB connection
      expect(message.retryCalled).toBe(true);
    });

    it("processes message with null token fields", async () => {
      // Test with minimal token fields to cover null branches
      const meteringMessage = createTestMessage({
        usage: {
          inputTokens: 0,
          outputTokens: 0,
        },
        costCenticents: 0,
      });

      const message = createMockMessage(meteringMessage);
      const batch = createMockBatch([message]);

      const env = {
        ENVIRONMENT: "test",
        DATABASE_URL: TEST_DATABASE_URL,
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      // Will retry due to missing data in worker's separate DB connection
      expect(message.retryCalled).toBe(true);
    });

    it("processes message with some undefined token fields", async () => {
      // Test with only some token fields to cover all null branches in ternaries
      const meteringMessage = createTestMessage({
        usage: {
          inputTokens: 100,
          outputTokens: 50,
          // cacheReadTokens and cacheWriteTokens are undefined
        },
        costCenticents: 150,
      });

      const message = createMockMessage(meteringMessage);
      const batch = createMockBatch([message]);

      const env = {
        ENVIRONMENT: "test",
        DATABASE_URL: TEST_DATABASE_URL,
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      // Will retry due to missing data in worker's separate DB connection
      expect(message.retryCalled).toBe(true);
    });
  });

  describe("error handling", () => {
    it("logs error and retries when updateAndSettleRouterRequest fails", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);

      // Environment with valid config but invalid DB connection
      const env = {
        ENVIRONMENT: "test",
        DATABASE_URL: "postgresql://invalid:invalid@localhost:5432/nonexistent",
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
      } as WorkerEnv;

      await routerMeteringQueue.queue(batch, env);

      // Should have logged error
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("[routerMeteringQueue] Error processing"),
        expect.anything(),
      );

      // Should have called retry
      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);

      consoleErrorSpy.mockRestore();
    });
  });

  describe("global layer", () => {
    it("default layer returns error when not initialized", async () => {
      const program = Effect.gen(function* () {
        const queue = yield* RouterMeteringQueueService;
        return yield* queue.send(createTestMessage());
      });

      const error = await Effect.runPromise(
        program.pipe(Effect.provide(routerMeteringQueueLayer), Effect.flip),
      );

      expect(error.message).toBe("RouterMeteringQueue not initialized");
    });

    it("setRouterMeteringQueueLayer updates the global layer", async () => {
      const mockSend = vi.fn().mockReturnValue(Effect.void);
      const newLayer = Layer.succeed(RouterMeteringQueueService, {
        send: mockSend,
      });

      setRouterMeteringQueueLayer(newLayer);

      const program = Effect.gen(function* () {
        const queue = yield* RouterMeteringQueueService;
        return yield* queue.send(createTestMessage());
      });

      await Effect.runPromise(
        program.pipe(Effect.provide(routerMeteringQueueLayer)),
      );

      expect(mockSend).toHaveBeenCalled();

      // Reset global layer to default
      setRouterMeteringQueueLayer(
        Layer.succeed(RouterMeteringQueueService, {
          send: () =>
            Effect.fail(new Error("RouterMeteringQueue not initialized")),
        }),
      );
    });
  });
});
