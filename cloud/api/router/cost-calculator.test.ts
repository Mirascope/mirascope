import { describe, it, expect, vi, beforeEach } from "@effect/vitest";
import { Effect } from "effect";
import assert from "node:assert";

import {
  OpenAICostCalculator,
  AnthropicCostCalculator,
  GoogleCostCalculator,
} from "@/api/router/cost-calculator";
import { clearPricingCache } from "@/api/router/pricing";
import { getCostCalculator } from "@/api/router/providers";

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
            prompt_tokens: 10000,
            completion_tokens: 5000,
            total_tokens: 15000,
          },
        };

        // Extract usage first
        const usage = calculator.extractUsage(responseBody);
        expect(usage).toBeDefined();
        expect(usage?.inputTokens).toBe(10000);
        expect(usage?.outputTokens).toBe(5000);
        expect(usage?.cacheReadTokens).toBeUndefined();

        // Then calculate cost
        const result = usage
          ? yield* calculator.calculate("gpt-4o-mini", usage)
          : null;

        expect(result).toBeDefined();
        expect(result?.totalCost).toBeGreaterThan(0n);
      }),
    );

    it("should return null for null body", () => {
      const calculator = new OpenAICostCalculator();
      const usage = calculator.extractUsage(null);

      expect(usage).toBeNull();
    });

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
            input_tokens: 10000,
            output_tokens: 5000,
            total_tokens: 15000,
          },
        };

        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        expect(usage.inputTokens).toBe(10000);
        expect(usage.outputTokens).toBe(5000);
        expect(usage.cacheReadTokens).toBeUndefined();

        const result = yield* calculator.calculate("gpt-4o-mini", usage);
        assert(result !== null);
        expect(result.totalCost).toBeGreaterThan(0n);
      }),
    );

    it.effect(
      "should extract cache tokens from OpenAI Completions API response",
      () =>
        Effect.gen(function* () {
          const calculator = new OpenAICostCalculator();
          const responseBody = {
            usage: {
              prompt_tokens: 10000,
              completion_tokens: 5000,
              total_tokens: 15000,
              prompt_tokens_details: {
                cached_tokens: 3000,
              },
            },
          };

          const usage = calculator.extractUsage(responseBody);
          assert(usage !== null);
          expect(usage.cacheReadTokens).toBe(3000);

          const result = yield* calculator.calculate("gpt-4o-mini", usage);
          assert(result !== null);
          expect(result.totalCost).toBeGreaterThan(0n);
        }),
    );

    it.effect(
      "should extract cache tokens from OpenAI Responses API response",
      () =>
        Effect.gen(function* () {
          const calculator = new OpenAICostCalculator();
          const responseBody = {
            usage: {
              input_tokens: 10000,
              output_tokens: 5000,
              total_tokens: 15000,
              input_tokens_details: {
                cached_tokens: 3000,
              },
            },
          };

          const usage = calculator.extractUsage(responseBody);
          assert(usage !== null);
          expect(usage.cacheReadTokens).toBe(3000);

          const result = yield* calculator.calculate("gpt-4o-mini", usage);
          assert(result !== null);
          expect(result.totalCost).toBeGreaterThan(0n);
        }),
    );

    it("should return null for invalid response body", () => {
      const calculator = new OpenAICostCalculator();
      const responseBody = { choices: [] }; // No usage

      const usage = calculator.extractUsage(responseBody);
      expect(usage).toBeNull();
    });

    it("should return null for response with invalid usage format", () => {
      const calculator = new OpenAICostCalculator();
      const responseBody = {
        usage: {
          // Missing both Completions and Responses API fields
          invalid_field: 100,
        },
      };

      const usage = calculator.extractUsage(responseBody);
      expect(usage).toBeNull();
    });

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

        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);

        const result = yield* calculator.calculate("gpt-4o-mini", usage);
        assert(result !== null);
        expect(result.inputCost).toBe(1n); // 1000 / 1M * 1500cc = 1.5cc -> 1cc (BIGINT truncation)
        expect(result.outputCost).toBe(3n); // 500 / 1M * 6000cc = 3cc
        expect(result.totalCost).toBe(4n);
      }),
    );

    it("should extract usage from OpenAI Responses API streaming chunk", () => {
      const calculator = new OpenAICostCalculator();
      const chunk = {
        type: "response.completed",
        response: {
          usage: {
            input_tokens: 100,
            output_tokens: 50,
          },
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.inputTokens).toBe(100);
      expect(usage?.outputTokens).toBe(50);
    });

    it("should extract usage with cache tokens from OpenAI Responses API streaming chunk", () => {
      const calculator = new OpenAICostCalculator();
      const chunk = {
        type: "response.completed",
        response: {
          usage: {
            input_tokens: 100,
            output_tokens: 50,
            input_tokens_details: {
              cached_tokens: 30,
            },
          },
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.inputTokens).toBe(100);
      expect(usage?.outputTokens).toBe(50);
      expect(usage?.cacheReadTokens).toBe(30);
    });

    it("should extract usage from OpenAI Completions API streaming chunk", () => {
      const calculator = new OpenAICostCalculator();
      const chunk = {
        usage: {
          prompt_tokens: 100,
          completion_tokens: 50,
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.inputTokens).toBe(100);
      expect(usage?.outputTokens).toBe(50);
    });

    it("should extract usage with cache tokens from OpenAI Completions API streaming chunk", () => {
      const calculator = new OpenAICostCalculator();
      const chunk = {
        usage: {
          prompt_tokens: 100,
          completion_tokens: 50,
          prompt_tokens_details: {
            cached_tokens: 30,
          },
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.inputTokens).toBe(100);
      expect(usage?.outputTokens).toBe(50);
      expect(usage?.cacheReadTokens).toBe(30);
    });

    it("should return null for OpenAI Responses API chunk without usage", () => {
      const calculator = new OpenAICostCalculator();
      const chunk = {
        type: "response.completed",
        response: {
          id: "resp_123",
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeNull();
    });

    it("should return null for null chunk", () => {
      const calculator = new OpenAICostCalculator();
      const usage = calculator.extractUsageFromStreamChunk(null);
      expect(usage).toBeNull();
    });

    it("should return null for non-object chunk", () => {
      const calculator = new OpenAICostCalculator();
      const usage = calculator.extractUsageFromStreamChunk("not an object");
      expect(usage).toBeNull();
    });
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

        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        expect(usage.inputTokens).toBe(100);
        expect(usage.outputTokens).toBe(50);

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          usage,
        );
        assert(result !== null);
        expect(result.totalCost).toBeGreaterThan(0n);
      }),
    );

    it("should return null for null body", () => {
      const calculator = new AnthropicCostCalculator();
      const usage = calculator.extractUsage(null);
      expect(usage).toBeNull();
    });

    it("should return null for response without usage", () => {
      const calculator = new AnthropicCostCalculator();
      const responseBody = {
        content: [{ type: "text", text: "Hello" }],
        // No usage field
      };

      const usage = calculator.extractUsage(responseBody);
      expect(usage).toBeNull();
    });

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

        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        expect(usage.inputTokens).toBe(100);
        expect(usage.cacheReadTokens).toBe(30);
        expect(usage.cacheWriteTokens).toBe(20);

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          usage,
        );
        assert(result !== null);
        expect(result.totalCost).toBeGreaterThan(0n);
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

        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        expect(usage.inputTokens).toBe(100);
        expect(usage.cacheReadTokens).toBeUndefined();
        expect(usage.cacheWriteTokens).toBeUndefined();

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          usage,
        );
        assert(result !== null);
        expect(result.totalCost).toBeGreaterThan(0n);
      }),
    );

    it.effect("should extract and price 5m cache correctly", () =>
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

        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        // 5m tokens remain 1:1, so cacheWriteTokens = 1000
        expect(usage.cacheWriteTokens).toBe(1000);

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          usage,
        );
        assert(result !== null);
        // Cost: 1000 tokens / 1M * 12500cc = 12cc
        expect(result.cacheWriteCost).toBe(12n);
      }),
    );

    it.effect("should extract and price 1h cache correctly", () =>
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

        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        // 1h tokens stored as actual count (no normalization)
        expect(usage.cacheWriteTokens).toBe(1000);

        const result = yield* calculator.calculate(
          "claude-3-5-haiku-20241022",
          usage,
        );
        assert(result !== null);
        // Cost: 1600 tokens / 1M * 12500cc = 20cc
        expect(result.cacheWriteCost).toBe(20n);
      }),
    );

    it.effect(
      "should extract and price mixed 5m + 1h cache tokens correctly",
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

          const usage = calculator.extractUsage(responseBody);
          assert(usage !== null);
          // Actual tokens: 500 (5m) + 1000 (1h) = 1500 (no normalization)
          expect(usage.cacheWriteTokens).toBe(1500);

          const result = yield* calculator.calculate(
            "claude-3-5-haiku-20241022",
            usage,
          );
          assert(result !== null);
          // Cost: 2100 tokens / 1M * 12500cc = 26cc
          expect(result.cacheWriteCost).toBe(26n);
        }),
    );

    it("should extract usage from Anthropic streaming chunk (message_stop)", () => {
      const calculator = new AnthropicCostCalculator();
      const chunk = {
        type: "message_stop",
        usage: {
          input_tokens: 100,
          output_tokens: 50,
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.inputTokens).toBe(100);
      expect(usage?.outputTokens).toBe(50);
    });

    it("should extract cumulative usage from Anthropic streaming chunk (message_delta)", () => {
      const calculator = new AnthropicCostCalculator();
      const chunk = {
        type: "message_delta",
        usage: {
          input_tokens: 100,
          output_tokens: 5,
          // Cumulative counts per Anthropic docs
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.inputTokens).toBe(100);
      expect(usage?.outputTokens).toBe(5);
    });

    it("should extract usage with cache tokens from Anthropic streaming chunk", () => {
      const calculator = new AnthropicCostCalculator();
      const chunk = {
        type: "message_stop",
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_read_input_tokens: 30,
          cache_creation_input_tokens: 20,
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.inputTokens).toBe(100);
      expect(usage?.outputTokens).toBe(50);
      expect(usage?.cacheReadTokens).toBe(30);
      expect(usage?.cacheWriteTokens).toBe(20);
    });

    it("should extract 5m cache tokens from Anthropic streaming chunk", () => {
      const calculator = new AnthropicCostCalculator();
      const chunk = {
        type: "message_stop",
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_creation: {
            ephemeral_5m_input_tokens: 500,
          },
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.cacheWriteTokens).toBe(500);
    });

    it("should extract 1h cache tokens from Anthropic streaming chunk", () => {
      const calculator = new AnthropicCostCalculator();
      const chunk = {
        type: "message_stop",
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_creation: {
            ephemeral_1h_input_tokens: 1000,
          },
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      // 1h tokens stored as actual count (no normalization)
      expect(usage?.cacheWriteTokens).toBe(1000);
    });

    it("should extract mixed 5m + 1h cache tokens from Anthropic streaming chunk", () => {
      const calculator = new AnthropicCostCalculator();
      const chunk = {
        type: "message_stop",
        usage: {
          input_tokens: 100,
          output_tokens: 50,
          cache_creation: {
            ephemeral_5m_input_tokens: 500,
            ephemeral_1h_input_tokens: 1000,
          },
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      // Actual tokens: 500 (5m) + 1000 (1h) = 1500 (no normalization)
      expect(usage?.cacheWriteTokens).toBe(1500);
    });
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

        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        expect(usage.inputTokens).toBe(100);
        expect(usage.outputTokens).toBe(50);

        const result = yield* calculator.calculate(
          "gemini-2.0-flash-exp",
          usage,
        );
        assert(result !== null);
        expect(result.totalCost).toBe(0n); // Free model
      }),
    );

    it("should return null for null body", () => {
      const calculator = new GoogleCostCalculator();
      const usage = calculator.extractUsage(null);
      expect(usage).toBeNull();
    });

    it("should return null for response without usageMetadata", () => {
      const calculator = new GoogleCostCalculator();
      const responseBody = {
        candidates: [{ content: { parts: [{ text: "Hello" }] } }],
        // No usageMetadata field
      };

      const usage = calculator.extractUsage(responseBody);
      expect(usage).toBeNull();
    });

    it("should return null for response with incomplete usageMetadata", () => {
      const calculator = new GoogleCostCalculator();
      const responseBody = {
        usageMetadata: {
          // Missing required promptTokenCount and candidatesTokenCount
          totalTokenCount: 150,
        },
      };

      const usage = calculator.extractUsage(responseBody);
      expect(usage).toBeNull();
    });

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

        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        expect(usage.cacheReadTokens).toBe(30);

        const result = yield* calculator.calculate(
          "gemini-2.0-flash-exp",
          usage,
        );
        assert(result !== null);
        expect(result.totalCost).toBe(0n); // Free model
      }),
    );

    it("should extract usage from Google streaming chunk", () => {
      const calculator = new GoogleCostCalculator();
      const chunk = {
        usageMetadata: {
          promptTokenCount: 100,
          candidatesTokenCount: 50,
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.inputTokens).toBe(100);
      expect(usage?.outputTokens).toBe(50);
    });

    it("should extract usage with cache tokens from Google streaming chunk", () => {
      const calculator = new GoogleCostCalculator();
      const chunk = {
        usageMetadata: {
          promptTokenCount: 100,
          candidatesTokenCount: 50,
          cachedContentTokenCount: 30,
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeDefined();
      expect(usage?.inputTokens).toBe(100);
      expect(usage?.outputTokens).toBe(50);
      expect(usage?.cacheReadTokens).toBe(30);
    });

    it("should return null for Google streaming chunk without usageMetadata", () => {
      const calculator = new GoogleCostCalculator();
      const chunk = {
        candidates: [{ content: { parts: [{ text: "Hello" }] } }],
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeNull();
    });

    it("should return null for Google streaming chunk with incomplete usageMetadata", () => {
      const calculator = new GoogleCostCalculator();
      const chunk = {
        usageMetadata: {
          totalTokenCount: 150,
          // Missing required promptTokenCount and candidatesTokenCount
        },
      };

      const usage = calculator.extractUsageFromStreamChunk(chunk);
      expect(usage).toBeNull();
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

        // Extract usage first
        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        expect(usage.inputTokens).toBe(1000);
        expect(usage.outputTokens).toBe(500);

        // Calculate returns null when pricing data is missing
        const result = yield* calculator.calculate("unknown-model", usage);
        expect(result).toBeNull();
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

        // Extract usage first
        const usage = calculator.extractUsage(responseBody);
        assert(usage !== null);
        expect(usage.inputTokens).toBe(1000);
        expect(usage.outputTokens).toBe(500);

        // Calculate returns null when fetch errors occur
        const result = yield* calculator.calculate("gpt-4o-mini", usage);
        expect(result).toBeNull();
      }),
    );

    it.effect("should handle decimal token values gracefully", () =>
      Effect.gen(function* () {
        const calculator = new OpenAICostCalculator();

        // Test with decimal tokens (BigInt constructor throws on decimals)
        const invalidUsage = {
          inputTokens: 100.5,
          outputTokens: 500,
        };

        const result = yield* calculator.calculate("gpt-4o-mini", invalidUsage);
        expect(result).toBeNull();
      }),
    );

    it.effect("should handle Infinity token values gracefully", () =>
      Effect.gen(function* () {
        const calculator = new OpenAICostCalculator();

        // Test with Infinity tokens (BigInt constructor throws on Infinity)
        const invalidUsage = {
          inputTokens: Infinity,
          outputTokens: 500,
        };

        const result = yield* calculator.calculate("gpt-4o-mini", invalidUsage);
        expect(result).toBeNull();
      }),
    );
  });
});
