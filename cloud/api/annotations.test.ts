import { describe as vitestDescribe, it as vitestIt, expect } from "vitest";
import { Effect } from "effect";
import {
  describe,
  expect as testApiExpect,
  TestApiContext,
  createApiClient,
} from "@/tests/api";
import type { PublicProject, PublicEnvironment } from "@/db/schema";
import { toAnnotationResponse } from "@/api/annotations.handlers";
import { TEST_DATABASE_URL } from "@/tests/db";

vitestDescribe("toAnnotationResponse", () => {
  vitestIt("converts dates to ISO strings", () => {
    const now = new Date();
    const annotation = {
      id: "test-id",
      spanDbId: "span-db-id",
      traceDbId: "trace-db-id",
      spanId: "span-id",
      traceId: "trace-id",
      label: "test-label",
      reasoning: "test-reasoning",
      data: { key: "value" },
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdBy: "user-id",
      createdAt: now,
      updatedAt: now,
    };

    const result = toAnnotationResponse(annotation);

    expect(result.createdAt).toBe(now.toISOString());
    expect(result.updatedAt).toBe(now.toISOString());
  });

  vitestIt("handles null dates", () => {
    const annotation = {
      id: "test-id",
      spanDbId: "span-db-id",
      traceDbId: "trace-db-id",
      spanId: "span-id",
      traceId: "trace-id",
      label: null,
      reasoning: null,
      data: null,
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdBy: "user-id",
      createdAt: null,
      updatedAt: null,
    };

    const result = toAnnotationResponse(annotation);

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
        testApiExpect(project.id).toBeDefined();
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
        testApiExpect(environment.id).toBeDefined();
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
        ownerDeletedAt: owner.deletedAt,
      };

      const result = yield* Effect.promise(() =>
        createApiClient(TEST_DATABASE_URL, owner, apiKeyInfo),
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
      testApiExpect(result.partialSuccess).toBeDefined();
    }),
  );

  it.effect("POST /annotations - creates annotation", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.create({
        payload: {
          traceId: "0123456789abcdef0123456789abcdef",
          spanId: "0123456789abcdef",
          label: "test-label",
        },
      });
      testApiExpect(result.id).toBeDefined();
      testApiExpect(result.label).toBe("test-label");
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
          traceId: optionalTraceId,
          spanId: optionalSpanId,
          label: "test-label-full",
          reasoning: "test-reasoning",
          data: { key: "value" },
        },
      });
      testApiExpect(result.id).toBeDefined();
      testApiExpect(result.label).toBe("test-label-full");
      testApiExpect(result.reasoning).toBe("test-reasoning");
      testApiExpect(result.data).toEqual({ key: "value" });
    }),
  );

  it.effect("GET /annotations/:id - gets annotation by ID", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.get({
        path: { id: createdAnnotationId },
      });
      testApiExpect(result.id).toBe(createdAnnotationId);
      testApiExpect(result.label).toBe("test-label");
    }),
  );

  it.effect("PUT /annotations/:id - updates annotation", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.update({
        path: { id: createdAnnotationId },
        payload: {
          label: "updated-label",
          reasoning: "updated-reasoning",
        },
      });
      testApiExpect(result.id).toBe(createdAnnotationId);
      testApiExpect(result.label).toBe("updated-label");
      testApiExpect(result.reasoning).toBe("updated-reasoning");
    }),
  );

  it.effect("GET /annotations - lists annotations", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.list({
        urlParams: {},
      });
      testApiExpect(result.total).toBeGreaterThanOrEqual(1);
      testApiExpect(result.annotations.length).toBeGreaterThanOrEqual(1);
    }),
  );

  it.effect("GET /annotations - filters by label", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.list({
        urlParams: { label: "updated-label" },
      });
      testApiExpect(result.total).toBeGreaterThanOrEqual(1);
      testApiExpect(
        result.annotations.every((a) => a.label === "updated-label"),
      ).toBe(true);
    }),
  );

  it.effect("GET /annotations - filters by traceId", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.list({
        urlParams: { traceId: "0123456789abcdef0123456789abcdef" },
      });
      testApiExpect(result.total).toBeGreaterThanOrEqual(1);
      testApiExpect(
        result.annotations.every(
          (a) => a.traceId === "0123456789abcdef0123456789abcdef",
        ),
      ).toBe(true);
    }),
  );

  it.effect("GET /annotations - paginates with limit and offset", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.annotations.list({
        urlParams: { limit: 1, offset: 0 },
      });
      testApiExpect(result.annotations.length).toBeLessThanOrEqual(1);
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
          traceId: deleteTraceId,
          spanId: deleteSpanId,
          label: "to-be-deleted",
        },
      });

      yield* apiKeyClient.annotations.delete({ path: { id: created.id } });

      const list = yield* apiKeyClient.annotations.list({
        urlParams: { label: "to-be-deleted" },
      });
      testApiExpect(
        list.annotations.find((a) => a.id === created.id),
      ).toBeUndefined();
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
