import {
  describe,
  it,
  expect,
  MockDrizzleORM,
  TestEffectEnvironmentFixture,
} from "@/tests/db";
import { Effect } from "effect";
import { EffectDatabase } from "@/db/database";
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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
          data: { name: "staging" },
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
        const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
        const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
        const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
        const db = yield* EffectDatabase;

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
          const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
          const db = yield* EffectDatabase;

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
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

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
        const db = yield* EffectDatabase;

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
          const db = yield* EffectDatabase;

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
  // verifyApiKey
  // ===========================================================================

  describe("verifyApiKey", () => {
    it.effect("verifies a valid API key", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "verify-test-key" },
          });

        const result =
          yield* db.organizations.projects.environments.apiKeys.verifyApiKey(
            created.key,
          );

        expect(result.apiKeyId).toBe(created.id);
        expect(result.environmentId).toBe(environment.id);
      }),
    );

    it.effect("updates lastUsedAt timestamp on verification", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

        const created =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "timestamp-test-key" },
          });

        // Verify the key
        yield* db.organizations.projects.environments.apiKeys.verifyApiKey(
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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

        // Create a valid key first to ensure there's data in the table
        yield* db.organizations.projects.environments.apiKeys.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { name: "real-key" },
        });

        const result = yield* db.organizations.projects.environments.apiKeys
          .verifyApiKey("mk_invalid_key_that_does_not_exist")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Invalid API key");
      }),
    );

    it.effect("returns `DatabaseError` when verification query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.organizations.projects.environments.apiKeys
          .verifyApiKey("mk_test_key")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to verify API key");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // verifyApiKey query fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when lastUsedAt update fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.organizations.projects.environments.apiKeys
          .verifyApiKey("mk_test_key")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe(
          "Failed to update API key last used timestamp",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // verifyApiKey query succeeds
            .select([{ id: "key-id", environmentId: "env-id" }])
            // lastUsedAt update fails
            .update(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // getCreator
  // ===========================================================================

  describe("getCreator", () => {
    it.effect("returns the user who created the API key (org OWNER)", () =>
      Effect.gen(function* () {
        const { org, project, environment, owner } =
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

        // Create an API key as owner
        const apiKey =
          yield* db.organizations.projects.environments.apiKeys.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { name: "owner-key" },
          });

        // Get the creator
        const creator =
          yield* db.organizations.projects.environments.apiKeys.getCreator(
            apiKey.id,
          );

        expect(creator.id).toBe(owner.id);
        expect(creator.email).toBe(owner.email);
        expect(creator.name).toBe(owner.name);
      }),
    );

    it.effect(
      "returns the user who created the API key (project DEVELOPER)",
      () =>
        Effect.gen(function* () {
          const { org, project, environment, projectDeveloper } =
            yield* TestEffectEnvironmentFixture;
          const db = yield* EffectDatabase;

          // Create an API key as developer
          const apiKey =
            yield* db.organizations.projects.environments.apiKeys.create({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: { name: "developer-key" },
            });

          // Get the creator
          const creator =
            yield* db.organizations.projects.environments.apiKeys.getCreator(
              apiKey.id,
            );

          expect(creator.id).toBe(projectDeveloper.id);
          expect(creator.email).toBe(projectDeveloper.email);
          expect(creator.name).toBe(projectDeveloper.name);
        }),
    );

    it.effect("returns `NotFoundError` for non-existent API key", () =>
      Effect.gen(function* () {
        yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

        // Use a valid UUID format that doesn't exist
        const nonExistentId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.organizations.projects.environments.apiKeys
          .getCreator(nonExistentId)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(`API key ${nonExistentId} not found`);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.organizations.projects.environments.apiKeys
          .getCreator("some-key-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get API key creator");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select(new Error("Database connection failed"))
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
          yield* TestEffectEnvironmentFixture;
        const db = yield* EffectDatabase;

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
});
