import {
  describe,
  it,
  expect,
  TestEnvironmentFixture,
  TestApiKeyFixture,
  MockDrizzleORM,
} from "@/tests/db";
import { Effect } from "effect";
import { Database } from "@/db/database";
import { DatabaseError, NotFoundError, PermissionDeniedError } from "@/errors";
import type { CreateRouterRequest } from "@/db/router-requests";

describe("RouterRequests", () => {
  const createRouterRequestInput = (
    overrides: Partial<CreateRouterRequest> = {},
  ): CreateRouterRequest => ({
    provider: "anthropic",
    model: "claude-3-opus-20240229",
    status: "pending",
    ...overrides,
  });

  describe("create", () => {
    it.effect("creates router request successfully", () =>
      Effect.gen(function* () {
        const envFixture = yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create an API key first
        const apiKey =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: envFixture.owner.id,
            organizationId: envFixture.org.id,
            projectId: envFixture.project.id,
            environmentId: envFixture.environment.id,
            data: { name: "test-key" },
          });

        const input = createRouterRequestInput();

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: input,
            },
          );

        expect(result.provider).toBe("anthropic");
        expect(result.model).toBe("claude-3-opus-20240229");
        expect(result.organizationId).toBe(envFixture.org.id);
        expect(result.status).toBe("pending");
      }),
    );

    it.effect("creates router request with all optional fields", () =>
      Effect.gen(function* () {
        const envFixture = yield* TestEnvironmentFixture;
        const db = yield* Database;

        const apiKey =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: envFixture.owner.id,
            organizationId: envFixture.org.id,
            projectId: envFixture.project.id,
            environmentId: envFixture.environment.id,
            data: { name: "test-key" },
          });

        const input = createRouterRequestInput({
          requestId: "req_123",
          inputTokens: 100n,
          outputTokens: 50n,
          cacheReadTokens: 10n,
          cacheWriteTokens: 5n,
          cacheWriteBreakdown: { ephemeral5m: 5 },
          costCenticents: 12345n,
          errorMessage: null,
        });

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: input,
            },
          );

        expect(result.requestId).toBe("req_123");
        expect(result.inputTokens).toBe(100n);
        expect(result.outputTokens).toBe(50n);
        expect(result.cacheReadTokens).toBe(10n);
        expect(result.cacheWriteTokens).toBe(5n);
        expect(result.cacheWriteBreakdown).toEqual({ ephemeral5m: 5 });
        expect(result.costCenticents).toBe(12345n);
      }),
    );

    describe("authorization", () => {
      it.effect("allows OWNER role", () =>
        Effect.gen(function* () {
          const envFixture = yield* TestEnvironmentFixture;
          const db = yield* Database;

          const apiKey =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              data: { name: "test-key" },
            });

          const input = createRouterRequestInput();

          const result =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
              {
                userId: envFixture.owner.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                data: input,
              },
            );

          expect(result.provider).toBe("anthropic");
        }),
      );

      it.effect("allows ADMIN role", () =>
        Effect.gen(function* () {
          const envFixture = yield* TestEnvironmentFixture;
          const db = yield* Database;

          const apiKey =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              data: { name: "test-key" },
            });

          const input = createRouterRequestInput();

          const result =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
              {
                userId: envFixture.admin.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                data: input,
              },
            );

          expect(result.provider).toBe("anthropic");
        }),
      );

      it.effect("returns PermissionDeniedError for VIEWER role", () =>
        Effect.gen(function* () {
          const envFixture = yield* TestEnvironmentFixture;
          const db = yield* Database;

          const apiKey =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              data: { name: "test-key" },
            });

          const input = createRouterRequestInput();

          const result =
            yield* db.organizations.projects.environments.apiKeys.routerRequests
              .create({
                userId: envFixture.projectViewer.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                data: input,
              })
              .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toContain("permission to create");
        }),
      );

      it.effect("returns NotFoundError for non-member", () =>
        Effect.gen(function* () {
          const envFixture = yield* TestEnvironmentFixture;
          const db = yield* Database;

          const apiKey =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              data: { name: "test-key" },
            });

          const input = createRouterRequestInput();

          const result =
            yield* db.organizations.projects.environments.apiKeys.routerRequests
              .create({
                userId: envFixture.nonMember.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                data: input,
              })
              .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
      );
    });
  });

  describe("findAll", () => {
    it.effect("returns all router requests for organization", () =>
      Effect.gen(function* () {
        const envFixture = yield* TestEnvironmentFixture;
        const db = yield* Database;

        const apiKey1 =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: envFixture.owner.id,
            organizationId: envFixture.org.id,
            projectId: envFixture.project.id,
            environmentId: envFixture.environment.id,
            data: { name: "test-key-1" },
          });

        const apiKey2 =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: envFixture.owner.id,
            organizationId: envFixture.org.id,
            projectId: envFixture.project.id,
            environmentId: envFixture.environment.id,
            data: { name: "test-key-2" },
          });

        yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
          {
            userId: envFixture.owner.id,
            organizationId: envFixture.org.id,
            projectId: envFixture.project.id,
            environmentId: envFixture.environment.id,
            apiKeyId: apiKey1.id,
            data: createRouterRequestInput({
              provider: "anthropic",
              model: "claude-3-opus",
            }),
          },
        );

        yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
          {
            userId: envFixture.owner.id,
            organizationId: envFixture.org.id,
            projectId: envFixture.project.id,
            environmentId: envFixture.environment.id,
            apiKeyId: apiKey2.id,
            data: createRouterRequestInput({
              provider: "openai",
              model: "gpt-4",
            }),
          },
        );

        const results =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findAll(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey1.id,
            },
          );

        expect(results.length).toBe(2);
      }),
    );

    it.effect("returns empty array when no router requests exist", () =>
      Effect.gen(function* () {
        const envFixture = yield* TestEnvironmentFixture;
        const db = yield* Database;

        const apiKey =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: envFixture.owner.id,
            organizationId: envFixture.org.id,
            projectId: envFixture.project.id,
            environmentId: envFixture.environment.id,
            data: { name: "test-key" },
          });

        const results =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findAll(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
            },
          );

        expect(results.length).toBe(0);
      }),
    );

    describe("authorization", () => {
      it.effect("allows OWNER role", () =>
        Effect.gen(function* () {
          const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
          const db = yield* Database;

          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

          const results =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.findAll(
              {
                userId: envFixture.owner.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
              },
            );

          expect(results.length).toBe(1);
        }),
      );

      it.effect("allows ADMIN role", () =>
        Effect.gen(function* () {
          const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
          const db = yield* Database;

          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

          const results =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.findAll(
              {
                userId: envFixture.admin.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
              },
            );

          expect(results.length).toBe(1);
        }),
      );

      it.effect("allows VIEWER role", () =>
        Effect.gen(function* () {
          const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
          const db = yield* Database;

          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

          const results =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.findAll(
              {
                userId: envFixture.projectViewer.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
              },
            );

          expect(results.length).toBe(1);
        }),
      );

      it.effect("returns NotFoundError for non-member", () =>
        Effect.gen(function* () {
          const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
          const db = yield* Database;

          const result =
            yield* db.organizations.projects.environments.apiKeys.routerRequests
              .findAll({
                userId: envFixture.nonMember.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
              })
              .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
      );
    });
  });

  describe("findById", () => {
    it.effect("returns router request by ID", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput({
                provider: "anthropic",
                model: "claude-3-opus",
              }),
            },
          );

        const found =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: created.id,
            },
          );

        expect(found.id).toBe(created.id);
        expect(found.provider).toBe("anthropic");
        expect(found.model).toBe("claude-3-opus");
      }),
    );

    it.effect("returns NotFoundError when router request not found", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .findById({
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: "00000000-0000-0000-0000-000000000000",
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toContain("not found");
      }),
    );

    describe("authorization", () => {
      it.effect("allows OWNER role", () =>
        Effect.gen(function* () {
          const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
              {
                userId: envFixture.owner.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                data: createRouterRequestInput(),
              },
            );

          const found =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
              {
                userId: envFixture.owner.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                routerRequestId: created.id,
              },
            );

          expect(found.id).toBe(created.id);
        }),
      );

      it.effect("allows ADMIN role", () =>
        Effect.gen(function* () {
          const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
              {
                userId: envFixture.owner.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                data: createRouterRequestInput(),
              },
            );

          const found =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
              {
                userId: envFixture.admin.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                routerRequestId: created.id,
              },
            );

          expect(found.id).toBe(created.id);
        }),
      );

      it.effect("allows VIEWER role", () =>
        Effect.gen(function* () {
          const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
              {
                userId: envFixture.owner.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                data: createRouterRequestInput(),
              },
            );

          const found =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.findById(
              {
                userId: envFixture.projectViewer.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                routerRequestId: created.id,
              },
            );

          expect(found.id).toBe(created.id);
        }),
      );

      it.effect("returns NotFoundError for non-member", () =>
        Effect.gen(function* () {
          const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
              {
                userId: envFixture.owner.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                data: createRouterRequestInput(),
              },
            );

          const result =
            yield* db.organizations.projects.environments.apiKeys.routerRequests
              .findById({
                userId: envFixture.nonMember.id,
                organizationId: envFixture.org.id,
                projectId: envFixture.project.id,
                environmentId: envFixture.environment.id,
                apiKeyId: apiKey.id,
                routerRequestId: created.id,
              })
              .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
      );
    });
  });

  describe("update", () => {
    it.effect("updates router request successfully", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

        const updated =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.update(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: created.id,
              data: {
                status: "success",
                inputTokens: 100n,
                outputTokens: 50n,
                costCenticents: 12345n,
                completedAt: new Date(),
              },
            },
          );

        expect(updated.id).toBe(created.id);
        expect(updated.status).toBe("success");
        expect(updated.inputTokens).toBe(100n);
        expect(updated.outputTokens).toBe(50n);
        expect(updated.costCenticents).toBe(12345n);
      }),
    );

    it.effect("allows DEVELOPER role to update", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

        const updated =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.update(
            {
              userId: envFixture.projectDeveloper.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: created.id,
              data: { status: "success" },
            },
          );

        expect(updated.status).toBe("success");
      }),
    );

    it.effect("returns PermissionDeniedError for VIEWER role", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .update({
              userId: envFixture.projectViewer.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: created.id,
              data: { status: "success" },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission to update");
      }),
    );

    it.effect("returns NotFoundError for non-member", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .update({
              userId: envFixture.nonMember.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: created.id,
              data: { status: "success" },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );
  });

  describe("delete", () => {
    it.effect("returns PermissionDeniedError for OWNER role", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .delete({
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: created.id,
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission to delete");
      }),
    );

    it.effect("returns PermissionDeniedError for ADMIN role", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .delete({
              userId: envFixture.projectAdmin.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: created.id,
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission to delete");
      }),
    );

    it.effect("returns PermissionDeniedError for DEVELOPER role", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .delete({
              userId: envFixture.projectDeveloper.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: created.id,
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission to delete");
      }),
    );

    it.effect("returns NotFoundError for non-member", () =>
      Effect.gen(function* () {
        const { apiKey, ...envFixture } = yield* TestApiKeyFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.routerRequests.create(
            {
              userId: envFixture.owner.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              data: createRouterRequestInput(),
            },
          );

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .delete({
              userId: envFixture.nonMember.id,
              organizationId: envFixture.org.id,
              projectId: envFixture.project.id,
              environmentId: envFixture.environment.id,
              apiKeyId: apiKey.id,
              routerRequestId: created.id,
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );
  });

  describe("DatabaseError", () => {
    it.effect("returns DatabaseError when create fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              apiKeyId: "key-id",
              data: {
                provider: "anthropic",
                model: "claude-3-opus",
              },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create router request");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([{ id: "project-id" }])
            .insert(new Error("insert failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when findAll fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .findAll({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              apiKeyId: "key-id",
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all router requests");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([{ id: "project-id" }])
            .select(new Error("select failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when findById fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .findById({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              apiKeyId: "key-id",
              routerRequestId: "request-id",
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find router request");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([{ id: "project-id" }])
            .select(new Error("select failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when update fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              apiKeyId: "key-id",
              routerRequestId: "request-id",
              data: { status: "success" },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update router request");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([{ id: "project-id" }])
            .update(new Error("update failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns NotFoundError when update finds no router request", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.apiKeys.routerRequests
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              apiKeyId: "key-id",
              routerRequestId: "nonexistent-id",
              data: { status: "success" },
            })
            .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toContain("not found");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            .select([{ id: "project-id" }])
            .update([])
            .build(),
        ),
      ),
    );
  });
});
