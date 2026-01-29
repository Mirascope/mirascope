import { eq } from "drizzle-orm";
import { Effect, Layer } from "effect";
import { vi, afterAll } from "vitest";

import { ClickHouse } from "@/db/clickhouse/client";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { organizations } from "@/db/schema/organizations";
import {
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  ImmutableResourceError,
  PlanLimitExceededError,
} from "@/errors";
import { TestClickHouse } from "@/tests/clickhouse";
import {
  describe,
  it,
  expect,
  TestEnvironmentFixture,
  MockDrizzleORM,
  TestDrizzleORM,
} from "@/tests/db";
import { getTestClickHouseConfig } from "@/tests/global-setup";
import { TestSubscriptionWithRealDatabaseFixture } from "@/tests/payments";
import {
  SpansIngestQueue,
  type SpansIngestMessage,
} from "@/workers/spanIngestQueue";

const clickhouseConfig = getTestClickHouseConfig();

const cleanupClickHouse = Effect.gen(function* () {
  const client = yield* ClickHouse;
  yield* client.command(
    `TRUNCATE TABLE ${clickhouseConfig.database}.spans_analytics`,
  );
});

afterAll(async () => {
  await Effect.runPromise(
    cleanupClickHouse.pipe(Effect.provide(TestClickHouse)),
  );
});

type QueueSend = (message: SpansIngestMessage) => Effect.Effect<void, Error>;

const baseTimeUnixNano = BigInt(Date.now()) * 1000000n;

const buildSpan = (index: number) => {
  const startTime = baseTimeUnixNano + BigInt(index) * 1000000n;
  const endTime = startTime + 1000000n;

  return {
    traceId: "trace-1",
    spanId: `span-${index}`,
    name: `span-${index}`,
    startTimeUnixNano: startTime.toString(),
    endTimeUnixNano: endTime.toString(),
  };
};

/**
 * Helper to create a complete test environment with a specific stripe customer ID.
 */
