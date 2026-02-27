/**
 * E2E tests for exponential backoff delay behavior.
 *
 * Tests that backoff delays are correctly applied between retry attempts.
 */

import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
  type Mock,
} from "vitest";

import { retryModel } from "@/llm/retries/retry-model";
import * as utils from "@/llm/retries/utils";

import {
  setupMockProvider,
  teardownMockProvider,
  SERVER_ERROR,
  type MockProvider,
} from "./mock-provider";

// Mock sleep to avoid actual delays and track calls
vi.mock("@/llm/retries/utils", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/llm/retries/utils")>();
  return {
    ...actual,
    sleep: vi.fn().mockResolvedValue(undefined),
  };
});

describe("backoff delays", () => {
  let mockProvider: MockProvider;
  let sleepMock: Mock;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
    sleepMock = utils.sleep as Mock;
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("applies exponential backoff delays between retries", async () => {
    // Fail twice, then succeed
    mockProvider.setExceptions([SERVER_ERROR, SERVER_ERROR]);

    const model = retryModel("mock/test-model", {
      maxRetries: 3,
      initialDelay: 0.1,
      backoffMultiplier: 2.0,
      jitter: 0,
    });

    const response = await model.call("Hello");

    expect(response.retryFailures).toHaveLength(2);
    // Sleep should be called twice (after each failed attempt)
    expect(sleepMock).toHaveBeenCalledTimes(2);
    // First delay: 0.1s = 100ms, second delay: 0.2s = 200ms
    expect(sleepMock).toHaveBeenNthCalledWith(1, 100);
    expect(sleepMock).toHaveBeenNthCalledWith(2, 200);
  });

  it("caps delay at maxDelay", async () => {
    // Fail 3 times, then succeed
    mockProvider.setExceptions([SERVER_ERROR, SERVER_ERROR, SERVER_ERROR]);

    const model = retryModel("mock/test-model", {
      maxRetries: 4,
      initialDelay: 1.0,
      backoffMultiplier: 10.0,
      maxDelay: 5.0,
      jitter: 0,
    });

    const response = await model.call("Hello");

    expect(response.retryFailures).toHaveLength(3);
    // First: 1.0s = 1000ms
    // Second: min(10.0, 5.0) = 5.0s = 5000ms
    // Third: min(100.0, 5.0) = 5.0s = 5000ms
    expect(sleepMock).toHaveBeenCalledTimes(3);
    expect(sleepMock).toHaveBeenNthCalledWith(1, 1000);
    expect(sleepMock).toHaveBeenNthCalledWith(2, 5000);
    expect(sleepMock).toHaveBeenNthCalledWith(3, 5000);
  });

  it("applies jitter when configured", async () => {
    // Mock Math.random to return a predictable value (0.5 -> midpoint)
    const originalRandom = Math.random;
    Math.random = () => 0.5;

    try {
      mockProvider.setExceptions([SERVER_ERROR]);

      const model = retryModel("mock/test-model", {
        maxRetries: 2,
        initialDelay: 1.0,
        jitter: 0.5,
      });

      const response = await model.call("Hello");

      expect(response.retryFailures).toHaveLength(1);
      // With jitter=0.5 and Math.random returning 0.5:
      // jitter_range = 1.0 * 0.5 = 0.5
      // jitter = (0.5 * 2 - 1) * 0.5 = 0 * 0.5 = 0
      // delay = 1.0 + 0 = 1.0s = 1000ms
      expect(sleepMock).toHaveBeenCalledTimes(1);
      expect(sleepMock).toHaveBeenCalledWith(1000);
    } finally {
      Math.random = originalRandom;
    }
  });

  it("applies no delay when initialDelay is 0", async () => {
    mockProvider.setExceptions([SERVER_ERROR]);

    const model = retryModel("mock/test-model", {
      maxRetries: 2,
      initialDelay: 0,
    });

    const response = await model.call("Hello");

    expect(response.retryFailures).toHaveLength(1);
    expect(sleepMock).toHaveBeenCalledTimes(1);
    expect(sleepMock).toHaveBeenCalledWith(0);
  });

  it("sleep is called between retry attempts", async () => {
    mockProvider.setExceptions([SERVER_ERROR]);

    const model = retryModel("mock/test-model", {
      maxRetries: 2,
      initialDelay: 0.5,
      jitter: 0,
    });

    await model.call("Hello");

    // Sleep should be called once (after the failed attempt)
    expect(sleepMock).toHaveBeenCalledTimes(1);
    // 0.5s = 500ms
    expect(sleepMock).toHaveBeenCalledWith(500);
  });
});
