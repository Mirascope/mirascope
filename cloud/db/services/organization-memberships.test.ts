import { describe, expect } from "vitest";
import { it } from "@effect/vitest";
import {
  TestDatabase,
  TestOrganizationFixture,
  MockDatabase,
} from "@/tests/db";
import { DatabaseService } from "@/db/services";
import { Effect } from "effect";
import {
  type PublicOrganizationMembership,
  type PublicOrganizationMembershipAudit,
} from "@/db/schema";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";

describe("OrganizationMembershipService", () => {
  // ===========================================================================
  // Create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates a membership for a target user", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows ADMIN to create memberships", () =>
      Effect.gen(function* () {
        const { org, admin, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "path param organizationId overwrites data.organizationId (security)",
      () =>
        Effect.gen(function* () {
          const { org, owner, nonMember } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          // Try to inject a different organizationId in data
          // The path param should be authoritative
          yield* db.organizations.memberships.create({
            userId: owner.id,
            organizationId: org.id, // path param - authoritative
            data: {
              memberId: nonMember.id,
              // @ts-expect-error - this should not be present in the data
              organizationId: "injected-org-id", // should be ignored regardless
              role: "MEMBER",
            },
          });

          // Verify the membership was created in the correct org
          const found = yield* db.organizations.memberships.findById({
            userId: owner.id,
            organizationId: org.id,
            memberId: nonMember.id,
          });

          expect(found.role).toBe("MEMBER");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `PermissionDeniedError` when trying to add OWNER", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations.memberships
          .create({
            userId: owner.id,
            organizationId: org.id,
            data: { memberId: nonMember.id, role: "OWNER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toBe("Cannot add a member with role OWNER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to add yourself",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations.memberships
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { memberId: owner.id, role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot add yourself to an organization");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const anotherUser = yield* db.users.create({
          data: { email: "another@example.com", name: "Another User" },
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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to add ADMIN",
      () =>
        Effect.gen(function* () {
          const { org, admin, nonMember } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations.memberships
            .create({
              userId: admin.id,
              organizationId: org.id,
              data: { memberId: nonMember.id, role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot add a member with role ADMIN");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to create",
      () =>
        Effect.gen(function* () {
          const { org, member, nonMember } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to create (second case)",
      () =>
        Effect.gen(function* () {
          const { org, member, nonMember } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `AlreadyExistsError` when user is already a member",
      () =>
        Effect.gen(function* () {
          const { org, owner, nonMember } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // authorize: membership found with OWNER role
          .select([{ role: "OWNER" }])
          // insert membership: fails
          .insert(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations.memberships
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { memberId: "target-id", role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create organization membership");
      }),
    );
  });

  // ===========================================================================
  // Find All
  // ===========================================================================

  describe("findAll", () => {
    it.effect("retrieves all memberships for an organization", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows any member role to read memberships", () =>
      Effect.gen(function* () {
        const { org, member } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const memberships = yield* db.organizations.memberships.findAll({
          userId: member.id,
          organizationId: org.id,
        });

        expect(memberships).toHaveLength(3);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations.memberships
          .findAll({
            userId: nonMember.id,
            organizationId: org.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // authorize: membership found
          .select([{ role: "OWNER" }])
          // findAll: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations.memberships
          .findAll({
            userId: "user-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe(
          "Failed to find all organization memberships",
        );
      }),
    );
  });

  // ===========================================================================
  // Find By ID
  // ===========================================================================

  describe("findById", () => {
    it.effect("retrieves a specific membership", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const membership = yield* db.organizations.memberships.findById({
          userId: owner.id,
          organizationId: org.id,
          memberId: member.id,
        });

        expect(membership.role).toBe("MEMBER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows any member to read another member's info", () =>
      Effect.gen(function* () {
        const { org, member, admin } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const membership = yield* db.organizations.memberships.findById({
          userId: member.id,
          organizationId: org.id,
          memberId: admin.id,
        });

        expect(membership.role).toBe("ADMIN");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when membership doesn't exist", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations.memberships
          .findById({
            userId: owner.id,
            organizationId: org.id,
            memberId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations.memberships
          .findById({
            userId: nonMember.id,
            organizationId: org.id,
            memberId: owner.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // authorize: membership found
          .select([{ role: "OWNER" }])
          // findById: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations.memberships
          .findById({
            userId: "user-id",
            organizationId: "org-id",
            memberId: "target-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find organization membership");
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
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows ADMIN to update memberships", () =>
      Effect.gen(function* () {
        const { org, admin, member } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to change role to OWNER",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to modify your own membership",
      () =>
        Effect.gen(function* () {
          const { org, admin } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to change an owner's role",
      () =>
        Effect.gen(function* () {
          const { org, admin, owner } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to update ADMIN",
      () =>
        Effect.gen(function* () {
          const { org, owner, admin } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          // Create a second ADMIN
          const secondAdmin = yield* db.users.create({
            data: { email: "admin2@example.com", name: "Admin 2" },
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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to promote to ADMIN",
      () =>
        Effect.gen(function* () {
          const { org, admin, member } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, member, admin } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const anotherMember = yield* db.users.create({
            data: {
              email: "another-member@example.com",
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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `DatabaseError` when getMembership for target fails",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // authorize: membership found with OWNER role
            .select([{ role: "OWNER" }])
            // getMembership for target: fails
            .select(new Error("Database connection failed"))
            .build();

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
        }),
    );

    it.effect(
      "returns `NotFoundError` when target membership doesn't exist",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // authorize: membership found with OWNER role
            .select([{ role: "OWNER" }])
            // getMembership for target: not found
            .select([])
            .build();

          const result = yield* db.organizations.memberships
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              memberId: "nonexistent-id",
              data: { role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "User is not a member of this organization",
          );
        }),
    );

    it.effect("returns `DatabaseError` when update fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // authorize: membership found with OWNER role
          .select([{ role: "OWNER" }])
          // getMembership for target: returns MEMBER
          .select([{ role: "MEMBER" }])
          // update: fails
          .update(new Error("Database connection failed"))
          .build();

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
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to remove yourself",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations.memberships
            .delete({
              userId: owner.id,
              organizationId: org.id,
              memberId: owner.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "Cannot remove yourself from an organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to remove an owner",
      () =>
        Effect.gen(function* () {
          // We need to use a mock here since we can't have two owners
          const db = new MockDatabase()
            // authorize: membership found with OWNER role
            .select([{ role: "OWNER" }])
            // getMembership for target: returns OWNER
            .select([{ role: "OWNER" }])
            .build();

          const result = yield* db.organizations.memberships
            .delete({
              userId: "admin-id",
              organizationId: "org-id",
              memberId: "owner-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot remove a member with role OWNER");
        }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations.memberships
          .delete({
            userId: nonMember.id,
            organizationId: org.id,
            memberId: "some-user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows ADMIN to delete MEMBER", () =>
      Effect.gen(function* () {
        const { org, admin, member } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

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
        } satisfies Partial<PublicOrganizationMembershipAudit>);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to delete ADMIN",
      () =>
        Effect.gen(function* () {
          const { org, owner, admin } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          // Create a second ADMIN
          const secondAdmin = yield* db.users.create({
            data: { email: "admin2@example.com", name: "Admin 2" },
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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `DatabaseError` when getMembership for target fails",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // authorize: membership found with OWNER role
            .select([{ role: "OWNER" }])
            // getMembership for target: fails
            .select(new Error("Database connection failed"))
            .build();

          const result = yield* db.organizations.memberships
            .delete({
              userId: "owner-id",
              organizationId: "org-id",
              memberId: "target-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get membership");
        }),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // authorize: membership found with OWNER role
          .select([{ role: "OWNER" }])
          // getMembership for target: returns MEMBER
          .select([{ role: "MEMBER" }])
          // delete: fails
          .delete(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations.memberships
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            memberId: "target-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete organization membership");
      }),
    );

    it.effect(
      "returns `NotFoundError` when target membership doesn't exist",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // authorize: membership found with OWNER role
            .select([{ role: "OWNER" }])
            // getMembership for target: not found
            .select([])
            .build();

          const result = yield* db.organizations.memberships
            .delete({
              userId: "owner-id",
              organizationId: "org-id",
              memberId: "nonexistent-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "User is not a member of this organization",
          );
        }),
    );
  });
});
