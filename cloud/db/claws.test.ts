import { Effect, Layer } from "effect";

import type { PublicClaw } from "@/db/schema";

import { Database } from "@/db/database";
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
  MockDrizzleORM,
  TestOrganizationFixture,
  TestFreePlanOrganizationFixture,
  TestDrizzleORM,
} from "@/tests/db";
import { TestSubscriptionWithRealDatabaseFixture } from "@/tests/payments";

describe("Claws", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates a claw (org OWNER) and adds creator as ADMIN", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "new-claw", displayName: "New Claw" },
        });

        expect(claw).toMatchObject({
          slug: "new-claw",
          displayName: "New Claw",
          organizationId: org.id,
          createdByUserId: owner.id,
        } satisfies Partial<PublicClaw>);

        // Verify creator was added as claw ADMIN
        const membership = yield* db.organizations.claws.memberships.findById({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
          memberId: owner.id,
        });
        expect(membership.role).toBe("ADMIN");

        // Verify audit log was created
        const audits = yield* db.organizations.claws.memberships.audits.findAll(
          {
            clawId: claw.id,
            memberId: owner.id,
          },
        );
        expect(audits).toHaveLength(1);
        expect(audits[0]).toMatchObject({
          actorId: owner.id,
          targetId: owner.id,
          action: "GRANT",
          previousRole: null,
          newRole: "ADMIN",
        });
      }),
    );

    it.effect("creates a claw (org ADMIN)", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: admin.id,
          organizationId: org.id,
          data: {
            slug: "admin-created-claw",
            displayName: "Admin Created Claw",
          },
        });

        expect(claw.displayName).toBe("Admin Created Claw");
        expect(claw.slug).toBe("admin-created-claw");
        expect(claw.createdByUserId).toBe(admin.id);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when org MEMBER tries to create",
      () =>
        Effect.gen(function* () {
          const { org, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .create({
              userId: member.id,
              organizationId: org.id,
              data: {
                slug: "unauthorized-claw",
                displayName: "Unauthorized Claw",
              },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to create claws in this organization",
          );
        }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to create (hides org)",
      () =>
        Effect.gen(function* () {
          const { org, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .create({
              userId: nonMember.id,
              organizationId: org.id,
              data: {
                slug: "unauthorized-claw-2",
                displayName: "Unauthorized Claw 2",
              },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Organization not found");
        }),
    );

    it.effect("returns `DatabaseError` when claw insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { slug: "test-claw", displayName: "Test Claw" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create claw");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole
            .select([{ role: "OWNER" }])
            // findById: get membership
            .select([
              { memberId: "owner-id", role: "OWNER", createdAt: new Date() },
            ])
            // checkClawLimit: getPlan -> fetch organization
            .select([{ stripeCustomerId: "cus_test" }])
            // checkClawLimit: count claws (under limit)
            .select([{ count: 0 }])
            // getPlan (for plan defaults)
            .select([{ stripeCustomerId: "cus_test" }])
            // claw insert fails
            .insert(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `AlreadyExistsError` when slug is taken in the same organization",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* Database;

          // Create first claw
          yield* db.organizations.claws.create({
            userId: owner.id,
            organizationId: org.id,
            data: { slug: "shared-slug", displayName: "First Claw" },
          });

          // Try to create second claw with same slug
          const result = yield* db.organizations.claws
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { slug: "shared-slug", displayName: "Second Claw" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "A claw with this slug already exists in this organization",
          );
        }),
    );

    it.effect(
      "allows claws with the same slug across different organizations",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          // Create first organization and claw
          const user1 = yield* db.users.create({
            data: { email: "user1@example.com", name: "User 1" },
          });
          const org1 = yield* db.organizations.create({
            userId: user1.id,
            data: { name: "Org 1", slug: "org-1" },
          });
          const claw1 = yield* db.organizations.claws.create({
            userId: user1.id,
            organizationId: org1.id,
            data: { slug: "shared-slug", displayName: "Claw" },
          });

          // Create second organization and claw with same slug
          const user2 = yield* db.users.create({
            data: { email: "user2@example.com", name: "User 2" },
          });
          const org2 = yield* db.organizations.create({
            userId: user2.id,
            data: { name: "Org 2", slug: "org-2" },
          });
          const claw2 = yield* db.organizations.claws.create({
            userId: user2.id,
            organizationId: org2.id,
            data: { slug: "shared-slug", displayName: "Claw" },
          });

          // Both should succeed
          expect(claw1.slug).toBe("shared-slug");
          expect(claw2.slug).toBe("shared-slug");
          expect(claw1.id).not.toBe(claw2.id);
          expect(claw1.organizationId).not.toBe(claw2.organizationId);
        }),
    );

    it.effect(
      "returns `PlanLimitExceededError` when claw limit is exceeded",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestFreePlanOrganizationFixture;
          const db = yield* Database;

          // Create first claw (FREE plan allows 1)
          yield* db.organizations.claws.create({
            userId: owner.id,
            organizationId: org.id,
            data: { slug: "first-claw", displayName: "First Claw" },
          });

          // Try to create second claw - should fail
          const result = yield* db.organizations.claws
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { slug: "second-claw", displayName: "Second Claw" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PlanLimitExceededError);
          if (result instanceof PlanLimitExceededError) {
            expect(result.message).toContain("free plan limit is 1 claw(s)");
            expect(result.limitType).toBe("claws");
            expect(result.currentUsage).toBe(1);
            expect(result.limit).toBe(1);
          }
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

    it.effect("returns non-SqlError from getPlan in checkClawLimit", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { slug: "test-claw", displayName: "Test Claw" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found: org-id");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }]) // authorize: getRole
            .select([
              { memberId: "owner-id", role: "OWNER", createdAt: new Date() },
            ]) // findById
            .select([]) // checkClawLimit: getPlan -> org not found
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `DatabaseError` when counting claws fails in checkClawLimit",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { slug: "test-claw", displayName: "Test Claw" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to count claws");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([{ role: "OWNER" }]) // authorize: getRole
              .select([
                { memberId: "owner-id", role: "OWNER", createdAt: new Date() },
              ]) // findById
              .select([{ stripeCustomerId: "cus_test" }]) // checkClawLimit: getPlan
              .select(new Error("Connection failed")) // checkClawLimit: count fails
              .build(),
          ),
        ),
    );
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("org OWNER sees all claws in the organization", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Create claws
        yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "claw-1", displayName: "Claw 1" },
        });
        yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "claw-2", displayName: "Claw 2" },
        });

        // Owner sees all claws
        const ownerClaws = yield* db.organizations.claws.findAll({
          userId: owner.id,
          organizationId: org.id,
        });
        expect(ownerClaws).toHaveLength(2);

        // Member sees none (no claw membership)
        const memberClaws = yield* db.organizations.claws.findAll({
          userId: member.id,
          organizationId: org.id,
        });
        expect(memberClaws).toHaveLength(0);
      }),
    );

    it.effect("org MEMBER only sees claws they are members of", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Create claws
        const claw1 = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "claw-1", displayName: "Claw 1" },
        });
        yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "claw-2", displayName: "Claw 2" },
        });

        // Add member to claw1 only
        yield* db.organizations.claws.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw1.id,
          data: { memberId: member.id, role: "DEVELOPER" },
        });

        // Member only sees claw1
        const memberClaws = yield* db.organizations.claws.findAll({
          userId: member.id,
          organizationId: org.id,
        });
        expect(memberClaws).toHaveLength(1);
        expect(memberClaws[0].id).toBe(claw1.id);
      }),
    );

    it.effect("returns `NotFoundError` when non-member calls findAll", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .findAll({
            userId: nonMember.id,
            organizationId: org.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect(
      "returns `DatabaseError` when findAll query fails (privileged)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .findAll({
              userId: "owner-id",
              organizationId: "org-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to find all claws");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // organizationMemberships.findById -> authorize -> getRole
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // organizationMemberships.findById -> actual select
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // findAll query fails
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when findAll query fails (non-privileged)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .findAll({
              userId: "member-id",
              organizationId: "org-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to find all claws");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // organizationMemberships.findById -> authorize -> getRole
              .select([
                {
                  role: "MEMBER",
                  organizationId: "org-id",
                  memberId: "member-id",
                  createdAt: new Date(),
                },
              ])
              // organizationMemberships.findById -> actual select
              .select([
                {
                  role: "MEMBER",
                  organizationId: "org-id",
                  memberId: "member-id",
                  createdAt: new Date(),
                },
              ])
              // findAll query fails
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );
  });

  // ===========================================================================
  // findById
  // ===========================================================================

  describe("findById", () => {
    it.effect("finds a claw by id", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "test-claw", displayName: "Test Claw" },
        });

        const found = yield* db.organizations.claws.findById({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        expect(found.id).toBe(claw.id);
        expect(found.slug).toBe("test-claw");
        expect(found.displayName).toBe("Test Claw");
      }),
    );

    it.effect("returns `NotFoundError` when non-member tries to access", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "test-claw", displayName: "Test Claw" },
        });

        const result = yield* db.organizations.claws
          .findById({
            userId: nonMember.id,
            organizationId: org.id,
            clawId: claw.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns `NotFoundError` when claw does not exist", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            clawId: "nonexistent-claw-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org memberships getRole
            .select([{ role: "OWNER" }])
            // authorize: org memberships findById
            .select([
              {
                memberId: "owner-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "nonexistent-claw-id" }])
            // authorize: clawMemberships findById
            .select([
              {
                memberId: "owner-id",
                role: "ADMIN",
                clawId: "nonexistent-claw-id",
                createdAt: new Date(),
              },
            ])
            // findById: select claw
            .select([])
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when findById query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            clawId: "claw-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find claw");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org memberships getRole
            .select([{ role: "OWNER" }])
            // authorize: org memberships findById
            .select([
              {
                memberId: "owner-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: clawMemberships findById
            .select([
              {
                memberId: "owner-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // findById: select fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // update
  // ===========================================================================

  describe("update", () => {
    it.effect("updates claw displayName", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "test-claw", displayName: "Test Claw" },
        });

        const updated = yield* db.organizations.claws.update({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
          data: { displayName: "Updated Claw" },
        });

        expect(updated.displayName).toBe("Updated Claw");
        expect(updated.id).toBe(claw.id);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when DEVELOPER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const claw = yield* db.organizations.claws.create({
            userId: owner.id,
            organizationId: org.id,
            data: { slug: "test-claw", displayName: "Test Claw" },
          });

          // Add member as DEVELOPER
          yield* db.organizations.claws.memberships.create({
            userId: owner.id,
            organizationId: org.id,
            clawId: claw.id,
            data: { memberId: member.id, role: "DEVELOPER" },
          });

          const result = yield* db.organizations.claws
            .update({
              userId: member.id,
              organizationId: org.id,
              clawId: claw.id,
              data: { displayName: "Unauthorized Update" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when update triggers unique constraint",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              clawId: "claw-id",
              data: { displayName: "Updated" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "A claw with this slug already exists in this organization",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize: org memberships getRole
              .select([{ role: "OWNER" }])
              // authorize: org memberships findById
              .select([
                {
                  memberId: "owner-id",
                  role: "OWNER",
                  createdAt: new Date(),
                },
              ])
              // authorize: verifyClawExists
              .select([{ id: "claw-id" }])
              // authorize: clawMemberships findById
              .select([
                {
                  memberId: "owner-id",
                  role: "ADMIN",
                  clawId: "claw-id",
                  createdAt: new Date(),
                },
              ])
              // update fails with unique constraint error
              .update(
                Object.assign(new Error("unique_violation"), { code: "23505" }),
              )
              .build(),
          ),
        ),
    );

    it.effect("returns `DatabaseError` when update query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            clawId: "claw-id",
            data: { displayName: "Updated" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update claw");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org memberships getRole
            .select([{ role: "OWNER" }])
            // authorize: org memberships findById
            .select([
              {
                memberId: "owner-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: clawMemberships findById
            .select([
              {
                memberId: "owner-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // update fails
            .update(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `NotFoundError` when update returns empty result", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            clawId: "claw-id",
            data: { displayName: "Updated" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org memberships getRole
            .select([{ role: "OWNER" }])
            // authorize: org memberships findById
            .select([
              {
                memberId: "owner-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: clawMemberships findById
            .select([
              {
                memberId: "owner-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // update returns empty
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
    it.effect("deletes a claw", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "test-claw", displayName: "Test Claw" },
        });

        yield* db.organizations.claws.delete({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        // Verify it's gone
        const allClaws = yield* db.organizations.claws.findAll({
          userId: owner.id,
          organizationId: org.id,
        });
        expect(allClaws.find((c) => c.id === claw.id)).toBeUndefined();
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when DEVELOPER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const claw = yield* db.organizations.claws.create({
            userId: owner.id,
            organizationId: org.id,
            data: { slug: "test-claw", displayName: "Test Claw" },
          });

          // Add member as DEVELOPER
          yield* db.organizations.claws.memberships.create({
            userId: owner.id,
            organizationId: org.id,
            clawId: claw.id,
            data: { memberId: member.id, role: "DEVELOPER" },
          });

          const result = yield* db.organizations.claws
            .delete({
              userId: member.id,
              organizationId: org.id,
              clawId: claw.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect("returns `DatabaseError` when delete query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            clawId: "claw-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete claw");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org memberships getRole
            .select([{ role: "OWNER" }])
            // authorize: org memberships findById
            .select([
              {
                memberId: "owner-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: clawMemberships findById
            .select([
              {
                memberId: "owner-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // delete fails
            .delete(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `NotFoundError` when delete returns empty result", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            clawId: "claw-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org memberships getRole
            .select([{ role: "OWNER" }])
            // authorize: org memberships findById
            .select([
              {
                memberId: "owner-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: clawMemberships findById
            .select([
              {
                memberId: "owner-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // delete returns empty
            .delete([])
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // getRole
  // ===========================================================================

  describe("getRole", () => {
    it.effect("delegates to memberships.findById", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "test-claw", displayName: "Test Claw" },
        });

        const role = yield* db.organizations.claws.getRole({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        expect(role).toBe("ADMIN");
      }),
    );
  });
});
