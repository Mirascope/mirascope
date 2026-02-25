import { Effect } from "effect";

import type { PublicProject, PublicEnvironment } from "@/db/schema";

import { toFunction } from "@/api/functions.handlers";
import {
  describe,
  it,
  expect,
  TestApiContext,
  createApiClient,
} from "@/tests/api";
import { TEST_DATABASE_URL } from "@/tests/db";

describe("toFunction", () => {
  it("converts dates to ISO strings", () => {
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
      language: "python",
      dependencies: null,
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdAt: now,
      updatedAt: now,
    };

    const result = toFunction(fn);

    expect(result.createdAt).toBe(now.toISOString());
    expect(result.updatedAt).toBe(now.toISOString());
  });

  it("handles null dates", () => {
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
      language: "python",
      dependencies: null,
      environmentId: "env-id",
      projectId: "project-id",
      organizationId: "org-id",
      createdAt: null,
      updatedAt: null,
    };

    const result = toFunction(fn);

    expect(result.createdAt).toBeNull();
    expect(result.updatedAt).toBeNull();
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
        expect(project.id).toBeDefined();
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
        expect(environment.id).toBeDefined();
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

  it.effect("POST /functions - creates function", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.functions.create({
        payload: {
          code: "def test_func(): pass",
          hash: `api-test-hash-${Date.now()}`,
          signature: "def test_func() -> None",
          signatureHash: "api-sig-hash",
          name: "test_func",
          language: "python",
        },
      });
      expect(result.id).toBeDefined();
      expect(result.name).toBe("test_func");
    }),
  );

  it.effect("POST /functions - creates function with optional fields", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.functions.create({
        payload: {
          code: "def test_func_with_meta(): return 'hello'",
          hash: `api-test-hash-meta-${Date.now()}`,
          signature: "def test_func_with_meta() -> str",
          signatureHash: "api-sig-hash-meta",
          name: "test_func_with_meta",
          language: "python",
          description: "A test function with metadata",
          tags: ["test", "api"],
          metadata: { source: "api-test" },
          dependencies: {
            numpy: { version: "1.0.0", extras: ["full"] },
            pandas: { version: "2.0.0", extras: null },
          },
        },
      });
      expect(result.id).toBeDefined();
      expect(result.name).toBe("test_func_with_meta");
      expect(result.description).toBe("A test function with metadata");
      expect(result.tags).toEqual(["test", "api"]);
      expect(result.metadata).toEqual({ source: "api-test" });
      expect(result.dependencies).toEqual({
        numpy: { version: "1.0.0", extras: ["full"] },
        pandas: { version: "2.0.0", extras: null },
      });
    }),
  );

  it.effect("GET /functions - lists functions", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.functions.list({});
      expect(result.total).toBeGreaterThanOrEqual(1);
      expect(result.functions.length).toBeGreaterThanOrEqual(1);
    }),
  );

  it.effect("GET /functions/:functionId - gets function by ID", () =>
    Effect.gen(function* () {
      const created = yield* apiKeyClient.functions.create({
        payload: {
          code: "def get_by_id_func(): pass",
          hash: `get-by-id-hash-${Date.now()}`,
          signature: "def get_by_id_func() -> None",
          signatureHash: "get-by-id-sig-hash",
          name: "get_by_id_func",
          language: "python",
        },
      });

      const result = yield* apiKeyClient.functions.get({
        path: { id: created.id },
      });

      expect(result.id).toBe(created.id);
      expect(result.name).toBe("get_by_id_func");
    }),
  );

  it.effect("GET /functions/hash/:hash - gets function by hash", () =>
    Effect.gen(function* () {
      const uniqueHash = `get-by-hash-api-${Date.now()}`;

      yield* apiKeyClient.functions.create({
        payload: {
          code: "def get_by_hash_func(): pass",
          hash: uniqueHash,
          signature: "def get_by_hash_func() -> None",
          signatureHash: "get-by-hash-sig-hash",
          name: "get_by_hash_func",
          language: "python",
        },
      });

      const result = yield* apiKeyClient.functions.findByHash({
        path: { hash: uniqueHash },
      });

      expect(result.hash).toBe(uniqueHash);
      expect(result.name).toBe("get_by_hash_func");
    }),
  );

  it.effect("DELETE /functions/:functionId - deletes function", () =>
    Effect.gen(function* () {
      const created = yield* apiKeyClient.functions.create({
        payload: {
          code: "def delete_me(): pass",
          hash: `delete-test-hash-${Date.now()}`,
          signature: "def delete_me() -> None",
          signatureHash: "delete-sig-hash",
          name: "delete_me",
          language: "python",
        },
      });

      yield* apiKeyClient.functions.delete({
        path: { id: created.id },
      });

      // Verify function is deleted by trying to get it
      const result = yield* apiKeyClient.functions
        .get({
          path: { id: created.id },
        })
        .pipe(Effect.flip);

      expect(result._tag).toBe("NotFoundError");
    }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/functions/:functionId - gets function by env (session auth)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;

        // Create a function first using API key client
        const created = yield* apiKeyClient.functions.create({
          payload: {
            code: "def get_by_env_func(): pass",
            hash: `get-by-env-hash-${Date.now()}`,
            signature: "def get_by_env_func() -> None",
            signatureHash: "get-by-env-sig-hash",
            name: "get_by_env_func",
            language: "python",
          },
        });

        // Use session-authenticated client to get the function via getByEnv endpoint
        const result = yield* client.functions.getByEnv({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            functionId: created.id,
          },
        });

        expect(result.id).toBe(created.id);
        expect(result.name).toBe("get_by_env_func");
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/functions - lists functions by env (session auth)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;

        // Use session-authenticated client to list functions via listByEnv endpoint
        const result = yield* client.functions.listByEnv({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
        });

        expect(result.total).toBeGreaterThanOrEqual(1);
        expect(result.functions.length).toBeGreaterThanOrEqual(1);
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
