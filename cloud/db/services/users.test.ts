import { describe, it, expect } from "vitest";
import { withTestDatabase, createPartialMockDatabase } from "@/tests/db";
import { Effect } from "effect";
import { DatabaseError } from "@/db/errors";
import { UserService } from "@/db/services/users";

describe("UserService", () => {
  it(
    "should support basic CRUD",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const created = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });
        expect(created).toBeDefined();
        expect(created.id).toBeDefined();
        expect(created.email).toBe("test@example.com");
        expect(created.name).toBe("Test User");
        expect(created).not.toHaveProperty("createdAt");
        expect(created).not.toHaveProperty("updatedAt");

        const userId = created.id;

        const found = yield* db.users.findById(userId);
        expect(found).toBeDefined();
        expect(found.id).toBe(userId);
        expect(found.email).toBe("test@example.com");
        expect(found.name).toBe("Test User");

        const all = yield* db.users.findAll();
        expect(Array.isArray(all)).toBe(true);
        expect(all.find((u) => u.id === userId)).toBeDefined();

        const updated = yield* db.users.update(userId, {
          name: "Updated User",
          email: "updated@example.com",
        });
        expect(updated).toBeDefined();
        expect(updated.id).toBe(userId);
        expect(updated.name).toBe("Updated User");
        expect(updated.email).toBe("updated@example.com");

        const afterUpdate = yield* db.users.findById(userId);
        expect(afterUpdate).toBeDefined();
        expect(afterUpdate.name).toBe("Updated User");
        expect(afterUpdate.email).toBe("updated@example.com");

        yield* db.users.delete(userId);

        const afterDeleteResult = yield* Effect.either(
          db.users.findById(userId),
        );
        expect(afterDeleteResult._tag).toBe("Left");
        if (afterDeleteResult._tag === "Left") {
          expect(afterDeleteResult.left._tag).toBe("NotFoundError");
        }

        const afterDeleteAll = yield* db.users.findAll();
        expect(afterDeleteAll.find((u) => u.id === userId)).toBeUndefined();
      }),
    ),
  );

  describe("createOrUpdate", () => {
    it(
      "should create a new user",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.createOrUpdate({
            email: "newuser@example.com",
            name: "New User",
          });

          expect(user).toBeDefined();
          expect(user.id).toBeDefined();
          expect(user.email).toBe("newuser@example.com");
          expect(user.name).toBe("New User");
        }),
      ),
    );

    it(
      "should update existing user",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const created = yield* db.users.create({
            email: "existing@example.com",
            name: "Original Name",
          });

          const updated = yield* db.users.createOrUpdate({
            email: "existing@example.com",
            name: "Updated Name",
          });

          expect(updated).toBeDefined();
          expect(updated.id).toBe(created.id);
          expect(updated.email).toBe("existing@example.com");
          expect(updated.name).toBe("Updated Name");
        }),
      ),
    );

    it(
      "should not update if name is the same",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const created = yield* db.users.create({
            email: "samename@example.com",
            name: "Same Name",
          });

          const result = yield* db.users.createOrUpdate({
            email: "samename@example.com",
            name: "Same Name",
          });

          expect(result).toBeDefined();
          expect(result.id).toBe(created.id);
          expect(result.email).toBe("samename@example.com");
          expect(result.name).toBe("Same Name");
        }),
      ),
    );

    it(
      "should handle null name",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.createOrUpdate({
            email: "noname@example.com",
            name: null,
          });

          expect(user).toBeDefined();
          expect(user.id).toBeDefined();
          expect(user.email).toBe("noname@example.com");
          expect(user.name).toBeNull();

          const updated = yield* db.users.createOrUpdate({
            email: "noname@example.com",
            name: null,
          });

          expect(updated.id).toBe(user.id);
          expect(updated.name).toBeNull();
        }),
      ),
    );

    it(
      "should handle undefined name",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.createOrUpdate({
            email: "noname2@example.com",
          });

          expect(user).toBeDefined();
          expect(user.id).toBeDefined();
          expect(user.email).toBe("noname2@example.com");
          expect(user.name).toBeNull();
        }),
      ),
    );
  });

  describe("Error handling", () => {
    it("createOrUpdate returns DatabaseError when upsert fails", () => {
      return Effect.gen(function* () {
        const mockDb = createPartialMockDatabase({
          insert: () => ({
            values: () => ({
              onConflictDoUpdate: () =>
                Promise.reject(new Error("Database connection failed")),
            }),
          }),
        });

        const service = new UserService(mockDb);

        const result = yield* Effect.either(
          service.createOrUpdate({
            email: "test@example.com",
            name: "Test User",
          }),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain(
            "Failed to create or update user",
          );
        }
      }).pipe(Effect.runPromise);
    });

    it("createOrUpdate returns DatabaseError when fetch fails after successful upsert", () => {
      return Effect.gen(function* () {
        const mockDb = createPartialMockDatabase({
          select: () => {
            throw new Error("Database connection failed");
          },
          insert: () => ({
            values: () => ({
              onConflictDoUpdate: () => Promise.resolve(undefined),
            }),
          }),
        });

        const service = new UserService(mockDb);

        const result = yield* Effect.either(
          service.createOrUpdate({
            email: "test@example.com",
            name: "Test User",
          }),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain(
            "Failed to create or update user",
          );
        }
      }).pipe(Effect.runPromise);
    });

    it("createOrUpdate returns DatabaseError when select finds nothing after upsert", () => {
      return Effect.gen(function* () {
        const mockDb = createPartialMockDatabase({
          select: () => ({
            from: () => ({
              where: () => ({
                limit: () => Promise.resolve([]),
              }),
            }),
          }),
          insert: () => ({
            values: () => ({
              onConflictDoUpdate: () => Promise.resolve(undefined),
            }),
          }),
        });

        const service = new UserService(mockDb);

        const result = yield* Effect.either(
          service.createOrUpdate({
            email: "test@example.com",
            name: "Test User",
          }),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain(
            "Failed to create or update user",
          );
        }
      }).pipe(Effect.runPromise);
    });
  });
});
