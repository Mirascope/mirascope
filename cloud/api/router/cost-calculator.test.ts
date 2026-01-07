import { vi, beforeEach } from "vitest";
import { describe, it, expect } from "@/tests/api";
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
    it.effect("should extract usage from OpenAI Completions API response", () =>
      Effect.gen(function* () {
        const calculator = new OpenAICostCalculator();
        const responseBody = {
          choices: [{ message: { content: "Hello" } }],
          usage: {
            prompt_tokens: 100,
            completion_tokens: 50,
            total_tokens: 150,
          },
        };

        const result = yield* calculator.calculate("gpt-4o-mini", responseBody);

        expect(result).toBeDefined();
        expect(result?.usage.inputTokens).toBe(100);
        expect(result?.usage.outputTokens).toBe(50);
        expect(result?.usage.cacheReadTokens).toBeUndefined();
      }),
    );

    it.effect("should return null for null body", () =>
      Effect.gen(function* () {
        const calculator = new OpenAICostCalculator();
        const result = yield* calculator.calculate("gpt-4o-mini", null);

        expect(result).toBeNull();
      }),
    );

    it.effect("should extract usage from OpenAI Responses API response", () =>
      Effect.gen(function* () {
        const calculator = new OpenAICostCalculator();
        const responseBody = {
          output: [
            {
              type: "message",
              content: [{ type: "output_text", text: "Hello" }],
            },
          ],
          usage: {
            input_tokens: 100,
            output_tokens: 50,
            total_tokens: 150,
          },
        };

        const result = yield* calculator.calculate("gpt-4o-mini", responseBody);

        expect(result).toBeDefined();
        expect(result?.usage.inputTokens).toBe(100);
        expect(result?.usage.outputTokens).toBe(50);
        expect(result?.usage.cacheReadTokens).toBeUndefined();
      }),
    );

    it.effect(
      "should extract cache tokens from OpenAI Completions API response",
      () =>
        Effect.gen(function* () {
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

          const result = yield* calculator.calculate(
            "gpt-4o-mini",
            responseBody,
          );

          expect(result).toBeDefined();
          expect(result?.usage.cacheReadTokens).toBe(30);
        }),
    );

    it.effect(
      "should extract cache tokens from OpenAI Responses API response",
      () =>
        Effect.gen(function* () {
          const calculator = new OpenAICostCalculator();
          const responseBody = {
            usage: {
              input_tokens: 100,
              output_tokens: 50,
              total_tokens: 150,
              input_tokens_details: {
                cached_tokens: 30,
              },
            },
          };

          const result = yield* calculator.calculate(
            "gpt-4o-mini",
            responseBody,
          );

          expect(result).toBeDefined();
          expect(result?.usage.cacheReadTokens).toBe(30);
        }),
    );

    it.effect("should return null for invalid response body", () =>
      Effect.gen(function* () {
        const calculator = new OpenAICostCalculator();
        const responseBody = { choices: [] }; // No usage

        const result = yield* calculator.calculate("gpt-4o-mini", responseBody);

        expect(result).toBeNull();
      }),
    );

    it.effect("should return null for response with invalid usage format", () =>
      Effect.gen(function* () {
        const calculator = new OpenAICostCalculator();
        const responseBody = {
          usage: {
            // Missing both Completions and Responses API fields
            invalid_field: 100,
          },
        };

        const result = yield* calculator.calculate("gpt-4o-mini", responseBody);

        expect(result).toBeNull();
      }),
    );

    it.effect("should calculate cost correctly", () =>
      Effect.gen(function* () {
        const calculator = new OpenAICostCalculator();
        const responseBody = {
          usage: {
            prompt_tokens: 1000,
            completion_tokens: 500,
            total_tokens: 1500,
          },
        };

        const result = yield* calculator.calculate("gpt-4o-mini", responseBody);

        expect(result).toBeDefined();
        // 1000 / 1M * 1500 centicents = 1.5 -> 1 centicent
        expect(result?.cost.inputCost).toBe(1n);
        // 500 / 1M * 6000 centicents = 3 centicents
        expect(result?.cost.outputCost).toBe(3n);
        expect(result?.cost.totalCost).toBe(4n);
      }),
    );
  });

  describe("AnthropicCostCalculator", () => {
    it.effect("should extract usage from Anthropic response", () =>
      Effect.gen(function* () {
        const calculator = new AnthropicCostCalculator();
        const responseBody = {
          content: [{ type: "text", text: "Hello" }],
          usage: {
            input_tokens: 100,
            output_tokens: 50,
          },
        };

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          responseBody,
        );

        expect(result).toBeDefined();
        expect(result?.usage.inputTokens).toBe(100);
        expect(result?.usage.outputTokens).toBe(50);
      }),
    );

    it.effect("should return null for null body", () =>
      Effect.gen(function* () {
        const calculator = new AnthropicCostCalculator();
        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          null,
        );

        expect(result).toBeNull();
      }),
    );

    it.effect("should return null for response without usage", () =>
      Effect.gen(function* () {
        const calculator = new AnthropicCostCalculator();
        const responseBody = {
          content: [{ type: "text", text: "Hello" }],
          // No usage field
        };

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          responseBody,
        );

        expect(result).toBeNull();
      }),
    );

    it.effect("should correctly handle Anthropic cache tokens", () =>
      Effect.gen(function* () {
        const calculator = new AnthropicCostCalculator();
        const responseBody = {
          usage: {
            input_tokens: 100,
            output_tokens: 50,
            cache_read_input_tokens: 30,
            cache_creation_input_tokens: 20,
          },
        };

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          responseBody,
        );

        expect(result).toBeDefined();
        expect(result?.usage.inputTokens).toBe(100);
        expect(result?.usage.cacheReadTokens).toBe(30);
        expect(result?.usage.cacheWriteTokens).toBe(20);
      }),
    );

    it.effect("should handle missing cache tokens", () =>
      Effect.gen(function* () {
        const calculator = new AnthropicCostCalculator();
        const responseBody = {
          usage: {
            input_tokens: 100,
            output_tokens: 50,
          },
        };

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          responseBody,
        );

        expect(result).toBeDefined();
        expect(result?.usage.inputTokens).toBe(100);
        expect(result?.usage.cacheReadTokens).toBe(0);
        expect(result?.usage.cacheWriteTokens).toBe(0);
      }),
    );

    it.effect("should extract, normalize, and price 5m cache correctly", () =>
      Effect.gen(function* () {
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

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          responseBody,
        );

        expect(result).toBeDefined();
        // 5m tokens remain 1:1, so cacheWriteTokens = 1000
        expect(result?.usage.cacheWriteTokens).toBe(1000);
        // Cost in centi-cents: 1000 tokens / 1M * 12500cc (5m price) = 12.5cc -> 12cc
        expect(result?.cost.cacheWriteCost).toBe(12n);
      }),
    );

    it.effect("should extract, normalize, and price 1h cache correctly", () =>
      Effect.gen(function* () {
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

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          responseBody,
        );

        expect(result).toBeDefined();
        // Store ACTUAL 1h tokens (no normalization): 1000
        expect(result?.usage.cacheWriteTokens).toBe(1000);
        // Cost in centi-cents: 1000 tokens * 1.6 multiplier / 1M * 12500cc (5m price) = 20cc
        expect(result?.cost.cacheWriteCost).toBe(20n);
      }),
    );

    it.effect(
      "should extract, normalize, and price mixed 5m + 1h cache tokens correctly",
      () =>
        Effect.gen(function* () {
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

          const result = yield* calculator.calculate(
            "claude-3-5-haiku-20241022",
            responseBody,
          );

          expect(result).toBeDefined();
          // Store ACTUAL tokens: 500 (5m) + 1000 (1h) = 1500
          expect(result?.usage.cacheWriteTokens).toBe(1500);
          // Cost in centi-cents: (500 * 1.0 + 1000 * 1.6) / 1M * 12500cc = 26.25cc -> 26cc
          expect(result?.cost.cacheWriteCost).toBe(26n);
        }),
    );

    it.effect(
      "should fall back to cacheWriteTokens if breakdown is all zeroes",
      () =>
        Effect.gen(function* () {
          const calculator = new AnthropicCostCalculator();
          const responseBody = {
            usage: {
              input_tokens: 100,
              output_tokens: 50,
              cache_creation_input_tokens: 1000,
              cache_read_input_tokens: 0,
              cache_creation: {
                ephemeral_5m_input_tokens: 0,
                ephemeral_1h_input_tokens: 0,
              },
            },
          };

          const result = yield* calculator.calculate(
            "claude-3-5-haiku-20241022",
            responseBody,
          );

          expect(result).toBeDefined();
          // Store ACTUAL 1h tokens (no normalization): 1000
          expect(result?.usage.cacheWriteTokens).toBe(1000);
          // Cost in centi-cents: 1000 tokens / 1M * 12500cc (5m price) = 12cc
          expect(result?.cost.cacheWriteCost).toBe(12n);
        }),
    );
  });

  describe("GoogleCostCalculator", () => {
    it.effect("should extract usage from Google response", () =>
      Effect.gen(function* () {
        const calculator = new GoogleCostCalculator();
        const responseBody = {
          candidates: [{ content: { parts: [{ text: "Hello" }] } }],
          usageMetadata: {
            promptTokenCount: 100,
            candidatesTokenCount: 50,
            totalTokenCount: 150,
          },
        };

        const result = yield* calculator.calculate(
          "gemini-2.0-flash-exp",
          responseBody,
        );

        expect(result).toBeDefined();
        expect(result?.usage.inputTokens).toBe(100);
        expect(result?.usage.outputTokens).toBe(50);
      }),
    );

    it.effect("should return null for null body", () =>
      Effect.gen(function* () {
        const calculator = new GoogleCostCalculator();
        const result = yield* calculator.calculate(
          "gemini-2.0-flash-exp",
          null,
        );

        expect(result).toBeNull();
      }),
    );

    it.effect("should return null for response without usageMetadata", () =>
      Effect.gen(function* () {
        const calculator = new GoogleCostCalculator();
        const responseBody = {
          candidates: [{ content: { parts: [{ text: "Hello" }] } }],
          // No usageMetadata field
        };

        const result = yield* calculator.calculate(
          "gemini-2.0-flash-exp",
          responseBody,
        );

        expect(result).toBeNull();
      }),
    );

    it.effect(
      "should return null for response with incomplete usageMetadata",
      () =>
        Effect.gen(function* () {
          const calculator = new GoogleCostCalculator();
          const responseBody = {
            usageMetadata: {
              // Missing required promptTokenCount and candidatesTokenCount
              totalTokenCount: 150,
            },
          };

          const result = yield* calculator.calculate(
            "gemini-2.0-flash-exp",
            responseBody,
          );

          expect(result).toBeNull();
        }),
    );

    it.effect("should extract cached tokens from Google response", () =>
      Effect.gen(function* () {
        const calculator = new GoogleCostCalculator();
        const responseBody = {
          usageMetadata: {
            promptTokenCount: 100,
            candidatesTokenCount: 50,
            totalTokenCount: 150,
            cachedContentTokenCount: 30,
          },
        };

        const result = yield* calculator.calculate(
          "gemini-2.0-flash-exp",
          responseBody,
        );

        expect(result).toBeDefined();
        expect(result?.usage.cacheReadTokens).toBe(30);
      }),
    );
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
    it.effect("should handle missing pricing data gracefully", () =>
      Effect.gen(function* () {
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

        const result = yield* calculator.calculate(
          "unknown-model",
          responseBody,
        );

        expect(result).toBeDefined();
        expect(result?.usage.inputTokens).toBe(1000);
        expect(result?.cost.totalCost).toBe(0n);
      }),
    );

    it.effect("should handle fetch errors gracefully", () =>
      Effect.gen(function* () {
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

        const result = yield* calculator.calculate("gpt-4o-mini", responseBody);

        expect(result).toBeDefined();
        expect(result?.cost.totalCost).toBe(0n);
      }),
    );
  });
});
