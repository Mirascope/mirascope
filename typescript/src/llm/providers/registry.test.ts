/**
 * Tests for the provider registry.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";

import {
  MissingAPIKeyError,
  NoRegisteredProviderError,
} from "@/llm/exceptions";
import { AnthropicProvider } from "@/llm/providers/anthropic";
import {
  registerProvider,
  getProviderForModel,
  resetProviderRegistry,
} from "@/llm/providers/registry";

describe("provider registry", () => {
  beforeEach(() => {
    resetProviderRegistry();
    vi.stubEnv("ANTHROPIC_API_KEY", "test-key");
    vi.stubEnv("GOOGLE_API_KEY", "test-google-key");
    vi.stubEnv("OPENAI_API_KEY", "test-openai-key");
    vi.stubEnv("TOGETHER_API_KEY", "test-together-key");
  });

  describe("registerProvider", () => {
    it("registers a provider instance with default scope", () => {
      const provider = new AnthropicProvider({ apiKey: "test" });
      registerProvider(provider);

      const result = getProviderForModel("anthropic/claude-sonnet-4-20250514");
      expect(result).toBe(provider);
    });

    it("registers a provider by ID", () => {
      const provider = registerProvider("anthropic");

      expect(provider.id).toBe("anthropic");
      const result = getProviderForModel("anthropic/claude-sonnet-4-20250514");
      expect(result).toBe(provider);
    });

    it("registers a provider with custom scope", () => {
      const provider = new AnthropicProvider({ apiKey: "test" });
      registerProvider(provider, { scope: "anthropic/claude-sonnet-4" });

      const result = getProviderForModel("anthropic/claude-sonnet-4-20250514");
      expect(result).toBe(provider);
    });

    it("registers a provider with multiple scopes", () => {
      const provider = new AnthropicProvider({ apiKey: "test" });
      registerProvider(provider, {
        scope: ["anthropic/claude-sonnet-4", "anthropic/claude-opus-4"],
      });

      expect(getProviderForModel("anthropic/claude-sonnet-4-20250514")).toBe(
        provider,
      );
      expect(getProviderForModel("anthropic/claude-opus-4-20250514")).toBe(
        provider,
      );
    });

    it("registers a provider by ID with apiKey option", () => {
      const provider = registerProvider("anthropic", { apiKey: "custom-key" });
      expect(provider.id).toBe("anthropic");
    });

    it("registers a provider by ID with baseURL option", () => {
      const provider = registerProvider("anthropic", {
        baseURL: "https://custom.api.com",
      });
      expect(provider.id).toBe("anthropic");
    });

    it("returns cached provider singleton", () => {
      const provider1 = registerProvider("anthropic", { apiKey: "key1" });
      const provider2 = registerProvider("anthropic", { apiKey: "key1" });
      expect(provider1).toBe(provider2);
    });

    it("creates different providers for different options", () => {
      const provider1 = registerProvider("anthropic", { apiKey: "key1" });
      const provider2 = registerProvider("anthropic", { apiKey: "key2" });
      expect(provider1).not.toBe(provider2);
    });

    it("throws for unknown provider ID", () => {
      expect(() => registerProvider("unknown" as "anthropic")).toThrow(
        "Unknown provider: 'unknown'",
      );
    });

    it("registers google provider by ID", () => {
      const provider = registerProvider("google");
      expect(provider.id).toBe("google");
    });

    it("registers google provider by ID with options", () => {
      const provider = registerProvider("google", {
        apiKey: "custom-key",
        baseURL: "https://custom.google.api.com",
      });
      expect(provider.id).toBe("google");
    });

    it("registers openai provider by ID", () => {
      const provider = registerProvider("openai");
      expect(provider.id).toBe("openai");
    });

    it("registers openai provider by ID with options", () => {
      const provider = registerProvider("openai", {
        apiKey: "custom-key",
        baseURL: "https://custom.openai.api.com",
      });
      expect(provider.id).toBe("openai");
    });

    it("registers mirascope provider by ID", () => {
      vi.stubEnv("MIRASCOPE_API_KEY", "test-mirascope-key");
      const provider = registerProvider("mirascope");
      expect(provider.id).toBe("mirascope");
    });

    it("registers mirascope provider by ID with options", () => {
      const provider = registerProvider("mirascope", {
        apiKey: "custom-key",
        baseURL: "https://custom.mirascope.api.com",
      });
      expect(provider.id).toBe("mirascope");
    });

    it("registers ollama provider by ID", () => {
      const provider = registerProvider("ollama");
      expect(provider.id).toBe("ollama");
    });

    it("registers ollama provider by ID with options", () => {
      const provider = registerProvider("ollama", {
        apiKey: "custom-key",
        baseURL: "http://custom.ollama.example.com/v1/",
      });
      expect(provider.id).toBe("ollama");
    });

    it("registers together provider by ID", () => {
      const provider = registerProvider("together");
      expect(provider.id).toBe("together");
    });

    it("registers together provider by ID with options", () => {
      const provider = registerProvider("together", {
        apiKey: "custom-key",
        baseURL: "https://custom.together.api.com",
      });
      expect(provider.id).toBe("together");
    });

    it("registers openrouter provider by ID", () => {
      vi.stubEnv("OPENROUTER_API_KEY", "test-openrouter-key");
      const provider = registerProvider("openrouter");
      expect(provider.id).toBe("openrouter");
    });

    it("registers openrouter provider by ID with options", () => {
      const provider = registerProvider("openrouter", {
        apiKey: "custom-key",
        baseURL: "https://custom.openrouter.api.com",
      });
      expect(provider.id).toBe("openrouter");
    });
  });

  describe("getProviderForModel", () => {
    it("finds provider by longest matching scope", () => {
      const generalProvider = new AnthropicProvider({ apiKey: "general" });
      const specificProvider = new AnthropicProvider({ apiKey: "specific" });

      registerProvider(generalProvider, { scope: "anthropic/" });
      registerProvider(specificProvider, {
        scope: "anthropic/claude-sonnet-4",
      });

      // Specific scope should win
      const result = getProviderForModel("anthropic/claude-sonnet-4-20250514");
      expect(result).toBe(specificProvider);

      // General scope for other models
      const result2 = getProviderForModel("anthropic/claude-opus-4-20250514");
      expect(result2).toBe(generalProvider);
    });

    it("auto-registers provider on first use", () => {
      // No explicit registration - should auto-register
      const provider = getProviderForModel(
        "anthropic/claude-sonnet-4-20250514",
      );
      expect(provider.id).toBe("anthropic");
    });

    it("auto-registers ollama provider without API key requirement", () => {
      // Ollama doesn't require an API key (apiKeyEnvVar is null)
      const provider = getProviderForModel("ollama/llama2");
      expect(provider.id).toBe("ollama");
    });

    it("throws NoRegisteredProviderError for unknown model prefix", () => {
      expect(() => getProviderForModel("unknown/model")).toThrow(
        NoRegisteredProviderError,
      );
    });

    it("throws MissingAPIKeyError when no API key available", () => {
      // Remove the API key from env
      const originalKey = process.env["ANTHROPIC_API_KEY"];
      delete process.env["ANTHROPIC_API_KEY"];

      try {
        expect(() =>
          getProviderForModel("anthropic/claude-sonnet-4-20250514"),
        ).toThrow(MissingAPIKeyError);
      } finally {
        // Restore the key
        if (originalKey !== undefined) {
          process.env["ANTHROPIC_API_KEY"] = originalKey;
        }
      }
    });
  });
});
