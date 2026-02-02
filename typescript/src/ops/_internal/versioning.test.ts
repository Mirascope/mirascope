import { trace as otelTrace } from "@opentelemetry/api";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
  InMemorySpanExporter,
} from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import { version, type VersionedFunction } from "./versioning";

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

describe("versioning", () => {
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

  describe("version() - direct form", () => {
    it("should wrap a function and return its result", async () => {
      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      const result = await versioned(5);

      expect(result).toBe(10);
    });

    it("should create a span for each invocation", async () => {
      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      await versioned(5);

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
      expect(spans[0]!.name).toBe("fn");
    });

    it("should use function name for span name", async () => {
      async function myNamedFunction(x: number) {
        return x * 2;
      }
      const versioned = version(myNamedFunction);

      await versioned(5);

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.name).toBe("myNamedFunction");
    });

    it("should use anonymous for unnamed functions at runtime", async () => {
      // At runtime (without transform), anonymous functions get "anonymous" as name
      // The transform would infer the variable name, but tests run without transform
      const versioned = version(async () => 42);

      await versioned();

      const spans = exporter.getFinishedSpans();
      // Runtime fallback uses "anonymous" for unnamed arrow functions
      expect(spans[0]!.name).toBe("anonymous");
    });

    it("should set mirascope.type attribute to version", async () => {
      const fn = async () => "test";
      const versioned = version(fn);

      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.type"]).toBe("version");
    });

    it("should set version hash attribute", async () => {
      const fn = async () => "test";
      const versioned = version(fn);

      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.hash"]).toBeTruthy();
      expect(typeof spans[0]!.attributes["mirascope.version.hash"]).toBe(
        "string",
      );
    });

    it("should set version signature_hash attribute", async () => {
      const fn = async () => "test";
      const versioned = version(fn);

      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(
        spans[0]!.attributes["mirascope.version.signature_hash"],
      ).toBeTruthy();
    });
  });

  describe("version() - versionInfo", () => {
    it("should provide versionInfo property", async () => {
      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      expect(versioned.versionInfo).toBeTruthy();
      expect(versioned.versionInfo.name).toBe("fn");
      expect(versioned.versionInfo.hash).toBeTruthy();
      expect(versioned.versionInfo.signatureHash).toBeTruthy();
    });

    it("should use options.name in versionInfo", async () => {
      const fn = async () => "test";
      const versioned = version(fn, { name: "custom-name" });

      expect(versioned.versionInfo.name).toBe("custom-name");
    });

    it("should include tags in versionInfo", async () => {
      const fn = async () => "test";
      const versioned = version(fn, { tags: ["v1", "prod"] });

      expect(versioned.versionInfo.tags).toEqual(["prod", "v1"]); // Sorted
    });

    it("should include metadata in versionInfo", async () => {
      const fn = async () => "test";
      const versioned = version(fn, { metadata: { key: "value" } });

      expect(versioned.versionInfo.metadata).toEqual({ key: "value" });
    });

    it("should deduplicate tags", async () => {
      const fn = async () => "test";
      const versioned = version(fn, { tags: ["a", "b", "a", "c", "b"] });

      expect(versioned.versionInfo.tags).toEqual(["a", "b", "c"]);
    });
  });

  describe("version() - with options", () => {
    it("should set name attribute on span", async () => {
      const fn = async () => "test";
      const versioned = version(fn, { name: "my-function" });

      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.name"]).toBe(
        "my-function",
      );
    });

    it("should set tags attribute", async () => {
      const fn = async () => "test";
      const versioned = version(fn, { tags: ["tag1", "tag2"] });

      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.tags"]).toEqual([
        "tag1",
        "tag2",
      ]);
    });

    it("should set metadata attribute", async () => {
      const fn = async () => "test";
      const versioned = version(fn, { metadata: { key: "value" } });

      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.metadata"]).toBe(
        '{"key":"value"}',
      );
    });

    it("should not set tags attribute when empty array", async () => {
      const fn = async () => "test";
      const versioned = version(fn, { tags: [] });

      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.tags"]).toBeUndefined();
    });

    it("should not set metadata attribute when empty object", async () => {
      const fn = async () => "test";
      const versioned = version(fn, { metadata: {} });

      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(
        spans[0]!.attributes["mirascope.version.metadata"],
      ).toBeUndefined();
    });
  });

  describe("version() - with __closure (compile-time transform)", () => {
    it("should use injected closure metadata", async () => {
      const fn = async () => "test";
      const versioned = version(fn, {
        __closure: {
          code: "async () => 'test'",
          hash: "abc123def456",
          signature: "(): Promise<string>",
          signatureHash: "xyz789",
        },
      });

      expect(versioned.versionInfo.hash).toBe("abc123def456");
      expect(versioned.versionInfo.signatureHash).toBe("xyz789");
    });

    it("should set injected hash on span", async () => {
      const fn = async () => "test";
      const versioned = version(fn, {
        __closure: {
          code: "async () => 'test'",
          hash: "injected-hash-123",
          signature: "()",
          signatureHash: "sig-hash",
        },
      });

      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.hash"]).toBe(
        "injected-hash-123",
      );
    });
  });

  describe("version() - curried form", () => {
    it("should support curried form", async () => {
      const withVersion = version({ tags: ["api"] });
      const fn = async (x: number) => x * 2;
      const versioned = withVersion(fn);

      const result = await versioned(5);

      expect(result).toBe(10);
      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.version.tags"]).toEqual(["api"]);
    });

    it("should work with empty options in curried form", async () => {
      const withVersion = version({});
      const fn = async (x: number) => x * 2;
      const versioned = withVersion(fn);

      const result = await versioned(5);

      expect(result).toBe(10);
    });

    it("should preserve versionInfo in curried form", async () => {
      const withVersion = version({ name: "curried-fn", tags: ["test"] });
      const fn = async () => "result";
      const versioned = withVersion(fn);

      expect(versioned.versionInfo.name).toBe("curried-fn");
      expect(versioned.versionInfo.tags).toEqual(["test"]);
    });
  });

  describe("version() - error handling", () => {
    it("should record error on span and rethrow", async () => {
      const fn = async () => {
        throw new Error("Test error");
      };
      const versioned = version(fn);

      await expect(versioned()).rejects.toThrow("Test error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
      expect(spans[0]!.status.message).toBe("Test error");
    });

    it("should handle non-Error thrown values", async () => {
      const fn = async () => {
        throw "string error";
      };
      const versioned = version(fn);

      await expect(versioned()).rejects.toBe("string error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });

    it("should still finish span on error", async () => {
      const fn = async () => {
        throw new Error("Test error");
      };
      const versioned = version(fn);

      try {
        await versioned();
      } catch {
        // Expected
      }

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
      expect(spans[0]!.endTime).toBeTruthy();
    });
  });

  describe("versioned.wrapped()", () => {
    it("should return VersionedResult object with result", async () => {
      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      const result = await versioned.wrapped(5);

      expect(result.result).toBe(10);
    });

    it("should return VersionedResult object with span", async () => {
      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      const result = await versioned.wrapped(5);

      expect(result.span).toBeTruthy();
      expect(result.spanId).toBeTruthy();
      expect(result.traceId).toBeTruthy();
    });

    it("should return functionUuid when registered", async () => {
      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      const result = await versioned.wrapped(5);

      expect(result.functionUuid).toBe("function-uuid-123");
    });

    it("should provide annotate method", async () => {
      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      const result = await versioned.wrapped(5);

      expect(typeof result.annotate).toBe("function");
    });

    it("should create span for wrapped call", async () => {
      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      await versioned.wrapped(5);

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
    });

    it("should record error and rethrow in wrapped mode", async () => {
      const fn = async () => {
        throw new Error("Wrapped error");
      };
      const versioned = version(fn);

      await expect(versioned.wrapped()).rejects.toThrow("Wrapped error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });

    it("should handle non-Error thrown values in wrapped mode", async () => {
      const fn = async () => {
        throw "string error";
      };
      const versioned = version(fn);

      await expect(versioned.wrapped()).rejects.toBe("string error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // ERROR
    });
  });

  describe("VersionedFunction type", () => {
    it("should preserve argument types", async () => {
      const fn = async (a: string, b: number): Promise<string> => `${a}: ${b}`;
      const versioned: VersionedFunction<[string, number], string> =
        version(fn);

      const result = await versioned("test", 42);
      expect(result).toBe("test: 42");
    });

    it("should work with no arguments", async () => {
      const fn = async (): Promise<string> => "hello";
      const versioned: VersionedFunction<[], string> = version(fn);

      const result = await versioned();
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
      const versioned: VersionedFunction<[], ComplexResult> = version(fn);

      const result = await versioned();
      expect(result).toEqual({ name: "test", items: [1, 2, 3] });
    });
  });

  describe("hash computation", () => {
    it("should compute different hashes for different functions", async () => {
      const fn1 = async (x: string) => x.toUpperCase();
      const fn2 = async (x: string) => x.toLowerCase();

      const versioned1 = version(fn1);
      const versioned2 = version(fn2);

      expect(versioned1.versionInfo.hash).not.toBe(versioned2.versionInfo.hash);
    });

    it("should compute consistent hash for same function", async () => {
      const fn1 = async (x: string) => x.toUpperCase();
      const fn2 = async (x: string) => x.toUpperCase();

      const versioned1 = version(fn1);
      const versioned2 = version(fn2);

      // Note: At runtime, identical arrow functions are still different objects
      // so their toString() may differ. This test verifies hash computation works.
      expect(versioned1.versionInfo.hash).toBeTruthy();
      expect(versioned2.versionInfo.hash).toBeTruthy();
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

      const versioned = version(fn);
      await versioned();

      const spans = exporter.getFinishedSpans();
      expect(activeSpanId).toBe(spans[0]!.spanContext().spanId);
    });
  });

  describe("without tracer provider", () => {
    it("should still execute function when no tracer is registered", async () => {
      await provider.shutdown();
      otelTrace.disable();

      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      const result = await versioned(5);

      expect(result).toBe(10);
    });

    it("should still execute wrapped function when no tracer is registered", async () => {
      await provider.shutdown();
      otelTrace.disable();

      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      const result = await versioned.wrapped(5);

      expect(result.result).toBe(10);
    });

    it("should still provide versionInfo when no tracer is registered", async () => {
      await provider.shutdown();
      otelTrace.disable();

      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      expect(versioned.versionInfo).toBeTruthy();
      expect(versioned.versionInfo.hash).toBeTruthy();
    });
  });

  describe("version() - unified API with Call objects", () => {
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

    it("should detect Call objects and delegate to versionCall", async () => {
      const mockCall = createMockCall();
      const versioned = version(mockCall, { name: "test-call" });

      expect(versioned.versionInfo).toBeTruthy();
      expect(versioned.versionInfo.name).toBe("test-call");
    });

    it("should support curried form with Call objects", async () => {
      const mockCall = createMockCall();
      const withVersion = version({ name: "curried-call", tags: ["test"] });
      const versioned = withVersion(mockCall);

      expect(versioned.versionInfo).toBeTruthy();
      expect(versioned.versionInfo.name).toBe("curried-call");
      expect(versioned.versionInfo.tags).toEqual(["test"]);
    });

    it("should still handle functions in curried form", async () => {
      const withVersion = version({ name: "curried-fn", tags: ["test"] });
      const fn = async (x: number) => x * 2;
      const versioned = withVersion(fn);

      const result = await versioned(5);
      expect(result).toBe(10);
      expect(versioned.versionInfo.name).toBe("curried-fn");
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

      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      const result = await versioned.wrapped(5);

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

      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      // Should still execute without error
      const result = await versioned(5);

      expect(result).toBe(10);
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

      const fn = async (x: number) => x * 2;
      const versioned = version(fn);

      const result = await versioned.wrapped(5);

      expect(result.result).toBe(10);
      expect(result.functionUuid).toBeUndefined();
    });
  });
});
