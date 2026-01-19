import { Effect, Layer } from "effect";
import {
  describe,
  expect,
  it,
  TestApiContext,
  createApiClient,
} from "@/tests/api";
import type { PublicProject, PublicEnvironment } from "@/db/schema";
import { TEST_DATABASE_URL } from "@/tests/db";
import {
  toTrace,
  DEFAULT_LIST_LIMIT,
  DEFAULT_LIST_OFFSET,
  listByFunctionHashHandler,
} from "@/api/traces.handlers";
import { Database } from "@/db";
import { Authentication } from "@/auth";
import { ClickHouseSearch } from "@/db/clickhouse/search";

describe("traces.handlers constants", () => {
  it("DEFAULT_LIST_LIMIT is 100", () => {
    expect(DEFAULT_LIST_LIMIT).toBe(100);
  });

  it("DEFAULT_LIST_OFFSET is 0", () => {
    expect(DEFAULT_LIST_OFFSET).toBe(0);
  });
});

describe("toTrace", () => {
  it("converts dates to ISO strings", () => {
    const now = new Date();
    const trace = {
      id: "test-id",
      otelTraceId: "test-otel-trace-id",
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      serviceName: "test-service",
      serviceVersion: "1.0.0",
      resourceAttributes: { "service.name": "test-service" },
      createdAt: now,
    };

    const result = toTrace(trace);

    expect(result.createdAt).toBe(now.toISOString());
  });

  it("handles null dates", () => {
    const trace = {
      id: "test-id",
      otelTraceId: "test-otel-trace-id",
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      serviceName: "test-service",
      serviceVersion: "1.0.0",
      resourceAttributes: { "service.name": "test-service" },
      createdAt: null,
    };

    const result = toTrace(trace);

    expect(result.createdAt).toBeNull();
  });
});

describe("listByFunctionHashHandler", () => {
  it("deduplicates traces with same traceId from multiple spans", async () => {
    const mockFunctionId = "func-123";
    const mockUserId = "user-123";
    const mockOrgId = "org-123";
    const mockProjectId = "proj-123";
    const mockEnvId = "env-123";

    // Mock Database layer that returns a function record
    const mockDatabaseLayer = Layer.succeed(Database, {
      organizations: {
        projects: {
          environments: {
            functions: {
              findByHash: () => Effect.succeed({ id: mockFunctionId }),
            },
          },
        },
      },
    } as never);

    // Mock Authentication layer - provides AuthResult with apiKeyInfo
    const mockAuthLayer = Layer.succeed(Authentication, {
      user: { id: mockUserId } as never,
      apiKeyInfo: {
        organizationId: mockOrgId,
        projectId: mockProjectId,
        environmentId: mockEnvId,
      } as never,
    });

    // Mock ClickHouseSearch that returns multiple spans with same traceId
    // This tests the deduplication logic at lines 117-118
    const mockClickHouseSearchLayer = Layer.succeed(ClickHouseSearch, {
      search: () =>
        Effect.succeed({
          spans: [
            {
              traceId: "trace-abc",
              spanId: "span-1",
              name: "first-span",
              startTime: new Date().toISOString(),
              durationMs: 100,
              model: null,
              provider: null,
              totalTokens: null,
              functionId: mockFunctionId,
              functionName: null,
            },
            {
              // Same traceId - should be deduplicated (hits line 117 false branch)
              traceId: "trace-abc",
              spanId: "span-2",
              name: "second-span",
              startTime: new Date().toISOString(),
              durationMs: 200,
              model: null,
              provider: null,
              totalTokens: null,
              functionId: mockFunctionId,
              functionName: null,
            },
            {
              // Different traceId - should be included
              traceId: "trace-def",
              spanId: "span-3",
              name: "third-span",
              startTime: new Date().toISOString(),
              durationMs: 300,
              model: null,
              provider: null,
              totalTokens: null,
              functionId: mockFunctionId,
              functionName: null,
            },
          ],
          total: 3,
          hasMore: false,
        }),
      getTraceDetail: () =>
        Effect.succeed({
          traceId: "",
          spans: [],
          rootSpanId: null,
          totalDurationMs: null,
        }),
      getAnalyticsSummary: () =>
        Effect.succeed({
          totalSpans: 0,
          avgDurationMs: null,
          p50DurationMs: null,
          p95DurationMs: null,
          p99DurationMs: null,
          errorRate: 0,
          totalTokens: 0,
          totalCostUsd: 0,
          topModels: [],
          topFunctions: [],
        }),
      getSpanDetail: () =>
        Effect.succeed({
          traceId: "",
          spanId: "",
          parentSpanId: null,
          environmentId: "",
          projectId: "",
          organizationId: "",
          startTime: new Date().toISOString(),
          endTime: new Date().toISOString(),
          durationMs: null,
          name: "",
          kind: 1,
          statusCode: null,
          statusMessage: null,
          model: null,
          provider: null,
          inputTokens: null,
          outputTokens: null,
          totalTokens: null,
          costUsd: null,
          functionId: null,
          functionName: null,
          functionVersion: null,
          errorType: null,
          errorMessage: null,
          attributes: "{}",
          events: null,
          links: null,
          serviceName: null,
          serviceVersion: null,
          resourceAttributes: null,
        }),
      getTimeSeriesMetrics: () =>
        Effect.succeed({ points: [], timeFrame: "day" }),
      getFunctionAggregates: () =>
        Effect.succeed({ functions: [], total: 0 }),
    });

    const layers = Layer.mergeAll(
      mockDatabaseLayer,
      mockAuthLayer,
      mockClickHouseSearchLayer,
    );

    const result = await Effect.runPromise(
      listByFunctionHashHandler("test-hash", {}).pipe(Effect.provide(layers)),
    );

    // Should have 2 unique traces, not 3 (trace-abc deduplicated)
    expect(result.traces).toHaveLength(2);
    expect(result.traces.map((t) => t.id)).toEqual(["trace-abc", "trace-def"]);
    expect(result.total).toBe(3); // Total includes all spans
  });
});

