/**
 * @fileoverview Tests for RealtimeSpansDurableObject realtime cache behavior.
 */

import { describe, it, expect } from "vitest";
import { RealtimeSpansDurableObjectBase as RealtimeSpansDurableObject } from "@/workers/realtimeSpans/durableObject";
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
  DEFAULT_SERVICE_NAME,
  DEFAULT_ENV_ID,
} from "@/tests/workers/realtimeSpans";

describe("RealtimeSpansDurableObject", () => {
  it("upserts spans and checks existence", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state);

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
    const durableObject = new RealtimeSpansDurableObject(state);

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

  it("returns trace detail spans", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state);

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

  it("returns trace detail with resourceAttributes serialized", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state);

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

  it("returns trace detail with null resourceAttributes", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state);
    const time = createTimeContext();

    // Create span batch with explicitly null resourceAttributes
    await durableObject.fetch(
      createUpsertRequest({
        environmentId: DEFAULT_ENV_ID,
        projectId: "proj-1",
        organizationId: "org-1",
        receivedAt: time.nowMs,
        serviceName: DEFAULT_SERVICE_NAME,
        serviceVersion: "1.0.0",
        resourceAttributes: null as unknown as Record<string, unknown>,
        spans: [
          {
            traceId: "trace-null-attrs",
            spanId: "span-null-attrs",
            name: "null-attrs-span",
            startTimeUnixNano: time.startNano,
            endTimeUnixNano: time.endNano(1000),
          },
        ],
      }),
    );

    const traceResponse = await durableObject.fetch(
      createTraceRequest("trace-null-attrs"),
    );
    const traceBody = await parseJson<{
      spans: Array<{
        spanId: string;
        resourceAttributes: string | null;
      }>;
    }>(traceResponse);

    expect(traceBody.spans).toHaveLength(1);
    expect(traceBody.spans[0]?.resourceAttributes).toBeNull();
  });

  it("keeps long-running spans when endTime exceeds query range", async () => {
    const state = createState();
    const durableObject = new RealtimeSpansDurableObject(state);

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
      const durableObject = new RealtimeSpansDurableObject(state);
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
      const durableObject = new RealtimeSpansDurableObject(state);
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
      const durableObject = new RealtimeSpansDurableObject(state);
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
      const durableObject = new RealtimeSpansDurableObject(state);
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
      const durableObject = new RealtimeSpansDurableObject(state);
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
