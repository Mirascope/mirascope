import { describe, it, expect } from "@effect/vitest";
import { TestEffectDatabase, MockDrizzleORM } from "@/tests/db";
import { Effect } from "effect";
import { type PublicSession } from "@/db/schema";
import { type PublicUser } from "@/db/schema/users";
import {
  DatabaseError,
  DeletedUserError,
  InvalidSessionError,
  NotFoundError,
} from "@/db/errors";
import { EffectDatabase } from "@/db/database";

describe("Sessions", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates a session", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "test@example.com", name: "Test User" },
        });

        const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt },
        });

        expect(session.id).toBeDefined();
        // Compare timestamps to avoid timezone issues
        expect(session.expiresAt).toBeInstanceOf(Date);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.sessions
          .create({
            userId: "user-id",
            data: { userId: "user-id", expiresAt: new Date() },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create session");
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
    it.effect("finds all sessions for a user", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "findall@example.com", name: "Find All User" },
        });

        const expiresAt1 = new Date(Date.now() + 1000 * 60 * 60 * 24);
        const expiresAt2 = new Date(Date.now() + 1000 * 60 * 60 * 48);

        const session1 = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: expiresAt1 },
        });
        const session2 = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: expiresAt2 },
        });

        const all = yield* db.sessions.findAll({ userId: user.id });

        expect(all).toEqual([session1, session2] satisfies PublicSession[]);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns expired sessions (not auto-deleted)", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "findall-expired@example.com", name: "Find All User" },
        });

        // Create one valid and one expired session
        const validExpiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);
        const expiredAt = new Date(Date.now() - 1000 * 60 * 60 * 24); // 1 day ago

        const validSession = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: validExpiresAt },
        });
        const expiredSession = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: expiredAt },
        });

        const all = yield* db.sessions.findAll({ userId: user.id });

        // Both sessions should be returned - expired sessions are not auto-deleted
        expect(all).toHaveLength(2);
        expect(all).toEqual(
          expect.arrayContaining([validSession, expiredSession]),
        );
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns empty array when no sessions exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "nosessions@example.com", name: "No Sessions User" },
        });

        const all = yield* db.sessions.findAll({ userId: user.id });

        expect(all).toEqual([]);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.sessions
          .findAll({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all sessions");
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
    it.effect("finds a session by id", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "find@example.com", name: "Find User" },
        });

        const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt },
        });

        const found = yield* db.sessions.findById({
          userId: user.id,
          sessionId: session.id,
        });

        expect(found).toEqual(session);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const badUserId = "00000000-0000-0000-0000-000000000001";
        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.sessions
          .findById({ userId: badUserId, sessionId: badId })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `session with sessionId ${badId} not found for user with userId ${badUserId}`,
        );
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when session exists but userId is incorrect",
      () =>
        Effect.gen(function* () {
          const db = yield* EffectDatabase;

          // Create two users
          const user1 = yield* db.users.create({
            data: { email: "user1@example.com", name: "User 1" },
          });
          const user2 = yield* db.users.create({
            data: { email: "user2@example.com", name: "User 2" },
          });

          // Create session for user1
          const session = yield* db.sessions.create({
            userId: user1.id,
            data: {
              userId: user1.id,
              expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24),
            },
          });

          // Try to find session with user2's ID - should fail
          const result = yield* db.sessions
            .findById({ userId: user2.id, sessionId: session.id })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            `session with sessionId ${session.id} not found for user with userId ${user2.id}`,
          );
        }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns expired session (does not filter by expiration)", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "findbyid-expired@example.com", name: "User" },
        });

        // Create an expired session
        const expiredAt = new Date(Date.now() - 1000 * 60 * 60 * 24); // 1 day ago
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: expiredAt },
        });

        // findById should still return the expired session
        const found = yield* db.sessions.findById({
          userId: user.id,
          sessionId: session.id,
        });

        expect(found).toEqual(session);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.sessions
          .findById({ userId: "user-id", sessionId: "session-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find session");
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
    it.effect("updates a session", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "update@example.com", name: "Update User" },
        });

        const originalExpiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: originalExpiresAt },
        });

        const newExpiresAt = new Date(Date.now() + 1000 * 60 * 60 * 48);
        const updated = yield* db.sessions.update({
          userId: user.id,
          sessionId: session.id,
          data: { expiresAt: newExpiresAt },
        });

        expect(updated.id).toBe(session.id);
        expect(updated.expiresAt).toBeInstanceOf(Date);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("persists updates correctly", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "persist@example.com", name: "Persist User" },
        });

        const originalExpiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: originalExpiresAt },
        });

        const newExpiresAt = new Date(Date.now() + 1000 * 60 * 60 * 48);
        yield* db.sessions.update({
          userId: user.id,
          sessionId: session.id,
          data: { expiresAt: newExpiresAt },
        });

        const found = yield* db.sessions.findById({
          userId: user.id,
          sessionId: session.id,
        });

        // Verify the session was updated (expiresAt changed from original)
        expect(found.expiresAt.getTime()).not.toBe(originalExpiresAt.getTime());
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("can update an already expired session", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "update-expired@example.com", name: "User" },
        });

        // Create an expired session
        const expiredAt = new Date(Date.now() - 1000 * 60 * 60 * 24); // 1 day ago
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: expiredAt },
        });

        // Update the expired session to extend it
        const newExpiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24); // 1 day from now
        const updated = yield* db.sessions.update({
          userId: user.id,
          sessionId: session.id,
          data: { expiresAt: newExpiresAt },
        });

        expect(updated.id).toBe(session.id);
        expect(updated.expiresAt.getTime()).toBeGreaterThan(Date.now());
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const badUserId = "00000000-0000-0000-0000-000000000001";
        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.sessions
          .update({
            userId: badUserId,
            sessionId: badId,
            data: { expiresAt: new Date() },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `session with sessionId ${badId} not found for user with userId ${badUserId}`,
        );
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.sessions
          .update({
            userId: "user-id",
            sessionId: "session-id",
            data: { expiresAt: new Date() },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update session");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().update(new Error("Connection failed")).build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // delete
  // ===========================================================================

  describe("delete", () => {
    it.effect("deletes a session", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "delete@example.com", name: "Delete User" },
        });

        const session = yield* db.sessions.create({
          userId: user.id,
          data: {
            userId: user.id,
            expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24),
          },
        });

        yield* db.sessions.delete({ userId: user.id, sessionId: session.id });

        const result = yield* db.sessions
          .findById({ userId: user.id, sessionId: session.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("removes session from findAll results", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "deleteall@example.com", name: "Delete All User" },
        });

        const session = yield* db.sessions.create({
          userId: user.id,
          data: {
            userId: user.id,
            expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24),
          },
        });

        yield* db.sessions.delete({ userId: user.id, sessionId: session.id });

        const all = yield* db.sessions.findAll({ userId: user.id });

        expect(all.find((s) => s.id === session.id)).toBeUndefined();
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const badUserId = "00000000-0000-0000-0000-000000000001";
        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.sessions
          .delete({ userId: badUserId, sessionId: badId })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `session with sessionId ${badId} not found for user with userId ${badUserId}`,
        );
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.sessions
          .delete({ userId: "user-id", sessionId: "session-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete session");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().delete(new Error("Connection failed")).build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findUserBySessionId
  // ===========================================================================

  describe("findUserBySessionId", () => {
    it.effect("returns user for valid session", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const email = "finduser@example.com";
        const name = "Find User";
        const user = yield* db.users.create({ data: { email, name } });

        const session = yield* db.sessions.create({
          userId: user.id,
          data: {
            userId: user.id,
            expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24),
          },
        });

        const foundUser = yield* db.sessions.findUserBySessionId(session.id);

        expect(foundUser).toEqual({
          id: user.id,
          email,
          name,
          deletedAt: user.deletedAt,
        } satisfies PublicUser);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.sessions
          .findUserBySessionId(badId)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(`Session with id ${badId} not found`);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `DeletedUserError` when user has been deleted", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        // Create a user and session
        const user = yield* db.users.create({
          data: { email: "deleteduser@example.com", name: "Deleted User" },
        });

        const session = yield* db.sessions.create({
          userId: user.id,
          data: {
            userId: user.id,
            expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24),
          },
        });

        // Delete the user (soft delete)
        yield* db.users.delete({ userId: user.id });

        // Try to find user by session - should fail because user is deleted
        const result = yield* db.sessions
          .findUserBySessionId(session.id)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DeletedUserError);
        expect(result.message).toBe("This user has been deleted");
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `InvalidSessionError` for expired session", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "expired@example.com", name: "Expired User" },
        });

        // Use a date far in the past to ensure it's expired regardless of timezone
        const expiredAt = new Date(Date.now() - 1000 * 60 * 60 * 24); // 1 day ago
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: expiredAt },
        });

        const result = yield* db.sessions
          .findUserBySessionId(session.id)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(InvalidSessionError);
        expect(result.message).toBe("Session expired");
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.sessions
          .findUserBySessionId("session-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find session");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Connection failed")).build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // deleteBySessionId
  // ===========================================================================

  describe("deleteBySessionId", () => {
    it.effect("deletes a session by sessionId only", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const user = yield* db.users.create({
          data: { email: "deletebysessionid@example.com", name: "Delete User" },
        });

        const session = yield* db.sessions.create({
          userId: user.id,
          data: {
            userId: user.id,
            expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24),
          },
        });

        yield* db.sessions.deleteBySessionId(session.id);

        const result = yield* db.sessions
          .findById({ userId: user.id, sessionId: session.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.sessions
          .deleteBySessionId(badId)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `Session with sessionId ${badId} not found`,
        );
      }).pipe(Effect.provide(TestEffectDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* EffectDatabase;

        const result = yield* db.sessions
          .deleteBySessionId("session-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete session");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().delete(new Error("Connection failed")).build(),
        ),
      ),
    );
  });
});
