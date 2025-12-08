import { describe, it, expect } from "vitest";
import { withTestDatabase, withErroringService } from "@/tests/db";
import { Effect } from "effect";
import { DatabaseError } from "@/db/errors";
import { SessionService } from "@/db/services/sessions";

describe("SessionService", () => {
  it(
    "should support basic CRUD",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);

        const created = yield* db.sessions.create({
          userId: user.id,
          expiresAt,
        });
        expect(created).toBeDefined();
        expect(created.id).toBeDefined();
        expect(created.expiresAt).toBeInstanceOf(Date);

        const sessionId = created.id;

        const found = yield* db.sessions.findById(sessionId);
        expect(found).toBeDefined();
        expect(found?.id).toBe(sessionId);
        expect(found?.expiresAt.getTime()).toBe(expiresAt.getTime());

        const all = yield* db.sessions.findAll();
        expect(Array.isArray(all)).toBe(true);
        expect(all.find((s) => s.id === sessionId)).toBeDefined();

        const newExpiresAt = new Date(Date.now() + 1000 * 60 * 60 * 48);

        const updated = yield* db.sessions.update(sessionId, {
          expiresAt: newExpiresAt,
        });
        expect(updated).toBeDefined();
        expect(updated?.id).toBe(sessionId);
        expect(updated?.expiresAt.getTime()).toBe(newExpiresAt.getTime());

        const afterUpdate = yield* db.sessions.findById(sessionId);
        expect(afterUpdate).toBeDefined();
        expect(afterUpdate?.expiresAt.getTime()).toBe(newExpiresAt.getTime());

        yield* db.sessions.delete(sessionId);

        const afterDeleteResult = yield* Effect.either(
          db.sessions.findById(sessionId),
        );
        expect(afterDeleteResult._tag).toBe("Left");
        if (afterDeleteResult._tag === "Left") {
          expect(afterDeleteResult.left._tag).toBe("NotFoundError");
        }

        const afterDeleteAll = yield* db.sessions.findAll();
        expect(afterDeleteAll.find((s) => s.id === sessionId)).toBeUndefined();
      }),
    ),
  );

  it(
    "isValid should return true for valid session",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const user = yield* db.users.create({
          email: "valid@example.com",
          name: "Valid User",
        });

        const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);
        const session = yield* db.sessions.create({
          userId: user.id,
          expiresAt,
        });

        const isValid = yield* db.sessions.isValid(session.id);
        expect(isValid).toBe(true);
      }),
    ),
  );

  it(
    "isValid should return false for non-existent session",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const isValid = yield* db.sessions.isValid(
          "00000000-0000-0000-0000-000000000000",
        );
        expect(isValid).toBe(false);
      }),
    ),
  );

  it(
    "isValid should return false and delete expired session",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const user = yield* db.users.create({
          email: "expired@example.com",
          name: "Expired User",
        });

        const expiredAt = new Date(Date.now() - 1000);
        const session = yield* db.sessions.create({
          userId: user.id,
          expiresAt: expiredAt,
        });

        const isValid = yield* db.sessions.isValid(session.id);
        expect(isValid).toBe(false);

        const findResult = yield* Effect.either(
          db.sessions.findById(session.id),
        );
        expect(findResult._tag).toBe("Left");
      }),
    ),
  );

  it(
    "findUserBySessionId should return user for valid session",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const user = yield* db.users.create({
          email: "finduser@example.com",
          name: "Find User",
        });

        const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);
        const session = yield* db.sessions.create({
          userId: user.id,
          expiresAt,
        });

        const foundUser = yield* db.sessions.findUserBySessionId(session.id);
        expect(foundUser).toBeDefined();
        expect(foundUser.id).toBe(user.id);
        expect(foundUser.email).toBe("finduser@example.com");
        expect(foundUser.name).toBe("Find User");
      }),
    ),
  );

  it(
    "findUserBySessionId should fail for non-existent session",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const result = yield* Effect.either(
          db.sessions.findUserBySessionId(
            "00000000-0000-0000-0000-000000000000",
          ),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left._tag).toBe("NotFoundError");
        }
      }),
    ),
  );

  it(
    "findUserBySessionId should fail and delete expired session",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const user = yield* db.users.create({
          email: "expiredfind@example.com",
          name: "Expired Find User",
        });

        const expiredAt = new Date(Date.now() - 1000);
        const session = yield* db.sessions.create({
          userId: user.id,
          expiresAt: expiredAt,
        });

        const result = yield* Effect.either(
          db.sessions.findUserBySessionId(session.id),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left._tag).toBe("NotFoundError");
        }

        const findResult = yield* Effect.either(
          db.sessions.findById(session.id),
        );
        expect(findResult._tag).toBe("Left");
      }),
    ),
  );

  describe("DatabaseError handling", () => {
    it(
      "isValid returns DatabaseError on database query failure",
      withErroringService(SessionService, (service) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(
            service.isValid("test-session-id"),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain(
              "Failed to check session validity",
            );
          }
        }),
      ),
    );

    it(
      "findUserBySessionId returns DatabaseError on database query failure",
      withErroringService(SessionService, (service) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(
            service.findUserBySessionId("test-session-id"),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain("Failed to find session");
          }
        }),
      ),
    );
  });
});
