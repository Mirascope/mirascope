import { describe as vitestDescribe, it as vitestIt, expect } from "vitest";
import { Effect } from "effect";
import {
  describe,
  expect as testApiExpect,
  TestApiContext,
  createApiClient,
} from "@/tests/api";
import type { PublicProject, PublicEnvironment } from "@/db/schema";
import { toPublicFunction, toFunctionResponse } from "@/api/functions.handlers";
import { TEST_DATABASE_URL } from "@/tests/db";

vitestDescribe("toPublicFunction", () => {
  vitestIt("converts dates to ISO strings", () => {
    const now = new Date();
    const fn = {
      id: "test-id",
      hash: "test-hash",
      signatureHash: "sig-hash",
      name: "test",
      description: null,
      version: "1.0",
      tags: null,
      metadata: null,
      code: "def test(): pass",
      signature: "def test() -> None",
      dependencies: null,
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdAt: now,
      updatedAt: now,
    };

    const result = toPublicFunction(fn);

    expect(result.createdAt).toBe(now.toISOString());
    expect(result.updatedAt).toBe(now.toISOString());
  });

  vitestIt("handles null dates", () => {
    const fn = {
      id: "test-id",
      hash: "test-hash",
      signatureHash: "sig-hash",
      name: "test",
      description: null,
      version: "1.0",
      tags: null,
      metadata: null,
      code: "def test(): pass",
      signature: "def test() -> None",
      dependencies: null,
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdAt: null,
      updatedAt: null,
    };

    const result = toPublicFunction(fn);

    expect(result.createdAt).toBeNull();
    expect(result.updatedAt).toBeNull();
  });
});

vitestDescribe("toFunctionResponse", () => {
  vitestIt("converts dates to ISO strings with isNew field", () => {
    const now = new Date();
    const fn = {
      id: "test-id",
      hash: "test-hash",
      signatureHash: "sig-hash",
      name: "test",
      description: null,
      version: "1.0",
      tags: null,
      metadata: null,
      code: "def test(): pass",
      signature: "def test() -> None",
      dependencies: null,
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdAt: now,
      updatedAt: now,
      isNew: true,
    };

    const result = toFunctionResponse(fn);

    expect(result.createdAt).toBe(now.toISOString());
    expect(result.updatedAt).toBe(now.toISOString());
    expect(result.isNew).toBe(true);
  });

  vitestIt("handles null dates", () => {
    const fn = {
      id: "test-id",
      hash: "test-hash",
      signatureHash: "sig-hash",
      name: "test",
      description: null,
      version: "1.0",
      tags: null,
      metadata: null,
      code: "def test(): pass",
      signature: "def test() -> None",
      dependencies: null,
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdAt: null,
      updatedAt: null,
      isNew: false,
    };

    const result = toFunctionResponse(fn);

    expect(result.createdAt).toBeNull();
    expect(result.updatedAt).toBeNull();
    expect(result.isNew).toBe(false);
  });
});

describe.sequential("Functions API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;
  let apiKeyClient: Awaited<ReturnType<typeof createApiClient>>["client"];
  let disposeApiKeyClient: (() => Promise<void>) | null = null;

  it.effect(
    "POST /organizations/:orgId/projects - create project for functions test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: {
            name: "Functions Test Project",
            slug: "functions-test-project",
          },
        });
        testApiExpect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments - create environment for functions test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: {
            name: "Functions Test Environment",
            slug: "functions-test-env",
          },
        });
        testApiExpect(environment.id).toBeDefined();
      }),
  );

  it.effect("Create API key client for functions tests", () =>
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

  it.effect("POST /functions - registers function", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.functions.register({
        payload: {
          code: "def test_func(): pass",
          hash: `api-test-hash-${Date.now()}`,
          signature: "def test_func() -> None",
          signatureHash: "api-sig-hash",
          name: "test_func",
        },
      });
      testApiExpect(result.id).toBeDefined();
      testApiExpect(result.name).toBe("test_func");
      testApiExpect(result.isNew).toBe(true);
    }),
  );

  it.effect("POST /functions - registers function with optional fields", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.functions.register({
        payload: {
          code: "def test_func_with_meta(): return 'hello'",
          hash: `api-test-hash-meta-${Date.now()}`,
          signature: "def test_func_with_meta() -> str",
          signatureHash: "api-sig-hash-meta",
          name: "test_func_with_meta",
          description: "A test function with metadata",
          tags: ["test", "api"],
          metadata: { source: "api-test" },
          dependencies: {
            numpy: { version: "1.0.0", extras: ["full"] },
            pandas: { version: "2.0.0", extras: null },
          },
        },
      });
      testApiExpect(result.id).toBeDefined();
      testApiExpect(result.name).toBe("test_func_with_meta");
      testApiExpect(result.description).toBe("A test function with metadata");
      testApiExpect(result.tags).toEqual(["test", "api"]);
      testApiExpect(result.metadata).toEqual({ source: "api-test" });
      testApiExpect(result.dependencies).toEqual({
        numpy: { version: "1.0.0", extras: ["full"] },
        pandas: { version: "2.0.0", extras: null },
      });
    }),
  );

  it.effect("GET /functions - lists functions", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.functions.list({
        urlParams: {},
      });
      testApiExpect(result.total).toBeGreaterThanOrEqual(1);
      testApiExpect(result.functions.length).toBeGreaterThanOrEqual(1);
    }),
  );

  it.effect("GET /functions - filters by name", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.functions.list({
        urlParams: { name: "test_func" },
      });
      testApiExpect(result.total).toBeGreaterThanOrEqual(1);
      testApiExpect(result.functions.every((f) => f.name === "test_func")).toBe(
        true,
      );
    }),
  );

  it.effect("GET /functions - filters by tags", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.functions.list({
        urlParams: { tags: "api" },
      });
      testApiExpect(result.total).toBeGreaterThanOrEqual(1);
      testApiExpect(
        result.functions.every((f) => f.tags?.includes("api")),
      ).toBe(true);
    }),
  );

  it.effect("GET /functions - paginates with limit and offset", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.functions.list({
        urlParams: { limit: 1, offset: 0 },
      });
      testApiExpect(result.functions.length).toBeLessThanOrEqual(1);
    }),
  );

  it.effect("GET /functions/:functionId - gets function by ID", () =>
    Effect.gen(function* () {
      const created = yield* apiKeyClient.functions.register({
        payload: {
          code: "def get_by_id_func(): pass",
          hash: `get-by-id-hash-${Date.now()}`,
          signature: "def get_by_id_func() -> None",
          signatureHash: "get-by-id-sig-hash",
          name: "get_by_id_func",
        },
      });

      const result = yield* apiKeyClient.functions.get({
        path: { id: created.id },
      });

      testApiExpect(result.id).toBe(created.id);
      testApiExpect(result.name).toBe("get_by_id_func");
    }),
  );

  it.effect("GET /functions/by-hash/:hash - gets function by hash", () =>
    Effect.gen(function* () {
      const uniqueHash = `get-by-hash-api-${Date.now()}`;

      yield* apiKeyClient.functions.register({
        payload: {
          code: "def get_by_hash_func(): pass",
          hash: uniqueHash,
          signature: "def get_by_hash_func() -> None",
          signatureHash: "get-by-hash-sig-hash",
          name: "get_by_hash_func",
        },
      });

      const result = yield* apiKeyClient.functions.getByHash({
        path: { hash: uniqueHash },
      });

      testApiExpect(result.hash).toBe(uniqueHash);
      testApiExpect(result.name).toBe("get_by_hash_func");
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
