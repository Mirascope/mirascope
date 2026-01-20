import {
  describe,
  it,
  expect,
  TestEnvironmentFixture,
  MockDrizzleORM,
} from "@/tests/db";
import { Effect } from "effect";
import { Database } from "@/db";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  ImmutableResourceError,
} from "@/errors";
import type { FunctionCreateData, PublicFunction } from "@/db/functions";

describe("Functions", () => {
  const createFunctionInput = (
    overrides: Partial<FunctionCreateData> = {},
  ): FunctionCreateData => ({
    code: 'def my_func(): return "hello"',
    hash: `hash-${Math.random().toString(36).slice(2)}`,
    signature: "def my_func() -> str",
    signatureHash: "sig-hash-1",
    name: "my_func",
    ...overrides,
  });

  const buildPublicFunction = (
    overrides: Partial<PublicFunction> = {},
  ): PublicFunction => ({
    id: "function-id",
    hash: "hash",
    signatureHash: "sig-hash",
    name: "function",
    description: null,
    version: "1.0",
    tags: null,
    metadata: null,
    code: 'def my_func(): return "hello"',
    signature: "def my_func() -> str",
    dependencies: null,
    environmentId: "env-id",
    projectId: "project-id",
    organizationId: "org-id",
    createdAt: new Date("2024-01-01T00:00:00.000Z"),
    updatedAt: new Date("2024-01-01T00:00:00.000Z"),
    ...overrides,
  });

  const ownerMembership = {
    role: "OWNER",
    organizationId: "org-id",
    memberId: "owner-id",
    createdAt: new Date("2024-01-01T00:00:00.000Z"),
  };

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

  describe("findByName", () => {
    it.effect("returns functions by name", () =>
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
            name: "named_func",
            hash: "named-hash-1",
          }),
        });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "named_func",
            hash: "named-hash-2",
          }),
        });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "other_func",
            hash: "other-hash-1",
          }),
        });

        const result =
          yield* db.organizations.projects.environments.functions.findByName({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            name: "named_func",
          });

        expect(result).toHaveLength(2);
        expect(result.every((fn) => fn.name === "named_func")).toBe(true);
      }),
    );

    it.effect("returns empty array when no functions match", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.functions.findByName({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            name: "missing_func",
          });

        expect(result).toEqual([]);
      }),
    );
  });

  describe("findLatestByName", () => {
    it.effect("returns latest version per name", () =>
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
            name: "latest_func",
            hash: "latest-hash-1",
            signatureHash: "latest-sig",
          }),
        });

        const latest =
          yield* db.organizations.projects.environments.functions.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: createFunctionInput({
              name: "latest_func",
              hash: "latest-hash-2",
              signatureHash: "latest-sig",
            }),
          });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "second_func",
            hash: "second-hash-1",
          }),
        });

        const result =
          yield* db.organizations.projects.environments.functions.findLatestByName(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            },
          );

        expect(result).toHaveLength(2);
        const latestResult = result.find((fn) => fn.name === "latest_func");
        expect(latestResult?.hash).toBe(latest.hash);
      }),
    );

    it.effect("returns empty array when no functions exist", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.functions.findLatestByName(
            {
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: environment.id,
            },
          );

        expect(result).toEqual([]);
      }),
    );

    it.effect("prefers higher major version over createdAt ordering", () => {
      const currentVersion = buildPublicFunction({
        id: "function-1",
        name: "versioned_func",
        version: "1.0",
        createdAt: new Date("2024-01-02T00:00:00.000Z"),
        updatedAt: new Date("2024-01-02T00:00:00.000Z"),
      });

      const higherMajorVersion = buildPublicFunction({
        id: "function-2",
        name: "versioned_func",
        version: "2.0",
        createdAt: new Date("2024-01-01T00:00:00.000Z"),
        updatedAt: new Date("2024-01-01T00:00:00.000Z"),
      });

      return Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.functions.findLatestByName(
            {
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
            },
          );

        expect(result).toHaveLength(1);
        expect(result[0]?.id).toBe("function-2");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([ownerMembership])
            .select([ownerMembership])
            .select([{ id: "project-id" }])
            .select([currentVersion, higherMajorVersion])
            .build(),
        ),
      );
    });

    it.effect("keeps higher major version when lower major appears", () => {
      const higherMajorVersion = buildPublicFunction({
        id: "function-2",
        name: "versioned_func",
        version: "2.0",
        createdAt: new Date("2024-01-02T00:00:00.000Z"),
        updatedAt: new Date("2024-01-02T00:00:00.000Z"),
      });

      const lowerMajorVersion = buildPublicFunction({
        id: "function-1",
        name: "versioned_func",
        version: "1.0",
        createdAt: new Date("2024-01-01T00:00:00.000Z"),
        updatedAt: new Date("2024-01-01T00:00:00.000Z"),
      });

      return Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.functions.findLatestByName(
            {
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
            },
          );

        expect(result).toHaveLength(1);
        expect(result[0]?.id).toBe("function-2");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([ownerMembership])
            .select([ownerMembership])
            .select([{ id: "project-id" }])
            .select([higherMajorVersion, lowerMajorVersion])
            .build(),
        ),
      );
    });

    it.effect("uses createdAt tie-breaker when versions match", () => {
      const olderVersion = buildPublicFunction({
        id: "function-1",
        name: "versioned_func",
        version: "1.0",
        createdAt: new Date("2024-01-01T00:00:00.000Z"),
        updatedAt: new Date("2024-01-01T00:00:00.000Z"),
      });

      const newerVersion = buildPublicFunction({
        id: "function-2",
        name: "versioned_func",
        version: "1.0",
        createdAt: new Date("2024-01-02T00:00:00.000Z"),
        updatedAt: new Date("2024-01-02T00:00:00.000Z"),
      });

      return Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.functions.findLatestByName(
            {
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
            },
          );

        expect(result).toHaveLength(1);
        expect(result[0]?.id).toBe("function-2");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([ownerMembership])
            .select([ownerMembership])
            .select([{ id: "project-id" }])
            .select([olderVersion, newerVersion])
            .build(),
        ),
      );
    });

    it.effect("handles missing createdAt values when versions match", () => {
      const missingCreatedAt = buildPublicFunction({
        id: "function-1",
        name: "versioned_func",
        version: "1.0",
        createdAt: null,
        updatedAt: null,
      });

      const missingCreatedAtNext = buildPublicFunction({
        id: "function-2",
        name: "versioned_func",
        version: "1.0",
        createdAt: null,
        updatedAt: null,
      });

      return Effect.gen(function* () {
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.functions.findLatestByName(
            {
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
            },
          );

        expect(result).toHaveLength(1);
        expect(result[0]?.id).toBe("function-1");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([ownerMembership])
            .select([ownerMembership])
            .select([{ id: "project-id" }])
            .select([missingCreatedAt, missingCreatedAtNext])
            .build(),
        ),
      );
    });
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

  describe("deleteByName", () => {
    it.effect("deletes all function versions by name", () =>
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
            name: "remove_func",
            hash: "remove-hash-1",
          }),
        });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "remove_func",
            hash: "remove-hash-2",
          }),
        });

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "keep_func",
            hash: "keep-hash-1",
          }),
        });

        yield* db.organizations.projects.environments.functions.deleteByName({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          name: "remove_func",
        });

        const remaining =
          yield* db.organizations.projects.environments.functions.findByName({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            name: "remove_func",
          });

        expect(remaining).toEqual([]);

        const keep =
          yield* db.organizations.projects.environments.functions.findByName({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            name: "keep_func",
          });

        expect(keep).toHaveLength(1);
      }),
    );

    it.effect("returns NotFoundError when name not found", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .deleteByName({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            name: "missing_func",
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

        yield* db.organizations.projects.environments.functions.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: createFunctionInput({
            name: "delete_by_name_perm",
            hash: "delete-by-name-hash",
          }),
        });

        const result = yield* db.organizations.projects.environments.functions
          .deleteByName({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            name: "delete_by_name_perm",
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

    it.effect("returns DatabaseError when deleteByName fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .deleteByName({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            name: "delete-name",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete functions by name");
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

    it.effect("returns DatabaseError when findByName fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .findByName({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            name: "name",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to list functions by name");
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

    it.effect("returns DatabaseError when findLatestByName fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.functions
          .findLatestByName({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to list latest functions");
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
