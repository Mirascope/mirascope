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
import {
  Settings,
  type SettingsConfig,
  type ClickHouseConfig,
} from "@/settings";
import { createMockSettings } from "@/tests/settings";
import { searchHandler } from "@/api/search.handlers";
import type {
  SearchRequest,
  SearchResponse,
  TraceDetailResponse,
  AnalyticsSummaryResponse,
} from "@/api/search.schemas";
import { CLICKHOUSE_CONNECTION_FILE } from "@/tests/global-setup";
import fs from "fs";

type ClickHouseConnectionFile = {
  url: string;
  user: string;
  password: string;
  database: string;
  nativePort: number;
};

function getTestClickHouseConfig(): ClickHouseConfig {
  try {
    const raw = fs.readFileSync(CLICKHOUSE_CONNECTION_FILE, "utf-8");
    const conn = JSON.parse(raw) as ClickHouseConnectionFile;
    return {
      url: conn.url,
      user: conn.user,
      password: conn.password,
      database: conn.database,
      tls: {
        enabled: false,
        ca: "",
        skipVerify: false,
        hostnameVerify: true,
        minVersion: "1.2",
      },
    };
  } catch {
    throw new Error(
      "TEST_CLICKHOUSE_URL not set. Ensure global-setup.ts ran successfully.",
    );
  }
}

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
        // Use real ClickHouse testcontainer credentials
        const clickhouseConfig = getTestClickHouseConfig();
        const mockSettings: SettingsConfig = createMockSettings({
          env: "test",
          clickhouse: clickhouseConfig,
        });
        const settingsLayer = Layer.succeed(Settings, mockSettings);

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
