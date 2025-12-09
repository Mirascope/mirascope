import { Effect } from "effect";
import { describe, expect, TestApiContext, createApiClient } from "@/tests/api";
import type { PublicProject, PublicEnvironment } from "@/db/schema";
import { TEST_DATABASE_URL } from "@/tests/db";

describe.sequential("Traces API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;

  it.effect(
    "POST /organizations/:orgId/projects - create project for traces test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Traces Test Project", slug: "traces-test-project" },
        });
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments - create environment for traces test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "Traces Test Environment", slug: "traces-test-env" },
        });
        expect(environment.id).toBeDefined();
      }),
  );

  it.effect("POST /traces - creates trace", () =>
    Effect.gen(function* () {
      const { org, owner } = yield* TestApiContext;
      const payload = {
        resourceSpans: [
          {
            resource: {
              attributes: [
                {
                  key: "service.name",
                  value: {
                    stringValue: "test-service",
                  },
                },
              ],
            },
            scopeSpans: [
              {
                scope: {
                  name: "test-scope",
                  version: "1.0.0",
                },
                spans: [
                  {
                    traceId: "test-trace-id",
                    spanId: "test-span-id",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ],
      };

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

      const { client: apiKeyClient, dispose } = yield* Effect.promise(() =>
        createApiClient(TEST_DATABASE_URL, owner, apiKeyInfo),
      );

      let result;
      try {
        result = yield* apiKeyClient.traces.create({ payload });
      } finally {
        yield* Effect.promise(dispose);
      }

      expect(result.partialSuccess).toBeDefined();
    }),
  );

  it.effect("POST /traces - returns partialSuccess on rejected spans", () =>
    Effect.gen(function* () {
      const { org, owner } = yield* TestApiContext;
      const payload = {
        resourceSpans: [
          {
            resource: {
              attributes: [
                {
                  key: "service.name",
                  value: {
                    stringValue: "duplicate-span-service",
                  },
                },
              ],
            },
            scopeSpans: [
              {
                scope: {
                  name: "test-scope",
                  version: "1.0.0",
                },
                spans: [
                  {
                    traceId: "duplicate-trace-id",
                    spanId: "duplicate-span-id",
                    name: "duplicate-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                  {
                    traceId: "duplicate-trace-id",
                    spanId: "duplicate-span-id",
                    name: "duplicate-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ],
      };

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

      const { client: apiKeyClient, dispose } = yield* Effect.promise(() =>
        createApiClient(TEST_DATABASE_URL, owner, apiKeyInfo),
      );

      let result;
      try {
        result = yield* apiKeyClient.traces.create({ payload });
      } finally {
        yield* Effect.promise(dispose);
      }

      expect(result.partialSuccess?.rejectedSpans).toBe(1);
      expect(result.partialSuccess?.errorMessage).toContain("1 spans");
    }),
  );
});
