import { and, eq } from "drizzle-orm";
import { Effect, Layer } from "effect";

import type { PublicClaw } from "@/db/schema";

import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { claws, users } from "@/db/schema";
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

        // Verify service account resources were created
        expect(claw.botUserId).toBeDefined();
        expect(claw.homeProjectId).toBeDefined();
        expect(claw.homeEnvironmentId).toBeDefined();

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

    it.effect("creates a claw without displayName (uses slug)", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "no-display-name" },
        });

        expect(claw.slug).toBe("no-display-name");
        expect(claw.displayName).toBeNull();
        expect(claw.botUserId).toBeDefined();
      }),
    );

    it.effect("creates a claw with existing homeProjectId", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Create a project to use as home project
        const project = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Existing Project", slug: "existing-project" },
        });

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: {
            slug: "claw-with-project",
            displayName: "Claw With Project",
            homeProjectId: project.id,
          },
        });

        // Should use the provided project, not create a new one
        expect(claw.homeProjectId).toBe(project.id);
        expect(claw.botUserId).toBeDefined();
        expect(claw.homeEnvironmentId).toBeDefined();
      }),
    );

    it.effect("returns `NotFoundError` when homeProjectId does not exist", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .create({
            userId: owner.id,
            organizationId: org.id,
            data: {
              slug: "claw-bad-project",
              displayName: "Claw Bad Project",
              homeProjectId: owner.id, // valid UUID but not a project
            },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "Home project not found or does not belong to this organization",
        );
      }),
    );

    it.effect(
      "returns `DatabaseError` when home project validation query fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: {
                slug: "test-claw",
                displayName: "Test Claw",
                homeProjectId: "project-id",
              },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to validate home project");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize: getRole
              .select([{ role: "OWNER" }])
              // findById: get membership
              .select([
                {
                  memberId: "owner-id",
                  role: "OWNER",
                  createdAt: new Date(),
                },
              ])
              // checkClawLimit: getPlan -> fetch organization
              .select([{ stripeCustomerId: "cus_test" }])
              // checkClawLimit: count claws (under limit)
              .select([{ count: 0 }])
              // getPlan (for plan defaults)
              .select([{ stripeCustomerId: "cus_test" }])
              // claw insert (success)
              .insert([
                {
                  id: "claw-id",
                  slug: "test-claw",
                  displayName: "Test Claw",
                  organizationId: "org-id",
                  createdByUserId: "owner-id",
                },
              ])
              // create claw-user (success)
              .insert([{ id: "bot-user-id" }])
              // add claw-user to org (success)
              .insert([{}])
              // validate homeProjectId - fails with DB error
              .select(new Error("Database connection failed"))
              .build(),
          ),
        ),
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
    it.effect("deletes a claw and soft-deletes the bot user", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "test-claw", displayName: "Test Claw" },
        });

        // Bot user should exist before deletion
        expect(claw.botUserId).toBeTruthy();
        const client = yield* DrizzleORM;
        const [botUserBefore] = yield* client
          .select({ id: users.id, deletedAt: users.deletedAt })
          .from(users)
          .where(eq(users.id, claw.botUserId!));
        expect(botUserBefore).toBeDefined();
        expect(botUserBefore.deletedAt).toBeNull();

        yield* db.organizations.claws.delete({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        // Verify claw is gone
        const allClaws = yield* db.organizations.claws.findAll({
          userId: owner.id,
          organizationId: org.id,
        });
        expect(allClaws.find((c) => c.id === claw.id)).toBeUndefined();

        // Verify bot user is soft-deleted
        const [botUserAfter] = yield* client
          .select({ id: users.id, deletedAt: users.deletedAt })
          .from(users)
          .where(eq(users.id, claw.botUserId!));
        expect(botUserAfter.deletedAt).not.toBeNull();
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

    it.effect("deletes a claw without bot user (no bot user cleanup)", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        // Should succeed without attempting bot user soft-delete
        yield* db.organizations.claws.delete({
          userId: "owner-id",
          organizationId: "org-id",
          clawId: "claw-id",
        });
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
            // delete succeeds with no botUserId
            .delete([{ id: "claw-id", botUserId: null }])
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when bot user soft-delete fails", () =>
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
        expect(result.message).toBe("Failed to delete bot user");
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
            // delete succeeds with botUserId
            .delete([{ id: "claw-id", botUserId: "bot-user-id" }])
            // bot user soft-delete fails
            .update(new Error("Connection failed"))
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

  // ===========================================================================
  // recordUsage
  // ===========================================================================

  describe("recordUsage", () => {
    it.effect("records initial usage (sets up windows from null)", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "usage-claw", displayName: "Usage Claw" },
        });

        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 100n,
        });

        const updated = yield* db.organizations.claws.findById({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        expect(updated.weeklyUsageCenticents).toBe(100n);
        expect(updated.weeklyWindowStart).toBeInstanceOf(Date);
        expect(updated.burstUsageCenticents).toBe(100n);
        expect(updated.burstWindowStart).toBeInstanceOf(Date);
      }),
    );

    it.effect("accumulates usage on subsequent calls", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "accum-claw", displayName: "Accumulate Claw" },
        });

        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 100n,
        });

        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 200n,
        });

        const updated = yield* db.organizations.claws.findById({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        expect(updated.weeklyUsageCenticents).toBe(300n);
        expect(updated.burstUsageCenticents).toBe(300n);
      }),
    );

    it.effect("resets weekly window when expired", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;
        const client = yield* DrizzleORM;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "weekly-reset-claw", displayName: "Weekly Reset" },
        });

        // Record initial usage
        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 500n,
        });

        // Set weekly window start to 8 days ago (expires for 7-day weekly reset)
        const pastDate = new Date(Date.now() - 8 * 24 * 60 * 60 * 1000);
        yield* client
          .update(claws)
          .set({ weeklyWindowStart: pastDate })
          .where(and(eq(claws.id, claw.id), eq(claws.organizationId, org.id)));

        // Record more usage — should reset weekly window
        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 50n,
        });

        const updated = yield* db.organizations.claws.findById({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        // Weekly was reset: only the new 50n
        expect(updated.weeklyUsageCenticents).toBe(50n);
        // Burst was NOT reset (5-hour window hasn't expired): 500 + 50
        expect(updated.burstUsageCenticents).toBe(550n);
      }),
    );

    it.effect("resets burst window when expired", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;
        const client = yield* DrizzleORM;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "burst-reset-claw", displayName: "Burst Reset" },
        });

        // Record initial usage
        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 500n,
        });

        // Set burst window start to 6 hours ago (expires for 5-hour burst)
        const pastDate = new Date(Date.now() - 6 * 60 * 60 * 1000);
        yield* client
          .update(claws)
          .set({ burstWindowStart: pastDate })
          .where(and(eq(claws.id, claw.id), eq(claws.organizationId, org.id)));

        // Record more usage — should reset burst window
        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 50n,
        });

        const updated = yield* db.organizations.claws.findById({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        // Weekly was NOT reset: 500 + 50
        expect(updated.weeklyUsageCenticents).toBe(550n);
        // Burst was reset: only the new 50n
        expect(updated.burstUsageCenticents).toBe(50n);
      }),
    );

    it.effect("enforces per-claw spending guardrail", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;
        const client = yield* DrizzleORM;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "guardrail-claw", displayName: "Guardrail Claw" },
        });

        // Set a spending guardrail
        yield* client
          .update(claws)
          .set({ weeklySpendingGuardrailCenticents: 500n })
          .where(and(eq(claws.id, claw.id), eq(claws.organizationId, org.id)));

        // First usage: under guardrail
        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 400n,
        });

        // Second usage: would exceed guardrail
        const result = yield* db.organizations.claws
          .recordUsage({
            clawId: claw.id,
            organizationId: org.id,
            amountCenticents: 200n,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PlanLimitExceededError);
        if (result instanceof PlanLimitExceededError) {
          expect(result.limitType).toBe("weeklySpendingGuardrail");
          expect(result.currentUsage).toBe(600);
          expect(result.limit).toBe(500);
        }
      }),
    );

    it.effect("returns `NotFoundError` when claw does not exist", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .recordUsage({
            clawId: "nonexistent-claw-id",
            organizationId: "org-id",
            amountCenticents: 100n,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // recordUsage: select claw → empty
            .select([])
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when select fails in recordUsage", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .recordUsage({
            clawId: "claw-id",
            organizationId: "org-id",
            amountCenticents: 100n,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get claw for usage recording");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // recordUsage: select fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when update fails in recordUsage", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .recordUsage({
            clawId: "claw-id",
            organizationId: "org-id",
            amountCenticents: 100n,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to record usage");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // recordUsage: select claw
            .select([
              {
                weeklyWindowStart: new Date(),
                weeklyUsageCenticents: 0n,
                burstWindowStart: new Date(),
                burstUsageCenticents: 0n,
                weeklySpendingGuardrailCenticents: null,
              },
            ])
            // getPlan: fetch organization
            .select([{ stripeCustomerId: "cus_test" }])
            // update fails
            .update(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // getPoolUsage
  // ===========================================================================

  describe("getPoolUsage", () => {
    it.effect("returns total usage across all claws in org", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Create two claws and record usage
        const claw1 = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "pool-claw-1", displayName: "Pool Claw 1" },
        });
        const claw2 = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "pool-claw-2", displayName: "Pool Claw 2" },
        });

        yield* db.organizations.claws.recordUsage({
          clawId: claw1.id,
          organizationId: org.id,
          amountCenticents: 300n,
        });
        yield* db.organizations.claws.recordUsage({
          clawId: claw2.id,
          organizationId: org.id,
          amountCenticents: 700n,
        });

        const pool = yield* db.organizations.claws.getPoolUsage({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(pool.totalUsageCenticents).toBe(1000n);
        expect(pool.limitCenticents).toBeGreaterThan(0);
        expect(pool.percentUsed).toBeGreaterThan(0);
      }),
    );

    it.effect("returns 0 when no claws have usage", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const pool = yield* db.organizations.claws.getPoolUsage({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(pool.totalUsageCenticents).toBe(0n);
        expect(pool.percentUsed).toBe(0);
      }),
    );

    it.effect(
      "returns `NotFoundError` when non-member calls getPoolUsage",
      () =>
        Effect.gen(function* () {
          const { org, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .getPoolUsage({
              userId: nonMember.id,
              organizationId: org.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns `DatabaseError` when pool query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .getPoolUsage({
            userId: "owner-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get pool usage");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // org memberships getRole
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // org memberships findById
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // pool SUM query fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // getInternalPoolUsage
  // ===========================================================================

  describe("getInternalPoolUsage", () => {
    it.effect("returns total usage and limit without auth", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "internal-pool-claw", displayName: "Internal Pool" },
        });

        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 500n,
        });

        const pool = yield* db.organizations.claws.getInternalPoolUsage({
          organizationId: org.id,
        });

        expect(pool.totalUsageCenticents).toBe(500n);
        expect(pool.limitCenticents).toBeGreaterThan(0);
      }),
    );

    it.effect("returns 0 usage when no claws have usage", () =>
      Effect.gen(function* () {
        const { org } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const pool = yield* db.organizations.claws.getInternalPoolUsage({
          organizationId: org.id,
        });

        expect(pool.totalUsageCenticents).toBe(0n);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .getInternalPoolUsage({
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get internal pool usage");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // pool SUM query fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // getClawUsage
  // ===========================================================================

  describe("getClawUsage", () => {
    it.effect("returns usage info with pool data", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "usage-info-claw", displayName: "Usage Info Claw" },
        });

        yield* db.organizations.claws.recordUsage({
          clawId: claw.id,
          organizationId: org.id,
          amountCenticents: 250n,
        });

        const usage = yield* db.organizations.claws.getClawUsage({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        expect(usage.weeklyUsageCenticents).toBe(250n);
        expect(usage.weeklyWindowStart).toBeInstanceOf(Date);
        expect(usage.burstUsageCenticents).toBe(250n);
        expect(usage.burstWindowStart).toBeInstanceOf(Date);
        expect(usage.weeklySpendingGuardrailCenticents).toBeNull();
        expect(usage.poolUsageCenticents).toBe(250n);
        expect(usage.poolLimitCenticents).toBeGreaterThan(0);
        expect(usage.poolPercentUsed).toBeGreaterThan(0);
      }),
    );

    it.effect("returns `NotFoundError` for non-member", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const claw = yield* db.organizations.claws.create({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: "auth-usage-claw", displayName: "Auth Usage Claw" },
        });

        const result = yield* db.organizations.claws
          .getClawUsage({
            userId: nonMember.id,
            organizationId: org.id,
            clawId: claw.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect(
      "returns `NotFoundError` when claw does not exist in getClawUsage",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .getClawUsage({
              userId: "owner-id",
              organizationId: "org-id",
              clawId: "nonexistent-claw-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toContain("not found");
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
              // getClawUsage: select claw → empty
              .select([])
              .build(),
          ),
        ),
    );

    it.effect("returns `DatabaseError` when usage query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws
          .getClawUsage({
            userId: "owner-id",
            organizationId: "org-id",
            clawId: "claw-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get claw usage");
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
            // getClawUsage: select fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `DatabaseError` when pool query fails in getClawUsage",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws
            .getClawUsage({
              userId: "owner-id",
              organizationId: "org-id",
              clawId: "claw-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get pool usage");
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
              // getClawUsage: select claw
              .select([
                {
                  weeklyUsageCenticents: 100n,
                  weeklyWindowStart: new Date(),
                  burstUsageCenticents: 50n,
                  burstWindowStart: new Date(),
                  weeklySpendingGuardrailCenticents: null,
                },
              ])
              // pool SUM query fails
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );
  });
});
