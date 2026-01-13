import { Effect, Layer } from "effect";
import {
  describe,
  it,
  expect,
  TestApiContext,
  createApiClient,
} from "@/tests/api";
import type {
  ApiKeyInfo,
  PublicEnvironment,
  PublicProject,
  PublicUser,
} from "@/db/schema";
import { TEST_DATABASE_URL } from "@/tests/db";
import { Authentication } from "@/auth";
import { ClickHouseSearch } from "@/clickhouse/search";
import { ClickHouse } from "@/clickhouse/client";
import { SettingsService, getSettings } from "@/settings";
import { searchHandler, getTraceDetailHandler } from "@/api/search.handlers";
import type {
  SearchRequest,
  SearchResponse,
  TraceDetailResponse,
  AnalyticsSummaryResponse,
} from "@/api/search.schemas";
import { RealtimeSpans } from "@/realtimeSpans";

describe.sequential("Search API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;
  let apiKeyClient: Awaited<ReturnType<typeof createApiClient>>["client"];
  let disposeApiKeyClient: (() => Promise<void>) | null = null;
  let apiKeyInfo: ApiKeyInfo | undefined;
  let ownerFromContext: PublicUser | null = null;

  it.effect(
    "POST /organizations/:orgId/projects - create project for search test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Search Test Project", slug: "search-test-project" },
        });
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments - create environment for search test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: {
            name: "Search Test Environment",
            slug: "search-test-env",
          },
        });
        expect(environment.id).toBeDefined();
      }),
  );

  it.effect("Create API key client for search tests", () =>
    Effect.gen(function* () {
      const { org, owner } = yield* TestApiContext;
      apiKeyInfo = {
        apiKeyId: "test-search-api-key-id",
        organizationId: org.id,
        projectId: project.id,
        environmentId: environment.id,
        ownerId: owner.id,
        ownerEmail: owner.email,
        ownerName: owner.name,
        ownerDeletedAt: owner.deletedAt,
      };
      ownerFromContext = owner;

      const result = yield* Effect.promise(() =>
        createApiClient(TEST_DATABASE_URL, owner, apiKeyInfo),
      );
      apiKeyClient = result.client;
      disposeApiKeyClient = result.dispose;
    }),
  );

  it.effect(
    "POST /traces/search - returns empty results for new environment",
    () =>
      Effect.gen(function* () {
        const result = yield* apiKeyClient.traces.search({
          payload: {
            startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            endTime: new Date().toISOString(),
          },
        });

        expect(result.spans).toBeDefined();
        expect(Array.isArray(result.spans)).toBe(true);
        expect(typeof result.total).toBe("number");
        expect(typeof result.hasMore).toBe("boolean");
      }),
  );

  it.effect("POST /traces/search - with query filter", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.traces.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          query: "test",
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect("POST /traces/search - with model filter", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.traces.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          model: ["gpt-4"],
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect("POST /traces/search - with provider filter", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.traces.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          provider: ["openai"],
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect("POST /traces/search - with pagination", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.traces.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          limit: 10,
          offset: 0,
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect("POST /traces/search - with sorting", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.traces.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          sortBy: "duration_ms",
          sortOrder: "desc",
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect(
    "searchHandler supports optional filters and maps attributeFilters",
    () =>
      Effect.gen(function* () {
        const settings = getSettings();
        const settingsLayer = Layer.succeed(SettingsService, {
          ...settings,
          env: "test",
        });

        if (!apiKeyInfo || !ownerFromContext) {
          throw new Error("Missing API key context for search handler test");
        }

        const authenticationLayer = Layer.succeed(Authentication, {
          user: ownerFromContext,
          apiKeyInfo,
        });

        const clickHouseSearchLayer = ClickHouseSearch.Default.pipe(
          Layer.provide(ClickHouse.Default),
          Layer.provide(settingsLayer),
        );

        const result = yield* searchHandler({
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          attributeFilters: [
            {
              key: "span.type",
              operator: "eq",
              value: "server",
            },
          ],
        }).pipe(
          Effect.provide(
            Layer.mergeAll(authenticationLayer, clickHouseSearchLayer),
          ),
        );

        expect(result.spans).toBeDefined();
        expect(typeof result.total).toBe("number");
      }),
  );

  it.effect("GET /traces/:traceId - returns empty for non-existent trace", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.traces.getTraceDetail({
        path: { traceId: "00000000-0000-0000-0000-000000000000" },
      });

      expect(result.traceId).toBe("00000000-0000-0000-0000-000000000000");
      expect(result.spans).toEqual([]);
    }),
  );

  it.effect("GET /traces/analytics - returns analytics summary", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.traces.getAnalyticsSummary({
        urlParams: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
        },
      });

      expect(typeof result.totalSpans).toBe("number");
      expect(typeof result.errorRate).toBe("number");
      expect(typeof result.totalTokens).toBe("number");
      expect(typeof result.totalCostUsd).toBe("number");
      expect(Array.isArray(result.topModels)).toBe(true);
      expect(Array.isArray(result.topFunctions)).toBe(true);
    }),
  );

  it.effect("GET /traces/analytics - with functionId filter", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.traces.getAnalyticsSummary({
        urlParams: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          functionId: "00000000-0000-0000-0000-000000000001",
        },
      });

      expect(typeof result.totalSpans).toBe("number");
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

