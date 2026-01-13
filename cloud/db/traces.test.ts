import {
  describe,
  it,
  expect,
  TestEnvironmentFixture,
  TestDrizzleORM,
} from "@/tests/db";
import { Effect, Layer, Option } from "effect";
import { Database } from "@/db";
import {
  NotFoundError,
  PermissionDeniedError,
  ImmutableResourceError,
} from "@/errors";
import {
  SpansIngestQueueService,
  type SpansIngestMessage,
} from "@/workers/spanIngestQueue";
import { vi, afterAll } from "vitest";
import { createCustomIt } from "@/tests/shared";
import { DefaultMockPayments } from "@/tests/payments";
import { DrizzleORM } from "@/db/client";
import { SqlClient } from "@effect/sql";
import { ClickHouse } from "@/clickhouse/client";
import { TestClickHouse, clickHouseAvailable } from "@/tests/clickhouse";

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

type QueueSend = (message: SpansIngestMessage) => Effect.Effect<void, Error>;

const createQueueLayer = (
  send: QueueSend = vi.fn<QueueSend>().mockReturnValue(Effect.void),
) => Layer.succeed(SpansIngestQueueService, { send });

const TestDatabaseNoQueue = Database.Default.pipe(
  Layer.provideMerge(TestDrizzleORM),
  Layer.provide(DefaultMockPayments),
);

class TestRollbackError {
  readonly _tag = "TestRollbackError";
}

const withRollback = <A, E, R>(
  effect: Effect.Effect<A, E, R>,
): Effect.Effect<A, E, R> =>
  Effect.gen(function* () {
    const sqlOption = yield* Effect.serviceOption(SqlClient.SqlClient);

    if (Option.isNone(sqlOption)) {
      return yield* effect;
    }

    const sql = sqlOption.value;
    let result: A;

    yield* sql
      .withTransaction(
        Effect.gen(function* () {
          result = yield* effect;
          return yield* Effect.fail(new TestRollbackError());
        }),
      )
      .pipe(
        Effect.catchIf(
          (e): e is TestRollbackError => e instanceof TestRollbackError,
          () => Effect.void,
        ),
      );

    // @ts-expect-error - result is assigned before we get here
    return result;
  }) as Effect.Effect<A, E, R>;

const itNoQueue = createCustomIt<Database | DrizzleORM | SqlClient.SqlClient>(
  (original) => (name, fn, timeout) =>
    // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
    original(
      name,
      () => fn().pipe(withRollback).pipe(Effect.provide(TestDatabaseNoQueue)),
      timeout,
    ),
);

const buildSpan = (index: number) => ({
  traceId: "trace-1",
  spanId: `span-${index}`,
  name: `span-${index}`,
  startTimeUnixNano: "1000000000",
  endTimeUnixNano: "2000000000",
});

