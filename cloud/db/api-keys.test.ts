import {
  describe,
  it,
  expect,
  MockDrizzleORM,
  TestEnvironmentFixture,
} from "@/tests/db";
import { Effect } from "effect";
import { Database } from "@/db/database";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import type { PublicApiKey, ApiKeyCreateResponse } from "@/db/schema";

describe("ApiKeys", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect(
      "creates an API key and returns the plaintext key (org OWNER)",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const apiKey =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "production-key" },
            });

          expect(apiKey).toMatchObject({
            name: "production-key",
            environmentId: environment.id,
            ownerId: owner.id,
          } satisfies Partial<PublicApiKey>);
          expect(apiKey.id).toBeDefined();
          expect(apiKey.key).toBeDefined();
          expect(apiKey.key.startsWith("mk_")).toBe(true);
          expect(apiKey.keyPrefix).toBeDefined();
          expect(apiKey.keyPrefix.endsWith("...")).toBe(true);
        }),
    );

    it.effect("creates an API key (org ADMIN)", () =>
      Effect.gen(function* () {
        const { org, project, environment, admin } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const apiKey =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: admin.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "staging-key" },
          });

        expect(apiKey.name).toBe("staging-key");
        expect(apiKey.key).toBeDefined();
      }),
    );

    it.effect("creates an API key (project ADMIN)", () =>
      Effect.gen(function* () {
        const { org, project, environment, projectAdmin } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const apiKey =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: projectAdmin.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "dev-key" },
          });

        expect(apiKey.name).toBe("dev-key");
      }),
    );

    it.effect("creates an API key (project DEVELOPER)", () =>
      Effect.gen(function* () {
        const { org, project, environment, projectDeveloper } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const apiKey =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "testing-key" },
          });

        expect(apiKey.name).toBe("testing-key");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project VIEWER tries to create",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, projectViewer } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .create({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "unauthorized-key" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to create this api_key",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project ANNOTATOR tries to create",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, projectAnnotator } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .create({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "unauthorized-key" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to create (hides project)",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, nonMember } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .create({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "unauthorized-key" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when API key name is taken in same environment",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "my-key" },
          });

          const result = yield* db.organizations.projects.environments.apiKeys
            .create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "my-key" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            'An API key with name "my-key" already exists in this environment',
          );
        }),
    );

    it.effect("allows same API key name in different environments", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create API key in first environment
        const key1 =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "shared-name" },
          });

        // Create second environment
        const env2 = yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "staging", slug: "staging" },
        });

        // Create API key with same name in second environment
        const key2 =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: env2.id,
            data: { name: "shared-name" },
          });

        expect(key1.name).toBe(key2.name);
        expect(key1.id).not.toBe(key2.id);
        expect(key1.environmentId).toBe(environment.id);
        expect(key2.environmentId).toBe(env2.id);
      }),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.apiKeys
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            data: { name: "test-key" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create API key");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getMembership (via getRole)
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists
            .select([{ id: "project-id" }])
            // API key insert fails
            .insert(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("retrieves all API keys in an environment", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create API keys
        yield* db.organizations.projects.environments.apiKeys.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { name: "key-1" },
        });
        yield* db.organizations.projects.environments.apiKeys.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { name: "key-2" },
        });

        const apiKeys =
          yield* db.organizations.projects.environments.apiKeys.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(apiKeys).toHaveLength(2);
        expect(apiKeys.map((k) => k.name).sort()).toEqual(["key-1", "key-2"]);
        // Should NOT include the plaintext key
        expect((apiKeys[0] as ApiKeyCreateResponse).key).toBeUndefined();
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ANNOTATOR tries to list",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, projectAnnotator } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .findAll({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to list (hides project)",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, nonMember } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .findAll({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns empty array when environment has no API keys", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const apiKeys =
          yield* db.organizations.projects.environments.apiKeys.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(apiKeys).toHaveLength(0);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.apiKeys
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all API keys");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getMembership (via getRole)
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists
            .select([{ id: "project-id" }])
            // findAll query fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findById
  // ===========================================================================

  describe("findById", () => {
    it.effect("retrieves an API key by ID", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "my-key" },
          });

        const apiKey =
          yield* db.organizations.projects.environments.apiKeys.findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: created.id,
          });

        expect(apiKey.id).toBe(created.id);
        expect(apiKey.name).toBe("my-key");
        // Should NOT include the plaintext key
        expect((apiKey as ApiKeyCreateResponse).key).toBeUndefined();
      }),
    );

    it.effect("returns `NotFoundError` when API key doesn't exist", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.apiKeys
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "API key with apiKeyId 00000000-0000-0000-0000-000000000000 not found",
        );
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ANNOTATOR tries to get",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, projectAnnotator } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "hidden-key" },
            });

          const result = yield* db.organizations.projects.environments.apiKeys
            .findById({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to get (hides project)",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, nonMember } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "hidden-key" },
            });

          const result = yield* db.organizations.projects.environments.apiKeys
            .findById({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.apiKeys
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            apiKeyId: "key-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find API key");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getMembership (via getRole)
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists
            .select([{ id: "project-id" }])
            // findById query fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // update
  // ===========================================================================

  describe("update", () => {
    it.effect("updates an API key name", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "original-name" },
          });

        const updated =
          yield* db.organizations.projects.environments.apiKeys.update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: created.id,
            data: { name: "updated-name" },
          });

        expect(updated.name).toBe("updated-name");
        expect(updated.id).toBe(created.id);
      }),
    );

    it.effect("allows project DEVELOPER to update", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner, projectDeveloper } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "original" },
          });

        const updated =
          yield* db.organizations.projects.environments.apiKeys.update({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: created.id,
            data: { name: "updated-by-dev" },
          });

        expect(updated.name).toBe("updated-by-dev");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when VIEWER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, projectViewer } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "original" },
            });

          const result = yield* db.organizations.projects.environments.apiKeys
            .update({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: created.id,
              data: { name: "unauthorized" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this api_key",
          );
        }),
    );

    it.effect("returns `NotFoundError` when API key doesn't exist", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.apiKeys
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: "00000000-0000-0000-0000-000000000000",
            data: { name: "updated" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns `AlreadyExistsError` when new name conflicts", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        yield* db.organizations.projects.environments.apiKeys.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { name: "key-1" },
        });

        const key2 =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "key-2" },
          });

        const result = yield* db.organizations.projects.environments.apiKeys
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: key2.id,
            data: { name: "key-1" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect(result.message).toBe(
          'An API key with name "key-1" already exists in this environment',
        );
      }),
    );

    it.effect("returns `DatabaseError` when update fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.apiKeys
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            apiKeyId: "key-id",
            data: { name: "updated" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update API key");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getMembership (via getRole)
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists
            .select([{ id: "project-id" }])
            // update fails
            .update(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `NotFoundError` when update returns empty (defensive)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              apiKeyId: "key-id",
              data: { name: "updated" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("API key with apiKeyId key-id not found");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // organizationMemberships.getMembership (via getRole)
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // organizationMemberships.findById
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // verifyProjectExists
              .select([{ id: "project-id" }])
              // update returns empty array
              .update([])
              .build(),
          ),
        ),
    );
  });

  // ===========================================================================
  // delete
  // ===========================================================================

  describe("delete", () => {
    it.effect("deletes an API key", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "to-delete" },
          });

        yield* db.organizations.projects.environments.apiKeys.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          apiKeyId: created.id,
        });

        // Verify it's deleted
        const result = yield* db.organizations.projects.environments.apiKeys
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("allows DEVELOPER to delete their own API key", () =>
      Effect.gen(function* () {
        const { org, project, environment, projectDeveloper } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "developer-key" },
          });

        yield* db.organizations.projects.environments.apiKeys.delete({
          userId: projectDeveloper.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          apiKeyId: created.id,
        });

        // Verify it's deleted
        const result = yield* db.organizations.projects.environments.apiKeys
          .findById({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when DEVELOPER tries to delete another user's key",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, projectDeveloper } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "protected-key" },
            });

          const result = yield* db.organizations.projects.environments.apiKeys
            .delete({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You can only delete API keys you created",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when VIEWER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, projectViewer } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "protected-key" },
            });

          const result = yield* db.organizations.projects.environments.apiKeys
            .delete({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `NotFoundError` when API key doesn't exist (ADMIN)",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .delete({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: "00000000-0000-0000-0000-000000000000",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect(
      "returns `NotFoundError` when API key doesn't exist (DEVELOPER)",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, projectDeveloper } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .delete({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: "00000000-0000-0000-0000-000000000000",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "API key with apiKeyId 00000000-0000-0000-0000-000000000000 not found",
          );
        }),
    );

    it.effect(
      "returns `DatabaseError` when DEVELOPER ownership check fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .delete({
              userId: "developer-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              apiKeyId: "key-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to find API key");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // organizationMemberships.getMembership (via getRole) - MEMBER role
              .select([
                {
                  role: "MEMBER",
                  organizationId: "org-id",
                  memberId: "developer-id",
                  createdAt: new Date(),
                },
              ])
              // organizationMemberships.findById
              .select([
                {
                  role: "MEMBER",
                  organizationId: "org-id",
                  memberId: "developer-id",
                  createdAt: new Date(),
                },
              ])
              // projectMemberships.getMembership - DEVELOPER role
              .select([{ role: "DEVELOPER" }])
              // Fetch API key to check ownership fails
              .select(new Error("Database connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to delete (hides project)",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, nonMember } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const created =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "protected-key" },
            });

          const result = yield* db.organizations.projects.environments.apiKeys
            .delete({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              apiKeyId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.apiKeys
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            apiKeyId: "key-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete API key");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.getMembership (via getRole)
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists
            .select([{ id: "project-id" }])
            // delete fails
            .delete(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `NotFoundError` when delete returns empty (defensive)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .delete({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              apiKeyId: "key-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("API key with apiKeyId key-id not found");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // organizationMemberships.getMembership (via getRole)
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // organizationMemberships.findById
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // verifyProjectExists
              .select([{ id: "project-id" }])
              // delete returns empty array
              .delete([])
              .build(),
          ),
        ),
    );
  });

  // ===========================================================================
  // getApiKeyInfo
  // ===========================================================================

  describe("getApiKeyInfo", () => {
    it.effect("gets complete API key info including owner details", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "info-test-key" },
          });

        const result =
          yield* db.organizations.projects.environments.apiKeys.getApiKeyInfo(
            created.key,
          );

        expect(result.apiKeyId).toBe(created.id);
        expect(result.environmentId).toBe(environment.id);
        expect(result.projectId).toBe(project.id);
        expect(result.organizationId).toBe(org.id);
        expect(result.ownerId).toBe(owner.id);
        expect(result.ownerEmail).toBe(owner.email);
        expect(result.ownerName).toBe(owner.name);
        expect(result.ownerDeletedAt).toBe(owner.deletedAt);
      }),
    );

    it.effect("updates lastUsedAt timestamp when getting info", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "timestamp-test-key" },
          });

        // Get the API key info
        yield* db.organizations.projects.environments.apiKeys.getApiKeyInfo(
          created.key,
        );

        // Check the lastUsedAt was updated
        const apiKey =
          yield* db.organizations.projects.environments.apiKeys.findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            apiKeyId: created.id,
          });

        expect(apiKey.lastUsedAt).not.toBeNull();
      }),
    );

    it.effect("returns `NotFoundError` for invalid API key", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create a valid key first to ensure there's data in the table
        yield* db.organizations.projects.environments.apiKeys.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { name: "real-key" },
        });

        const result = yield* db.organizations.projects.environments.apiKeys
          .getApiKeyInfo("mk_invalid_key_that_does_not_exist")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Invalid API key or owner not found");
      }),
    );

    it.effect("returns `NotFoundError` when owner doesn't exist", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create an API key
        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "orphan-key" },
          });

        // Delete the owner user (simulate deleted user)
        yield* db.users.delete({ userId: owner.id });

        // Try to get API key info - should fail because owner doesn't exist
        const result = yield* db.organizations.projects.environments.apiKeys
          .getApiKeyInfo(created.key)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Invalid API key or owner not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.apiKeys
          .getApiKeyInfo("mk_test_key")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get API key info");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getApiKeyInfo query fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when lastUsedAt update fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.apiKeys
          .getApiKeyInfo("mk_test_key")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe(
          "Failed to update API key last used timestamp",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getApiKeyInfo query succeeds
            .select([
              {
                apiKeyId: "key-id",
                environmentId: "env-id",
                projectId: "proj-id",
                organizationId: "org-id",
                ownerId: "owner-id",
                ownerName: "Owner Name",
              },
            ])
            // lastUsedAt update fails
            .update(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // getRole (delegation to project memberships)
  // ===========================================================================

  describe("getRole", () => {
    it.effect("delegates to projectMemberships.getRole", () =>
      Effect.gen(function* () {
        const { org, project, owner, projectDeveloper } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Owner has implicit ADMIN
        const ownerRole =
          yield* db.organizations.projects.environments.apiKeys.getRole({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
          });
        expect(ownerRole).toBe("ADMIN");

        // Developer has explicit DEVELOPER role
        const devRole =
          yield* db.organizations.projects.environments.apiKeys.getRole({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
          });
        expect(devRole).toBe("DEVELOPER");
      }),
    );
  });

  // ===========================================================================
  // findAllForOrganization
  // ===========================================================================

  describe("findAllForOrganization", () => {
    it.effect(
      "org OWNER can see all API keys across all projects/environments",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          // Create API key in the first environment
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "key-1" },
          });

          // Create second project and environment
          const project2 = yield* db.organizations.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "project-2", slug: "project-2" },
          });
          const env2 = yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project2.id,
            data: { name: "env-2", slug: "env-2" },
          });

          // Create API key in second project
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project2.id,
            environmentId: env2.id,
            data: { name: "key-2" },
          });

          const apiKeys =
            yield* db.organizations.projects.environments.apiKeys.findAllForOrganization(
              {
                userId: owner.id,
                organizationId: org.id,
              },
            );

          expect(apiKeys).toHaveLength(2);
          expect(apiKeys.map((k) => k.name).sort()).toEqual(["key-1", "key-2"]);
          // Should include project and environment context
          expect(apiKeys[0].projectName).toBeDefined();
          expect(apiKeys[0].environmentName).toBeDefined();
          expect(apiKeys[0].projectId).toBeDefined();
        }),
    );

    it.effect(
      "org ADMIN can see all API keys across all projects/environments",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, admin } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          // Create API key as owner
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "admin-visible-key" },
          });

          // Admin should see the key
          const apiKeys =
            yield* db.organizations.projects.environments.apiKeys.findAllForOrganization(
              {
                userId: admin.id,
                organizationId: org.id,
              },
            );

          expect(apiKeys).toHaveLength(1);
          expect(apiKeys[0].name).toBe("admin-visible-key");
        }),
    );

    it.effect(
      "project DEVELOPER only sees API keys in projects they have access to",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, projectDeveloper } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          // Create API key in the accessible project
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "accessible-key" },
          });

          // Create second project WITHOUT adding the developer
          const project2 = yield* db.organizations.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "private-project", slug: "private-project" },
          });
          const env2 = yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project2.id,
            data: { name: "private-env", slug: "private-env" },
          });

          // Create API key in the private project
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project2.id,
            environmentId: env2.id,
            data: { name: "private-key" },
          });

          // Developer should only see the accessible key
          const apiKeys =
            yield* db.organizations.projects.environments.apiKeys.findAllForOrganization(
              {
                userId: projectDeveloper.id,
                organizationId: org.id,
              },
            );

          expect(apiKeys).toHaveLength(1);
          expect(apiKeys[0].name).toBe("accessible-key");
        }),
    );

    it.effect(
      "project VIEWER cannot see API keys (no ADMIN/DEVELOPER role)",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, projectViewer } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          // Create API key
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "viewer-cannot-see" },
          });

          // Viewer should not see any keys (they don't have ADMIN or DEVELOPER role)
          const apiKeys =
            yield* db.organizations.projects.environments.apiKeys.findAllForOrganization(
              {
                userId: projectViewer.id,
                organizationId: org.id,
              },
            );

          expect(apiKeys).toHaveLength(0);
        }),
    );

    it.effect(
      "returns empty array when non-admin user has no ADMIN/DEVELOPER projects",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, owner, projectAnnotator } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          // Create API key in the project
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "annotator-cannot-see" },
          });

          // Annotator has no ADMIN/DEVELOPER role so should see no keys
          const apiKeys =
            yield* db.organizations.projects.environments.apiKeys.findAllForOrganization(
              {
                userId: projectAnnotator.id,
                organizationId: org.id,
              },
            );

          expect(apiKeys).toHaveLength(0);
        }),
    );

    it.effect(
      "returns `NotFoundError` when user is not an organization member",
      () =>
        Effect.gen(function* () {
          const { org, nonMember } = yield* TestEnvironmentFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .findAllForOrganization({
              userId: nonMember.id,
              organizationId: org.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Organization not found");
        }),
    );

    it.effect(
      "returns `DatabaseError` when organization membership check fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .findAllForOrganization({
              userId: "user-id",
              organizationId: "org-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe(
            "Failed to check organization membership",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // Organization membership check fails
              .select(new Error("Database connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when project membership query fails (non-admin)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .findAllForOrganization({
              userId: "member-id",
              organizationId: "org-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get user project memberships");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // Organization membership check succeeds with MEMBER role
              .select([{ role: "MEMBER" }])
              // Project membership query fails
              .select(new Error("Database connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when API keys query fails (org admin)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .findAllForOrganization({
              userId: "owner-id",
              organizationId: "org-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe(
            "Failed to find API keys for organization",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // Organization membership check succeeds with OWNER role
              .select([{ role: "OWNER" }])
              // API keys query fails
              .select(new Error("Database connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when project memberships query fails (non-admin)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .findAllForOrganization({
              userId: "developer-id",
              organizationId: "org-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get user project memberships");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // Mock order follows client.select() CREATION order, not execution order:
              // 1. org membership, 2. baseQuery (API keys), 3. project memberships
              // But EXECUTION order for non-admin is: 1, 3, 2
              .select([{ role: "MEMBER" }]) // mock 0: org membership succeeds
              .select([]) // mock 1: baseQuery - won't be reached
              .select(new Error("Database connection failed")) // mock 2: project memberships fails
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when API keys query fails (non-admin with accessible projects)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.apiKeys
            .findAllForOrganization({
              userId: "developer-id",
              organizationId: "org-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe(
            "Failed to find API keys for organization",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // Mock order follows client.select() CREATION order, not execution order:
              // 1. org membership, 2. baseQuery (API keys), 3. project memberships
              // But EXECUTION order for non-admin is: 1, 3, 2
              .select([{ role: "MEMBER" }]) // mock 0: org membership succeeds
              .select(new Error("Database connection failed")) // mock 1: baseQuery fails
              .select([{ projectId: "project-1" }]) // mock 2: project memberships succeeds
              .build(),
          ),
        ),
    );
  });
});
