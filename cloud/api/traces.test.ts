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
import { DrizzleORM } from "@/db/client";
import { SpansMeteringQueueService } from "@/workers/spansMeteringQueue";
import { createTraceHandler } from "@/api/traces.handlers";
import { Authentication } from "@/auth";
import { Database } from "@/db";
import { DatabaseError } from "@/errors";

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

describe("Traces Handler - Metering", () => {
  it.rollback("handles empty span IDs gracefully (no metering queued)", () =>
    Effect.gen(function* () {
      const db = yield* Database;

      // Create a real user in the database
      const user = yield* db.users.create({
        data: {
          email: "test-metering-empty@example.com",
          name: "Test User Metering Empty",
        },
      });

      // Create org, project, and environment for this test
      const org = yield* db.organizations.create({
        userId: user.id,
        data: { name: "Test Org", slug: "test-org-metering-empty" },
      });
      const proj = yield* db.organizations.projects.create({
        userId: user.id,
        organizationId: org.id,
        data: { name: "Test Project", slug: "test-proj-metering-empty" },
      });
      const env = yield* db.organizations.projects.environments.create({
        userId: user.id,
        organizationId: org.id,
        projectId: proj.id,
        data: { name: "Test Env", slug: "test-env-metering-empty" },
      });

      // Track if queue.send was called
      let sendCalled = false;
      const MockQueueLayer = Layer.succeed(SpansMeteringQueueService, {
        send: () => {
          sendCalled = true;
          return Effect.succeed(undefined);
        },
      });

      // Empty payload - no spans
      const payload = { resourceSpans: [] };

      const authLayer = Layer.succeed(Authentication, {
        user,
        apiKeyInfo: {
          apiKeyId: "test-key",
          organizationId: org.id,
          projectId: proj.id,
          environmentId: env.id,
          ownerId: user.id,
          ownerEmail: user.email,
          ownerName: user.name,
          ownerDeletedAt: user.deletedAt,
        },
      });

      const result = yield* createTraceHandler(payload).pipe(
        Effect.provide(authLayer),
        Effect.provide(MockQueueLayer),
      );

      // Should complete without error and not call queue
      expect(result.partialSuccess).toBeDefined();
      expect(sendCalled).toBe(false);
    }),
  );

  it.rollback(
    "handles database error when fetching organization (logs and continues)",
    () =>
      Effect.gen(function* () {
        const db = yield* Database;

        // Create a real user in the database
        const user = yield* db.users.create({
          data: {
            email: "test-metering-dberror@example.com",
            name: "Test User Metering DB Error",
          },
        });

        // Create org, project, and environment
        const org = yield* db.organizations.create({
          userId: user.id,
          data: { name: "Test Org 2", slug: "test-org-metering-dberror" },
        });
        const proj = yield* db.organizations.projects.create({
          userId: user.id,
          organizationId: org.id,
          data: { name: "Test Project 2", slug: "test-proj-metering-dberror" },
        });
        const env = yield* db.organizations.projects.environments.create({
          userId: user.id,
          organizationId: org.id,
          projectId: proj.id,
          data: { name: "Test Env 2", slug: "test-env-metering-dberror" },
        });

        // Mock DrizzleORM to throw error when selecting org
        const MockDrizzleLayer = Layer.succeed(DrizzleORM, {
          select: () => ({
            from: () => ({
              where: () =>
                Effect.fail(
                  new DatabaseError({
                    message: "Simulated database error",
                  }),
                ),
            }),
          }),
        } as never);

        const MockQueueLayer = Layer.succeed(SpansMeteringQueueService, {
          send: () => Effect.succeed(undefined),
        });

        const payload = {
          resourceSpans: [
            {
              scopeSpans: [
                {
                  spans: [
                    {
                      traceId: "trace-db-error",
                      spanId: "span-db-error",
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

        const authLayer = Layer.succeed(Authentication, {
          user,
          apiKeyInfo: {
            apiKeyId: "test-key-2",
            organizationId: org.id,
            projectId: proj.id,
            environmentId: env.id,
            ownerId: user.id,
            ownerEmail: user.email,
            ownerName: user.name,
            ownerDeletedAt: user.deletedAt,
          },
        });

        // Should complete without error despite DB error
        const result = yield* createTraceHandler(payload).pipe(
          Effect.provide(authLayer),
          Effect.provide(MockDrizzleLayer),
          Effect.provide(MockQueueLayer),
        );

        expect(result.partialSuccess).toBeDefined();
      }),
  );

  it.rollback("handles organization not found (logs and continues)", () =>
    Effect.gen(function* () {
      const db = yield* Database;

      // Create a real user in the database
      const user = yield* db.users.create({
        data: {
          email: "test-metering-notfound@example.com",
          name: "Test User Metering Not Found",
        },
      });

      // Create org, project, and environment
      const org = yield* db.organizations.create({
        userId: user.id,
        data: { name: "Test Org 3", slug: "test-org-metering-notfound" },
      });
      const proj = yield* db.organizations.projects.create({
        userId: user.id,
        organizationId: org.id,
        data: {
          name: "Test Project 3",
          slug: "test-proj-metering-notfound",
        },
      });
      const env = yield* db.organizations.projects.environments.create({
        userId: user.id,
        organizationId: org.id,
        projectId: proj.id,
        data: { name: "Test Env 3", slug: "test-env-metering-notfound" },
      });

      // Mock DrizzleORM to return empty result
      const MockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: () => ({
          from: () => ({
            where: () => Effect.succeed([]), // Empty array = org not found
          }),
        }),
      } as never);

      const MockQueueLayer = Layer.succeed(SpansMeteringQueueService, {
        send: () => Effect.succeed(undefined),
      });

      const payload = {
        resourceSpans: [
          {
            scopeSpans: [
              {
                spans: [
                  {
                    traceId: "trace-notfound",
                    spanId: "span-notfound",
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

      const authLayer = Layer.succeed(Authentication, {
        user,
        apiKeyInfo: {
          apiKeyId: "test-key",
          organizationId: org.id,
          projectId: proj.id,
          environmentId: env.id,
          ownerId: user.id,
          ownerEmail: user.email,
          ownerName: user.name,
          ownerDeletedAt: user.deletedAt,
        },
      });

      // Should complete without error despite org not found
      const result = yield* createTraceHandler(payload).pipe(
        Effect.provide(authLayer),
        Effect.provide(MockDrizzleLayer),
        Effect.provide(MockQueueLayer),
      );

      expect(result.partialSuccess).toBeDefined();
    }),
  );

  it.rollback("handles queue send error (logs and continues)", () =>
    Effect.gen(function* () {
      const db = yield* Database;

      // Create a real user in the database
      const user = yield* db.users.create({
        data: {
          email: "test-metering-queueerror@example.com",
          name: "Test User Metering Queue Error",
        },
      });

      // Create org, project, and environment
      const org = yield* db.organizations.create({
        userId: user.id,
        data: { name: "Test Org 4", slug: "test-org-metering-queueerror" },
      });
      const proj = yield* db.organizations.projects.create({
        userId: user.id,
        organizationId: org.id,
        data: {
          name: "Test Project 4",
          slug: "test-proj-metering-queueerror",
        },
      });
      const env = yield* db.organizations.projects.environments.create({
        userId: user.id,
        organizationId: org.id,
        projectId: proj.id,
        data: { name: "Test Env 4", slug: "test-env-metering-queueerror" },
      });

      // Mock queue to throw error
      const MockQueueLayer = Layer.succeed(SpansMeteringQueueService, {
        send: () => Effect.fail(new Error("Queue send failed")),
      });

      const payload = {
        resourceSpans: [
          {
            scopeSpans: [
              {
                spans: [
                  {
                    traceId: "trace-queue-error",
                    spanId: "span-queue-error",
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

      const authLayer = Layer.succeed(Authentication, {
        user,
        apiKeyInfo: {
          apiKeyId: "test-key-4",
          organizationId: org.id,
          projectId: proj.id,
          environmentId: env.id,
          ownerId: user.id,
          ownerEmail: user.email,
          ownerName: user.name,
          ownerDeletedAt: user.deletedAt,
        },
      });

      // Should complete without error despite queue error
      const result = yield* createTraceHandler(payload).pipe(
        Effect.provide(authLayer),
        Effect.provide(MockQueueLayer),
      );

      expect(result.partialSuccess).toBeDefined();
    }),
  );
});
