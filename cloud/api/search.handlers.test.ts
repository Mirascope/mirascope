import { Effect, Layer } from "effect";
import { describe, expect, TestApiContext, createApiClient } from "@/tests/api";
import type {
  ApiKeyInfo,
  PublicEnvironment,
  PublicProject,
  PublicUser,
} from "@/db/schema";
import { TEST_DATABASE_URL } from "@/tests/db";
import { Authentication } from "@/auth";
import { ClickHouseSearchService } from "@/clickhouse/search";
import { ClickHouse } from "@/clickhouse/client";
import { SettingsService, getSettings } from "@/settings";
import { searchHandler } from "@/api/search.handlers";

describe.sequential("Search API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;
  let apiKeyClient: Awaited<ReturnType<typeof createApiClient>>["client"];
  let disposeApiKeyClient: (() => Promise<void>) | null = null;
  let apiKeyInfo: ApiKeyInfo | undefined;
  let ownerFromContext: PublicUser | null = null;

  it.effect(
    "POST /organizations/:orgId/projects - create project for search test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Search Test Project", slug: "search-test-project" },
        });
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments - create environment for search test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: {
            name: "Search Test Environment",
            slug: "search-test-env",
          },
        });
        expect(environment.id).toBeDefined();
      }),
  );

  it.effect("Create API key client for search tests", () =>
    Effect.gen(function* () {
      const { org, owner } = yield* TestApiContext;
      apiKeyInfo = {
        apiKeyId: "test-search-api-key-id",
        organizationId: org.id,
        projectId: project.id,
        environmentId: environment.id,
        ownerId: owner.id,
        ownerEmail: owner.email,
        ownerName: owner.name,
        ownerDeletedAt: owner.deletedAt,
      };
      ownerFromContext = owner;

      const result = yield* Effect.promise(() =>
        createApiClient(TEST_DATABASE_URL, owner, apiKeyInfo),
      );
      apiKeyClient = result.client;
      disposeApiKeyClient = result.dispose;
    }),
  );

  it.effect("POST /search - returns empty results for new environment", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.search.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
        },
      });

      expect(result.spans).toBeDefined();
      expect(Array.isArray(result.spans)).toBe(true);
      expect(typeof result.total).toBe("number");
      expect(typeof result.hasMore).toBe("boolean");
    }),
  );

  it.effect("POST /search - with query filter", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.search.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          query: "test",
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect("POST /search - with model filter", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.search.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          model: ["gpt-4"],
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect("POST /search - with provider filter", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.search.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          provider: ["openai"],
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect("POST /search - with pagination", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.search.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          limit: 10,
          offset: 0,
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect("POST /search - with sorting", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.search.search({
        payload: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          sortBy: "duration_ms",
          sortOrder: "desc",
        },
      });

      expect(result.spans).toBeDefined();
    }),
  );

  it.effect(
    "searchHandler supports optional filters and maps attributeFilters",
    () =>
      Effect.gen(function* () {
        const settings = getSettings();
        const settingsLayer = Layer.succeed(SettingsService, {
          ...settings,
          env: "test",
        });

        if (!apiKeyInfo || !ownerFromContext) {
          throw new Error("Missing API key context for search handler test");
        }

        const authenticationLayer = Layer.succeed(Authentication, {
          user: ownerFromContext,
          apiKeyInfo,
        });

        const clickHouseClientLayer = ClickHouse.Default.pipe(
          Layer.provide(settingsLayer),
        );
        const clickHouseSearchLayer = ClickHouseSearchService.Default.pipe(
          Layer.provide(clickHouseClientLayer),
        );

        const result = yield* searchHandler({
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          attributeFilters: [
            {
              key: "span.type",
              operator: "eq",
              value: "server",
            },
          ],
        }).pipe(
          Effect.provide(
            Layer.mergeAll(authenticationLayer, clickHouseSearchLayer),
          ),
        );

        expect(result.spans).toBeDefined();
        expect(typeof result.total).toBe("number");
      }),
  );

  it.effect(
    "GET /search/traces/:traceId - returns empty for non-existent trace",
    () =>
      Effect.gen(function* () {
        const result = yield* apiKeyClient.search.getTraceDetail({
          path: { traceId: "non-existent-trace-id" },
        });

        expect(result.traceId).toBe("non-existent-trace-id");
        expect(result.spans).toEqual([]);
      }),
  );

  it.effect("GET /search/analytics - returns analytics summary", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.search.getAnalyticsSummary({
        urlParams: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
        },
      });

      expect(typeof result.totalSpans).toBe("number");
      expect(typeof result.errorRate).toBe("number");
      expect(typeof result.totalTokens).toBe("number");
      expect(typeof result.totalCostUsd).toBe("number");
      expect(Array.isArray(result.topModels)).toBe(true);
      expect(Array.isArray(result.topFunctions)).toBe(true);
    }),
  );

  it.effect("GET /search/analytics - with functionId filter", () =>
    Effect.gen(function* () {
      const result = yield* apiKeyClient.search.getAnalyticsSummary({
        urlParams: {
          startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          endTime: new Date().toISOString(),
          functionId: "00000000-0000-0000-0000-000000000001",
        },
      });

      expect(typeof result.totalSpans).toBe("number");
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
