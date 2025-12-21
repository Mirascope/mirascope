import { describe, it, expect } from "@effect/vitest";
import { MockDatabase, TestDatabase } from "@/tests/db";
import { Effect } from "effect";
import { type PublicSession } from "@/db/schema";
import { type PublicUser } from "@/db/schema/users";
import { DatabaseError, NotFoundError, InvalidSessionError } from "@/db/errors";
import { DatabaseService } from "@/db/services";

describe("SessionService", () => {
  describe("create", () => {
    it.effect("creates a session", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          data: { email: "test@example.com", name: "Test User" },
        });

        const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt },
        });

        expect(session).toEqual({
          id: session.id,
          expiresAt,
        } satisfies PublicSession);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .insert(new Error("Database connection failed"))
          .build();

        const result = yield* db.sessions
          .create({
            userId: "user-id",
            data: { userId: "user-id", expiresAt: new Date() },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create session");
      }),
    );
  });

  describe("findById", () => {
    it.effect("finds a session by id", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badUserId = "00000000-0000-0000-0000-000000000001";
        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.sessions
          .findById({ userId: badUserId, sessionId: badId })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `session with sessionId ${badId} not found`,
        );
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.sessions
          .findById({ userId: "user-id", sessionId: "session-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find session");
      }),
    );
  });

  describe("findAll", () => {
    it.effect("finds all sessions", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.sessions
          .findAll({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all sessions");
      }),
    );
  });

  describe("update", () => {
    it.effect("updates a session", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

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

        expect(updated).toEqual({
          id: session.id,
          expiresAt: newExpiresAt,
        } satisfies PublicSession);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("persists updates correctly", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

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

        expect(found.expiresAt.getTime()).toBe(newExpiresAt.getTime());
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

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
          `session with sessionId ${badId} not found`,
        );
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .update(new Error("Database connection failed"))
          .build();

        const result = yield* db.sessions
          .update({
            userId: "user-id",
            sessionId: "session-id",
            data: { expiresAt: new Date() },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update session");
      }),
    );
  });

  describe("delete", () => {
    it.effect("deletes a session", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("removes session from findAll results", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badUserId = "00000000-0000-0000-0000-000000000001";
        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.sessions
          .delete({ userId: badUserId, sessionId: badId })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `session with sessionId ${badId} not found`,
        );
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .delete(new Error("Database connection failed"))
          .build();

        const result = yield* db.sessions
          .delete({ userId: "user-id", sessionId: "session-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete session");
      }),
    );
  });

  describe("findUserBySessionId", () => {
    /**
     * findUserBySessionId flow:
     * 1. fetchSessionWithUser (select join)
     * 2. handleEmptyResult (NotFoundError if no rows)
     * 3. handleExpiredSession (delete + InvalidSessionError if expired)
     * 4. transformToPublicUser (return user)
     */

    it.effect("returns user for valid session", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.sessions
          .findUserBySessionId("session-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find session");
      }),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.sessions
          .findUserBySessionId(badId)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(`Session with id ${badId} not found`);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `InvalidSessionError` for expired session", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          data: { email: "expired@example.com", name: "Expired User" },
        });

        const expiredAt = new Date(Date.now() - 1000);
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: expiredAt },
        });

        const result = yield* db.sessions
          .findUserBySessionId(session.id)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(InvalidSessionError);
        expect(result.message).toBe("Session expired");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("deletes expired session when returning error", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          data: {
            email: "expireddelete@example.com",
            name: "Expired Delete User",
          },
        });

        const expiredAt = new Date(Date.now() - 1000);
        const session = yield* db.sessions.create({
          userId: user.id,
          data: { userId: user.id, expiresAt: expiredAt },
        });

        // This should fail and delete the session
        yield* db.sessions.findUserBySessionId(session.id).pipe(Effect.flip);

        // Verify the session was deleted
        const findResult = yield* db.sessions
          .findById({ userId: user.id, sessionId: session.id })
          .pipe(Effect.flip);

        expect(findResult).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );
  });

  describe("deleteBySessionId", () => {
    it.effect("deletes a session by sessionId only", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when session does not exist", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.sessions
          .deleteBySessionId(badId)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `Session with sessionId ${badId} not found`,
        );
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .delete(new Error("Database connection failed"))
          .build();

        const result = yield* db.sessions
          .deleteBySessionId("session-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete session");
      }),
    );
  });
});
