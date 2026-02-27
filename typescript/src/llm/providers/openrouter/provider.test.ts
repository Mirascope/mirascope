/**
 * Tests for OpenRouterProvider.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";

import { EMPTY_FEATURE_INFO } from "@/llm/providers/openai/completions/_utils/feature-info";
import { OpenRouterProvider } from "@/llm/providers/openrouter/provider";

describe("OpenRouterProvider", () => {
  const originalApiKey = process.env.OPENROUTER_API_KEY;

  beforeEach(() => {
    delete process.env.OPENROUTER_API_KEY;
  });

  afterEach(() => {
    if (originalApiKey === undefined) {
      delete process.env.OPENROUTER_API_KEY;
    } else {
      process.env.OPENROUTER_API_KEY = originalApiKey;
    }
  });

  it("initializes with correct id", () => {
    const provider = new OpenRouterProvider({ apiKey: "test-key" });
    expect(provider.id).toBe("openrouter");
  });

  it("uses OPENROUTER_API_KEY from environment", () => {
    process.env.OPENROUTER_API_KEY = "env-test-key";
    const provider = new OpenRouterProvider();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.apiKey).toBe("env-test-key");
  });

  it("uses custom api_key from init", () => {
    const provider = new OpenRouterProvider({ apiKey: "custom-key" });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.apiKey).toBe("custom-key");
  });

  it("prefers init api_key over environment", () => {
    process.env.OPENROUTER_API_KEY = "env-key";
    const provider = new OpenRouterProvider({ apiKey: "init-key" });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.apiKey).toBe("init-key");
  });

  it("uses default base_url", () => {
    const provider = new OpenRouterProvider({ apiKey: "test-key" });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.baseURL).toBe(
      "https://openrouter.ai/api/v1",
    );
  });

  it("uses custom base_url from init", () => {
    const provider = new OpenRouterProvider({
      apiKey: "test-key",
      baseURL: "https://custom.openrouter.ai/v1",
    });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    expect((provider as any).client.baseURL).toBe(
      "https://custom.openrouter.ai/v1",
    );
  });

  describe("modelName", () => {
    it("strips 'openrouter/' prefix from model_id", () => {
      const provider = new OpenRouterProvider({ apiKey: "test-key" });
      expect(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
        (provider as any).modelName("openrouter/openai/gpt-4"),
      ).toBe("openai/gpt-4");
    });

    it("passes through model_id without 'openrouter/' prefix", () => {
      const provider = new OpenRouterProvider({ apiKey: "test-key" });
      expect(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
        (provider as any).modelName("openai/gpt-4"),
      ).toBe("openai/gpt-4");
    });

    it("handles anthropic models", () => {
      const provider = new OpenRouterProvider({ apiKey: "test-key" });
      expect(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
        (provider as any).modelName("anthropic/claude-3-opus"),
      ).toBe("anthropic/claude-3-opus");
    });
  });

  describe("modelFeatureInfo", () => {
    it("returns OpenAI feature info for openai/ models", () => {
      const provider = new OpenRouterProvider({ apiKey: "test-key" });
      // gpt-4 doesn't support strict
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      const info = (provider as any).modelFeatureInfo("openai/gpt-4");
      // gpt-4 is in MODELS_WITHOUT_JSON_SCHEMA_SUPPORT
      expect(info.strictSupport).toBe(false);
      // gpt-4 is in NON_REASONING_MODELS
      expect(info.isReasoningModel).toBe(false);
    });

    it("returns OpenAI feature info for openrouter/openai/ models", () => {
      const provider = new OpenRouterProvider({ apiKey: "test-key" });
      // gpt-4o supports strict
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      const info = (provider as any).modelFeatureInfo(
        "openrouter/openai/gpt-4o",
      );
      expect(info.strictSupport).toBe(true);
      expect(info.isReasoningModel).toBe(false);
    });

    it("returns feature info for o1 as reasoning model", () => {
      const provider = new OpenRouterProvider({ apiKey: "test-key" });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      const info = (provider as any).modelFeatureInfo("openai/o1");
      expect(info.isReasoningModel).toBe(true);
    });

    it("returns empty info for non-openai models", () => {
      const provider = new OpenRouterProvider({ apiKey: "test-key" });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      const info = (provider as any).modelFeatureInfo(
        "anthropic/claude-3-opus",
      );
      expect(info).toBe(EMPTY_FEATURE_INFO);
    });

    it("returns empty info for openrouter/anthropic models", () => {
      const provider = new OpenRouterProvider({ apiKey: "test-key" });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      const info = (provider as any).modelFeatureInfo(
        "openrouter/anthropic/claude-3-opus",
      );
      expect(info).toBe(EMPTY_FEATURE_INFO);
    });

    it("returns empty info for meta-llama models", () => {
      const provider = new OpenRouterProvider({ apiKey: "test-key" });
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
      const info = (provider as any).modelFeatureInfo(
        "meta-llama/Llama-3.3-70B",
      );
      expect(info).toBe(EMPTY_FEATURE_INFO);
    });
  });
});
