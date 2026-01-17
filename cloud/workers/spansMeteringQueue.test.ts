/**
 * @fileoverview Tests for spans metering queue consumer.
 */

import { describe, expect, vi, it } from "vitest";
import { Effect, Layer } from "effect";
import { Payments } from "@/payments";
import type { Message, MessageBatch } from "@cloudflare/workers-types";
import type { WorkerEnv } from "@/workers/config";
import { createMockEnv } from "@/tests/settings";

const TEST_DATABASE_URL = "postgres://test:test@localhost:5432/test";

// Import the queue handler and types
import spansMeteringQueue, {
  type SpanMeteringMessage,
  SpansMeteringQueueService,
  chargeSpanMeter,
} from "./spansMeteringQueue";

// =============================================================================
// Test Helpers
// =============================================================================

/**
 * Creates a mock message with retry tracking.
 */
function createMockMessage(
  body: SpanMeteringMessage,
): Message<SpanMeteringMessage> & {
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
  return mockMessage as unknown as Message<SpanMeteringMessage> & {
    retryCalled: boolean;
    retryOptions?: { delaySeconds: number };
  };
}

/**
 * Creates a mock message batch.
 */
function createMockBatch(
  messages: Message<SpanMeteringMessage>[],
): MessageBatch<SpanMeteringMessage> {
  return {
    messages,
    queue: "spans-metering",
    ackAll: vi.fn(),
    retryAll: vi.fn(),
  } as unknown as MessageBatch<SpanMeteringMessage>;
}

/**
 * Creates a valid test metering message.
 */
function createTestMessage(
  overrides: Partial<SpanMeteringMessage> = {},
): SpanMeteringMessage {
  return {
    spanId: "test-span-id",
    organizationId: "test-org-id",
    projectId: "test-project-id",
    environmentId: "test-env-id",
    stripeCustomerId: "cus_test123",
    timestamp: Date.now(),
    ...overrides,
  };
}

// =============================================================================
// Tests
// =============================================================================

