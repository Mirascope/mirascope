import { describe as vitestDescribe, it as vitestIt, expect } from "vitest";
import { Effect } from "effect";
import {
  describe,
  expect as testApiExpect,
  TestApiContext,
  it,
} from "@/tests/api";
import type { PublicProject, PublicEnvironment } from "@/db/schema";
import { toPublicFunction, toFunctionResponse } from "@/api/functions.handlers";
import { AuthenticatedApiKey, AuthenticatedUser } from "@/auth";
import {
  sdkRegisterFunctionHandler,
  sdkGetFunctionByHashHandler,
  sdkGetFunctionHandler,
  sdkListFunctionsHandler,
} from "@/api/functions.handlers";
import { Database } from "@/db";

// =============================================================================
// API Route Tests (using TestApiContext with hierarchical paths)
// =============================================================================

describe.sequential("Functions API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;

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

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments/:envId/functions - registers function",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.functions.register({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
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

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments/:envId/functions - registers function with optional fields",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.functions.register({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          payload: {
            code: "def test_func_with_meta(): return 'hello'",
            hash: `api-test-hash-meta-${Date.now()}`,
            signature: "def test_func_with_meta() -> str",
            signatureHash: "api-sig-hash-meta",
            name: "test_func_with_meta",
            description: "A test function with metadata",
            tags: ["test", "api"],
            metadata: { source: "api-test" },
            dependencies: { numpy: { version: "1.0.0", extras: ["full"] } },
          },
        });
        testApiExpect(result.id).toBeDefined();
        testApiExpect(result.name).toBe("test_func_with_meta");
        testApiExpect(result.description).toBe("A test function with metadata");
        testApiExpect(result.tags).toEqual(["test", "api"]);
        testApiExpect(result.metadata).toEqual({ source: "api-test" });
        testApiExpect(result.dependencies).toEqual({
          numpy: { version: "1.0.0", extras: ["full"] },
        });
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/functions - lists functions",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.functions.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          urlParams: {},
        });
        testApiExpect(result.total).toBeGreaterThanOrEqual(1);
        testApiExpect(result.functions.length).toBeGreaterThanOrEqual(1);
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/functions - filters by name",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.functions.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          urlParams: { name: "test_func" },
        });
        testApiExpect(result.total).toBeGreaterThanOrEqual(1);
        testApiExpect(
          result.functions.every((f) => f.name === "test_func"),
        ).toBe(true);
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/functions - filters by tags",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.functions.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          urlParams: { tags: "api" },
        });
        testApiExpect(result.total).toBeGreaterThanOrEqual(1);
        testApiExpect(
          result.functions.every((f) => f.tags?.includes("api")),
        ).toBe(true);
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/functions - paginates with limit and offset",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.functions.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          urlParams: { limit: 1, offset: 0 },
        });
        testApiExpect(result.functions.length).toBeLessThanOrEqual(1);
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/functions/:functionId - gets function by ID",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;

        // First create a function to get
        const created = yield* client.functions.register({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          payload: {
            code: "def get_by_id_func(): pass",
            hash: `get-by-id-hash-${Date.now()}`,
            signature: "def get_by_id_func() -> None",
            signatureHash: "get-by-id-sig-hash",
            name: "get_by_id_func",
          },
        });

        const result = yield* client.functions.get({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            id: created.id,
          },
        });

        testApiExpect(result.id).toBe(created.id);
        testApiExpect(result.name).toBe("get_by_id_func");
      }),
  );

  it.effect(
    "GET /organizations/:orgId/projects/:projId/environments/:envId/functions/by-hash/:hash - gets function by hash",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const uniqueHash = `get-by-hash-api-${Date.now()}`;

        // First create a function to get
        yield* client.functions.register({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          payload: {
            code: "def get_by_hash_func(): pass",
            hash: uniqueHash,
            signature: "def get_by_hash_func() -> None",
            signatureHash: "get-by-hash-sig-hash",
            name: "get_by_hash_func",
          },
        });

        const result = yield* client.functions.getByHash({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            hash: uniqueHash,
          },
        });

        testApiExpect(result.hash).toBe(uniqueHash);
        testApiExpect(result.name).toBe("get_by_hash_func");
      }),
  );
});

