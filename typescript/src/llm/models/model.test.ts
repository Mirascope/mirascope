import { afterEach, describe, expect, it } from "vitest";

import {
  MissingAPIKeyError,
  NoRegisteredProviderError,
} from "@/llm/exceptions";
import { Model, model } from "@/llm/models/model";
import {
  AnthropicProvider,
  registerProvider,
  resetProviderRegistry,
} from "@/llm/providers";

describe("Model", () => {
  afterEach(() => {
    resetProviderRegistry();
  });

  describe("constructor", () => {
    it("creates a model with valid model ID", () => {
      const m = new Model("anthropic/claude-sonnet-4-20250514");

      expect(m.modelId).toBe("anthropic/claude-sonnet-4-20250514");
      expect(m.params).toEqual({});
    });

    it("creates a model with params", () => {
      const m = new Model("anthropic/claude-sonnet-4-20250514", {
        temperature: 0.7,
        maxTokens: 1000,
      });

      expect(m.modelId).toBe("anthropic/claude-sonnet-4-20250514");
      expect(m.params).toEqual({ temperature: 0.7, maxTokens: 1000 });
    });

    it("throws error for invalid model ID format", () => {
      expect(() => new Model("invalid-model-id")).toThrow(
        /Invalid model_id format/,
      );
      expect(() => new Model("invalid-model-id")).toThrow(
        /Expected format: 'provider\/model-name'/,
      );
    });
  });

  describe("provider property", () => {
    it("returns registered provider for model", () => {
      const provider = new AnthropicProvider();
      registerProvider(provider, { scope: "anthropic/" });

      const m = new Model("anthropic/claude-sonnet-4-20250514");

      expect(m.provider).toBe(provider);
    });

    it("throws NoRegisteredProviderError for unknown provider", () => {
      const m = new Model("unknown/some-model");

      expect(() => m.provider).toThrow(NoRegisteredProviderError);
    });

    it("throws MissingAPIKeyError when API key not set", () => {
      // Reset to ensure no provider is registered
      resetProviderRegistry();
      // Clear the env vars if set
      const originalKey = process.env.ANTHROPIC_API_KEY;
      const originalMirascopeKey = process.env.MIRASCOPE_API_KEY;
      delete process.env.ANTHROPIC_API_KEY;
      delete process.env.MIRASCOPE_API_KEY;

      try {
        const m = new Model("anthropic/claude-sonnet-4-20250514");
        expect(() => m.provider).toThrow(MissingAPIKeyError);
      } finally {
        // Restore
        if (originalKey !== undefined) {
          process.env.ANTHROPIC_API_KEY = originalKey;
        }
        if (originalMirascopeKey !== undefined) {
          process.env.MIRASCOPE_API_KEY = originalMirascopeKey;
        }
      }
    });
  });

  describe("providerId property", () => {
    it("returns the provider ID", () => {
      const provider = new AnthropicProvider();
      registerProvider(provider, { scope: "anthropic/" });

      const m = new Model("anthropic/claude-sonnet-4-20250514");

      expect(m.providerId).toBe("anthropic");
    });
  });
});

describe("model helper", () => {
  it("creates a Model instance", () => {
    const m = model("anthropic/claude-sonnet-4-20250514");

    expect(m).toBeInstanceOf(Model);
    expect(m.modelId).toBe("anthropic/claude-sonnet-4-20250514");
  });

  it("passes params to Model", () => {
    const m = model("anthropic/claude-sonnet-4-20250514", {
      temperature: 0.5,
    });

    expect(m.params).toEqual({ temperature: 0.5 });
  });
});

describe("Model context methods", () => {
  afterEach(() => {
    resetProviderRegistry();
  });

  it("has contextCall method", () => {
    const m = new Model("anthropic/claude-sonnet-4-20250514");

    expect(typeof m.contextCall).toBe("function");
  });

  it("has contextStream method", () => {
    const m = new Model("anthropic/claude-sonnet-4-20250514");

    expect(typeof m.contextStream).toBe("function");
  });
});
