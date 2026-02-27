/**
 * E2E tests for RetryResponse property delegation and resume behavior.
 *
 * Tests that RetryResponse correctly delegates to wrapped response and
 * handles fallback model resume scenarios.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { createContext } from "@/llm/context";
import { retryModel } from "@/llm/retries/retry-model";

import {
  setupMockProvider,
  teardownMockProvider,
  CONNECTION_ERROR,
  RATE_LIMIT_ERROR,
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

describe("RetryResponse property delegation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("delegates all response properties to wrapped response", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 1 });

    const response = await model.call("Hello");

    // Test all delegated properties
    expect(response.raw).toBeDefined();
    expect(response.providerId).toBe("mock");
    expect(response.providerModelName).toBe("test-model");
    expect(response.params).toBeDefined();
    expect(response.toolkit).toBeDefined();
    expect(response.messages).toBeDefined();
    expect(response.content).toBeDefined();
    expect(response.texts).toBeDefined();
    expect(response.toolCalls).toBeDefined();
    expect(response.thoughts).toBeDefined();
    // These may be undefined depending on mock implementation
    expect(response.finishReason).toBeDefined();
    expect(response.usage).toBeDefined();
    expect(response.format).toBeNull(); // No format specified
    expect(response.parse()).toBeNull(); // No format specified
  });

  it("exposes retryConfig via getter", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 3 });

    const response = await model.call("Hello");

    expect(response.retryConfig.maxRetries).toBe(3);
  });

  it("executeTools returns empty array when no tools", async () => {
    const model = retryModel("mock/test-model", { maxRetries: 1 });

    const response = await model.call("Hello");
    const result = await response.executeTools();

    expect(result).toEqual([]);
  });
});

describe("resume with fallback models", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  it("resume uses fallback model when original succeeded on fallback", async () => {
    // First call: primary fails, fallback succeeds
    mockProvider.setExceptions([CONNECTION_ERROR]);

    const model = retryModel("mock/primary", {
      maxRetries: 0,
      fallbackModels: ["mock/fallback"],
    });

    const response = await model.call("Hello");

    // Response should have succeeded on fallback
    expect(response.modelId).toBe("mock/fallback");
    expect(response.retryFailures).toHaveLength(1);

    // Resume should use the fallback model (which succeeded)
    const resumed = await response.resume("Follow up");

    // Should succeed on fallback (no errors set)
    expect(resumed.modelId).toBe("mock/fallback");
  });

  it("resume can fall back to original if fallback fails", async () => {
    // First call: primary fails, fallback succeeds
    mockProvider.setExceptions([CONNECTION_ERROR]);

    const model = retryModel("mock/primary", {
      maxRetries: 0,
      fallbackModels: ["mock/fallback"],
    });

    const response = await model.call("Hello");

    // Response should have succeeded on fallback
    expect(response.modelId).toBe("mock/fallback");

    // For resume: fallback fails, primary succeeds
    mockProvider.setExceptions([RATE_LIMIT_ERROR]);

    const resumed = await response.resume("Follow up");

    // Should have fallen back to primary and succeeded
    expect(resumed.modelId).toBe("mock/primary");
    expect(resumed.retryFailures).toHaveLength(1);
    expect(resumed.retryFailures[0]?.model.modelId).toBe("mock/fallback");
  });

  it("model.resumeStream uses fallback model when original succeeded on fallback", async () => {
    // First call: primary fails, fallback succeeds
    mockProvider.setExceptions([CONNECTION_ERROR]);

    const model = retryModel("mock/primary", {
      maxRetries: 0,
      fallbackModels: ["mock/fallback"],
    });

    const response = await model.call("Hello");

    // Response should have succeeded on fallback
    expect(response.modelId).toBe("mock/fallback");

    // Get the model from response (which has fallback as active)
    const responseModel = await response.model;

    // ResumeStream should use the fallback model
    const streamResponse = await responseModel.resumeStream(
      response,
      "Follow up",
    );

    // Consume stream
    for await (const _text of streamResponse.textStream()) {
      // consume
    }

    expect(streamResponse.modelId).toBe("mock/fallback");
  });
});

describe("ContextRetryResponse", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
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
    const model = retryModel("mock/test-model", { maxRetries: 1 });
    const ctx = createContext({});

    const response = await model.contextCall(ctx, "Hello");
    const result = await response.executeTools(ctx);

    expect(result).toEqual([]);
  });

  it("resume with context uses fallback model when original succeeded on fallback", async () => {
    // First call: primary fails, fallback succeeds
    mockProvider.setExceptions([CONNECTION_ERROR]);

    const model = retryModel("mock/primary", {
      maxRetries: 0,
      fallbackModels: ["mock/fallback"],
    });
    const ctx = createContext({ userId: "123" });

    const response = await model.contextCall(ctx, "Hello");

    // Response should have succeeded on fallback
    expect(response.modelId).toBe("mock/fallback");

    // Resume should use the fallback model
    const resumed = await response.resume(ctx, "Follow up");

    expect(resumed.modelId).toBe("mock/fallback");
  });

  it("contextResume can fall back to original if fallback fails", async () => {
    // First call: primary fails, fallback succeeds
    mockProvider.setExceptions([CONNECTION_ERROR]);

    const model = retryModel("mock/primary", {
      maxRetries: 0,
      fallbackModels: ["mock/fallback"],
    });
    const ctx = createContext({});

    const response = await model.contextCall(ctx, "Hello");

    // Response should have succeeded on fallback
    expect(response.modelId).toBe("mock/fallback");

    // For resume: fallback fails, primary succeeds
    mockProvider.setExceptions([RATE_LIMIT_ERROR]);

    // Use response.resume which uses the response's model (with fallback as active)
    const resumed = await response.resume(ctx, "Follow up");

    // Should have fallen back to primary
    expect(resumed.modelId).toBe("mock/primary");
    expect(resumed.retryFailures).toHaveLength(1);
    expect(resumed.retryFailures[0]?.model.modelId).toBe("mock/fallback");
  });
});