describe("Search schema definitions", () => {
  describe("SearchRequest", () => {
    it("accepts valid search request with required fields", () => {
      const input: SearchRequest = {
        startTime: "2024-01-01T00:00:00Z",
        endTime: "2024-01-31T23:59:59Z",
      };

      expect(input.startTime).toBe("2024-01-01T00:00:00Z");
      expect(input.endTime).toBe("2024-01-31T23:59:59Z");
    });

    it("accepts search request with optional filters", () => {
      const input: SearchRequest = {
        startTime: "2024-01-01T00:00:00Z",
        endTime: "2024-01-31T23:59:59Z",
        query: "llm call",
        model: ["gpt-4", "gpt-3.5-turbo"],
        provider: ["openai"],
        hasError: false,
        limit: 100,
        offset: 0,
        sortBy: "start_time",
        sortOrder: "desc",
      };

      expect(input.query).toBe("llm call");
      expect(input.model).toHaveLength(2);
      expect(input.provider).toHaveLength(1);
      expect(input.limit).toBe(100);
    });

    it("accepts search request with attribute filters", () => {
      const input: SearchRequest = {
        startTime: "2024-01-01T00:00:00Z",
        endTime: "2024-01-31T23:59:59Z",
        attributeFilters: [
          { key: "gen_ai.request.model", operator: "eq", value: "gpt-4" },
          { key: "custom.tag", operator: "exists" },
        ],
      };

      expect(input.attributeFilters).toHaveLength(2);
      expect(input.attributeFilters?.[0]?.operator).toBe("eq");
      expect(input.attributeFilters?.[1]?.operator).toBe("exists");
    });

    it("accepts search request with message query filters", () => {
      const input: SearchRequest = {
        startTime: "2024-01-01T00:00:00Z",
        endTime: "2024-01-31T23:59:59Z",
        inputMessagesQuery: "hello world",
        outputMessagesQuery: "response text",
        fuzzySearch: true,
      };

      expect(input.inputMessagesQuery).toBe("hello world");
      expect(input.outputMessagesQuery).toBe("response text");
      expect(input.fuzzySearch).toBe(true);
    });

    it("accepts search request with fuzzySearch disabled", () => {
      const input: SearchRequest = {
        startTime: "2024-01-01T00:00:00Z",
        endTime: "2024-01-31T23:59:59Z",
        inputMessagesQuery: "programming",
        fuzzySearch: false,
      };

      expect(input.inputMessagesQuery).toBe("programming");
      expect(input.fuzzySearch).toBe(false);
    });

    it("accepts all valid sortBy values", () => {
      const validSortByValues: SearchRequest["sortBy"][] = [
        "start_time",
        "duration_ms",
        "total_tokens",
      ];

      for (const sortBy of validSortByValues) {
        const input: SearchRequest = {
          startTime: "2024-01-01T00:00:00Z",
          endTime: "2024-01-31T23:59:59Z",
          sortBy,
        };
        expect(input.sortBy).toBe(sortBy);
      }
    });

    it("accepts all valid sortOrder values", () => {
      const validSortOrderValues: SearchRequest["sortOrder"][] = [
        "asc",
        "desc",
      ];

      for (const sortOrder of validSortOrderValues) {
        const input: SearchRequest = {
          startTime: "2024-01-01T00:00:00Z",
          endTime: "2024-01-31T23:59:59Z",
          sortOrder,
        };
        expect(input.sortOrder).toBe(sortOrder);
      }
    });
  });

  describe("SearchResponse", () => {
    it("validates response structure", () => {
      const response: SearchResponse = {
        spans: [
          {
            id: "span-id-1",
            traceId: "trace-id-1",
            spanId: "otel-span-id-1",
            name: "llm.call",
            startTime: "2024-01-15T10:00:00Z",
            durationMs: 1500,
            model: "gpt-4",
            provider: "openai",
            totalTokens: 150,
            functionId: "00000000-0000-0000-0000-000000000001",
            functionName: "my_function",
          },
        ],
        total: 1,
        hasMore: false,
      };

      expect(response.spans).toHaveLength(1);
      expect(response.spans[0]?.name).toBe("llm.call");
      expect(response.total).toBe(1);
      expect(response.hasMore).toBe(false);
    });

    it("allows null values for optional span fields", () => {
      const response: SearchResponse = {
        spans: [
          {
            id: "span-id-1",
            traceId: "trace-id-1",
            spanId: "otel-span-id-1",
            name: "http.request",
            startTime: "2024-01-15T10:00:00Z",
            durationMs: null,
            model: null,
            provider: null,
            totalTokens: null,
            functionId: null,
            functionName: null,
          },
        ],
        total: 1,
        hasMore: false,
      };

      expect(response.spans[0]?.durationMs).toBeNull();
      expect(response.spans[0]?.model).toBeNull();
    });
  });

  describe("TraceDetailResponse", () => {
    it("validates trace detail response structure", () => {
      const response: TraceDetailResponse = {
        traceId: "trace-id-1",
        spans: [
          {
            id: "span-id-1",
            traceDbId: "trace-db-id-1",
            traceId: "trace-id-1",
            spanId: "otel-span-id-1",
            parentSpanId: null,
            environmentId: "env-id-1",
            projectId: "project-id-1",
            organizationId: "org-id-1",
            startTime: "2024-01-15T10:00:00Z",
            endTime: "2024-01-15T10:00:01Z",
            durationMs: 1000,
            name: "root.span",
            kind: 1,
            statusCode: 0,
            statusMessage: null,
            model: "gpt-4",
            provider: "openai",
            inputTokens: 100,
            outputTokens: 50,
            totalTokens: 150,
            costUsd: 0.01,
            functionId: null,
            functionName: null,
            functionVersion: null,
            errorType: null,
            errorMessage: null,
            attributes: "{}",
            events: null,
            links: null,
            serviceName: "my-service",
            serviceVersion: "1.0.0",
            resourceAttributes: null,
          },
        ],
        rootSpanId: "otel-span-id-1",
        totalDurationMs: 1000,
      };

      expect(response.traceId).toBe("trace-id-1");
      expect(response.spans).toHaveLength(1);
      expect(response.rootSpanId).toBe("otel-span-id-1");
      expect(response.totalDurationMs).toBe(1000);
    });

    it("allows null rootSpanId and totalDurationMs for empty traces", () => {
      const response: TraceDetailResponse = {
        traceId: "non-existent-trace",
        spans: [],
        rootSpanId: null,
        totalDurationMs: null,
      };

      expect(response.spans).toHaveLength(0);
      expect(response.rootSpanId).toBeNull();
      expect(response.totalDurationMs).toBeNull();
    });
  });

  describe("AnalyticsSummaryResponse", () => {
    it("validates analytics summary response structure", () => {
      const response: AnalyticsSummaryResponse = {
        totalSpans: 1000,
        avgDurationMs: 500.5,
        p50DurationMs: 400,
        p95DurationMs: 1200,
        p99DurationMs: 2000,
        errorRate: 0.05,
        totalTokens: 150000,
        totalCostUsd: 15.5,
        topModels: [
          { model: "gpt-4", count: 600 },
          { model: "gpt-3.5-turbo", count: 400 },
        ],
        topFunctions: [
          { functionName: "my_function", count: 200 },
          { functionName: "another_function", count: 100 },
        ],
      };

      expect(response.totalSpans).toBe(1000);
      expect(response.avgDurationMs).toBe(500.5);
      expect(response.topModels).toHaveLength(2);
      expect(response.topFunctions).toHaveLength(2);
    });

    it("allows empty arrays for topModels and topFunctions", () => {
      const response: AnalyticsSummaryResponse = {
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
      };

      expect(response.topModels).toHaveLength(0);
      expect(response.topFunctions).toHaveLength(0);
    });
  });
});

