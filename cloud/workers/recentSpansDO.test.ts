/**
 * @fileoverview Tests for RecentSpansDO realtime cache behavior.
 */

import { describe, it, expect } from "vitest";
import type { DurableObjectState } from "@cloudflare/workers-types";
import { RecentSpansDO } from "@/workers/recentSpansDO";

// =============================================================================
// Mocks
// =============================================================================

class MockStorage {
  private store = new Map<string, unknown>();

  get<T>(key: string): Promise<T | undefined> {
    return Promise.resolve(this.store.get(key) as T | undefined);
  }

  put<T>(key: string, value: T): Promise<void> {
    this.store.set(key, value);
    return Promise.resolve();
  }

  delete(keys: string | string[]): Promise<void> {
    if (Array.isArray(keys)) {
      for (const key of keys) {
        this.store.delete(key);
      }
      return Promise.resolve();
    }
    this.store.delete(keys);
    return Promise.resolve();
  }

  list<T>(options?: { prefix?: string }): Promise<Map<string, T>> {
    if (!options?.prefix) {
      return Promise.resolve(new Map(this.store.entries()) as Map<string, T>);
    }
    const entries = Array.from(this.store.entries()).filter(([key]) =>
      key.startsWith(options.prefix ?? ""),
    );
    return Promise.resolve(new Map(entries) as Map<string, T>);
  }
}

const parseJson = async <T>(response: Response): Promise<T> =>
  (await response.json()) as T;

const createState = (): DurableObjectState =>
  ({
    storage: new MockStorage(),
  }) as unknown as DurableObjectState;

const createPayload = (overrides?: Partial<Record<string, unknown>>) => {
  const now = BigInt(Date.now());
  const start = now * 1_000_000n;
  const mid = start + 500_000_000n;
  const end = start + 1_000_000_000n;
  const end2 = start + 1_500_000_000n;

  return {
    environmentId: "env-1",
    projectId: "proj-1",
    organizationId: "org-1",
    receivedAt: Date.now(),
    serviceName: "service",
    serviceVersion: "1.0.0",
    resourceAttributes: { region: "us-east-1" },
    spans: [
      {
        traceId: "trace-1",
        spanId: "span-1",
        parentSpanId: null,
        name: "alpha",
        kind: 1,
        startTimeUnixNano: start.toString(),
        endTimeUnixNano: end.toString(),
        attributes: { "gen_ai.request.model": "gpt-4" },
        status: { code: 1, message: "OK" },
        events: [{ name: "event-1" }],
        links: [{ traceId: "trace-2" }],
        droppedAttributesCount: 0,
        droppedEventsCount: 0,
        droppedLinksCount: 0,
      },
      {
        traceId: "trace-1",
        spanId: "span-2",
        parentSpanId: "span-1",
        name: "beta",
        kind: 1,
        startTimeUnixNano: mid.toString(),
        endTimeUnixNano: end2.toString(),
        attributes: { "gen_ai.request.model": "gpt-4" },
      },
    ],
    ...overrides,
  };
};

// =============================================================================
// Tests
// =============================================================================

describe("RecentSpansDO", () => {
  it("upserts spans and checks existence", async () => {
    const state = createState();
    const durableObject = new RecentSpansDO(state);

    const upsertResponse = await durableObject.fetch(
      new Request("https://recent-spans/upsert", {
        method: "POST",
        body: JSON.stringify(createPayload()),
        headers: { "content-type": "application/json" },
      }),
    );

    expect(upsertResponse.status).toBe(204);

    const existsResponse = await durableObject.fetch(
      new Request("https://recent-spans/exists", {
        method: "POST",
        body: JSON.stringify({
          environmentId: "env-1",
          traceId: "trace-1",
          spanId: "span-1",
        }),
        headers: { "content-type": "application/json" },
      }),
    );

    const existsBody = await parseJson<{ exists: boolean }>(existsResponse);
    expect(existsBody.exists).toBe(true);
  });

  it("searches spans within time range", async () => {
    const state = createState();
    const durableObject = new RecentSpansDO(state);

    await durableObject.fetch(
      new Request("https://recent-spans/upsert", {
        method: "POST",
        body: JSON.stringify(createPayload()),
        headers: { "content-type": "application/json" },
      }),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://recent-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: "env-1",
          startTime: new Date(Date.now() - 60_000).toISOString(),
          endTime: new Date(Date.now() + 60_000).toISOString(),
          query: "alpha",
          sortBy: "start_time",
          sortOrder: "desc",
        }),
        headers: { "content-type": "application/json" },
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
    const durableObject = new RecentSpansDO(state);

    await durableObject.fetch(
      new Request("https://recent-spans/upsert", {
        method: "POST",
        body: JSON.stringify(createPayload()),
        headers: { "content-type": "application/json" },
      }),
    );

    const traceResponse = await durableObject.fetch(
      new Request("https://recent-spans/trace/trace-1", {
        method: "GET",
      }),
    );

    const traceBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      rootSpanId: string | null;
    }>(traceResponse);

    expect(traceBody.spans).toHaveLength(2);
    expect(traceBody.rootSpanId).toBe("span-1");
  });

  it("keeps long-running spans when endTime exceeds query range", async () => {
    const state = createState();
    const durableObject = new RecentSpansDO(state);

    const nowMs = Date.now();
    const start = BigInt(nowMs - 5_000) * 1_000_000n;
    const end = BigInt(nowMs + 120_000) * 1_000_000n;

    await durableObject.fetch(
      new Request("https://recent-spans/upsert", {
        method: "POST",
        body: JSON.stringify(
          createPayload({
            spans: [
              {
                traceId: "trace-long",
                spanId: "span-long",
                name: "long-span",
                startTimeUnixNano: start.toString(),
                endTimeUnixNano: end.toString(),
              },
            ],
          }),
        ),
        headers: { "content-type": "application/json" },
      }),
    );

    const searchResponse = await durableObject.fetch(
      new Request("https://recent-spans/search", {
        method: "POST",
        body: JSON.stringify({
          environmentId: "env-1",
          startTime: new Date(nowMs - 10_000).toISOString(),
          endTime: new Date(nowMs + 5_000).toISOString(),
        }),
        headers: { "content-type": "application/json" },
      }),
    );

    const searchBody = await parseJson<{
      spans: Array<{ spanId: string }>;
      total: number;
    }>(searchResponse);

    expect(searchBody.total).toBe(1);
    expect(searchBody.spans[0]?.spanId).toBe("span-long");
  });
});
