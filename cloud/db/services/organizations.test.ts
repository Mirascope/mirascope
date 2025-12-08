import { describe, it, expect } from "vitest";
import {
  withTestDatabase,
  withErroringService,
  createPartialMockDatabase,
} from "@/tests/db";
import { Effect } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { OrganizationService } from "@/db/services/organizations";

describe("OrganizationService", () => {
  describe("create", () => {
    it(
      "should create an organization and membership",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const created = yield* db.organizations.create(
            { name: "Test Organization" },
            user.id,
          );

          expect(created).toBeDefined();
          expect(created.id).toBeDefined();
          expect(created.name).toBe("Test Organization");
          expect(created.role).toBe("OWNER");
        }),
      ),
    );

    it(
      "should return AlreadyExistsError when name is taken",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          yield* db.organizations.create({ name: "Duplicate Org" }, user.id);

          const result = yield* Effect.either(
            db.organizations.create({ name: "Duplicate Org" }, user.id),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(AlreadyExistsError);
            expect(result.left.message).toBe(
              "An organization with this name already exists",
            );
          }
        }),
      ),
    );
  });

  describe("findById", () => {
    it(
      "should retrieve organization when user is a member",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const created = yield* db.organizations.create(
            { name: "Find By Id Org" },
            user.id,
          );

          const result = yield* db.organizations.findById(created.id, user.id);
          expect(result).toBeDefined();
          expect(result.id).toBe(created.id);
          expect(result.name).toBe("Find By Id Org");
        }),
      ),
    );

    it(
      "should return PermissionDeniedError when user is not a member",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const otherUser = yield* db.users.create({
            email: "other@example.com",
            name: "Other User",
          });

          const created = yield* db.organizations.create(
            { name: "Non Member Read Org" },
            user.id,
          );

          const result = yield* Effect.either(
            db.organizations.findById(created.id, otherUser.id),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(PermissionDeniedError);
            expect(result.left.message).toBe(
              "You do not have permission to read this organization",
            );
          }
        }),
      ),
    );
  });

  describe("update", () => {
    it(
      "should update organization when user is admin or owner",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const created = yield* db.organizations.create(
            { name: "Update Org" },
            user.id,
          );

          const updated = yield* db.organizations.update(
            created.id,
            { name: "Updated Org Name" },
            user.id,
          );
          expect(updated).toBeDefined();
          expect(updated.id).toBe(created.id);
          expect(updated.name).toBe("Updated Org Name");
        }),
      ),
    );

    it(
      "should return PermissionDeniedError when user lacks permission",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const otherUser = yield* db.users.create({
            email: "other@example.com",
            name: "Other User",
          });

          const created = yield* db.organizations.create(
            { name: "Non Member Update Org" },
            user.id,
          );

          const result = yield* Effect.either(
            db.organizations.update(
              created.id,
              { name: "Should Fail" },
              otherUser.id,
            ),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(PermissionDeniedError);
            expect(result.left.message).toBe(
              "You do not have permission to update this organization",
            );
          }
        }),
      ),
    );
  });

  describe("delete", () => {
    it(
      "should delete an organization and its memberships",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const created = yield* db.organizations.create(
            { name: "Delete Test Org" },
            user.id,
          );

          yield* db.organizations.delete(created.id, user.id);

          // Organization should be deleted - trying to find it should fail
          const result = yield* Effect.either(
            db.organizations.findById(created.id, user.id),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            // Could be NotFoundError (not found) or PermissionDeniedError (can't check membership)
            // Since org is deleted, membership is also deleted, so permission check fails
            expect(
              result.left instanceof NotFoundError ||
                result.left instanceof PermissionDeniedError,
            ).toBe(true);
          }
        }),
      ),
    );

    it(
      "should return NotFoundError when organization does not exist",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const result = yield* Effect.either(
            db.organizations.delete(
              "00000000-0000-0000-0000-000000000000",
              user.id,
            ),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(NotFoundError);
            expect(result.left.message).toContain("not found");
          }
        }),
      ),
    );

    it(
      "should return PermissionDeniedError when user is not a member",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const otherUser = yield* db.users.create({
            email: "other@example.com",
            name: "Other User",
          });

          const created = yield* db.organizations.create(
            { name: "Non Member Delete Org" },
            user.id,
          );

          const result = yield* Effect.either(
            db.organizations.delete(created.id, otherUser.id),
          );

          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(PermissionDeniedError);
            expect(result.left.message).toBe(
              "You do not have permission to delete this organization",
            );
          }
        }),
      ),
    );

    it("should return PermissionDeniedError when user is not an owner", () => {
      return Effect.gen(function* () {
        // Mock the database to simulate a user who is a member but not an owner
        let selectCallCount = 0;
        const mockDb = createPartialMockDatabase({
          select: () => {
            selectCallCount++;
            if (selectCallCount === 1) {
              // First call: organization check - return existing org
              return {
                from: () => ({
                  where: () => ({
                    limit: () => Promise.resolve([{ id: "test-org-id" }]),
                  }),
                }),
              };
            }
            // Second call: membership check - return DEVELOPER membership
            return {
              from: () => ({
                where: () => ({
                  limit: () => Promise.resolve([{ role: "DEVELOPER" }]),
                }),
              }),
            };
          },
        });

        const service = new OrganizationService(mockDb);

        const result = yield* Effect.either(
          service.delete("test-org-id", "test-user-id"),
        );

        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(PermissionDeniedError);
          expect(result.left.message).toBe(
            "You do not have permission to delete this organization",
          );
        }
      }).pipe(Effect.runPromise);
    });
  });

  describe("findAll", () => {
    it(
      "should retrieve all organizations for a user",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          yield* db.organizations.create({ name: "Org 1" }, user.id);
          yield* db.organizations.create({ name: "Org 2" }, user.id);

          const organizations = yield* db.organizations.findAll(user.id);
          expect(organizations).toHaveLength(2);
          expect(organizations[0].role).toBe("OWNER");
          expect(organizations[1].role).toBe("OWNER");
        }),
      ),
    );

    it(
      "should return empty array for user with no organizations",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          const organizations = yield* db.organizations.findAll(user.id);
          expect(organizations).toHaveLength(0);
        }),
      ),
    );
  });

  describe("findAll", () => {
    it(
      "should return all organizations the user is a member of",
      withTestDatabase((db) =>
        Effect.gen(function* () {
          const user = yield* db.users.create({
            email: "test@example.com",
            name: "Test User",
          });

          yield* db.organizations.create({ name: "Org A" }, user.id);
          yield* db.organizations.create({ name: "Org B" }, user.id);

          const all = yield* db.organizations.findAll(user.id);
          expect(Array.isArray(all)).toBe(true);
          expect(all.length).toBe(2);
          expect(all.find((o) => o.name === "Org A")).toBeDefined();
          expect(all.find((o) => o.name === "Org B")).toBeDefined();
        }),
      ),
    );
  });

  describe("Error handling", () => {
    it(
      "create returns DatabaseError when check for existing fails",
      withErroringService(OrganizationService, (service) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(
            service.create({ name: "Test Org" }, "test-user-id"),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain(
              "Failed to check for existing organization",
            );
          }
        }),
      ),
    );

    it("findAll returns DatabaseError on database query failure", () => {
      return Effect.gen(function* () {
        const mockDb = createPartialMockDatabase({
          select: () => ({
            from: () => ({
              innerJoin: () => ({
                where: () =>
                  Promise.reject(new Error("Database connection failed")),
              }),
            }),
          }),
        });

        const service = new OrganizationService(mockDb);

        const result = yield* Effect.either(service.findAll("test-user-id"));
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain(
            "Failed to get user organizations",
          );
        }
      }).pipe(Effect.runPromise);
    });

    it(
      "delete returns DatabaseError on database query failure",
      withErroringService(OrganizationService, (service) =>
        Effect.gen(function* () {
          const result = yield* Effect.either(
            service.delete("test-org-id", "test-user-id"),
          );
          expect(result._tag).toBe("Left");
          if (result._tag === "Left") {
            expect(result.left).toBeInstanceOf(DatabaseError);
            expect(result.left.message).toContain(
              "Failed to find organization",
            );
          }
        }),
      ),
    );

    it("create returns DatabaseError when transaction fails", () => {
      return Effect.gen(function* () {
        let selectCallCount = 0;
        const mockDb = createPartialMockDatabase({
          select: () => {
            selectCallCount++;
            // First call returns empty (no existing org)
            if (selectCallCount === 1) {
              return {
                from: () => ({
                  where: () => ({
                    limit: () => Promise.resolve([]),
                  }),
                }),
              };
            }
            throw new Error("Database connection failed");
          },
          insert: () => {
            throw new Error("Transaction failed");
          },
        });

        // Add transaction mock
        (
          mockDb as unknown as { transaction: () => Promise<unknown> }
        ).transaction = () => Promise.reject(new Error("Transaction failed"));

        const service = new OrganizationService(mockDb);

        const result = yield* Effect.either(
          service.create({ name: "Test Org" }, "test-user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain(
            "Failed to create organization",
          );
        }
      }).pipe(Effect.runPromise);
    });

    it("delete returns DatabaseError when membership check fails", () => {
      return Effect.gen(function* () {
        let selectCallCount = 0;
        const mockDb = createPartialMockDatabase({
          select: () => {
            selectCallCount++;
            if (selectCallCount === 1) {
              // First call: organization check - return existing org
              return {
                from: () => ({
                  where: () => ({
                    limit: () => Promise.resolve([{ id: "test-org-id" }]),
                  }),
                }),
              };
            }
            // Second call: membership check - fail
            throw new Error("Database connection failed");
          },
        });

        const service = new OrganizationService(mockDb);

        const result = yield* Effect.either(
          service.delete("test-org-id", "test-user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain("Failed to check membership");
        }
      }).pipe(Effect.runPromise);
    });

    it("delete returns DatabaseError when delete transaction fails", () => {
      return Effect.gen(function* () {
        let selectCallCount = 0;
        const mockDb = createPartialMockDatabase({
          select: () => {
            selectCallCount++;
            if (selectCallCount === 1) {
              // First call: organization check - return existing org
              return {
                from: () => ({
                  where: () => ({
                    limit: () => Promise.resolve([{ id: "test-org-id" }]),
                  }),
                }),
              };
            }
            // Second call: membership check - return OWNER membership
            return {
              from: () => ({
                where: () => ({
                  limit: () => Promise.resolve([{ role: "OWNER" }]),
                }),
              }),
            };
          },
        });

        // Add transaction mock that fails
        (
          mockDb as unknown as { transaction: () => Promise<unknown> }
        ).transaction = () => Promise.reject(new Error("Transaction failed"));

        const service = new OrganizationService(mockDb);

        const result = yield* Effect.either(
          service.delete("test-org-id", "test-user-id"),
        );
        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(DatabaseError);
          expect(result.left.message).toContain(
            "Failed to delete organization",
          );
        }
      }).pipe(Effect.runPromise);
    });
  });
});
