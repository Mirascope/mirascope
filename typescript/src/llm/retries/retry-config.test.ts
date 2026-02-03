import { describe, expect, it } from "vitest";

import {
  ConnectionError,
  RateLimitError,
  ServerError,
  TimeoutError,
} from "@/llm/exceptions";
import { Model } from "@/llm/models";

import {
  RetryConfig,
  DEFAULT_RETRYABLE_ERRORS,
  DEFAULT_MAX_RETRIES,
  DEFAULT_INITIAL_DELAY,
  DEFAULT_MAX_DELAY,
  DEFAULT_BACKOFF_MULTIPLIER,
  DEFAULT_JITTER,
} from "./retry-config";

describe("RetryConfig", () => {
  describe("constructor with defaults", () => {
    it("uses default values when no args provided", () => {
      const config = new RetryConfig();

      expect(config.maxRetries).toBe(DEFAULT_MAX_RETRIES);
      expect(config.initialDelay).toBe(DEFAULT_INITIAL_DELAY);
      expect(config.maxDelay).toBe(DEFAULT_MAX_DELAY);
      expect(config.backoffMultiplier).toBe(DEFAULT_BACKOFF_MULTIPLIER);
      expect(config.jitter).toBe(DEFAULT_JITTER);
      expect(config.fallbackModels).toEqual([]);
    });

    it("uses default retryable errors", () => {
      const config = new RetryConfig();

      expect(config.retryOn).toEqual(DEFAULT_RETRYABLE_ERRORS);
    });
  });

  describe("constructor with custom values", () => {
    it("accepts custom maxRetries", () => {
      const config = new RetryConfig({ maxRetries: 5 });

      expect(config.maxRetries).toBe(5);
    });

    it("accepts custom initialDelay", () => {
      const config = new RetryConfig({ initialDelay: 1.5 });

      expect(config.initialDelay).toBe(1.5);
    });

    it("accepts custom maxDelay", () => {
      const config = new RetryConfig({ maxDelay: 120 });

      expect(config.maxDelay).toBe(120);
    });

    it("accepts custom backoffMultiplier", () => {
      const config = new RetryConfig({ backoffMultiplier: 3 });

      expect(config.backoffMultiplier).toBe(3);
    });

    it("accepts custom jitter", () => {
      const config = new RetryConfig({ jitter: 0.5 });

      expect(config.jitter).toBe(0.5);
    });

    it("accepts custom retryOn errors", () => {
      const customErrors = [RateLimitError, ServerError];
      const config = new RetryConfig({ retryOn: customErrors });

      expect(config.retryOn).toEqual(customErrors);
    });

    it("accepts fallback model IDs", () => {
      const config = new RetryConfig({
        fallbackModels: ["openai/gpt-4o", "anthropic/claude-sonnet-4-20250514"],
      });

      expect(config.fallbackModels).toHaveLength(2);
      expect(config.fallbackModels[0]).toBe("openai/gpt-4o");
      expect(config.fallbackModels[1]).toBe(
        "anthropic/claude-sonnet-4-20250514",
      );
    });

    it("accepts fallback Model instances", () => {
      const model1 = new Model("openai/gpt-4o", { temperature: 0.5 });
      const model2 = new Model("anthropic/claude-sonnet-4-20250514");
      const config = new RetryConfig({
        fallbackModels: [model1, model2],
      });

      expect(config.fallbackModels).toHaveLength(2);
      expect(config.fallbackModels[0]).toBe(model1);
      expect(config.fallbackModels[1]).toBe(model2);
    });

    it("accepts mixed fallback models and IDs", () => {
      const model = new Model("openai/gpt-4o");
      const config = new RetryConfig({
        fallbackModels: [model, "anthropic/claude-sonnet-4-20250514"],
      });

      expect(config.fallbackModels).toHaveLength(2);
      expect(config.fallbackModels[0]).toBe(model);
      expect(config.fallbackModels[1]).toBe(
        "anthropic/claude-sonnet-4-20250514",
      );
    });
  });

  describe("validation", () => {
    it("throws for negative maxRetries", () => {
      expect(() => new RetryConfig({ maxRetries: -1 })).toThrow(
        "maxRetries must be non-negative",
      );
    });

    it("allows zero maxRetries", () => {
      const config = new RetryConfig({ maxRetries: 0 });

      expect(config.maxRetries).toBe(0);
    });

    it("throws for negative initialDelay", () => {
      expect(() => new RetryConfig({ initialDelay: -0.1 })).toThrow(
        "initialDelay must be non-negative",
      );
    });

    it("allows zero initialDelay", () => {
      const config = new RetryConfig({ initialDelay: 0 });

      expect(config.initialDelay).toBe(0);
    });

    it("throws for negative maxDelay", () => {
      expect(() => new RetryConfig({ maxDelay: -1 })).toThrow(
        "maxDelay must be non-negative",
      );
    });

    it("allows zero maxDelay", () => {
      const config = new RetryConfig({ maxDelay: 0 });

      expect(config.maxDelay).toBe(0);
    });

    it("throws for backoffMultiplier less than 1", () => {
      expect(() => new RetryConfig({ backoffMultiplier: 0.9 })).toThrow(
        "backoffMultiplier must be >= 1",
      );
    });

    it("allows backoffMultiplier of 1", () => {
      const config = new RetryConfig({ backoffMultiplier: 1 });

      expect(config.backoffMultiplier).toBe(1);
    });

    it("throws for jitter less than 0", () => {
      expect(() => new RetryConfig({ jitter: -0.1 })).toThrow(
        "jitter must be between 0.0 and 1.0",
      );
    });

    it("throws for jitter greater than 1", () => {
      expect(() => new RetryConfig({ jitter: 1.1 })).toThrow(
        "jitter must be between 0.0 and 1.0",
      );
    });

    it("allows jitter of 0", () => {
      const config = new RetryConfig({ jitter: 0 });

      expect(config.jitter).toBe(0);
    });

    it("allows jitter of 1", () => {
      const config = new RetryConfig({ jitter: 1 });

      expect(config.jitter).toBe(1);
    });
  });

  describe("fromArgs", () => {
    it("creates a RetryConfig from args", () => {
      const config = RetryConfig.fromArgs({ maxRetries: 5 });

      expect(config).toBeInstanceOf(RetryConfig);
      expect(config.maxRetries).toBe(5);
    });

    it("creates a RetryConfig with defaults when no args", () => {
      const config = RetryConfig.fromArgs();

      expect(config).toBeInstanceOf(RetryConfig);
      expect(config.maxRetries).toBe(DEFAULT_MAX_RETRIES);
    });
  });
});

