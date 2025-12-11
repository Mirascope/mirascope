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
  describe("getRole", () => {
    it.effect("returns the user's role in an organization", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const role = yield* db.organizations.getRole({
          id: org.id,
          userId: owner.id,
        });

        expect(role).toBe("OWNER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations
          .getRole({ id: org.id, userId: nonMember.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .getRole({ id: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }),
    );
  });

  describe("create", () => {
    it.effect("creates an organization with owner membership", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const name = "Test Organization";
        const org = yield* db.organizations.create({
          data: { name },
          userId: user.id,
        });

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
          .create({ data: { name: org.name }, userId: owner.id })
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
          .create({ data: { name: "Test Org" }, userId: "user-id" })
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

        const org2 = yield* db.organizations.create({
          data: { name: "Org 2" },
          userId: owner.id,
        });

        const orgs = yield* db.organizations.findAll({ userId: owner.id });

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

        const orgs = yield* db.organizations.findAll({ userId: user.id });

        expect(orgs).toEqual([]);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .findAll({ userId: "user-id" })
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

        const found = yield* db.organizations.findById({
          id: org.id,
          userId: owner.id,
        });

        expect(found).toEqual(org);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .findById({ id: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations
          .findById({ id: org.id, userId: nonMember.id })
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
          .findById({ id: "org-id", userId: "user-id" })
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
          .findById({ id: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("organization with id org-id not found");
      }),
    );
  });

  describe("update", () => {
    it.effect("updates organization when user is admin or owner", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const newName = "Updated Name";
        const updated = yield* db.organizations.update({
          id: org.id,
          data: { name: newName },
          userId: owner.id,
        });

        expect(updated).toEqual({
          id: org.id,
          name: newName,
          role: "OWNER",
        } satisfies PublicOrganizationWithMembership);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .update({
            id: "org-id",
            data: { name: "New Name" },
            userId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
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
          .update({ id: badId, data: { name: "Should Fail" }, userId: user.id })
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
          .update({
            id: "org-id",
            data: { name: "New Name" },
            userId: "user-id",
          })
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
          .update({
            id: "org-id",
            data: { name: "New Name" },
            userId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("organization with id org-id not found");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when user lacks permission",
      () =>
        Effect.gen(function* () {
          const { org, developer } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations
            .update({
              id: org.id,
              data: { name: "New Name" },
              userId: developer.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );
  });

  describe("delete", () => {
    it.effect("deletes an organization and its memberships", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        yield* db.organizations.delete({ id: org.id, userId: owner.id });

        const result = yield* db.organizations
          .findById({ id: org.id, userId: owner.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // checkPermission: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .delete({ id: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
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
          .delete({ id: badId, userId: user.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `PermissionDeniedError` when user is not an owner", () =>
      Effect.gen(function* () {
        const { org, developer } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations
          .delete({ id: org.id, userId: developer.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toBe(
          "You do not have permission to delete this organization",
        );
      }).pipe(Effect.provide(TestDatabase)),
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
          .delete({ id: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete organization");
      }),
    );
  });

  describe("addMember", () => {
    it.effect("adds a member to an organization", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        // Create a new user to add as member
        const newMember = yield* db.users.create({
          email: "newmember@example.com",
          name: "New Member",
        });

        const membership = yield* db.organizations.addMember({
          id: org.id,
          memberUserId: newMember.id,
          role: "DEVELOPER",
          userId: owner.id,
        });

        expect(membership).toBeDefined();
        expect(membership.organizationId).toBe(org.id);
        expect(membership.userId).toBe(newMember.id);
        expect(membership.role).toBe("DEVELOPER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows added member to access organization", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const newMember = yield* db.users.create({
          email: "newmember@example.com",
          name: "New Member",
        });

        yield* db.organizations.addMember({
          id: org.id,
          memberUserId: newMember.id,
          role: "ANNOTATOR",
          userId: owner.id,
        });

        // Verify the new member can access the organization
        const foundOrg = yield* db.organizations.findById({
          id: org.id,
          userId: newMember.id,
        });

        expect(foundOrg.id).toBe(org.id);
        expect(foundOrg.role).toBe("ANNOTATOR");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when organization not found", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.organizations
          .addMember({
            id: badId,
            memberUserId: owner.id,
            role: "DEVELOPER",
            userId: owner.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when caller is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations
          .addMember({
            id: org.id,
            memberUserId: nonMember.id,
            role: "DEVELOPER",
            userId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when caller has insufficient role",
      () =>
        Effect.gen(function* () {
          const { org, developer, nonMember } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations
            .addMember({
              id: org.id,
              memberUserId: nonMember.id,
              role: "ANNOTATOR",
              userId: developer.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `AlreadyExistsError` when user is already a member",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          // Try to add the owner again (they're already a member)
          const result = yield* db.organizations
            .addMember({
              id: org.id,
              memberUserId: owner.id,
              role: "ADMIN",
              userId: owner.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "User is already a member of this organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: OWNER role (has permission)
          .select([{ role: "OWNER" }])
          // insert: fails
          .insert(new Error("Insert failed"))
          .build();

        const result = yield* db.organizations
          .addMember({
            id: "org-id",
            memberUserId: "new-user-id",
            role: "DEVELOPER",
            userId: "caller-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to add organization member");
      }),
    );
  });

  describe("terminateMember", () => {
    it.effect("removes a member from an organization", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        // Add a member first
        const member = yield* db.users.create({
          email: "member@example.com",
          name: "Member",
        });

        yield* db.organizations.addMember({
          id: org.id,
          memberUserId: member.id,
          role: "DEVELOPER",
          userId: owner.id,
        });

        // Now remove them
        yield* db.organizations.terminateMember({
          id: org.id,
          memberUserId: member.id,
          userId: owner.id,
        });

        // Verify they can no longer access the organization
        const result = yield* db.organizations
          .findById({ id: org.id, userId: member.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when organization not found", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.organizations
          .terminateMember({
            id: badId,
            memberUserId: owner.id,
            userId: owner.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when caller is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations
          .terminateMember({
            id: org.id,
            memberUserId: nonMember.id,
            userId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when caller has insufficient role",
      () =>
        Effect.gen(function* () {
          const { org, developer, annotator } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          // Developer tries to remove annotator (should fail - needs ADMIN or OWNER)
          const result = yield* db.organizations
            .terminateMember({
              id: org.id,
              memberUserId: annotator.id,
              userId: developer.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when user is not a member of the organization",
      () =>
        Effect.gen(function* () {
          const { org, owner, nonMember } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          // Try to remove someone who isn't a member
          const result = yield* db.organizations
            .terminateMember({
              id: org.id,
              memberUserId: nonMember.id,
              userId: owner.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "User is not a member of this organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: OWNER role (has permission)
          .select([{ role: "OWNER" }])
          // delete: fails
          .delete(new Error("Delete failed"))
          .build();

        const result = yield* db.organizations
          .terminateMember({
            id: "org-id",
            memberUserId: "member-id",
            userId: "caller-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to remove organization member");
      }),
    );
  });
});
