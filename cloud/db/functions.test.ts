import { describe, it, expect, TestEnvironmentFixture } from "@/tests/db";
import { Effect } from "effect";
import { DrizzleORM } from "@/db/client";
import { Functions, type RegisterFunctionInput } from "@/db/functions";
import { NotFoundError } from "@/errors";

// =============================================================================
// Functions class tests
// =============================================================================

describe("Functions", () => {
  const functionsService = new Functions();

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

  describe("getEnvironmentContext", () => {
    it.effect("returns context for valid environmentId", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;

        const context = yield* functionsService
          .getEnvironmentContext(environment.id)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(context).toEqual({
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        });
      }),
    );

    it.effect("returns NotFoundError when environment not found", () =>
      Effect.gen(function* () {
        const result = yield* functionsService
          .getEnvironmentContext("00000000-0000-0000-0000-000000000000")
          .pipe(
            Effect.provide(yield* Effect.context<DrizzleORM>()),
            Effect.flip,
          );

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toContain("not found");
      }),
    );
  });

  describe("registerOrGet", () => {
    describe("versioning", () => {
      it.effect("new function gets version 1.0", () =>
        Effect.gen(function* () {
          const { environment, project, org } = yield* TestEnvironmentFixture;
          const context = {
            environmentId: environment.id,
            projectId: project.id,
            organizationId: org.id,
          };

          const input = createFunctionInput({ name: "new_func" });

          const result = yield* functionsService
            .registerOrGet(input, context)
            .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

          expect(result.version).toBe("1.0");
          expect(result.isNew).toBe(true);
          expect(result.name).toBe("new_func");
        }),
      );

      it.effect("same hash returns existing function", () =>
        Effect.gen(function* () {
          const { environment, project, org } = yield* TestEnvironmentFixture;
          const context = {
            environmentId: environment.id,
            projectId: project.id,
            organizationId: org.id,
          };

          const input = createFunctionInput({ hash: "same-hash-123" });

          // First registration
          const first = yield* functionsService
            .registerOrGet(input, context)
            .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

          expect(first.isNew).toBe(true);

          // Second registration with same hash
          const second = yield* functionsService
            .registerOrGet(input, context)
            .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

          expect(second.isNew).toBe(false);
          expect(second.id).toBe(first.id);
        }),
      );

      it.effect("same signatureHash gets minor version bump", () =>
        Effect.gen(function* () {
          const { environment, project, org } = yield* TestEnvironmentFixture;
          const context = {
            environmentId: environment.id,
            projectId: project.id,
            organizationId: org.id,
          };

          const funcName = "versioned_func_minor";
          const signatureHash = "same-sig-hash";

          // First version
          const v1 = yield* functionsService
            .registerOrGet(
              createFunctionInput({
                name: funcName,
                signatureHash,
                hash: "hash-v1",
                code: "version 1",
              }),
              context,
            )
            .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

          expect(v1.version).toBe("1.0");

          // Second version - same signature, different implementation
          const v2 = yield* functionsService
            .registerOrGet(
              createFunctionInput({
                name: funcName,
                signatureHash,
                hash: "hash-v2",
                code: "version 2",
              }),
              context,
            )
            .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

          expect(v2.version).toBe("1.1");
        }),
      );

      it.effect("different signatureHash gets major version bump", () =>
        Effect.gen(function* () {
          const { environment, project, org } = yield* TestEnvironmentFixture;
          const context = {
            environmentId: environment.id,
            projectId: project.id,
            organizationId: org.id,
          };

          const funcName = "versioned_func_major";

          // First version
          const v1 = yield* functionsService
            .registerOrGet(
              createFunctionInput({
                name: funcName,
                signatureHash: "sig-v1",
                hash: "hash-major-v1",
              }),
              context,
            )
            .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

          expect(v1.version).toBe("1.0");

          // Second version - different signature
          const v2 = yield* functionsService
            .registerOrGet(
              createFunctionInput({
                name: funcName,
                signatureHash: "sig-v2",
                hash: "hash-major-v2",
              }),
              context,
            )
            .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

          expect(v2.version).toBe("2.0");
        }),
      );
    });

    it.effect("includes optional fields", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        const input = createFunctionInput({
          name: "func_with_metadata",
          description: "A test function",
          tags: ["test", "example"],
          metadata: { author: "test" },
          dependencies: { numpy: { version: "1.0", extras: ["full"] } },
        });

        const result = yield* functionsService
          .registerOrGet(input, context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result.description).toBe("A test function");
        expect(result.tags).toEqual(["test", "example"]);
        expect(result.metadata).toEqual({ author: "test" });
        expect(result.dependencies).toEqual({
          numpy: { version: "1.0", extras: ["full"] },
        });
      }),
    );
  });

  describe("getByHash", () => {
    it.effect("returns function by hash", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        const input = createFunctionInput({ hash: "find-by-hash-123" });

        yield* functionsService
          .registerOrGet(input, context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        const found = yield* functionsService
          .getByHash("find-by-hash-123", environment.id)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(found.hash).toBe("find-by-hash-123");
      }),
    );

    it.effect("returns NotFoundError when not found", () =>
      Effect.gen(function* () {
        const { environment } = yield* TestEnvironmentFixture;

        const result = yield* functionsService
          .getByHash("non-existent-hash", environment.id)
          .pipe(
            Effect.provide(yield* Effect.context<DrizzleORM>()),
            Effect.flip,
          );

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toContain("not found");
      }),
    );
  });

  describe("getById", () => {
    it.effect("returns function by id", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        const input = createFunctionInput();
        const created = yield* functionsService
          .registerOrGet(input, context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        const found = yield* functionsService
          .getById(created.id, environment.id)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(found.id).toBe(created.id);
      }),
    );

    it.effect("returns NotFoundError when not found", () =>
      Effect.gen(function* () {
        const { environment } = yield* TestEnvironmentFixture;

        const result = yield* functionsService
          .getById("00000000-0000-0000-0000-000000000000", environment.id)
          .pipe(
            Effect.provide(yield* Effect.context<DrizzleORM>()),
            Effect.flip,
          );

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toContain("not found");
      }),
    );
  });

  describe("list", () => {
    it.effect("lists all functions in environment", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        // Create some functions
        yield* functionsService
          .registerOrGet(
            createFunctionInput({ name: "func1", hash: "list-hash-1" }),
            context,
          )
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        yield* functionsService
          .registerOrGet(
            createFunctionInput({ name: "func2", hash: "list-hash-2" }),
            context,
          )
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        const result = yield* functionsService
          .list(environment.id)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result.total).toBe(2);
        expect(result.functions).toHaveLength(2);
      }),
    );

    it.effect("returns empty list when no functions", () =>
      Effect.gen(function* () {
        const { environment } = yield* TestEnvironmentFixture;

        const result = yield* functionsService
          .list(environment.id)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result.total).toBe(0);
        expect(result.functions).toEqual([]);
      }),
    );

    it.effect("filters by name", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        yield* functionsService
          .registerOrGet(
            createFunctionInput({ name: "target_func", hash: "filter-name-1" }),
            context,
          )
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        yield* functionsService
          .registerOrGet(
            createFunctionInput({ name: "other_func", hash: "filter-name-2" }),
            context,
          )
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        const result = yield* functionsService
          .list(environment.id, { name: "target_func" })
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result.total).toBe(1);
        expect(result.functions[0].name).toBe("target_func");
      }),
    );

    it.effect("filters by tags", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        yield* functionsService
          .registerOrGet(
            createFunctionInput({
              name: "tagged_func",
              hash: "filter-tag-1",
              tags: ["production", "ml"],
            }),
            context,
          )
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        yield* functionsService
          .registerOrGet(
            createFunctionInput({
              name: "untagged_func",
              hash: "filter-tag-2",
              tags: ["dev"],
            }),
            context,
          )
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        const result = yield* functionsService
          .list(environment.id, { tags: ["production"] })
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result.total).toBe(1);
        expect(result.functions[0].name).toBe("tagged_func");
      }),
    );

    it.effect("paginates with limit", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        // Create 3 functions
        for (let i = 0; i < 3; i++) {
          yield* functionsService
            .registerOrGet(
              createFunctionInput({
                name: `paginate_func_${i}`,
                hash: `paginate-hash-${i}`,
              }),
              context,
            )
            .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));
        }

        const result = yield* functionsService
          .list(environment.id, { limit: 2 })
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result.total).toBe(3);
        expect(result.functions).toHaveLength(2);
      }),
    );

    it.effect("paginates with offset", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        // Create 3 functions
        for (let i = 0; i < 3; i++) {
          yield* functionsService
            .registerOrGet(
              createFunctionInput({
                name: `offset_func_${i}`,
                hash: `offset-hash-${i}`,
              }),
              context,
            )
            .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));
        }

        const result = yield* functionsService
          .list(environment.id, { offset: 1 })
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result.total).toBe(3);
        expect(result.functions).toHaveLength(2);
      }),
    );
  });
});
