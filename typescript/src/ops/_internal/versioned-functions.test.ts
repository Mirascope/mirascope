import { trace as otelTrace } from "@opentelemetry/api";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
  InMemorySpanExporter,
} from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import { Span } from "./spans";
import { createVersionedResult } from "./versioned-functions";

// Mock the API client
vi.mock("@/api/client", () => ({
  getClient: vi.fn(() => ({
    annotations: {
      create: vi.fn().mockResolvedValue({ id: "annotation-123" }),
    },
  })),
}));

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
    vi.clearAllMocks();
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

    it("should include functionUuid when provided", () => {
      const span = new Span("test").start();
      const result = createVersionedResult("test-result", span, "uuid-123");

      expect(result.functionUuid).toBe("uuid-123");
      span.finish();
    });

    it("should have undefined functionUuid when not provided", () => {
      const span = new Span("test").start();
      const result = createVersionedResult("test-result", span);

      expect(result.functionUuid).toBeUndefined();
      span.finish();
    });

    describe("annotate", () => {
      it("should call API client with correct parameters", async () => {
        const { getClient } = await import("@/api/client");
        const mockCreate = vi.fn().mockResolvedValue({ id: "annotation-123" });
        vi.mocked(getClient).mockReturnValue({
          annotations: { create: mockCreate },
        } as unknown as ReturnType<typeof getClient>);

        const span = new Span("test").start();
        const result = createVersionedResult("test-result", span);

        await result.annotate({ label: "pass", reasoning: "Good result" });

        expect(mockCreate).toHaveBeenCalledWith({
          otelSpanId: span.spanId,
          otelTraceId: span.traceId,
          label: "pass",
          reasoning: "Good result",
          metadata: null,
        });

        span.finish();
      });

      it("should include metadata when provided", async () => {
        const { getClient } = await import("@/api/client");
        const mockCreate = vi.fn().mockResolvedValue({ id: "annotation-123" });
        vi.mocked(getClient).mockReturnValue({
          annotations: { create: mockCreate },
        } as unknown as ReturnType<typeof getClient>);

        const span = new Span("test").start();
        const result = createVersionedResult("test-result", span);

        await result.annotate({
          label: "fail",
          metadata: { key: "value" },
        });

        expect(mockCreate).toHaveBeenCalledWith({
          otelSpanId: span.spanId,
          otelTraceId: span.traceId,
          label: "fail",
          reasoning: null,
          metadata: { key: "value" },
        });

        span.finish();
      });

      it("should not call API when spanId is null", async () => {
        const { getClient } = await import("@/api/client");
        const mockCreate = vi.fn().mockResolvedValue({ id: "annotation-123" });
        vi.mocked(getClient).mockReturnValue({
          annotations: { create: mockCreate },
        } as unknown as ReturnType<typeof getClient>);

        // Shutdown tracer to get null spanId
        await provider.shutdown();
        otelTrace.disable();

        const span = new Span("test").start();
        const result = createVersionedResult("test-result", span);

        await result.annotate({ label: "pass" });

        expect(mockCreate).not.toHaveBeenCalled();

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
