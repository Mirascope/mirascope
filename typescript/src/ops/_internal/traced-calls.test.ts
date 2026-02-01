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

import { traceCall } from "./traced-calls";

// Mock the API client
vi.mock("@/api/client", () => ({
  getClient: vi.fn(() => ({
    annotations: {
      create: vi.fn().mockResolvedValue({ id: "annotation-123" }),
    },
  })),
}));

describe("traced-calls", () => {
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

  describe("traceCall() - direct form", () => {
    it("should wrap a call and return its response", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const traced = traceCall(mockCall);
      const result = await traced();

      expect(result).toBe(mockResponse);
    });

    it("should create a span for each invocation", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
        "testCall",
      );

      const traced = traceCall(mockCall);
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
      expect(spans[0]!.name).toBe("testCall");
    });

    it("should pass variables to the call", async () => {
      const mockCallFn = vi.fn().mockResolvedValue(createMockResponse("Hi!"));
      const mockCall = createMockCall<{ name: string }, undefined>(mockCallFn);

      const traced = traceCall(mockCall);
      await traced({ name: "Alice" });

      expect(mockCallFn).toHaveBeenCalledWith({ name: "Alice" });
    });

    it("should set mirascope.type attribute", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall);
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.type"]).toBe("trace");
    });

    it("should set call name attribute", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
        "myCallName",
      );

      const traced = traceCall(mockCall);
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.call.name"]).toBe("myCallName");
    });

    it("should set variables attribute", async () => {
      const mockCall = createMockCall<{ genre: string }, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall);
      await traced({ genre: "fantasy" });

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.call.variables"]).toBe(
        '{"genre":"fantasy"}',
      );
    });

    it("should not set variables attribute when undefined", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall);
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.call.variables"]).toBeUndefined();
    });
  });

  describe("traceCall() - with options", () => {
    it("should set tags attribute", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall, { tags: ["api", "v2"] });
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.tags"]).toEqual([
        "api",
        "v2",
      ]);
    });

    it("should set metadata attribute", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall, { metadata: { env: "prod" } });
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.metadata"]).toBe(
        '{"env":"prod"}',
      );
    });

    it("should not set tags when empty", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall, { tags: [] });
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.tags"]).toBeUndefined();
    });

    it("should not set metadata when empty", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall, { metadata: {} });
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.metadata"]).toBeUndefined();
    });
  });

  describe("traceCall() - curried form", () => {
    it("should support curried form", async () => {
      const withTracing = traceCall({ tags: ["curried"] });
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = withTracing(mockCall);
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.tags"]).toEqual(["curried"]);
    });
  });

  describe("traceCall() - error handling", () => {
    it("should record error on span and rethrow", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockRejectedValue(new Error("Call failed")),
      );

      const traced = traceCall(mockCall);

      await expect(traced()).rejects.toThrow("Call failed");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });

    it("should handle non-Error thrown values", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockRejectedValue("string error"),
      );

      const traced = traceCall(mockCall);

      await expect(traced()).rejects.toBe("string error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });
  });

  describe("traced.wrapped()", () => {
    it("should return Trace object with response", async () => {
      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const traced = traceCall(mockCall);
      const traceResult = await traced.wrapped();

      expect(traceResult.result).toBe(mockResponse);
    });

    it("should return Trace object with span info", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall);
      const traceResult = await traced.wrapped();

      expect(traceResult.spanId).toBeTruthy();
      expect(traceResult.traceId).toBeTruthy();
    });

    it("should provide annotate method", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall);
      const traceResult = await traced.wrapped();

      expect(typeof traceResult.annotate).toBe("function");
    });

    it("should record error and rethrow in wrapped mode", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockRejectedValue(new Error("Wrapped error")),
      );

      const traced = traceCall(mockCall);

      await expect(traced.wrapped()).rejects.toThrow("Wrapped error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });

    it("should handle non-Error thrown values in wrapped mode", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockRejectedValue("string error"),
      );

      const traced = traceCall(mockCall);

      await expect(traced.wrapped()).rejects.toBe("string error");
    });
  });

  describe("traced.stream()", () => {
    it("should call the stream method on the call", async () => {
      const mockStreamResponse = {
        textStream: async function* () {
          yield "chunk1";
        },
      };
      const mockStreamFn = vi.fn().mockResolvedValue(mockStreamResponse);
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );
      mockCall.stream = mockStreamFn;

      const traced = traceCall(mockCall);
      const result = await traced.stream();

      expect(result).toBe(mockStreamResponse);
      expect(mockStreamFn).toHaveBeenCalled();
    });

    it("should create a span for stream invocation", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
        "streamCall",
      );
      mockCall.stream = vi.fn().mockResolvedValue({});

      const traced = traceCall(mockCall);
      await traced.stream();

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
      expect(spans[0]!.name).toBe("streamCall");
    });

    it("should record error on stream failure", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );
      mockCall.stream = vi.fn().mockRejectedValue(new Error("Stream failed"));

      const traced = traceCall(mockCall);

      await expect(traced.stream()).rejects.toThrow("Stream failed");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });

    it("should handle non-Error thrown values in stream", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );
      mockCall.stream = vi.fn().mockRejectedValue("stream error");

      const traced = traceCall(mockCall);

      await expect(traced.stream()).rejects.toBe("stream error");
    });
  });

  describe("TracedCall.call property", () => {
    it("should expose the underlying call", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );

      const traced = traceCall(mockCall);

      expect(traced.call).toBe(mockCall);
    });
  });

  describe("context propagation", () => {
    it("should run within span context", async () => {
      let activeSpanId: string | undefined;

      const mockCallFn = vi.fn(async () => {
        const activeSpan = otelTrace.getActiveSpan();
        activeSpanId = activeSpan?.spanContext().spanId;
        return createMockResponse("test");
      });
      const mockCall = createMockCall<Record<string, never>, undefined>(
        mockCallFn,
      );

      const traced = traceCall(mockCall);
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(activeSpanId).toBe(spans[0]!.spanContext().spanId);
    });

    it("should run wrapped within span context", async () => {
      let activeSpanId: string | undefined;

      const mockCallFn = vi.fn(async () => {
        const activeSpan = otelTrace.getActiveSpan();
        activeSpanId = activeSpan?.spanContext().spanId;
        return createMockResponse("test");
      });
      const mockCall = createMockCall<Record<string, never>, undefined>(
        mockCallFn,
      );

      const traced = traceCall(mockCall);
      await traced.wrapped();

      const spans = exporter.getFinishedSpans();
      expect(activeSpanId).toBe(spans[0]!.spanContext().spanId);
    });

    it("should run stream within span context", async () => {
      let activeSpanId: string | undefined;

      const mockStreamFn = vi.fn(async () => {
        const activeSpan = otelTrace.getActiveSpan();
        activeSpanId = activeSpan?.spanContext().spanId;
        return {};
      });
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );
      mockCall.stream = mockStreamFn as unknown as typeof mockCall.stream;

      const traced = traceCall(mockCall);
      await traced.stream();

      const spans = exporter.getFinishedSpans();
      expect(activeSpanId).toBe(spans[0]!.spanContext().spanId);
    });
  });

  describe("call name extraction", () => {
    it("should use template name", async () => {
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
        "templateName",
      );

      const traced = traceCall(mockCall);
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.name).toBe("templateName");
    });

    it("should fallback to 'call' when no name available", async () => {
      const templateFn = function () {
        return "template";
      };
      Object.defineProperty(templateFn, "name", {
        value: "",
        writable: false,
        configurable: true,
      });
      const mockPrompt = {
        template: templateFn,
      };

      const baseFn = vi.fn().mockResolvedValue(createMockResponse("test"));
      // Also clear the name on the base function to ensure fallback to "call"
      Object.defineProperty(baseFn, "name", {
        value: "",
        writable: false,
        configurable: true,
      });

      const mockCall = Object.assign(baseFn, {
        call: vi.fn().mockResolvedValue(createMockResponse("test")),
        stream: vi.fn().mockResolvedValue({}),
        prompt: mockPrompt,
        template: mockPrompt.template,
        model: {},
        defaultModel: {},
        tools: undefined,
        format: undefined,
      }) as unknown as Call<Record<string, never>, undefined>;

      const traced = traceCall(mockCall);
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.name).toBe("call");
    });
  });

  describe("without tracer provider", () => {
    it("should still execute call when no tracer is registered", async () => {
      // Shutdown and disable the tracer
      await provider.shutdown();
      otelTrace.disable();

      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const traced = traceCall(mockCall);
      const result = await traced();

      expect(result).toBe(mockResponse);
    });

    it("should still execute wrapped call when no tracer is registered", async () => {
      // Shutdown and disable the tracer
      await provider.shutdown();
      otelTrace.disable();

      const mockResponse = createMockResponse("Hello!");
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(mockResponse),
      );

      const traced = traceCall(mockCall);
      const traceResult = await traced.wrapped();

      expect(traceResult.result).toBe(mockResponse);
    });

    it("should still execute stream when no tracer is registered", async () => {
      // Shutdown and disable the tracer
      await provider.shutdown();
      otelTrace.disable();

      const mockStreamResponse = { textStream: async function* () {} };
      const mockCall = createMockCall<Record<string, never>, undefined>(
        vi.fn().mockResolvedValue(createMockResponse("test")),
      );
      mockCall.stream = vi
        .fn()
        .mockResolvedValue(mockStreamResponse) as typeof mockCall.stream;

      const traced = traceCall(mockCall);
      const result = await traced.stream();

      expect(result).toBe(mockStreamResponse);
    });
  });
});
