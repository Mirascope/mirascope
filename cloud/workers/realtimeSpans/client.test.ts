/**
 * @fileoverview Tests for RealtimeSpans client global layer and setter.
 */

import { describe, expect, it, vi } from "vitest";
import { Effect, Layer } from "effect";
import type { DurableObjectNamespace } from "@cloudflare/workers-types";

import {
  RealtimeSpans,
  realtimeSpansLayer,
  setRealtimeSpansLayer,
} from "./client";

// =============================================================================
// Mock Helpers
// =============================================================================

interface MockFetchOptions {
  ok?: boolean;
  status?: number;
  json?: () => Promise<unknown>;
  throwOnFetch?: Error;
  throwOnJson?: Error;
  /** Throws synchronously from stub.fetch() instead of returning a promise */
  throwSyncOnFetch?: unknown;
}

interface MockNamespaceOptions {
  fetchOptions?: MockFetchOptions;
  /** Throws synchronously from namespace.get() */
  throwOnGet?: unknown;
}

const createMockNamespace = (
  options: MockFetchOptions | MockNamespaceOptions = {},
): DurableObjectNamespace => {
  // Support both old signature and new signature
  const fetchOptions: MockFetchOptions =
    "fetchOptions" in options
      ? (options.fetchOptions ?? {})
      : (options as MockFetchOptions);
  const throwOnGet = "throwOnGet" in options ? options.throwOnGet : undefined;

  const mockStub = {
    fetch: vi.fn().mockImplementation(() => {
      if (fetchOptions.throwSyncOnFetch) {
        // eslint-disable-next-line @typescript-eslint/only-throw-error -- testing non-Error throws
        throw fetchOptions.throwSyncOnFetch;
      }
      if (fetchOptions.throwOnFetch) {
        return Promise.reject(fetchOptions.throwOnFetch);
      }
      return Promise.resolve({
        ok: fetchOptions.ok ?? true,
        status: fetchOptions.status ?? 200,
        json: fetchOptions.json ?? (() => Promise.resolve({})),
      });
    }),
  };

  return {
    idFromName: vi.fn().mockReturnValue({ toString: () => "test-id" }),
    get: vi.fn().mockImplementation(() => {
      if (throwOnGet) {
        // eslint-disable-next-line @typescript-eslint/only-throw-error -- testing non-Error throws
        throw throwOnGet;
      }
      return mockStub;
    }),
  } as unknown as DurableObjectNamespace;
};

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

  describe("RealtimeSpans.Live", () => {
    describe("upsert", () => {
      it("sends POST request to /upsert", async () => {
        const namespace = createMockNamespace();
        const layer = RealtimeSpans.Live(namespace);

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

        await Effect.runPromise(program.pipe(Effect.provide(layer)));

        expect(namespace.idFromName).toHaveBeenCalledWith("test-env");
        const stub = namespace.get(namespace.idFromName("test-env"));
        expect(stub.fetch).toHaveBeenCalledWith(
          "https://realtime-spans/upsert",
          expect.objectContaining({
            method: "POST",
            headers: { "content-type": "application/json" },
          }),
        );
      });

      it("fails when fetch throws", async () => {
        const namespace = createMockNamespace({
          throwOnFetch: new Error("Network error"),
        });
        const layer = RealtimeSpans.Live(namespace);

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

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain(
          "RealtimeSpansDurableObject request failed",
        );
        expect(error.message).toContain("Network error");
      });

      it("fails when fetch throws non-Error", async () => {
        const namespace = createMockNamespace();
        const stub = namespace.get(namespace.idFromName("test"));
        (stub.fetch as ReturnType<typeof vi.fn>).mockRejectedValue(
          "string error",
        );

        const layer = RealtimeSpans.Live(namespace);

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

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain("string error");
      });

      it("fails when response is not ok", async () => {
        const namespace = createMockNamespace({ ok: false, status: 500 });
        const layer = RealtimeSpans.Live(namespace);

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

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain("500");
      });

      it("fails when stub.fetch throws synchronously", async () => {
        const namespace = createMockNamespace({
          fetchOptions: {
            throwSyncOnFetch: new Error("Sync stub error"),
          },
        });
        const layer = RealtimeSpans.Live(namespace);

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

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain(
          "RealtimeSpansDurableObject stub error",
        );
        expect(error.message).toContain("Sync stub error");
      });

      it("fails when namespace.get throws synchronously", async () => {
        const namespace = createMockNamespace({
          throwOnGet: new Error("Get stub error"),
        });
        const layer = RealtimeSpans.Live(namespace);

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

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain("Failed to get Durable Object stub");
        expect(error.message).toContain("Get stub error");
      });

      it("fails when stub.fetch throws synchronously with non-Error", async () => {
        const namespace = createMockNamespace({
          fetchOptions: {
            throwSyncOnFetch: "sync string error",
          },
        });
        const layer = RealtimeSpans.Live(namespace);

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

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain(
          "RealtimeSpansDurableObject stub error",
        );
        expect(error.message).toContain("sync string error");
      });

      it("fails when namespace.get throws synchronously with non-Error", async () => {
        const namespace = createMockNamespace({
          throwOnGet: "get string error",
        });
        const layer = RealtimeSpans.Live(namespace);

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

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain("Failed to get Durable Object stub");
        expect(error.message).toContain("get string error");
      });
    });

    describe("search", () => {
      it("sends POST request to /search and returns response", async () => {
        const mockResponse = { spans: [], total: 0, hasMore: false };
        const namespace = createMockNamespace({
          json: () => Promise.resolve(mockResponse),
        });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.search({
            environmentId: "test-env",
            startTime: new Date(),
            endTime: new Date(),
          });
        });

        const result = await Effect.runPromise(
          program.pipe(Effect.provide(layer)),
        );

        expect(result).toEqual(mockResponse);
      });

      it("fails when response is not ok", async () => {
        const namespace = createMockNamespace({ ok: false, status: 400 });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.search({
            environmentId: "test-env",
            startTime: new Date(),
            endTime: new Date(),
          });
        });

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain("400");
      });

      it("fails when fetch throws Error", async () => {
        const namespace = createMockNamespace({
          throwOnFetch: new Error("Network error"),
        });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.search({
            environmentId: "test-env",
            startTime: new Date(),
            endTime: new Date(),
          });
        });

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain("Network error");
      });

      it("fails when fetch throws non-Error", async () => {
        const namespace = createMockNamespace();
        const stub = namespace.get(namespace.idFromName("test"));
        (stub.fetch as ReturnType<typeof vi.fn>).mockRejectedValue(
          "network failure",
        );

        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.search({
            environmentId: "test-env",
            startTime: new Date(),
            endTime: new Date(),
          });
        });

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain("network failure");
      });

      it("fails when JSON parse throws", async () => {
        const namespace = createMockNamespace({
          json: () => Promise.reject(new Error("Invalid JSON")),
        });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.search({
            environmentId: "test-env",
            startTime: new Date(),
            endTime: new Date(),
          });
        });

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain("JSON parse failed");
      });

      it("fails when JSON parse throws non-Error", async () => {
        const namespace = createMockNamespace({
          // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
          json: () => Promise.reject("parse error"),
        });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.search({
            environmentId: "test-env",
            startTime: new Date(),
            endTime: new Date(),
          });
        });

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain("parse error");
      });

      it("fails when stub.fetch throws synchronously", async () => {
        const namespace = createMockNamespace({
          fetchOptions: {
            throwSyncOnFetch: new Error("Sync fetch error"),
          },
        });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.search({
            environmentId: "test-env",
            startTime: new Date(),
            endTime: new Date(),
          });
        });

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain(
          "RealtimeSpansDurableObject stub error",
        );
        expect(error.message).toContain("Sync fetch error");
      });

      it("fails when stub.fetch throws synchronously with non-Error", async () => {
        const namespace = createMockNamespace({
          fetchOptions: {
            throwSyncOnFetch: "sync search string error",
          },
        });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.search({
            environmentId: "test-env",
            startTime: new Date(),
            endTime: new Date(),
          });
        });

        const error = await Effect.runPromise(
          program.pipe(Effect.provide(layer), Effect.flip),
        );

        expect(error.message).toContain(
          "RealtimeSpansDurableObject stub error",
        );
        expect(error.message).toContain("sync search string error");
      });
    });

    describe("getTraceDetail", () => {
      it("sends GET request to /trace/:traceId", async () => {
        const mockResponse = {
          traceId: "test-trace",
          spans: [],
          rootSpanId: null,
          totalDurationMs: null,
        };
        const namespace = createMockNamespace({
          json: () => Promise.resolve(mockResponse),
        });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.getTraceDetail({
            environmentId: "test-env",
            traceId: "test-trace",
          });
        });

        const result = await Effect.runPromise(
          program.pipe(Effect.provide(layer)),
        );

        expect(result).toEqual(mockResponse);
        const stub = namespace.get(namespace.idFromName("test-env"));
        expect(stub.fetch).toHaveBeenCalledWith(
          "https://realtime-spans/trace/test-trace",
          expect.objectContaining({ method: "GET" }),
        );
      });
    });

    describe("exists", () => {
      it("sends POST request to /exists and extracts boolean", async () => {
        const namespace = createMockNamespace({
          json: () => Promise.resolve({ exists: true }),
        });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.exists({
            environmentId: "test-env",
            traceId: "test-trace",
            spanId: "test-span",
          });
        });

        const result = await Effect.runPromise(
          program.pipe(Effect.provide(layer)),
        );

        expect(result).toBe(true);
      });

      it("returns false when span does not exist", async () => {
        const namespace = createMockNamespace({
          json: () => Promise.resolve({ exists: false }),
        });
        const layer = RealtimeSpans.Live(namespace);

        const program = Effect.gen(function* () {
          const service = yield* RealtimeSpans;
          return yield* service.exists({
            environmentId: "test-env",
            traceId: "test-trace",
            spanId: "test-span",
          });
        });

        const result = await Effect.runPromise(
          program.pipe(Effect.provide(layer)),
        );

        expect(result).toBe(false);
      });
    });
  });
});
