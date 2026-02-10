import { Effect, Layer } from "effect";

import type { PublicProject, PublicEnvironment } from "@/db/schema";

import { toAnnotation } from "@/api/annotations.handlers";
import {
  describe,
  it,
  expect,
  TestApiContext,
  createApiClient,
} from "@/tests/api";
import { TEST_DATABASE_URL } from "@/tests/db";
import { RealtimeSpans } from "@/workers/realtimeSpans";

const AnnotationTestRealtimeLayer = Layer.succeed(RealtimeSpans, {
  upsert: () => Effect.void,
  search: () => Effect.succeed({ spans: [], total: 0, hasMore: false }),
  getTraceDetail: () =>
    Effect.succeed({
      traceId: "",
      spans: [],
      rootSpanId: null,
      totalDurationMs: null,
    }),
  exists: () => Effect.succeed(true),
});

describe("toAnnotation", () => {
  it("converts dates to ISO strings", () => {
    const now = new Date();
    const annotation = {
      id: "test-id",
      otelSpanId: "otel-span-id",
      otelTraceId: "otel-trace-id",
      label: "pass" as const,
      reasoning: "test-reasoning",
      metadata: { key: "value" },
      tags: ["Bug"],
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdBy: "user-id",
      createdAt: now,
      updatedAt: now,
    };

    const result = toAnnotation(annotation);

    expect(result.otelSpanId).toBe("otel-span-id");
    expect(result.otelTraceId).toBe("otel-trace-id");
    expect(result.tags).toEqual(["Bug"]);
    expect(result.createdAt).toBe(now.toISOString());
    expect(result.updatedAt).toBe(now.toISOString());
  });

  it("handles null dates", () => {
    const annotation = {
      id: "test-id",
      otelSpanId: "otel-span-id",
      otelTraceId: "otel-trace-id",
      label: null,
      reasoning: null,
      metadata: null,
      tags: null,
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdBy: "user-id",
      createdAt: null,
      updatedAt: null,
    };

    const result = toAnnotation(annotation);

    expect(result.otelSpanId).toBe("otel-span-id");
    expect(result.otelTraceId).toBe("otel-trace-id");
    expect(result.tags).toEqual([]);
    expect(result.createdAt).toBeNull();
    expect(result.updatedAt).toBeNull();
  });
});

