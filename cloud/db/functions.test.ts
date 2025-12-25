import {
  describe,
  it,
  expect,
  TestEnvironmentFixture,
  MockDrizzleORM,
} from "@/tests/db";
import { Effect } from "effect";
import { Database } from "@/db";
import type { RegisterFunctionInput } from "@/db/functions";
import { DatabaseError, NotFoundError, PermissionDeniedError } from "@/errors";

// =============================================================================
// Functions class tests
// =============================================================================

describe("Functions", () => {
  // Helper to create a basic function input
  const createFunctionInput = (
    overrides: Partial<RegisterFunctionInput> = {},
  ): RegisterFunctionInput => ({
    code: 'def my_func(): return "hello"',
    hash: `hash-${Math.random().toString(36).slice(2)}`,
    signature: "def my_func() -> str",
    signatureHash: "sig-hash-1",
    name: "my_func",
    ...overrides,
  });

  describe("create", () => {
    describe("versioning", () => {
      it.effect("new function gets version 1.0", () =>
        Effect.gen(function* () {
          const { environment, project, org, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const input = createFunctionInput({ name: "new_func" });

          const result =
            yield* db.organizations.projects.environments.functions.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: input,
            });

          expect(result.version).toBe("1.0");
          expect(result.isNew).toBe(true);
          expect(result.name).toBe("new_func");
        }),
      );

      it.effect("same hash returns existing function", () =>
        Effect.gen(function* () {
          const { environment, project, org, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const input = createFunctionInput({ hash: "same-hash-123" });

          // First registration
          const first =
            yield* db.organizations.projects.environments.functions.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: input,
            });

          expect(first.isNew).toBe(true);

          // Second registration with same hash
          const second =
            yield* db.organizations.projects.environments.functions.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: input,
            });

          expect(second.isNew).toBe(false);
          expect(second.id).toBe(first.id);
        }),
      );

      it.effect("same signatureHash gets minor version bump", () =>
        Effect.gen(function* () {
          const { environment, project, org, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const funcName = "versioned_func_minor";
          const signatureHash = "same-sig-hash";

          // First version
          const v1 =
            yield* db.organizations.projects.environments.functions.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: createFunctionInput({
                name: funcName,
                signatureHash,
                hash: "hash-v1",
                code: "version 1",
              }),
            });

          expect(v1.version).toBe("1.0");

          // Second version - same signature, different implementation
          const v2 =
            yield* db.organizations.projects.environments.functions.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: createFunctionInput({
                name: funcName,
                signatureHash,
                hash: "hash-v2",
                code: "version 2",
              }),
            });

          expect(v2.version).toBe("1.1");
        }),
      );

      it.effect("different signatureHash gets major version bump", () =>
        Effect.gen(function* () {
          const { environment, project, org, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const funcName = "versioned_func_major";

          // First version
          const v1 =
            yield* db.organizations.projects.environments.functions.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: createFunctionInput({
                name: funcName,
                signatureHash: "sig-v1",
                hash: "hash-major-v1",
              }),
            });

          expect(v1.version).toBe("1.0");

          // Second version - different signature
          const v2 =
            yield* db.organizations.projects.environments.functions.create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: createFunctionInput({
                name: funcName,
                signatureHash: "sig-v2",
                hash: "hash-major-v2",
              }),
            });

          expect(v2.version).toBe("2.0");
        }),
      );
    });

    it.effect("includes optional fields", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const input = createFunctionInput({
          name: "func_with_metadata",
          description: "A test function",
          tags: ["test", "example"],
          metadata: { author: "test" },
          dependencies: { numpy: { version: "1.0", extras: ["full"] } },
        });

        const result =
          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          });

        expect(result.description).toBe("A test function");
        expect(result.tags).toEqual(["test", "example"]);
        expect(result.metadata).toEqual({ author: "test" });
        expect(result.dependencies).toEqual({
          numpy: { version: "1.0", extras: ["full"] },
        });
      }),
    );

    describe("authorization", () => {
      it.effect("returns PermissionDeniedError for VIEWER role", () =>
        Effect.gen(function* () {
          const { environment, project, org, projectViewer } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const input = createFunctionInput({ name: "viewer_func" });

          const result = yield* db.organizations.projects.environments.functions
            .create({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: input,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toContain("permission to create");
        }),
      );

      it.effect("returns PermissionDeniedError for ANNOTATOR role", () =>
        Effect.gen(function* () {
          const { environment, project, org, projectAnnotator } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const input = createFunctionInput({ name: "annotator_func" });

          const result = yield* db.organizations.projects.environments.functions
            .create({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: input,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toContain("permission to create");
        }),
      );

      it.effect("allows DEVELOPER role", () =>
        Effect.gen(function* () {
          const { environment, project, org, projectDeveloper } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const input = createFunctionInput({
            name: "developer_func",
            hash: "developer-hash-123",
          });

          const result =
            yield* db.organizations.projects.environments.functions.create({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: input,
            });

          expect(result.isNew).toBe(true);
          expect(result.name).toBe("developer_func");
        }),
      );
    });
  });

  describe("getByHash", () => {
    it.effect("returns function by hash", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const input = createFunctionInput({ hash: "find-by-hash-123" });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: input,
        });

        const found =
          yield* db.organizations.projects.environments.functions.getByHash({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            hash: "find-by-hash-123",
          });

        expect(found.hash).toBe("find-by-hash-123");
      }),
    );

    it.effect("returns NotFoundError when not found", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .getByHash({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            hash: "non-existent-hash",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toContain("not found");
      }),
    );
  });

  describe("getById", () => {
    it.effect("returns function by id", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const input = createFunctionInput();
        const created =
          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          });

        const found =
          yield* db.organizations.projects.environments.functions.getById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            id: created.id,
          });

        expect(found.id).toBe(created.id);
      }),
    );

    it.effect("returns NotFoundError when not found", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .getById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            id: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toContain("not found");
      }),
    );
  });

  describe("list", () => {
    it.effect("lists all functions in environment", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create some functions
        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({ name: "func1", hash: "list-hash-1" }),
        });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({ name: "func2", hash: "list-hash-2" }),
        });

        const result =
          yield* db.organizations.projects.environments.functions.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(result.total).toBe(2);
        expect(result.functions).toHaveLength(2);
      }),
    );

    it.effect("returns empty list when no functions", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.functions.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(result.total).toBe(0);
        expect(result.functions).toEqual([]);
      }),
    );

    it.effect("filters by name", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "target_func",
            hash: "filter-name-1",
          }),
        });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "other_func",
            hash: "filter-name-2",
          }),
        });

        const result =
          yield* db.organizations.projects.environments.functions.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { name: "target_func" },
          });

        expect(result.total).toBe(1);
        expect(result.functions[0].name).toBe("target_func");
      }),
    );

    it.effect("filters by tags", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "tagged_func",
            hash: "filter-tag-1",
            tags: ["production", "ml"],
          }),
        });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "untagged_func",
            hash: "filter-tag-2",
            tags: ["dev"],
          }),
        });

        const result =
          yield* db.organizations.projects.environments.functions.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { tags: ["production"] },
          });

        expect(result.total).toBe(1);
        expect(result.functions[0].name).toBe("tagged_func");
      }),
    );

    it.effect("paginates with limit", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create 3 functions
        for (let i = 0; i < 3; i++) {
          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: createFunctionInput({
              name: `paginate_func_${i}`,
              hash: `paginate-hash-${i}`,
            }),
          });
        }

        const result =
          yield* db.organizations.projects.environments.functions.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { limit: 2 },
          });

        expect(result.total).toBe(3);
        expect(result.functions).toHaveLength(2);
      }),
    );

    it.effect("paginates with offset", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create 3 functions
        for (let i = 0; i < 3; i++) {
          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: createFunctionInput({
              name: `offset_func_${i}`,
              hash: `offset-hash-${i}`,
            }),
          });
        }

        const result =
          yield* db.organizations.projects.environments.functions.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { offset: 1 },
          });

        expect(result.total).toBe(3);
        expect(result.functions).toHaveLength(2);
      }),
    );
  });

  describe("findAll", () => {
    it.effect("returns all functions in environment", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create some functions
        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "findall_func1",
            hash: "fa-hash-1",
          }),
        });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "findall_func2",
            hash: "fa-hash-2",
          }),
        });

        const result =
          yield* db.organizations.projects.environments.functions.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(result).toHaveLength(2);
        expect(result.every((f) => f.isNew === false)).toBe(true);
      }),
    );

    it.effect("returns empty array when no functions", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.functions.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(result).toEqual([]);
      }),
    );
  });

  describe("findById", () => {
    it.effect("returns function by functionId", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: createFunctionInput({ hash: "findbyid-hash" }),
          });

        const found =
          yield* db.organizations.projects.environments.functions.findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            functionId: created.id,
          });

        expect(found.id).toBe(created.id);
        expect(found.isNew).toBe(false);
      }),
    );

    it.effect("returns NotFoundError when function not found", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            functionId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );
  });

  describe("update", () => {
    it.effect("returns PermissionDeniedError (functions are immutable)", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: createFunctionInput({ hash: "update-test-hash" }),
          });

        const result = yield* db.organizations.projects.environments.functions
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            functionId: created.id,
            data: undefined as never,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("immutable");
      }),
    );
  });

  describe("delete", () => {
    it.effect("deletes function successfully", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: createFunctionInput({ hash: "delete-test-hash" }),
          });

        // Delete the function
        yield* db.organizations.projects.environments.functions.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          functionId: created.id,
        });

        // Verify it's deleted
        const result = yield* db.organizations.projects.environments.functions
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            functionId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns NotFoundError when function not found", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .delete({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            functionId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns PermissionDeniedError for non-ADMIN role", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, projectDeveloper } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const created =
          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: createFunctionInput({ hash: "delete-perm-test-hash" }),
          });

        // Developer should not be able to delete
        const result = yield* db.organizations.projects.environments.functions
          .delete({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            functionId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("delete");
      }),
    );
  });

  describe("authorization", () => {
    it.effect("returns PermissionDeniedError for VIEWER role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectViewer } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const input = createFunctionInput({ name: "viewer_func" });

        const result = yield* db.organizations.projects.environments.functions
          .create({
            userId: projectViewer.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission to create");
      }),
    );

    it.effect("returns PermissionDeniedError for ANNOTATOR role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectAnnotator } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const input = createFunctionInput({ name: "annotator_func" });

        const result = yield* db.organizations.projects.environments.functions
          .create({
            userId: projectAnnotator.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission to create");
      }),
    );

    it.effect("allows DEVELOPER role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectDeveloper } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const input = createFunctionInput({
          name: "developer_func",
          hash: "developer-hash-123",
        });

        const result =
          yield* db.organizations.projects.environments.functions.create({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          });

        expect(result.isNew).toBe(true);
        expect(result.name).toBe("developer_func");
      }),
    );
  });

  describe("DatabaseError", () => {
    it.effect("returns DatabaseError when create check existing fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            data: {
              code: "def test(): pass",
              hash: "test-hash",
              signature: "def test() -> None",
              signatureHash: "sig-hash",
              name: "test_func",
            },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to check existing function");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // registerOrGet check existing fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns DatabaseError when create get latest version fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.functions
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              data: {
                code: "def test(): pass",
                hash: "test-hash",
                signature: "def test() -> None",
                signatureHash: "sig-hash",
                name: "test_func",
              },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get latest version");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // projectMemberships.getRole -> organizationMemberships.findById -> authorize
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // projectMemberships.getRole -> organizationMemberships.findById -> actual query
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // projectMemberships.getRole -> verifyProjectExists
              .select([{ id: "project-id" }])
              // registerOrGet check existing succeeds (no existing function)
              .select([])
              // registerOrGet get latest version fails (inside transaction)
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );

    it.effect("returns DatabaseError when create insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            data: {
              code: "def test(): pass",
              hash: "test-hash",
              signature: "def test() -> None",
              signatureHash: "sig-hash",
              name: "test_func",
            },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to insert function");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // registerOrGet check existing succeeds (no existing function)
            .select([])
            // registerOrGet get latest version succeeds (no existing version)
            .select([])
            // registerOrGet insert fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns DatabaseError when create fetch after conflict fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments.functions
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              data: {
                code: "def test(): pass",
                hash: "test-hash",
                signature: "def test() -> None",
                signatureHash: "sig-hash",
                name: "test_func",
              },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to fetch after conflict");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // projectMemberships.getRole -> organizationMemberships.findById -> authorize
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // projectMemberships.getRole -> organizationMemberships.findById -> actual query
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // projectMemberships.getRole -> verifyProjectExists
              .select([{ id: "project-id" }])
              // registerOrGet check existing succeeds (no existing function)
              .select([])
              // registerOrGet get latest version succeeds (no existing version)
              .select([])
              // registerOrGet insert returns empty (conflict)
              .insert([])
              // registerOrGet fetch after conflict fails
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );

    it.effect("returns existing function when insert conflicts", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.functions.create({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            data: {
              code: "def test(): pass",
              hash: "test-hash",
              signature: "def test() -> None",
              signatureHash: "sig-hash",
              name: "test_func",
            },
          });

        expect(result.isNew).toBe(false);
        expect(result.id).toBe("existing-id");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // registerOrGet check existing succeeds (no existing function)
            .select([])
            // registerOrGet get latest version succeeds (no existing version)
            .select([])
            // registerOrGet insert returns empty (conflict)
            .insert([])
            // registerOrGet fetch after conflict succeeds
            .select([
              {
                id: "existing-id",
                hash: "test-hash",
                signatureHash: "sig-hash",
                name: "test_func",
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
                createdAt: new Date(),
                updatedAt: new Date(),
              },
            ])
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when delete fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            functionId: "function-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete function");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // getByIdInternal (verify function exists)
            .select([
              {
                id: "function-id",
                hash: "hash",
                signatureHash: "sig-hash",
                name: "test_func",
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
                createdAt: new Date(),
                updatedAt: new Date(),
              },
            ])
            // delete fails
            .delete(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when list count fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .list({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to count functions");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // listInternal count fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when list query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .list({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to list functions");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // listInternal count succeeds
            .select([{ count: 0 }])
            // listInternal list query fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when getByHash fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .getByHash({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            hash: "some-hash",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get function by hash");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // getByHashInternal fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when getById fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .getById({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            id: "function-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get function by id");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // getByIdInternal fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when findById fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            functionId: "function-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get function by id");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // getByIdInternal fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when findAll fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to count functions");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById -> authorize
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById -> actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // listInternal count fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });
});
