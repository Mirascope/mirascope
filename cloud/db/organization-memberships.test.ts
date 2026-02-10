import { Effect, Layer } from "effect";

import { Database } from "@/db/database";
import {
  type PublicOrganizationMembership,
  type PublicOrganizationMembershipAudit,
} from "@/db/schema";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
} from "@/errors";
import {
  describe,
  it,
  expect,
  TestOrganizationFixture,
  TestFreePlanOrganizationFixture,
  MockDrizzleORM,
  TestDrizzleORM,
} from "@/tests/db";
import { TestSubscriptionWithRealDatabaseFixture } from "@/tests/payments";

describe("OrganizationMemberships", () => {
  // ===========================================================================
  // Create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates a membership for a target user", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const membership = yield* db.organizations.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          data: { memberId: nonMember.id, role: "MEMBER" },
        });

        expect(membership).toMatchObject({
          role: "MEMBER",
        } satisfies Partial<PublicOrganizationMembership>);

        // Verify audit log was created
        const audits = yield* db.organizations.memberships.audits.findAll({
          organizationId: org.id,
          memberId: nonMember.id,
        });
        expect(audits).toHaveLength(1);
        expect(audits[0]).toMatchObject({
          actorId: owner.id,
          targetId: nonMember.id,
          action: "GRANT",
          previousRole: null,
          newRole: "MEMBER",
        } satisfies Partial<PublicOrganizationMembershipAudit>);
      }),
    );

    it.effect("allows ADMIN to create memberships", () =>
      Effect.gen(function* () {
        const { org, admin, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const membership = yield* db.organizations.memberships.create({
          userId: admin.id,
          organizationId: org.id,
          data: { memberId: nonMember.id, role: "MEMBER" },
        });

        expect(membership.role).toBe("MEMBER");

        // Verify audit log was created
        const audits = yield* db.organizations.memberships.audits.findAll({
          organizationId: org.id,
          memberId: nonMember.id,
        });
        expect(audits).toHaveLength(1);
        expect(audits[0]).toMatchObject({
          actorId: admin.id,
          targetId: nonMember.id,
          action: "GRANT",
          newRole: "MEMBER",
        } satisfies Partial<PublicOrganizationMembershipAudit>);
      }),
    );

    it.effect("returns `PermissionDeniedError` when trying to add OWNER", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .create({
            userId: owner.id,
            organizationId: org.id,
            data: { memberId: nonMember.id, role: "OWNER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toBe("Cannot add a member with role OWNER");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to add yourself",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { memberId: owner.id, role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot add yourself to an organization");
        }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const testId = crypto.randomUUID().slice(0, 8);
        const anotherUser = yield* db.users.create({
          data: {
            email: `another-${testId}@example.com`,
            name: "Another User",
          },
        });

        const result = yield* db.organizations.memberships
          .create({
            userId: nonMember.id,
            organizationId: org.id,
            data: { memberId: anotherUser.id, role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to add ADMIN",
      () =>
        Effect.gen(function* () {
          const { org, admin, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .create({
              userId: admin.id,
              organizationId: org.id,
              data: { memberId: nonMember.id, role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot add a member with role ADMIN");
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to create",
      () =>
        Effect.gen(function* () {
          const { org, member, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .create({
              userId: member.id,
              organizationId: org.id,
              data: { memberId: nonMember.id, role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to create this organization membership",
          );
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when user is already a member",
      () =>
        Effect.gen(function* () {
          const { org, owner, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          // First add succeeds
          yield* db.organizations.memberships.create({
            userId: owner.id,
            organizationId: org.id,
            data: { memberId: nonMember.id, role: "MEMBER" },
          });

          // Second add fails
          const result = yield* db.organizations.memberships
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { memberId: nonMember.id, role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
        }),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { memberId: "target-id", role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create organization membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // checkSeatLimit (check: "membership"): getPlan -> fetch organization
            .select([{ stripeCustomerId: "cus_test" }])
            // checkSeatLimit (check: "membership"): count memberships only
            .select([{ count: 1 }])
            // insert membership: fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit log insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { memberId: "target-id", role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // checkSeatLimit (check: "membership"): getPlan -> fetch organization
            .select([{ stripeCustomerId: "cus_test" }])
            // checkSeatLimit (check: "membership"): count memberships only
            .select([{ count: 1 }])
            // insert membership: succeeds
            .insert([
              { memberId: "target-id", role: "MEMBER", createdAt: new Date() },
            ])
            // insert audit log: fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("allows adding a deleted user to an organization", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Delete the user
        yield* db.users.delete({ userId: nonMember.id });

        // Should be able to add the deleted user to the organization
        const membership = yield* db.organizations.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          data: { memberId: nonMember.id, role: "MEMBER" },
        });

        expect(membership).toMatchObject({
          memberId: nonMember.id,
          role: "MEMBER",
        } satisfies Partial<PublicOrganizationMembership>);
      }),
    );

    it.effect("returns non-SqlError from getPlan in checkSeatLimit", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { memberId: "target-id", role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found: org-id");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // checkSeatLimit: getPlan -> fetch organization returns empty (NotFoundError)
            .select([])
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `DatabaseError` when counting memberships fails in checkSeatLimit",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { memberId: "target-id", role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to count memberships");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize: getRole -> getMembership returns OWNER
              .select([{ role: "OWNER" }])
              // checkSeatLimit: getPlan -> fetch organization
              .select([{ stripeCustomerId: "cus_test" }])
              // checkSeatLimit: count memberships fails
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `PlanLimitExceededError` when seat limit is exceeded",
      () =>
        Effect.gen(function* () {
          const { org, owner, nonMember } =
            yield* TestFreePlanOrganizationFixture;
          const db = yield* Database;

          // Org has 1 seat (owner) and FREE plan allows only 1 seat
          // Trying to add another member should exceed the limit
          const result = yield* db.organizations.memberships
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { memberId: nonMember.id, role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PlanLimitExceededError);
          expect(result.message).toContain("free plan limit is 1 seat(s)");
        }).pipe(
          Effect.provide(
            Database.Default.pipe(
              Layer.provide(
                TestSubscriptionWithRealDatabaseFixture(
                  { plan: "free" },
                  TestDrizzleORM,
                ),
              ),
            ),
          ),
        ),
    );

    it.effect("does not count BOT members toward seat limit", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } =
          yield* TestFreePlanOrganizationFixture;
        const db = yield* Database;

        // Create a claw, which adds a BOT member to the organization
        yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "test-claw", displayName: "Test Claw" },
        });

        // Even though there's now an OWNER + BOT in the org, adding a
        // human member should still fail with PlanLimitExceeded because
        // the free plan limit is 1 seat and the BOT doesn't count
        const result = yield* db.organizations.memberships
          .create({
            userId: owner.id,
            organizationId: org.id,
            data: { memberId: nonMember.id, role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PlanLimitExceededError);
        expect(result.message).toContain("free plan limit is 1 seat(s)");
      }).pipe(
        Effect.provide(
          Database.Default.pipe(
            Layer.provide(
              TestSubscriptionWithRealDatabaseFixture(
                { plan: "free" },
                TestDrizzleORM,
              ),
            ),
          ),
        ),
      ),
    );
  });

  // ===========================================================================
  // Find All
  // ===========================================================================

  describe("findAll", () => {
    it.effect("retrieves all memberships for an organization", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Fixture creates owner + admin + member = 3 members
        const memberships = yield* db.organizations.memberships.findAll({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(memberships).toHaveLength(3);
        expect(memberships.map((m) => m.role).sort()).toEqual([
          "ADMIN",
          "MEMBER",
          "OWNER",
        ]);
      }),
    );

    it.effect("allows any member role to read memberships", () =>
      Effect.gen(function* () {
        const { org, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const memberships = yield* db.organizations.memberships.findAll({
          userId: member.id,
          organizationId: org.id,
        });

        expect(memberships).toHaveLength(3);
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .findAll({
            userId: nonMember.id,
            organizationId: org.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .findAll({
            userId: "user-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all memberships");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // findAll: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns deleted users in the membership list", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Add the user to the organization
        const membership = yield* db.organizations.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          data: { memberId: nonMember.id, role: "MEMBER" },
        });

        // Delete the user (soft delete)
        yield* db.users.delete({ userId: nonMember.id });

        // Find all memberships - deleted user should still appear
        const memberships = yield* db.organizations.memberships.findAll({
          userId: owner.id,
          organizationId: org.id,
        });

        // Fixture creates owner + admin + member = 3, plus our new member = 4
        expect(memberships).toHaveLength(4);
        expect(memberships).toContainEqual(membership);
      }),
    );
  });

  // ===========================================================================
  // Find All With User Info
  // ===========================================================================

  describe("findAllWithUserInfo", () => {
    it.effect("retrieves all memberships with user info", () =>
      Effect.gen(function* () {
        const { org, owner, admin, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const memberships =
          yield* db.organizations.memberships.findAllWithUserInfo({
            userId: owner.id,
            organizationId: org.id,
          });

        // Fixture creates owner + admin + member = 3 members
        expect(memberships).toHaveLength(3);

        // Verify structure includes user info
        const ownerMembership = memberships.find(
          (m) => m.memberId === owner.id,
        );
        expect(ownerMembership).toBeDefined();
        expect(ownerMembership).toHaveProperty("email");
        expect(ownerMembership).toHaveProperty("name");
        expect(ownerMembership).toHaveProperty("role", "OWNER");
        expect(ownerMembership).toHaveProperty("createdAt");

        // Verify other members are present
        expect(memberships.some((m) => m.memberId === admin.id)).toBe(true);
        expect(memberships.some((m) => m.memberId === member.id)).toBe(true);
      }),
    );

    it.effect("excludes soft-deleted users", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Add the user to the organization
        yield* db.organizations.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          data: { memberId: nonMember.id, role: "MEMBER" },
        });

        // Delete the user (soft delete)
        yield* db.users.delete({ userId: nonMember.id });

        // Find all memberships with user info - deleted user should NOT appear
        const memberships =
          yield* db.organizations.memberships.findAllWithUserInfo({
            userId: owner.id,
            organizationId: org.id,
          });

        // Fixture creates owner + admin + member = 3, deleted user not included
        expect(memberships).toHaveLength(3);
        expect(memberships.some((m) => m.memberId === nonMember.id)).toBe(
          false,
        );
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .findAllWithUserInfo({
            userId: nonMember.id,
            organizationId: org.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .findAllWithUserInfo({
            userId: "user-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe(
          "Failed to find all memberships with user info",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // findAllWithUserInfo: query fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // Find By ID
  // ===========================================================================

  describe("findById", () => {
    it.effect("retrieves a specific membership", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const membership = yield* db.organizations.memberships.findById({
          userId: owner.id,
          organizationId: org.id,
          memberId: member.id,
        });

        expect(membership.role).toBe("MEMBER");
      }),
    );

    it.effect("allows any member to read another member's info", () =>
      Effect.gen(function* () {
        const { org, member, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const membership = yield* db.organizations.memberships.findById({
          userId: member.id,
          organizationId: org.id,
          memberId: admin.id,
        });

        expect(membership.role).toBe("ADMIN");
      }),
    );

    it.effect("returns `NotFoundError` when membership doesn't exist", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .findById({
            userId: owner.id,
            organizationId: org.id,
            memberId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `Membership for member ${nonMember.id} not found`,
        );
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .findById({
            userId: nonMember.id,
            organizationId: org.id,
            memberId: owner.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .findById({
            userId: "user-id",
            organizationId: "org-id",
            memberId: "target-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // findById: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns membership for a deleted user", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Add the user to the organization
        const membership = yield* db.organizations.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          data: { memberId: nonMember.id, role: "MEMBER" },
        });

        // Delete the user (soft delete)
        yield* db.users.delete({ userId: nonMember.id });

        // Should still be able to find the membership
        const found = yield* db.organizations.memberships.findById({
          userId: owner.id,
          organizationId: org.id,
          memberId: nonMember.id,
        });

        expect(found).toEqual(membership);
      }),
    );
  });

  // ===========================================================================
  // Update
  // ===========================================================================

  describe("update", () => {
    it.effect("updates a membership role", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const updated = yield* db.organizations.memberships.update({
          userId: owner.id,
          organizationId: org.id,
          memberId: member.id,
          data: { role: "ADMIN" },
        });

        expect(updated.role).toBe("ADMIN");

        // Verify audit log was created
        const audits = yield* db.organizations.memberships.audits.findAll({
          organizationId: org.id,
          memberId: member.id,
        });
        // Filter for CHANGE actions (there may be GRANT from fixture setup)
        const changeAudits = audits.filter((a) => a.action === "CHANGE");
        expect(changeAudits).toHaveLength(1);
        expect(changeAudits[0]).toMatchObject({
          actorId: owner.id,
          targetId: member.id,
          action: "CHANGE",
          previousRole: "MEMBER",
          newRole: "ADMIN",
        } satisfies Partial<PublicOrganizationMembershipAudit>);
      }),
    );

    it.effect("allows ADMIN to update memberships", () =>
      Effect.gen(function* () {
        const { org, admin, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const updated = yield* db.organizations.memberships.update({
          userId: admin.id,
          organizationId: org.id,
          memberId: member.id,
          data: { role: "MEMBER" },
        });

        expect(updated.role).toBe("MEMBER");

        // Verify audit log was created
        const audits = yield* db.organizations.memberships.audits.findAll({
          organizationId: org.id,
          memberId: member.id,
        });
        const changeAudits = audits.filter((a) => a.action === "CHANGE");
        expect(changeAudits).toHaveLength(1);
        expect(changeAudits[0]).toMatchObject({
          actorId: admin.id,
          targetId: member.id,
          action: "CHANGE",
          previousRole: "MEMBER",
          newRole: "MEMBER",
        } satisfies Partial<PublicOrganizationMembershipAudit>);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to change role to OWNER",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .update({
              userId: owner.id,
              organizationId: org.id,
              memberId: member.id,
              data: { role: "OWNER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot change a member's role to OWNER");
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to modify your own membership",
      () =>
        Effect.gen(function* () {
          const { org, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .update({
              userId: admin.id,
              organizationId: org.id,
              memberId: admin.id,
              data: { role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot modify your own membership");
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to change an owner's role",
      () =>
        Effect.gen(function* () {
          const { org, admin, owner } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .update({
              userId: admin.id,
              organizationId: org.id,
              memberId: owner.id,
              data: { role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot modify a member with role OWNER");
        }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .update({
            userId: nonMember.id,
            organizationId: org.id,
            memberId: "some-user-id",
            data: { role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to update ADMIN",
      () =>
        Effect.gen(function* () {
          const { org, owner, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          // Create a second ADMIN with unique email
          const testId = crypto.randomUUID().slice(0, 8);
          const secondAdmin = yield* db.users.create({
            data: { email: `admin2-${testId}@example.com`, name: "Admin 2" },
          });
          yield* db.organizations.memberships.create({
            userId: owner.id,
            organizationId: org.id,
            data: { memberId: secondAdmin.id, role: "ADMIN" },
          });

          // First ADMIN should not be able to update second ADMIN
          const result = yield* db.organizations.memberships
            .update({
              userId: admin.id,
              organizationId: org.id,
              memberId: secondAdmin.id,
              data: { role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot modify a member with role ADMIN");
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to promote to ADMIN",
      () =>
        Effect.gen(function* () {
          const { org, admin, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          // ADMIN should not be able to promote MEMBER to ADMIN
          const result = yield* db.organizations.memberships
            .update({
              userId: admin.id,
              organizationId: org.id,
              memberId: member.id,
              data: { role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot change a member's role to ADMIN");
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, member, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const testId = crypto.randomUUID().slice(0, 8);
          const anotherMember = yield* db.users.create({
            data: {
              email: `another-member-${testId}@example.com`,
              name: "Another Member",
            },
          });
          yield* db.organizations.memberships.create({
            userId: admin.id,
            organizationId: org.id,
            data: { memberId: anotherMember.id, role: "MEMBER" },
          });

          const result = yield* db.organizations.memberships
            .update({
              userId: member.id,
              organizationId: org.id,
              memberId: anotherMember.id,
              data: { role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this organization membership",
          );
        }),
    );

    it.effect(
      "returns `NotFoundError` when target membership doesn't exist",
      () =>
        Effect.gen(function* () {
          const { org, owner, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .update({
              userId: owner.id,
              organizationId: org.id,
              memberId: nonMember.id,
              data: { role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "User is not a member of this organization",
          );
        }),
    );

    it.effect(
      "returns `DatabaseError` when getMembership for target fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              memberId: "target-id",
              data: { role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get membership");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize: getRole -> getMembership returns OWNER
              .select([{ role: "OWNER" }])
              // getMembership for target: fails
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );

    it.effect("returns `DatabaseError` when update fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            memberId: "target-id",
            data: { role: "ADMIN" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update organization membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // getMembership for target: returns MEMBER
            .select([{ role: "MEMBER" }])
            // update: fails
            .update(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit log insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            memberId: "target-id",
            data: { role: "ADMIN" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // getMembership for target: returns MEMBER
            .select([{ role: "MEMBER" }])
            // update: succeeds
            .update([
              { memberId: "target-id", role: "ADMIN", createdAt: new Date() },
            ])
            // audit log insert: fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("allows updating a deleted user's membership", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Add the user to the organization
        yield* db.organizations.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          data: { memberId: nonMember.id, role: "MEMBER" },
        });

        // Delete the user (soft delete)
        yield* db.users.delete({ userId: nonMember.id });

        // Should be able to update the deleted user's membership
        const updated = yield* db.organizations.memberships.update({
          userId: owner.id,
          organizationId: org.id,
          memberId: nonMember.id,
          data: { role: "ADMIN" },
        });

        expect(updated).toMatchObject({
          memberId: nonMember.id,
          role: "ADMIN",
        } satisfies Partial<PublicOrganizationMembership>);
      }),
    );
  });

  // ===========================================================================
  // Delete
  // ===========================================================================

  describe("delete", () => {
    it.effect("removes a member from an organization", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        yield* db.organizations.memberships.delete({
          userId: owner.id,
          organizationId: org.id,
          memberId: member.id,
        });

        // Verify membership is gone
        const result = yield* db.organizations.memberships
          .findById({
            userId: owner.id,
            organizationId: org.id,
            memberId: member.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);

        // Verify audit log was created
        const audits = yield* db.organizations.memberships.audits.findAll({
          organizationId: org.id,
          memberId: member.id,
        });
        const revokeAudits = audits.filter((a) => a.action === "REVOKE");
        expect(revokeAudits).toHaveLength(1);
        expect(revokeAudits[0]).toMatchObject({
          actorId: owner.id,
          targetId: member.id,
          action: "REVOKE",
          previousRole: "MEMBER",
          newRole: null,
        } satisfies Partial<PublicOrganizationMembershipAudit>);
      }),
    );

    it.effect(
      "allows a MEMBER to remove themself (leave the organization)",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          yield* db.organizations.memberships.delete({
            userId: member.id,
            organizationId: org.id,
            memberId: member.id,
          });

          // Verify membership is gone (owner can still read)
          const result = yield* db.organizations.memberships
            .findById({
              userId: owner.id,
              organizationId: org.id,
              memberId: member.id,
            })
            .pipe(Effect.flip);
          expect(result).toBeInstanceOf(NotFoundError);

          // Verify audit log was created
          const audits = yield* db.organizations.memberships.audits.findAll({
            organizationId: org.id,
            memberId: member.id,
          });
          const revokeAudits = audits.filter((a) => a.action === "REVOKE");
          expect(revokeAudits).toHaveLength(1);
          expect(revokeAudits[0]).toMatchObject({
            actorId: member.id,
            targetId: member.id,
            action: "REVOKE",
            previousRole: "MEMBER",
            newRole: null,
          } satisfies Partial<PublicOrganizationMembershipAudit>);
        }),
    );

    it.effect(
      "allows an ADMIN to remove themself (leave the organization)",
      () =>
        Effect.gen(function* () {
          const { org, owner, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          yield* db.organizations.memberships.delete({
            userId: admin.id,
            organizationId: org.id,
            memberId: admin.id,
          });

          // Verify membership is gone (owner can still read)
          const result = yield* db.organizations.memberships
            .findById({
              userId: owner.id,
              organizationId: org.id,
              memberId: admin.id,
            })
            .pipe(Effect.flip);
          expect(result).toBeInstanceOf(NotFoundError);

          // Verify audit log was created
          const audits = yield* db.organizations.memberships.audits.findAll({
            organizationId: org.id,
            memberId: admin.id,
          });
          const revokeAudits = audits.filter((a) => a.action === "REVOKE");
          expect(revokeAudits).toHaveLength(1);
          expect(revokeAudits[0]).toMatchObject({
            actorId: admin.id,
            targetId: admin.id,
            action: "REVOKE",
            previousRole: "ADMIN",
            newRole: null,
          } satisfies Partial<PublicOrganizationMembershipAudit>);
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when OWNER tries to remove themself",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .delete({
              userId: owner.id,
              organizationId: org.id,
              memberId: owner.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot remove a member with role OWNER");
        }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .delete({
            userId: nonMember.id,
            organizationId: org.id,
            memberId: "some-user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("allows ADMIN to delete MEMBER", () =>
      Effect.gen(function* () {
        const { org, admin, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // ADMIN should be able to delete MEMBER
        yield* db.organizations.memberships.delete({
          userId: admin.id,
          organizationId: org.id,
          memberId: member.id,
        });

        // Verify the membership is deleted
        const result = yield* db.organizations.memberships
          .findById({
            userId: admin.id,
            organizationId: org.id,
            memberId: member.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);

        // Verify audit log was created
        const audits = yield* db.organizations.memberships.audits.findAll({
          organizationId: org.id,
          memberId: member.id,
        });
        const revokeAudits = audits.filter((a) => a.action === "REVOKE");
        expect(revokeAudits).toHaveLength(1);
        expect(revokeAudits[0]).toMatchObject({
          actorId: admin.id,
          targetId: member.id,
          action: "REVOKE",
          previousRole: "MEMBER",
          newRole: null,
        } satisfies Partial<PublicOrganizationMembershipAudit>);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to delete ADMIN",
      () =>
        Effect.gen(function* () {
          const { org, owner, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          // Create a second ADMIN with unique email
          const testId = crypto.randomUUID().slice(0, 8);
          const secondAdmin = yield* db.users.create({
            data: { email: `admin2-${testId}@example.com`, name: "Admin 2" },
          });
          yield* db.organizations.memberships.create({
            userId: owner.id,
            organizationId: org.id,
            data: { memberId: secondAdmin.id, role: "ADMIN" },
          });

          // First ADMIN should not be able to delete second ADMIN
          const result = yield* db.organizations.memberships
            .delete({
              userId: admin.id,
              organizationId: org.id,
              memberId: secondAdmin.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot remove a member with role ADMIN");
        }),
    );

    it.effect(
      "returns `NotFoundError` when target membership doesn't exist",
      () =>
        Effect.gen(function* () {
          const { org, owner, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .delete({
              userId: owner.id,
              organizationId: org.id,
              memberId: nonMember.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "User is not a member of this organization",
          );
        }),
    );

    it.effect(
      "returns `DatabaseError` when getMembership for target fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.memberships
            .delete({
              userId: "owner-id",
              organizationId: "org-id",
              memberId: "target-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get membership");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize: getRole -> getMembership returns OWNER
              .select([{ role: "OWNER" }])
              // getMembership for target: fails
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            memberId: "target-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete organization membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // getMembership for target: returns MEMBER
            .select([{ role: "MEMBER" }])
            // delete: fails
            .delete(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit log insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            memberId: "target-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole -> getMembership returns OWNER
            .select([{ role: "OWNER" }])
            // getMembership for target: returns MEMBER
            .select([{ role: "MEMBER" }])
            // delete: succeeds
            .delete([])
            // audit log insert: fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("allows removing a deleted user from an organization", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Add the user to the organization
        yield* db.organizations.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          data: { memberId: nonMember.id, role: "MEMBER" },
        });

        // Delete the user (soft delete)
        yield* db.users.delete({ userId: nonMember.id });

        // Should be able to remove the deleted user's membership
        yield* db.organizations.memberships.delete({
          userId: owner.id,

          organizationId: org.id,
          memberId: nonMember.id,
        });

        // Verify the membership is gone
        const result = yield* db.organizations.memberships
          .findById({
            userId: owner.id,
            organizationId: org.id,
            memberId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .findById({
            userId: "user-id",
            organizationId: "org-id",
            memberId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getMembership: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // getRole (Authorization Helper)
  // ===========================================================================

  describe("getRole", () => {
    it.effect("returns role when user is a member", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const role = yield* db.organizations.memberships.getRole({
          userId: admin.id,
          organizationId: org.id,
        });

        expect(role).toBe("ADMIN");
      }),
    );

    it.effect("returns NotFoundError when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .getRole({
            userId: nonMember.id,
            organizationId: org.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect(
      "returns NotFoundError when user is soft-deleted (lacks permissions)",
      () =>
        Effect.gen(function* () {
          const { org, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          // Soft-delete the admin user
          yield* db.users.delete({ userId: admin.id });

          // Try to get role - should fail because deleted users have no permissions
          const result = yield* db.organizations.memberships
            .getRole({
              userId: admin.id,
              organizationId: org.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Organization not found");
        }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships
          .getRole({
            userId: "user-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getMembership: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // Audits (Sub-service)
  // ===========================================================================

  describe("audits", () => {
    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.memberships.audits
          .findAll({
            organizationId: "org-id",
            memberId: "member-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find audit entries");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // audits.findAll: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });
});