describe.sequential("Traces API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;
  let apiKeyClient: Awaited<ReturnType<typeof createApiClient>>["client"];
  let disposeApiKeyClient: (() => Promise<void>) | null = null;

  it.effect(
    "POST /organizations/:orgId/projects - create project for traces test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Traces Test Project", slug: "traces-test-project" },
        });
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments - create environment for traces test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "Traces Test Environment", slug: "traces-test-env" },
        });
        expect(environment.id).toBeDefined();
      }),
  );

  it.effect("setup API key client for traces tests", () =>
    Effect.gen(function* () {
      const { org, owner } = yield* TestApiContext;

      const apiKeyInfo = {
        apiKeyId: "test-api-key-id",
        organizationId: org.id,
        projectId: project.id,
        environmentId: environment.id,
        ownerId: owner.id,
        ownerEmail: owner.email,
        ownerName: owner.name,
        ownerDeletedAt: owner.deletedAt,
      };

      const result = yield* Effect.promise(() =>
        createApiClient(
          TEST_DATABASE_URL,
          owner,
          apiKeyInfo,
          () => Effect.void,
        ),
      );
      apiKeyClient = result.client;
      disposeApiKeyClient = result.dispose;
    }),
  );

  it.effect("GET /traces/function/hash/:hash - defaults limit and offset", () =>
    Effect.gen(function* () {
      const hash = `traces-test-hash-${Date.now()}`;

      yield* apiKeyClient.functions.create({
        payload: {
          name: "traces_list_by_hash",
          hash,
          code: "def traces_list_by_hash(): pass",
          signature: "def traces_list_by_hash()",
          signatureHash: "traces-list-by-hash",
        },
      });

      const result = yield* apiKeyClient.traces.listByFunctionHash({
        path: { hash },
        urlParams: {},
      });

      expect(result.traces).toEqual([]);
      expect(result.total).toBe(0);
    }),
  );

  it.effect("POST /traces - creates trace", () =>
    Effect.gen(function* () {
      const payload = {
        resourceSpans: [
          {
            resource: {
              attributes: [
                {
                  key: "service.name",
                  value: { stringValue: "test-service" },
                },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test-scope", version: "1.0.0" },
                spans: [
                  {
                    traceId: "test-trace-id",
                    spanId: "test-span-id",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ],
      };

      const result = yield* apiKeyClient.traces.create({ payload });
      expect(result.partialSuccess).toBeDefined();
    }),
  );

  it.effect("POST /traces - returns partialSuccess on rejected spans", () =>
    Effect.gen(function* () {
      const payload = {
        resourceSpans: [
          {
            resource: {
              attributes: [
                {
                  key: "service.name",
                  value: { stringValue: "duplicate-span-service" },
                },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test-scope", version: "1.0.0" },
                spans: [
                  {
                    traceId: "duplicate-trace-id",
                    spanId: "duplicate-span-id",
                    name: "duplicate-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                  {
                    traceId: "duplicate-trace-id",
                    spanId: "duplicate-span-id",
                    name: "duplicate-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ],
      };

      const { org, owner } = yield* TestApiContext;

      const apiKeyInfo = {
        apiKeyId: "test-api-key-id",
        organizationId: org.id,
        projectId: project.id,
        environmentId: environment.id,
        ownerId: owner.id,
        ownerEmail: owner.email,
        ownerName: owner.name,
        ownerDeletedAt: owner.deletedAt,
      };

      const { client: apiKeyClient, dispose } = yield* Effect.promise(() =>
        createApiClient(TEST_DATABASE_URL, owner, apiKeyInfo, () =>
          Effect.fail(new Error("Queue send failed")),
        ),
      );

      let result;
      try {
        result = yield* apiKeyClient.traces.create({ payload });
      } finally {
        yield* Effect.promise(dispose);
      }

      expect(result.partialSuccess?.rejectedSpans).toBe(2);
      expect(result.partialSuccess?.errorMessage).toContain("2 spans");
    }),
  );

  it.effect("Dispose API key client", () =>
    Effect.gen(function* () {
      if (disposeApiKeyClient) {
        yield* Effect.promise(disposeApiKeyClient);
      }
    }),
  );
});
