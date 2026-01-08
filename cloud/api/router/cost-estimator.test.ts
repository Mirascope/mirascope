import { describe, it, expect, vi, beforeEach } from "vitest";
import { Effect } from "effect";
import { estimateCost } from "@/api/router/cost-estimator";
import { PricingUnavailableError } from "@/errors";
import * as pricing from "@/api/router/pricing";

describe("cost-estimator", () => {
  describe("estimateCost", () => {
    beforeEach(() => {
      vi.restoreAllMocks();
    });

    it("should estimate cost for OpenAI request with messages", async () => {
      const mockPricing = {
        input: 10, // $10 per million
        output: 30, // $30 per million
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const requestBody = {
        model: "gpt-4",
        messages: [
          { role: "user", content: "Hello world" }, // ~11 chars + 4 role = 15 chars = ~4 tokens
        ],
        max_tokens: 100,
      };

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "gpt-4",
          requestBody,
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0);
      expect(result.outputTokens).toBe(100);
      expect(result.cost).toBeGreaterThan(0);
    });

    it("should estimate cost for Anthropic request with multimodal content", async () => {
      const mockPricing = {
        input: 15,
        output: 75,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const requestBody = {
        model: "claude-3-opus-20240229",
        messages: [
          {
            role: "user",
            content: [
              { type: "text", text: "What's in this image?" },
              { type: "image", source: { type: "base64", data: "..." } },
            ],
          },
        ],
        max_tokens: 500,
      };

      const result = await Effect.runPromise(
        estimateCost({
          provider: "anthropic",
          modelId: "claude-3-opus-20240229",
          requestBody,
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0);
      expect(result.outputTokens).toBe(500);
      expect(result.cost).toBeGreaterThan(0);
    });

    it("should estimate cost for Google request with contents", async () => {
      const mockPricing = {
        input: 5,
        output: 15,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const requestBody = {
        contents: [
          {
            role: "user",
            parts: [{ text: "Hello from Google" }],
          },
        ],
        generationConfig: {
          maxOutputTokens: 200,
        },
      };

      const result = await Effect.runPromise(
        estimateCost({
          provider: "google",
          modelId: "gemini-pro",
          requestBody,
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0);
      expect(result.outputTokens).toBe(200);
      expect(result.cost).toBeGreaterThan(0);
    });

    it("should use default output tokens when max_tokens not specified", async () => {
      const mockPricing = {
        input: 10,
        output: 30,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const requestBody = {
        messages: [{ role: "user", content: "Hello" }],
      };

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "gpt-4",
          requestBody,
        }),
      );

      expect(result).toBeDefined();
      expect(result.outputTokens).toBe(1000); // DEFAULT_OUTPUT_TOKENS_ESTIMATE
    });

    it("should throw PricingUnavailableError when pricing returns null", async () => {
      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(null),
      );

      const requestBody = {
        messages: [{ role: "user", content: "Hello" }],
      };

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "unknown-model",
          requestBody,
        }).pipe(Effect.flip),
      );

      expect(result).toBeInstanceOf(PricingUnavailableError);
      expect((result as PricingUnavailableError).provider).toBe("openai");
      expect((result as PricingUnavailableError).model).toBe("unknown-model");
    });

    it("should throw PricingUnavailableError when pricing fails", async () => {
      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.fail(new Error("Pricing not found")),
      );

      const requestBody = {
        messages: [{ role: "user", content: "Hello" }],
      };

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "unknown-model",
          requestBody,
        }).pipe(Effect.flip),
      );

      expect(result).toBeInstanceOf(Error);
    });

    it("should handle empty request body", async () => {
      const mockPricing = {
        input: 10,
        output: 30,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "gpt-4",
          requestBody: {},
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0); // Fallback to stringifying
      expect(result.outputTokens).toBe(1000);
    });

    it("should handle null request body", async () => {
      const mockPricing = {
        input: 10,
        output: 30,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "gpt-4",
          requestBody: null,
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBe(0);
      expect(result.outputTokens).toBe(1000);
    });

    it("should handle Google request with null body", async () => {
      const mockPricing = {
        input: 5,
        output: 15,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "google",
          modelId: "gemini-pro",
          requestBody: null,
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBe(0);
      expect(result.outputTokens).toBe(1000);
    });

    it("should handle Google request with no contents or generationConfig", async () => {
      const mockPricing = {
        input: 5,
        output: 15,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "google",
          modelId: "gemini-pro",
          requestBody: { model: "gemini-pro" },
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0); // Falls back to stringify
      expect(result.outputTokens).toBe(1000); // Default
    });

    it("should handle Anthropic request with null body", async () => {
      const mockPricing = {
        input: 15,
        output: 75,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "anthropic",
          modelId: "claude-3-opus-20240229",
          requestBody: null,
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBe(0);
      expect(result.outputTokens).toBe(1000);
    });

    it("should handle Anthropic request with no messages", async () => {
      const mockPricing = {
        input: 15,
        output: 75,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "anthropic",
          modelId: "claude-3-opus-20240229",
          requestBody: { model: "claude-3-opus-20240229" },
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0); // Falls back to stringify
      expect(result.outputTokens).toBe(1000); // Default
    });

    it("should handle OpenAI request with no messages", async () => {
      const mockPricing = {
        input: 10,
        output: 30,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "gpt-4",
          requestBody: { model: "gpt-4" },
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0); // Falls back to stringify
      expect(result.outputTokens).toBe(1000); // Default
    });

    it("should handle OpenAI request with non-object body", async () => {
      const mockPricing = {
        input: 10,
        output: 30,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "gpt-4",
          requestBody: "invalid",
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBe(0); // Non-object returns 0
      expect(result.outputTokens).toBe(1000); // Default
    });

    it("should handle Anthropic request with non-object body", async () => {
      const mockPricing = {
        input: 15,
        output: 75,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "anthropic",
          modelId: "claude-3-opus-20240229",
          requestBody: 123,
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBe(0); // Non-object returns 0
      expect(result.outputTokens).toBe(1000); // Default
    });

    it("should handle Google request with non-object body", async () => {
      const mockPricing = {
        input: 5,
        output: 15,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "google",
          modelId: "gemini-pro",
          requestBody: true,
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBe(0); // Non-object returns 0
      expect(result.outputTokens).toBe(1000); // Default
    });

    it("should handle OpenAI request with non-string/non-array content", async () => {
      const mockPricing = {
        input: 10,
        output: 30,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "gpt-4",
          requestBody: {
            messages: [
              { role: "user", content: 123 }, // Non-string, non-array content
            ],
          },
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0); // Counts role
      expect(result.outputTokens).toBe(1000);
    });

    it("should handle message without role field", async () => {
      const mockPricing = {
        input: 10,
        output: 30,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "openai",
          modelId: "gpt-4",
          requestBody: {
            messages: [
              { content: "Hello world" }, // No role field
            ],
          },
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0);
      expect(result.outputTokens).toBe(1000);
    });

    it("should handle Google request with invalid maxOutputTokens", async () => {
      const mockPricing = {
        input: 5,
        output: 15,
      };

      vi.spyOn(pricing, "getModelPricing").mockReturnValue(
        Effect.succeed(mockPricing),
      );

      const result = await Effect.runPromise(
        estimateCost({
          provider: "google",
          modelId: "gemini-pro",
          requestBody: {
            contents: [{ role: "user", parts: [{ text: "Hello" }] }],
            generationConfig: {
              maxOutputTokens: 0, // Invalid (not > 0)
            },
          },
        }),
      );

      expect(result).toBeDefined();
      expect(result.inputTokens).toBeGreaterThan(0);
      expect(result.outputTokens).toBe(1000); // Should use default
    });
  });
});
