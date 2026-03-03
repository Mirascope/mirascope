import { trace } from "@opentelemetry/api";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
  InMemorySpanExporter,
} from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, beforeEach, afterEach } from "vitest";

import { Span } from "./spans";
import { createTrace, type Trace } from "./traced-functions";

describe("traced-functions", () => {
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
    trace.disable();
  });

  describe("createTrace()", () => {
    it("should create a Trace with result and span", () => {
      const span = new Span("test-span");
      span.start();

      const result = { data: "test-data" };
      const traced: Trace<typeof result> = createTrace(result, span);

      expect(traced.result).toBe(result);
      expect(traced.span).toBe(span);

      span.finish();
    });

    it("should expose spanId from the span", () => {
      const span = new Span("test-span");
      span.start();

      const traced = createTrace("result", span);

      // spanId should be available since tracer is configured
      expect(traced.spanId).toBeTruthy();
      expect(typeof traced.spanId).toBe("string");

      span.finish();
    });

    it("should expose traceId from the span", () => {
      const span = new Span("test-span");
      span.start();

      const traced = createTrace("result", span);

      // traceId should be available since tracer is configured
      expect(traced.traceId).toBeTruthy();
      expect(typeof traced.traceId).toBe("string");

      span.finish();
    });

    it("should return null spanId when span has no context", () => {
      const span = new Span("test-span");
      // Don't start the span - it won't have a context

      const traced = createTrace("result", span);

      expect(traced.spanId).toBeNull();
    });

    it("should return null traceId when span has no context", () => {
      const span = new Span("test-span");
      // Don't start the span - it won't have a context

      const traced = createTrace("result", span);

      expect(traced.traceId).toBeNull();
    });
  });

  describe("Trace.annotate()", () => {
    it("should set annotation attributes on the span", () => {
      const span = new Span("test-span");
      span.start();

      const traced = createTrace("result", span);

      traced.annotate({
        label: "pass",
        reasoning: "Looks good",
        metadata: { score: 0.95 },
      });

      // Verify span attributes were set by checking the exported span
      span.finish();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.annotation.label"]).toBe("pass");
      expect(spans[0]!.attributes["mirascope.annotation.reasoning"]).toBe(
        "Looks good",
      );
      expect(spans[0]!.attributes["mirascope.annotation.metadata"]).toBe(
        '{"score":0.95}',
      );
    });

    it("should handle fail label", () => {
      const span = new Span("test-span");
      span.start();

      const traced = createTrace("result", span);

      traced.annotate({
        label: "fail",
      });

      span.finish();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.annotation.label"]).toBe("fail");
      expect(
        spans[0]!.attributes["mirascope.annotation.reasoning"],
      ).toBeUndefined();
      expect(
        spans[0]!.attributes["mirascope.annotation.metadata"],
      ).toBeUndefined();
    });

    it("should not set attributes when spanId is null", () => {
      const span = new Span("test-span");
      // Don't start the span - no spanId

      const traced = createTrace("result", span);

      // Should not throw
      traced.annotate({ label: "pass" });
    });

    it("should handle undefined reasoning and metadata", () => {
      const span = new Span("test-span");
      span.start();

      const traced = createTrace("result", span);

      traced.annotate({ label: "pass" });

      span.finish();

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["mirascope.annotation.label"]).toBe("pass");
      expect(
        spans[0]!.attributes["mirascope.annotation.reasoning"],
      ).toBeUndefined();
      expect(
        spans[0]!.attributes["mirascope.annotation.metadata"],
      ).toBeUndefined();
    });
  });

  describe("Trace.tag()", () => {
    it("should throw NotImplementedError", async () => {
      const span = new Span("test-span");
      span.start();

      const traced = createTrace("result", span);

      await expect(traced.tag("tag1", "tag2")).rejects.toThrow(
        "tag() is not yet implemented. Tagging will be available in a future release.",
      );

      span.finish();
    });
  });

  describe("Trace.assign()", () => {
    it("should throw NotImplementedError", async () => {
      const span = new Span("test-span");
      span.start();

      const traced = createTrace("result", span);

      await expect(traced.assign("user@example.com")).rejects.toThrow(
        "assign() is not yet implemented. Assignment will be available in a future release.",
      );

      span.finish();
    });
  });

  describe("Trace interface", () => {
    it("should work with any result type", () => {
      const span = new Span("test-span");
      span.start();

      // Test with different types
      const stringTrace = createTrace("hello", span);
      expect(stringTrace.result).toBe("hello");

      const numberTrace = createTrace(42, span);
      expect(numberTrace.result).toBe(42);

      const objectTrace = createTrace({ key: "value" }, span);
      expect(objectTrace.result).toEqual({ key: "value" });

      const arrayTrace = createTrace([1, 2, 3], span);
      expect(arrayTrace.result).toEqual([1, 2, 3]);

      span.finish();
    });

    it("should preserve type information", () => {
      interface MyResult {
        name: string;
        count: number;
      }

      const span = new Span("test-span");
      span.start();

      const result: MyResult = { name: "test", count: 5 };
      const traced: Trace<MyResult> = createTrace(result, span);

      // TypeScript should know the type of result
      const name: string = traced.result.name;
      const count: number = traced.result.count;

      expect(name).toBe("test");
      expect(count).toBe(5);

      span.finish();
    });
  });
});
