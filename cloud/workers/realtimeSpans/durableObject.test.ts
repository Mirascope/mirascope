/**
 * @fileoverview Tests for RealtimeSpansDurableObject realtime cache behavior.
 */

import { Effect, Layer } from "effect";
import { afterEach, describe, expect, it } from "vitest";

import type { SpansBatchRequest } from "@/db/clickhouse/types";

import {
  parseJson,
  createState,
  createSpanBatch,
  createUpsertRequest,
  createSearchRequest,
  createTraceRequest,
  createExistsRequest,
  createTimeContext,
  msToNano,
  DEFAULT_ENV_ID,
  DEFAULT_ORG_ID,
  DEFAULT_PROJECT_ID,
  DEFAULT_SERVICE_NAME,
  DEFAULT_SERVICE_VERSION,
} from "@/tests/workers/realtimeSpans";
import {
  RealtimeSpans,
  realtimeSpansLayer,
  setRealtimeSpansLayer,
} from "@/workers/realtimeSpans";
import { RealtimeSpansDurableObjectBase as RealtimeSpansDurableObject } from "@/workers/realtimeSpans/durableObject";

describe("RealtimeSpansDurableObject", () => {
  it("upserts spans and checks existence", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});

    const upsertResponse = await durableObject.fetch(
      createUpsertRequest(createSpanBatch()),
    );
    expect(upsertResponse.status).toBe(204);

    const existsResponse = await durableObject.fetch(
      createExistsRequest({ traceId: "trace-1", spanId: "span-1" }),
    );
    const existsBody = await parseJson<{ exists: boolean }>(existsResponse);
    expect(existsBody.exists).toBe(true);
  });

  it("searches spans within time range", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});

    await durableObject.fetch(createUpsertRequest(createSpanBatch()));

    const searchResponse = await durableObject.fetch(
      createSearchRequest({
        query: "alpha",
        sortBy: "start_time",
        sortOrder: "desc",
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
      hasMore: boolean;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-1");
  });

  it("filters out spans outside time range", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-time",
              spanId: "span-in-range",
              name: "in-range",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
            {
              // Start time is 2 minutes before now - will be outside search range
              traceId: "trace-time",
              spanId: "span-out-range",
              name: "out-range",
              startTimeUnixNano: msToNano(time.nowMs - 120_000),
              endTimeUnixNano: msToNano(time.nowMs - 119_900),
            },
          ],
        }),
      ),
    );

    // Search with narrow time range that excludes the old span
    const searchResponse = await durableObject.fetch(
      createSearchRequest({
        startTime: new Date(time.nowMs - 10_000).toISOString(),
        endTime: new Date(time.nowMs + 60_000).toISOString(),
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-in-range");
  });

  it("returns trace detail spans", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});

    await durableObject.fetch(createUpsertRequest(createSpanBatch()));

    const traceResponse = await durableObject.fetch(
      createTraceRequest("trace-1"),
    );
    const traceBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      rootSpanId: string | null;
    }>(traceResponse);

    expect(traceBody.spans).toHaveLength(2);
    expect(traceBody.rootSpanId).toBe("span-1");
  });

  it("computes totalDurationMs with spans ending at different times", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    // Span-2 ends BEFORE span-1 to test the end <= maxEnd branch
    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-duration",
              spanId: "span-long",
              parentSpanId: null,
              name: "long",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(1000), // Ends at +1000ms
            },
            {
              traceId: "trace-duration",
              spanId: "span-short",
              parentSpanId: "span-long",
              name: "short",
              startTimeUnixNano: time.laterStartNano(100),
              endTimeUnixNano: time.endNano(500), // Ends at +500ms (before span-long)
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      totalDurationMs: number | null;
    }>(await durableObject.fetch(createTraceRequest("trace-duration")));

    // Total duration should be from earliest start to latest end (1000ms)
    expect(traceBody.totalDurationMs).toBe(1000);
  });

  it("returns trace detail with resourceAttributes serialized", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          resourceAttributes: { deployment: "production", version: "2.0.0" },
        }),
      ),
    );

    const traceResponse = await durableObject.fetch(
      createTraceRequest("trace-1"),
    );
    const traceBody = await parseJson<{
      spans: Array<{
        spanId: string;
        resourceAttributes: string | null;
      }>;
    }>(traceResponse);

    expect(traceBody.spans).toHaveLength(2);
    expect(traceBody.spans[0]?.resourceAttributes).toBe(
      JSON.stringify({ deployment: "production", version: "2.0.0" }),
    );
  });

  it("returns null resourceAttributes when none are provided", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const now = Date.now();

    const payload: SpansBatchRequest = {
      environmentId: DEFAULT_ENV_ID,
      projectId: DEFAULT_PROJECT_ID,
      organizationId: DEFAULT_ORG_ID,
      receivedAt: now,
      serviceName: DEFAULT_SERVICE_NAME,
      serviceVersion: DEFAULT_SERVICE_VERSION,
      resourceAttributes: null,
      spans: [
        {
          traceId: "trace-no-resource",
          spanId: "span-no-resource",
          name: "no-resource",
          startTimeUnixNano: msToNano(now),
          endTimeUnixNano: msToNano(now + 1000),
        },
      ],
    };

    const request = new Request("https://realtime-spans/upsert", {
      method: "POST",
      body: JSON.stringify(payload),
      headers: { "content-type": "application/json" },
    });

    await durableObject.fetch(request);

    const traceBody = await parseJson<{
      spans: Array<{ resourceAttributes: string | null }>;
    }>(await durableObject.fetch(createTraceRequest("trace-no-resource")));

    expect(traceBody.spans[0]?.resourceAttributes).toBeNull();
  });

  it("keeps long-running spans when endTime exceeds query range", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});

    const nowMs = Date.now();
    const payload = createSpanBatch({
      spans: [
        {
          traceId: "trace-long",
          spanId: "span-long",
          name: "long-span",
          startTimeUnixNano: msToNano(nowMs - 5_000),
          endTimeUnixNano: msToNano(nowMs + 120_000),
        },
      ],
    });

    await durableObject.fetch(createUpsertRequest(payload));

    const searchResponse = await durableObject.fetch(
      createSearchRequest({
        startTime: new Date(nowMs - 10_000).toISOString(),
        endTime: new Date(nowMs + 5_000).toISOString(),
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-long");
  });

  describe("pending → final merge", () => {
    it("merges pending span with final update", async () => {
      const state = createState();
      const durableObject = new RealtimeSpansDurableObject(state, {});
      const time = createTimeContext();

      // Send pending span (no endTime)
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs,
            resourceAttributes: null,
            spans: [
              {
                traceId: "trace-merge",
                spanId: "span-merge",
                parentSpanId: null,
                name: "pending-span",
                kind: 1,
                startTimeUnixNano: time.startNano,
                attributes: { key1: "value1" },
                events: [{ name: "start-event" }],
              },
            ],
          }),
        ),
      );

      // Send final update with endTime
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs + 1000,
            resourceAttributes: null,
            spans: [
              {
                traceId: "trace-merge",
                spanId: "span-merge",
                name: "pending-span",
                endTimeUnixNano: time.endNano(1000),
                status: { code: 1, message: "OK" },
              },
            ],
          }),
        ),
      );

      const traceBody = await parseJson<{
        spans: Array<{
          spanId: string;
          durationMs: number | null;
          statusCode: number | null;
        }>;
      }>(await durableObject.fetch(createTraceRequest("trace-merge")));

      expect(traceBody.spans).toHaveLength(1);
      expect(traceBody.spans[0]?.durationMs).toBe(1000);
      expect(traceBody.spans[0]?.statusCode).toBe(1);
    });

    it("preserves earliest start time on merge", async () => {
      const state = createState();
      const durableObject = new RealtimeSpansDurableObject(state, {});
      const time = createTimeContext();

      // First upsert with earlier start time
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs,
            resourceAttributes: null,
            spans: [
              {
                traceId: "trace-start",
                spanId: "span-start",
                name: "start-test",
                startTimeUnixNano: time.startNano,
              },
            ],
          }),
        ),
      );

      // Second upsert with later start time (should be ignored)
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs + 1000,
            resourceAttributes: null,
            spans: [
              {
                traceId: "trace-start",
                spanId: "span-start",
                name: "start-test",
                startTimeUnixNano: time.laterStartNano(500),
                endTimeUnixNano: time.endNano(1000),
              },
            ],
          }),
        ),
      );

      const traceBody = await parseJson<{
        spans: Array<{
          spanId: string;
          startTime: string;
          durationMs: number | null;
        }>;
      }>(await durableObject.fetch(createTraceRequest("trace-start")));

      expect(traceBody.spans).toHaveLength(1);
      expect(traceBody.spans[0]?.startTime).toBe(
        new Date(time.nowMs).toISOString(),
      );
      expect(traceBody.spans[0]?.durationMs).toBe(1000);
    });

    it("preserves existing fields when update omits them", async () => {
      const state = createState();
      const durableObject = new RealtimeSpansDurableObject(state, {});
      const time = createTimeContext();

      // Initial span with all fields
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs,
            resourceAttributes: { region: "us-east-1" },
            spans: [
              {
                traceId: "trace-preserve",
                spanId: "span-preserve",
                parentSpanId: "parent-1",
                name: "preserve-test",
                kind: 2,
                startTimeUnixNano: time.startNano,
                attributes: { original: "attr" },
                events: [{ name: "original-event" }],
                links: [{ traceId: "linked-trace" }],
                droppedAttributesCount: 5,
              },
            ],
          }),
        ),
      );

      // Update with minimal fields (others should be preserved)
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs + 500,
            serviceName: null,
            serviceVersion: null,
            resourceAttributes: null,
            spans: [
              {
                traceId: "trace-preserve",
                spanId: "span-preserve",
                name: "preserve-test",
                endTimeUnixNano: time.endNano(500),
              },
            ],
          }),
        ),
      );

      const traceBody = await parseJson<{
        spans: Array<{
          spanId: string;
          parentSpanId: string | null;
          kind: number;
          attributes: string;
          events: string | null;
          links: string | null;
          serviceName: string | null;
          resourceAttributes: string | null;
        }>;
      }>(await durableObject.fetch(createTraceRequest("trace-preserve")));

      expect(traceBody.spans).toHaveLength(1);
      const span = traceBody.spans[0];
      expect(span?.parentSpanId).toBe("parent-1");
      expect(span?.kind).toBe(2);
      expect(JSON.parse(span?.attributes ?? "{}")).toEqual({
        original: "attr",
      });
      expect(JSON.parse(span?.events ?? "[]")).toEqual([
        { name: "original-event" },
      ]);
      expect(JSON.parse(span?.links ?? "[]")).toEqual([
        { traceId: "linked-trace" },
      ]);
      expect(span?.serviceName).toBe(DEFAULT_SERVICE_NAME);
      expect(JSON.parse(span?.resourceAttributes ?? "{}")).toEqual({
        region: "us-east-1",
      });
    });

    it("replaces attributes when new ones are provided", async () => {
      const state = createState();
      const durableObject = new RealtimeSpansDurableObject(state, {});
      const time = createTimeContext();

      // Initial span with old attributes
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs,
            resourceAttributes: null,
            spans: [
              {
                traceId: "trace-attrs",
                spanId: "span-attrs",
                name: "attrs-test",
                startTimeUnixNano: time.startNano,
                attributes: { old: "value" },
              },
            ],
          }),
        ),
      );

      // Update with new attributes
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs + 500,
            resourceAttributes: null,
            spans: [
              {
                traceId: "trace-attrs",
                spanId: "span-attrs",
                name: "attrs-test",
                attributes: { new: "value", "gen_ai.usage.total_tokens": 100 },
              },
            ],
          }),
        ),
      );

      const traceBody = await parseJson<{
        spans: Array<{
          spanId: string;
          attributes: string;
          totalTokens: number | null;
        }>;
      }>(await durableObject.fetch(createTraceRequest("trace-attrs")));

      expect(traceBody.spans).toHaveLength(1);
      expect(JSON.parse(traceBody.spans[0]?.attributes ?? "{}")).toEqual({
        new: "value",
        "gen_ai.usage.total_tokens": 100,
      });
      expect(traceBody.spans[0]?.totalTokens).toBe(100);
    });

    it("preserves largest endTime on out-of-order updates", async () => {
      const state = createState();
      const durableObject = new RealtimeSpansDurableObject(state, {});
      const time = createTimeContext();

      // First update with later endTime
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs,
            resourceAttributes: null,
            spans: [
              {
                traceId: "trace-ooo",
                spanId: "span-ooo",
                name: "out-of-order-test",
                startTimeUnixNano: time.startNano,
                endTimeUnixNano: time.endNano(2000),
              },
            ],
          }),
        ),
      );

      // Second update with earlier endTime (should be ignored)
      await durableObject.fetch(
        createUpsertRequest(
          createSpanBatch({
            receivedAt: time.nowMs + 500,
            resourceAttributes: null,
            spans: [
              {
                traceId: "trace-ooo",
                spanId: "span-ooo",
                name: "out-of-order-test",
                startTimeUnixNano: time.startNano,
                endTimeUnixNano: time.endNano(1000),
              },
            ],
          }),
        ),
      );

      const traceBody = await parseJson<{
        spans: Array<{
          spanId: string;
          durationMs: number | null;
        }>;
      }>(await durableObject.fetch(createTraceRequest("trace-ooo")));

      expect(traceBody.spans).toHaveLength(1);
      expect(traceBody.spans[0]?.durationMs).toBe(2000);
    });
  });
});

