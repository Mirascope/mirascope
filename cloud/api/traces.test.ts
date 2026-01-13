import { Effect } from "effect";
import {
  describe,
  expect,
  it,
  TestApiContext,
  createApiClient,
} from "@/tests/api";
import type { PublicProject, PublicEnvironment } from "@/db/schema";
import { TEST_DATABASE_URL } from "@/tests/db";
import { toTrace } from "@/api/traces.handlers";
import { ClickHouse } from "@/clickhouse/client";
import { TestClickHouse, clickHouseAvailable } from "@/tests/clickhouse";
import { afterAll } from "vitest";

const CLICKHOUSE_DATABASE =
  process.env.CLICKHOUSE_DATABASE ?? "mirascope_analytics";

const cleanupClickHouse = Effect.gen(function* () {
  const client = yield* ClickHouse;
  yield* client.command(
    `TRUNCATE TABLE ${CLICKHOUSE_DATABASE}.spans_analytics`,
  );
});

afterAll(async () => {
  if (!clickHouseAvailable) return;
  await Effect.runPromise(
    cleanupClickHouse.pipe(Effect.provide(TestClickHouse)),
  );
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

// Helper to build a ClickHouse span row with timestamps within 30-day search range
const buildClickHouseSpan = (params: {
  traceId: string;
  spanId: string;
  environmentId: string;
  projectId: string;
  organizationId: string;
  functionHash: string;
  offsetMinutes?: number;
}) => {
  // Use current time minus offset to ensure within 30-day search window
  const now = new Date();
  const startTimeDate = new Date(
    now.getTime() - (params.offsetMinutes ?? 5) * 60 * 1000,
  );
  const endTimeDate = new Date(startTimeDate.getTime() + 1000);

  const formatClickHouseTime = (date: Date) => {
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, "0");
    const day = String(date.getUTCDate()).padStart(2, "0");
    const hours = String(date.getUTCHours()).padStart(2, "0");
    const minutes = String(date.getUTCMinutes()).padStart(2, "0");
    const seconds = String(date.getUTCSeconds()).padStart(2, "0");
    const milliseconds = String(date.getUTCMilliseconds()).padStart(3, "0");
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${milliseconds}000000`;
  };

  const formatCreatedAt = (date: Date) => {
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, "0");
    const day = String(date.getUTCDate()).padStart(2, "0");
    const hours = String(date.getUTCHours()).padStart(2, "0");
    const minutes = String(date.getUTCMinutes()).padStart(2, "0");
    const seconds = String(date.getUTCSeconds()).padStart(2, "0");
    const milliseconds = String(date.getUTCMilliseconds()).padStart(3, "0");
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${milliseconds}`;
  };

  return {
    trace_id: params.traceId,
    span_id: params.spanId,
    parent_span_id: null,
    environment_id: params.environmentId,
    project_id: params.projectId,
    organization_id: params.organizationId,
    start_time: formatClickHouseTime(startTimeDate),
    end_time: formatClickHouseTime(endTimeDate),
    duration_ms: 1000,
    name: "test-span",
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
      "mirascope.version.hash": params.functionHash,
    }),
    events: null,
    links: null,
    service_name: "test-service",
    service_version: "1.0.0",
    resource_attributes: null,
    created_at: formatCreatedAt(startTimeDate),
    _version: Date.now(),
  };
};

describe.sequential("Traces API", (it) => {
  let orgId: string;
  let project: PublicProject;
  let environment: PublicEnvironment;
  let apiKeyClient: Awaited<ReturnType<typeof createApiClient>>["client"];
  let disposeApiKeyClient: (() => Promise<void>) | null = null;

  it.effect(
    "POST /organizations/:orgId/projects - create project for traces test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        orgId = org.id;
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
        createApiClient(TEST_DATABASE_URL, owner, apiKeyInfo),
      );
      apiKeyClient = result.client;
      disposeApiKeyClient = result.dispose;
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

  it.effect(
    "GET /traces/function/hash/:hash - returns traces by function hash",
    () =>
      Effect.gen(function* () {
        // Insert test span directly into ClickHouse
        const testSpan = buildClickHouseSpan({
          traceId: "trace-with-func-hash",
          spanId: "span-with-func-hash",
          environmentId: environment.id,
          projectId: project.id,
          organizationId: orgId,
          functionHash: "api-test-hash-123",
        });

        yield* Effect.promise(async () => {
          await Effect.runPromise(
            Effect.gen(function* () {
              const client = yield* ClickHouse;
              yield* client.insert("spans_analytics", [testSpan]);
            }).pipe(Effect.provide(TestClickHouse)),
          );
        });

        const result = yield* apiKeyClient.traces.listByFunctionHash({
          path: { hash: "api-test-hash-123" },
          urlParams: {},
        });

        expect(result.traces).toHaveLength(1);
        expect(result.traces[0]?.otelTraceId).toBe("trace-with-func-hash");
        expect(result.total).toBe(1);
      }),
  );

  it.effect(
    "GET /traces/function/hash/:hash - returns empty array for non-existent hash",
    () =>
      Effect.gen(function* () {
        const result = yield* apiKeyClient.traces.listByFunctionHash({
          path: { hash: "non-existent-hash" },
          urlParams: {},
        });

        expect(result.traces).toHaveLength(0);
        expect(result.total).toBe(0);
      }),
  );

  it.effect(
    "GET /traces/function/hash/:hash - supports pagination with limit and offset",
    () =>
      Effect.gen(function* () {
        // Insert 3 spans with same function hash into ClickHouse
        const testSpans = Array.from({ length: 3 }, (_unused, index) =>
          buildClickHouseSpan({
            traceId: `paginate-api-trace-${index + 1}`,
            spanId: `paginate-api-span-${index + 1}`,
            environmentId: environment.id,
            projectId: project.id,
            organizationId: orgId,
            functionHash: "paginate-api-hash",
            offsetMinutes: 10 + index,
          }),
        );

        yield* Effect.promise(async () => {
          await Effect.runPromise(
            Effect.gen(function* () {
              const client = yield* ClickHouse;
              yield* client.insert("spans_analytics", testSpans);
            }).pipe(Effect.provide(TestClickHouse)),
          );
        });

        const result = yield* apiKeyClient.traces.listByFunctionHash({
          path: { hash: "paginate-api-hash" },
          urlParams: { limit: 2, offset: 0 },
        });

        expect(result.traces).toHaveLength(2);
        expect(result.total).toBe(3);
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
