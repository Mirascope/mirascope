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
        const user = yield* db.users.create({ email, name });

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
        yield* db.users.create({ email, name: "First User" });

        const result = yield* db.users
          .create({ email, name: "Second User" })
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
          .create({ email: "test@example.com", name: "Test" })
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
          email: "find@example.com",
          name: "Find User",
        });
        const found = yield* db.users.findById(user.id);

        expect(found).toEqual(user);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.users.findById(badId).pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(`user with id ${badId} not found`);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.users.findById("user-id").pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find user");
      }),
    );
  });

  describe("findAll", () => {
    it.effect("finds all users", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user1 = yield* db.users.create({
          email: "user1@example.com",
          name: "User 1",
        });
        const user2 = yield* db.users.create({
          email: "user2@example.com",
          name: "User 2",
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
        expect(result.message).toBe("Failed to find all users");
      }),
    );
  });

  describe("update", () => {
    it.effect("updates a user", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const created = yield* db.users.create({
          name: "Original Name",
          email: "original@example.com",
        });

        const updatedName = "Updated Name";
        const updatedEmail = "updated@example.com";
        const updated = yield* db.users.update(created.id, {
          name: updatedName,
          email: updatedEmail,
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
          email: "persist@example.com",
          name: "Original",
        });

        yield* db.users.update(created.id, { name: "Persisted" });

        const found = yield* db.users.findById(created.id);

        expect(found.name).toBe("Persisted");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.users
          .update(badId, { name: "Should Fail" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(`user with id ${badId} not found`);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .update(new Error("Database connection failed"))
          .build();

        const result = yield* db.users
          .update("user-id", { name: "Test" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update user");
      }),
    );

    it.effect("returns `DatabaseError` when updating to existing email", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user1 = yield* db.users.create({
          email: "user1@example.com",
          name: "User 1",
        });
        yield* db.users.create({
          email: "user2@example.com",
          name: "User 2",
        });

        const result = yield* db.users
          .update(user1.id, { email: "user2@example.com" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update user");
      }).pipe(Effect.provide(TestDatabase)),
    );
  });

  describe("delete", () => {
    it.effect("deletes a user", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const created = yield* db.users.create({
          email: "delete@example.com",
          name: "Delete User",
        });

        yield* db.users.delete(created.id);

        const result = yield* db.users.findById(created.id).pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("removes user from findAll results", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const created = yield* db.users.create({
          email: "deleteall@example.com",
          name: "Delete All User",
        });

        yield* db.users.delete(created.id);

        const all = yield* db.users.findAll();

        expect(all.find((u) => u.id === created.id)).toBeUndefined();
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.users.delete(badId).pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(`user with id ${badId} not found`);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .delete(new Error("Database connection failed"))
          .build();

        const result = yield* db.users.delete("user-id").pipe(Effect.flip);

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
        const created = yield* db.users.create({
          email,
          name,
        });

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
