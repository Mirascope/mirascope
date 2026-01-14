import { Effect, Layer } from "effect";
import { describe, it, expect } from "@/tests/api";
import { handleRequest } from "@/api/handler";
import type { ListByFunctionHashResponse } from "@/api/traces.schemas";
import type { PublicUser } from "@/db/schema";
import { ClickHouseError, HandlerError } from "@/errors";
import { ClickHouse } from "@/db/clickhouse/client";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { Database } from "@/db";
import { DrizzleORM } from "@/db/client";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import { SpansIngestQueue } from "@/workers/spanIngestQueue";
import { SettingsService, getSettings } from "@/settings";
import { CLICKHOUSE_CONNECTION_FILE } from "@/tests/global-setup";
import { MockDrizzleORMLayer } from "@/tests/mock-drizzle";
import type { PublicFunction } from "@/db/functions";
import fs from "fs";

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
  deletedAt: null,
};

const listByFunctionHashIdentifiers = {
  organizationId: "organization-1",
  projectId: "project-1",
  environmentId: "environment-1",
};

const listByFunctionHashFunction: PublicFunction = {
  id: "function-id",
  hash: "hash-list-by-function",
  signatureHash: "signature-hash-list-by-function",
  name: "test-function",
  description: null,
  version: "1.0",
  tags: null,
  metadata: null,
  code: "export const handler = () => null;",
  signature: "function handler()",
  dependencies: null,
  environmentId: listByFunctionHashIdentifiers.environmentId,
  projectId: listByFunctionHashIdentifiers.projectId,
  organizationId: listByFunctionHashIdentifiers.organizationId,
  createdAt: new Date(0),
  updatedAt: new Date(0),
};

type ClickHouseConnectionFile = {
  url: string;
  user: string;
  password: string;
  database: string;
  nativePort: number;
};

function getTestClickHouseConfig(): ClickHouseConnectionFile {
  try {
    const raw = fs.readFileSync(CLICKHOUSE_CONNECTION_FILE, "utf-8");
    return JSON.parse(raw) as ClickHouseConnectionFile;
  } catch {
    throw new Error(
      "TEST_CLICKHOUSE_URL not set. Ensure global-setup.ts ran successfully.",
    );
  }
}

const clickhouseConfig = getTestClickHouseConfig();
const settings = getSettings();
const settingsLayer = Layer.succeed(SettingsService, {
  ...settings,
  env: "test",
  CLICKHOUSE_URL: clickhouseConfig.url,
  CLICKHOUSE_USER: clickhouseConfig.user,
  CLICKHOUSE_PASSWORD: clickhouseConfig.password,
  CLICKHOUSE_DATABASE: clickhouseConfig.database,
});
const clickHouseSearchLayer = ClickHouseSearch.Default.pipe(
  Layer.provide(ClickHouse.Default),
  Layer.provide(settingsLayer),
);
const drizzleLayer = MockDrizzleORMLayer;
const spansIngestQueueLayer = Layer.succeed(SpansIngestQueue, {
  send: () => Effect.void,
});
const realtimeSpansLayer = Layer.succeed(RealtimeSpans, {
  upsert: () => Effect.void,
  search: () => Effect.succeed({ spans: [], total: 0, hasMore: false }),
  getTraceDetail: () =>
    Effect.succeed({
      traceId: "",
      spans: [],
      rootSpanId: null,
      totalDurationMs: null,
    }),
  exists: () => Effect.succeed(false),
});