describe("edge cases", () => {
  it("returns 404 for unknown endpoints", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});

    const response = await durableObject.fetch(
      new Request("https://realtime-spans/unknown", { method: "GET" }),
    );
    expect(response.status).toBe(404);
    expect(await response.text()).toBe("Not Found");
  });

  it("exists returns false for non-existent span", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});

    const response = await durableObject.fetch(
      createExistsRequest({ traceId: "missing-trace", spanId: "missing-span" }),
    );
    const body = await parseJson<{ exists: boolean }>(response);
    expect(body.exists).toBe(false);
  });

  it("exists returns false and deletes expired span", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});

    // Directly insert an expired span record into storage
    const expiredRecord = {
      span: {
        traceId: "trace-expired",
        spanId: "span-expired",
        name: "expired-span",
        receivedAt: Date.now() - 20 * 60 * 1000, // 20 minutes ago
        environmentId: DEFAULT_ENV_ID,
        projectId: DEFAULT_PROJECT_ID,
        organizationId: DEFAULT_ORG_ID,
        serviceName: DEFAULT_SERVICE_NAME,
        serviceVersion: DEFAULT_SERVICE_VERSION,
        resourceAttributes: null,
      },
      receivedAt: Date.now() - 20 * 60 * 1000,
      expiresAt: Date.now() - 10 * 60 * 1000, // Expired 10 minutes ago
      sizeBytes: 100,
    };
    await state.storage.put("span:trace-expired:span-expired", expiredRecord);

    // Verify the span exists in storage before the check
    const before = await state.storage.get("span:trace-expired:span-expired");
    expect(before).toBeDefined();

    // Call exists - should return false and delete the expired span
    const response = await durableObject.fetch(
      createExistsRequest({ traceId: "trace-expired", spanId: "span-expired" }),
    );
    const body = await parseJson<{ exists: boolean }>(response);
    expect(body.exists).toBe(false);

    // Verify the span was deleted from storage
    const after = await state.storage.get("span:trace-expired:span-expired");
    expect(after).toBeUndefined();
  });

  it("pruneStorage deletes expired entries during upsert", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    // Directly insert an expired span record into storage
    const expiredRecord = {
      span: {
        traceId: "trace-prune-expired",
        spanId: "span-prune-expired",
        name: "prune-expired-span",
        receivedAt: Date.now() - 20 * 60 * 1000,
        environmentId: DEFAULT_ENV_ID,
        projectId: DEFAULT_PROJECT_ID,
        organizationId: DEFAULT_ORG_ID,
        serviceName: DEFAULT_SERVICE_NAME,
        serviceVersion: DEFAULT_SERVICE_VERSION,
        resourceAttributes: null,
      },
      receivedAt: Date.now() - 20 * 60 * 1000,
      expiresAt: Date.now() - 10 * 60 * 1000, // Expired 10 minutes ago
      sizeBytes: 100,
    };
    await state.storage.put(
      "span:trace-prune-expired:span-prune-expired",
      expiredRecord,
    );

    // Verify the expired span exists in storage before upsert
    const before = await state.storage.get(
      "span:trace-prune-expired:span-prune-expired",
    );
    expect(before).toBeDefined();

    // Upsert a new span - this triggers pruneStorage which should delete expired entries
    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-new",
              spanId: "span-new",
              name: "new-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
      ),
    );

    // Verify the expired span was deleted during pruneStorage
    const afterExpired = await state.storage.get(
      "span:trace-prune-expired:span-prune-expired",
    );
    expect(afterExpired).toBeUndefined();

    // Verify the new span was stored
    const newSpan = await state.storage.get("span:trace-new:span-new");
    expect(newSpan).toBeDefined();
  });

  it("filters by hasError when true", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-error",
              spanId: "span-error",
              name: "error-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "exception.type": "Error",
                "exception.message": "Test error",
              },
            },
            {
              traceId: "trace-success",
              spanId: "span-success",
              name: "success-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          hasError: true,
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-error");
  });

  it("filters by hasError when false", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-error",
              spanId: "span-error",
              name: "error-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "exception.type": "Error" },
            },
            {
              traceId: "trace-success",
              spanId: "span-success",
              name: "success-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          hasError: false,
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-success");
  });

  it("filters by model", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-model",
              spanId: "span-gpt4",
              name: "gpt4",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.request.model": "gpt-4" },
            },
            {
              traceId: "trace-model",
              spanId: "span-gpt35",
              name: "gpt35",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.request.model": "gpt-3.5-turbo" },
            },
          ],
        }),
      ),
    );

    // Filter to only gpt-4 models, excluding gpt-3.5-turbo
    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          model: ["gpt-4"],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-gpt4");
  });

  it("filters by provider", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-provider",
              spanId: "span-openai",
              name: "openai",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.system": "openai" },
            },
            {
              traceId: "trace-provider",
              spanId: "span-anthropic",
              name: "anthropic",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.system": "anthropic" },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          provider: ["openai"],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-openai");
  });

  it("filters by functionId", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-func",
              spanId: "span-func-a",
              name: "func-a",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "mirascope.function_id": "func-id-a" },
            },
            {
              traceId: "trace-func",
              spanId: "span-func-b",
              name: "func-b",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "mirascope.function_id": "func-id-b" },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          functionId: "func-id-a",
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-func-a");
  });

  it("filters by functionName", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-funcname",
              spanId: "span-name-foo",
              name: "foo",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "mirascope.function_name": "foo_function" },
            },
            {
              traceId: "trace-funcname",
              spanId: "span-name-bar",
              name: "bar",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "mirascope.function_name": "bar_function" },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          functionName: "foo_function",
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-name-foo");
  });

  it("filters by minTokens and maxTokens", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-tokens",
              spanId: "span-few-tokens",
              name: "few-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.usage.total_tokens": 10 },
            },
            {
              traceId: "trace-tokens",
              spanId: "span-many-tokens",
              name: "many-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.usage.total_tokens": 1000 },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          minTokens: 50,
          maxTokens: 2000,
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string; totalTokens: number }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-many-tokens");
    expect(searchBody.spans[0]?.totalTokens).toBe(1000);
  });

  it("filters out spans exceeding maxTokens", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-max-tokens",
              spanId: "span-under-limit",
              name: "under",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.usage.total_tokens": 100 },
            },
            {
              traceId: "trace-max-tokens",
              spanId: "span-over-limit",
              name: "over",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.usage.total_tokens": 500 },
            },
          ],
        }),
      ),
    );

    // maxTokens 200 should filter out the 500 token span
    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          maxTokens: 200,
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string; totalTokens: number }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-under-limit");
  });

  it("filters by minDuration and maxDuration", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-duration",
              spanId: "span-fast",
              name: "fast",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(10),
            },
            {
              traceId: "trace-duration",
              spanId: "span-slow",
              name: "slow",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(500),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          minDuration: 100,
          maxDuration: 1000,
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string; durationMs: number }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-slow");
    expect(searchBody.spans[0]?.durationMs).toBe(500);
  });

  it("filters out spans exceeding maxDuration", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-maxdur",
              spanId: "span-under-limit",
              name: "under",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(50),
            },
            {
              traceId: "trace-maxdur",
              spanId: "span-over-limit",
              name: "over",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(150),
            },
          ],
        }),
      ),
    );

    // maxDuration 100 should filter out the 150ms span
    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          maxDuration: 100,
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string; durationMs: number }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-under-limit");
  });

  it("sorts by duration_ms ascending", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-sort",
              spanId: "span-medium",
              name: "medium",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(200),
            },
            {
              traceId: "trace-sort",
              spanId: "span-fast",
              name: "fast",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(50),
            },
            {
              traceId: "trace-sort",
              spanId: "span-slow",
              name: "slow",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(500),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      createSearchRequest({
        sortBy: "duration_ms",
        sortOrder: "asc",
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string; durationMs: number }>;
    }>(searchResponse);

    expect(searchBody.spans[0]?.spanId).toBe("span-fast");
    expect(searchBody.spans[1]?.spanId).toBe("span-medium");
    expect(searchBody.spans[2]?.spanId).toBe("span-slow");
  });

  it("handles sorting spans with identical timestamps", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    // Two spans with IDENTICAL start times
    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-identical",
              spanId: "span-a",
              name: "a",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
            {
              traceId: "trace-identical",
              spanId: "span-b",
              name: "b",
              startTimeUnixNano: time.startNano, // Same start time as span-a
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      createSearchRequest({
        sortBy: "start_time",
        sortOrder: "asc",
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    // Both spans should be returned (order doesn't matter since they're equal)
    expect(searchBody.total).toBe(2);
    expect(searchBody.spans.map((s) => s.spanId).sort()).toEqual([
      "span-a",
      "span-b",
    ]);
  });

  it("sorts by total_tokens descending", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-sort-tokens",
              spanId: "span-few",
              name: "few",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.usage.total_tokens": 10 },
            },
            {
              traceId: "trace-sort-tokens",
              spanId: "span-many",
              name: "many",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.usage.total_tokens": 1000 },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      createSearchRequest({
        sortBy: "total_tokens",
        sortOrder: "desc",
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string; totalTokens: number }>;
    }>(searchResponse);

    expect(searchBody.spans[0]?.spanId).toBe("span-many");
    expect(searchBody.spans[1]?.spanId).toBe("span-few");
  });

  it("computes totalTokens from input+output when total_tokens not set", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-computed",
              spanId: "span-computed",
              name: "computed-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "gen_ai.usage.input_tokens": 50,
                "gen_ai.usage.output_tokens": 30,
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ totalTokens: number | null }>;
    }>(await durableObject.fetch(createTraceRequest("trace-computed")));

    expect(traceBody.spans[0]?.totalTokens).toBe(80);
  });

  it("parses string-based token counts", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-string-tokens",
              spanId: "span-string-tokens",
              name: "string-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                // Some OTLP implementations send token counts as strings
                "gen_ai.usage.input_tokens": "25",
                "gen_ai.usage.output_tokens": "15",
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ totalTokens: number | null }>;
    }>(await durableObject.fetch(createTraceRequest("trace-string-tokens")));

    // Should parse strings and compute 25 + 15 = 40
    expect(traceBody.spans[0]?.totalTokens).toBe(40);
  });

  it("computes totalTokens from input only when output_tokens not set", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-input-only",
              spanId: "span-input-only",
              name: "input-only-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "gen_ai.usage.input_tokens": 42,
                // No output_tokens set
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ totalTokens: number | null }>;
    }>(await durableObject.fetch(createTraceRequest("trace-input-only")));

    // Should use input + 0 since output is null
    expect(traceBody.spans[0]?.totalTokens).toBe(42);
  });

  it("computes totalTokens from output only when input_tokens not set", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-output-only",
              spanId: "span-output-only",
              name: "output-only-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                // No input_tokens set
                "gen_ai.usage.output_tokens": 37,
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ totalTokens: number | null }>;
    }>(await durableObject.fetch(createTraceRequest("trace-output-only")));

    // Should use 0 + output since input is null
    expect(traceBody.spans[0]?.totalTokens).toBe(37);
  });

  it("sorts by total_tokens with null tokens using ascending order", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-null-tokens",
              spanId: "span-no-tokens",
              name: "no-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              // No token attributes - totalTokens will be null
            },
            {
              traceId: "trace-null-tokens",
              spanId: "span-with-tokens",
              name: "with-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.usage.total_tokens": 50 },
            },
          ],
        }),
      ),
    );

    // Ascending: spans with tokens should come first (50 < POSITIVE_INFINITY)
    const searchAsc = await durableObject.fetch(
      createSearchRequest({
        startTime: new Date(time.nowMs - 60_000).toISOString(),
        endTime: new Date(time.nowMs + 60_000).toISOString(),
        sortBy: "total_tokens",
        sortOrder: "asc",
      }),
    );
    const ascBody = await parseJson<{
      spans: Array<{ spanId: string; totalTokens: number | null }>;
    }>(searchAsc);

    expect(ascBody.spans[0]?.spanId).toBe("span-with-tokens");
    expect(ascBody.spans[1]?.spanId).toBe("span-no-tokens");
  });

  it("sorts by total_tokens with null tokens using descending order", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-null-tokens-desc",
              spanId: "span-no-tokens-desc",
              name: "no-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              // No token attributes
            },
            {
              traceId: "trace-null-tokens-desc",
              spanId: "span-with-tokens-desc",
              name: "with-tokens",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.usage.total_tokens": 50 },
            },
          ],
        }),
      ),
    );

    // Descending: spans with tokens should come first (50 > NEGATIVE_INFINITY)
    const searchDesc = await durableObject.fetch(
      createSearchRequest({
        startTime: new Date(time.nowMs - 60_000).toISOString(),
        endTime: new Date(time.nowMs + 60_000).toISOString(),
        sortBy: "total_tokens",
        sortOrder: "desc",
      }),
    );
    const descBody = await parseJson<{
      spans: Array<{ spanId: string; totalTokens: number | null }>;
    }>(searchDesc);

    expect(descBody.spans[0]?.spanId).toBe("span-with-tokens-desc");
    expect(descBody.spans[1]?.spanId).toBe("span-no-tokens-desc");
  });

  it("handles attribute filters with eq operator", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-attr",
              spanId: "span-gpt4",
              name: "gpt4",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.request.model": "gpt-4" },
            },
            {
              traceId: "trace-attr",
              spanId: "span-claude",
              name: "claude",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.request.model": "claude-3" },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [
            { key: "gen_ai.request.model", operator: "eq", value: "gpt-4" },
          ],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-gpt4");
  });

  it("handles attribute filters with numeric values", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-numeric",
              spanId: "span-match-num",
              name: "match-num",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { count: 42 },
            },
            {
              traceId: "trace-numeric",
              spanId: "span-other-num",
              name: "other-num",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { count: 99 },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [{ key: "count", operator: "eq", value: "42" }],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-match-num");
  });

  it("handles attribute filters with boolean values", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-bool",
              spanId: "span-true",
              name: "bool-true",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { enabled: true },
            },
            {
              traceId: "trace-bool",
              spanId: "span-false",
              name: "bool-false",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { enabled: false },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [{ key: "enabled", operator: "eq", value: "true" }],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-true");
  });

  it("handles attribute filters with exists operator", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-exists",
              spanId: "span-with-custom",
              name: "with-custom",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { custom_attr: "value" },
            },
            {
              traceId: "trace-exists",
              spanId: "span-without-custom",
              name: "without-custom",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {},
            },
            {
              traceId: "trace-exists",
              spanId: "span-with-undefined",
              name: "with-undefined",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              // Explicitly set attribute to undefined to test that branch
              attributes: { custom_attr: undefined } as Record<string, unknown>,
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [{ key: "custom_attr", operator: "exists" }],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    // Only span-with-custom has a defined value; undefined and missing don't match exists
    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-with-custom");
  });

  it("handles attribute filters with contains operator", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-contains",
              spanId: "span-openai",
              name: "openai-model",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.system": "openai" },
            },
            {
              traceId: "trace-contains",
              spanId: "span-anthropic",
              name: "anthropic-model",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.system": "anthropic" },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [
            { key: "gen_ai.system", operator: "contains", value: "open" },
          ],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-openai");
  });

  it("handles attribute filters with neq operator", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-neq",
              spanId: "span-gpt4",
              name: "gpt4-model",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.request.model": "gpt-4" },
            },
            {
              traceId: "trace-neq",
              spanId: "span-claude",
              name: "claude-model",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.request.model": "claude-3" },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [
            { key: "gen_ai.request.model", operator: "neq", value: "gpt-4" },
          ],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-claude");
  });

  it("handles attribute filters with neq on missing attribute", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-neq-missing",
              spanId: "span-with-attr",
              name: "with-attr",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { custom_field: "value" },
            },
            {
              traceId: "trace-neq-missing",
              spanId: "span-without-attr",
              name: "without-attr",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {},
            },
          ],
        }),
      ),
    );

    // neq on missing attribute should match (null != "value")
    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [
            { key: "custom_field", operator: "neq", value: "value" },
          ],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    // span without the attribute matches because null != "value"
    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-without-attr");
  });

  it("handles attribute filters with non-stringifiable value (object)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-object-attr",
              spanId: "span-object",
              name: "object-attr",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              // Object value cannot be converted to string by toSearchString
              attributes: { nested: { foo: "bar" } },
            },
            {
              traceId: "trace-object-attr",
              spanId: "span-string",
              name: "string-attr",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { nested: "string-value" },
            },
          ],
        }),
      ),
    );

    // eq on object attribute should not match (valueString is null)
    const eqResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [
            { key: "nested", operator: "eq", value: "string-value" },
          ],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const eqBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(eqResponse);

    // Only the string attribute matches eq
    expect(eqBody.total).toBe(1);
    expect(eqBody.spans[0]?.spanId).toBe("span-string");

    // neq on object attribute should match (valueString is null, so neq returns true)
    const neqResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [
            { key: "nested", operator: "neq", value: "string-value" },
          ],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const neqBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(neqResponse);

    // Object attribute matches neq because valueString is null
    expect(neqBody.total).toBe(1);
    expect(neqBody.spans[0]?.spanId).toBe("span-object");
  });

  it("handles attribute filters with unknown operator", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-unknown-op",
              spanId: "span-1",
              name: "test-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { field: "value" },
            },
          ],
        }),
      ),
    );

    // Unknown operator with no value should return false (no matches)
    // This also tests the filter.value ?? "" branch
    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [
            // Cast to bypass type checking for test purposes - no value provided
            { key: "field", operator: "invalid_operator" },
          ],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    // Unknown operator returns false, so no spans match
    expect(searchBody.total).toBe(0);
  });

  it("handles attribute filters on span with null attributes", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    // Create a span with explicitly null attributes
    const payload: SpansBatchRequest = {
      environmentId: DEFAULT_ENV_ID,
      projectId: DEFAULT_PROJECT_ID,
      organizationId: DEFAULT_ORG_ID,
      receivedAt: time.nowMs,
      serviceName: DEFAULT_SERVICE_NAME,
      serviceVersion: DEFAULT_SERVICE_VERSION,
      resourceAttributes: null,
      spans: [
        {
          traceId: "trace-null-attrs",
          spanId: "span-null-attrs",
          name: "null-attrs",
          startTimeUnixNano: time.startNano,
          endTimeUnixNano: time.endNano(100),
          // No attributes field - will be null/undefined
        },
      ],
    };

    await durableObject.fetch(
      new Request("https://realtime-spans/upsert", {
        method: "POST",
        body: JSON.stringify(payload),
        headers: { "content-type": "application/json" },
      }),
    );

    // exists filter should not match span with null attributes
    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [{ key: "any_field", operator: "exists" }],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    // Span with null attributes should not match exists filter
    expect(searchBody.total).toBe(0);
  });

  it("handles attribute filter with null value", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-null-filter",
              spanId: "span-match",
              name: "match",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "test.attr": "" },
            },
            {
              traceId: "trace-null-filter",
              spanId: "span-no-match",
              name: "no-match",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "test.attr": "value" },
            },
          ],
        }),
      ),
    );

    // Filter with null/undefined value should default to empty string comparison
    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          attributeFilters: [{ key: "test.attr", operator: "eq", value: null }],
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    // Span with empty string value should match filter with null value (both compare to "")
    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-match");
  });

  it("handles inputMessagesQuery filter", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-input-msg",
              spanId: "span-matching",
              name: "matching",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "gen_ai.input_messages": "Hello, how are you today?",
              },
            },
            {
              traceId: "trace-input-msg",
              spanId: "span-non-matching",
              name: "non-matching",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.input_messages": "Goodbye" },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          inputMessagesQuery: "hello",
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-matching");
  });

  it("handles outputMessagesQuery filter", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-output-msg",
              spanId: "span-matching",
              name: "matching",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "gen_ai.output_messages": "The answer is 42",
              },
            },
            {
              traceId: "trace-output-msg",
              spanId: "span-non-matching",
              name: "non-matching",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: { "gen_ai.output_messages": "Unknown" },
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          outputMessagesQuery: "answer",
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-matching");
  });

  it("returns empty trace detail for non-existent trace", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});

    const traceBody = await parseJson<{
      spans: unknown[];
      rootSpanId: string | null;
      totalDurationMs: number | null;
    }>(await durableObject.fetch(createTraceRequest("missing-trace")));

    expect(traceBody.spans).toHaveLength(0);
    expect(traceBody.rootSpanId).toBeNull();
    expect(traceBody.totalDurationMs).toBeNull();
  });

  it("handles span without startTimeUnixNano (uses receivedAt)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const nowMs = Date.now();

    // Create a span without startTimeUnixNano - should fall back to receivedAt
    const payload: SpansBatchRequest = {
      environmentId: DEFAULT_ENV_ID,
      projectId: DEFAULT_PROJECT_ID,
      organizationId: DEFAULT_ORG_ID,
      receivedAt: nowMs,
      serviceName: DEFAULT_SERVICE_NAME,
      serviceVersion: DEFAULT_SERVICE_VERSION,
      resourceAttributes: null,
      spans: [
        {
          traceId: "trace-no-start",
          spanId: "span-no-start",
          name: "no-start-time",
          // No startTimeUnixNano - should use receivedAt as fallback
        },
      ],
    };

    await durableObject.fetch(
      new Request("https://realtime-spans/upsert", {
        method: "POST",
        body: JSON.stringify(payload),
        headers: { "content-type": "application/json" },
      }),
    );

    // Search should still find the span using receivedAt for time filtering
    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(nowMs - 60_000).toISOString(),
          endTime: new Date(nowMs + 60_000).toISOString(),
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-no-start");
  });

  it("filters by traceId", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-target",
              spanId: "span-target",
              name: "target",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
            {
              traceId: "trace-other",
              spanId: "span-other",
              name: "other",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          traceId: "trace-target",
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-target");
  });

  it("filters by spanId", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-filter",
              spanId: "span-target",
              name: "target",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
            {
              traceId: "trace-filter",
              spanId: "span-other",
              name: "other",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          spanId: "span-target",
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-target");
  });

  it("filters by spanNamePrefix with exact match", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-prefix",
              spanId: "span-librarian",
              name: "librarian",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
            {
              traceId: "trace-prefix",
              spanId: "span-librarian-call",
              name: "librarian.call",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
            {
              traceId: "trace-prefix",
              spanId: "span-chat",
              name: "chat anthropic/claude",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          spanNamePrefix: "librarian",
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string; name: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(2);
    const spanIds = searchBody.spans.map((s) => s.spanId).sort();
    expect(spanIds).toEqual(["span-librarian", "span-librarian-call"]);
  });

  it("filters by rootSpansOnly excluding child spans", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-root",
              spanId: "span-root",
              name: "root-span",
              parentSpanId: null,
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
            {
              traceId: "trace-root",
              spanId: "span-child",
              name: "child-span",
              parentSpanId: "span-root",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          rootSpansOnly: true,
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-root");
  });

  it("includes child spans when rootSpansOnly is false", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-all",
              spanId: "span-root-2",
              name: "root-span",
              parentSpanId: null,
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
            {
              traceId: "trace-all",
              spanId: "span-child-2",
              name: "child-span",
              parentSpanId: "span-root-2",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
      ),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          rootSpansOnly: false,
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(2);
  });

  it("handles inputMessagesQuery with object value (returns null from toSearchString)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    // Object values in gen_ai.input_messages will cause toSearchString to return null
    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-object-msg",
              spanId: "span-object-msg",
              name: "object-msg-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              // Object value - toSearchString returns null for objects
              attributes: {
                "gen_ai.input_messages": { nested: "object" },
              },
            },
            {
              traceId: "trace-object-msg",
              spanId: "span-string-msg",
              name: "string-msg-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "gen_ai.input_messages": "hello world",
              },
            },
          ],
        }),
      ),
    );

    // Search for "hello" - should only match the string value span
    const searchResponse = await durableObject.fetch(
      new Request("https://realtime-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          startTime: new Date(time.nowMs - 60_000).toISOString(),
          endTime: new Date(time.nowMs + 60_000).toISOString(),
          inputMessagesQuery: "hello",
        }),
        headers: { "content-type": "application/json" },
      }),
    );
    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-string-msg");
  });

  it("merges resourceAttributes when updating span (null incoming preserves existing)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    // First upsert with resourceAttributes
    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          resourceAttributes: { "service.region": "us-west" },
          spans: [
            {
              traceId: "trace-resource",
              spanId: "span-resource",
              name: "resource-span",
              startTimeUnixNano: time.startNano,
            },
          ],
        }),
      ),
    );

    // Second upsert with null resourceAttributes - must use raw request to pass null through
    // (createSpanBatch uses ?? which converts null to default)
    await durableObject.fetch(
      new Request("https://realtime-spans/upsert", {
        method: "POST",
        body: JSON.stringify({
          environmentId: DEFAULT_ENV_ID,
          projectId: DEFAULT_PROJECT_ID,
          organizationId: DEFAULT_ORG_ID,
          receivedAt: time.nowMs + 1000,
          serviceName: DEFAULT_SERVICE_NAME,
          serviceVersion: DEFAULT_SERVICE_VERSION,
          resourceAttributes: null,
          spans: [
            {
              traceId: "trace-resource",
              spanId: "span-resource",
              name: "resource-span",
              endTimeUnixNano: time.endNano(100),
            },
          ],
        }),
        headers: { "content-type": "application/json" },
      }),
    );

    // Get trace detail to verify resourceAttributes are preserved
    const traceResponse = await durableObject.fetch(
      createTraceRequest("trace-resource"),
    );
    const traceBody = await parseJson<{
      spans: Array<{ resourceAttributes: Record<string, unknown> | null }>;
    }>(traceResponse);

    expect(traceBody.spans).toHaveLength(1);
    // resourceAttributes may be returned as JSON string in trace detail response
    const resourceAttrs = traceBody.spans[0]?.resourceAttributes;
    expect(
      typeof resourceAttrs === "string"
        ? JSON.parse(resourceAttrs)
        : resourceAttrs,
    ).toEqual({
      "service.region": "us-west",
    });
  });

  it("extracts model from mirascope.response.model_id attribute (priority over gen_ai)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-mirascope-model",
              spanId: "span-mirascope-model",
              name: "mirascope-model-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "mirascope.response.model_id": "claude-sonnet-4-20250514",
                "gen_ai.request.model": "fallback-model",
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ model: string | null }>;
    }>(await durableObject.fetch(createTraceRequest("trace-mirascope-model")));

    // mirascope.response.model_id takes priority over gen_ai.request.model
    expect(traceBody.spans[0]?.model).toBe("claude-sonnet-4-20250514");
  });

  it("extracts provider from mirascope.response.provider_id attribute (priority over gen_ai)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-mirascope-provider",
              spanId: "span-mirascope-provider",
              name: "mirascope-provider-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "mirascope.response.provider_id": "anthropic",
                "gen_ai.system": "fallback-provider",
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ provider: string | null }>;
    }>(
      await durableObject.fetch(createTraceRequest("trace-mirascope-provider")),
    );

    // mirascope.response.provider_id takes priority over gen_ai.system
    expect(traceBody.spans[0]?.provider).toBe("anthropic");
  });

  it("extracts cost from mirascope.response.cost attribute (JSON string)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    // Cost in centicents: 50000 centicents = $5.00
    const costJson = JSON.stringify({
      input_cost: 25000,
      output_cost: 20000,
      cache_read_cost: 5000,
      total_cost: 50000,
    });

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-mirascope-cost",
              spanId: "span-mirascope-cost",
              name: "mirascope-cost-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "mirascope.response.cost": costJson,
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ costUsd: number | null }>;
    }>(await durableObject.fetch(createTraceRequest("trace-mirascope-cost")));

    // 50000 centicents / 10000 = $5.00
    expect(traceBody.spans[0]?.costUsd).toBe(5.0);
  });

  it("extracts cost from mirascope.response.cost attribute (object)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-mirascope-cost-obj",
              spanId: "span-mirascope-cost-obj",
              name: "mirascope-cost-obj-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                // Cost as object instead of JSON string: 10000 centicents = $1.00
                "mirascope.response.cost": {
                  input_cost: 5000,
                  output_cost: 3000,
                  total_cost: 10000,
                },
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ costUsd: number | null }>;
    }>(
      await durableObject.fetch(createTraceRequest("trace-mirascope-cost-obj")),
    );

    // 10000 centicents / 10000 = $1.00
    expect(traceBody.spans[0]?.costUsd).toBe(1.0);
  });

  it("handles mirascope.response.cost with invalid JSON (falls back to gen_ai.usage.cost)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-invalid-cost",
              spanId: "span-invalid-cost",
              name: "invalid-cost-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                // Invalid JSON string
                "mirascope.response.cost": "not-valid-json{",
                // Fallback cost in USD
                "gen_ai.usage.cost": 2.5,
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ costUsd: number | null }>;
    }>(await durableObject.fetch(createTraceRequest("trace-invalid-cost")));

    // Should fall back to gen_ai.usage.cost
    expect(traceBody.spans[0]?.costUsd).toBe(2.5);
  });

  it("extracts tokens from mirascope.response.usage attribute (JSON string)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    const usageJson = JSON.stringify({
      input_tokens: 100,
      output_tokens: 50,
      total_tokens: 150,
    });

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-mirascope-usage",
              spanId: "span-mirascope-usage",
              name: "mirascope-usage-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "mirascope.response.usage": usageJson,
                // gen_ai fallbacks should be ignored
                "gen_ai.usage.input_tokens": 999,
                "gen_ai.usage.output_tokens": 999,
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{
        inputTokens: number | null;
        outputTokens: number | null;
        totalTokens: number | null;
      }>;
    }>(await durableObject.fetch(createTraceRequest("trace-mirascope-usage")));

    expect(traceBody.spans[0]?.inputTokens).toBe(100);
    expect(traceBody.spans[0]?.outputTokens).toBe(50);
    expect(traceBody.spans[0]?.totalTokens).toBe(150);
  });

  it("falls back to gen_ai when mirascope.response.usage missing expected fields", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    // Usage object without token fields
    const usageJson = JSON.stringify({
      some_other_field: "value",
    });

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-missing-fields",
              spanId: "span-missing-fields",
              name: "missing-fields-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                "mirascope.response.usage": usageJson,
                // Should fall back to gen_ai values
                "gen_ai.usage.input_tokens": 42,
                "gen_ai.usage.output_tokens": 18,
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{
        inputTokens: number | null;
        outputTokens: number | null;
        totalTokens: number | null;
      }>;
    }>(await durableObject.fetch(createTraceRequest("trace-missing-fields")));

    // Should fall back to gen_ai values since mirascope.response.usage doesn't have the fields
    expect(traceBody.spans[0]?.inputTokens).toBe(42);
    expect(traceBody.spans[0]?.outputTokens).toBe(18);
    expect(traceBody.spans[0]?.totalTokens).toBe(60);
  });

  it("extracts tokens from mirascope.response.usage attribute (object, not JSON string)", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-usage-object",
              spanId: "span-usage-object",
              name: "usage-object-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                // Usage as object instead of JSON string
                "mirascope.response.usage": {
                  input_tokens: 200,
                  output_tokens: 100,
                  total_tokens: 300,
                },
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{
        inputTokens: number | null;
        outputTokens: number | null;
        totalTokens: number | null;
      }>;
    }>(await durableObject.fetch(createTraceRequest("trace-usage-object")));

    expect(traceBody.spans[0]?.inputTokens).toBe(200);
    expect(traceBody.spans[0]?.outputTokens).toBe(100);
    expect(traceBody.spans[0]?.totalTokens).toBe(300);
  });

  it("falls back to gen_ai when mirascope.response.cost.total_cost is not a valid number", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state, {});
    const time = createTimeContext();

    await durableObject.fetch(
      createUpsertRequest(
        createSpanBatch({
          receivedAt: time.nowMs,
          spans: [
            {
              traceId: "trace-invalid-total-cost",
              spanId: "span-invalid-total-cost",
              name: "invalid-total-cost-span",
              startTimeUnixNano: time.startNano,
              endTimeUnixNano: time.endNano(100),
              attributes: {
                // total_cost is not a valid number
                "mirascope.response.cost": JSON.stringify({
                  total_cost: "not-a-number",
                }),
                // Should fall back to gen_ai.usage.cost
                "gen_ai.usage.cost": 1.5,
              },
            },
          ],
        }),
      ),
    );

    const traceBody = await parseJson<{
      spans: Array<{ costUsd: number | null }>;
    }>(
      await durableObject.fetch(createTraceRequest("trace-invalid-total-cost")),
    );

    // Should fall back to gen_ai.usage.cost
    expect(traceBody.spans[0]?.costUsd).toBe(1.5);
  });
});

