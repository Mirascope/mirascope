import { describe as vitestDescribe, it as vitestIt, expect } from "vitest";
import { Effect } from "effect";
import { describe, expect as testApiExpect, TestApiContext } from "@/tests/api";
import type { PublicProject, PublicEnvironment } from "@/db/schema";
import { toAnnotationResponse } from "@/api/annotations.handlers";

// =============================================================================
// API Route Tests (using TestApiContext with hierarchical paths)
// =============================================================================

describe.sequential("Annotations API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;
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

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments/:envId/traces - create trace for annotations test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.traces.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
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

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments/:envId/annotations - creates annotation",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.annotations.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
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

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments/:envId/annotations - creates annotation with optional fields",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.annotations.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          payload: {
            traceId: "0123456789abcdef0123456789abcdef",
            spanId: "0123456789abcdef",
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

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/annotations/:id - gets annotation by ID",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.annotations.get({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            id: createdAnnotationId,
          },
        });
        testApiExpect(result.id).toBe(createdAnnotationId);
        testApiExpect(result.label).toBe("test-label");
      }),
  );

  it.effect(
    "PUT /organizations/:orgId/projects/:projId/environments/:envId/annotations/:id - updates annotation",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.annotations.update({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            id: createdAnnotationId,
          },
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

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/annotations - lists annotations",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.annotations.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          urlParams: {},
        });
        testApiExpect(result.total).toBeGreaterThanOrEqual(1);
        testApiExpect(result.annotations.length).toBeGreaterThanOrEqual(1);
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/annotations - filters by label",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.annotations.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          urlParams: { label: "updated-label" },
        });
        testApiExpect(result.total).toBeGreaterThanOrEqual(1);
        testApiExpect(
          result.annotations.every((a) => a.label === "updated-label"),
        ).toBe(true);
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/annotations - filters by traceId",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.annotations.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
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

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/annotations - paginates with limit and offset",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.annotations.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          urlParams: { limit: 1, offset: 0 },
        });
        testApiExpect(result.annotations.length).toBeLessThanOrEqual(1);
      }),
  );

  it.effect(
    "DELETE /organizations/:orgId/projects/:projId/environments/:envId/annotations/:id - deletes annotation",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        // Create a new annotation to delete
        const created = yield* client.annotations.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          payload: {
            traceId: "0123456789abcdef0123456789abcdef",
            spanId: "0123456789abcdef",
            label: "to-be-deleted",
          },
        });

        yield* client.annotations.delete({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            id: created.id,
          },
        });

        // Verify deletion - list should not contain this annotation
        const list = yield* client.annotations.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          urlParams: { label: "to-be-deleted" },
        });
        testApiExpect(
          list.annotations.find((a) => a.id === created.id),
        ).toBeUndefined();
      }),
  );
});

// =============================================================================
// Utility Function Tests (pure functions, no database required)
// =============================================================================

vitestDescribe("Utility Functions", () => {
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
});
