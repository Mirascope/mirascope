import { Effect } from "effect";

import type { FunctionCreateData } from "@/db/functions";

import { Database } from "@/db/database";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  ImmutableResourceError,
} from "@/errors";
import {
  describe,
  it,
  expect,
  TestEnvironmentFixture,
  MockDrizzleORM,
} from "@/tests/db";

describe("Functions", () => {
  const createFunctionInput = (
    overrides: Partial<FunctionCreateData> = {},
  ): FunctionCreateData => ({
    code: 'def my_func(): return "hello"',
    hash: `hash-${Math.random().toString(36).slice(2)}`,
    signature: "def my_func() -> str",
    signatureHash: "sig-hash-1",
    name: "my_func",
    language: "python",
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
          expect(result.name).toBe("new_func");
        }),
      );

      it.effect("same hash returns AlreadyExistsError", () =>
        Effect.gen(function* () {
          const { environment, project, org, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const input = createFunctionInput({ hash: "same-hash-123" });

          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          });

          const error = yield* db.organizations.projects.environments.functions
            .create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
              data: input,
            })
            .pipe(Effect.flip);

          expect(error).toBeInstanceOf(AlreadyExistsError);
          expect(error.message).toContain("same-hash-123");
        }),
      );

      it.effect("same signatureHash gets minor version bump", () =>
        Effect.gen(function* () {
          const { environment, project, org, owner } =
            yield* TestEnvironmentFixture;
          const db = yield* Database;

          const funcName = "versioned_func_minor";
          const signatureHash = "same-sig-hash";

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

          expect(result.name).toBe("developer_func");
        }),
      );
    });
  });

  describe("findByHash", () => {
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
          yield* db.organizations.projects.environments.functions.findByHash({
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
          .findByHash({
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

  describe("findAll", () => {
    it.effect("returns all functions in environment", () =>
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
    it.effect("returns ImmutableResourceError (functions are immutable)", () =>
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

        expect(result).toBeInstanceOf(ImmutableResourceError);
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

        yield* db.organizations.projects.environments.functions.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          functionId: created.id,
        });

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

  describe("DatabaseError", () => {
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
                language: "python",
              },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get latest version");
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
              language: "python",
            },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create function");
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
            .select([])
            .insert(new Error("Connection failed"))
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
            .delete(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns DatabaseError when findByHash fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .findByHash({
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
        expect(result.message).toBe("Failed to get function");
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
        expect(result.message).toBe("Failed to list functions");
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
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });
});
