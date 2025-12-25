import { Effect } from "effect";
import { describe, expect, TestApiContext, it } from "@/tests/api";
import type { PublicProject, PublicEnvironment } from "@/db/schema";
import { AuthenticatedApiKey, AuthenticatedUser } from "@/auth";
import { sdkCreateTraceHandler } from "@/api/traces.handlers";
import { Database } from "@/db";

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

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments/:envId/traces - creates trace",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
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

        const result = yield* client.traces.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          payload,
        });

        expect(result.partialSuccess).toBeDefined();
      }),
  );
});

// SDK Traces Handler Unit Tests (requires Database context)
describe("SDK Traces Handler", () => {
  const mockOwner = {
    id: "test-owner-id",
    email: "test@example.com",
    name: "Test Owner",
    deletedAt: null,
  };

  it.effect("sdkCreateTraceHandler - creates trace with API key auth", () =>
    Effect.gen(function* () {
      const db = yield* Database;

      // Create test user
      const owner = yield* db.users.create({
        data: {
          email: `sdk-test-${Date.now()}@example.com`,
          name: "SDK Test User",
        },
      });

      // Create test organization
      const org = yield* db.organizations.create({
        userId: owner.id,
        data: { name: "SDK Test Org", slug: `sdk-test-org-${Date.now()}` },
      });

      // Create test project
      const project = yield* db.organizations.projects.create({
        userId: owner.id,
        organizationId: org.id,
        data: { name: "SDK Test Project", slug: "sdk-test-project" },
      });

      // Create test environment
      const environment = yield* db.organizations.projects.environments.create({
        userId: owner.id,
        organizationId: org.id,
        projectId: project.id,
        data: { name: "SDK Test Environment", slug: "sdk-test-env" },
      });

      // Create API key
      const createdApiKey =
        yield* db.organizations.projects.environments.apiKeys.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { name: "SDK Test API Key" },
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
        resourceSpans: [
          {
            resource: {
              attributes: [
                {
                  key: "service.name",
                  value: { stringValue: "sdk-test-service" },
                },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "sdk-test-scope", version: "1.0.0" },
                spans: [
                  {
                    traceId: "sdk-trace-handler-test",
                    spanId: "sdk-span-handler-test",
                    name: "sdk-test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ],
      };

      // Call SDK handler with API key context
      const result = yield* sdkCreateTraceHandler(payload).pipe(
        Effect.provideService(AuthenticatedUser, owner),
        Effect.provideService(AuthenticatedApiKey, apiKeyInfo),
      );

      expect(result.partialSuccess).toBeDefined();

      // Cleanup
      yield* db.organizations.delete({
        organizationId: org.id,
        userId: owner.id,
      });
      yield* db.users.delete({ userId: owner.id });
    }),
  );

  it.effect(
    "sdkCreateTraceHandler - fails without API key auth (UnauthorizedError)",
    () =>
      Effect.gen(function* () {
        const payload = {
          resourceSpans: [
            {
              scopeSpans: [
                {
                  spans: [
                    {
                      traceId: "test",
                      spanId: "test",
                      name: "test",
                      startTimeUnixNano: "1000000000",
                      endTimeUnixNano: "2000000000",
                    },
                  ],
                },
              ],
            },
          ],
        };

        // Call SDK handler without API key context - should fail
        const error = yield* sdkCreateTraceHandler(payload).pipe(
          Effect.provideService(AuthenticatedUser, mockOwner),
          Effect.flip,
        );

        expect(error._tag).toBe("UnauthorizedError");
        expect(error.message).toBe("API key required for this endpoint");
      }),
  );
});
