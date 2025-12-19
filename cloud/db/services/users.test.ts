import { describe, it, expect } from "@effect/vitest";
import { MockDatabase, TestDatabase } from "@/tests/db";
import { Effect } from "effect";
import { type PublicUser } from "@/db/schema";
import { AlreadyExistsError, DatabaseError, NotFoundError } from "@/db/errors";
import { DatabaseService } from "@/db/services";

describe("UserService", () => {
  describe("create", () => {
    it.effect("creates a user", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const email = "test@example.com";
        const name = "Test User";
        const user = yield* db.users.create({ data: { email, name } });

        expect(user).toEqual({
          id: user.id,
          email,
          name,
        } satisfies PublicUser);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `AlreadyExistsError` when email is taken", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const email = "duplicate@example.com";
        yield* db.users.create({ data: { email, name: "First User" } });

        const result = yield* db.users
          .create({ data: { email, name: "Second User" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect(result.message).toBe("user already exists");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .insert(new Error("Database connection failed"))
          .build();

        const result = yield* db.users
          .create({ data: { email: "test@example.com", name: "Test" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create user");
      }),
    );
  });

  describe("findById", () => {
    it.effect("finds a user by id", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          data: { email: "find@example.com", name: "Find User" },
        });
        const found = yield* db.users.findById({ userId: user.id });

        expect(found).toEqual(user);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.users
          .findById({ userId: badId })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("User not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.users
          .findById({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get user");
      }),
    );
  });

  describe("findAll", () => {
    it.effect("finds all users", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user1 = yield* db.users.create({
          data: { email: "user1@example.com", name: "User 1" },
        });
        const user2 = yield* db.users.create({
          data: { email: "user2@example.com", name: "User 2" },
        });

        const all = yield* db.users.findAll();

        expect(all).toEqual([user1, user2] satisfies PublicUser[]);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.users.findAll().pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get users");
      }),
    );
  });

  describe("update", () => {
    it.effect("updates a user", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const created = yield* db.users.create({
          data: { name: "Original Name", email: "original@example.com" },
        });

        const updatedName = "Updated Name";
        const updatedEmail = "updated@example.com";
        const updated = yield* db.users.update({
          userId: created.id,
          data: { name: updatedName, email: updatedEmail },
        });

        expect(updated).toEqual({
          id: created.id,
          name: updatedName,
          email: updatedEmail,
        } satisfies PublicUser);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("persists updates correctly", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const created = yield* db.users.create({
          data: { email: "persist@example.com", name: "Original" },
        });

        yield* db.users.update({
          userId: created.id,
          data: { name: "Persisted" },
        });

        const found = yield* db.users.findById({ userId: created.id });

        expect(found.name).toBe("Persisted");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.users
          .update({ userId: badId, data: { name: "Should Fail" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(`user with userId ${badId} not found`);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .update(new Error("Database connection failed"))
          .build();

        const result = yield* db.users
          .update({ userId: "user-id", data: { name: "Test" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update user");
      }),
    );

    it.effect("returns `DatabaseError` when updating to existing email", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user1 = yield* db.users.create({
          data: { email: "user1@example.com", name: "User 1" },
        });
        yield* db.users.create({
          data: { email: "user2@example.com", name: "User 2" },
        });

        const result = yield* db.users
          .update({ userId: user1.id, data: { email: "user2@example.com" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update user");
      }).pipe(Effect.provide(TestDatabase)),
    );
  });

  describe("delete (soft deletion)", () => {
    it.effect("soft-deletes a user (no longer found by findById)", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const created = yield* db.users.create({
          data: { email: "delete@example.com", name: "Delete User" },
        });

        yield* db.users.delete({ userId: created.id });

        const result = yield* db.users
          .findById({ userId: created.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("removes user from findAll results", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const created = yield* db.users.create({
          data: { email: "deleteall@example.com", name: "Delete All User" },
        });

        yield* db.users.delete({ userId: created.id });

        const all = yield* db.users.findAll();

        expect(all.find((u) => u.id === created.id)).toBeUndefined();
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("replaces PII with placeholders on deletion", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const created = yield* db.users.create({
          data: { email: "pii@example.com", name: "PII User" },
        });

        yield* db.users.delete({ userId: created.id });

        // Use createOrUpdate with the placeholder email to verify it exists
        // (This is a workaround since findById filters deleted users)
        const placeholderEmail = `deleted-${created.id}@deleted.local`;
        const reactivated = yield* db.users.createOrUpdate({
          email: placeholderEmail,
          name: "Reactivated",
        });

        // The UUID should be preserved (same id)
        expect(reactivated.id).toBe(created.id);
        // Email should be the placeholder
        expect(reactivated.email).toBe(placeholderEmail);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.users
          .delete({ userId: badId })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("User not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when deleting already-deleted user",
      () =>
        Effect.gen(function* () {
          const db = yield* DatabaseService;

          const created = yield* db.users.create({
            data: { email: "double-delete@example.com", name: "Double Delete" },
          });

          // First delete succeeds
          yield* db.users.delete({ userId: created.id });

          // Second delete fails with NotFoundError
          const result = yield* db.users
            .delete({ userId: created.id })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("User not found");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .update(new Error("Database connection failed"))
          .build();

        const result = yield* db.users
          .delete({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete user");
      }),
    );
  });

  describe("createOrUpdate", () => {
    it.effect("creates a new user", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const email = "newuser@example.com";
        const name = "New User";
        const user = yield* db.users.createOrUpdate({ email, name });

        expect(user).toEqual({
          id: user.id,
          email,
          name,
        } satisfies PublicUser);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("updates existing user by email", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const email = "existing@example.com";
        const name = "Original Name";
        const created = yield* db.users.create({ data: { email, name } });

        const updatedName = "Updated Name";
        const updated = yield* db.users.createOrUpdate({
          email,
          name: updatedName,
        });

        expect(updated).toEqual({
          id: created.id,
          email,
          name: updatedName,
        } satisfies PublicUser);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("handles undefined name", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.createOrUpdate({
          email: "undefinedname@example.com",
        });

        expect(user).toBeDefined();
        expect(user.id).toBeDefined();
        expect(user.email).toBe("undefinedname@example.com");
        expect(user.name).toBeNull();
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when upsert fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .insert(new Error("Database connection failed"))
          .build();

        const result = yield* db.users
          .createOrUpdate({ email: "test@example.com", name: "Test" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create or update user");
      }),
    );

    it.effect("returns `DatabaseError` when fetch after upsert fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // upsert succeeds
          .insert([])
          // fetch fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.users
          .createOrUpdate({ email: "test@example.com", name: "Test" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create or update user");
      }),
    );

    it.effect("returns `DatabaseError` when user not found after upsert", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // upsert succeeds
          .insert([])
          // fetch returns empty
          .select([])
          .build();

        const result = yield* db.users
          .createOrUpdate({ email: "test@example.com", name: "Test" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create or update user");
      }),
    );
  });
});
