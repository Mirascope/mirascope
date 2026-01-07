import { describe, it, expect, beforeEach } from "vitest";
import {
  getSupportedProviders,
  isValidProvider,
  getProviderConfig,
  getProviderApiKey,
  getModelsDotDevProviderIds,
  getCostCalculator,
} from "@/api/router/providers";
import {
  OpenAICostCalculator,
  AnthropicCostCalculator,
  GoogleCostCalculator,
} from "@/api/router/cost-calculator";

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
    beforeEach(() => {
      // Clear environment variables
      delete process.env.OPENAI_API_KEY;
      delete process.env.ANTHROPIC_API_KEY;
      delete process.env.GEMINI_API_KEY;
    });

    it("should return OpenAI API key from environment", () => {
      process.env.OPENAI_API_KEY = "test-openai-key";
      expect(getProviderApiKey("openai")).toBe("test-openai-key");
    });

    it("should return Anthropic API key from environment", () => {
      process.env.ANTHROPIC_API_KEY = "test-anthropic-key";
      expect(getProviderApiKey("anthropic")).toBe("test-anthropic-key");
    });

    it("should return Google API key from environment", () => {
      process.env.GEMINI_API_KEY = "test-gemini-key";
      expect(getProviderApiKey("google")).toBe("test-gemini-key");
    });

    it("should return undefined when API key not set", () => {
      expect(getProviderApiKey("openai")).toBeUndefined();
      expect(getProviderApiKey("anthropic")).toBeUndefined();
      expect(getProviderApiKey("google")).toBeUndefined();
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
});
