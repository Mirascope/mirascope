/**
 * E2E tests for fallback model behavior.
 *
 * Tests that when primary model exhausts retries, fallback models are tried.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { RetriesExhausted, StreamRestarted } from "@/llm/exceptions";
import { Model } from "@/llm/models";
import { RetryConfig } from "@/llm/retries/retry-config";
import { RetryModel, retryModel } from "@/llm/retries/retry-model";

import {
  setupMockProvider,
  teardownMockProvider,
  SERVER_ERROR,
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

describe("fallback models", () => {
  let mockProvider: MockProvider;

  beforeEach(() => {
    vi.clearAllMocks();
    mockProvider = setupMockProvider();
  });

  afterEach(() => {
    teardownMockProvider();
  });

  describe("fallback progression", () => {
    it("tries fallback model after primary exhausted", async () => {
      // Primary fails twice (maxRetries=1 means 1 retry after initial)
      mockProvider.setExceptions([SERVER_ERROR, SERVER_ERROR]);

      const model = retryModel("mock/primary-model", {
        maxRetries: 1,
        fallbackModels: ["mock/fallback-model"],
      });

      const response = await model.call("Hello");

      // Primary failed 2 times, then fallback succeeded
      expect(response.retryFailures).toHaveLength(2);
      expect(mockProvider.callCount).toBe(3);
    });

    it("tries multiple fallback models in order", async () => {
      // Primary fails 2x, first fallback fails 2x, second fallback succeeds
      mockProvider.setExceptions([
        SERVER_ERROR,
        SERVER_ERROR,
        CONNECTION_ERROR,
        CONNECTION_ERROR,
      ]);

      const model = retryModel("mock/primary-model", {
        maxRetries: 1,
        fallbackModels: ["mock/fallback-1", "mock/fallback-2"],
      });

      const response = await model.call("Hello");

      expect(response.retryFailures).toHaveLength(4);
      expect(mockProvider.callCount).toBe(5);
    });

    it("exhausts when all models fail", async () => {
      mockProvider.setExceptions([
        SERVER_ERROR,
        SERVER_ERROR,
        CONNECTION_ERROR,
        CONNECTION_ERROR,
      ]);

      const model = retryModel("mock/primary-model", {
        maxRetries: 1,
        fallbackModels: ["mock/fallback-model"],
      });

      await expect(model.call("Hello")).rejects.toThrow(RetriesExhausted);
    });
  });

  describe("fallback model configuration", () => {
    it("accepts ModelId strings as fallbacks", () => {
      const model = retryModel("mock/primary-model", {
        fallbackModels: ["mock/fallback-1", "mock/fallback-2"],
      });

      expect(model.retryConfig.fallbackModels).toHaveLength(2);
    });

    it("accepts Model instances as fallbacks", () => {
      const fallback = new Model("mock/fallback-model", { temperature: 0.9 });
      const config = new RetryConfig({ fallbackModels: [fallback] });
      const model = new RetryModel("mock/primary-model", config);

      expect(model.retryConfig.fallbackModels).toHaveLength(1);
    });

    it("accepts mixed fallbacks", () => {
      const fallbackModel = new Model("mock/fallback-1");
      const config = new RetryConfig({
        fallbackModels: [fallbackModel, "mock/fallback-2"],
      });
      const model = new RetryModel("mock/primary-model", config);

      expect(model.retryConfig.fallbackModels).toHaveLength(2);
    });
  });

  describe("parameter inheritance", () => {
    it("fallback ModelId strings inherit params from primary", async () => {
      mockProvider.setExceptions([SERVER_ERROR, SERVER_ERROR]);

      const model = retryModel("mock/primary-model", {
        temperature: 0.7,
        maxRetries: 1,
        fallbackModels: ["mock/fallback-model"],
      });

      const response = await model.call("Hello");

      // Fallback should inherit temperature from primary
      expect(response.params).toEqual({ temperature: 0.7 });
    });

    it("fallback Model instances keep their own params", async () => {
      mockProvider.setExceptions([SERVER_ERROR, SERVER_ERROR]);

      const fallback = new Model("mock/fallback-model", { temperature: 0.9 });
      const model = new RetryModel(
        "mock/primary-model",
        new RetryConfig({
          maxRetries: 1,
          fallbackModels: [fallback],
        }),
        { temperature: 0.3 },
      );

      const response = await model.call("Hello");
      // The fallback model has temperature: 0.9
      expect(response.params).toEqual({ temperature: 0.9 });
    });
  });

  describe("variantsAsync iteration", () => {
    it("yields correct number of variants", async () => {
      const model = retryModel("mock/primary-model", {
        maxRetries: 2,
        fallbackModels: ["mock/fallback-model"],
      });

      const variants: RetryModel[] = [];
      for await (const variant of model.variantsAsync()) {
        variants.push(variant);
      }

      // Primary: 1 initial + 2 retries = 3
      // Fallback: 1 initial + 2 retries = 3
      // Total: 6
      expect(variants).toHaveLength(6);
    });

    it("primary model variants come first", async () => {
      const model = retryModel("mock/primary-model", {
        maxRetries: 1,
        fallbackModels: ["mock/fallback-model"],
      });

      const modelIds: string[] = [];
      for await (const variant of model.variantsAsync()) {
        modelIds.push(variant.getActiveModel().modelId);
      }

      expect(modelIds).toEqual([
        "mock/primary-model",
        "mock/primary-model",
        "mock/fallback-model",
        "mock/fallback-model",
      ]);
    });
  });

  describe("response model property", () => {
    it("response.model has successful model as active", async () => {
      mockProvider.setExceptions([SERVER_ERROR, SERVER_ERROR]);

      const model = retryModel("mock/primary-model", {
        maxRetries: 1,
        fallbackModels: ["mock/fallback-model"],
      });

      const response = await model.call("Hello");
      const responseModel = await response.model;

      // The response's model should have the fallback as active
      expect(responseModel.getActiveModel().modelId).toBe(
        "mock/fallback-model",
      );
    });

    it("response.model preserves retry config", async () => {
      const model = retryModel("mock/primary-model", {
        maxRetries: 5,
        initialDelay: 2.0,
      });

      const response = await model.call("Hello");
      const responseModel = await response.model;

      expect(responseModel.retryConfig.maxRetries).toBe(5);
      expect(responseModel.retryConfig.initialDelay).toBe(2.0);
    });
  });

  describe("stream fallback", () => {
    it("stream falls back to next model on exhaustion", async () => {
      mockProvider.setStreamExceptions([
        SERVER_ERROR,
        SERVER_ERROR,
        RATE_LIMIT_ERROR,
        RATE_LIMIT_ERROR,
      ]);

      const model = retryModel("mock/primary-model", {
        maxRetries: 2,
        fallbackModels: ["mock/fallback-model"],
      });

      const response = await model.stream("Hello");

      let restartCount = 0;
      while (true) {
        try {
          for await (const _text of response.textStream()) {
            // Consume
          }
          break;
        } catch (e) {
          if (e instanceof StreamRestarted) {
            restartCount++;
          } else {
            throw e;
          }
        }
      }

      // 4 errors means 4 restarts before success on 5th attempt
      // maxRetries=2 gives 3 attempts per model = 6 total (enough for 4 failures + success)
      expect(restartCount).toBe(4);
      expect(response.retryFailures).toHaveLength(4);
    });
  });
});
