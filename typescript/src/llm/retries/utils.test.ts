import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import {
  RateLimitError,
  ServerError,
  TimeoutError,
  BadRequestError,
} from "@/llm/exceptions";

import { RetryConfig } from "./retry-config";
import { calculateDelay, isRetryableError, sleep } from "./utils";

describe("calculateDelay", () => {
  it("returns initialDelay for first attempt", () => {
    const config = new RetryConfig({ initialDelay: 1.0, backoffMultiplier: 2 });

    const delay = calculateDelay(config, 1);

    expect(delay).toBe(1.0);
  });

  it("applies exponential backoff", () => {
    const config = new RetryConfig({
      initialDelay: 1.0,
      backoffMultiplier: 2,
      maxDelay: 100,
    });

    expect(calculateDelay(config, 1)).toBe(1.0); // 1 * 2^0
    expect(calculateDelay(config, 2)).toBe(2.0); // 1 * 2^1
    expect(calculateDelay(config, 3)).toBe(4.0); // 1 * 2^2
    expect(calculateDelay(config, 4)).toBe(8.0); // 1 * 2^3
  });

  it("caps delay at maxDelay", () => {
    const config = new RetryConfig({
      initialDelay: 1.0,
      backoffMultiplier: 2,
      maxDelay: 5.0,
    });

    expect(calculateDelay(config, 4)).toBe(5.0); // Would be 8.0, capped at 5.0
    expect(calculateDelay(config, 5)).toBe(5.0); // Would be 16.0, capped at 5.0
  });

  it("applies jitter when configured", () => {
    const config = new RetryConfig({
      initialDelay: 10.0,
      backoffMultiplier: 1,
      jitter: 0.5,
      maxDelay: 100,
    });

    // Run multiple times to ensure jitter is applied
    const delays: number[] = [];
    for (let i = 0; i < 100; i++) {
      delays.push(calculateDelay(config, 1));
    }

    // All delays should be within jitter range: [5, 15]
    for (const delay of delays) {
      expect(delay).toBeGreaterThanOrEqual(5);
      expect(delay).toBeLessThanOrEqual(15);
    }

    // Delays should vary (not all the same)
    const unique = new Set(delays);
    expect(unique.size).toBeGreaterThan(1);
  });

  it("ensures delay is non-negative with jitter", () => {
    const config = new RetryConfig({
      initialDelay: 0.1,
      backoffMultiplier: 1,
      jitter: 1.0, // Max jitter
      maxDelay: 100,
    });

    // Run multiple times to ensure delay never goes negative
    for (let i = 0; i < 100; i++) {
      const delay = calculateDelay(config, 1);
      expect(delay).toBeGreaterThanOrEqual(0);
    }
  });

  it("returns 0 delay when initialDelay is 0", () => {
    const config = new RetryConfig({
      initialDelay: 0,
      backoffMultiplier: 2,
      jitter: 0,
    });

    expect(calculateDelay(config, 1)).toBe(0);
    expect(calculateDelay(config, 2)).toBe(0);
  });

  it("works with backoffMultiplier of 1 (no exponential growth)", () => {
    const config = new RetryConfig({
      initialDelay: 2.0,
      backoffMultiplier: 1,
      jitter: 0,
    });

    expect(calculateDelay(config, 1)).toBe(2.0);
    expect(calculateDelay(config, 2)).toBe(2.0);
    expect(calculateDelay(config, 3)).toBe(2.0);
  });
});

describe("isRetryableError", () => {
  it("returns true for error in retryOn list", () => {
    const config = new RetryConfig({
      retryOn: [RateLimitError, ServerError],
    });
    const error = new RateLimitError("rate limited", { provider: "openai" });

    expect(isRetryableError(error, config)).toBe(true);
  });

  it("returns false for error not in retryOn list", () => {
    const config = new RetryConfig({
      retryOn: [RateLimitError, ServerError],
    });
    const error = new BadRequestError("bad request", { provider: "openai" });

    expect(isRetryableError(error, config)).toBe(false);
  });

  it("returns false for generic Error", () => {
    const config = new RetryConfig();
    const error = new Error("generic error");

    expect(isRetryableError(error, config)).toBe(false);
  });

  it("returns true for ServerError with default config", () => {
    const config = new RetryConfig();
    const error = new ServerError("server error", { provider: "anthropic" });

    expect(isRetryableError(error, config)).toBe(true);
  });

  it("returns true for TimeoutError with default config", () => {
    const config = new RetryConfig();
    const error = new TimeoutError("timeout", { provider: "google" });

    expect(isRetryableError(error, config)).toBe(true);
  });

  it("returns false for empty retryOn list", () => {
    const config = new RetryConfig({ retryOn: [] });
    const error = new RateLimitError("rate limited", { provider: "openai" });

    expect(isRetryableError(error, config)).toBe(false);
  });

  it("checks inheritance chain (ServerError is not RateLimitError)", () => {
    const config = new RetryConfig({
      retryOn: [RateLimitError],
    });
    const error = new ServerError("server error", { provider: "openai" });

    expect(isRetryableError(error, config)).toBe(false);
  });
});

describe("sleep", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("resolves after specified milliseconds", async () => {
    const promise = sleep(1000);

    // Should not be resolved yet
    let resolved = false;
    promise.then(() => {
      resolved = true;
    });
    expect(resolved).toBe(false);

    // Advance time
    await vi.advanceTimersByTimeAsync(1000);

    // Now should be resolved
    await promise;
    expect(resolved).toBe(true);
  });

  it("resolves immediately for 0 milliseconds", async () => {
    const promise = sleep(0);

    await vi.advanceTimersByTimeAsync(0);
    await promise;
    // If we get here without hanging, test passes
    expect(true).toBe(true);
  });

  it("returns a promise", () => {
    const result = sleep(100);

    expect(result).toBeInstanceOf(Promise);
  });
});
