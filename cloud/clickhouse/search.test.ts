import { readFileSync } from "node:fs";
import {
  describe,
  it,
  expect,
  TestClickHouse,
  clickHouseAvailable,
} from "@/tests/clickhouse";
import { Effect, Layer } from "effect";
import { ClickHouse } from "@/clickhouse/client";
import { ClickHouseSearch } from "@/clickhouse/search";
import { beforeAll, afterAll } from "vitest";

// Test data IDs
const TEST_ENVIRONMENT_ID = "00000000-0000-0000-0000-000000000001";
const TEST_PROJECT_ID = "00000000-0000-0000-0000-000000000002";
const TEST_ORG_ID = "00000000-0000-0000-0000-000000000003";
const TEST_TRACE_ID = "abc123def456";
const TEST_SPAN_ID_1 = "span001";
const TEST_SPAN_ID_2 = "span002";

const CLICKHOUSE_DATABASE =
  process.env.CLICKHOUSE_DATABASE ?? "mirascope_analytics";

const MIGRATION_SQL = [
  readFileSync(
    new URL(
      "./migrations/00001_create_spans_analytics.up.sql",
      import.meta.url,
    ),
    "utf8",
  ),
  readFileSync(
    new URL("./migrations/00002_drop_span_db_ids.up.sql", import.meta.url),
    "utf8",
  ),
];

const renderMigrationSql = (database: string) =>
  MIGRATION_SQL.map((sql) => sql.replaceAll("{{database}}", database)).join(
    "\n",
  );

const splitStatements = (sql: string): string[] =>
  sql
    .split(";")
    .map((statement) => statement.trim())
    .filter((statement) => statement.length > 0);

const TestSearchLayer = ClickHouseSearch.Default.pipe(
  Layer.provide(TestClickHouse),
);

const provideSearchLayer = <A, E, R>(effect: Effect.Effect<A, E, R>) =>
  effect.pipe(Effect.provide(TestSearchLayer));

// Setup and teardown for test data
const setupSchema = Effect.gen(function* () {
  const client = yield* ClickHouse;
  const statements = splitStatements(renderMigrationSql(CLICKHOUSE_DATABASE));

  for (const statement of statements) {
    yield* client.command(statement);
  }

  const tables = yield* client.unsafeQuery<{ name: string }>(
    `SELECT name FROM system.tables
     WHERE database = {database:String}
       AND name IN ('spans_analytics', 'annotations_analytics')`,
    { database: CLICKHOUSE_DATABASE },
  );

  if (tables.length < 2) {
    throw new Error("ClickHouse test schema is missing required tables");
  }
});

const testSpans = [
  {
    trace_id: TEST_TRACE_ID,
    span_id: TEST_SPAN_ID_1,
    parent_span_id: null,
    environment_id: TEST_ENVIRONMENT_ID,
    project_id: TEST_PROJECT_ID,
    organization_id: TEST_ORG_ID,
    start_time: "2024-01-15 10:00:00.000000000",
    end_time: "2024-01-15 10:00:01.000000000",
    duration_ms: 1000,
    name: "llm call openai",
    kind: 1,
    status_code: 0,
    status_message: null,
    model: "gpt-4",
    provider: "openai",
    input_tokens: 100,
    output_tokens: 50,
    total_tokens: 150,
    cost_usd: 0.01,
    function_id: null,
    function_name: "my_function",
    function_version: "v1",
    error_type: null,
    error_message: null,
    attributes: JSON.stringify({
      "gen_ai.input_messages": "What is programming?",
      "gen_ai.output_messages": "Programming is the art of writing code.",
      "mirascope.trace.arg_values": '{"prompt": "Tell me about programming"}',
      "mirascope.trace.output": "Programming involves creating software.",
    }),
    events: null,
    links: null,
    service_name: "test-service",
    service_version: "1.0.0",
    resource_attributes: null,
    created_at: "2024-01-15 10:00:00.000",
    _version: Date.now(),
  },
  {
    trace_id: TEST_TRACE_ID,
    span_id: TEST_SPAN_ID_2,
    parent_span_id: TEST_SPAN_ID_1,
    environment_id: TEST_ENVIRONMENT_ID,
    project_id: TEST_PROJECT_ID,
    organization_id: TEST_ORG_ID,
    start_time: "2024-01-15 10:00:00.100000000",
    end_time: "2024-01-15 10:00:00.500000000",
    duration_ms: 400,
    name: "embedding call",
    kind: 1,
    status_code: 0,
    status_message: null,
    model: "text-embedding-3-small",
    provider: "openai",
    input_tokens: 50,
    output_tokens: 0,
    total_tokens: 50,
    cost_usd: 0.001,
    function_id: null,
    function_name: null,
    function_version: null,
    error_type: null,
    error_message: null,
    attributes: "{}",
    events: null,
    links: null,
    service_name: "test-service",
    service_version: "1.0.0",
    resource_attributes: null,
    created_at: "2024-01-15 10:00:00.100",
    _version: Date.now(),
  },
];

