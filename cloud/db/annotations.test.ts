/**
 * Tests for the Effect-native Annotations service.
 */

import { Effect, Layer } from "effect";
import { it as vitestIt } from "vitest";
import {
  describe,
  it,
  expect,
  TestEnvironmentFixture,
  TestSpanFixture,
  MockDrizzleORM,
} from "@/tests/db";
import { Database } from "@/db/database";
import { ClickHouseSearch } from "@/clickhouse/search";
import { RealtimeSpans } from "@/realtimeSpans";
import {
  NotFoundError,
  DatabaseError,
  PermissionDeniedError,
  AlreadyExistsError,
  ClickHouseError,
} from "@/errors";

// =============================================================================
// Annotations Tests
// =============================================================================

describe("Annotations", () => {
  describe("create", () => {
    it.effect("creates an annotation for a span", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        const annotation =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: {
                otelSpanId: spanId,
                otelTraceId: traceId,
                label: "pass",
                reasoning: "This span completed successfully",
                metadata: { score: 0.95 },
              },
            },
          );

        expect(annotation).toBeDefined();
        expect(annotation.otelSpanId).toBe(spanId);
        expect(annotation.otelTraceId).toBe(traceId);
        expect(annotation.label).toBe("pass");
        expect(annotation.reasoning).toBe("This span completed successfully");
        expect(annotation.metadata).toEqual({ score: 0.95 });
        expect(annotation.environmentId).toBe(environment.id);
        expect(annotation.projectId).toBe(project.id);
        expect(annotation.organizationId).toBe(org.id);
      }),
    );

    it.effect("creates an annotation with createdBy set to userId", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        const annotation =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: {
                otelSpanId: spanId,
                otelTraceId: traceId,
                label: "fail",
              },
            },
          );

        expect(annotation.createdBy).toBe(owner.id);
      }),
    );

    it.effect("returns NotFoundError when span does not exist", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: {
                otelSpanId: "nonexistentspanid",
                otelTraceId: "nonexistenttraceid0123456789ab",
                label: "pass",
              },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect((result as NotFoundError).resource).toBe("span");
      }).pipe(
        Effect.provide(
          Layer.mergeAll(
            Layer.succeed(RealtimeSpans, {
              upsert: () => Effect.void,
              search: () =>
                Effect.succeed({ spans: [], total: 0, hasMore: false }),
              getTraceDetail: () =>
                Effect.succeed({
                  traceId: "nonexistenttraceid0123456789ab",
                  spans: [],
                  rootSpanId: null,
                  totalDurationMs: null,
                }),
              exists: () => Effect.succeed(false),
            }),
            Layer.succeed(ClickHouseSearch, {
              search: () =>
                Effect.succeed({ spans: [], total: 0, hasMore: false }),
              getTraceDetail: () =>
                Effect.succeed({
                  traceId: "nonexistenttraceid0123456789ab",
                  spans: [],
                  rootSpanId: null,
                  totalDurationMs: null,
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
            }),
          ),
        ),
      ),
    );

    it.effect(
      "returns NotFoundError when realtime and ClickHouse miss span",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result =
            yield* db.organizations.projects.environments.traces.annotations
              .create({
                userId: "00000000-0000-0000-0000-000000000000",
                organizationId: "00000000-0000-0000-0000-000000000003",
                projectId: "00000000-0000-0000-0000-000000000002",
                environmentId: "00000000-0000-0000-0000-000000000001",
                data: {
                  otelSpanId: "missing-span",
                  otelTraceId: "missing-trace",
                  label: "pass",
                },
              })
              .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              new MockDrizzleORM()
                // organizationMemberships.getRole (inside authorize)
                .select([
                  {
                    role: "MEMBER",
                    organizationId: "00000000-0000-0000-0000-000000000003",
                    memberId: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                  },
                ])
                // organizationMemberships.findById result
                .select([
                  {
                    role: "MEMBER",
                    organizationId: "00000000-0000-0000-0000-000000000003",
                    memberId: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                  },
                ])
                // projectMemberships.getMembership (authorization)
                .select([
                  {
                    role: "ADMIN",
                    projectId: "00000000-0000-0000-0000-000000000002",
                    memberId: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                  },
                ])
                // span lookup
                .select([])
                .build(),
              Layer.succeed(RealtimeSpans, {
                upsert: () => Effect.void,
                search: () =>
                  Effect.succeed({ spans: [], total: 0, hasMore: false }),
                getTraceDetail: () =>
                  Effect.succeed({
                    traceId: "missing-trace",
                    spans: [],
                    rootSpanId: null,
                    totalDurationMs: null,
                  }),
                exists: () => Effect.succeed(false),
              }),
              Layer.succeed(ClickHouseSearch, {
                search: () =>
                  Effect.succeed({ spans: [], total: 0, hasMore: false }),
                getTraceDetail: () =>
                  Effect.succeed({
                    traceId: "missing-trace",
                    spans: [],
                    rootSpanId: null,
                    totalDurationMs: null,
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
              }),
            ),
          ),
        ),
    );

    it.effect("creates annotation when realtime span exists", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const annotation =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              data: {
                otelSpanId: "exists-span",
                otelTraceId: "exists-trace",
                label: "pass",
              },
            },
          );

        expect(annotation.otelSpanId).toBe("exists-span");
      }).pipe(
        Effect.provide(
          Layer.mergeAll(
            new MockDrizzleORM()
              .select([
                {
                  role: "MEMBER",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "MEMBER",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "ADMIN",
                  projectId: "00000000-0000-0000-0000-000000000002",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([])
              .insert([
                {
                  id: "annotation-id",
                  otelSpanId: "exists-span",
                  otelTraceId: "exists-trace",
                  label: "pass",
                  reasoning: null,
                  metadata: null,
                  environmentId: "00000000-0000-0000-0000-000000000001",
                  projectId: "00000000-0000-0000-0000-000000000002",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  createdBy: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                  updatedAt: new Date(),
                },
              ])
              .build(),
            Layer.succeed(RealtimeSpans, {
              upsert: () => Effect.void,
              search: () =>
                Effect.succeed({ spans: [], total: 0, hasMore: false }),
              getTraceDetail: () =>
                Effect.succeed({
                  traceId: "exists-trace",
                  spans: [],
                  rootSpanId: null,
                  totalDurationMs: null,
                }),
              exists: () => Effect.succeed(true),
            }),
          ),
        ),
      ),
    );

    it.effect("returns NotFoundError when realtime and ClickHouse fail", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .create({
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              data: {
                otelSpanId: "error-span",
                otelTraceId: "error-trace",
                label: "pass",
              },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(
        Effect.provide(
          Layer.mergeAll(
            new MockDrizzleORM()
              .select([
                {
                  role: "MEMBER",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "MEMBER",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "ADMIN",
                  projectId: "00000000-0000-0000-0000-000000000002",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([])
              .build(),
            Layer.succeed(RealtimeSpans, {
              upsert: () => Effect.void,
              search: () =>
                Effect.succeed({ spans: [], total: 0, hasMore: false }),
              getTraceDetail: () =>
                Effect.succeed({
                  traceId: "error-trace",
                  spans: [],
                  rootSpanId: null,
                  totalDurationMs: null,
                }),
              exists: () => Effect.fail(new Error("realtime failed")),
            }),
            Layer.succeed(ClickHouseSearch, {
              search: () =>
                Effect.succeed({ spans: [], total: 0, hasMore: false }),
              getTraceDetail: () =>
                Effect.fail(
                  new ClickHouseError({
                    message: "clickhouse failed",
                    cause: new Error("clickhouse failed"),
                  }),
                ),
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
            }),
          ),
        ),
      ),
    );

    it.effect(
      "creates annotation when realtime and ClickHouse services missing",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const annotation =
            yield* db.organizations.projects.environments.traces.annotations.create(
              {
                userId: "00000000-0000-0000-0000-000000000000",
                organizationId: "00000000-0000-0000-0000-000000000003",
                projectId: "00000000-0000-0000-0000-000000000002",
                environmentId: "00000000-0000-0000-0000-000000000001",
                data: {
                  otelSpanId: "missing-services-span",
                  otelTraceId: "missing-services-trace",
                  label: "pass",
                },
              },
            );

          expect(annotation.otelSpanId).toBe("missing-services-span");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([
                {
                  role: "MEMBER",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "MEMBER",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "ADMIN",
                  projectId: "00000000-0000-0000-0000-000000000002",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([])
              .insert([
                {
                  id: "annotation-id",
                  otelSpanId: "missing-services-span",
                  otelTraceId: "missing-services-trace",
                  label: "pass",
                  reasoning: null,
                  metadata: null,
                  environmentId: "00000000-0000-0000-0000-000000000001",
                  projectId: "00000000-0000-0000-0000-000000000002",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  createdBy: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                  updatedAt: new Date(),
                },
              ])
              .build(),
          ),
        ),
    );

    vitestIt(
      "returns NotFoundError when both services are missing",
      async () => {
        const effect = Effect.gen(function* () {
          const db = yield* Database;

          return yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              data: {
                otelSpanId: "no-services-span",
                otelTraceId: "no-services-trace",
                label: "pass",
              },
            },
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([
                {
                  role: "MEMBER",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "MEMBER",
                  organizationId: "00000000-0000-0000-0000-000000000003",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "ADMIN",
                  projectId: "00000000-0000-0000-0000-000000000002",
                  memberId: "00000000-0000-0000-0000-000000000000",
                  createdAt: new Date(),
                },
              ])
              .build(),
          ),
          Effect.flip,
        );

        const result = await Effect.runPromise(effect);
        expect(result).toBeInstanceOf(NotFoundError);
      },
    );

    vitestIt(
      "returns NotFoundError when realtime exists false and ClickHouse missing",
      async () => {
        const effect = Effect.gen(function* () {
          const db = yield* Database;

          return yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              data: {
                otelSpanId: "no-clickhouse-span",
                otelTraceId: "no-clickhouse-trace",
                label: "pass",
              },
            },
          );
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              new MockDrizzleORM()
                .select([
                  {
                    role: "MEMBER",
                    organizationId: "00000000-0000-0000-0000-000000000003",
                    memberId: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                  },
                ])
                .select([
                  {
                    role: "MEMBER",
                    organizationId: "00000000-0000-0000-0000-000000000003",
                    memberId: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                  },
                ])
                .select([
                  {
                    role: "ADMIN",
                    projectId: "00000000-0000-0000-0000-000000000002",
                    memberId: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                  },
                ])
                .build(),
              Layer.succeed(RealtimeSpans, {
                upsert: () => Effect.void,
                search: () =>
                  Effect.succeed({ spans: [], total: 0, hasMore: false }),
                getTraceDetail: () =>
                  Effect.succeed({
                    traceId: "no-clickhouse-trace",
                    spans: [],
                    rootSpanId: null,
                    totalDurationMs: null,
                  }),
                exists: () => Effect.succeed(false),
              }),
            ),
          ),
          Effect.flip,
        );

        const result = await Effect.runPromise(effect);
        expect(result).toBeInstanceOf(NotFoundError);
      },
    );

    vitestIt(
      "creates annotation when realtime missing and ClickHouse has span",
      async () => {
        const effect = Effect.gen(function* () {
          const db = yield* Database;

          return yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              data: {
                otelSpanId: "clickhouse-span",
                otelTraceId: "clickhouse-trace",
                label: "pass",
              },
            },
          );
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              new MockDrizzleORM()
                .select([
                  {
                    role: "MEMBER",
                    organizationId: "00000000-0000-0000-0000-000000000003",
                    memberId: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                  },
                ])
                .select([
                  {
                    role: "MEMBER",
                    organizationId: "00000000-0000-0000-0000-000000000003",
                    memberId: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                  },
                ])
                .select([
                  {
                    role: "ADMIN",
                    projectId: "00000000-0000-0000-0000-000000000002",
                    memberId: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                  },
                ])
                .select([])
                .insert([
                  {
                    id: "annotation-id",
                    otelSpanId: "clickhouse-span",
                    otelTraceId: "clickhouse-trace",
                    label: "pass",
                    reasoning: null,
                    metadata: null,
                    environmentId: "00000000-0000-0000-0000-000000000001",
                    projectId: "00000000-0000-0000-0000-000000000002",
                    organizationId: "00000000-0000-0000-0000-000000000003",
                    createdBy: "00000000-0000-0000-0000-000000000000",
                    createdAt: new Date(),
                    updatedAt: new Date(),
                  },
                ])
                .build(),
              Layer.succeed(ClickHouseSearch, {
                search: () =>
                  Effect.succeed({ spans: [], total: 0, hasMore: false }),
                getTraceDetail: () =>
                  Effect.succeed({
                    traceId: "clickhouse-trace",
                    spans: [
                      {
                        traceId: "clickhouse-trace",
                        spanId: "clickhouse-span",
                        parentSpanId: null,
                        environmentId: "00000000-0000-0000-0000-000000000001",
                        projectId: "00000000-0000-0000-0000-000000000002",
                        organizationId: "00000000-0000-0000-0000-000000000003",
                        name: "trace-span",
                        startTime: new Date().toISOString(),
                        endTime: new Date().toISOString(),
                        durationMs: 1,
                        kind: 1,
                        statusCode: null,
                        statusMessage: null,
                        model: null,
                        provider: null,
                        inputTokens: null,
                        outputTokens: null,
                        totalTokens: null,
                        costUsd: null,
                        functionId: null,
                        functionName: null,
                        functionVersion: null,
                        errorType: null,
                        errorMessage: null,
                        attributes: "{}",
                        events: null,
                        links: null,
                        serviceName: null,
                        serviceVersion: null,
                        resourceAttributes: null,
                      },
                    ],
                    rootSpanId: null,
                    totalDurationMs: null,
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
              }),
            ),
          ),
        );

        const result = await Effect.runPromise(effect);
        expect(result.otelSpanId).toBe("clickhouse-span");
      },
    );

    it.effect("returns PermissionDeniedError when user lacks permission", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectViewer } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .create({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: {
                otelSpanId: "0123456789abcdef",
                otelTraceId: "0123456789abcdef0123456789abcdef",
                label: "pass",
              },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );

    it.effect("allows ANNOTATOR role to create annotations", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectAnnotator, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        const annotation =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: {
                otelSpanId: spanId,
                otelTraceId: traceId,
                label: "pass",
              },
            },
          );

        expect(annotation.label).toBe("pass");
        expect(annotation.createdBy).toBe(projectAnnotator.id);
      }),
    );

    it.effect("returns AlreadyExistsError for duplicate annotation", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .create({
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              data: {
                otelSpanId: "testspan",
                otelTraceId: "testtrace",
                label: "pass",
              },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect(result.message).toBe(
          "Annotation for span testspan already exists",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getRole (inside authorize)
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById result
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getMembership (authorization)
            .select([
              {
                role: "ADMIN",
                projectId: "00000000-0000-0000-0000-000000000002",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // annotation insert (unique constraint violation)
            .insert(
              Object.assign(new Error("duplicate key"), { code: "23505" }),
            )
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when annotation insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .create({
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              data: {
                otelSpanId: "testspan",
                otelTraceId: "testtrace",
                label: "pass",
              },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create annotation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getRole (inside authorize)
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById result
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getMembership (authorization)
            .select([
              {
                role: "ADMIN",
                projectId: "00000000-0000-0000-0000-000000000002",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // annotation insert (fail)
            .insert(new Error("Insert failed"))
            .build(),
        ),
      ),
    );
  });

  describe("findById", () => {
    it.effect("returns annotation by ID", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
            },
          );

        const found =
          yield* db.organizations.projects.environments.traces.annotations.findById(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: created.id,
            },
          );

        expect(found.id).toBe(created.id);
        expect(found.label).toBe("pass");
      }),
    );

    it.effect("returns NotFoundError when annotation does not exist", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .findById({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: "00000000-0000-0000-0000-000000000000",
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect((result as NotFoundError).resource).toBe("annotation");
      }),
    );

    it.effect("returns PermissionDeniedError when user lacks permission", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const db = yield* Database;

        // User with no access
        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .findById({
              userId: "00000000-0000-0000-0000-000000000099",
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: "00000000-0000-0000-0000-000000000000",
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError); // NotFoundError for non-members
      }),
    );

    it.effect("returns DatabaseError on query failure", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .findById({
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              annotationId: "00000000-0000-0000-0000-000000000000",
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get annotation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getRole (inside authorize)
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById result
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getMembership (authorization)
            .select([
              {
                role: "ADMIN",
                projectId: "00000000-0000-0000-0000-000000000002",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // annotation query (fail)
            .select(new Error("Query failed"))
            .build(),
        ),
      ),
    );
  });

  describe("update", () => {
    it.effect("updates annotation label", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
            },
          );

        const updated =
          yield* db.organizations.projects.environments.traces.annotations.update(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: created.id,
              data: { label: "fail" },
            },
          );

        expect(updated.label).toBe("fail");
        expect(updated.id).toBe(created.id);
      }),
    );

    it.effect("updates annotation reasoning", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: {
                otelSpanId: spanId,
                otelTraceId: traceId,
                reasoning: "original reasoning",
              },
            },
          );

        const updated =
          yield* db.organizations.projects.environments.traces.annotations.update(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: created.id,
              data: { reasoning: "updated reasoning" },
            },
          );

        expect(updated.reasoning).toBe("updated reasoning");
      }),
    );

    it.effect("updates annotation data", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: {
                otelSpanId: spanId,
                otelTraceId: traceId,
                metadata: { key: "original" },
              },
            },
          );

        const updated =
          yield* db.organizations.projects.environments.traces.annotations.update(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: created.id,
              data: { metadata: { key: "updated", extra: true } },
            },
          );

        expect(updated.metadata).toEqual({ key: "updated", extra: true });
      }),
    );

    it.effect("returns NotFoundError when annotation does not exist", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .update({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: "00000000-0000-0000-0000-000000000000",
              data: { label: "pass" },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns PermissionDeniedError when user lacks permission", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectViewer } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .update({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: "00000000-0000-0000-0000-000000000000",
              data: { label: "pass" },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );

    it.effect("allows ANNOTATOR role to update annotations", () =>
      Effect.gen(function* () {
        const {
          environment,
          project,
          org,
          owner,
          projectAnnotator,
          traceId,
          spanId,
        } = yield* TestSpanFixture;
        const db = yield* Database;

        // Owner creates the annotation
        const created =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
            },
          );

        // Annotator updates it
        const updated =
          yield* db.organizations.projects.environments.traces.annotations.update(
            {
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: created.id,
              data: { label: "fail" },
            },
          );

        expect(updated.label).toBe("fail");
      }),
    );

    it.effect("returns DatabaseError on update failure", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .update({
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              annotationId: "00000000-0000-0000-0000-000000000000",
              data: { label: "pass" },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update annotation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getRole (inside authorize)
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById result
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getMembership (authorization)
            .select([
              {
                role: "ADMIN",
                projectId: "00000000-0000-0000-0000-000000000002",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // update query (fail)
            .update(new Error("Update failed"))
            .build(),
        ),
      ),
    );
  });

  describe("delete", () => {
    it.effect("deletes an annotation", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
            },
          );

        // Delete should succeed
        yield* db.organizations.projects.environments.traces.annotations.delete(
          {
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: created.id,
          },
        );

        // Should not be findable anymore
        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .findById({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: created.id,
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns NotFoundError when annotation does not exist", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .delete({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: "00000000-0000-0000-0000-000000000000",
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

        // Developer cannot delete (only ADMIN can)
        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .delete({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: "00000000-0000-0000-0000-000000000000",
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

        // Annotator cannot delete (only ADMIN can)
        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .delete({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              annotationId: "00000000-0000-0000-0000-000000000000",
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );

    it.effect("returns DatabaseError on delete failure", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .delete({
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
              annotationId: "00000000-0000-0000-0000-000000000000",
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete annotation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getRole (inside authorize)
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById result
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getMembership (authorization)
            .select([
              {
                role: "ADMIN",
                projectId: "00000000-0000-0000-0000-000000000002",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // delete query (fail)
            .delete(new Error("Delete failed"))
            .build(),
        ),
      ),
    );
  });

  describe("findAll", () => {
    it.effect("lists all annotations in environment", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        // Create annotation for the existing span
        yield* db.organizations.projects.environments.traces.annotations.create(
          {
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
          },
        );

        yield* db.organizations.projects.environments.traces.annotations.create(
          {
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: {
              otelSpanId: "abcdef0123456789",
              otelTraceId: traceId,
              label: "fail",
            },
          },
        );

        const listResult =
          yield* db.organizations.projects.environments.traces.annotations.findAll(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            },
          );

        expect(listResult.length).toBe(2);
      }),
    );

    it.effect("returns empty list when no annotations", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations.findAll(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            },
          );

        expect(result.length).toBe(0);
        expect(result).toEqual([]);
      }),
    );

    it.effect("filters by traceId", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        yield* db.organizations.projects.environments.traces.annotations.create(
          {
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
          },
        );

        const result =
          yield* db.organizations.projects.environments.traces.annotations.findAll(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              filters: { otelTraceId: traceId },
            },
          );

        expect(result.length).toBe(1);
        expect(result[0].label).toBe("pass");
      }),
    );

    it.effect("filters by spanId", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        yield* db.organizations.projects.environments.traces.annotations.create(
          {
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
          },
        );

        const result =
          yield* db.organizations.projects.environments.traces.annotations.findAll(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              filters: { otelSpanId: spanId },
            },
          );

        expect(result.length).toBe(1);
        expect(result[0].otelSpanId).toBe(spanId);
      }),
    );

    it.effect("filters by label", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, traceId, spanId } =
          yield* TestSpanFixture;
        const db = yield* Database;

        yield* db.organizations.projects.environments.traces.annotations.create(
          {
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
          },
        );

        const positiveResult =
          yield* db.organizations.projects.environments.traces.annotations.findAll(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              filters: { label: "pass" },
            },
          );
        expect(positiveResult.length).toBe(1);

        const negativeResult =
          yield* db.organizations.projects.environments.traces.annotations.findAll(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              filters: { label: "fail" },
            },
          );
        expect(negativeResult.length).toBe(0);
      }),
    );

    it.effect("paginates with limit", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create 3 spans with annotations
        const traceId = "0123456789abcdef0123456789abcdef";
        const spanIds = [
          "span000000000001",
          "span000000000002",
          "span000000000003",
        ];

        for (const spanId of spanIds) {
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
            },
          );
        }

        const result =
          yield* db.organizations.projects.environments.traces.annotations.findAll(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              filters: { limit: 2 },
            },
          );

        expect(result.length).toBe(2);
      }),
    );

    it.effect("paginates with offset", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create 3 spans with annotations
        const traceId = "0123456789abcdef0123456789abcdef";
        const spanIds = [
          "span000000000001",
          "span000000000002",
          "span000000000003",
        ];

        for (const spanId of spanIds) {
          yield* db.organizations.projects.environments.traces.annotations.create(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { otelSpanId: spanId, otelTraceId: traceId, label: "pass" },
            },
          );
        }

        const result =
          yield* db.organizations.projects.environments.traces.annotations.findAll(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              filters: { limit: 10, offset: 2 },
            },
          );

        expect(result.length).toBe(1);
      }),
    );

    it.effect("returns PermissionDeniedError when user lacks permission", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const db = yield* Database;

        // User with no access
        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .findAll({
              userId: "00000000-0000-0000-0000-000000000099",
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError); // NotFoundError for non-members
      }),
    );

    it.effect("returns DatabaseError on query failure", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.traces.annotations
            .findAll({
              userId: "00000000-0000-0000-0000-000000000000",
              organizationId: "00000000-0000-0000-0000-000000000003",
              projectId: "00000000-0000-0000-0000-000000000002",
              environmentId: "00000000-0000-0000-0000-000000000001",
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to list annotations");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getRole (inside authorize)
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById result
            .select([
              {
                role: "MEMBER",
                organizationId: "00000000-0000-0000-0000-000000000003",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getMembership (authorization)
            .select([
              {
                role: "ADMIN",
                projectId: "00000000-0000-0000-0000-000000000002",
                memberId: "00000000-0000-0000-0000-000000000000",
                createdAt: new Date(),
              },
            ])
            // annotations query (fail)
            .select(new Error("Query failed"))
            .build(),
        ),
      ),
    );
  });
});
