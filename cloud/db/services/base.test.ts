import { describe, it, expect } from "vitest";
import { withTestDatabase, withErroringService } from "@/tests/db";
import { Effect } from "effect";
import {
  NotFoundError,
  DatabaseError,
  AlreadyExistsError,
  PermissionDeniedError,
} from "@/db/errors";
import { UserService } from "@/db/services/users";

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

  describe("AlreadyExistsError", () => {
    it(
      "create returns AlreadyExistsError on unique constraint violation",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          yield* db.users.create({
            email: "duplicate@example.com",
            name: "First User",
          });

          const result = yield* Effect.either(
            db.users.create({
              email: "duplicate@example.com",
              name: "Second User",
            }),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(AlreadyExistsError);
            if (result.left instanceof AlreadyExistsError) {
              expect(result.left.message).toContain("already exists");
              expect(result.left.resource).toBe("user");
            }
          }
        }),
      ),
    );
  });

  describe("DatabaseError", () => {
    it(
      "create returns DatabaseError on non-unique database failure",
      withErroringService(UserService, (service) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(
            service.create({ email: "test@example.com", name: "Test" }),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain("Failed to create");
          }
        }),
      ),
    );

    it(
      "findById returns DatabaseError on database query failure",
      withErroringService(UserService, (service) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(service.findById("test-id"));
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain("Failed to find");
          }
        }),
      ),
    );

    it(
      "update returns DatabaseError on unique constraint violation",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user1 = yield* db.users.create({
            email: "user1@example.com",
            name: "User 1",
          });
          yield* db.users.create({
            email: "user2@example.com",
            name: "User 2",
          });

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

    it(
      "delete returns DatabaseError on database query failure",
      withErroringService(UserService, (service) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(service.delete("test-id"));
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain("Failed to delete");
          }
        }),
      ),
    );

    it(
      "findAll returns DatabaseError on database query failure",
      withErroringService(UserService, (service) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(service.findAll());
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain("Failed to find all");
          }
        }),
      ),
    );
  });
});

describe("BaseAuthenticatedService", () => {
  describe("permission checks", () => {
    it(
      "should deny access to non-members",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "owner@example.com",
            name: "Owner",
          });

          const otherUser = yield* db.users.create({
            email: "other@example.com",
            name: "Other User",
          });

          const org = yield* db.organizations.create(
            { name: "Test Org" },
            user.id,
          );

          // Other user tries to read - should fail
          const result = yield* Effect.either(
            db.organizations.findById(org.id, otherUser.id),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(PermissionDeniedError);
          }
        }),
      ),
    );
  });
});