const setupTestData = Effect.gen(function* () {
  const client = yield* ClickHouse;
  yield* client.command(
    `TRUNCATE TABLE ${CLICKHOUSE_DATABASE}.spans_analytics`,
  );
  yield* client.insert("spans_analytics", testSpans);
});

const cleanupTestData = Effect.gen(function* () {
  const client = yield* ClickHouse;
  yield* client.command(
    `TRUNCATE TABLE ${CLICKHOUSE_DATABASE}.spans_analytics`,
  );
});

beforeAll(async () => {
  if (!clickHouseAvailable) return;
  try {
    await Effect.runPromise(
      Effect.gen(function* () {
        yield* setupSchema;
        yield* setupTestData;
      }).pipe(Effect.provide(TestClickHouse)),
    );
  } catch (error) {
    console.warn("ClickHouse test setup failed:", error);
    throw error;
  }
});

afterAll(async () => {
  if (!clickHouseAvailable) return;
  await Effect.runPromise(cleanupTestData.pipe(Effect.provide(TestClickHouse)));
});

describe("ClickHouseSearch", () => {
  describe("search", () => {
    it.effect("returns spans matching query", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          query: "llm",
        });

        expect(result.spans.length).toBeGreaterThan(0);
        expect(result.spans[0]?.name).toContain("llm");
      }).pipe(provideSearchLayer),
    );

    it.effect("returns empty array for non-matching query", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          query: "nonexistentqueryterm",
        });

        expect(result.spans).toHaveLength(0);
      }).pipe(provideSearchLayer),
    );

    it.effect("filters by model", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          model: ["gpt-4"],
        });

        expect(result.spans.length).toBeGreaterThan(0);
        for (const span of result.spans) {
          expect(span.model).toBe("gpt-4");
        }
      }).pipe(provideSearchLayer),
    );

    it.effect("filters by provider", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          provider: ["openai"],
        });

        expect(result.spans.length).toBeGreaterThan(0);
        for (const span of result.spans) {
          expect(span.provider).toBe("openai");
        }
      }).pipe(provideSearchLayer),
    );

    it.effect("respects limit and offset", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          limit: 1,
          offset: 0,
        });

        expect(result.spans.length).toBeLessThanOrEqual(1);
      }).pipe(provideSearchLayer),
    );

    it.effect("sorts by start_time descending by default", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
        });

        if (result.spans.length >= 2) {
          const first = new Date(result.spans[0].startTime).getTime();
          const second = new Date(result.spans[1].startTime).getTime();
          expect(first).toBeGreaterThanOrEqual(second);
        }
      }).pipe(provideSearchLayer),
    );

    it.effect("returns total count and hasMore", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          limit: 1,
        });

        expect(typeof result.total).toBe("number");
        expect(typeof result.hasMore).toBe("boolean");
      }).pipe(provideSearchLayer),
    );

    it.effect("filters by inputMessagesQuery using LIKE", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          inputMessagesQuery: "programming",
        });

        expect(result.spans.length).toBeGreaterThan(0);
      }).pipe(provideSearchLayer),
    );

    it.effect("filters by outputMessagesQuery using LIKE", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          outputMessagesQuery: "art of writing",
        });

        expect(result.spans.length).toBeGreaterThan(0);
      }).pipe(provideSearchLayer),
    );

    it.effect("returns empty for non-matching inputMessagesQuery", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          inputMessagesQuery: "nonexistentterm12345",
        });

        expect(result.spans).toHaveLength(0);
      }).pipe(provideSearchLayer),
    );

    it.effect("filters by inputMessagesQuery with fuzzySearch enabled", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        // "programing" (typo) should match "programming" with fuzzy search
        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          inputMessagesQuery: "programing",
          fuzzySearch: true,
        });

        expect(result.spans.length).toBeGreaterThan(0);
      }).pipe(provideSearchLayer),
    );

    it.effect(
      "fuzzySearch does not match without typo tolerance in LIKE mode",
      () =>
        Effect.gen(function* () {
          const searchService = yield* ClickHouseSearch;

          // "programing" (typo) should NOT match "programming" with LIKE (default)
          const result = yield* searchService.search({
            environmentId: TEST_ENVIRONMENT_ID,
            startTime: new Date("2024-01-01"),
            endTime: new Date("2024-01-31"),
            inputMessagesQuery: "programing",
            fuzzySearch: false,
          });

          expect(result.spans).toHaveLength(0);
        }).pipe(provideSearchLayer),
    );
  });

  describe("getTraceDetail", () => {
    it.effect("returns all spans for a trace", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.getTraceDetail({
          environmentId: TEST_ENVIRONMENT_ID,
          traceId: TEST_TRACE_ID,
        });

        expect(result.traceId).toBe(TEST_TRACE_ID);
        expect(result.spans.length).toBeGreaterThan(0);
      }).pipe(provideSearchLayer),
    );

    it.effect("identifies root span", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.getTraceDetail({
          environmentId: TEST_ENVIRONMENT_ID,
          traceId: TEST_TRACE_ID,
        });

        expect(result.rootSpanId).toBe(TEST_SPAN_ID_1);
      }).pipe(provideSearchLayer),
    );

    it.effect("calculates total duration", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.getTraceDetail({
          environmentId: TEST_ENVIRONMENT_ID,
          traceId: TEST_TRACE_ID,
        });

        expect(result.totalDurationMs).toBeGreaterThan(0);
      }).pipe(provideSearchLayer),
    );

    it.effect("returns empty for non-existent trace", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.getTraceDetail({
          environmentId: TEST_ENVIRONMENT_ID,
          traceId: "non-existent-trace-id",
        });

        expect(result.spans).toHaveLength(0);
        expect(result.rootSpanId).toBeNull();
        expect(result.totalDurationMs).toBeNull();
      }).pipe(provideSearchLayer),
    );
  });

  describe("getAnalyticsSummary", () => {
    it.effect("returns analytics summary", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.getAnalyticsSummary({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
        });

        expect(typeof result.totalSpans).toBe("number");
        expect(typeof result.errorRate).toBe("number");
        expect(typeof result.totalTokens).toBe("number");
        expect(Array.isArray(result.topModels)).toBe(true);
        expect(Array.isArray(result.topFunctions)).toBe(true);
      }).pipe(provideSearchLayer),
    );

    it.effect("returns top models", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.getAnalyticsSummary({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
        });

        if (result.topModels.length > 0) {
          expect(result.topModels[0]?.model).toBeDefined();
          expect(result.topModels[0]?.count).toBeGreaterThan(0);
        }
      }).pipe(provideSearchLayer),
    );
  });

  describe("validation", () => {
    it("throws on time range exceeding 30 days for search", async () => {
      const program = Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-03-01"), // 60 days
        });
      }).pipe(provideSearchLayer);

      await expect(Effect.runPromise(program)).rejects.toThrow(
        /Time range exceeds maximum/,
      );
    });

    it("throws on query exceeding max length", async () => {
      const longQuery = "a".repeat(501);

      const program = Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          query: longQuery,
        });
      }).pipe(provideSearchLayer);

      await expect(Effect.runPromise(program)).rejects.toThrow(
        /Query exceeds maximum length/,
      );
    });

    it("throws on offset exceeding max", async () => {
      const program = Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          offset: 10001,
        });
      }).pipe(provideSearchLayer);

      await expect(Effect.runPromise(program)).rejects.toThrow(
        /Offset exceeds maximum/,
      );
    });

    it("throws on too many attribute filters", async () => {
      const tooManyFilters = Array.from({ length: 11 }, (_, i) => ({
        key: `attr${i}`,
        operator: "eq" as const,
        value: "test",
      }));

      const program = Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          attributeFilters: tooManyFilters,
        });
      }).pipe(provideSearchLayer);

      await expect(Effect.runPromise(program)).rejects.toThrow(
        /Too many attribute filters/,
      );
    });

    it("throws on too many model values", async () => {
      const tooManyModels = Array.from({ length: 21 }, (_, i) => `model${i}`);

      const program = Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
          model: tooManyModels,
        });
      }).pipe(provideSearchLayer);

      await expect(Effect.runPromise(program)).rejects.toThrow(
        /Too many model values/,
      );
    });
  });

  describe("transformations", () => {
    it.effect("transforms snake_case to camelCase in search results", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.search({
          environmentId: TEST_ENVIRONMENT_ID,
          startTime: new Date("2024-01-01"),
          endTime: new Date("2024-01-31"),
        });

        if (result.spans.length > 0) {
          const span = result.spans[0];
          // Verify camelCase keys exist
          expect("traceId" in span).toBe(true);
          expect("spanId" in span).toBe(true);
          expect("startTime" in span).toBe(true);
          expect("durationMs" in span).toBe(true);
          expect("totalTokens" in span).toBe(true);
          expect("functionId" in span).toBe(true);
          expect("functionName" in span).toBe(true);
        }
      }).pipe(provideSearchLayer),
    );

    it.effect("transforms snake_case to camelCase in trace detail", () =>
      Effect.gen(function* () {
        const searchService = yield* ClickHouseSearch;

        const result = yield* searchService.getTraceDetail({
          environmentId: TEST_ENVIRONMENT_ID,
          traceId: TEST_TRACE_ID,
        });

        if (result.spans.length > 0) {
          const span = result.spans[0];
          // Verify camelCase keys exist
          expect("parentSpanId" in span).toBe(true);
          expect("environmentId" in span).toBe(true);
          expect("projectId" in span).toBe(true);
          expect("organizationId" in span).toBe(true);
          expect("statusCode" in span).toBe(true);
          expect("inputTokens" in span).toBe(true);
          expect("outputTokens" in span).toBe(true);
          expect("costUsd" in span).toBe(true);
          expect("errorType" in span).toBe(true);
          expect("serviceName" in span).toBe(true);
        }
      }).pipe(provideSearchLayer),
    );
  });
});
