import { describe, it, expect } from "@effect/vitest";
import {
  MockDatabase,
  TestDatabase,
  TestOrganizationFixture,
} from "@/tests/db";
import { Effect } from "effect";
import { type PublicOrganizationWithMembership } from "@/db/schema";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { DatabaseService } from "@/db/services";

describe("OrganizationService", () => {
  describe("create", () => {
    it.effect("creates an organization with owner membership", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const name = "Test Organization";
        const org = yield* db.organizations.create({ name }, user.id);

        expect(org).toEqual({
          id: org.id,
          name,
          role: "OWNER",
        } satisfies PublicOrganizationWithMembership);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `AlreadyExistsError` when name is taken", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations
          .create({ name: org.name }, owner.id)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect(result.message).toBe(
          "An organization with this name already exists",
        );
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when transaction fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .insert(new Error("Transaction failed"))
          .build();

        const result = yield* db.organizations
          .create({ name: "Test Org" }, "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create organization");
      }),
    );
  });

  describe("findAll", () => {
    it.effect("retrieves all organizations for a user", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const org2 = yield* db.organizations.create(
          { name: "Org 2" },
          owner.id,
        );

        const orgs = yield* db.organizations.findAll(owner.id);

        expect(orgs).toEqual([org, org2]);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns empty array for user with no organizations", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const orgs = yield* db.organizations.findAll(user.id);

        expect(orgs).toEqual([]);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .findAll("user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get user organizations");
      }),
    );
  });

  describe("findById", () => {
    it.effect("retrieves organization when user is a member", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const found = yield* db.organizations.findById(org.id, owner.id);

        expect(found).toEqual(org);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when membership check fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .findById("org-id", "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to check membership");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations
          .findById(org.id, nonMember.id)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when fetching organization fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: membership found
          .select([{ role: "OWNER" }])
          // fetch organization: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .findById("org-id", "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find organization");
      }),
    );

    it.effect("returns `NotFoundError` when organization not found", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: membership found
          .select([{ role: "OWNER" }])
          // fetch organization: not found
          .select([])
          .build();

        const result = yield* db.organizations
          .findById("org-id", "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization with id org-id not found");
      }),
    );
  });

  describe("update", () => {
    it.effect("updates organization when user is admin or owner", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const newName = "Updated Name";
        const updated = yield* db.organizations.update(
          org.id,
          { name: newName },
          owner.id,
        );

        expect(updated).toEqual({
          id: org.id,
          name: newName,
          role: "OWNER",
        } satisfies PublicOrganizationWithMembership);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when membership check fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .update("org-id", { name: "New Name" }, "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to check membership");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.organizations
          .update(badId, { name: "Should Fail" }, user.id)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when update query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: has ADMIN role
          .select([{ role: "ADMIN" }])
          // updateOrganization: fails
          .update(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .update("org-id", { name: "New Name" }, "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update organization");
      }),
    );

    it.effect("returns `NotFoundError` when organization does not exist", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: has ADMIN role
          .select([{ role: "ADMIN" }])
          // updateOrganization: no rows updated
          .update([])
          .build();

        const result = yield* db.organizations
          .update("org-id", { name: "New Name" }, "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization with id org-id not found");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when user lacks permission",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // checkPermission: has DEVELOPER role (not ADMIN)
            .select([{ role: "DEVELOPER" }])
            .build();

          const result = yield* db.organizations
            .update("org-id", { name: "New Name" }, "user-id")
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this organization",
          );
        }),
    );
  });

  describe("delete", () => {
    it.effect("deletes an organization and its memberships", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        yield* db.organizations.delete(org.id, owner.id);

        const result = yield* db.organizations
          .findById(org.id, owner.id)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when membership check fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .delete("org-id", "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to check membership");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.organizations
          .delete(badId, user.id)
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `PermissionDeniedError` when user is not an owner", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: has DEVELOPER role (not OWNER)
          .select([{ role: "DEVELOPER" }])
          .build();

        const result = yield* db.organizations
          .delete("org-id", "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toBe(
          "You do not have permission to delete this organization",
        );
      }),
    );

    it.effect("returns `DatabaseError` when delete transaction fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: has OWNER role
          .select([{ role: "OWNER" }])
          // deleteOrganizationWithMemberships: fails
          .delete(new Error("Transaction failed"))
          .build();

        const result = yield* db.organizations
          .delete("org-id", "user-id")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete organization");
      }),
    );
  });
});
