import { Effect, Schema } from "effect";

import type {
  PublicApiKey,
  ApiKeyCreateResponse,
  ApiKeyWithContext,
  PublicProject,
  PublicEnvironment,
} from "@/db/schema";

import {
  toApiKey,
  toApiKeyCreateResponse,
  toApiKeyWithContext,
} from "@/api/api-keys.handlers";
import { CreateApiKeyRequestSchema } from "@/api/api-keys.schemas";
import { describe, it, expect, TestApiContext } from "@/tests/api";

describe("toApiKey helper", () => {
  it("should convert dates to ISO strings", () => {
    const date = new Date("2025-01-01T00:00:00.000Z");
    const apiKey: PublicApiKey = {
      id: "test-id",
      name: "test-key",
      keyPrefix: "mk_abc...",
      environmentId: "env-id",
      ownerId: "user-id",
      createdAt: date,
      lastUsedAt: date,
      deletedAt: null,
    };

    const result = toApiKey(apiKey);

    expect(result.createdAt).toBe("2025-01-01T00:00:00.000Z");
    expect(result.lastUsedAt).toBe("2025-01-01T00:00:00.000Z");
    expect(result.ownerId).toBe("user-id");
  });

  it("should handle null dates", () => {
    const apiKey: PublicApiKey = {
      id: "test-id",
      name: "test-key",
      keyPrefix: "mk_abc...",
      environmentId: "env-id",
      ownerId: "user-id",
      createdAt: null,
      lastUsedAt: null,
      deletedAt: null,
    };

    const result = toApiKey(apiKey);

    expect(result.createdAt).toBeNull();
    expect(result.lastUsedAt).toBeNull();
  });
});

describe("toApiKeyCreateResponse helper", () => {
  it("should convert dates to ISO strings", () => {
    const date = new Date("2025-01-01T00:00:00.000Z");
    const apiKey: ApiKeyCreateResponse = {
      id: "test-id",
      name: "test-key",
      keyPrefix: "mk_abc...",
      environmentId: "env-id",
      ownerId: "user-id",
      createdAt: date,
      lastUsedAt: date,
      deletedAt: null,
      key: "mk_secret_key",
    };

    const result = toApiKeyCreateResponse(apiKey);

    expect(result.createdAt).toBe("2025-01-01T00:00:00.000Z");
    expect(result.lastUsedAt).toBe("2025-01-01T00:00:00.000Z");
    expect(result.ownerId).toBe("user-id");
    expect(result.key).toBe("mk_secret_key");
  });

  it("should handle null dates", () => {
    const apiKey: ApiKeyCreateResponse = {
      id: "test-id",
      name: "test-key",
      keyPrefix: "mk_abc...",
      environmentId: "env-id",
      ownerId: "user-id",
      createdAt: null,
      lastUsedAt: null,
      deletedAt: null,
      key: "mk_secret_key",
    };

    const result = toApiKeyCreateResponse(apiKey);

    expect(result.createdAt).toBeNull();
    expect(result.lastUsedAt).toBeNull();
    expect(result.key).toBe("mk_secret_key");
  });
});

describe("toApiKeyWithContext helper", () => {
  it("should convert dates to ISO strings", () => {
    const date = new Date("2025-01-01T00:00:00.000Z");
    const apiKey: ApiKeyWithContext = {
      id: "test-id",
      name: "test-key",
      keyPrefix: "mk_abc...",
      environmentId: "env-id",
      ownerId: "user-id",
      createdAt: date,
      lastUsedAt: date,
      deletedAt: null,
      projectId: "project-id",
      projectName: "My Project",
      environmentName: "production",
    };

    const result = toApiKeyWithContext(apiKey);

    expect(result.createdAt).toBe("2025-01-01T00:00:00.000Z");
    expect(result.lastUsedAt).toBe("2025-01-01T00:00:00.000Z");
    expect(result.projectId).toBe("project-id");
    expect(result.projectName).toBe("My Project");
    expect(result.environmentName).toBe("production");
  });

  it("should handle null dates", () => {
    const apiKey: ApiKeyWithContext = {
      id: "test-id",
      name: "test-key",
      keyPrefix: "mk_abc...",
      environmentId: "env-id",
      ownerId: "user-id",
      createdAt: null,
      lastUsedAt: null,
      deletedAt: null,
      projectId: "project-id",
      projectName: "My Project",
      environmentName: "production",
    };

    const result = toApiKeyWithContext(apiKey);

    expect(result.createdAt).toBeNull();
    expect(result.lastUsedAt).toBeNull();
  });
});

describe("CreateApiKeyRequestSchema validation", () => {
  it("rejects empty name", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreateApiKeyRequestSchema)({ name: "" }),
    ).toThrow("API key name is required");
  });

  it("rejects name > 100 chars", () => {
    const longName = "a".repeat(101);
    expect(() =>
      Schema.decodeUnknownSync(CreateApiKeyRequestSchema)({ name: longName }),
    ).toThrow("API key name must be at most 100 characters");
  });

  it("accepts valid name", () => {
    const result = Schema.decodeUnknownSync(CreateApiKeyRequestSchema)({
      name: "valid-api-key-name",
    });
    expect(result.name).toBe("valid-api-key-name");
  });
});

