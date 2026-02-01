/**
 * E2E tests for OpenAI-compatible providers (Together, Ollama).
 *
 * Tests verify that OpenAI-compatible providers work correctly
 * with the same API as the core providers.
 */

import { describe, expect, it } from "vitest";

import { OllamaProvider } from "@/llm/providers/ollama";
import { TogetherProvider } from "@/llm/providers/together";

describe("Together provider", () => {
  it("creates provider with default base URL", () => {
    // Store original env var
    const originalKey = process.env.TOGETHER_API_KEY;
    process.env.TOGETHER_API_KEY = "test-key";

    try {
      const provider = new TogetherProvider();
      expect(provider.id).toBe("together");
    } finally {
      if (originalKey !== undefined) {
        process.env.TOGETHER_API_KEY = originalKey;
      } else {
        delete process.env.TOGETHER_API_KEY;
      }
    }
  });

  it("creates provider with custom API key", () => {
    const provider = new TogetherProvider({ apiKey: "custom-key" });
    expect(provider.id).toBe("together");
  });

  it("creates provider with custom base URL", () => {
    const provider = new TogetherProvider({
      apiKey: "test-key",
      baseURL: "https://custom.together.xyz/v1",
    });
    expect(provider.id).toBe("together");
  });
});

describe("Ollama provider", () => {
  it("creates provider with default base URL", () => {
    const provider = new OllamaProvider();
    expect(provider.id).toBe("ollama");
  });

  it("creates provider with custom base URL", () => {
    const provider = new OllamaProvider({
      baseURL: "http://localhost:11435",
    });
    expect(provider.id).toBe("ollama");
  });
});
