import { describe, it, expect, vi, beforeEach } from "vitest";
import { Effect } from "effect";
import {
  fetchModelsDotDevPricingData,
  getModelsDotDevPricingData,
  getModelPricing,
  calculateCost,
  formatCostBreakdown,
  clearPricingCache,
} from "@/api/router/pricing";

describe("Pricing", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    clearPricingCache();
  });

  describe("fetchPricingData", () => {
    it("should fetch and return pricing data", async () => {
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "gpt-4o-mini": {
              id: "gpt-4o-mini",
              name: "GPT-4o Mini",
              cost: {
                input: 0.15,
                output: 0.6,
              },
            },
          },
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      }) as unknown as typeof fetch;

      const result = await Effect.runPromise(fetchModelsDotDevPricingData());

      expect(result).toEqual(mockData);
      expect(fetch).toHaveBeenCalledWith("https://models.dev/api.json");
    });

    it("should fail when fetch returns non-ok response", async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        statusText: "Not Found",
      }) as unknown as typeof fetch;

      const result = await Effect.runPromise(
        fetchModelsDotDevPricingData().pipe(Effect.flip),
      );

      expect(result).toBeInstanceOf(Error);
      expect(result.message).toContain("Failed to fetch pricing data");
    });

    it("should fail when fetch throws an error", async () => {
      global.fetch = vi
        .fn()
        .mockRejectedValue(
          new Error("Network error"),
        ) as unknown as typeof fetch;

      const result = await Effect.runPromise(
        fetchModelsDotDevPricingData().pipe(Effect.flip),
      );

      expect(result).toBeInstanceOf(Error);
      expect(result.message).toContain("Network error");
    });

    it("should fail when JSON parsing fails", async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.reject(new Error("Invalid JSON")),
      }) as unknown as typeof fetch;

      const result = await Effect.runPromise(
        fetchModelsDotDevPricingData().pipe(Effect.flip),
      );

      expect(result).toBeInstanceOf(Error);
      expect(result.message).toContain(
        "Failed to parse JSON from response body",
      );
      expect(result.message).toContain("Invalid JSON");
    });
  });

  describe("getModelPricing", () => {
    it("should return pricing for OpenAI model", async () => {
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "gpt-4o-mini": {
              id: "gpt-4o-mini",
              name: "GPT-4o Mini",
              cost: {
                input: 0.15,
                output: 0.6,
                cache_read: 0.075,
                cache_write: 0.1875,
              },
            },
          },
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      }) as unknown as typeof fetch;

      const result = await Effect.runPromise(
        getModelPricing("openai", "gpt-4o-mini"),
      );

      expect(result).toMatchObject({
        input: 0.15,
        output: 0.6,
        cache_read: 0.075,
        cache_write: 0.1875,
      });
    });

    it("should return pricing for Anthropic model", async () => {
      const mockData = {
        anthropic: {
          id: "anthropic",
          name: "Anthropic",
          models: {
            "claude-3-5-haiku-20241022": {
              id: "claude-3-5-haiku-20241022",
              name: "Claude 3.5 Haiku",
              cost: {
                input: 1.0,
                output: 5.0,
                cache_read: 0.1,
                cache_write: 1.25,
              },
            },
          },
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      }) as unknown as typeof fetch;

      const result = await Effect.runPromise(
        getModelPricing("anthropic", "claude-3-5-haiku-20241022"),
      );

      expect(result).toMatchObject({
        input: 1.0,
        output: 5.0,
        cache_read: 0.1,
        cache_write: 1.25,
      });
    });

    it("should try both google and google-ai-studio for Google models", async () => {
      const mockData = {
        "google-ai-studio": {
          id: "google-ai-studio",
          name: "Google AI Studio",
          models: {
            "gemini-2.0-flash-exp": {
              id: "gemini-2.0-flash-exp",
              name: "Gemini 2.0 Flash",
              cost: {
                input: 0.0,
                output: 0.0,
              },
            },
          },
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      }) as unknown as typeof fetch;

      const result = await Effect.runPromise(
        getModelPricing("google", "gemini-2.0-flash-exp"),
      );

      expect(result).toMatchObject({
        input: 0.0,
        output: 0.0,
      });
      expect(result?.cache_read).toBeUndefined();
      expect(result?.cache_write).toBeUndefined();
    });

    it("should return null for unknown model", async () => {
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {},
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      }) as unknown as typeof fetch;

      const result = await Effect.runPromise(
        getModelPricing("openai", "unknown-model"),
      );

      expect(result).toBeNull();
    });
  });

  describe("calculateCost", () => {
    it("should calculate cost correctly for basic usage", () => {
      const pricing = {
        input: 0.15, // per million tokens
        output: 0.6,
      };

      const usage = {
        inputTokens: 1000,
        outputTokens: 500,
      };

      const result = calculateCost(pricing, usage);

      expect(result.inputCost).toBe(0.00015); // 1000 / 1M * 0.15
      expect(result.outputCost).toBe(0.0003); // 500 / 1M * 0.6
      expect(result.totalCost).toBe(0.00045);
      expect(result.cacheReadCost).toBeUndefined();
      expect(result.cacheWriteCost).toBeUndefined();
    });

    it("should calculate cost with cache tokens", () => {
      const pricing = {
        input: 0.15,
        output: 0.6,
        cache_read: 0.075,
        cache_write: 0.1875,
      };

      const usage = {
        inputTokens: 1000,
        outputTokens: 500,
        cacheReadTokens: 200,
        cacheWriteTokens: 100,
      };

      const result = calculateCost(pricing, usage);

      expect(result.inputCost).toBeCloseTo(0.00015, 10);
      expect(result.outputCost).toBeCloseTo(0.0003, 10);
      expect(result.cacheReadCost).toBeCloseTo(0.000015, 10); // 200 / 1M * 0.075
      expect(result.cacheWriteCost).toBeCloseTo(0.00001875, 10); // 100 / 1M * 0.1875
      expect(result.totalCost).toBeCloseTo(
        0.00015 + 0.0003 + 0.000015 + 0.00001875,
        10,
      );
    });

    it("should handle missing cache pricing", () => {
      const pricing = {
        input: 0.15,
        output: 0.6,
      };

      const usage = {
        inputTokens: 1000,
        outputTokens: 500,
        cacheReadTokens: 200,
        cacheWriteTokens: 100,
      };

      const result = calculateCost(pricing, usage);

      expect(result.cacheReadCost).toBeUndefined();
      expect(result.cacheWriteCost).toBeUndefined();
      expect(result.totalCost).toBe(0.00045);
    });

    it("should handle zero tokens", () => {
      const pricing = {
        input: 0.15,
        output: 0.6,
      };

      const usage = {
        inputTokens: 0,
        outputTokens: 0,
      };

      const result = calculateCost(pricing, usage);

      expect(result.inputCost).toBe(0);
      expect(result.outputCost).toBe(0);
      expect(result.totalCost).toBe(0);
    });
  });

  describe("formatCostBreakdown", () => {
    it("should format cost breakdown with 6 decimal places", () => {
      const breakdown = {
        inputCost: 0.00015,
        outputCost: 0.0003,
        cacheReadCost: 0.000075,
        cacheWriteCost: 0.0001,
        totalCost: 0.000525,
      };

      const formatted = formatCostBreakdown(breakdown);

      expect(formatted.input).toBe("$0.000150");
      expect(formatted.output).toBe("$0.000300");
      expect(formatted.cacheRead).toBe("$0.000075");
      expect(formatted.cacheWrite).toBe("$0.000100");
      expect(formatted.total).toBe("$0.000525");
    });

    it("should handle undefined cache costs", () => {
      const breakdown = {
        inputCost: 0.00015,
        outputCost: 0.0003,
        totalCost: 0.00045,
      };

      const formatted = formatCostBreakdown(breakdown);

      expect(formatted.input).toBe("$0.000150");
      expect(formatted.output).toBe("$0.000300");
      expect(formatted.cacheRead).toBeUndefined();
      expect(formatted.cacheWrite).toBeUndefined();
      expect(formatted.total).toBe("$0.000450");
    });
  });

  describe("getPricingData", () => {
    it("should use cached data when cache is fresh", async () => {
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "gpt-4o-mini": {
              id: "gpt-4o-mini",
              name: "GPT-4o Mini",
              cost: {
                input: 0.15,
                output: 0.6,
              },
            },
          },
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      }) as unknown as typeof fetch;

      // First fetch - should call the API
      const result1 = await Effect.runPromise(getModelsDotDevPricingData());
      expect(fetch).toHaveBeenCalledTimes(1);
      expect(result1).toEqual(mockData);

      // Second fetch - should use cache, not call API again
      const result2 = await Effect.runPromise(getModelsDotDevPricingData());
      expect(fetch).toHaveBeenCalledTimes(1); // Still 1, not 2
      expect(result2).toEqual(mockData);
    });
  });

  describe("clearPricingCache", () => {
    it("should clear the pricing cache", async () => {
      // Set up mock data
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "gpt-4o-mini": {
              id: "gpt-4o-mini",
              name: "GPT-4o Mini",
              cost: {
                input: 0.15,
                output: 0.6,
              },
            },
          },
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      }) as unknown as typeof fetch;

      // Fetch pricing data to populate cache
      await Effect.runPromise(getModelsDotDevPricingData());

      // Verify fetch was called once
      expect(fetch).toHaveBeenCalledTimes(1);

      // Clear the cache
      clearPricingCache();

      // Fetch again - should trigger a new fetch since cache was cleared
      await Effect.runPromise(getModelsDotDevPricingData());

      // Verify fetch was called again
      expect(fetch).toHaveBeenCalledTimes(2);
    });
  });
});
