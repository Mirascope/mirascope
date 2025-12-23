import {
  describe,
  it,
  expect,
  TestOrganizationFixture,
  MockDrizzleORM,
} from "@/tests/db";
import { Database } from "@/db/database";
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
} from "@/errors";

describe("Organizations", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates an organization with owner membership", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const user = yield* db.users.create({
          data: { email: "create-org@example.com", name: "Create Org User" },
        });

        const name = "New Test Organization";
        const org = yield* db.organizations.create({
          userId: user.id,
          data: { name },
        });

        expect(org).toEqual({
          id: org.id,
          name,
          role: "OWNER",
        } satisfies PublicOrganizationWithMembership);

        // Verify the organization can be found
        const found = yield* db.organizations.findById({
          userId: user.id,
          organizationId: org.id,
        });
        expect(found.name).toBe(name);

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
      }),
    );

    it.effect("returns `AlreadyExistsError` when name is taken", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations
          .create({ userId: owner.id, data: { name: org.name } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect(result.message).toBe(
          "An organization with this name already exists",
        );
      }),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .create({ userId: "user-id", data: { name: "Test Org" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create organization");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().insert(new Error("Connection failed")).build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when membership insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .create({ userId: "user-id", data: { name: "Test Org" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create organization membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // insert organization: succeeds
            .insert([{ id: "org-id", name: "Test Org" }])
            // insert membership: fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit log insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .create({ userId: "user-id", data: { name: "Test Org" } })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // insert organization: succeeds
            .insert([{ id: "org-id", name: "Test Org" }])
            // insert membership: succeeds
            .insert([])
            // insert audit: fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("retrieves all organizations for a user", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Create a second organization
        const org2 = yield* db.organizations.create({
          userId: owner.id,
          data: { name: "Second Organization" },
        });

        const orgs = yield* db.organizations.findAll({ userId: owner.id });

        expect(orgs).toHaveLength(2);
        expect(orgs.map((o) => o.name).sort()).toEqual(
          [org.name, org2.name].sort(),
        );
      }),
    );

    it.effect("returns empty array for user with no organizations", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const user = yield* db.users.create({
          data: { email: "no-orgs@example.com", name: "No Orgs User" },
        });

        const orgs = yield* db.organizations.findAll({ userId: user.id });

        expect(orgs).toEqual([]);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .findAll({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get user organizations");
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
    it.effect("retrieves organization when user is OWNER", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const found = yield* db.organizations.findById({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(found).toMatchObject({
          id: org.id,
          name: org.name,
          role: "OWNER",
        } satisfies Partial<PublicOrganizationWithMembership>);
      }),
    );

    it.effect("retrieves organization when user is ADMIN", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const found = yield* db.organizations.findById({
          userId: admin.id,
          organizationId: org.id,
        });

        expect(found).toMatchObject({
          id: org.id,
          name: org.name,
          role: "ADMIN",
        });
      }),
    );

    it.effect("retrieves organization when user is MEMBER", () =>
      Effect.gen(function* () {
        const { org, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const found = yield* db.organizations.findById({
          userId: member.id,
          organizationId: org.id,
        });

        expect(found).toMatchObject({
          id: org.id,
          name: org.name,
          role: "MEMBER",
        });
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations
          .findById({ userId: nonMember.id, organizationId: org.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .findById({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getRole -> getMembership: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when fetching organization fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .findById({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find organization");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // findById query: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `NotFoundError` when organization not found", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .findById({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "Organization with organizationId org-id not found",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // findById query: returns empty (org not found)
            .select([])
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // update
  // ===========================================================================

  describe("update", () => {
    it.effect("updates organization when user is OWNER", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const newName = "Updated Organization Name";
        const updated = yield* db.organizations.update({
          userId: owner.id,
          organizationId: org.id,
          data: { name: newName },
        });

        expect(updated).toEqual({
          id: org.id,
          name: newName,
          role: "OWNER",
        } satisfies PublicOrganizationWithMembership);
      }),
    );

    it.effect("updates organization when user is ADMIN", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const newName = "Admin Updated Name";
        const updated = yield* db.organizations.update({
          userId: admin.id,
          organizationId: org.id,
          data: { name: newName },
        });

        expect(updated).toEqual({
          id: org.id,
          name: newName,
          role: "ADMIN",
        } satisfies PublicOrganizationWithMembership);
      }),
    );

    it.effect("persists updates correctly", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const newName = "Persisted Name";
        yield* db.organizations.update({
          userId: owner.id,
          organizationId: org.id,
          data: { name: newName },
        });

        const found = yield* db.organizations.findById({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(found.name).toBe(newName);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations
            .update({
              userId: member.id,
              organizationId: org.id,
              data: { name: "Should Fail" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this organization",
          );
        }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations
          .update({
            userId: nonMember.id,
            organizationId: org.id,
            data: { name: "Should Fail" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .update({
            userId: "user-id",
            organizationId: "org-id",
            data: { name: "New Name" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getRole -> getMembership: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when update query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .update({
            userId: "user-id",
            organizationId: "org-id",
            data: { name: "New Name" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update organization");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> memberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // update query: fails
            .update(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `NotFoundError` when organization does not exist", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .update({
            userId: "user-id",
            organizationId: "org-id",
            data: { name: "New Name" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "organization with organizationId org-id not found",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> memberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // update query: no rows updated
            .update([])
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // delete
  // ===========================================================================

  describe("delete", () => {
    it.effect("deletes an organization", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        // Create a new organization to delete
        const user = yield* db.users.create({
          data: { email: "delete-test@example.com", name: "Delete Test User" },
        });

        const org = yield* db.organizations.create({
          userId: user.id,
          data: { name: "Organization To Delete" },
        });

        yield* db.organizations.delete({
          userId: user.id,
          organizationId: org.id,
        });

        // Verify it's gone
        const result = yield* db.organizations
          .findById({ userId: user.id, organizationId: org.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations
            .delete({ userId: admin.id, organizationId: org.id })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this organization",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations
            .delete({ userId: member.id, organizationId: org.id })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this organization",
          );
        }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations
          .delete({ userId: nonMember.id, organizationId: org.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .delete({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getRole -> getMembership: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .delete({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete organization");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> memberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // delete: fails
            .delete(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });
});