describe("handleRequest", () => {
  it.effect("should return 404 for unknown route", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      const req = new Request(
        "http://localhost/api/v0/this-route-does-not-exist",
        { method: "GET" },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        environment: "test",
        prefix: "/api/v0",
        drizzle: yield* DrizzleORM,
        clickHouseSearch,
        realtimeSpans: yield* RealtimeSpans,
        spansIngestQueue: yield* SpansIngestQueue,
      });

      expect(response.status).toBe(404);
      expect(matched).toBe(false);
    }).pipe(
      Effect.provide(
        Layer.mergeAll(
          drizzleLayer,
          clickHouseSearchLayer,
          spansIngestQueueLayer,
          realtimeSpansLayer,
        ),
      ),
    ),
  );

  it.effect("should return 404 for non-existing routes", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      const req = new Request(
        "http://localhost/api/v0/this-route-does-not-exist",
        { method: "GET" },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        environment: "test",
        prefix: "/api/v0",
        drizzle: yield* DrizzleORM,
        clickHouseSearch,
        realtimeSpans: yield* RealtimeSpans,
        spansIngestQueue: yield* SpansIngestQueue,
      });

      expect(response.status).toBe(404);
      expect(matched).toBe(false);
    }).pipe(
      Effect.provide(
        Layer.mergeAll(
          drizzleLayer,
          clickHouseSearchLayer,
          spansIngestQueueLayer,
          realtimeSpansLayer,
        ),
      ),
    ),
  );

  it.effect(
    "should return 404 when pathname exactly matches prefix (no route)",
    () =>
      Effect.gen(function* () {
        const clickHouseSearch = yield* ClickHouseSearch;
        const req = new Request("http://localhost/api/v0", { method: "GET" });

        const { matched, response } = yield* handleRequest(req, {
          user: mockUser,
          environment: "test",
          prefix: "/api/v0",
          drizzle: yield* DrizzleORM,
          clickHouseSearch,
          realtimeSpans: yield* RealtimeSpans,
          spansIngestQueue: yield* SpansIngestQueue,
        });

        // The path becomes "/" after stripping prefix, which doesn't match any route
        expect(response.status).toBe(404);
        expect(matched).toBe(false);
      }).pipe(
        Effect.provide(
          Layer.mergeAll(
            drizzleLayer,
            clickHouseSearchLayer,
            spansIngestQueueLayer,
            realtimeSpansLayer,
          ),
        ),
      ),
  );

  it.effect(
    "should return error for a request that triggers an exception",
    () =>
      Effect.gen(function* () {
        const clickHouseSearch = yield* ClickHouseSearch;
        const faultyRequest = new Proxy(
          {},
          {
            get() {
              throw new Error("boom");
            },
          },
        ) as Request;

        const error = yield* handleRequest(faultyRequest, {
          user: mockUser,
          environment: "test",
          drizzle: yield* DrizzleORM,
          clickHouseSearch,
          realtimeSpans: yield* RealtimeSpans,
          spansIngestQueue: yield* SpansIngestQueue,
        }).pipe(Effect.flip);

        expect(error).toBeInstanceOf(HandlerError);
        expect(error.message).toContain(
          "[Effect API] Error handling request: boom",
        );
      }).pipe(
        Effect.provide(
          Layer.mergeAll(
            drizzleLayer,
            clickHouseSearchLayer,
            spansIngestQueueLayer,
            realtimeSpansLayer,
          ),
        ),
      ),
  );

  it.effect("should handle POST requests with body", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      // POST request with body to trigger duplex: "half"
      const req = new Request(
        "http://localhost/api/v0/organizations/00000000-0000-0000-0000-000000000099/projects",
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ name: "Test", slug: "test" }),
        },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        environment: "test",
        prefix: "/api/v0",
        drizzle: yield* DrizzleORM,
        clickHouseSearch,
        realtimeSpans: yield* RealtimeSpans,
        spansIngestQueue: yield* SpansIngestQueue,
      });

      expect(matched).toBe(true);
      expect(response.status).toBeGreaterThanOrEqual(400);
    }).pipe(
      Effect.provide(
        Layer.mergeAll(
          drizzleLayer,
          clickHouseSearchLayer,
          spansIngestQueueLayer,
          realtimeSpansLayer,
        ),
      ),
    ),
  );

  it.effect("should transform _tag in JSON error responses", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      // Trigger a NotFoundError by trying to get a non-existent organization
      const req = new Request(
        "http://localhost/api/v0/organizations/00000000-0000-0000-0000-000000000099",
        {
          method: "GET",
        },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        environment: "test",
        prefix: "/api/v0",
        drizzle: yield* DrizzleORM,
        clickHouseSearch,
        realtimeSpans: yield* RealtimeSpans,
        spansIngestQueue: yield* SpansIngestQueue,
      });

      const body = yield* Effect.promise(() => response.text());

      expect(matched).toBe(true);
      expect(response.status).toBeGreaterThanOrEqual(400);
      // Ensure _tag is transformed to tag in error responses
      expect(body).toContain('"tag"');
      expect(body).not.toContain('"_tag"');
    }).pipe(
      Effect.provide(
        Layer.mergeAll(
          drizzleLayer,
          clickHouseSearchLayer,
          spansIngestQueueLayer,
          realtimeSpansLayer,
        ),
      ),
    ),
  );

  it.effect("should handle listByFunctionHash requests", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;

      const apiKeyInfo = {
        apiKeyId: "api-key-id",
        organizationId: listByFunctionHashIdentifiers.organizationId,
        projectId: listByFunctionHashIdentifiers.projectId,
        environmentId: listByFunctionHashIdentifiers.environmentId,
        ownerId: mockUser.id,
        ownerEmail: mockUser.email,
        ownerName: mockUser.name,
        ownerDeletedAt: mockUser.deletedAt,
      };

      const requestWithParams = new Request(
        `http://localhost/api/v0/traces/function/hash/${listByFunctionHashFunction.hash}?limit=1&offset=0`,
        { method: "GET" },
      );

      const { matched, response } = yield* handleRequest(requestWithParams, {
        user: mockUser,
        apiKeyInfo,
        environment: "test",
        prefix: "/api/v0",
        drizzle: yield* DrizzleORM,
        clickHouseSearch,
        realtimeSpans: yield* RealtimeSpans,
        spansIngestQueue: yield* SpansIngestQueue,
      });

      const body = (yield* Effect.promise(() =>
        response.json(),
      )) as ListByFunctionHashResponse;

      expect(matched).toBe(true);
      expect(response.status).toBe(200);
      expect(body.total).toBe(2);
      expect(body.traces).toHaveLength(1);
      expect(body.traces[0]?.id).toBe("trace-1");
      expect(body.traces[0]?.otelTraceId).toBe("trace-1");

      const requestWithoutParams = new Request(
        `http://localhost/api/v0/traces/function/hash/${listByFunctionHashFunction.hash}`,
        { method: "GET" },
      );

      const { matched: matchedDefault, response: responseDefault } =
        yield* handleRequest(requestWithoutParams, {
          user: mockUser,
          apiKeyInfo,
          environment: "test",
          prefix: "/api/v0",
          drizzle: yield* DrizzleORM,
          clickHouseSearch,
          realtimeSpans: yield* RealtimeSpans,
          spansIngestQueue: yield* SpansIngestQueue,
        });

      expect(matchedDefault).toBe(true);
      expect(responseDefault.status).toBe(200);
    }).pipe(
      Effect.provide(
        Layer.mergeAll(
          drizzleLayer,
          spansIngestQueueLayer,
          realtimeSpansLayer,
          Layer.succeed(Database, {
            organizations: {
              projects: {
                environments: {
                  functions: {
                    findByHash: () =>
                      Effect.succeed(listByFunctionHashFunction),
                  },
                },
              },
            },
          } as never),
          Layer.succeed(ClickHouseSearch, {
            search: () =>
              Effect.succeed({
                spans: [
                  {
                    traceId: "trace-1",
                    spanId: "span-1",
                    name: "span",
                    startTime: new Date().toISOString(),
                    durationMs: 10,
                    model: null,
                    provider: null,
                    totalTokens: null,
                    functionId: "function-id",
                    functionName: "test-function",
                  },
                  {
                    traceId: "trace-1",
                    spanId: "span-2",
                    name: "span",
                    startTime: new Date().toISOString(),
                    durationMs: 20,
                    model: null,
                    provider: null,
                    totalTokens: null,
                    functionId: "function-id",
                    functionName: "test-function",
                  },
                ],
                total: 2,
                hasMore: false,
              }),
            getTraceDetail: () =>
              Effect.fail(
                new ClickHouseError({
                  message: "getTraceDetail not used",
                }),
              ),
            getAnalyticsSummary: () =>
              Effect.fail(
                new ClickHouseError({
                  message: "getAnalyticsSummary not used",
                }),
              ),
          }),
        ),
      ),
    ),
  );
});
