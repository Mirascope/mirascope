import { trace, context as otelContext } from "@opentelemetry/api";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
  InMemorySpanExporter,
} from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

import {
  ContextPropagator,
  getPropagator,
  resetPropagator,
  extractContext,
  injectContext,
  propagatedContext,
} from "./propagation";
import { session, SESSION_HEADER_NAME } from "./session";
import { Span } from "./spans";

describe("propagation", () => {
  let provider: NodeTracerProvider;
  let exporter: InMemorySpanExporter;

  beforeEach(() => {
    exporter = new InMemorySpanExporter();
    provider = new NodeTracerProvider({
      spanProcessors: [new SimpleSpanProcessor(exporter)],
    });
    // Use register() instead of setGlobalTracerProvider to also set up context manager
    provider.register();
    resetPropagator();
  });

  afterEach(async () => {
    await provider.shutdown();
    trace.disable();
    resetPropagator();
    vi.unstubAllEnvs();
  });

  describe("ContextPropagator", () => {
    describe("constructor", () => {
      it("should create with default tracecontext format", () => {
        const propagator = new ContextPropagator(false);
        expect(propagator.format).toBe("tracecontext");
      });

      it("should use MIRASCOPE_PROPAGATOR env var", () => {
        vi.stubEnv("MIRASCOPE_PROPAGATOR", "b3");
        const propagator = new ContextPropagator(false);
        expect(propagator.format).toBe("b3");
      });

      it("should use provided format", () => {
        const propagator = new ContextPropagator(false, "jaeger");
        expect(propagator.format).toBe("jaeger");
      });

      it("should support b3multi format", () => {
        const propagator = new ContextPropagator(false, "b3multi");
        expect(propagator.format).toBe("b3multi");
      });

      it("should support composite format", () => {
        const propagator = new ContextPropagator(false, "composite");
        expect(propagator.format).toBe("composite");
      });

      it("should default to tracecontext for unknown format", () => {
        // Cast to bypass TypeScript's type checking for testing the default case
        const propagator = new ContextPropagator(
          false,
          "unknown" as "tracecontext",
        );
        // The format will be stored as-is, but the propagator created will be W3C
        expect(propagator.format).toBe("unknown");
      });
    });

    describe("extractContext()", () => {
      it("should extract W3C trace context headers", () => {
        const propagator = new ContextPropagator(true, "tracecontext");
        const headers = {
          traceparent:
            "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
        };

        const ctx = propagator.extractContext(headers);
        expect(ctx).toBeTruthy();
      });

      it("should handle array header values", () => {
        const propagator = new ContextPropagator(true, "tracecontext");
        const headers = {
          traceparent: [
            "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
          ],
        };

        const ctx = propagator.extractContext(headers);
        expect(ctx).toBeTruthy();
      });

      it("should handle empty headers", () => {
        const propagator = new ContextPropagator(true, "tracecontext");
        const ctx = propagator.extractContext({});
        expect(ctx).toBeTruthy();
      });
    });

    describe("injectContext()", () => {
      it("should inject trace context into headers when span is active", () => {
        const propagator = new ContextPropagator(true, "tracecontext");
        const tracer = trace.getTracer("test");

        // Use startActiveSpan to properly set the active context
        tracer.startActiveSpan("test-span", (span) => {
          const headers: Record<string, string> = {};
          propagator.injectContext(headers);

          // Traceparent should be injected
          expect(headers.traceparent).toBeTruthy();
          expect(headers.traceparent).toMatch(
            /^00-[a-f0-9]{32}-[a-f0-9]{16}-0[0-3]$/,
          );

          span.end();
        });
      });

      it("should inject context with explicit context parameter", () => {
        const propagator = new ContextPropagator(true, "tracecontext");
        const tracer = trace.getTracer("test");

        const span = tracer.startSpan("test-span");
        const ctx = trace.setSpan(otelContext.active(), span);

        const headers: Record<string, string> = {};
        propagator.injectContext(headers, ctx);

        expect(headers.traceparent).toBeTruthy();

        span.end();
      });

      it("should inject session ID when session is active", async () => {
        const propagator = new ContextPropagator(true, "tracecontext");

        await session({ id: "test-session-123" }, async () => {
          const headers: Record<string, string> = {};
          propagator.injectContext(headers);

          expect(headers[SESSION_HEADER_NAME]).toBe("test-session-123");
        });
      });

      it("should not inject session ID when no session", () => {
        const propagator = new ContextPropagator(true, "tracecontext");
        const headers: Record<string, string> = {};
        propagator.injectContext(headers);

        expect(headers[SESSION_HEADER_NAME]).toBeUndefined();
      });
    });
  });

  describe("getPropagator()", () => {
    it("should return singleton instance", () => {
      const p1 = getPropagator();
      const p2 = getPropagator();
      expect(p1).toBe(p2);
    });

    it("should create new instance after reset", () => {
      const p1 = getPropagator();
      resetPropagator();
      const p2 = getPropagator();
      expect(p1).not.toBe(p2);
    });
  });

  describe("resetPropagator()", () => {
    it("should clear the singleton", () => {
      const p1 = getPropagator();
      resetPropagator();
      const p2 = getPropagator();
      expect(p1).not.toBe(p2);
    });
  });

  describe("extractContext()", () => {
    it("should use global propagator", () => {
      const headers = {
        traceparent: "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
      };

      const ctx = extractContext(headers);
      expect(ctx).toBeTruthy();
    });
  });

  describe("injectContext()", () => {
    it("should use global propagator with active span", () => {
      const tracer = trace.getTracer("test");

      tracer.startActiveSpan("test-span", (span) => {
        const headers: Record<string, string> = {};
        injectContext(headers);

        expect(headers.traceparent).toBeTruthy();

        span.end();
      });
    });

    it("should inject session ID", async () => {
      await session({ id: "my-session" }, async () => {
        const headers: Record<string, string> = {};
        injectContext(headers);

        expect(headers[SESSION_HEADER_NAME]).toBe("my-session");
      });
    });
  });

  describe("propagatedContext()", () => {
    it("should run function with extracted context", async () => {
      const tracer = trace.getTracer("test");

      // Create an initial span and get its context
      const span = tracer.startSpan("initial-span");
      const ctx = trace.setSpan(otelContext.active(), span);

      // Get headers with trace context
      const headers: Record<string, string> = {};
      const propagator = getPropagator();
      propagator.injectContext(headers, ctx);

      span.end();

      // Run with propagated context
      await propagatedContext(headers, async () => {
        // Spans created here should be linked to the extracted context
        const s = new Span("child-span");
        s.start();
        s.finish();
      });

      const spans = exporter.getFinishedSpans();
      expect(spans.length).toBe(2);
    });

    it("should return function result", async () => {
      const result = await propagatedContext({}, async () => {
        return "test-result";
      });

      expect(result).toBe("test-result");
    });

    it("should work with sync functions", async () => {
      const result = await propagatedContext({}, () => {
        return 42;
      });

      expect(result).toBe(42);
    });

    it("should propagate errors", async () => {
      await expect(
        propagatedContext({}, async () => {
          throw new Error("propagated error");
        }),
      ).rejects.toThrow("propagated error");
    });
  });

  describe("propagator formats", () => {
    it("should store b3 format correctly", () => {
      const propagator = new ContextPropagator(false, "b3");
      expect(propagator.format).toBe("b3");
    });

    it("should store b3multi format correctly", () => {
      const propagator = new ContextPropagator(false, "b3multi");
      expect(propagator.format).toBe("b3multi");
    });

    it("should store jaeger format correctly", () => {
      const propagator = new ContextPropagator(false, "jaeger");
      expect(propagator.format).toBe("jaeger");
    });

    it("composite format should inject W3C traceparent", () => {
      resetPropagator();
      const propagator = new ContextPropagator(true, "composite");
      const tracer = trace.getTracer("test");

      tracer.startActiveSpan("test-span", (span) => {
        const headers: Record<string, string> = {};
        propagator.injectContext(headers);

        // Composite includes W3C which should set traceparent
        expect(headers.traceparent).toBeTruthy();

        span.end();
      });
    });
  });
});
