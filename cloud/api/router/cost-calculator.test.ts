import { describe, it, expect, vi, beforeEach } from "vitest";
import { Effect } from "effect";
import {
  OpenAICostCalculator,
  AnthropicCostCalculator,
  GoogleCostCalculator,
} from "@/api/router/cost-calculator";
import { getCostCalculator } from "@/api/router/providers";
import { clearPricingCache } from "@/api/router/pricing";

describe("CostCalculator", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    clearPricingCache();

    // Mock pricing data fetch
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
  });

  describe("OpenAICostCalculator", () => {
    it("should extract usage from OpenAI response", async () => {
      const calculator = new OpenAICostCalculator();
      const responseBody = {
        choices: [{ message: { content: "Hello" } }],
        usage: {
          prompt_tokens: 100,
          completion_tokens: 50,
          total_tokens: 150,
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("gpt-4o-mini", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.usage.inputTokens).toBe(100);
      expect(result?.usage.outputTokens).toBe(50);
      expect(result?.usage.cacheReadTokens).toBeUndefined();
    });

    it("should return null for null body", async () => {
      const calculator = new OpenAICostCalculator();
      const result = await Effect.runPromise(
        calculator.calculate("gpt-4o-mini", null),
      );

      expect(result).toBeNull();
    });

    it("should extract cache tokens from OpenAI response", async () => {
      const calculator = new OpenAICostCalculator();
      const responseBody = {
        usage: {
          prompt_tokens: 100,
          completion_tokens: 50,
          total_tokens: 150,
          prompt_tokens_details: {
            cached_tokens: 30,
          },
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("gpt-4o-mini", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.usage.cacheReadTokens).toBe(30);
    });

    it("should return null for invalid response body", async () => {
      const calculator = new OpenAICostCalculator();
      const responseBody = { choices: [] }; // No usage

      const result = await Effect.runPromise(
        calculator.calculate("gpt-4o-mini", responseBody),
      );

      expect(result).toBeNull();
    });

    it("should calculate cost correctly", async () => {
      const calculator = new OpenAICostCalculator();
      const responseBody = {
        usage: {
          prompt_tokens: 1000,
          completion_tokens: 500,
          total_tokens: 1500,
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("gpt-4o-mini", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.cost.inputCost).toBe(0.00015); // 1000 / 1M * 0.15
      expect(result?.cost.outputCost).toBe(0.0003); // 500 / 1M * 0.6
      expect(result?.cost.totalCost).toBe(0.00045);
    });
  });

  describe("AnthropicCostCalculator", () => {
    it("should extract usage from Anthropic response", async () => {
      const calculator = new AnthropicCostCalculator();
      const responseBody = {
        content: [{ type: "text", text: "Hello" }],
        usage: {
          input_tokens: 100,
          output_tokens: 50,
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("claude-3-5-haiku-20241022", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.usage.inputTokens).toBe(100);
      expect(result?.usage.outputTokens).toBe(50);
    });

    it("should return null for null body", async () => {
      const calculator = new AnthropicCostCalculator();
      const result = await Effect.runPromise(
        calculator.calculate("claude-3-5-haiku-20241022", null),
      );

      expect(result).toBeNull();
    });

    it("should return null for response without usage", async () => {
      const calculator = new AnthropicCostCalculator();
      const responseBody = {
        content: [{ type: "text", text: "Hello" }],
        // No usage field
      };

      const result = await Effect.runPromise(
        calculator.calculate("claude-3-5-haiku-20241022", responseBody),
      );

      expect(result).toBeNull();
    });

    it("should correctly handle Anthropic cache tokens", async () => {
      const calculator = new AnthropicCostCalculator();
      const responseBody = {
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_read_input_tokens: 30,
          cache_creation_input_tokens: 20,
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("claude-3-5-haiku-20241022", responseBody),
      );

      expect(result).toBeDefined();
      // inputTokens should be base + cache_read + cache_write
      expect(result?.usage.inputTokens).toBe(150); // 100 + 30 + 20
      expect(result?.usage.cacheReadTokens).toBe(30);
      expect(result?.usage.cacheWriteTokens).toBe(20);
    });

    it("should handle missing cache tokens", async () => {
      const calculator = new AnthropicCostCalculator();
      const responseBody = {
        usage: {
          input_tokens: 100,
          output_tokens: 50,
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("claude-3-5-haiku-20241022", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.usage.inputTokens).toBe(100);
      expect(result?.usage.cacheReadTokens).toBe(0);
      expect(result?.usage.cacheWriteTokens).toBe(0);
    });

    it("should extract, normalize, and price 5m cache correctly", async () => {
      const calculator = new AnthropicCostCalculator();
      const responseBody = {
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_creation_input_tokens: 1000,
          cache_read_input_tokens: 0,
          cache_creation: {
            ephemeral_5m_input_tokens: 1000,
            ephemeral_1h_input_tokens: 0,
          },
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("claude-3-5-haiku-20241022", responseBody),
      );

      expect(result).toBeDefined();
      // 5m tokens remain 1:1, so cacheWriteTokens = 1000
      expect(result?.usage.cacheWriteTokens).toBe(1000);
      // Cost: 1000 tokens / 1M * 1.25 (5m price) = 0.00125
      expect(result?.cost.cacheWriteCost).toBeCloseTo(0.00125, 6);
    });

    it("should extract, normalize, and price 1h cache correctly", async () => {
      const calculator = new AnthropicCostCalculator();
      const responseBody = {
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_creation_input_tokens: 1000,
          cache_read_input_tokens: 0,
          cache_creation: {
            ephemeral_5m_input_tokens: 0,
            ephemeral_1h_input_tokens: 1000,
          },
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("claude-3-5-haiku-20241022", responseBody),
      );

      expect(result).toBeDefined();
      // 1h tokens normalized: 1000 * 1.6 = 1600
      expect(result?.usage.cacheWriteTokens).toBe(1600);
      // Cost: 1600 tokens / 1M * 1.25 (5m price) = 0.002
      expect(result?.cost.cacheWriteCost).toBeCloseTo(0.002, 6);
    });

    it("should extract, normalize, and price mixed 5m + 1h cache tokens correctly", async () => {
      const calculator = new AnthropicCostCalculator();
      const responseBody = {
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_creation_input_tokens: 1500,
          cache_read_input_tokens: 0,
          cache_creation: {
            ephemeral_5m_input_tokens: 500,
            ephemeral_1h_input_tokens: 1000,
          },
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("claude-3-5-haiku-20241022", responseBody),
      );

      expect(result).toBeDefined();
      // Normalized: 500 (5m) + 1000 * 1.6 (1h) = 500 + 1600 = 2100
      expect(result?.usage.cacheWriteTokens).toBe(2100);
      // Cost: 2100 tokens / 1M * 1.25 (5m price) = 0.002625
      expect(result?.cost.cacheWriteCost).toBeCloseTo(0.002625, 6);
    });
  });

  describe("GoogleCostCalculator", () => {
    it("should extract usage from Google response", async () => {
      const calculator = new GoogleCostCalculator();
      const responseBody = {
        candidates: [{ content: { parts: [{ text: "Hello" }] } }],
        usageMetadata: {
          promptTokenCount: 100,
          candidatesTokenCount: 50,
          totalTokenCount: 150,
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("gemini-2.0-flash-exp", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.usage.inputTokens).toBe(100);
      expect(result?.usage.outputTokens).toBe(50);
    });

    it("should return null for null body", async () => {
      const calculator = new GoogleCostCalculator();
      const result = await Effect.runPromise(
        calculator.calculate("gemini-2.0-flash-exp", null),
      );

      expect(result).toBeNull();
    });

    it("should return null for response without usageMetadata", async () => {
      const calculator = new GoogleCostCalculator();
      const responseBody = {
        candidates: [{ content: { parts: [{ text: "Hello" }] } }],
        // No usageMetadata field
      };

      const result = await Effect.runPromise(
        calculator.calculate("gemini-2.0-flash-exp", responseBody),
      );

      expect(result).toBeNull();
    });

    it("should extract cached tokens from Google response", async () => {
      const calculator = new GoogleCostCalculator();
      const responseBody = {
        usageMetadata: {
          promptTokenCount: 100,
          candidatesTokenCount: 50,
          totalTokenCount: 150,
          cachedContentTokenCount: 30,
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("gemini-2.0-flash-exp", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.usage.cacheReadTokens).toBe(30);
    });
  });

  describe("getCostCalculator", () => {
    it("should return OpenAICostCalculator for openai", () => {
      const calculator = getCostCalculator("openai");
      expect(calculator).toBeInstanceOf(OpenAICostCalculator);
    });

    it("should return AnthropicCostCalculator for anthropic", () => {
      const calculator = getCostCalculator("anthropic");
      expect(calculator).toBeInstanceOf(AnthropicCostCalculator);
    });

    it("should return GoogleCostCalculator for google", () => {
      const calculator = getCostCalculator("google");
      expect(calculator).toBeInstanceOf(GoogleCostCalculator);
    });
  });

  describe("BaseCostCalculator - error handling", () => {
    it("should handle missing pricing data gracefully", async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({}), // Empty pricing data
      }) as unknown as typeof fetch;

      const calculator = new OpenAICostCalculator();
      const responseBody = {
        usage: {
          prompt_tokens: 1000,
          completion_tokens: 500,
          total_tokens: 1500,
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("unknown-model", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.usage.inputTokens).toBe(1000);
      expect(result?.cost.totalCost).toBe(0);
      expect(result?.formattedCost.input).toBe("N/A");
      expect(result?.formattedCost.output).toBe("N/A");
      expect(result?.formattedCost.total).toBe("N/A");
    });

    it("should handle fetch errors gracefully", async () => {
      global.fetch = vi
        .fn()
        .mockRejectedValue(
          new Error("Network error"),
        ) as unknown as typeof fetch;

      const calculator = new OpenAICostCalculator();
      const responseBody = {
        usage: {
          prompt_tokens: 1000,
          completion_tokens: 500,
          total_tokens: 1500,
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("gpt-4o-mini", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.cost.totalCost).toBe(0);
      expect(result?.formattedCost.total).toBe("N/A");
    });
  });

  describe("formatted cost output", () => {
    it("should format costs correctly", async () => {
      const calculator = new OpenAICostCalculator();
      const responseBody = {
        usage: {
          prompt_tokens: 1000,
          completion_tokens: 500,
          total_tokens: 1500,
          prompt_tokens_details: {
            cached_tokens: 200,
          },
        },
      };

      const result = await Effect.runPromise(
        calculator.calculate("gpt-4o-mini", responseBody),
      );

      expect(result).toBeDefined();
      expect(result?.formattedCost.input).toMatch(/^\$\d+\.\d{6}$/);
      expect(result?.formattedCost.output).toMatch(/^\$\d+\.\d{6}$/);
      expect(result?.formattedCost.total).toMatch(/^\$\d+\.\d{6}$/);
      expect(result?.formattedCost.cacheRead).toMatch(/^\$\d+\.\d{6}$/);
    });
  });
});
