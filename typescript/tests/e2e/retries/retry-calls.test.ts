/**
 * E2E tests for retry call behavior.
 *
 * Tests the complete retry flow with mock providers for deterministic testing.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createContext } from "@/llm/context";
import { RetriesExhausted } from "@/llm/exceptions";
import { withModel } from "@/llm/models/model-context";
import { RetryConfig } from "@/llm/retries/retry-config";
import { RetryModel, retryModel } from "@/llm/retries/retry-model";
import {
  RetryResponse,
  ContextRetryResponse,
} from "@/llm/retries/retry-responses";
import { ContextRetryStreamResponse } from "@/llm/retries/retry-stream-responses";
import * as utils from "@/llm/retries/utils";

import {
  setupMockProvider,
  teardownMockProvider,
  SERVER_ERROR,
  CONNECTION_ERROR,
  RATE_LIMIT_ERROR,
  TIMEOUT_ERROR,
  DEFAULT_RETRYABLE_EXCEPTIONS,
  type MockProvider,
} from "./mock-provider";

// Mock sleep to avoid actual delays in tests
vi.mock("@/llm/retries/utils", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/llm/retries/utils")>();
  return {
    ...actual,
    sleep: vi.fn().mockResolvedValue(undefined),
  };
});

describe("RetryModel call", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  describe("successful calls", () => {
    it("returns RetryResponse on first attempt success", async () => {
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.call("Hello");

      expect(response).toBeInstanceOf(RetryResponse);
      expect(response.text()).toBe("mock response");
      expect(response.retryFailures).toHaveLength(0);
      expect(mockProvider.callCount).toBe(1);
    });

    it("preserves model params in response", async () => {
      const model = retryModel("mock/test-model", {
        temperature: 0.5,
        maxTokens: 100,
      });

      const response = await model.call("Hello");

      expect(response.params).toEqual({ temperature: 0.5, maxTokens: 100 });
    });
  });

  describe("retries on default exceptions", () => {
    it("retries on ServerError", async () => {
      mockProvider.setExceptions([SERVER_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.call("Hello");

      expect(response.retryFailures).toHaveLength(1);
      expect(response.retryFailures[0]?.exception).toBe(SERVER_ERROR);
      expect(mockProvider.callCount).toBe(2);
    });

    it("retries on ConnectionError", async () => {
      mockProvider.setExceptions([CONNECTION_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.call("Hello");

      expect(response.retryFailures).toHaveLength(1);
      expect(response.retryFailures[0]?.exception).toBe(CONNECTION_ERROR);
    });

    it("retries on RateLimitError", async () => {
      mockProvider.setExceptions([RATE_LIMIT_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.call("Hello");

      expect(response.retryFailures).toHaveLength(1);
      expect(response.retryFailures[0]?.exception).toBe(RATE_LIMIT_ERROR);
    });

    it("retries on TimeoutError", async () => {
      mockProvider.setExceptions([TIMEOUT_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      const response = await model.call("Hello");

      expect(response.retryFailures).toHaveLength(1);
      expect(response.retryFailures[0]?.exception).toBe(TIMEOUT_ERROR);
    });

    it("retries on all default retryable exceptions", async () => {
      mockProvider.setExceptions(DEFAULT_RETRYABLE_EXCEPTIONS);
      const model = retryModel("mock/test-model", { maxRetries: 4 });

      const response = await model.call("Hello");

      expect(response.retryFailures).toHaveLength(4);
      expect(mockProvider.callCount).toBe(5);
    });
  });

  describe("exhausted retries", () => {
    it("throws RetriesExhausted when all retries fail", async () => {
      mockProvider.setExceptions([SERVER_ERROR, SERVER_ERROR, SERVER_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 2 });

      await expect(model.call("Hello")).rejects.toThrow(RetriesExhausted);
    });

    it("RetriesExhausted contains all failures", async () => {
      mockProvider.setExceptions([
        SERVER_ERROR,
        CONNECTION_ERROR,
        RATE_LIMIT_ERROR,
      ]);
      const model = retryModel("mock/test-model", { maxRetries: 2 });

      try {
        await model.call("Hello");
        expect.fail("Should have thrown");
      } catch (e) {
        expect(e).toBeInstanceOf(RetriesExhausted);
        const exhausted = e as RetriesExhausted;
        expect(exhausted.failures).toHaveLength(3);
        expect(exhausted.failures[0]?.exception).toBe(SERVER_ERROR);
        expect(exhausted.failures[1]?.exception).toBe(CONNECTION_ERROR);
        expect(exhausted.failures[2]?.exception).toBe(RATE_LIMIT_ERROR);
      }
    });

    it("RetriesExhausted.cause is the last exception", async () => {
      mockProvider.setExceptions([SERVER_ERROR, RATE_LIMIT_ERROR]);
      const model = retryModel("mock/test-model", { maxRetries: 1 });

      try {
        await model.call("Hello");
        expect.fail("Should have thrown");
      } catch (e) {
        expect(e).toBeInstanceOf(RetriesExhausted);
        expect((e as RetriesExhausted).cause).toBe(RATE_LIMIT_ERROR);
      }
    });
  });

  describe("non-retryable errors", () => {
    it("throws non-retryable errors immediately", async () => {
      const nonRetryable = new Error("non-retryable");
      mockProvider.setExceptions([nonRetryable]);
      const model = retryModel("mock/test-model", { maxRetries: 3 });

      await expect(model.call("Hello")).rejects.toBe(nonRetryable);
      expect(mockProvider.callCount).toBe(1);
    });
  });

  describe("backoff behavior", () => {
    it("applies sleep between retries", async () => {
      mockProvider.setExceptions([SERVER_ERROR, SERVER_ERROR]);
      const model = retryModel("mock/test-model", {
        maxRetries: 3,
        initialDelay: 1.0,
      });

      await model.call("Hello");

      expect(utils.sleep).toHaveBeenCalled();
    });
  });
});

describe("RetryModel contextCall", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("returns ContextRetryResponse on success", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({ userId: "123" });

    const response = await model.contextCall(ctx, "Hello");

    expect(response).toBeInstanceOf(ContextRetryResponse);
    expect(response.text()).toBe("mock response");
    expect(response.retryFailures).toHaveLength(0);
  });

  it("retries on retryable error", async () => {
    mockProvider.setExceptions([SERVER_ERROR]);
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({});

    const response = await model.contextCall(ctx, "Hello");

    expect(response.retryFailures).toHaveLength(1);
    expect(mockProvider.callCount).toBe(2);
  });

  it("throws RetriesExhausted when all retries fail", async () => {
    mockProvider.setExceptions([SERVER_ERROR, SERVER_ERROR, SERVER_ERROR]);
    const model = retryModel("mock/test-model", { maxRetries: 2 });
    const ctx = createContext({});

    await expect(model.contextCall(ctx, "Hello")).rejects.toThrow(
      RetriesExhausted,
    );
  });
});

describe("retryModel helper", () => {
  beforeEach(() => {
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("creates a RetryModel with model ID", () => {
    const model = retryModel("mock/test-model");

    expect(model).toBeInstanceOf(RetryModel);
    expect(model.modelId).toBe("mock/test-model");
  });

  it("separates retry args from model params", () => {
    const model = retryModel("mock/test-model", {
      temperature: 0.5,
      maxTokens: 100,
      maxRetries: 5,
      initialDelay: 2.0,
    });

    expect(model.params).toEqual({ temperature: 0.5, maxTokens: 100 });
    expect(model.retryConfig.maxRetries).toBe(5);
    expect(model.retryConfig.initialDelay).toBe(2.0);
  });

  it("uses default retry config when no retry args provided", () => {
    const model = retryModel("mock/test-model");

    expect(model.retryConfig.maxRetries).toBe(3);
  });
});

describe("RetryModel construction", () => {
  beforeEach(() => {
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("creates RetryModel with RetryConfig", () => {
    const config = new RetryConfig({ maxRetries: 5 });
    const model = new RetryModel("mock/test-model", config);

    expect(model.modelId).toBe("mock/test-model");
    expect(model.retryConfig.maxRetries).toBe(5);
  });

  it("inherits params when wrapping a Model", async () => {
    const { Model } = await import("@/llm/models");
    const baseModel = new Model("mock/test-model", { temperature: 0.7 });
    const config = new RetryConfig();
    const model = new RetryModel(baseModel, config);

    expect(model.params).toEqual({ temperature: 0.7 });
  });

  it("getActiveModel returns a plain Model", async () => {
    const { Model } = await import("@/llm/models");
    const config = new RetryConfig();
    const model = new RetryModel("mock/test-model", config);

    const active = model.getActiveModel();

    expect(active).toBeInstanceOf(Model);
    expect(active).not.toBeInstanceOf(RetryModel);
  });

  it("strips nested RetryModel when wrapping", async () => {
    const { Model } = await import("@/llm/models");
    // Create a RetryModel
    const innerRetryModel = retryModel("mock/inner-model", { maxRetries: 2 });
    // Wrap it in another RetryModel
    const outerModel = new RetryModel(
      innerRetryModel,
      new RetryConfig({ maxRetries: 3 }),
    );

    // The active model should be a plain Model, not a RetryModel
    const active = outerModel.getActiveModel();
    expect(active).toBeInstanceOf(Model);
    expect(active).not.toBeInstanceOf(RetryModel);
    expect(active.modelId).toBe("mock/inner-model");
  });
});

describe("RetryModel resume methods", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("resume returns RetryResponse", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const initialResponse = await model.call("Hello");

    const followUp = await model.resume(initialResponse, "Follow up");

    expect(followUp).toBeInstanceOf(RetryResponse);
    expect(mockProvider.callCount).toBe(2);
  });

  it("resume retries on error", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const initialResponse = await model.call("Hello");
    mockProvider.setExceptions([SERVER_ERROR]); // Resume call fails first time

    const followUp = await model.resume(initialResponse, "Follow up");

    expect(followUp.retryFailures).toHaveLength(1);
  });

  it("contextResume returns ContextRetryResponse", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({ userId: "123" });
    const initialResponse = await model.contextCall(ctx, "Hello");

    const followUp = await model.contextResume(
      ctx,
      initialResponse,
      "Follow up",
    );

    expect(followUp).toBeInstanceOf(ContextRetryResponse);
  });

  it("contextResumeStream returns ContextRetryStreamResponse", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({ userId: "123" });
    const initialResponse = await model.contextCall(ctx, "Hello");

    const followUp = await model.contextResumeStream(
      ctx,
      initialResponse,
      "Follow up",
    );

    expect(followUp).toBeInstanceOf(ContextRetryStreamResponse);
    // Consume stream
    for await (const _text of followUp.textStream()) {
      // consume
    }
  });
});

describe("RetryResponse.model property", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("returns RetryModel with same config", async () => {
    const model = retryModel("mock/test-model", {
      maxRetries: 5,
      initialDelay: 2.0,
    });

    const response = await model.call("Hello");
    const responseModel = await response.model;

    expect(responseModel).toBeInstanceOf(RetryModel);
    expect(responseModel.retryConfig.maxRetries).toBe(5);
    expect(responseModel.retryConfig.initialDelay).toBe(2.0);
  });
});

describe("RetryResponse.executeTools", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("returns empty array when no tools", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const response = await model.call("Hello");

    const result = await response.executeTools();

    expect(result).toEqual([]);
  });
});

describe("RetryResponse.retryConfig", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("exposes retryConfig via getter", async () => {
    const model = retryModel("mock/test-model", {
      maxRetries: 7,
      initialDelay: 3.0,
    });
    const response = await model.call("Hello");

    expect(response.retryConfig.maxRetries).toBe(7);
    expect(response.retryConfig.initialDelay).toBe(3.0);
  });
});

describe("ContextRetryResponse.resume", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("resumes conversation via response method", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({ userId: "123" });
    const initialResponse = await model.contextCall(ctx, "Hello");

    const followUp = await initialResponse.resume(ctx, "Follow up");

    expect(followUp).toBeInstanceOf(ContextRetryResponse);
  });

  it("exposes retryConfig via getter", async () => {
    const model = retryModel("mock/test-model", {
      maxRetries: 5,
      initialDelay: 2.0,
    });
    const ctx = createContext({});
    const response = await model.contextCall(ctx, "Hello");

    expect(response.retryConfig.maxRetries).toBe(5);
    expect(response.retryConfig.initialDelay).toBe(2.0);
  });

  it("executeTools returns empty array when no tools", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });
    const ctx = createContext({});
    const response = await model.contextCall(ctx, "Hello");

    const result = await response.executeTools(ctx);

    expect(result).toEqual([]);
  });
});

describe("withModel context override", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("response.model uses context model when set", async () => {
    const model = retryModel("mock/original-model", { maxRetries: 3 });
    const response = await model.call("Hello");

    // Response model should be original
    const responseModel = await response.model;
    expect(responseModel.modelId).toBe("mock/original-model");

    // Inside withModel context, response.model should use context model
    await withModel("mock/override-model", async () => {
      const contextModel = await response.model;
      expect(contextModel.modelId).toBe("mock/override-model");
      // Should still be a RetryModel with same config
      expect(contextModel).toBeInstanceOf(RetryModel);
      expect(contextModel.retryConfig.maxRetries).toBe(3);
    });
  });

  it("resume uses context model when set", async () => {
    const model = retryModel("mock/original-model", { maxRetries: 3 });
    const response = await model.call("Hello");

    expect(mockProvider.callCount).toBe(1);

    // Resume inside withModel context should use override model
    const followUp = await withModel("mock/override-model", async () => {
      return response.resume("Continue");
    });

    expect(followUp).toBeInstanceOf(RetryResponse);
    expect(mockProvider.callCount).toBe(2);
  });

  it("withModel with RetryModel uses its config", async () => {
    mockProvider.setExceptions([SERVER_ERROR]);
    const originalModel = retryModel("mock/original-model", { maxRetries: 1 });
    const response = await originalModel.call("Hello");

    // Create a RetryModel to use as context override
    const contextRetryModel = retryModel("mock/override-model", {
      maxRetries: 5,
    });

    // Inside context, response.model should return the context RetryModel directly
    await withModel(contextRetryModel, async () => {
      const model = await response.model;
      expect(model).toBeInstanceOf(RetryModel);
      expect(model.retryConfig.maxRetries).toBe(5);
      expect(model.modelId).toBe("mock/override-model");
    });
  });
});
