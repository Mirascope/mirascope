import { trace, SpanKind, SpanStatusCode } from "@opentelemetry/api";
import { ExportResultCode } from "@opentelemetry/core";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
  InMemorySpanExporter,
  type ReadableSpan,
} from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import { MirascopeOTLPExporter } from "./mirascope-exporter";

describe("MirascopeOTLPExporter", () => {
  let provider: NodeTracerProvider;
  let memoryExporter: InMemorySpanExporter;
  let mockClient: {
    traces: { create: ReturnType<typeof vi.fn> };
  };

  beforeEach(() => {
    memoryExporter = new InMemorySpanExporter();
    provider = new NodeTracerProvider({
      spanProcessors: [new SimpleSpanProcessor(memoryExporter)],
    });
    provider.register();

    mockClient = {
      traces: {
        create: vi.fn().mockResolvedValue({}),
      },
    };
  });

  afterEach(async () => {
    await provider.shutdown();
    trace.disable();
    vi.clearAllMocks();
  });

  function createTestSpan(): ReadableSpan {
    const tracer = trace.getTracer("test");
    tracer.startActiveSpan("test-span", (span) => {
      span.setAttribute("test.attr", "value");
      span.addEvent("test-event", { "event.attr": "event-value" });
      span.end();
    });

    const spans = memoryExporter.getFinishedSpans();
    return spans[spans.length - 1]!;
  }

  describe("export()", () => {
    it("should export spans successfully", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const span = createTestSpan();

      const result = await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([span], resolve),
      );

      expect(result.code).toBe(ExportResultCode.SUCCESS);
      expect(mockClient.traces.create).toHaveBeenCalledTimes(1);
    });

    it("should succeed immediately for empty spans array", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const result = await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([], resolve),
      );

      expect(result.code).toBe(ExportResultCode.SUCCESS);
      expect(mockClient.traces.create).not.toHaveBeenCalled();
    });

    it("should succeed immediately after shutdown", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      await exporter.shutdown();

      const span = createTestSpan();
      const result = await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([span], resolve),
      );

      expect(result.code).toBe(ExportResultCode.SUCCESS);
      expect(mockClient.traces.create).not.toHaveBeenCalled();
    });

    it("should convert span attributes to OTLP format", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const span = createTestSpan();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([span], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      expect(call.resourceSpans).toBeDefined();
      expect(call.resourceSpans.length).toBeGreaterThan(0);

      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.name).toBe("test-span");
      expect(otlpSpan.traceId).toBeTruthy();
      expect(otlpSpan.spanId).toBeTruthy();
    });

    it("should convert span events to OTLP format", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const span = createTestSpan();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([span], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];

      expect(otlpSpan.events.length).toBe(1);
      expect(otlpSpan.events[0].name).toBe("test-event");
    });

    it("should handle events without attributes", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test-span", (span) => {
        span.addEvent("simple-event");
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      const span = spans[spans.length - 1]!;

      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([span], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.events[0].attributes).toEqual([]);
    });
  });

  describe("retry logic", () => {
    it("should retry on failure", async () => {
      mockClient.traces.create
        .mockRejectedValueOnce(new Error("Network error"))
        .mockResolvedValueOnce({});

      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
        3,
        10,
        100,
      );

      const span = createTestSpan();
      const result = await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([span], resolve),
      );

      expect(result.code).toBe(ExportResultCode.SUCCESS);
      expect(mockClient.traces.create).toHaveBeenCalledTimes(2);
    });

    it("should fail after max retries", async () => {
      mockClient.traces.create.mockRejectedValue(new Error("Network error"));

      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
        3,
        10,
        100,
      );

      const span = createTestSpan();
      const result = await new Promise<{
        code: ExportResultCode;
        error?: Error;
      }>((resolve) => exporter.export([span], resolve));

      expect(result.code).toBe(ExportResultCode.FAILED);
      expect(result.error).toBeDefined();
      expect(mockClient.traces.create).toHaveBeenCalledTimes(3);
    });

    it("should handle non-Error thrown values", async () => {
      mockClient.traces.create.mockRejectedValue("string error");

      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
        1,
        10,
        100,
      );

      const span = createTestSpan();
      const result = await new Promise<{
        code: ExportResultCode;
        error?: Error;
      }>((resolve) => exporter.export([span], resolve));

      expect(result.code).toBe(ExportResultCode.FAILED);
      expect(result.error?.message).toBe("string error");
    });

    it("should use exponential backoff with max delay", async () => {
      mockClient.traces.create
        .mockRejectedValueOnce(new Error("Error 1"))
        .mockRejectedValueOnce(new Error("Error 2"))
        .mockResolvedValueOnce({});

      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
        3,
        10,
        15,
      );

      const span = createTestSpan();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([span], resolve),
      );

      expect(mockClient.traces.create).toHaveBeenCalledTimes(3);
    });
  });

  describe("OTLP conversion", () => {
    it("should convert string attributes", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", (span) => {
        span.setAttribute("string.attr", "hello");
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const attrs = call.resourceSpans[0].scopeSpans[0].spans[0].attributes;
      const stringAttr = attrs.find(
        (a: { key: string }) => a.key === "string.attr",
      );
      expect(stringAttr?.value.stringValue).toBe("hello");
    });

    it("should convert integer attributes", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", (span) => {
        span.setAttribute("int.attr", 42);
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const attrs = call.resourceSpans[0].scopeSpans[0].spans[0].attributes;
      const intAttr = attrs.find((a: { key: string }) => a.key === "int.attr");
      expect(intAttr?.value.intValue).toBe("42");
    });

    it("should convert double attributes", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", (span) => {
        span.setAttribute("double.attr", 3.14);
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const attrs = call.resourceSpans[0].scopeSpans[0].spans[0].attributes;
      const doubleAttr = attrs.find(
        (a: { key: string }) => a.key === "double.attr",
      );
      expect(doubleAttr?.value.doubleValue).toBe(3.14);
    });

    it("should convert boolean attributes", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", (span) => {
        span.setAttribute("bool.attr", true);
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const attrs = call.resourceSpans[0].scopeSpans[0].spans[0].attributes;
      const boolAttr = attrs.find(
        (a: { key: string }) => a.key === "bool.attr",
      );
      expect(boolAttr?.value.boolValue).toBe(true);
    });

    it("should convert array attributes", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", (span) => {
        span.setAttribute("array.attr", ["a", "b", "c"]);
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const attrs = call.resourceSpans[0].scopeSpans[0].spans[0].attributes;
      const arrayAttr = attrs.find(
        (a: { key: string }) => a.key === "array.attr",
      );
      expect(arrayAttr?.value.arrayValue.values).toHaveLength(3);
    });

    it("should convert span kind INTERNAL", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", { kind: SpanKind.INTERNAL }, (span) => {
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.kind).toBe(1);
    });

    it("should convert span kind SERVER", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", { kind: SpanKind.SERVER }, (span) => {
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.kind).toBe(2);
    });

    it("should convert span kind CLIENT", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", { kind: SpanKind.CLIENT }, (span) => {
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.kind).toBe(3);
    });

    it("should convert span kind PRODUCER", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", { kind: SpanKind.PRODUCER }, (span) => {
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.kind).toBe(4);
    });

    it("should convert span kind CONSUMER", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", { kind: SpanKind.CONSUMER }, (span) => {
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.kind).toBe(5);
    });

    it("should convert OK status", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", (span) => {
        span.setStatus({ code: SpanStatusCode.OK });
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.status.code).toBe(1);
    });

    it("should convert ERROR status with message", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("test", (span) => {
        span.setStatus({ code: SpanStatusCode.ERROR, message: "test error" });
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[spans.length - 1]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.status.code).toBe(2);
      expect(otlpSpan.status.message).toBe("test error");
    });

    it("should include parentSpanId when present", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test");
      tracer.startActiveSpan("parent", (parentSpan) => {
        tracer.startActiveSpan("child", (childSpan) => {
          childSpan.end();
        });
        parentSpan.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      // Export only the child span
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([spans[0]!], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];
      expect(otlpSpan.parentSpanId).toBeTruthy();
    });

    it("should handle time conversion to nanoseconds", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const span = createTestSpan();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([span], resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      const otlpSpan = call.resourceSpans[0].scopeSpans[0].spans[0];

      expect(typeof otlpSpan.startTimeUnixNano).toBe("string");
      expect(typeof otlpSpan.endTimeUnixNano).toBe("string");
      expect(BigInt(otlpSpan.startTimeUnixNano)).toBeGreaterThan(0n);
      expect(BigInt(otlpSpan.endTimeUnixNano)).toBeGreaterThanOrEqual(
        BigInt(otlpSpan.startTimeUnixNano),
      );
    });
  });

  describe("shutdown()", () => {
    it("should set shutdown flag", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      await exporter.shutdown();

      const span = createTestSpan();
      const result = await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export([span], resolve),
      );

      expect(result.code).toBe(ExportResultCode.SUCCESS);
      expect(mockClient.traces.create).not.toHaveBeenCalled();
    });
  });

  describe("forceFlush()", () => {
    it("should return resolved promise", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      await expect(exporter.forceFlush()).resolves.toBeUndefined();
    });
  });

  describe("grouping spans", () => {
    it("should group spans by resource and scope", async () => {
      const exporter = new MirascopeOTLPExporter(
        mockClient as unknown as ConstructorParameters<
          typeof MirascopeOTLPExporter
        >[0],
      );

      const tracer = trace.getTracer("test-tracer", "1.0.0");
      tracer.startActiveSpan("span1", (span) => {
        span.end();
      });
      tracer.startActiveSpan("span2", (span) => {
        span.end();
      });

      const spans = memoryExporter.getFinishedSpans();
      await new Promise<{ code: ExportResultCode }>((resolve) =>
        exporter.export(spans, resolve),
      );

      const call = mockClient.traces.create.mock.calls[0]![0];
      expect(call.resourceSpans).toHaveLength(1);
      expect(call.resourceSpans[0].scopeSpans).toHaveLength(1);
      expect(call.resourceSpans[0].scopeSpans[0].spans).toHaveLength(2);
    });
  });
});