describe.sequential("API Keys API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;
  let createdApiKeyId: string;

  it.effect(
    "POST /organizations/:organizationId/projects - create project for api key tests",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: {
            name: "API Keys Test Project",
            slug: "api-keys-test-project",
          },
        });
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects/:projectId/environments - create environment for api key tests",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "development", slug: "development" },
        });
        expect(environment.id).toBeDefined();
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/api-keys - list all api keys for org (initially empty)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const apiKeys = yield* client.apiKeys.listAllForOrg({
          path: { organizationId: org.id },
        });
        expect(Array.isArray(apiKeys)).toBe(true);
        expect(apiKeys).toHaveLength(0);
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/projects/:projectId/environments/:environmentId/api-keys - list api keys (initially empty)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const apiKeys = yield* client.apiKeys.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
        });
        expect(Array.isArray(apiKeys)).toBe(true);
        expect(apiKeys).toHaveLength(0);
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects/:projectId/environments/:environmentId/api-keys - create api key",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const apiKey = yield* client.apiKeys.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          payload: { name: "my-api-key" },
        });

        expect(apiKey.name).toBe("my-api-key");
        expect(apiKey.environmentId).toBe(environment.id);
        expect(apiKey.id).toBeDefined();
        // The key should be returned on create
        expect(apiKey.key).toBeDefined();
        expect(apiKey.key.startsWith("mk_")).toBe(true);
        // The keyPrefix should be a truncated version
        expect(apiKey.keyPrefix).toBeDefined();
        expect(apiKey.keyPrefix.endsWith("...")).toBe(true);

        createdApiKeyId = apiKey.id;
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects/:projectId/environments/:environmentId/api-keys - rejects empty name",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.apiKeys
          .create({
            path: {
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            },
            payload: { name: "" },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("ParseError");
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects/:projectId/environments/:environmentId/api-keys - rejects name > 100 chars",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const longName = "a".repeat(101);
        const result = yield* client.apiKeys
          .create({
            path: {
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            },
            payload: { name: longName },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("ParseError");
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/projects/:projectId/environments/:environmentId/api-keys - list api keys (after create)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const apiKeys = yield* client.apiKeys.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
        });
        expect(apiKeys).toHaveLength(1);
        expect(apiKeys[0].id).toBe(createdApiKeyId);
        expect(apiKeys[0].name).toBe("my-api-key");
        // The plaintext key should NOT be returned on list
        expect((apiKeys[0] as { key?: string }).key).toBeUndefined();
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/api-keys - list all api keys for org (after create)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const apiKeys = yield* client.apiKeys.listAllForOrg({
          path: { organizationId: org.id },
        });
        expect(apiKeys).toHaveLength(1);
        expect(apiKeys[0].id).toBe(createdApiKeyId);
        expect(apiKeys[0].name).toBe("my-api-key");
        // Should include project and environment context
        expect(apiKeys[0].projectId).toBe(project.id);
        expect(apiKeys[0].projectName).toBe("API Keys Test Project");
        expect(apiKeys[0].environmentId).toBe(environment.id);
        expect(apiKeys[0].environmentName).toBe("development");
        // The plaintext key should NOT be returned
        expect((apiKeys[0] as { key?: string }).key).toBeUndefined();
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/projects/:projectId/environments/:environmentId/api-keys/:apiKeyId - get api key",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const apiKey = yield* client.apiKeys.get({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: createdApiKeyId,
          },
        });

        expect(apiKey.id).toBe(createdApiKeyId);
        expect(apiKey.name).toBe("my-api-key");
        expect(apiKey.environmentId).toBe(environment.id);
        // The plaintext key should NOT be returned on get
        expect((apiKey as { key?: string }).key).toBeUndefined();
      }),
  );

  it.effect(
    "DELETE /organizations/:organizationId/projects/:projectId/environments/:environmentId/api-keys/:apiKeyId - delete api key",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client.apiKeys.delete({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: createdApiKeyId,
          },
        });

        // Verify it's gone by listing
        const apiKeys = yield* client.apiKeys.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
        });
        const found = apiKeys.find((k) => k.id === createdApiKeyId);
        expect(found).toBeUndefined();
      }),
  );

  it.effect(
    "DELETE /organizations/:organizationId/projects/:projectId/environments/:environmentId - cleanup environment",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client.environments.delete({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
        });
      }),
  );

  it.effect(
    "DELETE /organizations/:organizationId/projects/:projectId - cleanup project",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client.projects.delete({
          path: { organizationId: org.id, projectId: project.id },
        });
      }),
  );
});