describe("RealtimeSpans global layer", () => {
  const originalRealtimeSpansLayer = realtimeSpansLayer;
  const buildUpsertRequest = (): SpansBatchRequest => ({
    environmentId: DEFAULT_ENV_ID,
    projectId: "project-1",
    organizationId: "org-1",
    receivedAt: Date.now(),
    serviceName: DEFAULT_SERVICE_NAME,
    serviceVersion: "1.0.0",
    resourceAttributes: null,
    spans: [
      {
        traceId: "trace-1",
        spanId: "span-1",
        name: "test-span",
      },
    ],
  });

  afterEach(() => {
    setRealtimeSpansLayer(originalRealtimeSpansLayer);
  });

  it("fails when global layer is not initialized", async () => {
    const upsertRequest = buildUpsertRequest();
    const searchInput = {
      environmentId: DEFAULT_ENV_ID,
      startTime: new Date("2024-01-01T00:00:00.000Z"),
      endTime: new Date("2024-01-01T00:00:01.000Z"),
    };
    const traceInput = {
      environmentId: DEFAULT_ENV_ID,
      traceId: "trace-1",
    };
    const existsInput = {
      environmentId: DEFAULT_ENV_ID,
      traceId: "trace-1",
      spanId: "span-1",
    };

    const program = Effect.gen(function* () {
      const realtime = yield* RealtimeSpans;
      const upsertError = yield* realtime
        .upsert(upsertRequest)
        .pipe(Effect.flip);
      const searchError = yield* realtime.search(searchInput).pipe(Effect.flip);
      const traceError = yield* realtime
        .getTraceDetail(traceInput)
        .pipe(Effect.flip);
      const existsError = yield* realtime.exists(existsInput).pipe(Effect.flip);

      return { upsertError, searchError, traceError, existsError };
    });

    const result = await Effect.runPromise(
      program.pipe(Effect.provide(realtimeSpansLayer)),
    );

    expect(result.upsertError.message).toBe("RealtimeSpans not initialized");
    expect(result.searchError.message).toBe("RealtimeSpans not initialized");
    expect(result.traceError.message).toBe("RealtimeSpans not initialized");
    expect(result.existsError.message).toBe("RealtimeSpans not initialized");
  });

  it("setRealtimeSpansLayer updates the global layer", async () => {
    const upsertRequest = buildUpsertRequest();
    const layer = Layer.succeed(RealtimeSpans, {
      upsert: () => Effect.void,
      search: () =>
        Effect.succeed({
          spans: [],
          total: 0,
          hasMore: false,
        }),
      getTraceDetail: () =>
        Effect.succeed({
          traceId: "trace-1",
          spans: [],
          rootSpanId: null,
          totalDurationMs: null,
        }),
      exists: () => Effect.succeed(false),
    });

    setRealtimeSpansLayer(layer);

    const program = Effect.gen(function* () {
      const realtime = yield* RealtimeSpans;
      yield* realtime.upsert(upsertRequest);
    });

    await Effect.runPromise(program.pipe(Effect.provide(realtimeSpansLayer)));
  });
});
