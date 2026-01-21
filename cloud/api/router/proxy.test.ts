import { describe, it, expect, vi, beforeEach } from "vitest";
import { Effect } from "effect";
import { proxyToProvider, extractProviderPath } from "@/api/router/proxy";
import { PROVIDER_CONFIGS } from "@/api/router/providers";
import { ProxyError } from "@/errors";
describe("Proxy", () => {
  describe("extractProviderPath", () => {
    it("should extract path for OpenAI", () => {
      const path = extractProviderPath(
        "/router/v2/openai/v1/chat/completions",
        "openai",
      );
      expect(path).toBe("v1/chat/completions");
    });
    it("should extract path for Anthropic", () => {
      const path = extractProviderPath(
        "/router/v2/anthropic/v1/messages",
        "anthropic",
      );
      expect(path).toBe("v1/messages");
    });
    it("should extract path for Google", () => {
      const path = extractProviderPath(
        "/router/v2/google/v1beta/models/gemini-pro:generateContent",
        "google",
      );
      expect(path).toBe("v1beta/models/gemini-pro:generateContent");
    });
    it("should return original path if prefix doesn't match", () => {
      const path = extractProviderPath("/some/other/path", "openai");
      expect(path).toBe("/some/other/path");
    });
  });
  describe("proxyToProvider", () => {
    beforeEach(() => {
      // Reset fetch mock before each test
      vi.restoreAllMocks();
    });
    it("should fail with ProxyError when API key is missing", async () => {
      const request = new Request(
        "http://localhost/router/v2/openai/v1/chat/completions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ model: "gpt-4", messages: [] }),
        },
      );
      const result = await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.openai,
            apiKey: "", // Empty API key should fail
          },
          "openai",
        ).pipe(Effect.flip),
      );
      expect(result).toBeInstanceOf(ProxyError);
      expect(result.message).toContain("API key not configured");
    });
    it("should proxy request successfully for non-streaming response", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        clone: () => ({
          text: () =>
            Promise.resolve(
              JSON.stringify({
                choices: [{ message: { content: "Hello" } }],
                usage: { prompt_tokens: 10, completion_tokens: 20 },
              }),
            ),
        }),
      };
      global.fetch = vi
        .fn()
        .mockResolvedValue(mockResponse) as unknown as typeof fetch;
      const request = new Request(
        "http://localhost/router/v2/openai/v1/chat/completions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer user-key",
          },
          body: JSON.stringify({ model: "gpt-4", messages: [] }),
        },
      );
      const result = await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.openai,
            apiKey: "test-key",
          },
          "openai",
        ),
      );
      expect(result.response).toBeDefined();
      expect(result.body).toBeDefined();
      expect(result.body).toHaveProperty("usage");
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining("https://api.openai.com/v1/chat/completions"),
        expect.objectContaining({
          method: "POST",
          headers: expect.any(Object) as Headers,
        }),
      );
    });
    it("should not parse body for streaming responses", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "text/event-stream" }),
        clone: () => ({
          text: () => Promise.resolve("data: test\n\n"),
        }),
      };
      global.fetch = vi
        .fn()
        .mockResolvedValue(mockResponse) as unknown as typeof fetch;
      const request = new Request(
        "http://localhost/router/v2/openai/v1/chat/completions",
        {
          method: "POST",
          body: JSON.stringify({ model: "gpt-4", messages: [], stream: true }),
        },
      );
      const result = await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.openai,
            apiKey: "test-key",
          },
          "openai",
        ),
      );
      expect(result.response).toBeDefined();
      expect(result.body).toBeNull();
    });
    it("should identify streaming responses and return stream format", async () => {
      const sseData = `data: {"id":"1","choices":[{"text":"Hello"}]}\n\ndata: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });
      const mockResponse = {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "text/event-stream" }),
        body: stream,
      };
      global.fetch = vi
        .fn()
        .mockResolvedValue(mockResponse) as unknown as typeof fetch;
      const request = new Request(
        "http://localhost/router/v2/openai/v1/chat/completions",
        {
          method: "POST",
          body: JSON.stringify({ model: "gpt-4", messages: [], stream: true }),
        },
      );
      const result = await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.openai,
            apiKey: "test-key",
          },
          "openai",
        ),
      );
      expect(result.response).toBeDefined();
      expect(result.body).toBeNull();
      expect(result.isStreaming).toBe(true);
      expect(result.streamFormat).toBe("sse");
      // Response should have the stream body
      expect(result.response.body).toBeDefined();
    });

    it("should identify NDJSON streaming responses", async () => {
      const ndjsonData = `{"id":"1","choices":[{"text":"Hello"}]}\n{"usage":{"prompt_tokens":10,"completion_tokens":5}}\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(ndjsonData));
          controller.close();
        },
      });
      const mockResponse = {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/x-ndjson" }),
        body: stream,
      };
      global.fetch = vi
        .fn()
        .mockResolvedValue(mockResponse) as unknown as typeof fetch;
      const request = new Request(
        "http://localhost/router/v2/google/v1beta/models/gemini-pro:streamGenerateContent",
        {
          method: "POST",
          body: JSON.stringify({ prompt: { text: "Hello" } }),
        },
      );
      const result = await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.google,
            apiKey: "test-key",
          },
          "google",
        ),
      );
      expect(result.response).toBeDefined();
      expect(result.body).toBeNull();
      expect(result.isStreaming).toBe(true);
      expect(result.streamFormat).toBe("ndjson");
      // Response should have the stream body
      expect(result.response.body).toBeDefined();
    });

    it("should handle response without content-type header", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        headers: new Headers(),
        clone: () => ({
          text: () => Promise.resolve(JSON.stringify({ result: "success" })),
        }),
      };
      global.fetch = vi
        .fn()
        .mockResolvedValue(mockResponse) as unknown as typeof fetch;
      const request = new Request(
        "http://localhost/router/v2/openai/v1/chat/completions",
        {
          method: "POST",
          body: JSON.stringify({ model: "gpt-4", messages: [] }),
        },
      );
      const result = await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.openai,
            apiKey: "test-key",
          },
          "openai",
        ),
      );
      expect(result.response).toBeDefined();
      expect(result.body).toEqual({ result: "success" });
    });
    it("should handle JSON parse errors gracefully", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        clone: () => ({
          text: () => Promise.resolve("invalid json"),
        }),
      };
      global.fetch = vi
        .fn()
        .mockResolvedValue(mockResponse) as unknown as typeof fetch;
      const request = new Request(
        "http://localhost/router/v2/openai/v1/chat/completions",
        {
          method: "POST",
          body: JSON.stringify({ model: "gpt-4", messages: [] }),
        },
      );
      const result = await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.openai,
            apiKey: "test-key",
          },
          "openai",
        ),
      );
      expect(result.response).toBeDefined();
      expect(result.body).toBeNull();
    });
    it("should fail when fetch throws an error", async () => {
      global.fetch = vi
        .fn()
        .mockRejectedValue(
          new Error("Network error"),
        ) as unknown as typeof fetch;
      const request = new Request(
        "http://localhost/router/v2/openai/v1/chat/completions",
        {
          method: "POST",
          body: JSON.stringify({ model: "gpt-4", messages: [] }),
        },
      );
      const result = await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.openai,
            apiKey: "test-key",
          },
          "openai",
        ).pipe(Effect.flip),
      );
      expect(result).toBeInstanceOf(ProxyError);
      expect(result.message).toContain("Failed to proxy request");
      expect(result.message).toContain("Network error");
    });
    it("should handle body reading errors gracefully", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        clone: () => ({
          text: () => Promise.reject(new Error("Failed to read body")),
        }),
      };
      global.fetch = vi
        .fn()
        .mockResolvedValue(mockResponse) as unknown as typeof fetch;
      const request = new Request(
        "http://localhost/router/v2/openai/v1/chat/completions",
        {
          method: "POST",
          body: JSON.stringify({ model: "gpt-4", messages: [] }),
        },
      );
      const result = await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.openai,
            apiKey: "test-key",
          },
          "openai",
        ),
      );
      expect(result.response).toBeDefined();
      expect(result.body).toBeNull();
    });
    it("should exclude authorization and host headers from forwarded request", async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        clone: () => ({
          text: () => Promise.resolve("{}"),
        }),
      };
      let capturedHeaders: Headers | undefined;
      global.fetch = vi
        .fn()
        .mockImplementation((_url, options: RequestInit | undefined) => {
          capturedHeaders = options?.headers as Headers;
          return Promise.resolve(mockResponse);
        }) as unknown as typeof fetch;
      const request = new Request(
        "http://localhost/router/v2/openai/v1/chat/completions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer user-key",
            Host: "localhost",
            "X-Custom": "value",
          },
          body: JSON.stringify({ model: "gpt-4", messages: [] }),
        },
      );
      await Effect.runPromise(
        proxyToProvider(
          request,
          {
            ...PROVIDER_CONFIGS.openai,
            apiKey: "test-key",
          },
          "openai",
        ),
      );
      expect(capturedHeaders?.get("authorization")).toBe("Bearer test-key");
      expect(capturedHeaders?.get("host")).toBeNull();
      expect(capturedHeaders?.get("content-type")).toBe("application/json");
      expect(capturedHeaders?.get("x-custom")).toBe("value");
    });
  });
  describe("PROVIDER_CONFIGS", () => {
    it("should have correct OpenAI configuration", () => {
      expect(PROVIDER_CONFIGS.openai.baseUrl).toBe("https://api.openai.com");
      expect(PROVIDER_CONFIGS.openai.authHeader).toBe("Authorization");
      expect(PROVIDER_CONFIGS.openai.authFormat("test-key")).toBe(
        "Bearer test-key",
      );
    });
    it("should have correct Anthropic configuration", () => {
      expect(PROVIDER_CONFIGS.anthropic.baseUrl).toBe(
        "https://api.anthropic.com",
      );
      expect(PROVIDER_CONFIGS.anthropic.authHeader).toBe("x-api-key");
      expect(PROVIDER_CONFIGS.anthropic.authFormat("test-key")).toBe(
        "test-key",
      );
    });
    it("should have correct Google configuration", () => {
      expect(PROVIDER_CONFIGS.google.baseUrl).toBe(
        "https://generativelanguage.googleapis.com",
      );
      expect(PROVIDER_CONFIGS.google.authHeader).toBe("x-goog-api-key");
      expect(PROVIDER_CONFIGS.google.authFormat("test-key")).toBe("test-key");
    });
  });
});
