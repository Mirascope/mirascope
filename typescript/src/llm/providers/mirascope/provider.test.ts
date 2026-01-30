import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import { user } from "@/llm/messages";
import { resetProviderRegistry } from "@/llm/providers/registry";

import { createUnderlyingProvider } from "./_utils";
import { MirascopeProvider } from "./provider";

vi.mock("./_utils", async (importOriginal) => {
  const actual = await importOriginal<typeof import("./_utils")>();
  return {
    ...actual,
    createUnderlyingProvider: vi.fn(),
  };
});

describe("MirascopeProvider", () => {
  const originalEnv = process.env.MIRASCOPE_API_KEY;
  const createMockStreamResponse = () => ({
    wrapChunkIterator: vi.fn(),
    text: () => "Hello!",
  });

  const mockUnderlyingProvider = {
    call: vi.fn(),
    stream: vi.fn(),
    contextCall: vi.fn(),
    contextStream: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    resetProviderRegistry();
    vi.mocked(createUnderlyingProvider).mockReturnValue(
      mockUnderlyingProvider as never,
    );
  });

  afterEach(() => {
    if (originalEnv === undefined) {
      delete process.env.MIRASCOPE_API_KEY;
    } else {
      process.env.MIRASCOPE_API_KEY = originalEnv;
    }
  });

  describe("constructor", () => {
    it("uses apiKey from init", () => {
      const provider = new MirascopeProvider({ apiKey: "test-key" });
      expect(provider.id).toBe("mirascope");
    });

    it("uses apiKey from environment", () => {
      process.env.MIRASCOPE_API_KEY = "env-key";
      const provider = new MirascopeProvider();
      expect(provider.id).toBe("mirascope");
    });

    it("throws when no apiKey is available", () => {
      delete process.env.MIRASCOPE_API_KEY;
      expect(() => new MirascopeProvider()).toThrow(
        "Mirascope API key not found",
      );
    });

    it("accepts custom baseURL", () => {
      const provider = new MirascopeProvider({
        apiKey: "test-key",
        baseURL: "https://custom.example.com",
      });
      expect(provider.id).toBe("mirascope");
    });
  });

  describe("call", () => {
    it("delegates to underlying provider", async () => {
      const mockResponse = { text: () => "Hello!" };
      mockUnderlyingProvider.call.mockResolvedValueOnce(mockResponse);

      const provider = new MirascopeProvider({ apiKey: "test-key" });
      const response = await provider.call({
        modelId: "openai/gpt-4",
        messages: [user("Hi")],
      });

      expect(response).toBe(mockResponse);
      expect(createUnderlyingProvider).toHaveBeenCalledWith(
        "openai",
        "test-key",
        "https://mirascope.com/router/v2",
      );
    });

    it("throws for invalid model ID format", async () => {
      const provider = new MirascopeProvider({ apiKey: "test-key" });
      await expect(
        provider.call({
          modelId: "gpt-4",
          messages: [user("Hi")],
        }),
      ).rejects.toThrow("Invalid model ID format: gpt-4");
    });
  });

  describe("stream", () => {
    it("delegates to underlying provider", async () => {
      const mockResponse = createMockStreamResponse();
      mockUnderlyingProvider.stream.mockResolvedValueOnce(mockResponse);

      const provider = new MirascopeProvider({ apiKey: "test-key" });
      const response = await provider.stream({
        modelId: "openai/gpt-4",
        messages: [user("Hi")],
      });

      expect(response).toBe(mockResponse);
      expect(mockResponse.wrapChunkIterator).toHaveBeenCalled();
    });

    it("throws for invalid model ID format", async () => {
      const provider = new MirascopeProvider({ apiKey: "test-key" });
      await expect(
        provider.stream({
          modelId: "gpt-4",
          messages: [user("Hi")],
        }),
      ).rejects.toThrow("Invalid model ID format: gpt-4");
    });
  });

  describe("contextCall", () => {
    it("delegates to underlying provider", async () => {
      const mockResponse = { text: () => "Hello!" };
      mockUnderlyingProvider.contextCall.mockResolvedValueOnce(mockResponse);

      const provider = new MirascopeProvider({ apiKey: "test-key" });
      const response = await provider.contextCall({
        ctx: { deps: {} } as never,
        modelId: "openai/gpt-4",
        messages: [user("Hi")],
      });

      expect(response).toBe(mockResponse);
    });

    it("throws for invalid model ID format", async () => {
      const provider = new MirascopeProvider({ apiKey: "test-key" });
      await expect(
        provider.contextCall({
          ctx: { deps: {} } as never,
          modelId: "gpt-4",
          messages: [user("Hi")],
        }),
      ).rejects.toThrow("Invalid model ID format: gpt-4");
    });
  });

  describe("contextStream", () => {
    it("delegates to underlying provider", async () => {
      const mockResponse = createMockStreamResponse();
      mockUnderlyingProvider.contextStream.mockResolvedValueOnce(mockResponse);

      const provider = new MirascopeProvider({ apiKey: "test-key" });
      const response = await provider.contextStream({
        ctx: { deps: {} } as never,
        modelId: "openai/gpt-4",
        messages: [user("Hi")],
      });

      expect(response).toBe(mockResponse);
      expect(mockResponse.wrapChunkIterator).toHaveBeenCalled();
    });

    it("throws for invalid model ID format", async () => {
      const provider = new MirascopeProvider({ apiKey: "test-key" });
      await expect(
        provider.contextStream({
          ctx: { deps: {} } as never,
          modelId: "gpt-4",
          messages: [user("Hi")],
        }),
      ).rejects.toThrow("Invalid model ID format: gpt-4");
    });
  });
});
