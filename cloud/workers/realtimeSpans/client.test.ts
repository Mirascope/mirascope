/**
 * @fileoverview Tests for RealtimeSpans client global layer and setter.
 */

import { describe, expect, it, vi } from "vitest";
import { Effect, Layer } from "effect";

import {
  RealtimeSpans,
  realtimeSpansLayer,
  setRealtimeSpansLayer,
} from "./client";

// =============================================================================
// Tests
// =============================================================================

describe("RealtimeSpans client", () => {
  describe("global layer", () => {
    it("default upsert returns error when not initialized", async () => {
      const program = Effect.gen(function* () {
        const service = yield* RealtimeSpans;
        return yield* service.upsert({
          environmentId: "test-env",
          projectId: "test-project",
          organizationId: "test-org",
          receivedAt: Date.now(),
          serviceName: null,
          serviceVersion: null,
          resourceAttributes: null,
          spans: [],
        });
      });

      const error = await Effect.runPromise(
        program.pipe(Effect.provide(realtimeSpansLayer), Effect.flip),
      );

      expect(error.message).toBe("RealtimeSpans not initialized");
    });

    it("default search returns error when not initialized", async () => {
      const program = Effect.gen(function* () {
        const service = yield* RealtimeSpans;
        return yield* service.search({
          environmentId: "test-env",
          startTime: new Date(),
          endTime: new Date(),
        });
      });

      const error = await Effect.runPromise(
        program.pipe(Effect.provide(realtimeSpansLayer), Effect.flip),
      );

      expect(error.message).toBe("RealtimeSpans not initialized");
    });

    it("default getTraceDetail returns error when not initialized", async () => {
      const program = Effect.gen(function* () {
        const service = yield* RealtimeSpans;
        return yield* service.getTraceDetail({
          environmentId: "test-env",
          traceId: "test-trace",
        });
      });

      const error = await Effect.runPromise(
        program.pipe(Effect.provide(realtimeSpansLayer), Effect.flip),
      );

      expect(error.message).toBe("RealtimeSpans not initialized");
    });

    it("default exists returns error when not initialized", async () => {
      const program = Effect.gen(function* () {
        const service = yield* RealtimeSpans;
        return yield* service.exists({
          environmentId: "test-env",
          traceId: "test-trace",
          spanId: "test-span",
        });
      });

      const error = await Effect.runPromise(
        program.pipe(Effect.provide(realtimeSpansLayer), Effect.flip),
      );

      expect(error.message).toBe("RealtimeSpans not initialized");
    });

    it("setRealtimeSpansLayer updates the global layer", async () => {
      const mockUpsert = vi.fn().mockReturnValue(Effect.void);
      const mockSearch = vi
        .fn()
        .mockReturnValue(
          Effect.succeed({ spans: [], total: 0, hasMore: false }),
        );
      const mockGetTraceDetail = vi.fn().mockReturnValue(
        Effect.succeed({
          traceId: "test",
          spans: [],
          rootSpanId: null,
          totalDurationMs: null,
        }),
      );
      const mockExists = vi.fn().mockReturnValue(Effect.succeed(true));

      const newLayer = Layer.succeed(RealtimeSpans, {
        upsert: mockUpsert,
        search: mockSearch,
        getTraceDetail: mockGetTraceDetail,
        exists: mockExists,
      });

      setRealtimeSpansLayer(newLayer);

      const program = Effect.gen(function* () {
        const service = yield* RealtimeSpans;
        yield* service.upsert({
          environmentId: "test-env",
          projectId: "test-project",
          organizationId: "test-org",
          receivedAt: Date.now(),
          serviceName: null,
          serviceVersion: null,
          resourceAttributes: null,
          spans: [],
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(realtimeSpansLayer)));

      expect(mockUpsert).toHaveBeenCalled();

      // Reset global layer to default
      setRealtimeSpansLayer(
        Layer.succeed(RealtimeSpans, {
          upsert: () => Effect.fail(new Error("RealtimeSpans not initialized")),
          search: () => Effect.fail(new Error("RealtimeSpans not initialized")),
          getTraceDetail: () =>
            Effect.fail(new Error("RealtimeSpans not initialized")),
          exists: () => Effect.fail(new Error("RealtimeSpans not initialized")),
        }),
      );
    });
  });
});
