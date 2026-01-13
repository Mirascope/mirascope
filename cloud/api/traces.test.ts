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

      const result = yield* apiKeyClient.traces.create({ payload });
      expect(result.partialSuccess?.rejectedSpans).toBe(1);
      expect(result.partialSuccess?.errorMessage).toContain("1 spans");
    }),
  );

  it.effect(
    "GET /traces/function/hash/:hash - returns traces by function hash",
    () =>
      Effect.gen(function* () {
        const payload = {
          resourceSpans: [
            {
              resource: {
                attributes: [
                  {
                    key: "service.name",
                    value: { stringValue: "hash-test-service" },
                  },
                ],
              },
              scopeSpans: [
                {
                  scope: { name: "test-scope", version: "1.0.0" },
                  spans: [
                    {
                      traceId: "trace-with-func-hash",
                      spanId: "span-with-func-hash",
                      name: "versioned-span",
                      startTimeUnixNano: "1000000000",
                      endTimeUnixNano: "2000000000",
                      attributes: [
                        {
                          key: "mirascope.version.hash",
                          value: { stringValue: "api-test-hash-123" },
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
        };

        yield* apiKeyClient.traces.create({ payload });

        const result = yield* apiKeyClient.traces.listByFunctionHash({
          path: { hash: "api-test-hash-123" },
          urlParams: {},
        });

        expect(result.traces).toHaveLength(1);
        expect(result.traces[0].otelTraceId).toBe("trace-with-func-hash");
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
        for (let i = 1; i <= 3; i++) {
          const payload = {
            resourceSpans: [
              {
                resource: { attributes: [] },
                scopeSpans: [
                  {
                    scope: { name: "test-scope", version: "1.0.0" },
                    spans: [
                      {
                        traceId: `paginate-api-trace-${i}`,
                        spanId: `paginate-api-span-${i}`,
                        name: "paginated-span",
                        startTimeUnixNano: `${1000000000 + i * 1000000}`,
                        endTimeUnixNano: `${2000000000 + i * 1000000}`,
                        attributes: [
                          {
                            key: "mirascope.version.hash",
                            value: { stringValue: "paginate-api-hash" },
                          },
                        ],
                      },
                    ],
                  },
                ],
              },
            ],
          };
          yield* apiKeyClient.traces.create({ payload });
        }

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
