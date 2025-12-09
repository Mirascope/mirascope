import { describe, it, expect, vi } from "vitest";
import { Effect } from "effect";
import { ApiKeyService } from "@/db/services/api-keys";
import {
  DatabaseError,
  NotFoundError,
  AlreadyExistsError,
  PermissionDeniedError,
} from "@/db/errors";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import type * as schema from "@/db/schema";
import { withTestDatabase } from "@/tests/db";

describe("ApiKeyService", () => {
  describe("create", () => {
    it(
      "should create an API key and return the plaintext key",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            user.id,
          );

          const project = yield* db.projects.create(
            { name: "Test Project", organizationId: org.id },
            user.id,
          );

          // Get the default development environment
          const envs = yield* db.environments.findByProject(
            project.id,
            user.id,
          );
          const devEnv = envs.find((e) => e.name === "development")!;

          const apiKey = yield* db.apiKeys.create(
            { name: "test-key", environmentId: devEnv.id },
            user.id,
          );

          expect(apiKey).toBeDefined();
          expect(apiKey.id).toBeDefined();
          expect(apiKey.name).toBe("test-key");
          expect(apiKey.key).toBeDefined();
          expect(apiKey.key.startsWith("mk_")).toBe(true);
          expect(apiKey.keyPrefix).toBeDefined();
          expect(apiKey.environmentId).toBe(devEnv.id);
        }),
      ),
    );

    it(
      "should fail with PermissionDeniedError when user is not a member",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const owner = yield* db.users.create({
            email: "owner@example.com",
            name: "Owner",
          });

          const otherUser = yield* db.users.create({
            email: "other@example.com",
            name: "Other User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            owner.id,
          );

          const project = yield* db.projects.create(
            { name: "Test Project", organizationId: org.id },
            owner.id,
          );

          const envs = yield* db.environments.findByProject(
            project.id,
            owner.id,
          );
          const devEnv = envs.find((e) => e.name === "development")!;

          const result = yield* Effect.either(
            db.apiKeys.create(
              { name: "test-key", environmentId: devEnv.id },
              otherUser.id,
            ),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(PermissionDeniedError);
          }
        }),
      ),
    );

    it(
      "should fail with AlreadyExistsError when API key name exists",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            user.id,
          );

          const project = yield* db.projects.create(
            { name: "Test Project", organizationId: org.id },
            user.id,
          );

          const envs = yield* db.environments.findByProject(
            project.id,
            user.id,
          );
          const devEnv = envs.find((e) => e.name === "development")!;

          yield* db.apiKeys.create(
            { name: "test-key", environmentId: devEnv.id },
            user.id,
          );

          const result = yield* Effect.either(
            db.apiKeys.create(
              { name: "test-key", environmentId: devEnv.id },
              user.id,
            ),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(AlreadyExistsError);
            expect(result.left.message).toContain("already exists");
          }
        }),
      ),
    );
  });

  describe("findByEnvironment", () => {
    it(
      "should return API keys for an environment",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            user.id,
          );

          const project = yield* db.projects.create(
            { name: "Test Project", organizationId: org.id },
            user.id,
          );

          const envs = yield* db.environments.findByProject(
            project.id,
            user.id,
          );
          const devEnv = envs.find((e) => e.name === "development")!;

          yield* db.apiKeys.create(
            { name: "key-1", environmentId: devEnv.id },
            user.id,
          );
          yield* db.apiKeys.create(
            { name: "key-2", environmentId: devEnv.id },
            user.id,
          );

          const keys = yield* db.apiKeys.findByEnvironment(devEnv.id, user.id);

          expect(keys).toHaveLength(2);
          expect(keys.find((k) => k.name === "key-1")).toBeDefined();
          expect(keys.find((k) => k.name === "key-2")).toBeDefined();
          // Should not include the plaintext key
          expect((keys[0] as { key?: string }).key).toBeUndefined();
        }),
      ),
    );

    it(
      "should fail with PermissionDeniedError when user is not a member",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const owner = yield* db.users.create({
            email: "owner@example.com",
            name: "Owner",
          });

          const otherUser = yield* db.users.create({
            email: "other@example.com",
            name: "Other User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            owner.id,
          );

          const project = yield* db.projects.create(
            { name: "Test Project", organizationId: org.id },
            owner.id,
          );

          const envs = yield* db.environments.findByProject(
            project.id,
            owner.id,
          );
          const devEnv = envs.find((e) => e.name === "development")!;

          const result = yield* Effect.either(
            db.apiKeys.findByEnvironment(devEnv.id, otherUser.id),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(PermissionDeniedError);
          }
        }),
      ),
    );
  });

  describe("findById", () => {
    it(
      "should return an API key by ID",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            user.id,
          );

          const project = yield* db.projects.create(
            { name: "Test Project", organizationId: org.id },
            user.id,
          );

          const envs = yield* db.environments.findByProject(
            project.id,
            user.id,
          );
          const devEnv = envs.find((e) => e.name === "development")!;

          const created = yield* db.apiKeys.create(
            { name: "test-key", environmentId: devEnv.id },
            user.id,
          );

          const key = yield* db.apiKeys.findById(created.id, user.id);

          expect(key.id).toBe(created.id);
          expect(key.name).toBe("test-key");
          // Should not include the plaintext key
          expect((key as { key?: string }).key).toBeUndefined();
        }),
      ),
    );

    it(
      "should fail with PermissionDeniedError when API key doesn't exist",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const result = yield* Effect.either(
            db.apiKeys.findById(
              "00000000-0000-0000-0000-000000000000",
              user.id,
            ),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(PermissionDeniedError);
          }
        }),
      ),
    );
  });

  describe("findAll", () => {
    it(
      "should return all API keys for user's environments",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            user.id,
          );

          const project1 = yield* db.projects.create(
            { name: "Project 1", organizationId: org.id },
            user.id,
          );

          const project2 = yield* db.projects.create(
            { name: "Project 2", organizationId: org.id },
            user.id,
          );

          const envs1 = yield* db.environments.findByProject(
            project1.id,
            user.id,
          );
          const envs2 = yield* db.environments.findByProject(
            project2.id,
            user.id,
          );

          yield* db.apiKeys.create(
            { name: "key-1", environmentId: envs1[0].id },
            user.id,
          );
          yield* db.apiKeys.create(
            { name: "key-2", environmentId: envs2[0].id },
            user.id,
          );

          const keys = yield* db.apiKeys.findAll(user.id);

          expect(keys).toHaveLength(2);
        }),
      ),
    );
  });

  describe("delete", () => {
    it(
      "should delete an API key",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            user.id,
          );

          const project = yield* db.projects.create(
            { name: "Test Project", organizationId: org.id },
            user.id,
          );

          const envs = yield* db.environments.findByProject(
            project.id,
            user.id,
          );
          const devEnv = envs.find((e) => e.name === "development")!;

          const created = yield* db.apiKeys.create(
            { name: "test-key", environmentId: devEnv.id },
            user.id,
          );

          yield* db.apiKeys.delete(created.id, user.id);

          const result = yield* Effect.either(
            db.apiKeys.findById(created.id, user.id),
          );

          expect(result._tag).toBe("Left");
        }),
      ),
    );

    it(
      "should fail with PermissionDeniedError when user is not a member",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const owner = yield* db.users.create({
            email: "owner@example.com",
            name: "Owner",
          });

          const otherUser = yield* db.users.create({
            email: "other@example.com",
            name: "Other User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            owner.id,
          );

          const project = yield* db.projects.create(
            { name: "Test Project", organizationId: org.id },
            owner.id,
          );

          const envs = yield* db.environments.findByProject(
            project.id,
            owner.id,
          );
          const devEnv = envs.find((e) => e.name === "development")!;

          const created = yield* db.apiKeys.create(
            { name: "test-key", environmentId: devEnv.id },
            owner.id,
          );

          const result = yield* Effect.either(
            db.apiKeys.delete(created.id, otherUser.id),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(PermissionDeniedError);
          }
        }),
      ),
    );
  });

  describe("verifyApiKey", () => {
    it(
      "should verify a valid API key",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            user.id,
          );

          const project = yield* db.projects.create(
            { name: "Test Project", organizationId: org.id },
            user.id,
          );

          const envs = yield* db.environments.findByProject(
            project.id,
            user.id,
          );
          const devEnv = envs.find((e) => e.name === "development")!;

          const created = yield* db.apiKeys.create(
            { name: "test-key", environmentId: devEnv.id },
            user.id,
          );

          const result = yield* db.apiKeys.verifyApiKey(created.key);

          expect(result.apiKeyId).toBe(created.id);
          expect(result.environmentId).toBe(devEnv.id);
        }),
      ),
    );

    it(
      "should fail with NotFoundError for invalid API key",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(
            db.apiKeys.verifyApiKey("mk_invalid_key"),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(NotFoundError);
            expect(result.left.message).toBe("Invalid API key");
          }
        }),
      ),
    );
  });

  describe("database errors", () => {
    it("should fail with DatabaseError on environment lookup error", async () => {
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockRejectedValue(new Error("DB error")),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to fetch environment");
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with DatabaseError on project lookup error", async () => {
      let callCount = 0;
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  // Environment lookup succeeds
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                // Project lookup fails
                return Promise.reject(new Error("DB error"));
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to fetch project");
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with DatabaseError on membership lookup error", async () => {
      let callCount = 0;
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                if (callCount === 2) {
                  return Promise.resolve([{ organizationId: "org-id" }]);
                }
                return Promise.reject(new Error("DB error"));
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to check membership");
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with PermissionDeniedError when environment not found", async () => {
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockResolvedValue([]),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(PermissionDeniedError);
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with PermissionDeniedError when project not found", async () => {
      let callCount = 0;
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                return Promise.resolve([]);
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(PermissionDeniedError);
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with PermissionDeniedError when membership not found", async () => {
      let callCount = 0;
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                if (callCount === 2) {
                  return Promise.resolve([{ organizationId: "org-id" }]);
                }
                return Promise.resolve([]);
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(PermissionDeniedError);
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with PermissionDeniedError when role is too low", async () => {
      let callCount = 0;
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                if (callCount === 2) {
                  return Promise.resolve([{ organizationId: "org-id" }]);
                }
                // ANNOTATOR role is too low for API key operations
                return Promise.resolve([{ role: "ANNOTATOR" }]);
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(PermissionDeniedError);
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with DatabaseError on existing API key check error", async () => {
      let callCount = 0;
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                if (callCount === 2) {
                  return Promise.resolve([{ organizationId: "org-id" }]);
                }
                if (callCount === 3) {
                  return Promise.resolve([{ role: "DEVELOPER" }]);
                }
                return Promise.reject(new Error("DB error"));
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain(
            "Failed to check existing API key",
          );
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with DatabaseError on findAll query error", async () => {
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              innerJoin: vi.fn().mockReturnValue({
                innerJoin: vi.fn().mockReturnValue({
                  where: vi.fn().mockRejectedValue(new Error("DB error")),
                }),
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(service.findAll("user-id"));
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to fetch API keys");
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with DatabaseError on verifyApiKey query error", async () => {
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockRejectedValue(new Error("DB error")),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.verifyApiKey("mk_test_key"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to verify API key");
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with DatabaseError on findByEnvironment query error", async () => {
      let callCount = 0;
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockImplementation(() => {
              callCount++;
              if (callCount <= 3) {
                return {
                  limit: vi.fn().mockImplementation(() => {
                    if (callCount === 1) {
                      return Promise.resolve([{ projectId: "project-id" }]);
                    }
                    if (callCount === 2) {
                      return Promise.resolve([{ organizationId: "org-id" }]);
                    }
                    return Promise.resolve([{ role: "DEVELOPER" }]);
                  }),
                };
              }
              return Promise.reject(new Error("DB error"));
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.findByEnvironment("env-id", "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain(
            "Failed to fetch API keys for environment",
          );
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with DatabaseError on API key lookup error in checkPermission", async () => {
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockRejectedValue(new Error("DB error")),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.findById("key-id", "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to fetch API key");
        }
      }).pipe(Effect.runPromise);
    });

    it("should fail with DatabaseError on insert error", async () => {
      let callCount = 0;
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                if (callCount === 2) {
                  return Promise.resolve([{ organizationId: "org-id" }]);
                }
                if (callCount === 3) {
                  return Promise.resolve([{ role: "DEVELOPER" }]);
                }
                return Promise.resolve([]);
              }),
            }),
          }),
        }),
        insert: vi.fn().mockReturnValue({
          values: vi.fn().mockReturnValue({
            returning: vi.fn().mockRejectedValue(new Error("Insert error")),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to create API key");
        }
      }).pipe(Effect.runPromise);
    });

    it("should handle non-Error thrown on environment lookup", async () => {
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      const nonErrorRejection = () => Promise.reject("string error");
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(nonErrorRejection),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Unknown error");
        }
      }).pipe(Effect.runPromise);
    });

    it("should handle non-Error thrown on project lookup", async () => {
      let callCount = 0;
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      const nonErrorRejection = () => Promise.reject("string error");
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                return nonErrorRejection();
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Unknown error");
        }
      }).pipe(Effect.runPromise);
    });

    it("should handle non-Error thrown on membership lookup", async () => {
      let callCount = 0;
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      const nonErrorRejection = () => Promise.reject("string error");
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                if (callCount === 2) {
                  return Promise.resolve([{ organizationId: "org-id" }]);
                }
                return nonErrorRejection();
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Unknown error");
        }
      }).pipe(Effect.runPromise);
    });

    it("should handle non-Error thrown on existing check", async () => {
      let callCount = 0;
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      const nonErrorRejection = () => Promise.reject("string error");
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                if (callCount === 2) {
                  return Promise.resolve([{ organizationId: "org-id" }]);
                }
                if (callCount === 3) {
                  return Promise.resolve([{ role: "DEVELOPER" }]);
                }
                return nonErrorRejection();
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Unknown error");
        }
      }).pipe(Effect.runPromise);
    });

    it("should handle non-Error thrown on insert", async () => {
      let callCount = 0;
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      const nonErrorRejection = () => Promise.reject("string error");
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(() => {
                callCount++;
                if (callCount === 1) {
                  return Promise.resolve([{ projectId: "project-id" }]);
                }
                if (callCount === 2) {
                  return Promise.resolve([{ organizationId: "org-id" }]);
                }
                if (callCount === 3) {
                  return Promise.resolve([{ role: "DEVELOPER" }]);
                }
                return Promise.resolve([]);
              }),
            }),
          }),
        }),
        insert: vi.fn().mockReturnValue({
          values: vi.fn().mockReturnValue({
            returning: vi.fn().mockImplementation(nonErrorRejection),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.create({ name: "test", environmentId: "env-id" }, "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Unknown error");
        }
      }).pipe(Effect.runPromise);
    });

    it("should handle non-Error thrown on findAll query", async () => {
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      const nonErrorRejection = () => Promise.reject("string error");
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            innerJoin: vi.fn().mockReturnValue({
              innerJoin: vi.fn().mockReturnValue({
                innerJoin: vi.fn().mockReturnValue({
                  where: vi.fn().mockImplementation(nonErrorRejection),
                }),
              }),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(service.findAll("user-id"));
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Unknown error");
        }
      }).pipe(Effect.runPromise);
    });

    it("should handle non-Error thrown on verifyApiKey query", async () => {
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      const nonErrorRejection = () => Promise.reject("string error");
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(nonErrorRejection),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.verifyApiKey("mk_test_key"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Unknown error");
        }
      }).pipe(Effect.runPromise);
    });

    it("should handle non-Error thrown on findByEnvironment query", async () => {
      let callCount = 0;
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      const nonErrorRejection = () => Promise.reject("string error");
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockImplementation(() => {
              callCount++;
              if (callCount <= 3) {
                return {
                  limit: vi.fn().mockImplementation(() => {
                    if (callCount === 1) {
                      return Promise.resolve([{ projectId: "project-id" }]);
                    }
                    if (callCount === 2) {
                      return Promise.resolve([{ organizationId: "org-id" }]);
                    }
                    return Promise.resolve([{ role: "DEVELOPER" }]);
                  }),
                };
              }
              return nonErrorRejection();
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.findByEnvironment("env-id", "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Unknown error");
        }
      }).pipe(Effect.runPromise);
    });

    it("should handle non-Error thrown on API key lookup in checkPermission", async () => {
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      const nonErrorRejection = () => Promise.reject("string error");
      const mockDb = {
        select: vi.fn().mockReturnValue({
          from: vi.fn().mockReturnValue({
            where: vi.fn().mockReturnValue({
              limit: vi.fn().mockImplementation(nonErrorRejection),
            }),
          }),
        }),
      } as unknown as PostgresJsDatabase<typeof schema>;

      const service = new ApiKeyService(mockDb);

      await Effect.gen(function* () {
        const result = yield* Effect.either(
          service.findById("key-id", "user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Unknown error");
        }
      }).pipe(Effect.runPromise);
    });
  });
});
