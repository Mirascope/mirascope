import { trace as otelTrace } from "@opentelemetry/api";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
  InMemorySpanExporter,
} from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, beforeEach, afterEach } from "vitest";

import { Span } from "./spans";
import { createVersionedResult } from "./versioned-functions";

describe("versioned-functions", () => {
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
  });

  describe("createVersionedResult", () => {
    it("should create a VersionedResult with result", () => {
      const span = new Span("test").start();
      const result = createVersionedResult("test-result", span);

      expect(result.result).toBe("test-result");
      span.finish();
    });

    it("should include span reference", () => {
      const span = new Span("test").start();
      const result = createVersionedResult("test-result", span);

      expect(result.span).toBe(span);
      span.finish();
    });

    it("should include spanId and traceId", () => {
      const span = new Span("test").start();
      const result = createVersionedResult("test-result", span);

      expect(result.spanId).toBeTruthy();
      expect(result.traceId).toBeTruthy();
      span.finish();
    });

    describe("annotate", () => {
      it("should set annotation attributes on the span", () => {
        const span = new Span("test").start();
        const result = createVersionedResult("test-result", span);

        result.annotate({ label: "pass", reasoning: "Good result" });

        span.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["mirascope.annotation.label"]).toBe("pass");
        expect(spans[0]!.attributes["mirascope.annotation.reasoning"]).toBe(
          "Good result",
        );
      });

      it("should include metadata when provided", () => {
        const span = new Span("test").start();
        const result = createVersionedResult("test-result", span);

        result.annotate({
          label: "fail",
          metadata: { key: "value" },
        });

        span.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["mirascope.annotation.label"]).toBe("fail");
        expect(spans[0]!.attributes["mirascope.annotation.metadata"]).toBe(
          '{"key":"value"}',
        );
      });

      it("should not set attributes when spanId is null", () => {
        // Shutdown tracer to get null spanId
        provider.shutdown();
        otelTrace.disable();

        const span = new Span("test").start();
        const result = createVersionedResult("test-result", span);

        // Should not throw
        result.annotate({ label: "pass" });

        span.finish();
      });
    });

    describe("tag", () => {
      it("should throw NotImplementedError", async () => {
        const span = new Span("test").start();
        const result = createVersionedResult("test-result", span);

        await expect(result.tag("tag1", "tag2")).rejects.toThrow(
          "tag() is not yet implemented. Tagging will be available in a future release.",
        );

        span.finish();
      });
    });

    describe("assign", () => {
      it("should throw NotImplementedError", async () => {
        const span = new Span("test").start();
        const result = createVersionedResult("test-result", span);

        await expect(result.assign("user@example.com")).rejects.toThrow(
          "assign() is not yet implemented. Assignment will be available in a future release.",
        );

        span.finish();
      });
    });
  });
});