// =============================================================================
// Realtime merge tests
// =============================================================================

describe("Realtime span merge", () => {
  const createMockSpan = (
    overrides: Partial<SearchResponse["spans"][number]> = {},
  ): SearchResponse["spans"][number] => ({
    id: "span-1",
    traceId: "trace-1",
    spanId: "span-1",
    name: "test-span",
    startTime: new Date().toISOString(),
    durationMs: 100,
    model: "gpt-4",
    provider: "openai",
    totalTokens: 50,
    functionId: null,
    functionName: null,
    ...overrides,
  });

  const createMockTraceSpan = (
    overrides: Partial<TraceDetailResponse["spans"][number]> = {},
  ): TraceDetailResponse["spans"][number] => ({
    id: "span-1",
    traceDbId: "trace-db-1",
    traceId: "trace-1",
    spanId: "span-1",
    parentSpanId: null,
    environmentId: "env-1",
    projectId: "proj-1",
    organizationId: "org-1",
    startTime: new Date().toISOString(),
    endTime: new Date(Date.now() + 100).toISOString(),
    durationMs: 100,
    name: "test-span",
    kind: 1,
    statusCode: 0,
    statusMessage: null,
    model: "gpt-4",
    provider: "openai",
    inputTokens: 25,
    outputTokens: 25,
    totalTokens: 50,
    costUsd: 0.01,
    functionId: null,
    functionName: null,
    functionVersion: null,
    errorType: null,
    errorMessage: null,
    attributes: "{}",
    events: null,
    links: null,
    serviceName: "test-service",
    serviceVersion: "1.0.0",
    resourceAttributes: null,
    ...overrides,
  });

  const mockApiKeyInfo: ApiKeyInfo = {
    apiKeyId: "test-api-key",
    organizationId: "org-1",
    projectId: "proj-1",
    environmentId: "env-1",
    ownerId: "user-1",
    ownerEmail: "test@example.com",
    ownerName: "Test User",
    ownerDeletedAt: null,
  };

  const mockUser: PublicUser = {
    id: "user-1",
    email: "test@example.com",
    name: "Test User",
    deletedAt: null,
  };

  const authenticationLayer = Layer.succeed(Authentication, {
    user: mockUser,
    apiKeyInfo: mockApiKeyInfo,
  });

  const createClickHouseSearchLayer = (
    searchResult: SearchResponse,
    traceDetailResult?: TraceDetailResponse,
  ) =>
    Layer.succeed(ClickHouseSearch, {
      search: () =>
        Effect.succeed({
          spans: [...searchResult.spans],
          total: searchResult.total,
          hasMore: searchResult.hasMore,
        }),
      getTraceDetail: () =>
        Effect.succeed({
          traceId: traceDetailResult?.traceId ?? "trace-1",
          spans: [...(traceDetailResult?.spans ?? [])],
          rootSpanId: traceDetailResult?.rootSpanId ?? null,
          totalDurationMs: traceDetailResult?.totalDurationMs ?? null,
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

  const createRealtimeLayer = (
    searchResult: SearchResponse | null,
    traceDetailResult?: TraceDetailResponse | null,
  ) =>
    Layer.succeed(RealtimeSpans, {
      upsert: () => Effect.succeed(undefined),
      search: () =>
        searchResult
          ? Effect.succeed({
              spans: [...searchResult.spans],
              total: searchResult.total,
              hasMore: searchResult.hasMore,
            })
          : Effect.fail(new Error("No realtime data")),
      getTraceDetail: () =>
        traceDetailResult
          ? Effect.succeed({
              traceId: traceDetailResult.traceId,
              spans: [...traceDetailResult.spans],
              rootSpanId: traceDetailResult.rootSpanId,
              totalDurationMs: traceDetailResult.totalDurationMs,
            })
          : Effect.fail(new Error("No realtime data")),
      exists: () => Effect.succeed(false),
    });

  describe("searchHandler with realtime merge", () => {
    it.effect(
      "merges realtime spans with ClickHouse results for first page",
      () =>
        Effect.gen(function* () {
          const now = new Date();
          const clickhouseSpan = createMockSpan({
            id: "ch-span-1",
            spanId: "ch-span-1",
            traceId: "trace-1",
            name: "clickhouse-span",
          });
          const realtimeSpan = createMockSpan({
            id: "rt-span-1",
            spanId: "rt-span-1",
            traceId: "trace-2",
            name: "realtime-span",
          });

          const clickhouseResult: SearchResponse = {
            spans: [clickhouseSpan],
            total: 1,
            hasMore: false,
          };
          const realtimeResult: SearchResponse = {
            spans: [realtimeSpan],
            total: 1,
            hasMore: false,
          };

          const result = yield* searchHandler({
            startTime: new Date(now.getTime() - 5 * 60 * 1000).toISOString(),
            endTime: now.toISOString(),
          }).pipe(
            Effect.provide(
              Layer.mergeAll(
                authenticationLayer,
                createClickHouseSearchLayer(clickhouseResult),
                createRealtimeLayer(realtimeResult),
              ),
            ),
          );

          expect(result.spans).toHaveLength(2);
          expect(result.total).toBe(2);
        }),
    );

    it.effect("skips realtime merge for paginated requests (offset > 0)", () =>
      Effect.gen(function* () {
        const now = new Date();
        const clickhouseSpan = createMockSpan({
          id: "ch-span-1",
          spanId: "ch-span-1",
        });

        const clickhouseResult: SearchResponse = {
          spans: [clickhouseSpan],
          total: 10,
          hasMore: true,
        };
        const realtimeResult: SearchResponse = {
          spans: [createMockSpan({ id: "rt-span-1", spanId: "rt-span-1" })],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now.getTime() - 5 * 60 * 1000).toISOString(),
          endTime: now.toISOString(),
          offset: 10,
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        // Should only have ClickHouse results since offset > 0
        expect(result.spans).toHaveLength(1);
        expect(result.spans[0]?.id).toBe("ch-span-1");
      }),
    );

    it.effect("deduplicates spans with same traceId+spanId", () =>
      Effect.gen(function* () {
        const now = new Date();
        const duplicateSpan = createMockSpan({
          id: "span-1",
          spanId: "same-span-id",
          traceId: "same-trace-id",
          name: "clickhouse-version",
        });
        const realtimeSpan = createMockSpan({
          id: "span-2",
          spanId: "same-span-id",
          traceId: "same-trace-id",
          name: "realtime-version",
        });

        const clickhouseResult: SearchResponse = {
          spans: [duplicateSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [realtimeSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now.getTime() - 5 * 60 * 1000).toISOString(),
          endTime: now.toISOString(),
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        // ClickHouse takes precedence for duplicates
        expect(result.spans).toHaveLength(1);
        expect(result.spans[0]?.name).toBe("clickhouse-version");
      }),
    );

    it.effect("continues when realtime service fails", () =>
      Effect.gen(function* () {
        const now = new Date();
        const clickhouseSpan = createMockSpan({ id: "ch-span-1" });

        const clickhouseResult: SearchResponse = {
          spans: [clickhouseSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now.getTime() - 5 * 60 * 1000).toISOString(),
          endTime: now.toISOString(),
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(null),
            ),
          ),
        );

        expect(result.spans).toHaveLength(1);
        expect(result.spans[0]?.id).toBe("ch-span-1");
      }),
    );

    it.effect("skips realtime for queries outside TTL window", () =>
      Effect.gen(function* () {
        // Query for data from 2 days ago (outside 10-minute TTL)
        const oldDate = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000);
        const clickhouseSpan = createMockSpan({ id: "ch-span-1" });

        const clickhouseResult: SearchResponse = {
          spans: [clickhouseSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [createMockSpan({ id: "rt-span-1" })],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: oldDate.toISOString(),
          endTime: new Date(oldDate.getTime() + 60 * 1000).toISOString(),
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        // Should only have ClickHouse results since query is outside TTL
        expect(result.spans).toHaveLength(1);
        expect(result.spans[0]?.id).toBe("ch-span-1");
      }),
    );

    it.effect("sorts merged results by start_time descending", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const olderSpan = createMockSpan({
          id: "older",
          spanId: "older",
          startTime: new Date(now - 5000).toISOString(),
        });
        const newerSpan = createMockSpan({
          id: "newer",
          spanId: "newer",
          startTime: new Date(now).toISOString(),
        });

        const clickhouseResult: SearchResponse = {
          spans: [olderSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [newerSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          sortBy: "start_time",
          sortOrder: "desc",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        expect(result.spans[0]?.id).toBe("newer");
        expect(result.spans[1]?.id).toBe("older");
      }),
    );

    it.effect("sorts merged results by duration_ms", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const shortSpan = createMockSpan({
          id: "short",
          spanId: "short",
          durationMs: 100,
        });
        const longSpan = createMockSpan({
          id: "long",
          spanId: "long",
          durationMs: 500,
        });

        const clickhouseResult: SearchResponse = {
          spans: [longSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [shortSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          sortBy: "duration_ms",
          sortOrder: "asc",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        expect(result.spans[0]?.id).toBe("short");
        expect(result.spans[1]?.id).toBe("long");
      }),
    );

    it.effect("handles null duration values in sorting", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const nullDurationSpan = createMockSpan({
          id: "null-dur",
          spanId: "null-dur",
          durationMs: null,
        });
        const validDurationSpan = createMockSpan({
          id: "valid-dur",
          spanId: "valid-dur",
          durationMs: 100,
        });

        const clickhouseResult: SearchResponse = {
          spans: [nullDurationSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [validDurationSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          sortBy: "duration_ms",
          sortOrder: "asc",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        // Null values should be at the end for asc
        expect(result.spans[0]?.id).toBe("valid-dur");
        expect(result.spans[1]?.id).toBe("null-dur");
      }),
    );

    it.effect("sorts by total_tokens", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const lowTokenSpan = createMockSpan({
          id: "low",
          spanId: "low",
          totalTokens: 10,
        });
        const highTokenSpan = createMockSpan({
          id: "high",
          spanId: "high",
          totalTokens: 100,
        });

        const clickhouseResult: SearchResponse = {
          spans: [highTokenSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [lowTokenSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          sortBy: "total_tokens",
          sortOrder: "desc",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        expect(result.spans[0]?.id).toBe("high");
        expect(result.spans[1]?.id).toBe("low");
      }),
    );

    it.effect("applies limit after merge", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const spans = Array.from({ length: 10 }, (_, i) =>
          createMockSpan({
            id: `span-${i}`,
            spanId: `span-${i}`,
            startTime: new Date(now - i * 1000).toISOString(),
          }),
        );

        const clickhouseResult: SearchResponse = {
          spans: spans.slice(0, 5),
          total: 5,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: spans.slice(5),
          total: 5,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          limit: 3,
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(3);
      }),
    );

    it.effect("handles null duration values in desc sorting", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const nullDurationSpan = createMockSpan({
          id: "null-dur-desc",
          spanId: "null-dur-desc",
          durationMs: null,
        });
        const validDurationSpan = createMockSpan({
          id: "valid-dur-desc",
          spanId: "valid-dur-desc",
          durationMs: 100,
        });

        const clickhouseResult: SearchResponse = {
          spans: [nullDurationSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [validDurationSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          sortBy: "duration_ms",
          sortOrder: "desc",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        // Valid values first in desc, null values at end
        expect(result.spans[0]?.id).toBe("valid-dur-desc");
        expect(result.spans[1]?.id).toBe("null-dur-desc");
      }),
    );

    it.effect("sorts by total_tokens asc with null handling", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const nullTokenSpan = createMockSpan({
          id: "null-tok",
          spanId: "null-tok",
          totalTokens: null,
        });
        const validTokenSpan = createMockSpan({
          id: "valid-tok",
          spanId: "valid-tok",
          totalTokens: 50,
        });

        const clickhouseResult: SearchResponse = {
          spans: [nullTokenSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [validTokenSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          sortBy: "total_tokens",
          sortOrder: "asc",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        // Null values should be at the end for asc
        expect(result.spans[0]?.id).toBe("valid-tok");
        expect(result.spans[1]?.id).toBe("null-tok");
      }),
    );

    it.effect("handles null token values in desc sorting", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const nullTokenSpan = createMockSpan({
          id: "null-tok-desc",
          spanId: "null-tok-desc",
          totalTokens: null,
        });
        const validTokenSpan = createMockSpan({
          id: "valid-tok-desc",
          spanId: "valid-tok-desc",
          totalTokens: 50,
        });

        const clickhouseResult: SearchResponse = {
          spans: [nullTokenSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [validTokenSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          sortBy: "total_tokens",
          sortOrder: "desc",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        // Valid values first in desc, null values at end
        expect(result.spans[0]?.id).toBe("valid-tok-desc");
        expect(result.spans[1]?.id).toBe("null-tok-desc");
      }),
    );

    it.effect("sorts by start_time asc with invalid timestamp handling", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const invalidTimeSpan = createMockSpan({
          id: "invalid-time",
          spanId: "invalid-time",
          startTime: "invalid-timestamp",
        });
        const validTimeSpan = createMockSpan({
          id: "valid-time",
          spanId: "valid-time",
          startTime: new Date(now - 1000).toISOString(),
        });

        const clickhouseResult: SearchResponse = {
          spans: [invalidTimeSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [validTimeSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          sortBy: "start_time",
          sortOrder: "asc",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        // Invalid values should be at the end for asc
        expect(result.spans[0]?.id).toBe("valid-time");
        expect(result.spans[1]?.id).toBe("invalid-time");
      }),
    );

    it.effect("sorts by start_time desc with invalid timestamp handling", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const invalidTimeSpan = createMockSpan({
          id: "invalid-time-desc",
          spanId: "invalid-time-desc",
          startTime: "invalid-timestamp",
        });
        const validTimeSpan = createMockSpan({
          id: "valid-time-desc",
          spanId: "valid-time-desc",
          startTime: new Date(now - 1000).toISOString(),
        });

        const clickhouseResult: SearchResponse = {
          spans: [invalidTimeSpan],
          total: 1,
          hasMore: false,
        };
        const realtimeResult: SearchResponse = {
          spans: [validTimeSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
          sortBy: "start_time",
          sortOrder: "desc",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        // Valid values first in desc, invalid values at end
        expect(result.spans[0]?.id).toBe("valid-time-desc");
        expect(result.spans[1]?.id).toBe("invalid-time-desc");
      }),
    );

    it.effect("uses clickhouse total when hasMore is true", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const chSpan = createMockSpan({ id: "ch", spanId: "ch" });
        const rtSpan = createMockSpan({ id: "rt", spanId: "rt" });

        const clickhouseResult: SearchResponse = {
          spans: [chSpan],
          total: 100,
          hasMore: true,
        };
        const realtimeResult: SearchResponse = {
          spans: [rtSpan],
          total: 1,
          hasMore: false,
        };

        const result = yield* searchHandler({
          startTime: new Date(now - 5 * 60 * 1000).toISOString(),
          endTime: new Date(now).toISOString(),
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(clickhouseResult),
              createRealtimeLayer(realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        // Should use clickhouse total (100) since hasMore is true
        expect(result.total).toBe(100);
        expect(result.hasMore).toBe(true);
      }),
    );
  });

  describe("getTraceDetailHandler with realtime merge", () => {
    it.effect("merges realtime spans with ClickHouse trace details", () =>
      Effect.gen(function* () {
        const clickhouseSpan = createMockTraceSpan({
          id: "ch-span-1",
          spanId: "ch-span-1",
        });
        const realtimeSpan = createMockTraceSpan({
          id: "rt-span-1",
          spanId: "rt-span-1",
        });

        const clickhouseResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [clickhouseSpan],
          rootSpanId: "ch-span-1",
          totalDurationMs: 100,
        };
        const realtimeResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [realtimeSpan],
          rootSpanId: null,
          totalDurationMs: null,
        };

        const result = yield* getTraceDetailHandler("trace-1").pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(
                { spans: [], total: 0, hasMore: false },
                clickhouseResult,
              ),
              createRealtimeLayer(null, realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        expect(result.traceId).toBe("trace-1");
      }),
    );

    it.effect("deduplicates trace spans with same traceId+spanId", () =>
      Effect.gen(function* () {
        const clickhouseSpan = createMockTraceSpan({
          id: "ch-span-1",
          spanId: "same-span-id",
          traceId: "trace-1",
          name: "clickhouse-version",
        });
        const realtimeSpan = createMockTraceSpan({
          id: "rt-span-1",
          spanId: "same-span-id",
          traceId: "trace-1",
          name: "realtime-version",
        });

        const clickhouseResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [clickhouseSpan],
          rootSpanId: "same-span-id",
          totalDurationMs: 100,
        };
        const realtimeResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [realtimeSpan],
          rootSpanId: null,
          totalDurationMs: null,
        };

        const result = yield* getTraceDetailHandler("trace-1").pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(
                { spans: [], total: 0, hasMore: false },
                clickhouseResult,
              ),
              createRealtimeLayer(null, realtimeResult),
            ),
          ),
        );

        // ClickHouse takes precedence for duplicates
        expect(result.spans).toHaveLength(1);
        expect(result.spans[0]?.name).toBe("clickhouse-version");
      }),
    );

    it.effect("recalculates root span and duration after merge", () =>
      Effect.gen(function* () {
        const now = Date.now();
        const childSpan = createMockTraceSpan({
          id: "child",
          spanId: "child-span",
          parentSpanId: "root-span",
          startTime: new Date(now + 10).toISOString(),
          endTime: new Date(now + 50).toISOString(),
          durationMs: 40,
        });
        const rootSpan = createMockTraceSpan({
          id: "root",
          spanId: "root-span",
          parentSpanId: null,
          startTime: new Date(now).toISOString(),
          endTime: new Date(now + 100).toISOString(),
          durationMs: 100,
        });

        const clickhouseResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [childSpan],
          rootSpanId: null,
          totalDurationMs: 40,
        };
        const realtimeResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [rootSpan],
          rootSpanId: "root-span",
          totalDurationMs: 100,
        };

        const result = yield* getTraceDetailHandler("trace-1").pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(
                { spans: [], total: 0, hasMore: false },
                clickhouseResult,
              ),
              createRealtimeLayer(null, realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        expect(result.rootSpanId).toBe("root-span");
        expect(result.totalDurationMs).toBe(100);
      }),
    );

    it.effect("continues when realtime service fails for trace detail", () =>
      Effect.gen(function* () {
        const clickhouseSpan = createMockTraceSpan({ id: "ch-span-1" });

        const clickhouseResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [clickhouseSpan],
          rootSpanId: "ch-span-1",
          totalDurationMs: 100,
        };

        const result = yield* getTraceDetailHandler("trace-1").pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(
                { spans: [], total: 0, hasMore: false },
                clickhouseResult,
              ),
              createRealtimeLayer(null, null),
            ),
          ),
        );

        expect(result.spans).toHaveLength(1);
        expect(result.spans[0]?.id).toBe("ch-span-1");
      }),
    );

    it.effect("handles empty spans from both sources", () =>
      Effect.gen(function* () {
        const clickhouseResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [],
          rootSpanId: null,
          totalDurationMs: null,
        };
        const realtimeResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [],
          rootSpanId: null,
          totalDurationMs: null,
        };

        const result = yield* getTraceDetailHandler("trace-1").pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(
                { spans: [], total: 0, hasMore: false },
                clickhouseResult,
              ),
              createRealtimeLayer(null, realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(0);
        expect(result.rootSpanId).toBe(null);
        expect(result.totalDurationMs).toBe(null);
      }),
    );

    it.effect("handles spans with no root (all have parentSpanId)", () =>
      Effect.gen(function* () {
        const span1 = createMockTraceSpan({
          id: "span-1",
          spanId: "span-1",
          parentSpanId: "external-root",
          startTime: "2024-01-01T00:00:00.000Z",
          endTime: "2024-01-01T00:00:00.100Z",
        });
        const span2 = createMockTraceSpan({
          id: "span-2",
          spanId: "span-2",
          parentSpanId: "span-1",
          startTime: "2024-01-01T00:00:00.010Z",
          endTime: "2024-01-01T00:00:00.050Z",
        });

        const clickhouseResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [span1],
          rootSpanId: null,
          totalDurationMs: 100,
        };
        const realtimeResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [span2],
          rootSpanId: null,
          totalDurationMs: null,
        };

        const result = yield* getTraceDetailHandler("trace-1").pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(
                { spans: [], total: 0, hasMore: false },
                clickhouseResult,
              ),
              createRealtimeLayer(null, realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(2);
        expect(result.rootSpanId).toBe(null);
        expect(result.totalDurationMs).toBe(100);
      }),
    );

    it.effect("handles spans with invalid timestamps", () =>
      Effect.gen(function* () {
        const span1 = createMockTraceSpan({
          id: "span-1",
          spanId: "span-1",
          parentSpanId: null,
          startTime: "invalid-timestamp",
          endTime: "invalid-timestamp",
        });

        const clickhouseResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [span1],
          rootSpanId: "span-1",
          totalDurationMs: null,
        };
        const realtimeResult: TraceDetailResponse = {
          traceId: "trace-1",
          spans: [],
          rootSpanId: null,
          totalDurationMs: null,
        };

        const result = yield* getTraceDetailHandler("trace-1").pipe(
          Effect.provide(
            Layer.mergeAll(
              authenticationLayer,
              createClickHouseSearchLayer(
                { spans: [], total: 0, hasMore: false },
                clickhouseResult,
              ),
              createRealtimeLayer(null, realtimeResult),
            ),
          ),
        );

        expect(result.spans).toHaveLength(1);
        expect(result.rootSpanId).toBe("span-1");
        expect(result.totalDurationMs).toBe(null);
      }),
    );
  });
});