describe("Traces", () => {
  describe("create", () => {
    itNoQueue.effect("enqueues spans and converts OTLP values", () => {
      const sentMessages: SpansIngestMessage[] = [];
      const send = vi.fn<QueueSend>((message: SpansIngestMessage) => {
        sentMessages.push(message);
        return Effect.void;
      });

      return Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test-service" } },
                {
                  key: "service.version",
                  value: { stringValue: "1.0.0" },
                },
                { key: "int-attr", value: { intValue: "42" } },
                { key: "double-attr", value: { doubleValue: 3.14 } },
                { key: "bool-attr", value: { boolValue: true } },
                {
                  key: "array-attr",
                  value: {
                    arrayValue: {
                      values: [
                        { stringValue: "item1" },
                        { intValue: "123" },
                        "raw-string-value" as unknown as {
                          stringValue: string;
                        },
                      ],
                    },
                  },
                },
                {
                  key: "kvlist-attr",
                  value: {
                    kvlistValue: {
                      values: [
                        { key: "nested", value: { stringValue: "value" } },
                        { key: "raw", value: "direct-value" },
                      ],
                    },
                  },
                },
                { key: "unknown-attr", value: {} },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "abc123",
                    spanId: "span001",
                    name: "test-span",
                    startTimeUnixNano: "1234567890000000000",
                    endTimeUnixNano: "1234567891000000000",
                    events: [{ name: "event-1" }],
                    links: [{ traceId: "link-trace", spanId: "link-span" }],
                  },
                  {
                    traceId: "abc123",
                    spanId: "span002",
                    name: "empty-start",
                    startTimeUnixNano: "",
                    endTimeUnixNano: "",
                  },
                ],
              },
            ],
          },
        ];

        const result =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          });

        expect(result.acceptedSpans).toBe(2);
        expect(result.rejectedSpans).toBe(0);
        expect(sentMessages).toHaveLength(1);
        const message = sentMessages[0];
        if (!message) {
          throw new Error("Expected spans ingest message");
        }
        expect(message.serviceName).toBe("test-service");
        expect(message.serviceVersion).toBe("1.0.0");
        expect(message.resourceAttributes).toEqual({
          "service.name": "test-service",
          "service.version": "1.0.0",
          "int-attr": "42",
          "double-attr": 3.14,
          "bool-attr": true,
          "array-attr": ["item1", "123", "raw-string-value"],
          "kvlist-attr": { nested: "value", raw: "direct-value" },
          "unknown-attr": null,
        });
        expect(message.spans[0]?.events).toEqual([{ name: "event-1" }]);
        expect(message.spans[0]?.links).toEqual([
          { traceId: "link-trace", spanId: "link-span" },
        ]);
        expect(message.spans[1]?.startTimeUnixNano).toBeUndefined();
      }).pipe(Effect.provide(createQueueLayer(send)));
    });

    itNoQueue.effect("splits spans into 50-span batches", () => {
      const sentMessages: SpansIngestMessage[] = [];
      const send = vi.fn<QueueSend>((message: SpansIngestMessage) => {
        sentMessages.push(message);
        return Effect.void;
      });

      return Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const spans = Array.from({ length: 101 }, (_, index) =>
          buildSpan(index),
        );

        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [{ scope: { name: "test" }, spans }],
          },
        ];

        const result =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          });

        expect(result.acceptedSpans).toBe(101);
        expect(result.rejectedSpans).toBe(0);
        expect(sentMessages).toHaveLength(3);
        expect(sentMessages[0]?.spans).toHaveLength(50);
        expect(sentMessages[1]?.spans).toHaveLength(50);
        expect(sentMessages[2]?.spans).toHaveLength(1);
      }).pipe(Effect.provide(createQueueLayer(send)));
    });

    itNoQueue.effect("rejects spans when queue binding is missing", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-missing-queue",
                    spanId: "span-missing-queue",
                    name: "queue-missing-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        const result =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          });

        expect(result.acceptedSpans).toBe(0);
        expect(result.rejectedSpans).toBe(1);
      }),
    );
    itNoQueue.effect("rejects spans when enqueue fails", () => {
      const send = vi
        .fn()
        .mockReturnValue(Effect.fail(new Error("Queue down")));

      return Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [
              {
                scope: { name: "test" },
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
        ];

        const result =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          });

        expect(result.rejectedSpans).toBe(1);
        expect(result.acceptedSpans).toBe(0);
      }).pipe(Effect.provide(createQueueLayer(send)));
    });

    itNoQueue.effect("handles empty resourceSpans", () => {
      const send = vi.fn<QueueSend>().mockReturnValue(Effect.void);

      return Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans: [] },
          });

        expect(result.acceptedSpans).toBe(0);
        expect(result.rejectedSpans).toBe(0);
        expect(send).not.toHaveBeenCalled();
      }).pipe(Effect.provide(createQueueLayer(send)));
    });

    itNoQueue.effect("skips resources with no spans", () => {
      const send = vi.fn().mockReturnValue(Effect.void);

      return Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: {
              resourceSpans: [
                {
                  resource: { attributes: [] },
                  scopeSpans: [{ scope: { name: "test" }, spans: [] }],
                },
              ],
            },
          });

        expect(result.acceptedSpans).toBe(0);
        expect(result.rejectedSpans).toBe(0);
        expect(send).not.toHaveBeenCalled();
      }).pipe(Effect.provide(createQueueLayer(send)));
    });

    itNoQueue.effect("normalizes empty timestamp strings to undefined", () => {
      const sentMessages: SpansIngestMessage[] = [];
      const send = vi.fn<QueueSend>((message: SpansIngestMessage) => {
        sentMessages.push(message);
        return Effect.void;
      });

      return Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        yield* db.organizations.projects.environments.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: {
            resourceSpans: [
              {
                resource: { attributes: [] },
                scopeSpans: [
                  {
                    scope: { name: "test" },
                    spans: [
                      {
                        traceId: "trace-empty-ts",
                        spanId: "span-empty-ts",
                        name: "test-span",
                        startTimeUnixNano: "   ",
                        endTimeUnixNano: "",
                      },
                    ],
                  },
                ],
              },
            ],
          },
        });

        expect(sentMessages).toHaveLength(1);
        const message = sentMessages[0];
        if (!message) {
          throw new Error("Expected spans ingest message");
        }
        expect(message.spans[0]?.startTimeUnixNano).toBeUndefined();
        expect(message.spans[0]?.endTimeUnixNano).toBeUndefined();
      }).pipe(Effect.provide(createQueueLayer(send)));
    });

    it.effect("returns PermissionDeniedError for VIEWER role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectViewer } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .create({
            userId: projectViewer.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans: [] },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }).pipe(Effect.provide(createQueueLayer())),
    );

    it.effect("returns PermissionDeniedError for ANNOTATOR role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectAnnotator } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .create({
            userId: projectAnnotator.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans: [] },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }).pipe(Effect.provide(createQueueLayer())),
    );
  });

  describe("findAll", () => {
    it.effect("returns empty array for environments", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const traces =
          yield* db.organizations.projects.environments.traces.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(traces).toEqual([]);
      }),
    );
  });

  describe("findById", () => {
    it.effect("returns NotFoundError for missing trace", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId: "missing-trace",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );
  });

  describe("findByFunctionHash", () => {
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

    it.effect("retrieves traces by function version hash", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Insert test span directly into ClickHouse
        const testSpan = buildClickHouseSpan({
          traceId: "trace-func-hash-1",
          spanId: "span-func-hash-1",
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
          functionHash: "abc123",
        });

        yield* Effect.promise(async () => {
          await Effect.runPromise(
            Effect.gen(function* () {
              const client = yield* ClickHouse;
              yield* client.insert("spans_analytics", [testSpan]);
            }).pipe(Effect.provide(TestClickHouse)),
          );
        });

        const result =
          yield* db.organizations.projects.environments.traces.findByFunctionHash(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              functionHash: "abc123",
            },
          );

        expect(result.traces).toHaveLength(1);
        expect(result.traces[0]?.otelTraceId).toBe("trace-func-hash-1");
        expect(result.total).toBe(1);
      }),
    );

    it.effect("returns empty array when no traces match function hash", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.findByFunctionHash(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              functionHash: "non-existent-hash",
            },
          );

        expect(result.traces).toHaveLength(0);
        expect(result.total).toBe(0);
      }),
    );

    it.effect("respects limit and offset parameters", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Insert 5 spans with same function hash into ClickHouse
        // Use different offsetMinutes to ensure distinct timestamps for sorting
        const testSpans = Array.from({ length: 5 }, (_unused, index) =>
          buildClickHouseSpan({
            traceId: `trace-paginate-${index + 1}`,
            spanId: `span-paginate-${index + 1}`,
            environmentId: environment.id,
            projectId: project.id,
            organizationId: org.id,
            functionHash: "paginate-hash",
            offsetMinutes: 10 + index, // Different times for proper ordering
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

        const limitedResult =
          yield* db.organizations.projects.environments.traces.findByFunctionHash(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              functionHash: "paginate-hash",
              limit: 2,
              offset: 0,
            },
          );

        expect(limitedResult.traces).toHaveLength(2);
        expect(limitedResult.total).toBe(5);

        const offsetResult =
          yield* db.organizations.projects.environments.traces.findByFunctionHash(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              functionHash: "paginate-hash",
              limit: 2,
              offset: 2,
            },
          );

        expect(offsetResult.traces).toHaveLength(2);
        expect(offsetResult.total).toBe(5);
      }),
    );

    it.effect("deduplicates traces when spans have same trace ID", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Insert multiple spans with the SAME trace ID (different span IDs)
        // This tests the deduplication logic in findByFunctionHash
        const testSpans = [
          buildClickHouseSpan({
            traceId: "trace-duplicate-test",
            spanId: "span-duplicate-1",
            environmentId: environment.id,
            projectId: project.id,
            organizationId: org.id,
            functionHash: "dedupe-hash",
            offsetMinutes: 5,
          }),
          buildClickHouseSpan({
            traceId: "trace-duplicate-test", // Same trace ID
            spanId: "span-duplicate-2",
            environmentId: environment.id,
            projectId: project.id,
            organizationId: org.id,
            functionHash: "dedupe-hash",
            offsetMinutes: 6,
          }),
        ];

        yield* Effect.promise(async () => {
          await Effect.runPromise(
            Effect.gen(function* () {
              const client = yield* ClickHouse;
              yield* client.insert("spans_analytics", testSpans);
            }).pipe(Effect.provide(TestClickHouse)),
          );
        });

        const result =
          yield* db.organizations.projects.environments.traces.findByFunctionHash(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              functionHash: "dedupe-hash",
            },
          );

        // Should return only 1 unique trace, not 2
        expect(result.traces).toHaveLength(1);
        expect(result.traces[0]?.otelTraceId).toBe("trace-duplicate-test");
        expect(result.total).toBe(1);
      }),
    );

    it.effect(
      "returns NotFoundError when non-member tries to query (hides project)",
      () =>
        Effect.gen(function* () {
          const { environment, project, org, nonMember } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.traces
            .findByFunctionHash({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              functionHash: "any-hash",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );
  });

  describe("update", () => {
    it.effect("returns PermissionDeniedError (traces are immutable)", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId: "trace-id",
            data: undefined as never,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(ImmutableResourceError);
      }),
    );
  });

  describe("delete", () => {
    it.effect("returns NotFoundError when trace not found", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .delete({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId: "trace-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns PermissionDeniedError for DEVELOPER role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectDeveloper } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .delete({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId: "trace-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );
  });
});
