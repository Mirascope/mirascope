import { Effect } from "effect";

import type { PublicProject, PublicEnvironment } from "@/db/schema";

import { toTag } from "@/api/tags.handlers";
import {
  describe,
  it,
  expect,
  TestApiContext,
  createApiClient,
} from "@/tests/api";
import { TEST_DATABASE_URL } from "@/tests/db";

describe("toTag", () => {
  it("converts dates to ISO strings", () => {
    const now = new Date();
    const tag = {
      id: "test-id",
      name: "Bug",
      projectId: "project-id",
      organizationId: "org-id",
      createdBy: "user-id",
      createdAt: now,
      updatedAt: now,
    };

    const result = toTag(tag);

    expect(result.createdAt).toBe(now.toISOString());
    expect(result.updatedAt).toBe(now.toISOString());
  });

  it("handles null dates", () => {
    const tag = {
      id: "test-id",
      name: "Bug",
      projectId: "project-id",
      organizationId: "org-id",
      createdBy: null,
      createdAt: null,
      updatedAt: null,
    };

    const result = toTag(tag);

    expect(result.createdAt).toBeNull();
    expect(result.updatedAt).toBeNull();
  });
});

describe.sequential("Tags API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;
  let apiKeyClient: Awaited<ReturnType<typeof createApiClient>>["client"];
  let disposeApiKeyClient: (() => Promise<void>) | null = null;
  let createdTagId: string;

  it.effect(
    "POST /organizations/:orgId/projects - create project for tags",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: {
            name: "Tags Test Project",
            slug: "tags-test-project",
          },
        });
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments - create environment for tags",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: {
            name: "Tags Test Environment",
            slug: "tags-test-env",
          },
        });
        expect(environment.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/tags - creates tag",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.tags.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "Bug" },
        });
        expect(result.id).toBeDefined();
        expect(result.name).toBe("Bug");
        createdTagId = result.id;
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/tags - lists tags",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.tags.list({
          path: { organizationId: org.id, projectId: project.id },
        });
        expect(result.total).toBeGreaterThanOrEqual(1);
        expect(result.tags.length).toBeGreaterThanOrEqual(1);
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/tags/:tagId - gets tag",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.tags.get({
          path: {
            organizationId: org.id,
            projectId: project.id,
            tagId: createdTagId,
          },
        });
        expect(result.id).toBe(createdTagId);
        expect(result.name).toBe("Bug");
      }),
  );

  it.effect(
    "PUT /organizations/:orgId/projects/:projId/tags/:tagId - updates tag",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.tags.update({
          path: {
            organizationId: org.id,
            projectId: project.id,
            tagId: createdTagId,
          },
          payload: { name: "Bugfix" },
        });
        expect(result.id).toBe(createdTagId);
        expect(result.name).toBe("Bugfix");
      }),
  );

  it.effect("Create API key client for tags API key tests", () =>
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
        ),
      );
      apiKeyClient = result.client;
      disposeApiKeyClient = result.dispose;
    }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/tags - creates tag via API key",
    () =>
      Effect.gen(function* () {
        const { org } = yield* TestApiContext;
        const result = yield* apiKeyClient.tags.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "ApiKeyTag" },
        });
        expect(result.id).toBeDefined();
        expect(result.name).toBe("ApiKeyTag");
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/tags - lists tags via API key",
    () =>
      Effect.gen(function* () {
        const { org } = yield* TestApiContext;
        const result = yield* apiKeyClient.tags.list({
          path: { organizationId: org.id, projectId: project.id },
        });
        expect(result.total).toBeGreaterThanOrEqual(1);
        expect(result.tags.length).toBeGreaterThanOrEqual(1);
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/tags/:tagId - gets tag via API key",
    () =>
      Effect.gen(function* () {
        const { org } = yield* TestApiContext;
        const created = yield* apiKeyClient.tags.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "ApiKeyGet" },
        });

        const result = yield* apiKeyClient.tags.get({
          path: {
            organizationId: org.id,
            projectId: project.id,
            tagId: created.id,
          },
        });

        expect(result.id).toBe(created.id);
        expect(result.name).toBe("ApiKeyGet");
      }),
  );

  it.effect(
    "PUT /organizations/:orgId/projects/:projId/tags/:tagId - updates tag via API key",
    () =>
      Effect.gen(function* () {
        const { org } = yield* TestApiContext;
        const created = yield* apiKeyClient.tags.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "ApiKeyUpdate" },
        });

        const result = yield* apiKeyClient.tags.update({
          path: {
            organizationId: org.id,
            projectId: project.id,
            tagId: created.id,
          },
          payload: { name: "ApiKeyUpdated" },
        });

        expect(result.id).toBe(created.id);
        expect(result.name).toBe("ApiKeyUpdated");
      }),
  );

  it.effect(
    "DELETE /organizations/:orgId/projects/:projId/tags/:tagId - deletes tag via API key",
    () =>
      Effect.gen(function* () {
        const { org } = yield* TestApiContext;
        const created = yield* apiKeyClient.tags.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "ApiKeyDelete" },
        });

        yield* apiKeyClient.tags.delete({
          path: {
            organizationId: org.id,
            projectId: project.id,
            tagId: created.id,
          },
        });

        const result = yield* apiKeyClient.tags
          .get({
            path: {
              organizationId: org.id,
              projectId: project.id,
              tagId: created.id,
            },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("NotFoundError");
      }),
  );

  it.effect(
    "DELETE /organizations/:orgId/projects/:projId/tags/:tagId - deletes tag",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client.tags.delete({
          path: {
            organizationId: org.id,
            projectId: project.id,
            tagId: createdTagId,
          },
        });

        const result = yield* client.tags
          .get({
            path: {
              organizationId: org.id,
              projectId: project.id,
              tagId: createdTagId,
            },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("NotFoundError");
      }),
  );

  it.effect("Dispose API key client", () =>
    Effect.gen(function* () {
      if (!disposeApiKeyClient) {
        return;
      }

      const dispose = disposeApiKeyClient;
      yield* Effect.promise(() => dispose());
    }),
  );
});
