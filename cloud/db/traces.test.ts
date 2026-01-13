import { describe, it, expect, TestEnvironmentFixture } from "@/tests/db";
import { Effect, Layer } from "effect";
import { Database } from "@/db";
import { enqueueSpanMetering } from "@/db/traces";
import { DrizzleORM } from "@/db/client";
import {
  NotFoundError,
  PermissionDeniedError,
  ImmutableResourceError,
} from "@/errors";
import {
  SpansIngestQueue,
  type SpansIngestMessage,
} from "@/workers/spanIngestQueue";
import {
  SpansMeteringQueueService,
  type SpanMeteringMessage,
} from "@/workers/spansMeteringQueue";
import { vi } from "vitest";

type QueueSend = (message: SpansIngestMessage) => Effect.Effect<void, Error>;

const buildSpan = (index: number) => ({
  traceId: "trace-1",
  spanId: `span-${index}`,
  name: `span-${index}`,
  startTimeUnixNano: "1000000000",
  endTimeUnixNano: "2000000000",
});

describe("Traces", () => {
  describe("create", () => {
    it.effect("enqueues spans and converts OTLP values", () => {
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

        // span001 is complete (has both timestamps), span002 is incomplete (empty timestamps)
        expect(result.acceptedSpans).toBe(1);
        expect(result.rejectedSpans).toBe(1);
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
        // Only completed spans are included
        expect(message.spans).toHaveLength(1);
      }).pipe(Effect.provide(Layer.succeed(SpansIngestQueue, { send })));
    });

    it.effect("splits spans into 50-span batches", () => {
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
      }).pipe(Effect.provide(Layer.succeed(SpansIngestQueue, { send })));
    });

    it.effect("meters accepted spans when metering queue is available", () => {
      const sentMessages: SpansIngestMessage[] = [];
      const meteringMessages: SpanMeteringMessage[] = [];
      const send = vi.fn<QueueSend>((message: SpansIngestMessage) => {
        sentMessages.push(message);
        return Effect.void;
      });
      const meteringSend = vi.fn((message: SpanMeteringMessage) => {
        meteringMessages.push(message);
        return Effect.void;
      });

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
                    traceId: "trace-metering",
                    spanId: "span-1",
                    name: "test-span-1",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                  {
                    traceId: "trace-metering",
                    spanId: "span-2",
                    name: "test-span-2",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                  {
                    traceId: "trace-metering",
                    spanId: "span-incomplete",
                    name: "test-span-incomplete",
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
        expect(result.rejectedSpans).toBe(1);
        expect(sentMessages).toHaveLength(1);
        expect(meteringMessages).toHaveLength(2);
        expect(meteringMessages[0]?.stripeCustomerId).toBe(
          org.stripeCustomerId,
        );
        expect(meteringMessages.map((message) => message.spanId)).toEqual([
          "trace-metering:span-1",
          "trace-metering:span-2",
        ]);
      }).pipe(
        Effect.provide(Layer.succeed(SpansIngestQueue, { send })),
        Effect.provide(
          Layer.succeed(SpansMeteringQueueService, {
            send: meteringSend,
          }),
        ),
      );
    });

    it.effect("continues when metering queue send fails", () => {
      const send = vi.fn<QueueSend>().mockReturnValue(Effect.void);
      const meteringSend = vi
        .fn()
        .mockReturnValue(Effect.fail(new Error("Metering queue down")));

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
                    traceId: "trace-metering-fail",
                    spanId: "span-fail",
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

        expect(result.acceptedSpans).toBe(1);
        expect(result.rejectedSpans).toBe(0);
        expect(meteringSend).toHaveBeenCalled();
      }).pipe(
        Effect.provide(Layer.succeed(SpansIngestQueue, { send })),
        Effect.provide(
          Layer.succeed(SpansMeteringQueueService, {
            send: meteringSend,
          }),
        ),
      );
    });

    it.noSpanIngestQueue.effect(
      "rejects spans when queue binding is missing",
      () =>
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
    it.effect("rejects spans when enqueue fails", () => {
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
      }).pipe(Effect.provide(Layer.succeed(SpansIngestQueue, { send })));
    });

    it.effect("handles empty resourceSpans", () => {
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
      }).pipe(Effect.provide(Layer.succeed(SpansIngestQueue, { send })));
    });

    it.effect("skips resources with no spans", () => {
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
      }).pipe(Effect.provide(Layer.succeed(SpansIngestQueue, { send })));
    });

    it.effect("rejects spans with empty timestamps as incomplete", () => {
      const sentMessages: SpansIngestMessage[] = [];
      const send = vi.fn<QueueSend>((message: SpansIngestMessage) => {
        sentMessages.push(message);
        return Effect.void;
      });

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

        // Spans with empty/whitespace timestamps are rejected as incomplete
        expect(result.acceptedSpans).toBe(0);
        expect(result.rejectedSpans).toBe(1);
        expect(sentMessages).toHaveLength(0);
      }).pipe(Effect.provide(Layer.succeed(SpansIngestQueue, { send })));
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
      }),
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
      }),
    );
  });

  describe("enqueueSpanMetering", () => {
    it.effect("returns early when metering queue is missing", () =>
      Effect.gen(function* () {
        yield* enqueueSpanMetering(
          ["trace-id:span-id"],
          "org-id",
          "project-id",
          "environment-id",
        );
      }).pipe(
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            select: () => ({
              from: () => ({
                where: () => Effect.fail(new Error("Drizzle should not run")),
              }),
            }),
          } as never),
        ),
      ),
    );

    it.effect("handles database error when fetching organization", () => {
      let sendCalled = false;
      const MockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: () => ({
          from: () => ({
            where: () => Effect.fail(new Error("DB error")),
          }),
        }),
      } as never);
      const MockQueueLayer = Layer.succeed(SpansMeteringQueueService, {
        send: () => {
          sendCalled = true;
          return Effect.void;
        },
      });

      return Effect.gen(function* () {
        yield* enqueueSpanMetering(
          ["trace-id:span-id"],
          "org-id",
          "project-id",
          "environment-id",
        );

        expect(sendCalled).toBe(false);
      }).pipe(Effect.provide(Layer.merge(MockDrizzleLayer, MockQueueLayer)));
    });

    it.effect("handles organization not found", () => {
      let sendCalled = false;
      const MockDrizzleLayer = Layer.succeed(DrizzleORM, {
        select: () => ({
          from: () => ({
            where: () => Effect.succeed([]),
          }),
        }),
      } as never);
      const MockQueueLayer = Layer.succeed(SpansMeteringQueueService, {
        send: () => {
          sendCalled = true;
          return Effect.void;
        },
      });

      return Effect.gen(function* () {
        yield* enqueueSpanMetering(
          ["trace-id:span-id"],
          "org-id",
          "project-id",
          "environment-id",
        );

        expect(sendCalled).toBe(false);
      }).pipe(Effect.provide(Layer.merge(MockDrizzleLayer, MockQueueLayer)));
    });
  });

  describe("findAll", () => {
    it.effect("returns traces for environments", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const traceId = "trace-find-all";
        const resourceSpans = [
          {
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [{ ...buildSpan(1), traceId }],
              },
            ],
          },
        ];

        yield* db.organizations.projects.environments.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        const traces =
          yield* db.organizations.projects.environments.traces.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(traces).toHaveLength(1);
        expect(traces[0]?.otelTraceId).toBe(traceId);
      }),
    );
  });

  describe("findById", () => {
    it.effect("returns trace by id", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const traceId = "trace-find-by-id";
        const resourceSpans = [
          {
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [{ ...buildSpan(1), traceId }],
              },
            ],
          },
        ];

        yield* db.organizations.projects.environments.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        const trace = yield* db.organizations.projects.environments.traces
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId,
          });

        expect(trace.otelTraceId).toBe(traceId);
      }),
    );

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
