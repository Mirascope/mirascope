import { describe, it, expect } from "vitest";

import {
  OpenAICostCalculator,
  AnthropicCostCalculator,
  GoogleCostCalculator,
} from "@/api/router/cost-calculator";
import {
  getSupportedProviders,
  isValidProvider,
  getProviderConfig,
  getProviderApiKey,
  getModelsDotDevProviderIds,
  getCostCalculator,
  extractModelId,
} from "@/api/router/providers";
import { createMockSettings } from "@/tests/settings";

describe("Providers", () => {
  describe("getSupportedProviders", () => {
    it("should return all supported provider names", () => {
      const providers = getSupportedProviders();
      expect(providers).toEqual(["anthropic", "google", "openai"]);
      expect(providers).toHaveLength(3);
    });
  });

  describe("isValidProvider", () => {
    it("should return true for valid providers", () => {
      expect(isValidProvider("openai")).toBe(true);
      expect(isValidProvider("anthropic")).toBe(true);
      expect(isValidProvider("google")).toBe(true);
    });

    it("should return false for invalid providers", () => {
      expect(isValidProvider("invalid")).toBe(false);
      expect(isValidProvider("")).toBe(false);
      expect(isValidProvider("cohere")).toBe(false);
    });
  });

  describe("getProviderConfig", () => {
    it("should return config for valid providers", () => {
      const openaiConfig = getProviderConfig("openai");
      expect(openaiConfig).toEqual({
        baseUrl: "https://api.openai.com",
        authHeader: "Authorization",
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        authFormat: expect.any(Function),
        modelsDotDevIds: ["openai"],
      });

      const anthropicConfig = getProviderConfig("anthropic");
      expect(anthropicConfig).toEqual({
        baseUrl: "https://api.anthropic.com",
        authHeader: "x-api-key",
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        authFormat: expect.any(Function),
        modelsDotDevIds: ["anthropic"],
      });

      const googleConfig = getProviderConfig("google");
      expect(googleConfig).toEqual({
        baseUrl: "https://generativelanguage.googleapis.com",
        authHeader: "x-goog-api-key",
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        authFormat: expect.any(Function),
        modelsDotDevIds: ["google", "google-ai-studio"],
      });
    });

    it("should return null for invalid provider", () => {
      expect(getProviderConfig("invalid")).toBeNull();
      expect(getProviderConfig("cohere")).toBeNull();
    });

    it("should have correct auth format functions", () => {
      const openaiConfig = getProviderConfig("openai");
      expect(openaiConfig?.authFormat("test-key")).toBe("Bearer test-key");

      const anthropicConfig = getProviderConfig("anthropic");
      expect(anthropicConfig?.authFormat("test-key")).toBe("test-key");

      const googleConfig = getProviderConfig("google");
      expect(googleConfig?.authFormat("test-key")).toBe("test-key");
    });
  });

  describe("getProviderApiKey", () => {
    it("should return OpenAI API key from settings", () => {
      const settings = createMockSettings({
        router: {
          openaiApiKey: "test-openai-key",
          anthropicApiKey: "test-anthropic-key",
          geminiApiKey: "test-gemini-key",
        },
      });
      expect(getProviderApiKey("openai", settings)).toBe("test-openai-key");
    });

    it("should return Anthropic API key from settings", () => {
      const settings = createMockSettings({
        router: {
          openaiApiKey: "test-openai-key",
          anthropicApiKey: "test-anthropic-key",
          geminiApiKey: "test-gemini-key",
        },
      });
      expect(getProviderApiKey("anthropic", settings)).toBe(
        "test-anthropic-key",
      );
    });

    it("should return Google API key from settings", () => {
      const settings = createMockSettings({
        router: {
          openaiApiKey: "test-openai-key",
          anthropicApiKey: "test-anthropic-key",
          geminiApiKey: "test-gemini-key",
        },
      });
      expect(getProviderApiKey("google", settings)).toBe("test-gemini-key");
    });
  });

  describe("getModelsDotDevProviderIds", () => {
    it("should return provider IDs for OpenAI", () => {
      expect(getModelsDotDevProviderIds("openai")).toEqual(["openai"]);
    });

    it("should return provider IDs for Anthropic", () => {
      expect(getModelsDotDevProviderIds("anthropic")).toEqual(["anthropic"]);
    });

    it("should return provider IDs for Google", () => {
      expect(getModelsDotDevProviderIds("google")).toEqual([
        "google",
        "google-ai-studio",
      ]);
    });
  });

  describe("getCostCalculator", () => {
    it("should return OpenAI cost calculator", () => {
      const calculator = getCostCalculator("openai");
      expect(calculator).toBeInstanceOf(OpenAICostCalculator);
    });

    it("should return Anthropic cost calculator", () => {
      const calculator = getCostCalculator("anthropic");
      expect(calculator).toBeInstanceOf(AnthropicCostCalculator);
    });

    it("should return Google cost calculator", () => {
      const calculator = getCostCalculator("google");
      expect(calculator).toBeInstanceOf(GoogleCostCalculator);
    });
  });

  describe("extractModelId", () => {
    describe("OpenAI provider", () => {
      it("should extract model from request body", () => {
        const request = new Request(
          "https://api.example.com/v1/chat/completions",
        );
        const parsedBody = { model: "gpt-4" };
        const modelId = extractModelId("openai", request, parsedBody);
        expect(modelId).toBe("gpt-4");
      });

      it("should return null when model field is missing", () => {
        const request = new Request(
          "https://api.example.com/v1/chat/completions",
        );
        const parsedBody = { messages: [] };
        const modelId = extractModelId("openai", request, parsedBody);
        expect(modelId).toBeNull();
      });

      it("should return null when body is not an object", () => {
        const request = new Request(
          "https://api.example.com/v1/chat/completions",
        );
        const modelId = extractModelId("openai", request, null);
        expect(modelId).toBeNull();
      });
    });

    describe("Anthropic provider", () => {
      it("should extract model from request body", () => {
        const request = new Request("https://api.anthropic.com/v1/messages");
        const parsedBody = { model: "claude-3-opus-20240229" };
        const modelId = extractModelId("anthropic", request, parsedBody);
        expect(modelId).toBe("claude-3-opus-20240229");
      });

      it("should return null when model field is missing", () => {
        const request = new Request("https://api.anthropic.com/v1/messages");
        const parsedBody = { messages: [] };
        const modelId = extractModelId("anthropic", request, parsedBody);
        expect(modelId).toBeNull();
      });
    });

    describe("Google provider", () => {
      it("should extract model from URL path with generateContent", () => {
        const request = new Request(
          "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        );
        const modelId = extractModelId("google", request, null);
        expect(modelId).toBe("gemini-2.0-flash");
      });

      it("should extract model from URL path with streamGenerateContent", () => {
        const request = new Request(
          "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:streamGenerateContent",
        );
        const modelId = extractModelId("google", request, null);
        expect(modelId).toBe("gemini-pro");
      });

      it("should extract model from URL path without action suffix", () => {
        const request = new Request(
          "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash",
        );
        const modelId = extractModelId("google", request, null);
        expect(modelId).toBe("gemini-flash");
      });

      it("should return null when URL format is invalid", () => {
        const request = new Request(
          "https://generativelanguage.googleapis.com/v1beta/invalid",
        );
        const modelId = extractModelId("google", request, null);
        expect(modelId).toBeNull();
      });
    });
  });
});
