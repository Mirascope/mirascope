import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import { withTestClientDb } from "@/tests/api";
import { toApiKey, toApiKeyCreateResponse } from "@/api/api-keys.handlers";
import type { PublicApiKey, ApiKeyCreateResponse } from "@/db/schema";

describe("toApiKey helper", () => {
  it("should convert dates to ISO strings", () => {
    const date = new Date("2025-01-01T00:00:00.000Z");
    const apiKey: PublicApiKey = {
      id: "test-id",
      name: "test-key",
      keyPrefix: "mk_abc...",
      environmentId: "env-id",
      createdAt: date,
      lastUsedAt: date,
    };

    const result = toApiKey(apiKey);

    expect(result.createdAt).toBe("2025-01-01T00:00:00.000Z");
    expect(result.lastUsedAt).toBe("2025-01-01T00:00:00.000Z");
  });

  it("should handle null dates", () => {
    const apiKey: PublicApiKey = {
      id: "test-id",
      name: "test-key",
      keyPrefix: "mk_abc...",
      environmentId: "env-id",
      createdAt: null,
      lastUsedAt: null,
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
      createdAt: date,
      lastUsedAt: date,
      key: "mk_secret_key",
    };

    const result = toApiKeyCreateResponse(apiKey);

    expect(result.createdAt).toBe("2025-01-01T00:00:00.000Z");
    expect(result.lastUsedAt).toBe("2025-01-01T00:00:00.000Z");
    expect(result.key).toBe("mk_secret_key");
  });

  it("should handle null dates", () => {
    const apiKey: ApiKeyCreateResponse = {
      id: "test-id",
      name: "test-key",
      keyPrefix: "mk_abc...",
      environmentId: "env-id",
      createdAt: null,
      lastUsedAt: null,
      key: "mk_secret_key",
    };

    const result = toApiKeyCreateResponse(apiKey);

    expect(result.createdAt).toBeNull();
    expect(result.lastUsedAt).toBeNull();
    expect(result.key).toBe("mk_secret_key");
  });
});

describe("API Keys API", () => {
  it(
    "GET /organizations/:orgId/projects/:projectId/environments/:envId/api-keys - list api keys",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({
          payload: { name: "List ApiKey Test Org" },
        }),
      );

      const project = await Effect.runPromise(
        client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Test Project" },
        }),
      );

      // Get the default development environment
      const environments = await Effect.runPromise(
        client.environments.list({
          path: { organizationId: org.id, projectId: project.id },
        }),
      );
      const devEnv = environments[0];

      // Create an API key
      await Effect.runPromise(
        client.apiKeys.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: devEnv.id,
          },
          payload: { name: "test-key" },
        }),
      );

      const apiKeys = await Effect.runPromise(
        client.apiKeys.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: devEnv.id,
          },
        }),
      );

      expect(Array.isArray(apiKeys)).toBe(true);
      expect(apiKeys).toHaveLength(1);
      expect(apiKeys[0].name).toBe("test-key");
    }),
  );

  it(
    "POST /organizations/:orgId/projects/:projectId/environments/:envId/api-keys - create api key",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({
          payload: { name: "Create ApiKey Test Org" },
        }),
      );

      const project = await Effect.runPromise(
        client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Test Project" },
        }),
      );

      const environments = await Effect.runPromise(
        client.environments.list({
          path: { organizationId: org.id, projectId: project.id },
        }),
      );
      const devEnv = environments[0];

      const apiKey = await Effect.runPromise(
        client.apiKeys.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: devEnv.id,
          },
          payload: { name: "my-api-key" },
        }),
      );

      expect(apiKey.name).toBe("my-api-key");
      expect(apiKey.environmentId).toBe(devEnv.id);
      expect(apiKey.id).toBeDefined();
      // The key should be returned on create
      expect(apiKey.key).toBeDefined();
      expect(apiKey.key.startsWith("mk_")).toBe(true);
      // The keyPrefix should be a truncated version
      expect(apiKey.keyPrefix).toBeDefined();
      expect(apiKey.keyPrefix.endsWith("...")).toBe(true);
    }),
  );

  it(
    "GET /organizations/:orgId/projects/:projectId/environments/:envId/api-keys/:apiKeyId - get api key",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({
          payload: { name: "Get ApiKey Test Org" },
        }),
      );

      const project = await Effect.runPromise(
        client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Test Project" },
        }),
      );

      const environments = await Effect.runPromise(
        client.environments.list({
          path: { organizationId: org.id, projectId: project.id },
        }),
      );
      const devEnv = environments[0];

      const created = await Effect.runPromise(
        client.apiKeys.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: devEnv.id,
          },
          payload: { name: "my-api-key" },
        }),
      );

      const apiKey = await Effect.runPromise(
        client.apiKeys.get({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: devEnv.id,
            apiKeyId: created.id,
          },
        }),
      );

      expect(apiKey.id).toBe(created.id);
      expect(apiKey.name).toBe("my-api-key");
      expect(apiKey.environmentId).toBe(devEnv.id);
      // The key should NOT be returned on get, only on create
      expect((apiKey as { key?: string }).key).toBeUndefined();
    }),
  );

  it(
    "DELETE /organizations/:orgId/projects/:projectId/environments/:envId/api-keys/:apiKeyId - delete api key",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({
          payload: { name: "Delete ApiKey Test Org" },
        }),
      );

      const project = await Effect.runPromise(
        client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Test Project" },
        }),
      );

      const environments = await Effect.runPromise(
        client.environments.list({
          path: { organizationId: org.id, projectId: project.id },
        }),
      );
      const devEnv = environments[0];

      const created = await Effect.runPromise(
        client.apiKeys.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: devEnv.id,
          },
          payload: { name: "to-delete-key" },
        }),
      );

      await Effect.runPromise(
        client.apiKeys.delete({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: devEnv.id,
            apiKeyId: created.id,
          },
        }),
      );

      // Verify it's gone by listing
      const apiKeys = await Effect.runPromise(
        client.apiKeys.list({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: devEnv.id,
          },
        }),
      );
      const found = apiKeys.find((k) => k.id === created.id);
      expect(found).toBeUndefined();
    }),
  );
});
