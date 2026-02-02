import { trace as otelTrace } from "@opentelemetry/api";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
  InMemorySpanExporter,
} from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import { trace, type TracedFunction } from "./tracing";

// Mock the API client
vi.mock("@/api/client", () => ({
  getClient: vi.fn(() => ({
    annotations: {
      create: vi.fn().mockResolvedValue({ id: "annotation-123" }),
    },
  })),
}));

describe("tracing", () => {
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

  describe("trace() - direct form", () => {
    it("should wrap a function and return its result", async () => {
      const fn = async (x: number) => x * 2;
      const traced = trace(fn, { name: "double" });

      const result = await traced(5);

      expect(result).toBe(10);
    });

    it("should create a span for each invocation", async () => {
      const fn = async (x: number) => x * 2;
      const traced = trace(fn, { name: "double" });

      await traced(5);

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
      expect(spans[0]!.name).toBe("double");
    });

    it("should use provided name for span name", async () => {
      async function myNamedFunction(x: number) {
        return x * 2;
      }
      const traced = trace(myNamedFunction, { name: "customName" });

      await traced(5);

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.name).toBe("customName");
    });

    it("should require name option", async () => {
      const fn = async () => 42;
      // Runtime check - TypeScript overloads don't catch this at compile time
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      expect(() => trace(fn as any)).toThrow(
        "trace() requires options with a name",
      );
    });

    it("should set mirascope.type attribute", async () => {
      const fn = async () => "test";
      const traced = trace(fn, { name: "testFn" });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.type"]).toBe("trace");
    });

    it("should set argument types attribute", async () => {
      const fn = async (name: string, age: number) => `${name}: ${age}`;
      const traced = trace(fn, { name: "formatPerson" });

      await traced("Alice", 30);

      const spans = exporter.getFinishedSpans();
      const argTypes = JSON.parse(
        spans[0]!.attributes["mirascope.trace.arg_types"] as string,
      );
      expect(argTypes).toEqual({ name: "string", age: "number" });
    });

    it("should set argument values attribute", async () => {
      const fn = async (name: string, count: number) => `${name}: ${count}`;
      const traced = trace(fn, { name: "formatCount" });

      await traced("Alice", 30);

      const spans = exporter.getFinishedSpans();
      const argValues = JSON.parse(
        spans[0]!.attributes["mirascope.trace.arg_values"] as string,
      );
      expect(argValues).toEqual({ name: "Alice", count: 30 });
    });

    it("should set output attribute", async () => {
      const fn = async () => "test result";
      const traced = trace(fn, { name: "getResult" });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.output"]).toBe(
        "test result",
      );
    });

    it("should set output attribute for numbers", async () => {
      const fn = async () => 42;
      const traced = trace(fn, { name: "getNumber" });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.output"]).toBe("42");
    });

    it("should set output attribute for booleans", async () => {
      const fn = async () => true;
      const traced = trace(fn, { name: "getBool" });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.output"]).toBe("true");
    });

    it("should set output attribute for objects", async () => {
      const fn = async () => ({ key: "value" });
      const traced = trace(fn, { name: "getObject" });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.output"]).toBe(
        '{"key":"value"}',
      );
    });

    it("should not set output attribute for null", async () => {
      const fn = async () => null;
      const traced = trace(fn, { name: "getNull" });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.output"]).toBeUndefined();
    });

    it("should not set output attribute for undefined", async () => {
      const fn = async () => undefined;
      const traced = trace(fn, { name: "getUndefined" });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.output"]).toBeUndefined();
    });
  });

  describe("trace() - with options", () => {
    it("should set tags attribute", async () => {
      const fn = async () => "test";
      const traced = trace(fn, { name: "testFn", tags: ["tag1", "tag2"] });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.tags"]).toEqual([
        "tag1",
        "tag2",
      ]);
    });

    it("should set metadata attribute", async () => {
      const fn = async () => "test";
      const traced = trace(fn, { name: "testFn", metadata: { key: "value" } });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.metadata"]).toBe(
        '{"key":"value"}',
      );
    });

    it("should not set tags attribute when empty array", async () => {
      const fn = async () => "test";
      const traced = trace(fn, { name: "testFn", tags: [] });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.tags"]).toBeUndefined();
    });

    it("should not set metadata attribute when empty object", async () => {
      const fn = async () => "test";
      const traced = trace(fn, { name: "testFn", metadata: {} });

      await traced();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.metadata"]).toBeUndefined();
    });
  });

  describe("trace() - curried form", () => {
    it("should support curried form", async () => {
      const withTracing = trace({ name: "double", tags: ["api"] });
      const fn = async (x: number) => x * 2;
      const traced = withTracing(fn);

      const result = await traced(5);

      expect(result).toBe(10);
      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.trace.tags"]).toEqual(["api"]);
    });

    it("should use name from curried options", async () => {
      const withTracing = trace({ name: "curriedFn" });
      const fn = async (x: number) => x * 2;
      const traced = withTracing(fn);

      await traced(5);

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.name).toBe("curriedFn");
    });
  });

  describe("trace() - error handling", () => {
    it("should record error on span and rethrow", async () => {
      const fn = async () => {
        throw new Error("Test error");
      };
      const traced = trace(fn, { name: "errorFn" });

      await expect(traced()).rejects.toThrow("Test error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
      expect(spans[0]!.status.message).toBe("Test error");
    });

    it("should handle non-Error thrown values", async () => {
      const fn = async () => {
        throw "string error";
      };
      const traced = trace(fn, { name: "stringErrorFn" });

      await expect(traced()).rejects.toBe("string error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });

    it("should still finish span on error", async () => {
      const fn = async () => {
        throw new Error("Test error");
      };
      const traced = trace(fn, { name: "errorFn" });

      try {
        await traced();
      } catch {
        // Expected
      }

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
      // Span is finished (endTime is set)
      expect(spans[0]!.endTime).toBeTruthy();
    });
  });

  describe("traced.wrapped()", () => {
    it("should return Trace object with result", async () => {
      const fn = async (x: number) => x * 2;
      const traced = trace(fn, { name: "double" });

      const traceResult = await traced.wrapped(5);

      expect(traceResult.result).toBe(10);
    });

    it("should return Trace object with span", async () => {
      const fn = async (x: number) => x * 2;
      const traced = trace(fn, { name: "double" });

      const traceResult = await traced.wrapped(5);

      expect(traceResult.span).toBeTruthy();
      expect(traceResult.spanId).toBeTruthy();
      expect(traceResult.traceId).toBeTruthy();
    });

    it("should provide annotate method", async () => {
      const fn = async (x: number) => x * 2;
      const traced = trace(fn, { name: "double" });

      const traceResult = await traced.wrapped(5);

      expect(typeof traceResult.annotate).toBe("function");
    });

    it("should create span for wrapped call", async () => {
      const fn = async (x: number) => x * 2;
      const traced = trace(fn, { name: "double" });

      await traced.wrapped(5);

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
    });

    it("should record error and rethrow in wrapped mode", async () => {
      const fn = async () => {
        throw new Error("Wrapped error");
      };
      const traced = trace(fn, { name: "wrappedErrorFn" });

      await expect(traced.wrapped()).rejects.toThrow("Wrapped error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });

    it("should handle non-Error thrown values in wrapped mode", async () => {
      const fn = async () => {
        throw "string error";
      };
      const traced = trace(fn, { name: "stringErrorFn" });

      await expect(traced.wrapped()).rejects.toBe("string error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });
  });

  describe("TracedFunction type", () => {
    it("should preserve argument types", async () => {
      const fn = async (a: string, b: number): Promise<string> => `${a}: ${b}`;
      const traced: TracedFunction<[string, number], string> = trace(fn, {
        name: "formatArgs",
      });

      const result = await traced("test", 42);
      expect(result).toBe("test: 42");
    });

    it("should work with no arguments", async () => {
      const fn = async (): Promise<string> => "hello";
      const traced: TracedFunction<[], string> = trace(fn, {
        name: "sayHello",
      });

      const result = await traced();
      expect(result).toBe("hello");
    });

    it("should work with complex return types", async () => {
      interface ComplexResult {
        name: string;
        items: number[];
      }

      const fn = async (): Promise<ComplexResult> => ({
        name: "test",
        items: [1, 2, 3],
      });
      const traced: TracedFunction<[], ComplexResult> = trace(fn, {
        name: "getComplex",
      });

      const result = await traced();
      expect(result).toEqual({ name: "test", items: [1, 2, 3] });
    });
  });

  describe("context propagation", () => {
    it("should run within span context", async () => {
      let activeSpanId: string | undefined;

      const fn = async () => {
        const activeSpan = otelTrace.getActiveSpan();
        activeSpanId = activeSpan?.spanContext().spanId;
        return "result";
      };

      const traced = trace(fn, { name: "contextTest" });
      await traced();

      const spans = exporter.getFinishedSpans();
      expect(activeSpanId).toBe(spans[0]!.spanContext().spanId);
    });
  });

  describe("trace() - unified API with Call objects", () => {
    // Create a mock Call-like object
    function createMockCall() {
      // Use a named function for the template to avoid readonly name issue
      function mockTemplate({ query }: { query: string }) {
        return `Hello ${query}`;
      }
      const mockCall = Object.assign(async () => ({ text: () => "response" }), {
        call: async () => ({ text: () => "response" }),
        stream: async () => ({ text: () => "stream" }),
        template: mockTemplate,
        prompt: { template: mockTemplate },
      });
      return mockCall;
    }

    it("should detect Call objects and delegate to traceCall", async () => {
      const mockCall = createMockCall();
      const traced = trace(mockCall, { name: "mockCall", tags: ["test"] });

      // TracedCall has a `.call` property
      expect(traced.call).toBe(mockCall);
    });

    it("should require options when tracing a Call object", () => {
      const mockCall = createMockCall();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      expect(() => trace(mockCall as any)).toThrow(
        "trace() requires options with a name",
      );
    });

    it("should support curried form with Call objects", async () => {
      const mockCall = createMockCall();
      const withTracing = trace({
        name: "curriedCall",
        tags: ["curried-test"],
      });
      const traced = withTracing(mockCall);

      // TracedCall has a `.call` property
      expect(traced.call).toBe(mockCall);
    });

    it("should still handle functions in curried form", async () => {
      const withTracing = trace({ name: "double", tags: ["test"] });
      const fn = async (x: number) => x * 2;
      const traced = withTracing(fn);

      const result = await traced(5);
      expect(result).toBe(10);
    });
  });

  describe("without tracer provider", () => {
    it("should still execute function when no tracer is registered", async () => {
      // Shutdown and disable the tracer
      await provider.shutdown();
      otelTrace.disable();

      const fn = async (x: number) => x * 2;
      const traced = trace(fn, { name: "double" });

      const result = await traced(5);

      expect(result).toBe(10);
    });

    it("should still execute wrapped function when no tracer is registered", async () => {
      // Shutdown and disable the tracer
      await provider.shutdown();
      otelTrace.disable();

      const fn = async (x: number) => x * 2;
      const traced = trace(fn, { name: "double" });

      const traceResult = await traced.wrapped(5);

      expect(traceResult.result).toBe(10);
    });
  });
});