describe.sequential("Annotations API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;
  let apiKeyClient: Awaited<ReturnType<typeof createApiClient>>["client"];
  let disposeApiKeyClient: (() => Promise<void>) | null = null;
  let createdAnnotationId: string;

  it.effect(
    "POST /organizations/:orgId/projects - create project for annotations test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: {
            name: "Annotations Test Project",
            slug: "annotations-test-project",
          },
        });
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments - create environment for annotations test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: {
            name: "Annotations Test Environment",
            slug: "annotations-test-env",
          },
        });
        expect(environment.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/tags - create tags for annotations test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;

        const tag = yield* client.tags.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "Bug" },
        });

        const secondTag = yield* client.tags.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "Feature" },
        });

        expect(tag.id).toBeDefined();
        expect(secondTag.id).toBeDefined();
      }),
  );

  it.effect("Create API key client for annotations tests", () =>
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
        ownerAccountType: "user" as const,
        ownerDeletedAt: owner.deletedAt,
        clawId: null,
      };
      const result = yield* Effect.promise(() =>
        createApiClient(
          TEST_DATABASE_URL,
          owner,
          apiKeyInfo,
          () => Effect.void,
          AnnotationTestRealtimeLayer,
        ),
      );
      apiKeyClient = result.client;
      disposeApiKeyClient = result.dispose;
    }),
  );

  it.effect("POST /traces - create trace for annotations test", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.traces.create({
        payload: {
          resourceSpans: [
            {
              resource: {
                attributes: [
                  { key: "service.name", value: { stringValue: "test-svc" } },
                ],
              },
              scopeSpans: [
                {
                  scope: { name: "test-scope" },
                  spans: [
                    {
                      traceId: "0123456789abcdef0123456789abcdef",
                      spanId: "0123456789abcdef",
                      name: "test-span",
                      startTimeUnixNano: "1700000000000000000",
                      endTimeUnixNano: "1700000001000000000",
                    },
                  ],
                },
              ],
            },
          ],
        },
      });
      expect(result.partialSuccess).toBeDefined();
    }),
  );

  it.effect("POST /annotations - creates annotation", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.create({
        payload: {
          otelTraceId: "0123456789abcdef0123456789abcdef",
          otelSpanId: "0123456789abcdef",
          label: "pass",
          tags: ["Bug"],
        },
      });
      expect(result.id).toBeDefined();
      expect(result.otelTraceId).toBe("0123456789abcdef0123456789abcdef");
      expect(result.otelSpanId).toBe("0123456789abcdef");
      expect(result.label).toBe("pass");
      expect(result.tags).toEqual(["Bug"]);
      createdAnnotationId = result.id;
    }),
  );

  it.effect("POST /annotations - creates annotation with optional fields", () =>
    Effect.gen(function* () {
      const optionalTraceId = "fedcba9876543210fedcba9876543210";
      const optionalSpanId = "fedcba9876543210";

      yield* apiKeyClient.traces.create({
        payload: {
          resourceSpans: [
            {
              resource: {
                attributes: [
                  { key: "service.name", value: { stringValue: "test-svc" } },
                ],
              },
              scopeSpans: [
                {
                  scope: { name: "test-scope" },
                  spans: [
                    {
                      traceId: optionalTraceId,
                      spanId: optionalSpanId,
                      name: "optional-span",
                      startTimeUnixNano: "1700000000000000001",
                      endTimeUnixNano: "1700000001000000001",
                    },
                  ],
                },
              ],
            },
          ],
        },
      });

      const result = yield* apiKeyClient.annotations.create({
        payload: {
          otelTraceId: optionalTraceId,
          otelSpanId: optionalSpanId,
          label: "fail",
          reasoning: "test-reasoning",
          metadata: { key: "value" },
          tags: ["Feature"],
        },
      });
      expect(result.id).toBeDefined();
      expect(result.label).toBe("fail");
      expect(result.reasoning).toBe("test-reasoning");
      expect(result.metadata).toEqual({ key: "value" });
      expect(result.tags).toEqual(["Feature"]);
    }),
  );

  it.effect("POST /annotations - creates annotation with null tags", () =>
    Effect.gen(function* () {
      const nullTagsTraceId = "1234567890abcdef1234567890abcdef";
      const nullTagsSpanId = "1234567890abcdef";

      yield* apiKeyClient.traces.create({
        payload: {
          resourceSpans: [
            {
              resource: {
                attributes: [
                  { key: "service.name", value: { stringValue: "test-svc" } },
                ],
              },
              scopeSpans: [
                {
                  scope: { name: "test-scope" },
                  spans: [
                    {
                      traceId: nullTagsTraceId,
                      spanId: nullTagsSpanId,
                      name: "null-tags-span",
                      startTimeUnixNano: "1700000000000000003",
                      endTimeUnixNano: "1700000001000000003",
                    },
                  ],
                },
              ],
            },
          ],
        },
      });

      const result = yield* apiKeyClient.annotations.create({
        payload: {
          otelTraceId: nullTagsTraceId,
          otelSpanId: nullTagsSpanId,
          tags: null,
        },
      });

      expect(result.id).toBeDefined();
      expect(result.tags).toEqual([]);
    }),
  );

  it.effect("POST /annotations - creates annotation without tags", () =>
    Effect.gen(function* () {
      const noTagsTraceId = "abcdefabcdefabcdefabcdefabcdefab";
      const noTagsSpanId = "abcdefabcdefabcd";

      yield* apiKeyClient.traces.create({
        payload: {
          resourceSpans: [
            {
              resource: {
                attributes: [
                  { key: "service.name", value: { stringValue: "test-svc" } },
                ],
              },
              scopeSpans: [
                {
                  scope: { name: "test-scope" },
                  spans: [
                    {
                      traceId: noTagsTraceId,
                      spanId: noTagsSpanId,
                      name: "no-tags-span",
                      startTimeUnixNano: "1700000000000000004",
                      endTimeUnixNano: "1700000001000000004",
                    },
                  ],
                },
              ],
            },
          ],
        },
      });

      const result = yield* apiKeyClient.annotations.create({
        payload: {
          otelTraceId: noTagsTraceId,
          otelSpanId: noTagsSpanId,
        },
      });

      expect(result.id).toBeDefined();
      expect(result.tags).toEqual([]);
    }),
  );

  it.effect(
    "POST /annotations - creates annotation without optional label",
    () =>
      Effect.gen(function* () {
        const noLabelTraceId = "abcdef0123456789abcdef0123456789";
        const noLabelSpanId = "abcdef0123456789";

        // Create a new span for this test
        yield* apiKeyClient.traces.create({
          payload: {
            resourceSpans: [
              {
                resource: {
                  attributes: [
                    { key: "service.name", value: { stringValue: "test-svc" } },
                  ],
                },
                scopeSpans: [
                  {
                    scope: { name: "test-scope" },
                    spans: [
                      {
                        traceId: noLabelTraceId,
                        spanId: noLabelSpanId,
                        name: "no-label-span",
                        startTimeUnixNano: "1700000000000000002",
                        endTimeUnixNano: "1700000001000000002",
                      },
                    ],
                  },
                ],
              },
            ],
          },
        });

        const result = yield* apiKeyClient.annotations.create({
          payload: {
            otelTraceId: noLabelTraceId,
            otelSpanId: noLabelSpanId,
            // No label provided - should default to null
          },
        });
        expect(result.id).toBeDefined();
        expect(result.label).toBeNull();
      }),
  );

  it.effect("GET /annotations/:id - gets annotation by ID", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.get({
        path: { id: createdAnnotationId },
      });
      expect(result.id).toBe(createdAnnotationId);
      expect(result.label).toBe("pass");
    }),
  );

  it.effect("PUT /annotations/:id - updates annotation", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.update({
        path: { id: createdAnnotationId },
        payload: {
          label: "fail",
          reasoning: "updated-reasoning",
          tags: null,
        },
      });
      expect(result.id).toBe(createdAnnotationId);
      expect(result.label).toBe("fail");
      expect(result.reasoning).toBe("updated-reasoning");
      expect(result.tags).toEqual([]);
    }),
  );

  it.effect("PUT /annotations/:id - updates annotation without tags", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.update({
        path: { id: createdAnnotationId },
        payload: {
          label: "pass",
        },
      });
      expect(result.id).toBe(createdAnnotationId);
      expect(result.label).toBe("pass");
    }),
  );

  it.effect("PUT /annotations/:id - updates annotation tags", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.update({
        path: { id: createdAnnotationId },
        payload: {
          tags: ["Bug"],
        },
      });
      expect(result.id).toBe(createdAnnotationId);
      expect(result.tags).toEqual(["Bug"]);
    }),
  );

  it.effect("GET /annotations - lists annotations", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.list({
        urlParams: {},
      });
      expect(result.total).toBeGreaterThanOrEqual(1);
      expect(result.annotations.length).toBeGreaterThanOrEqual(1);
    }),
  );

  it.effect("GET /annotations - filters by label", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.list({
        urlParams: { label: "fail" },
      });
      expect(result.total).toBeGreaterThanOrEqual(1);
      expect(result.annotations.every((a) => a.label === "fail")).toBe(true);
    }),
  );

  it.effect("GET /annotations - filters by otelTraceId", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.list({
        urlParams: { otelTraceId: "0123456789abcdef0123456789abcdef" },
      });
      expect(result.total).toBeGreaterThanOrEqual(1);
    }),
  );

  it.effect("GET /annotations - paginates with limit and offset", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.list({
        urlParams: { limit: 1, offset: 0 },
      });
      expect(result.annotations.length).toBeLessThanOrEqual(1);
    }),
  );

  it.effect("DELETE /annotations/:id - deletes annotation", () =>
    Effect.gen(function* () {
      const deleteTraceId = "00112233445566778899aabbccddeeff";
      const deleteSpanId = "0011223344556677";

      yield* apiKeyClient.traces.create({
        payload: {
          resourceSpans: [
            {
              resource: {
                attributes: [
                  { key: "service.name", value: { stringValue: "test-svc" } },
                ],
              },
              scopeSpans: [
                {
                  scope: { name: "test-scope" },
                  spans: [
                    {
                      traceId: deleteTraceId,
                      spanId: deleteSpanId,
                      name: "delete-span",
                      startTimeUnixNano: "1700000000000000002",
                      endTimeUnixNano: "1700000001000000002",
                    },
                  ],
                },
              ],
            },
          ],
        },
      });

      const created = yield* apiKeyClient.annotations.create({
        payload: {
          otelTraceId: deleteTraceId,
          otelSpanId: deleteSpanId,
          label: "pass",
        },
      });

      yield* apiKeyClient.annotations.delete({ path: { id: created.id } });

      const list = yield* apiKeyClient.annotations.list({
        urlParams: {},
      });
      expect(list.annotations.find((a) => a.id === created.id)).toBeUndefined();
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