function* createTestEnvironmentWithCustomer(customerId: string) {
  const db = yield* Database;
  const drizzle = yield* DrizzleORM;

  // Create owner user
  const owner = yield* db.users.create({
    data: { email: `owner-${crypto.randomUUID()}@example.com`, name: "Owner" },
  });

  // Create organization through Database service
  const org = yield* db.organizations.create({
    userId: owner.id,
    data: {
      name: "Test Organization",
      slug: `test-org-${crypto.randomUUID()}`,
    },
  });

  // Update organization with specific stripe customer ID
  yield* drizzle
    .update(organizations)
    .set({ stripeCustomerId: customerId })
    .where(eq(organizations.id, org.id));

  // Create project
  const project = yield* db.organizations.projects.create({
    userId: owner.id,
    organizationId: org.id,
    data: { name: "Test Project", slug: `project-${crypto.randomUUID()}` },
  });

  // Create environment
  const environment = yield* db.organizations.projects.environments.create({
    userId: owner.id,
    organizationId: org.id,
    projectId: project.id,
    data: { name: "development", slug: "development" },
  });

  return { org, owner, project, environment };
}

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

    it.effect("creates trace successfully when under span limit", () => {
      const customerId = `cus_under_limit_${Date.now()}_${Math.random()}`;

      return Effect.gen(function* () {
        const { environment, project, org, owner } = yield* Effect.gen(
          createTestEnvironmentWithCustomer.bind(null, customerId),
        );
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: `trace-under-limit-${crypto.randomUUID()}`,
                    spanId: `span-under-limit-${crypto.randomUUID()}`,
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
      }).pipe(
        Effect.provide(
          Database.Default.pipe(
            Layer.provideMerge(TestDrizzleORM),
            Layer.provide(
              TestSubscriptionWithRealDatabaseFixture(
                {
                  plan: "free",
                  stripeCustomerId: customerId,
                  meterBalance: "500000", // Under 1M limit
                },
                TestDrizzleORM,
              ),
            ),
          ),
        ),
      );
    });

    it.effect("returns PlanLimitExceededError when at span limit", () => {
      const customerId = `cus_at_limit_${Date.now()}_${Math.random()}`;

      return Effect.gen(function* () {
        const { environment, project, org, owner } = yield* Effect.gen(
          createTestEnvironmentWithCustomer.bind(null, customerId),
        );
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: `trace-at-limit-${crypto.randomUUID()}`,
                    spanId: `span-at-limit-${crypto.randomUUID()}`,
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        const result = yield* db.organizations.projects.environments.traces
          .create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PlanLimitExceededError);
        if (result instanceof PlanLimitExceededError) {
          expect(result.message).toContain("Cannot ingest spans");
          expect(result.message).toContain("1,000,000 spans/month");
          expect(result.currentUsage).toBe(1000000);
          expect(result.limit).toBe(1000000);
          expect(result.limitType).toBe("spansPerMonth");
        }
      }).pipe(
        Effect.provide(
          Database.Default.pipe(
            Layer.provideMerge(TestDrizzleORM),
            Layer.provide(
              TestSubscriptionWithRealDatabaseFixture(
                {
                  plan: "free",
                  stripeCustomerId: customerId,
                  meterBalance: "1000000", // At 1M limit
                },
                TestDrizzleORM,
              ),
            ),
          ),
        ),
      );
    });

    it.effect("returns PlanLimitExceededError when over span limit", () => {
      const customerId = `cus_over_limit_${Date.now()}_${Math.random()}`;

      return Effect.gen(function* () {
        const { environment, project, org, owner } = yield* Effect.gen(
          createTestEnvironmentWithCustomer.bind(null, customerId),
        );
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: `trace-over-limit-${crypto.randomUUID()}`,
                    spanId: `span-over-limit-${crypto.randomUUID()}`,
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        const result = yield* db.organizations.projects.environments.traces
          .create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PlanLimitExceededError);
        if (result instanceof PlanLimitExceededError) {
          expect(result.currentUsage).toBe(1500000);
          expect(result.limit).toBe(1000000);
        }
      }).pipe(
        Effect.provide(
          Database.Default.pipe(
            Layer.provideMerge(TestDrizzleORM),
            Layer.provide(
              TestSubscriptionWithRealDatabaseFixture(
                {
                  plan: "free",
                  stripeCustomerId: customerId,
                  meterBalance: "1500000", // Over 1M limit
                },
                TestDrizzleORM,
              ),
            ),
          ),
        ),
      );
    });

    it.effect(
      "returns DatabaseError when organization fetch fails during span limit check",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const resourceSpans = [
            {
              resource: { attributes: [] },
              scopeSpans: [
                {
                  scope: { name: "test" },
                  spans: [
                    {
                      traceId: "trace-org-fetch-error",
                      spanId: "span-org-fetch-error",
                      name: "test-span",
                      startTimeUnixNano: "1000000000",
                      endTimeUnixNano: "2000000000",
                    },
                  ],
                },
              ],
            },
          ];

          const result = yield* db.organizations.projects.environments.traces
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              data: { resourceSpans },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toContain(
            "Failed to fetch organization for span limit check",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              .select([{ id: "project-id" }])
              .select(new Error("Database error during organization fetch"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns NotFoundError when organization not found during span limit check",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const resourceSpans = [
            {
              resource: { attributes: [] },
              scopeSpans: [
                {
                  scope: { name: "test" },
                  spans: [
                    {
                      traceId: "trace-org-not-found",
                      spanId: "span-org-not-found",
                      name: "test-span",
                      startTimeUnixNano: "1000000000",
                      endTimeUnixNano: "2000000000",
                    },
                  ],
                },
              ],
            },
          ];

          const result = yield* db.organizations.projects.environments.traces
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              data: { resourceSpans },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toContain("Organization not found");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              .select([{ id: "project-id" }])
              .select([]) // Empty result - organization not found
              .build(),
          ),
        ),
    );
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

    it.effect("returns DatabaseError when list query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to list traces");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select([
              {
                memberId: "owner-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            .select([{ id: "project-id" }])
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
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

        const trace =
          yield* db.organizations.projects.environments.traces.findById({
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

    it.effect("returns DatabaseError when trace lookup fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            traceId: "trace-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get trace");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select([
              {
                memberId: "owner-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            .select([{ id: "project-id" }])
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
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
