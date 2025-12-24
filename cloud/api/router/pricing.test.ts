import { describe, it, expect, vi, beforeEach } from "vitest";
import { Effect } from "effect";
import {
  fetchModelsDotDevPricingData,
  getModelsDotDevPricingData,
  getModelPricing,
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
    it("should return pricing for OpenAI model in centi-cents", async () => {
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

      // Pricing is converted from dollars to centi-cents
      // $0.15 = 1500cc, $0.6 = 6000cc, $0.075 = 750cc, $0.1875 = 1875cc
      expect(result).toMatchObject({
        input: 1500n,
        output: 6000n,
        cache_read: 750n,
        cache_write: 1875n,
      });
    });

    it("should return pricing for Anthropic model in centi-cents", async () => {
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

      // $1.0 = 10000cc, $5.0 = 50000cc, $0.1 = 1000cc, $1.25 = 12500cc
      expect(result).toMatchObject({
        input: 10000n,
        output: 50000n,
        cache_read: 1000n,
        cache_write: 12500n,
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
        input: 0n,
        output: 0n,
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

    it("should return null for model with invalid cache pricing (NaN)", async () => {
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "invalid-model": {
              id: "invalid-model",
              name: "Invalid Model",
              cost: {
                input: 0.15,
                output: 0.6,
                cache_read: NaN, // Invalid cache pricing
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
        getModelPricing("openai", "invalid-model"),
      );

      expect(result).toBeNull();
    });

    it("should return null for model with negative cache pricing", async () => {
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "invalid-model": {
              id: "invalid-model",
              name: "Invalid Model",
              cost: {
                input: 0.15,
                output: 0.6,
                cache_write: -0.5, // Negative cache pricing
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
        getModelPricing("openai", "invalid-model"),
      );

      expect(result).toBeNull();
    });

    it("should return null for model with invalid input pricing (NaN)", async () => {
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "invalid-model": {
              id: "invalid-model",
              name: "Invalid Model",
              cost: {
                input: NaN, // Invalid input pricing
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

      const result = await Effect.runPromise(
        getModelPricing("openai", "invalid-model"),
      );

      expect(result).toBeNull();
    });

    it("should return null for model with negative input pricing", async () => {
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "invalid-model": {
              id: "invalid-model",
              name: "Invalid Model",
              cost: {
                input: -0.5, // Negative input pricing
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

      const result = await Effect.runPromise(
        getModelPricing("openai", "invalid-model"),
      );

      expect(result).toBeNull();
    });

    it("should return null for model with invalid output pricing (Infinity)", async () => {
      const mockData = {
        openai: {
          id: "openai",
          name: "OpenAI",
          models: {
            "invalid-model": {
              id: "invalid-model",
              name: "Invalid Model",
              cost: {
                input: 0.15,
                output: Infinity, // Invalid output pricing
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
        getModelPricing("openai", "invalid-model"),
      );

      expect(result).toBeNull();
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