// =============================================================================
// Utility Function Tests (pure functions, no database required)
// =============================================================================

vitestDescribe("Utility Functions", () => {
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
  });
});

// =============================================================================
// SDK Handler Tests (requires Database context)
// =============================================================================

describe("SDK Functions Handler", () => {
  const mockOwner = {
    id: "test-owner-id",
    email: "test@example.com",
    name: "Test Owner",
    deletedAt: null,
  };

  it.effect(
    "sdkRegisterFunctionHandler - registers function with API key auth",
    () =>
      Effect.gen(function* () {
        const db = yield* Database;

        // Create test user
        const owner = yield* db.users.create({
          data: {
            email: `sdk-fn-test-${Date.now()}@example.com`,
            name: "SDK Functions Test User",
          },
        });

        // Create test organization
        const org = yield* db.organizations.create({
          userId: owner.id,
          data: {
            name: "SDK Functions Test Org",
            slug: `sdk-fn-org-${Date.now()}`,
          },
        });

        // Create test project
        const project = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "SDK Functions Test Project", slug: "sdk-fn-project" },
        });

        // Create test environment
        const environment =
          yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "SDK Functions Test Env", slug: "sdk-fn-env" },
          });

        // Create API key
        const createdApiKey =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "SDK Functions Test API Key" },
          });

        // Construct ApiKeyInfo
        const apiKeyInfo = {
          apiKeyId: createdApiKey.id,
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
          ownerId: owner.id,
          ownerEmail: owner.email,
          ownerName: owner.name,
          ownerImageUrl: null,
          ownerDeletedAt: null,
        };

        const payload = {
          code: "def my_function(): pass",
          hash: `test-hash-${Date.now()}`,
          signature: "def my_function(): ...",
          signatureHash: `sig-hash-${Date.now()}`,
          name: "my_function",
          description: "Test function",
          tags: ["test"],
          metadata: { key: "value" },
        };

        // Call SDK handler with API key context
        const result = yield* sdkRegisterFunctionHandler(payload).pipe(
          Effect.provideService(AuthenticatedUser, owner),
          Effect.provideService(AuthenticatedApiKey, apiKeyInfo),
        );

        expect(result.id).toBeDefined();
        expect(result.name).toBe("my_function");
        expect(result.hash).toBe(payload.hash);
        expect(result.isNew).toBe(true);

        // Test getByHash
        const byHash = yield* sdkGetFunctionByHashHandler(payload.hash).pipe(
          Effect.provideService(AuthenticatedUser, owner),
          Effect.provideService(AuthenticatedApiKey, apiKeyInfo),
        );
        expect(byHash.id).toBe(result.id);

        // Test get
        const byId = yield* sdkGetFunctionHandler(result.id).pipe(
          Effect.provideService(AuthenticatedUser, owner),
          Effect.provideService(AuthenticatedApiKey, apiKeyInfo),
        );
        expect(byId.id).toBe(result.id);

        // Test list
        const listResult = yield* sdkListFunctionsHandler({}).pipe(
          Effect.provideService(AuthenticatedUser, owner),
          Effect.provideService(AuthenticatedApiKey, apiKeyInfo),
        );
        expect(listResult.total).toBeGreaterThan(0);
        expect(listResult.functions.some((f) => f.id === result.id)).toBe(true);

        // Cleanup
        yield* db.organizations.delete({
          organizationId: org.id,
          userId: owner.id,
        });
        yield* db.users.delete({ userId: owner.id });
      }),
  );

  it.effect(
    "sdkRegisterFunctionHandler - fails without API key auth (UnauthorizedError)",
    () =>
      Effect.gen(function* () {
        const payload = {
          code: "def test(): pass",
          hash: "test-hash",
          signature: "def test(): ...",
          signatureHash: "sig-hash",
          name: "test",
        };

        // Call SDK handler without API key context - should fail
        const error = yield* sdkRegisterFunctionHandler(payload).pipe(
          Effect.provideService(AuthenticatedUser, mockOwner),
          Effect.flip,
        );

        expect(error._tag).toBe("UnauthorizedError");
        expect(error.message).toBe("API key required for this endpoint");
      }),
  );
});
