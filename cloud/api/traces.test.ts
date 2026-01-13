import { Effect, Layer } from "effect";
import {
  describe,
  expect,
  it,
  TestApiContext,
  createApiClient,
} from "@/tests/api";
import {
  it as itDb,
  TEST_DATABASE_URL,
  TestEnvironmentFixture,
} from "@/tests/db";
import type { PublicProject, PublicEnvironment } from "@/db/schema";
import { toTrace, listByFunctionHashHandler } from "@/api/traces.handlers";
import { Authentication } from "@/auth";
import { Database } from "@/db";
import { NotFoundError } from "@/errors";
import { ClickHouseSearch } from "@/db/clickhouse/search";

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

describe("listByFunctionHashHandler", () => {
  itDb.effect("returns traces for function hash", () =>
    Effect.gen(function* () {
      const { environment, project, org, owner } =
        yield* TestEnvironmentFixture;
      const db = yield* Database;

      // Create a function with a known hash
      const fn = yield* db.organizations.projects.environments.functions.create(
        {
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: {
            name: "test-function",
            hash: "test-hash-for-traces",
            code: "def test(): pass",
            signature: "def test()",
            signatureHash: "sig-hash",
          },
        },
      );

      // Mock ClickHouseSearch to return spans with this function
      const mockClickHouseSearch = Layer.succeed(ClickHouseSearch, {
        search: () =>
          Effect.succeed({
            spans: [
              {
                id: "span-1",
                traceId: "trace-1",
                spanId: "otel-span-1",
                name: "test-span",
                startTime: "2024-01-01T00:00:00Z",
                durationMs: 100,
                model: "gpt-4",
                provider: "openai",
                totalTokens: 100,
                functionId: fn.id,
                functionName: "test-function",
              },
              {
                id: "span-2",
                traceId: "trace-1",
                spanId: "otel-span-2",
                name: "test-span-2",
                startTime: "2024-01-01T00:00:01Z",
                durationMs: 50,
                model: "gpt-4",
                provider: "openai",
                totalTokens: 50,
                functionId: fn.id,
                functionName: "test-function",
              },
              {
                id: "span-3",
                traceId: "trace-2",
                spanId: "otel-span-3",
                name: "test-span-3",
                startTime: "2024-01-01T00:00:02Z",
                durationMs: 75,
                model: "gpt-4",
                provider: "openai",
                totalTokens: 75,
                functionId: fn.id,
                functionName: "test-function",
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
      });

      const authLayer = Layer.succeed(Authentication, {
        user: owner,
        apiKeyInfo: {
          apiKeyId: "test-key",
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          ownerId: owner.id,
          ownerEmail: owner.email,
          ownerName: owner.name,
          ownerDeletedAt: owner.deletedAt,
        },
      });

      const result = yield* listByFunctionHashHandler("test-hash-for-traces", {
        limit: 100,
        offset: 0,
      }).pipe(Effect.provide(Layer.mergeAll(authLayer, mockClickHouseSearch)));

      // Should return unique traces (2 traces from 3 spans)
      expect(result.traces).toHaveLength(2);
      expect(result.traces[0]?.otelTraceId).toBe("trace-1");
      expect(result.traces[1]?.otelTraceId).toBe("trace-2");
      expect(result.total).toBe(3);
    }),
  );

  itDb.effect("returns NotFoundError for non-existent function hash", () =>
    Effect.gen(function* () {
      const { environment, project, org, owner } =
        yield* TestEnvironmentFixture;

      const mockClickHouseSearch = Layer.succeed(ClickHouseSearch, {
        search: () => Effect.succeed({ spans: [], total: 0, hasMore: false }),
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
      });

      const authLayer = Layer.succeed(Authentication, {
        user: owner,
        apiKeyInfo: {
          apiKeyId: "test-key",
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          ownerId: owner.id,
          ownerEmail: owner.email,
          ownerName: owner.name,
          ownerDeletedAt: owner.deletedAt,
        },
      });

      const result = yield* listByFunctionHashHandler(
        "non-existent-hash",
        {},
      ).pipe(
        Effect.provide(Layer.mergeAll(authLayer, mockClickHouseSearch)),
        Effect.flip,
      );

      expect(result).toBeInstanceOf(NotFoundError);
    }),
  );

  itDb.effect("returns empty traces when no spans match function", () =>
    Effect.gen(function* () {
      const { environment, project, org, owner } =
        yield* TestEnvironmentFixture;
      const db = yield* Database;

      // Create a function
      yield* db.organizations.projects.environments.functions.create({
        userId: owner.id,
        organizationId: org.id,
        projectId: project.id,
        environmentId: environment.id,
        data: {
          name: "empty-function",
          hash: "empty-hash-for-traces",
          code: "def empty(): pass",
          signature: "def empty()",
          signatureHash: "empty-sig-hash",
        },
      });

      // Mock ClickHouseSearch to return empty spans
      const mockClickHouseSearch = Layer.succeed(ClickHouseSearch, {
        search: () => Effect.succeed({ spans: [], total: 0, hasMore: false }),
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
      });

      const authLayer = Layer.succeed(Authentication, {
        user: owner,
        apiKeyInfo: {
          apiKeyId: "test-key",
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          ownerId: owner.id,
          ownerEmail: owner.email,
          ownerName: owner.name,
          ownerDeletedAt: owner.deletedAt,
        },
      });

      const result = yield* listByFunctionHashHandler("empty-hash-for-traces", {
        limit: 50,
      }).pipe(Effect.provide(Layer.mergeAll(authLayer, mockClickHouseSearch)));

      expect(result.traces).toHaveLength(0);
      expect(result.total).toBe(0);
    }),
  );
});
