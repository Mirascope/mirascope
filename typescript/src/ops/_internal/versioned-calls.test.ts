import { trace as otelTrace } from "@opentelemetry/api";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
  InMemorySpanExporter,
} from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import type { Call } from "@/llm/calls";
import type { AnyFormatInput } from "@/llm/formatting";
import type { Response } from "@/llm/responses";

import { versionCall, extractSignatureFromString } from "./versioned-calls";

// Mock the API client
vi.mock("@/api/client", () => ({
  getClient: vi.fn(() => ({
    annotations: {
      create: vi.fn().mockResolvedValue({ id: "annotation-123" }),
    },
    functions: {
      findbyhash: vi.fn().mockRejectedValue(new Error("Not found")),
      create: vi.fn().mockResolvedValue({ id: "function-uuid-123" }),
    },
  })),
}));

describe("versioned-calls", () => {
  let provider: NodeTracerProvider;
  let exporter: InMemorySpanExporter;

  beforeEach(() => {
    exporter = new InMemorySpanExporter();
    provider = new NodeTracerProvider({
      spanProcessors: [new SimpleSpanProcessor(exporter)],
    });
    provider.register();
  });

  afterEach(async () => {
    await provider.shutdown();
    otelTrace.disable();
    vi.clearAllMocks();
  });

  // Helper to create a mock Call
  function createMockCall<T, F extends AnyFormatInput>(
    callFn: (vars?: T) => Promise<Response<undefined>>,
    name?: string,
  ): Call<T, F> {
    const templateFn = function templateFn() {
      return "template";
    };
    Object.defineProperty(templateFn, "name", {
      value: name || "mockTemplate",
      writable: false,
      configurable: true,
    });
    const mockPrompt = {
      template: templateFn,
    };

    const call = Object.assign(callFn, {
      call: callFn,
      stream: vi.fn().mockResolvedValue({ textStream: async function* () {} }),
      prompt: mockPrompt,
      template: mockPrompt.template,
      model: {} as Call<T, F>["model"],
      defaultModel: {} as Call<T, F>["defaultModel"],
      tools: undefined,
      format: undefined,
    }) as unknown as Call<T, F>;

    return call;
  }

  // Helper to create a mock Response
  function createMockResponse(content: string): Response<undefined> {
    return {
      text: () => content,
      parse: () => undefined,
      rawContent: [],
      toolCalls: () => [],
      usage: { inputTokens: 10, outputTokens: 20 },
    } as unknown as Response<undefined>;
  }

  describe("versionCall() - direct form", () => {
    it("should wrap a call and return its response", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      const result = await versioned();

      expect(result).toBe(mockResponse);
    });

    it("should create a span for each invocation", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
      expect(spans[0]!.name).toBe("mockTemplate");
    });

    it("should set mirascope.type attribute to version", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.type"]).toBe("version");
    });

    it("should set call name attribute", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
        "myCallName",
      );

      const versioned = versionCall(mockCall);
      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.call.name"]).toBe("myCallName");
    });

    it("should set version hash attribute", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.hash"]).toBeTruthy();
    });

    it("should include variables in span attributes", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<{ city: string }, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      await versioned({ city: "London" });

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.call.variables"]).toBe(
        '{"city":"London"}',
      );
    });
  });

  describe("versionCall() - versionInfo", () => {
    it("should provide versionInfo property", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const versioned = versionCall(mockCall);

      expect(versioned.versionInfo).toBeTruthy();
      expect(versioned.versionInfo.name).toBe("mockTemplate");
      expect(versioned.versionInfo.hash).toBeTruthy();
    });

    it("should use options.name in versionInfo", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const versioned = versionCall(mockCall, { name: "custom-name" });

      expect(versioned.versionInfo.name).toBe("custom-name");
    });

    it("should include tags in versionInfo", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const versioned = versionCall(mockCall, { tags: ["v1", "prod"] });

      expect(versioned.versionInfo.tags).toEqual(["prod", "v1"]); // Sorted
    });
  });

  describe("versionCall() - with options", () => {
    it("should set name attribute on span", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const versioned = versionCall(mockCall, { name: "my-function" });
      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.name"]).toBe(
        "my-function",
      );
    });

    it("should set tags attribute", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const versioned = versionCall(mockCall, { tags: ["tag1", "tag2"] });
      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.tags"]).toEqual([
        "tag1",
        "tag2",
      ]);
    });

    it("should set metadata attribute", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const versioned = versionCall(mockCall, { metadata: { key: "value" } });
      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.metadata"]).toBe(
        '{"key":"value"}',
      );
    });

    it("should use injected __closure from compile-time transform", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      // Cast options with __closure (internal compile-time property)
      const options = {
        __closure: {
          code: "template code",
          hash: "injected-hash-123",
          signature: "()",
          signatureHash: "sig-hash",
        },
      };
      const versioned = versionCall(
        mockCall,
        options as unknown as { name?: string },
      );
      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.hash"]).toBe(
        "injected-hash-123",
      );
    });
  });

  describe("versionCall() - curried form", () => {
    it("should support curried form", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const withVersion = versionCall({ tags: ["api"] });
      const versioned = withVersion(mockCall);
      const result = await versioned();

      expect(result).toBe(mockResponse);
      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.tags"]).toEqual(["api"]);
    });
  });

  describe("versionCall() - error handling", () => {
    it("should record error on span and rethrow", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockRejectedValue(new Error("Test error")),
      );

      const versioned = versionCall(mockCall);

      await expect(versioned()).rejects.toThrow("Test error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
      expect(spans[0]!.status.message).toBe("Test error");
    });

    it("should handle non-Error thrown values", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockRejectedValue("string error"),
      );

      const versioned = versionCall(mockCall);

      await expect(versioned()).rejects.toBe("string error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });
  });

  describe("versioned.wrapped()", () => {
    it("should return VersionedResult object with result", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      const result = await versioned.wrapped();

      expect(result.result).toBe(mockResponse);
    });

    it("should return VersionedResult object with span", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      const result = await versioned.wrapped();

      expect(result.span).toBeTruthy();
      expect(result.spanId).toBeTruthy();
      expect(result.traceId).toBeTruthy();
    });

    it("should return functionUuid when registered", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      const result = await versioned.wrapped();

      expect(result.functionUuid).toBe("function-uuid-123");
    });

    it("should record error and rethrow in wrapped mode", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockRejectedValue(new Error("Wrapped error")),
      );

      const versioned = versionCall(mockCall);

      await expect(versioned.wrapped()).rejects.toThrow("Wrapped error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });
  });

  describe("versioned.stream()", () => {
    it("should call stream method on the underlying call", async () => {
      const mockStream = { textStream: async function* () {} };
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );
      mockCall.stream = vi.fn().mockResolvedValue(mockStream);

      const versioned = versionCall(mockCall);
      const result = await versioned.stream();

      expect(result).toBe(mockStream);
      expect(mockCall.stream).toHaveBeenCalled();
    });

    it("should create span for stream invocation", async () => {
      const mockStream = { textStream: async function* () {} };
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );
      mockCall.stream = vi.fn().mockResolvedValue(mockStream);

      const versioned = versionCall(mockCall);
      await versioned.stream();

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
      expect(spans[0]!.attributes["mirascope.type"]).toBe("version");
    });

    it("should record error on span for stream errors", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );
      mockCall.stream = vi.fn().mockRejectedValue(new Error("Stream error"));

      const versioned = versionCall(mockCall);

      await expect(versioned.stream()).rejects.toThrow("Stream error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });
  });

  describe("versioned.call property", () => {
    it("should expose the underlying call", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const versioned = versionCall(mockCall);

      expect(versioned.call).toBe(mockCall);
    });
  });

  describe("extractSignatureFromString", () => {
    it("should extract signature from arrow function", () => {
      const fnStr = "({ name }) => `Hello ${name}`";
      expect(extractSignatureFromString(fnStr)).toBe("({ name })");
    });

    it("should extract signature from async arrow function", () => {
      const fnStr = "async ({ id }) => await fetch(id)";
      expect(extractSignatureFromString(fnStr)).toBe("({ id })");
    });

    it("should extract signature from regular function declaration", () => {
      const fnStr = "function myFunc(a, b) { return a + b; }";
      expect(extractSignatureFromString(fnStr)).toBe("(a, b)");
    });

    it("should extract signature from anonymous function", () => {
      const fnStr = "function (x) { return x * 2; }";
      expect(extractSignatureFromString(fnStr)).toBe("(x)");
    });

    it("should extract signature from async function", () => {
      const fnStr = "async function getData(url) { return fetch(url); }";
      expect(extractSignatureFromString(fnStr)).toBe("(url)");
    });

    it("should handle arrow function with return type annotation", () => {
      const fnStr = "({ x }: Props): string => x.toString()";
      expect(extractSignatureFromString(fnStr)).toBe("({ x }: Props)");
    });

    it("should fall back to (...) for unrecognized patterns", () => {
      const fnStr = "someWeirdThing";
      expect(extractSignatureFromString(fnStr)).toBe("(...)");
    });
  });

  describe("signature extraction", () => {
    // Helper to create a mock Call with a custom template function
    function createMockCallWithTemplate<T, F extends AnyFormatInput>(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      templateFn: (...args: any[]) => any,
      name?: string,
    ): Call<T, F> {
      Object.defineProperty(templateFn, "name", {
        value: name || "mockTemplate",
        writable: false,
        configurable: true,
      });
      const mockPrompt = {
        template: templateFn,
      };

      const callFn = vi.fn().mockResolvedValue(createMockResponse("test"));
      const call = Object.assign(callFn, {
        call: callFn,
        stream: vi
          .fn()
          .mockResolvedValue({ textStream: async function* () {} }),
        prompt: mockPrompt,
        template: mockPrompt.template,
        model: {} as Call<T, F>["model"],
        defaultModel: {} as Call<T, F>["defaultModel"],
        tools: undefined,
        format: undefined,
      }) as unknown as Call<T, F>;

      return call;
    }

    it("should extract signature from regular function with params", async () => {
      // Use Function constructor to ensure we get a real function string representation
      // eslint-disable-next-line @typescript-eslint/no-implied-eval, no-new-func
      const templateFn = new Function(
        "query",
        'return "Hello " + query',
      ) as unknown as (query: string) => string;

      const mockCall = createMockCallWithTemplate<{ query: string }, undefined>(
        templateFn,
        "template",
      );

      const versioned = versionCall(mockCall);

      // The signature hash should be based on the actual signature, not "(...)"
      expect(versioned.versionInfo.signatureHash).toBeTruthy();
    });

    it("should extract signature from arrow function", async () => {
      const templateFn = ({ name }: { name: string }) => `Hello ${name}`;

      const mockCall = createMockCallWithTemplate<{ name: string }, undefined>(
        templateFn,
        "template",
      );

      const versioned = versionCall(mockCall);

      expect(versioned.versionInfo.signatureHash).toBeTruthy();
    });

    it("should extract signature from async function", async () => {
      const templateFn = async function template({ id }: { id: number }) {
        return `Item ${id}`;
      };

      const mockCall = createMockCallWithTemplate<{ id: number }, undefined>(
        templateFn,
        "template",
      );

      const versioned = versionCall(mockCall);

      expect(versioned.versionInfo.signatureHash).toBeTruthy();
    });
  });

  describe("function registration", () => {
    it("should use existing function when found by hash", async () => {
      const { getClient } = await import("@/api/client");
      const mockFindbyhash = vi.fn().mockResolvedValue({ id: "existing-uuid" });
      const mockCreate = vi.fn().mockResolvedValue({ id: "new-uuid" });
      vi.mocked(getClient).mockReturnValue({
        annotations: { create: vi.fn() },
        functions: {
          findbyhash: mockFindbyhash,
          create: mockCreate,
        },
      } as unknown as ReturnType<typeof getClient>);

      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const versioned = versionCall(mockCall);
      const result = await versioned.wrapped();

      expect(mockFindbyhash).toHaveBeenCalled();
      expect(mockCreate).not.toHaveBeenCalled();
      expect(result.functionUuid).toBe("existing-uuid");
    });

    it("should handle registration failure gracefully", async () => {
      const { getClient } = await import("@/api/client");
      vi.mocked(getClient).mockReturnValue({
        annotations: { create: vi.fn() },
        functions: {
          findbyhash: vi.fn().mockRejectedValue(new Error("Not found")),
          create: vi.fn().mockRejectedValue(new Error("API error")),
        },
      } as unknown as ReturnType<typeof getClient>);

      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      const result = await versioned();

      expect(result).toBe(mockResponse);
    });

    it("should handle registration failure in wrapped mode", async () => {
      const { getClient } = await import("@/api/client");
      vi.mocked(getClient).mockReturnValue({
        annotations: { create: vi.fn() },
        functions: {
          findbyhash: vi.fn().mockRejectedValue(new Error("Not found")),
          create: vi.fn().mockRejectedValue(new Error("API error")),
        },
      } as unknown as ReturnType<typeof getClient>);

      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const versioned = versionCall(mockCall);
      const result = await versioned.wrapped();

      expect(result.result).toBe(mockResponse);
      expect(result.functionUuid).toBeUndefined();
    });
  });
});
