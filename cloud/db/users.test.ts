import { describe, it, expect, MockDrizzleORM } from "@/tests/db";
import { Effect } from "effect";
import { type PublicUser, users } from "@/db/schema";
import { AlreadyExistsError, DatabaseError, NotFoundError } from "@/errors";
import { DrizzleORM } from "@/db/client";
import { EffectDatabase } from "@/db/database";
import { eq } from "drizzle-orm";

describe("Users", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates a user", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const email = "test@example.com";
        const name = "Test User";
        const user = yield* db.users.create({ data: { email, name } });

        expect(user).toEqual({
          id: user.id,
          email,
          name,
          deletedAt: null,
        } satisfies PublicUser);
      }),
    );

    it.effect("returns `AlreadyExistsError` when email is taken", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const email = "duplicate@example.com";
        yield* db.users.create({ data: { email, name: "First User" } });

        const result = yield* db.users
          .create({ data: { email, name: "Second User" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect(result.message).toBe("User already exists");
      }),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.users
          .create({ data: { email: "test@example.com", name: "Test" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create user");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().insert(new Error("Connection failed")).build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("finds all users", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user1 = yield* db.users.create({
          data: { email: "user1@example.com", name: "User 1" },
        });
        const user2 = yield* db.users.create({
          data: { email: "user2@example.com", name: "User 2" },
        });

        const all = yield* db.users.findAll();

        expect(all).toEqual([user1, user2] satisfies PublicUser[]);
      }),
    );

    it.effect("returns empty array when no users exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const all = yield* db.users.findAll();

        expect(all).toEqual([]);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.users.findAll().pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get users");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Connection failed")).build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findById
  // ===========================================================================

  describe("findById", () => {
    it.effect("finds a user by id", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "find@example.com", name: "Find User" },
        });
        const found = yield* db.users.findById({ userId: user.id });

        expect(found).toEqual(user);
      }),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.users
          .findById({ userId: badId })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("User not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.users
          .findById({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get user");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Connection failed")).build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // update
  // ===========================================================================

  describe("update", () => {
    it.effect("updates a user", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

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
          deletedAt: null,
        } satisfies PublicUser);
      }),
    );

    it.effect("persists updates correctly", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const created = yield* db.users.create({
          data: { email: "persist@example.com", name: "Original" },
        });

        yield* db.users.update({
          userId: created.id,
          data: { name: "Persisted" },
        });

        const found = yield* db.users.findById({ userId: created.id });

        expect(found.name).toBe("Persisted");
      }),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.users
          .update({ userId: badId, data: { name: "Should Fail" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("User not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.users
          .update({ userId: "user-id", data: { name: "Test" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update user");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().update(new Error("Connection failed")).build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // delete (soft deletion)
  // ===========================================================================

  describe("delete (soft deletion)", () => {
    it.effect("soft-deletes a user (PII replaced)", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const created = yield* db.users.create({
          data: { email: "delete@example.com", name: "Delete User" },
        });

        yield* db.users.delete({ userId: created.id });

        const result = yield* db.users.findById({ userId: created.id });

        expect(result.name).toBeNull();
        expect(result.email).toBe(`deleted-${created.id}@deleted.local`);
      }),
    );

    it.effect("includes deleted user from findAll results", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const created = yield* db.users.create({
          data: { email: "deleteall@example.com", name: "Delete All User" },
        });

        yield* db.users.delete({ userId: created.id });

        const all = yield* db.users.findAll();

        expect(all.find((u) => u.id === created.id)).toBeDefined();
      }),
    );

    it.effect("replaces PII with placeholders on deletion", () =>
      Effect.gen(function* () {
        const client = yield* DrizzleORM;
        const db = yield* EffectDatabase;

        const created = yield* db.users.create({
          data: { email: "pii@example.com", name: "PII User" },
        });

        yield* db.users.delete({ userId: created.id });

        const [deleted] = yield* client
          .select()
          .from(users)
          .where(eq(users.id, created.id))
          .limit(1);

        expect(deleted.id).toBe(created.id);
        expect(deleted.email).toBe(`deleted-${created.id}@deleted.local`);
      }),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.users
          .delete({ userId: badId })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("User not found");
      }),
    );

    it.effect(
      "returns `NotFoundError` when deleting already-deleted user",
      () =>
        Effect.gen(function* () {
          const db = yield* EffectDatabase;

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
        }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.users
          .delete({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete user");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .update(new Error("Connection failed")) // soft delete uses update
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findByEmail
  // ===========================================================================

  describe("findByEmail", () => {
    it.effect("finds a user by email", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const email = "findbyemail@example.com";
        const name = "Find By Email User";
        const created = yield* db.users.create({ data: { email, name } });

        const found = yield* db.users.findByEmail(email);

        expect(found).toEqual(created);
      }),
    );

    it.effect("returns `NotFoundError` when email does not exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.users
          .findByEmail("nonexistent@example.com")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("User not found");
      }),
    );

    it.effect("returns `NotFoundError` for deleted user", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const email = "deletedfind@example.com";
        const user = yield* db.users.create({
          data: { email, name: "Will Be Deleted" },
        });

        yield* db.users.delete({ userId: user.id });

        // The original email no longer exists (PII replaced)
        const result = yield* db.users.findByEmail(email).pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.users
          .findByEmail("test@example.com")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find user by email");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Connection failed")).build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // count
  // ===========================================================================

  describe("count", () => {
    it.effect("returns 0 when no users exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const count = yield* db.users.count();

        expect(count).toBe(0);
      }),
    );

    it.effect("counts non-deleted users", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        yield* db.users.create({
          data: { email: "count1@example.com", name: "Count 1" },
        });
        yield* db.users.create({
          data: { email: "count2@example.com", name: "Count 2" },
        });
        yield* db.users.create({
          data: { email: "count3@example.com", name: "Count 3" },
        });

        const count = yield* db.users.count();

        expect(count).toBe(3);
      }),
    );

    it.effect("excludes soft-deleted users from count", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user1 = yield* db.users.create({
          data: { email: "countdel1@example.com", name: "Count Del 1" },
        });
        yield* db.users.create({
          data: { email: "countdel2@example.com", name: "Count Del 2" },
        });

        yield* db.users.delete({ userId: user1.id });

        const count = yield* db.users.count();

        expect(count).toBe(1);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.users.count().pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to count users");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Connection failed")).build(),
        ),
      ),
    );

    it.effect("returns 0 when count is undefined", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const count = yield* db.users.count();

        expect(count).toBe(0);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select([{ count: undefined }]).build(),
        ),
      ),
    );
  });
});
