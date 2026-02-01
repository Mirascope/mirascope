import { trace } from "@opentelemetry/api";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
  InMemorySpanExporter,
} from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, beforeEach, afterEach } from "vitest";

import { session } from "./session";
import { Span, span } from "./spans";

describe("spans", () => {
  let provider: NodeTracerProvider;
  let exporter: InMemorySpanExporter;

  beforeEach(() => {
    exporter = new InMemorySpanExporter();
    provider = new NodeTracerProvider({
      spanProcessors: [new SimpleSpanProcessor(exporter)],
    });
    trace.setGlobalTracerProvider(provider);
  });

  afterEach(async () => {
    await provider.shutdown();
    trace.disable();
  });

  describe("Span class", () => {
    describe("start()", () => {
      it("should create a span", () => {
        const s = new Span("test-span");
        s.start();
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans.length).toBe(1);
        expect(spans[0]!.name).toBe("test-span");
      });

      it("should return this for chaining", () => {
        const s = new Span("test-span");
        const result = s.start();
        expect(result).toBe(s);
        s.finish();
      });

      it("should set mirascope.type attribute", () => {
        const s = new Span("test-span");
        s.start();
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["mirascope.type"]).toBe("span");
      });

      it("should set initial attributes", () => {
        const s = new Span("test-span", { "initial.key": "value" });
        s.start();
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["initial.key"]).toBe("value");
      });
    });

    describe("set()", () => {
      it("should set string attributes", () => {
        const s = new Span("test-span");
        s.start();
        s.set({ key: "value" });
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["key"]).toBe("value");
      });

      it("should set number attributes", () => {
        const s = new Span("test-span");
        s.start();
        s.set({ count: 42 });
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["count"]).toBe(42);
      });

      it("should set boolean attributes", () => {
        const s = new Span("test-span");
        s.start();
        s.set({ enabled: true });
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["enabled"]).toBe(true);
      });

      it("should serialize object attributes", () => {
        const s = new Span("test-span");
        s.start();
        s.set({ data: { nested: "value" } });
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["data"]).toBe('{"nested":"value"}');
      });

      it("should not set attributes after finish", () => {
        const s = new Span("test-span");
        s.start();
        s.finish();
        s.set({ late: "attribute" });

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["late"]).toBeUndefined();
      });
    });

    describe("event()", () => {
      it("should add event to span", () => {
        const s = new Span("test-span");
        s.start();
        s.event("test-event", { key: "value" });
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.events.length).toBe(1);
        expect(spans[0]!.events[0]!.name).toBe("test-event");
        expect(spans[0]!.events[0]!.attributes?.["key"]).toBe("value");
      });

      it("should serialize object event attributes", () => {
        const s = new Span("test-span");
        s.start();
        s.event("test-event", { data: { nested: true } });
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.events[0]!.attributes?.["data"]).toBe(
          '{"nested":true}',
        );
      });
    });

    describe("logging methods", () => {
      it("debug() should add log event with debug level", () => {
        const s = new Span("test-span");
        s.start();
        s.debug("debug message");
        s.finish();

        const spans = exporter.getFinishedSpans();
        const event = spans[0]!.events[0]!;
        expect(event.name).toBe("log");
        expect(event.attributes?.["level"]).toBe("debug");
        expect(event.attributes?.["message"]).toBe("debug message");
      });

      it("info() should add log event with info level", () => {
        const s = new Span("test-span");
        s.start();
        s.info("info message");
        s.finish();

        const spans = exporter.getFinishedSpans();
        const event = spans[0]!.events[0]!;
        expect(event.attributes?.["level"]).toBe("info");
        expect(event.attributes?.["message"]).toBe("info message");
      });

      it("warning() should add log event with warning level", () => {
        const s = new Span("test-span");
        s.start();
        s.warning("warning message");
        s.finish();

        const spans = exporter.getFinishedSpans();
        const event = spans[0]!.events[0]!;
        expect(event.attributes?.["level"]).toBe("warning");
      });

      it("error() should add log event and set error status", () => {
        const s = new Span("test-span");
        s.start();
        s.error("error message");
        s.finish();

        const spans = exporter.getFinishedSpans();
        const event = spans[0]!.events[0]!;
        expect(event.attributes?.["level"]).toBe("error");
        expect(spans[0]!.status.code).toBe(2); // SpanStatusCode.ERROR
        expect(spans[0]!.status.message).toBe("error message");
      });

      it("critical() should add log event and set error status", () => {
        const s = new Span("test-span");
        s.start();
        s.critical("critical message");
        s.finish();

        const spans = exporter.getFinishedSpans();
        const event = spans[0]!.events[0]!;
        expect(event.attributes?.["level"]).toBe("critical");
        expect(spans[0]!.status.code).toBe(2); // SpanStatusCode.ERROR
      });

      it("should include additional attributes in log events", () => {
        const s = new Span("test-span");
        s.start();
        s.info("message", { extra: "data" });
        s.finish();

        const spans = exporter.getFinishedSpans();
        const event = spans[0]!.events[0]!;
        expect(event.attributes?.["extra"]).toBe("data");
      });
    });

    describe("finish()", () => {
      it("should end the span", () => {
        const s = new Span("test-span");
        s.start();
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans.length).toBe(1);
      });

      it("should be idempotent", () => {
        const s = new Span("test-span");
        s.start();
        s.finish();
        s.finish();
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(spans.length).toBe(1);
      });

      it("should set isFinished to true", () => {
        const s = new Span("test-span");
        s.start();
        expect(s.isFinished).toBe(false);
        s.finish();
        expect(s.isFinished).toBe(true);
      });
    });

    describe("getters", () => {
      it("spanId should return span ID after start", () => {
        const s = new Span("test-span");
        s.start();
        expect(s.spanId).toBeTruthy();
        expect(typeof s.spanId).toBe("string");
        s.finish();
      });

      it("traceId should return trace ID after start", () => {
        const s = new Span("test-span");
        s.start();
        expect(s.traceId).toBeTruthy();
        expect(typeof s.traceId).toBe("string");
        s.finish();
      });

      it("spanContext should return span context after start", () => {
        const s = new Span("test-span");
        s.start();
        const ctx = s.spanContext;
        expect(ctx).toBeTruthy();
        expect(ctx?.spanId).toBe(s.spanId);
        expect(ctx?.traceId).toBe(s.traceId);
        s.finish();
      });

      it("isNoop should be false when tracer is configured", () => {
        const s = new Span("test-span");
        s.start();
        expect(s.isNoop).toBe(false);
        s.finish();
      });

      it("otelSpan should return underlying span", () => {
        const s = new Span("test-span");
        s.start();
        expect(s.otelSpan).toBeTruthy();
        s.finish();
      });

      it("getters should return null before start", () => {
        const s = new Span("test-span");
        expect(s.spanId).toBeNull();
        expect(s.traceId).toBeNull();
        expect(s.spanContext).toBeNull();
        expect(s.otelSpan).toBeNull();
      });
    });

    describe("noop span behavior", () => {
      it("should create noop span when no tracer is configured", async () => {
        // Shutdown the provider to simulate no tracer configured
        await provider.shutdown();
        trace.disable();

        const s = new Span("test-span");
        s.start();

        expect(s.isNoop).toBe(true);
        expect(s.spanId).toBeNull();
        expect(s.otelSpan).toBeNull();

        // Operations should be no-ops
        s.set({ key: "value" });
        s.info("test message");
        s.error("error message");
        s.finish();

        expect(s.isFinished).toBe(true);
      });
    });

    describe("session integration", () => {
      it("should include session ID in span attributes", async () => {
        await session({ id: "test-session-123" }, async () => {
          const s = new Span("test-span");
          s.start();
          s.finish();
        });

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["mirascope.ops.session.id"]).toBe(
          "test-session-123",
        );
      });

      it("should include session attributes when present", async () => {
        await session(
          {
            id: "test-session",
            attributes: { userId: "user-123" },
          },
          async () => {
            const s = new Span("test-span");
            s.start();
            s.finish();
          },
        );

        const spans = exporter.getFinishedSpans();
        expect(spans[0]!.attributes["mirascope.ops.session.attributes"]).toBe(
          '{"userId":"user-123"}',
        );
      });

      it("should not include session attributes when no session", () => {
        const s = new Span("test-span");
        s.start();
        s.finish();

        const spans = exporter.getFinishedSpans();
        expect(
          spans[0]!.attributes["mirascope.ops.session.id"],
        ).toBeUndefined();
      });
    });
  });

  describe("span() helper", () => {
    it("should create and finish span around function", async () => {
      const result = await span("test-operation", async () => {
        return "result";
      });

      expect(result).toBe("result");

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
      expect(spans[0]!.name).toBe("test-operation");
    });

    it("should pass span to callback", async () => {
      await span("test-operation", async (s) => {
        s.set({ custom: "attribute" });
        s.info("inside span");
      });

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["custom"]).toBe("attribute");
      expect(spans[0]!.events.length).toBe(1);
    });

    it("should set initial attributes", async () => {
      await span("test-operation", async () => {}, { initial: "value" });

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.attributes["initial"]).toBe("value");
    });

    it("should log and rethrow errors", async () => {
      await expect(
        span("test-operation", async () => {
          throw new Error("test error");
        }),
      ).rejects.toThrow("test error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.status.code).toBe(2); // SpanStatusCode.ERROR
      expect(spans[0]!.events[0]!.attributes?.["level"]).toBe("error");
      expect(spans[0]!.events[0]!.attributes?.["message"]).toBe("test error");
    });

    it("should handle non-Error throws", async () => {
      await expect(
        span("test-operation", async () => {
          throw "string error";
        }),
      ).rejects.toBe("string error");

      const spans = exporter.getFinishedSpans();
      expect(spans[0]!.events[0]!.attributes?.["message"]).toBe("string error");
    });

    it("should finish span even on error", async () => {
      try {
        await span("test-operation", async () => {
          throw new Error("test");
        });
      } catch {
        // Expected
      }

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
    });

    it("should work with sync functions", async () => {
      const result = await span("sync-operation", () => {
        return 42;
      });

      expect(result).toBe(42);

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(1);
    });

    it("should support nested spans", async () => {
      await span("outer", async (outerSpan) => {
        outerSpan.info("outer start");
        await span("inner", async (innerSpan) => {
          innerSpan.info("inner");
        });
        outerSpan.info("outer end");
      });

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(2);

      const names = spans.map((s) => s.name);
      expect(names).toContain("outer");
      expect(names).toContain("inner");
    });
  });
});