describe("Spans Metering Queue", () => {
  describe("chargeSpanMeter", () => {
    it("charges the spans meter for the customer", async () => {
      const message = createTestMessage();

      // Create a mock to capture the call
      let capturedParams: {
        stripeCustomerId: string;
        spanId: string;
      } | null = null;

      const MockPaymentsLayer = Layer.succeed(Payments, {
        customers: {} as never,
        products: {
          router: {} as never,
          spans: {
            chargeMeter: (params) => {
              capturedParams = params;
              return Effect.succeed(undefined);
            },
            getUsageMeterBalance: () => Effect.succeed(0n),
            checkSpanLimit: () => Effect.succeed(undefined),
          },
        },
        paymentIntents: {} as never,
      });

      await Effect.runPromise(
        chargeSpanMeter(message).pipe(Effect.provide(MockPaymentsLayer)),
      );

      // Verify the meter was charged with correct parameters
      expect(capturedParams).toEqual({
        stripeCustomerId: message.stripeCustomerId,
        spanId: message.spanId,
      });
    });
  });

  describe("SpansMeteringQueueService", () => {
    it("Live method creates working service layer", async () => {
      const mockQueue = {
        send: vi.fn().mockResolvedValue(undefined),
      };

      const layer = SpansMeteringQueueService.Live(mockQueue);

      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* SpansMeteringQueueService;
        yield* queue.send(testMessage);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      expect(mockQueue.send).toHaveBeenCalledWith(testMessage);
    });

    it("handles send errors properly", async () => {
      const mockQueue = {
        send: vi.fn().mockRejectedValue(new Error("Queue send failed")),
      };

      const layer = SpansMeteringQueueService.Live(mockQueue);

      const testMessage = createTestMessage();

      const program = Effect.gen(function* () {
        const queue = yield* SpansMeteringQueueService;
        return yield* queue.send(testMessage);
      });

      const result = await Effect.runPromise(
        program.pipe(Effect.provide(layer), Effect.either),
      );

      expect(result._tag).toBe("Left");
      if (result._tag === "Left") {
        expect(result.left.message).toContain(
          "Failed to enqueue span metering",
        );
      }
    });
  });

  describe("queue handler", () => {
    it("processes message with complete Settings environment", async () => {
      // Test with complete Settings to cover the Settings success path (lines 132-141)
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);

      // Use createMockEnv to get a complete environment that passes Settings validation
      const completeEnv = createMockEnv({
        DATABASE_URL: TEST_DATABASE_URL,
      });
      const env = completeEnv as unknown as WorkerEnv;

      await spansMeteringQueue.queue(batch, env);

      // Will retry due to DB/Stripe error, but Settings validation passes
      expect(message.retryCalled).toBe(true);
    });

    it("retries when DATABASE_URL is missing", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);

      const env: WorkerEnv = {
        ENVIRONMENT: "test",
      } as never;

      await spansMeteringQueue.queue(batch, env);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
    });

    it("retries when Stripe configuration is missing", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);

      const env: WorkerEnv = {
        ENVIRONMENT: "test",
        DATABASE_URL: TEST_DATABASE_URL,
        // Missing STRIPE_CLOUD_SPANS_METER_ID
        STRIPE_SECRET_KEY: "sk_test_123",
        STRIPE_CLOUD_SPANS_PRICE_ID: "price_123",
      } as never;

      await spansMeteringQueue.queue(batch, env);

      expect(message.retryCalled).toBe(true);
      expect(message.retryOptions?.delaySeconds).toBe(60);
    });

    it("processes message with valid configuration (triggers retry on DB error)", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);

      const env: WorkerEnv = {
        ENVIRONMENT: "test",
        DATABASE_URL: TEST_DATABASE_URL,
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_ROUTER_PRICE_ID: "price_xxx",
        STRIPE_ROUTER_METER_ID: "meter_xxx",
        STRIPE_CLOUD_FREE_PRICE_ID: "price_free",
        STRIPE_CLOUD_PRO_PRICE_ID: "price_pro",
        STRIPE_CLOUD_TEAM_PRICE_ID: "price_team",
        STRIPE_CLOUD_SPANS_PRICE_ID: "price_spans",
        STRIPE_CLOUD_SPANS_METER_ID: "meter_spans",
      } as WorkerEnv;

      await spansMeteringQueue.queue(batch, env);

      // Will retry due to database connection error in test environment
      expect(message.retryCalled).toBe(true);
    });

    it("processes message with minimal config (undefined optional env vars)", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);

      // Only required env vars, optional ones are undefined (test fallback branches)
      const env: WorkerEnv = {
        ENVIRONMENT: "test",
        DATABASE_URL: TEST_DATABASE_URL,
        STRIPE_SECRET_KEY: "sk_test_xxx",
        // STRIPE_ROUTER_PRICE_ID is undefined - tests fallback branch
        // STRIPE_ROUTER_METER_ID is undefined - tests fallback branch
        // STRIPE_CLOUD_FREE_PRICE_ID is undefined - tests fallback branch
        // STRIPE_CLOUD_PRO_PRICE_ID is undefined - tests fallback branch
        // STRIPE_CLOUD_TEAM_PRICE_ID is undefined - tests fallback branch
        STRIPE_CLOUD_SPANS_PRICE_ID: "price_spans",
        STRIPE_CLOUD_SPANS_METER_ID: "meter_spans",
      } as WorkerEnv;

      await spansMeteringQueue.queue(batch, env);

      // Will retry due to database connection error in test environment
      expect(message.retryCalled).toBe(true);
    });

    it("processes message with undefined STRIPE_SECRET_KEY fallback", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);

      // Explicitly set STRIPE_SECRET_KEY to undefined to test line 149 fallback
      const env: WorkerEnv = {
        ENVIRONMENT: "test",
        DATABASE_URL: TEST_DATABASE_URL,
        STRIPE_SECRET_KEY: undefined as unknown as string,
        STRIPE_CLOUD_SPANS_PRICE_ID: "price_spans",
        STRIPE_CLOUD_SPANS_METER_ID: "meter_spans",
      } as WorkerEnv;

      await spansMeteringQueue.queue(batch, env);

      // Should retry due to missing STRIPE_SECRET_KEY in validation
      expect(message.retryCalled).toBe(true);
    });

    it("processes message with undefined cloud spans config fallback", async () => {
      const message = createMockMessage(createTestMessage());
      const batch = createMockBatch([message]);

      // Explicitly set cloud spans env vars to undefined to test lines 155-156 fallback
      const env: WorkerEnv = {
        ENVIRONMENT: "test",
        DATABASE_URL: TEST_DATABASE_URL,
        STRIPE_SECRET_KEY: "sk_test_xxx",
        STRIPE_CLOUD_SPANS_PRICE_ID: undefined as unknown as string,
        STRIPE_CLOUD_SPANS_METER_ID: undefined as unknown as string,
      } as WorkerEnv;

      await spansMeteringQueue.queue(batch, env);

      // Should retry due to missing cloud spans config in validation
      expect(message.retryCalled).toBe(true);
    });

    it("processes multiple messages in batch", async () => {
      const message1 = createMockMessage(createTestMessage());
      const message2 = createMockMessage(createTestMessage());
      const batch = createMockBatch([message1, message2]);

      // Create env without DB - will trigger retry for config validation
      const env = {
        ENVIRONMENT: "test",
      } as WorkerEnv;

      await spansMeteringQueue.queue(batch, env);

      // Both messages should be retried
      expect(message1.retryCalled).toBe(true);
      expect(message2.retryCalled).toBe(true);
    });
  });
});
