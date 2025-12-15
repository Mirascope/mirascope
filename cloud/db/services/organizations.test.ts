import { describe, it, expect } from "@effect/vitest";
import {
  MockDatabase,
  TestDatabase,
  TestOrganizationFixture,
} from "@/tests/db";
import { Effect } from "effect";
import {
  type PublicOrganizationWithMembership,
  type PublicOrganizationMembershipAudit,
} from "@/db/schema";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { DatabaseService } from "@/db/services";

describe("OrganizationService", () => {
  describe("getRole", () => {
    it.effect("returns OWNER role", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const role = yield* db.organizations.getRole({
          organizationId: org.id,
          userId: owner.id,
        });

        expect(role).toBe("OWNER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns ADMIN role", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const role = yield* db.organizations.getRole({
          organizationId: org.id,
          userId: admin.id,
        });

        expect(role).toBe("ADMIN");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns DEVELOPER role", () =>
      Effect.gen(function* () {
        const { org, developer } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const role = yield* db.organizations.getRole({
          organizationId: org.id,
          userId: developer.id,
        });

        expect(role).toBe("DEVELOPER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns VIEWER role", () =>
      Effect.gen(function* () {
        const { org, viewer } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const role = yield* db.organizations.getRole({
          organizationId: org.id,
          userId: viewer.id,
        });

        expect(role).toBe("VIEWER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations
          .getRole({ organizationId: org.id, userId: nonMember.id })
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
          .getRole({ organizationId: "org-id", userId: "user-id" })
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
          data: { email: "test@example.com", name: "Test User" },
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

        // Verify audit log was created for OWNER GRANT
        const audits = yield* db.organizations.memberships.audits.findAll({
          organizationId: org.id,
          memberId: user.id,
        });
        expect(audits).toHaveLength(1);
        expect(audits[0]).toMatchObject({
          actorId: user.id,
          targetId: user.id,
          action: "GRANT",
          previousRole: null,
          newRole: "OWNER",
        } satisfies Partial<PublicOrganizationMembershipAudit>);
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
          data: { email: "test@example.com", name: "Test User" },
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
    it.effect("retrieves organization when user is OWNER", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const found = yield* db.organizations.findById({
          organizationId: org.id,
          userId: owner.id,
        });

        expect(found).toEqual(org);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("retrieves organization when user is ADMIN", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const found = yield* db.organizations.findById({
          organizationId: org.id,
          userId: admin.id,
        });

        expect(found).toMatchObject({
          id: org.id,
          name: org.name,
          role: "ADMIN",
        });
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("retrieves organization when user is DEVELOPER", () =>
      Effect.gen(function* () {
        const { org, developer } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const found = yield* db.organizations.findById({
          organizationId: org.id,
          userId: developer.id,
        });

        expect(found).toMatchObject({
          id: org.id,
          name: org.name,
          role: "DEVELOPER",
        });
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("retrieves organization when user is VIEWER", () =>
      Effect.gen(function* () {
        const { org, viewer } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const found = yield* db.organizations.findById({
          organizationId: org.id,
          userId: viewer.id,
        });

        expect(found).toMatchObject({
          id: org.id,
          name: org.name,
          role: "VIEWER",
        });
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .findById({ organizationId: "org-id", userId: "user-id" })
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
          .findById({ organizationId: org.id, userId: nonMember.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when fetching organization fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: membership found with OWNER role
          .select([{ role: "OWNER" }])
          // findById query: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .findById({ organizationId: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find organization");
      }),
    );

    it.effect("returns `NotFoundError` when organization not found", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: membership found with OWNER role
          .select([{ role: "OWNER" }])
          // findById query: not found (edge case - membership exists but org doesn't)
          .select([])
          .build();

        const result = yield* db.organizations
          .findById({ organizationId: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "organization with organizationId org-id not found",
        );
      }),
    );
  });

  describe("update", () => {
    it.effect("updates organization when user is owner", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const newName = "Updated Name";
        const updated = yield* db.organizations.update({
          organizationId: org.id,
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

    it.effect("updates organization when user is admin", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const newName = "Admin Updated Name";
        const updated = yield* db.organizations.update({
          organizationId: org.id,
          data: { name: newName },
          userId: admin.id,
        });

        expect(updated).toEqual({
          id: org.id,
          name: newName,
          role: "ADMIN",
        } satisfies PublicOrganizationWithMembership);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: database query fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .update({
            organizationId: "org-id",
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
          data: { email: "test@example.com", name: "Test User" },
        });

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.organizations
          .update({
            organizationId: badId,
            data: { name: "Should Fail" },
            userId: user.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when update query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: membership found with ADMIN role
          .select([{ role: "ADMIN" }])
          // update query: fails
          .update(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .update({
            organizationId: "org-id",
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
          // getRole: membership found with ADMIN role
          .select([{ role: "ADMIN" }])
          // update query: no rows updated (edge case)
          .update([])
          .build();

        const result = yield* db.organizations
          .update({
            organizationId: "org-id",
            data: { name: "New Name" },
            userId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "organization with organizationId org-id not found",
        );
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when DEVELOPER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, developer } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations
            .update({
              userId: developer.id,
              organizationId: org.id,
              data: { name: "New Name" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when VIEWER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, viewer } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations
            .update({
              userId: viewer.id,
              organizationId: org.id,
              data: { name: "New Name" },
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

        yield* db.organizations.delete({
          organizationId: org.id,
          userId: owner.id,
        });

        const result = yield* db.organizations
          .findById({ organizationId: org.id, userId: owner.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: database query fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations
          .delete({ organizationId: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          data: { email: "test@example.com", name: "Test User" },
        });

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.organizations
          .delete({ organizationId: badId, userId: user.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, admin } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations
            .delete({ organizationId: org.id, userId: admin.id })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when DEVELOPER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, developer } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations
            .delete({ organizationId: org.id, userId: developer.id })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when VIEWER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, viewer } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations
            .delete({ organizationId: org.id, userId: viewer.id })
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
          // getRole: membership found with OWNER role
          .select([{ role: "OWNER" }])
          // delete transaction: fails
          .delete(new Error("Transaction failed"))
          .build();

        const result = yield* db.organizations
          .delete({ organizationId: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete organization");
      }),
    );
  });
});
