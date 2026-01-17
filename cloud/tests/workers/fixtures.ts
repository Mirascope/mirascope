/**
 * @fileoverview Shared queue message fixtures for worker tests.
 */

import type { Message, MessageBatch } from "@cloudflare/workers-types";
import { vi } from "vitest";

export type RetryTrackingMessage<T> = Message<T> & {
  retryCalled: boolean;
  retryOptions?: { delaySeconds: number };
};

/**
 * Creates a mock queue message with retry tracking.
 */
export const createMockQueueMessage = <T>(body: T): RetryTrackingMessage<T> => {
  const mockMessage = {
    body,
    id: "test-message-id",
    timestamp: new Date(),
    attempts: 1,
    retryCalled: false,
    retryOptions: undefined as { delaySeconds: number } | undefined,
    ack: vi.fn(),
    retry: vi.fn((options?: { delaySeconds: number }) => {
      mockMessage.retryCalled = true;
      mockMessage.retryOptions = options;
    }),
  };
  return mockMessage as unknown as RetryTrackingMessage<T>;
};

/**
 * Creates a mock queue message batch.
 */
export const createMockQueueBatch = <T>(
  messages: Message<T>[],
  queue = "test-queue",
): MessageBatch<T> =>
  ({
    messages,
    queue,
    ackAll: vi.fn(),
    retryAll: vi.fn(),
  }) as unknown as MessageBatch<T>;
