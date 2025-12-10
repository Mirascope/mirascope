import {
  describe,
  it,
  expect,
  TestEnvironmentFixture,
  MockDrizzleORM,
} from "@/tests/db";
import { Effect } from "effect";
import { Database } from "@/db";
import {
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  ImmutableResourceError,
} from "@/errors";

describe("Traces", () => {
  describe("create", () => {
    it.effect("creates single span", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test-service" } },
                { key: "service.version", value: { stringValue: "1.0.0" } },
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
        expect(result.otelTraceId).toBe("abc123");
        expect(result.serviceName).toBe("test-service");
      }),
    );

    it.effect("creates multiple spans", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test-service" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace001",
                    spanId: "span001",
                    name: "span-1",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                  {
                    traceId: "trace001",
                    spanId: "span002",
                    parentSpanId: "span001",
                    name: "span-2",
                    startTimeUnixNano: "1100000000",
                    endTimeUnixNano: "1900000000",
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
        expect(result.otelTraceId).toBe("trace001");
        expect(result.serviceName).toBe("test-service");
      }),
    );

    it.effect("upserts trace on conflict", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const makeResourceSpans = (spanId: string, serviceName: string) => [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: serviceName } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "same-trace-id",
                    spanId,
                    name: "span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        const result1 =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans: makeResourceSpans("span-a", "service-v1") },
          });

        expect(result1.acceptedSpans).toBe(1);

        const result2 =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans: makeResourceSpans("span-b", "service-v2") },
          });

        expect(result2.acceptedSpans).toBe(1);
      }),
    );

    it.effect("rejects duplicate spans", () =>
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
                    traceId: "trace-dup",
                    spanId: "span-dup",
                    name: "duplicate-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        const result1 =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          });

        expect(result1.acceptedSpans).toBe(1);
        expect(result1.rejectedSpans).toBe(0);

        const result2 =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          });

        expect(result2.acceptedSpans).toBe(0);
        expect(result2.rejectedSpans).toBe(1);
      }),
    );

    it.effect("handles span with null/optional fields", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: {},
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-null",
                    spanId: "span-null",
                    name: "minimal-span",
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

        expect(result.acceptedSpans).toBe(1);
      }),
    );

    it.effect("handles span with events and links", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-events",
                    spanId: "span-events",
                    name: "span-with-events",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                    kind: 1,
                    status: { code: 1, message: "OK" },
                    attributes: [
                      { key: "attr1", value: { stringValue: "val1" } },
                    ],
                    events: [
                      {
                        name: "event1",
                        timeUnixNano: "1500000000",
                        attributes: [
                          { key: "level", value: { stringValue: "info" } },
                        ],
                      },
                    ],
                    links: [
                      {
                        traceId: "linked-trace",
                        spanId: "linked-span",
                      },
                    ],
                    droppedAttributesCount: 0,
                    droppedEventsCount: 0,
                    droppedLinksCount: 0,
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
      }),
    );

    it.effect("handles all OTLP value types including unknown", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test" } },
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
                  key: "array-empty",
                  value: {
                    arrayValue: {
                      values: [],
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
                {
                  key: "kvlist-empty",
                  value: {
                    kvlistValue: {
                      values: [],
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
                    traceId: "trace-types",
                    spanId: "span-types",
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
      }),
    );

    it.effect("returns DatabaseError when trace upsert fails", () =>
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
        ];

        const result =
          yield* db.organizations.projects.environments.traces.create({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            data: { resourceSpans },
          });

        // When trace upsert fails, the span is rejected
        expect(result.rejectedSpans).toBe(1);
        expect(result.acceptedSpans).toBe(0);
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
            .insert(new Error("Trace upsert failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when span insert fails", () =>
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
                    traceId: "trace-span-error",
                    spanId: "span-span-error",
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
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            data: { resourceSpans },
          });

        // When span insert fails, the span is rejected
        expect(result.rejectedSpans).toBe(1);
        expect(result.acceptedSpans).toBe(0);
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
            .insert([{ id: "trace-id" }]) // Trace upsert succeeds
            .insert(new Error("Span insert failed")) // Span insert fails
            .build(),
        ),
      ),
    );

    it.effect("handles empty resourceSpans", () =>
      Effect.gen(function* () {
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
        expect(result.id).toBe("");
      }),
    );

    it.effect("returns PermissionDeniedError for VIEWER role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectViewer } =
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
                    traceId: "trace-perm",
                    spanId: "span-perm",
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
            userId: projectViewer.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission");
      }),
    );

    it.effect("returns PermissionDeniedError for ANNOTATOR role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectAnnotator } =
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
                    traceId: "trace-perm2",
                    spanId: "span-perm2",
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
            userId: projectAnnotator.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission");
      }),
    );
  });

  describe("findAll", () => {
    it.effect("retrieves all traces in an environment", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create traces
        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "svc-1" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-list-1",
                    spanId: "span-list-1",
                    name: "span-1",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
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

        yield* db.organizations.projects.environments.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: {
            resourceSpans: [
              {
                resource: {
                  attributes: [
                    { key: "service.name", value: { stringValue: "svc-2" } },
                  ],
                },
                scopeSpans: [
                  {
                    scope: { name: "test" },
                    spans: [
                      {
                        traceId: "trace-list-2",
                        spanId: "span-list-2",
                        name: "span-2",
                        startTimeUnixNano: "1000000000",
                        endTimeUnixNano: "2000000000",
                      },
                    ],
                  },
                ],
              },
            ],
          },
        });

        const traces =
          yield* db.organizations.projects.environments.traces.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(traces).toHaveLength(2);
        expect(traces.map((t) => t.otelTraceId).sort()).toEqual([
          "trace-list-1",
          "trace-list-2",
        ]);
      }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to list (hides project)",
      () =>
        Effect.gen(function* () {
          const { environment, project, org, nonMember } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.traces
            .findAll({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns empty array when environment has no traces", () =>
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

        expect(traces).toHaveLength(0);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
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
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  describe("findById", () => {
    it.effect("retrieves a trace by ID", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test-svc" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-get-123",
                    spanId: "span-get-123",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
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
            traceId: "trace-get-123",
          });

        expect(trace.otelTraceId).toBe("trace-get-123");
        expect(trace.serviceName).toBe("test-svc");
      }),
    );

    it.effect("returns `NotFoundError` when trace doesn't exist", () =>
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
            traceId: "non-existent-trace-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Trace non-existent-trace-id not found");
      }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to get (hides project)",
      () =>
        Effect.gen(function* () {
          const { environment, project, org, owner, nonMember } =
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
                      traceId: "trace-hidden",
                      spanId: "span-hidden",
                      name: "test-span",
                      startTimeUnixNano: "1000000000",
                      endTimeUnixNano: "2000000000",
                    },
                  ],
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

          const result = yield* db.organizations.projects.environments.traces
            .findById({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              traceId: "trace-hidden",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
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
            traceId: "some-trace-id",
            data: undefined as never,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(ImmutableResourceError);
        expect(result.message).toContain("immutable");
      }),
    );
  });

  describe("delete", () => {
    it.effect("deletes trace and associated spans", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "del-service" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-to-delete",
                    spanId: "span-to-delete",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
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

        yield* db.organizations.projects.environments.traces.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          traceId: "trace-to-delete",
        });

        const result =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          });

        expect(result.acceptedSpans).toBe(1);
      }),
    );

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
            traceId: "non-existent-trace-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns PermissionDeniedError for DEVELOPER role", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, projectDeveloper } =
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
                    traceId: "trace-no-delete",
                    spanId: "span-no-delete",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
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

        const result = yield* db.organizations.projects.environments.traces
          .delete({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId: "trace-no-delete",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("delete");
      }),
    );

    it.effect("returns DatabaseError when span deletion fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            traceId: "trace-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete spans");
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
            .delete(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when trace deletion fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.traces
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            traceId: "trace-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete trace");
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
            .delete([])
            .delete(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });
});
