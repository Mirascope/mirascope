import { describe, it, expect } from "vitest";
import { withTestDatabase } from "@/tests/db";
import { Effect } from "effect";
import { NotFoundError, DatabaseError } from "../errors";
import { UserService } from "./users";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import type * as schema from "../schema";

// Helper to create a UserService with a mock database that throws errors
function createUserServiceWithErroringDb(error: Error): UserService {
  // Create a mock that properly rejects for all query types
  const createRejectingPromise = () => Promise.reject(error);

  const mockDb = {
    select: () => ({
      from: () => {
        const promise = createRejectingPromise();
        return {
          where: () => ({
            limit: () => promise,
          }),
          // For findAll, return the promise directly (it's awaitable)
          then: promise.then.bind(promise),
          catch: promise.catch.bind(promise),
        };
      },
    }),
    delete: () => ({
      where: () => ({
        returning: () => createRejectingPromise(),
      }),
    }),
    insert: () => ({
      values: () => ({
        returning: () => createRejectingPromise(),
      }),
    }),
    update: () => ({
      set: () => ({
        where: () => ({
          returning: () => createRejectingPromise(),
        }),
      }),
    }),
  } as unknown as PostgresJsDatabase<typeof schema>;

  return new UserService(mockDb);
}

describe("BaseService error handling", () => {
  describe("NotFoundError", () => {
    it(
      "findById returns NotFoundError for non-existent record",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(
            db.users.findById("00000000-0000-0000-0000-000000000000"),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(NotFoundError);
            if (result.left instanceof NotFoundError) {
              expect(result.left.message).toContain("not found");
              expect(result.left.resource).toBe("user");
            }
          }
        }),
      ),
    );

    it(
      "update returns NotFoundError for non-existent record",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(
            db.users.update("00000000-0000-0000-0000-000000000000", {
              name: "Updated",
            }),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(NotFoundError);
            if (result.left instanceof NotFoundError) {
              expect(result.left.message).toContain("not found");
              expect(result.left.resource).toBe("user");
            }
          }
        }),
      ),
    );

    it(
      "delete returns NotFoundError for non-existent record",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(
            db.users.delete("00000000-0000-0000-0000-000000000000"),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(NotFoundError);
            if (result.left instanceof NotFoundError) {
              expect(result.left.message).toContain("not found");
              expect(result.left.resource).toBe("user");
            }
          }
        }),
      ),
    );
  });

  describe("DatabaseError", () => {
    it(
      "create returns DatabaseError on unique constraint violation",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          // Create a user first
          yield* db.users.create({
            email: "duplicate@example.com",
            name: "First User",
          });

          // Try to create another user with the same email (unique constraint violation)
          const result = yield* Effect.either(
            db.users.create({
              email: "duplicate@example.com",
              name: "Second User",
            }),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain("Failed to create");
          }
        }),
      ),
    );

    it("findById returns DatabaseError on database query failure", () => {
      return Effect.gen(function* () {
        // Create a UserService with a database that throws errors
        const erroringService = createUserServiceWithErroringDb(
          new Error("Database connection failed"),
        );

        const result = yield* Effect.either(
          erroringService.findById("test-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to find");
        }
      }).pipe(Effect.runPromise);
    });

    it(
      "update returns DatabaseError on unique constraint violation",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          // Create two users with different emails
          const user1 = yield* db.users.create({
            email: "user1@example.com",
            name: "User 1",
          });
          yield* db.users.create({
            email: "user2@example.com",
            name: "User 2",
          });

          // Try to update user1's email to user2's email (unique constraint violation)
          const result = yield* Effect.either(
            db.users.update(user1.id, {
              email: "user2@example.com",
            }),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain("Failed to update");
          }
        }),
      ),
    );

    it("delete returns DatabaseError on database query failure", () => {
      return Effect.gen(function* () {
        // Create a UserService with a database that throws errors
        const erroringService = createUserServiceWithErroringDb(
          new Error("Database connection failed"),
        );

        const result = yield* Effect.either(erroringService.delete("test-id"));
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to delete");
        }
      }).pipe(Effect.runPromise);
    });

    it("findAll returns DatabaseError on database query failure", () => {
      return Effect.gen(function* () {
        // Create a UserService with a database that throws errors
        const erroringService = createUserServiceWithErroringDb(
          new Error("Database connection failed"),
        );

        const result = yield* Effect.either(erroringService.findAll());
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to find all");
        }
      }).pipe(Effect.runPromise);
    });
  });
});