describe("DEFAULT_RETRYABLE_ERRORS", () => {
  it("includes ConnectionError", () => {
    expect(DEFAULT_RETRYABLE_ERRORS).toContain(ConnectionError);
  });

  it("includes RateLimitError", () => {
    expect(DEFAULT_RETRYABLE_ERRORS).toContain(RateLimitError);
  });

  it("includes ServerError", () => {
    expect(DEFAULT_RETRYABLE_ERRORS).toContain(ServerError);
  });

  it("includes TimeoutError", () => {
    expect(DEFAULT_RETRYABLE_ERRORS).toContain(TimeoutError);
  });

  it("has exactly 4 error types", () => {
    expect(DEFAULT_RETRYABLE_ERRORS).toHaveLength(4);
  });
});

describe("default constants", () => {
  it("DEFAULT_MAX_RETRIES is 3", () => {
    expect(DEFAULT_MAX_RETRIES).toBe(3);
  });

  it("DEFAULT_INITIAL_DELAY is 0.5", () => {
    expect(DEFAULT_INITIAL_DELAY).toBe(0.5);
  });

  it("DEFAULT_MAX_DELAY is 60.0", () => {
    expect(DEFAULT_MAX_DELAY).toBe(60.0);
  });

  it("DEFAULT_BACKOFF_MULTIPLIER is 2.0", () => {
    expect(DEFAULT_BACKOFF_MULTIPLIER).toBe(2.0);
  });

  it("DEFAULT_JITTER is 0.0", () => {
    expect(DEFAULT_JITTER).toBe(0.0);
  });
});
