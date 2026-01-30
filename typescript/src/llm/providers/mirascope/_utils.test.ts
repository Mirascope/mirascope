import { describe, it, expect, afterEach } from "vitest";

import { AnthropicProvider } from "@/llm/providers/anthropic";
import { GoogleProvider } from "@/llm/providers/google";
import {
  getDefaultRouterBaseUrl,
  extractModelScope,
  createUnderlyingProvider,
} from "@/llm/providers/mirascope/_utils";
import { OpenAIProvider } from "@/llm/providers/openai/provider";
import { resetProviderRegistry } from "@/llm/providers/registry";

describe("getDefaultRouterBaseUrl", () => {
  const originalEnv = process.env.MIRASCOPE_ROUTER_BASE_URL;

  afterEach(() => {
    if (originalEnv === undefined) {
      delete process.env.MIRASCOPE_ROUTER_BASE_URL;
    } else {
      process.env.MIRASCOPE_ROUTER_BASE_URL = originalEnv;
    }
  });

  it("returns default URL when env var is not set", () => {
    delete process.env.MIRASCOPE_ROUTER_BASE_URL;
    expect(getDefaultRouterBaseUrl()).toBe("https://mirascope.com/router/v2");
  });

  it("returns env var when set", () => {
    process.env.MIRASCOPE_ROUTER_BASE_URL = "https://custom.example.com";
    expect(getDefaultRouterBaseUrl()).toBe("https://custom.example.com");
  });
});

describe("extractModelScope", () => {
  it("extracts scope from model ID with slash", () => {
    expect(extractModelScope("openai/gpt-4")).toBe("openai");
    expect(extractModelScope("anthropic/claude-3-opus")).toBe("anthropic");
    expect(extractModelScope("google/gemini-pro")).toBe("google");
  });

  it("returns null for model ID without slash", () => {
    expect(extractModelScope("gpt-4")).toBeNull();
    expect(extractModelScope("claude-3")).toBeNull();
  });

  it("handles model IDs with multiple slashes", () => {
    expect(extractModelScope("provider/model/version")).toBe("provider");
  });
});

describe("createUnderlyingProvider", () => {
  afterEach(() => {
    resetProviderRegistry();
  });

  it("creates AnthropicProvider for anthropic scope", () => {
    const provider = createUnderlyingProvider(
      "anthropic",
      "test-key",
      "https://router.example.com",
    );
    expect(provider).toBeInstanceOf(AnthropicProvider);
  });

  it("creates GoogleProvider for google scope", () => {
    const provider = createUnderlyingProvider(
      "google",
      "test-key",
      "https://router.example.com",
    );
    expect(provider).toBeInstanceOf(GoogleProvider);
  });

  it("creates OpenAIProvider for openai scope", () => {
    const provider = createUnderlyingProvider(
      "openai",
      "test-key",
      "https://router.example.com",
    );
    expect(provider).toBeInstanceOf(OpenAIProvider);
  });

  it("uses shared provider cache from registry", () => {
    const provider1 = createUnderlyingProvider(
      "anthropic",
      "key1",
      "https://router.example.com",
    );
    const provider2 = createUnderlyingProvider(
      "anthropic",
      "key1",
      "https://router.example.com",
    );
    expect(provider1).toBe(provider2);
  });

  it("creates separate providers for different keys", () => {
    const provider1 = createUnderlyingProvider(
      "anthropic",
      "key1",
      "https://router.example.com",
    );
    const provider2 = createUnderlyingProvider(
      "anthropic",
      "key2",
      "https://router.example.com",
    );
    expect(provider1).not.toBe(provider2);
  });

  it("throws for unsupported provider scope", () => {
    expect(() =>
      createUnderlyingProvider("unknown", "key", "https://router.example.com"),
    ).toThrow(
      "Unsupported provider: unknown. Mirascope Router currently supports: anthropic, google, openai",
    );
  });

  it("clears cache via resetProviderRegistry", () => {
    const provider1 = createUnderlyingProvider(
      "anthropic",
      "key1",
      "https://router.example.com",
    );
    resetProviderRegistry();
    const provider2 = createUnderlyingProvider(
      "anthropic",
      "key1",
      "https://router.example.com",
    );
    expect(provider1).not.toBe(provider2);
  });
});
