import { Effect } from "effect";

import type {
  PublicClawMembership,
  PublicClawMembershipAudit,
} from "@/db/schema";

import { Database } from "@/db/database";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import {
  describe,
  it,
  expect,
  MockDrizzleORM,
  TestClawFixture,
} from "@/tests/db";

describe("ClawMemberships", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates a claw membership (ADMIN actor) and writes audit", () =>
      Effect.gen(function* () {
        const { claw, org, owner } = yield* TestClawFixture;
        const db = yield* Database;

        const newOrgMember = yield* db.users.create({
          data: {
            email: "new-org-member@example.com",
            name: "New Org Member",
          },
        });
        yield* db.organizations.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          data: { memberId: newOrgMember.id, role: "MEMBER" },
        });

        const membership = yield* db.organizations.claws.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
          data: { memberId: newOrgMember.id, role: "VIEWER" },
        });

        expect(membership).toMatchObject({
          clawId: claw.id,
          memberId: newOrgMember.id,
          role: "VIEWER",
        } satisfies Partial<PublicClawMembership>);

        // Verify audit was created
        const audits = yield* db.organizations.claws.memberships.audits.findAll(
          {
            clawId: claw.id,
            memberId: newOrgMember.id,
          },
        );

        expect(audits).toHaveLength(1);
        expect(audits[0]).toMatchObject({
          actorId: owner.id,
          targetId: newOrgMember.id,
          action: "GRANT",
          previousRole: null,
          newRole: "VIEWER",
        } satisfies Partial<PublicClawMembershipAudit>);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when non-ADMIN tries to create",
      () =>
        Effect.gen(function* () {
          const { claw, org, clawDeveloper } = yield* TestClawFixture;
          const db = yield* Database;

          const newOrgMember = yield* db.users.create({
            data: {
              email: "new-member-2@example.com",
              name: "New Member 2",
            },
          });
          yield* db.organizations.memberships
            .create({
              userId: clawDeveloper.id,
              organizationId: org.id,
              data: { memberId: newOrgMember.id, role: "MEMBER" },
            })
            .pipe(Effect.catchTag("PermissionDeniedError", () => Effect.void));

          const result = yield* db.organizations.claws.memberships
            .create({
              userId: clawDeveloper.id,
              organizationId: org.id,
              clawId: claw.id,
              data: { memberId: newOrgMember.id, role: "VIEWER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect("returns `AlreadyExistsError` when member is already added", () =>
      Effect.gen(function* () {
        const { claw, org, owner, clawAdmin } = yield* TestClawFixture;
        const db = yield* Database;

        // clawAdmin is already a member - try to add again
        const result = yield* db.organizations.claws.memberships
          .create({
            userId: owner.id,
            organizationId: org.id,
            clawId: claw.id,
            data: { memberId: clawAdmin.id, role: "DEVELOPER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect(result.message).toBe("User is already a member of this claw");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when target is not an org member (FK constraint)",
      () =>
        Effect.gen(function* () {
          const { claw, org, owner } = yield* TestClawFixture;
          const db = yield* Database;

          // Create a user who is NOT an org member
          const outsider = yield* db.users.create({
            data: {
              email: "outsider@example.com",
              name: "Outsider",
            },
          });

          const result = yield* db.organizations.claws.memberships
            .create({
              userId: owner.id,
              organizationId: org.id,
              clawId: claw.id,
              data: { memberId: outsider.id, role: "VIEWER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "User must be a member of the organization before being added to a claw",
          );
        }),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .create({
            userId: "admin-id",
            organizationId: "org-id",
            clawId: "claw-id",
            data: { memberId: "member-id", role: "DEVELOPER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create claw membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org getRole
            .select([{ role: "OWNER" }])
            // authorize: org findById
            .select([
              {
                memberId: "admin-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: claw memberships findById
            .select([
              {
                memberId: "admin-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // membership insert fails
            .insert(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .create({
            userId: "admin-id",
            organizationId: "org-id",
            clawId: "claw-id",
            data: { memberId: "member-id", role: "DEVELOPER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org getRole
            .select([{ role: "OWNER" }])
            // authorize: org findById
            .select([
              {
                memberId: "admin-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: claw memberships findById
            .select([
              {
                memberId: "admin-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // membership insert succeeds
            .insert([
              {
                clawId: "claw-id",
                memberId: "member-id",
                role: "DEVELOPER",
                createdAt: new Date(),
              },
            ])
            // audit insert fails
            .insert(new Error("Audit write failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("lists all members for a claw", () =>
      Effect.gen(function* () {
        const { claw, org, owner } = yield* TestClawFixture;
        const db = yield* Database;

        const members = yield* db.organizations.claws.memberships.findAll({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
        });

        // owner + clawAdmin + clawDeveloper + clawViewer + clawAnnotator = 5
        expect(members).toHaveLength(5);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when non-member calls findAll",
      () =>
        Effect.gen(function* () {
          const { claw, org, member } = yield* TestClawFixture;
          const db = yield* Database;

          // member is an org MEMBER but not a claw member
          const result = yield* db.organizations.claws.memberships
            .findAll({
              userId: member.id,
              organizationId: org.id,
              clawId: claw.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns `DatabaseError` when findAll query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .findAll({
            userId: "admin-id",
            organizationId: "org-id",
            clawId: "claw-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all claw memberships");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> organizationMemberships.findById -> authorize -> getRole
            .select([{ role: "OWNER" }])
            // authorize -> getRole -> organizationMemberships.findById -> actual select
            .select([
              {
                memberId: "admin-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize -> getRole -> verifyClawExists (org OWNER shortcircuit)
            .select([{ id: "claw-id" }])
            // findAll query fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `DatabaseError` when getMembership fails during authorization (non-OWNER)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws.memberships
            .findAll({
              userId: "member-id",
              organizationId: "org-id",
              clawId: "claw-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get claw membership");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize -> getRole -> organizationMemberships.findById -> authorize -> getRole
              .select([{ role: "MEMBER" }])
              // authorize -> getRole -> organizationMemberships.findById -> actual select
              .select([
                {
                  memberId: "member-id",
                  role: "MEMBER",
                  createdAt: new Date(),
                },
              ])
              // getMembership: DB query fails (covers line 260)
              .select(new Error("Database connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when claw verification fails during authorization",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws.memberships
            .findAll({
              userId: "owner-id",
              organizationId: "org-id",
              clawId: "claw-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to verify claw");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize -> getRole -> organizationMemberships.findById -> authorize -> getRole
              .select([{ role: "OWNER" }])
              // authorize -> getRole -> organizationMemberships.findById -> actual select
              .select([
                {
                  memberId: "owner-id",
                  role: "OWNER",
                  createdAt: new Date(),
                },
              ])
              // verifyClawExists: DB query fails (covers line 360)
              .select(new Error("Database connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `NotFoundError` when claw does not exist during authorization",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.claws.memberships
            .findAll({
              userId: "owner-id",
              organizationId: "org-id",
              clawId: "nonexistent-claw-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Claw not found");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize -> getRole -> organizationMemberships.findById -> authorize -> getRole
              .select([{ role: "OWNER" }])
              // authorize -> getRole -> organizationMemberships.findById -> actual select
              .select([
                {
                  memberId: "owner-id",
                  role: "OWNER",
                  createdAt: new Date(),
                },
              ])
              // verifyClawExists: empty result (covers line 368)
              .select([])
              .build(),
          ),
        ),
    );
  });

  // ===========================================================================
  // findById
  // ===========================================================================

  describe("findById", () => {
    it.effect("finds a specific membership", () =>
      Effect.gen(function* () {
        const { claw, org, owner, clawAdmin } = yield* TestClawFixture;
        const db = yield* Database;

        const membership = yield* db.organizations.claws.memberships.findById({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
          memberId: clawAdmin.id,
        });

        expect(membership.memberId).toBe(clawAdmin.id);
        expect(membership.role).toBe("ADMIN");
      }),
    );

    it.effect("returns `NotFoundError` when membership does not exist", () =>
      Effect.gen(function* () {
        const { claw, org, owner, member } = yield* TestClawFixture;
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .findById({
            userId: owner.id,
            organizationId: org.id,
            clawId: claw.id,
            memberId: member.id, // org member, but not a claw member
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `Membership for member ${member.id} not found`,
        );
      }),
    );

    it.effect("returns `DatabaseError` when findById query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .findById({
            userId: "admin-id",
            organizationId: "org-id",
            clawId: "claw-id",
            memberId: "member-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find claw membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> organizationMemberships.findById -> authorize -> getRole
            .select([{ role: "OWNER" }])
            // authorize -> getRole -> organizationMemberships.findById -> actual select
            .select([
              {
                memberId: "admin-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize -> getRole -> verifyClawExists (org OWNER shortcircuit)
            .select([{ id: "claw-id" }])
            // findById query fails
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
    it.effect("updates a membership role and writes audit", () =>
      Effect.gen(function* () {
        const { claw, org, owner, clawDeveloper } = yield* TestClawFixture;
        const db = yield* Database;

        const updated = yield* db.organizations.claws.memberships.update({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
          memberId: clawDeveloper.id,
          data: { role: "ADMIN" },
        });

        expect(updated.role).toBe("ADMIN");

        // Verify audit was created
        const audits = yield* db.organizations.claws.memberships.audits.findAll(
          {
            clawId: claw.id,
            memberId: clawDeveloper.id,
          },
        );

        // GRANT from fixture + CHANGE = 2
        const changeAudit = audits.find((a) => a.action === "CHANGE");
        expect(changeAudit).toBeDefined();
        expect(changeAudit).toMatchObject({
          actorId: owner.id,
          targetId: clawDeveloper.id,
          action: "CHANGE",
          previousRole: "DEVELOPER",
          newRole: "ADMIN",
        } satisfies Partial<PublicClawMembershipAudit>);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when non-ADMIN tries to update",
      () =>
        Effect.gen(function* () {
          const { claw, org, clawDeveloper, clawViewer } =
            yield* TestClawFixture;
          const db = yield* Database;

          const result = yield* db.organizations.claws.memberships
            .update({
              userId: clawDeveloper.id,
              organizationId: org.id,
              clawId: claw.id,
              memberId: clawViewer.id,
              data: { role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect("returns `DatabaseError` when update query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .update({
            userId: "admin-id",
            organizationId: "org-id",
            clawId: "claw-id",
            memberId: "member-id",
            data: { role: "ADMIN" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update claw membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org getRole
            .select([{ role: "OWNER" }])
            // authorize: org findById
            .select([
              {
                memberId: "admin-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: claw memberships findById
            .select([
              {
                memberId: "admin-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // getMembership for existing
            .select([{ role: "DEVELOPER" }])
            // update fails
            .update(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .update({
            userId: "admin-id",
            organizationId: "org-id",
            clawId: "claw-id",
            memberId: "member-id",
            data: { role: "ADMIN" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org getRole
            .select([{ role: "OWNER" }])
            // authorize: org findById
            .select([
              {
                memberId: "admin-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: claw memberships findById
            .select([
              {
                memberId: "admin-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // getMembership for existing
            .select([{ role: "DEVELOPER" }])
            // update succeeds
            .update([
              {
                clawId: "claw-id",
                memberId: "member-id",
                role: "ADMIN",
                createdAt: new Date(),
              },
            ])
            // audit insert fails
            .insert(new Error("Audit write failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // delete
  // ===========================================================================

  describe("delete", () => {
    it.effect("deletes a membership and writes audit", () =>
      Effect.gen(function* () {
        const { claw, org, owner, clawDeveloper } = yield* TestClawFixture;
        const db = yield* Database;

        yield* db.organizations.claws.memberships.delete({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
          memberId: clawDeveloper.id,
        });

        // Verify audit was created
        const audits = yield* db.organizations.claws.memberships.audits.findAll(
          {
            clawId: claw.id,
            memberId: clawDeveloper.id,
          },
        );

        const revokeAudit = audits.find((a) => a.action === "REVOKE");
        expect(revokeAudit).toBeDefined();
        expect(revokeAudit).toMatchObject({
          actorId: owner.id,
          targetId: clawDeveloper.id,
          action: "REVOKE",
          previousRole: "DEVELOPER",
          newRole: null,
        } satisfies Partial<PublicClawMembershipAudit>);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when non-ADMIN tries to delete",
      () =>
        Effect.gen(function* () {
          const { claw, org, clawDeveloper, clawViewer } =
            yield* TestClawFixture;
          const db = yield* Database;

          const result = yield* db.organizations.claws.memberships
            .delete({
              userId: clawDeveloper.id,
              organizationId: org.id,
              clawId: claw.id,
              memberId: clawViewer.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect("returns `DatabaseError` when delete query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .delete({
            userId: "admin-id",
            organizationId: "org-id",
            clawId: "claw-id",
            memberId: "member-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete claw membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org getRole
            .select([{ role: "OWNER" }])
            // authorize: org findById
            .select([
              {
                memberId: "admin-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: claw memberships findById
            .select([
              {
                memberId: "admin-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // getMembership for existing
            .select([{ role: "DEVELOPER" }])
            // delete fails
            .delete(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit insert fails on delete", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .delete({
            userId: "admin-id",
            organizationId: "org-id",
            clawId: "claw-id",
            memberId: "member-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: org getRole
            .select([{ role: "OWNER" }])
            // authorize: org findById
            .select([
              {
                memberId: "admin-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize: verifyClawExists
            .select([{ id: "claw-id" }])
            // authorize: claw memberships findById
            .select([
              {
                memberId: "admin-id",
                role: "ADMIN",
                clawId: "claw-id",
                createdAt: new Date(),
              },
            ])
            // getMembership for existing
            .select([{ role: "DEVELOPER" }])
            // delete succeeds
            .delete([])
            // audit insert fails
            .insert(new Error("Audit write failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findAllWithUserInfo
  // ===========================================================================

  describe("findAllWithUserInfo", () => {
    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships
          .findAllWithUserInfo({
            userId: "admin-id",
            organizationId: "org-id",
            clawId: "claw-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe(
          "Failed to find all claw memberships with user info",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> organizationMemberships.findById -> authorize -> getRole
            .select([{ role: "OWNER" }])
            // authorize -> getRole -> organizationMemberships.findById -> actual select
            .select([
              {
                memberId: "admin-id",
                role: "OWNER",
                createdAt: new Date(),
              },
            ])
            // authorize -> getRole -> verifyClawExists (org OWNER shortcircuit)
            .select([{ id: "claw-id" }])
            // findAllWithUserInfo query fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // audits
  // ===========================================================================

  describe("audits", () => {
    it.effect("finds audit entries for a member", () =>
      Effect.gen(function* () {
        const { claw, org, owner, clawDeveloper } = yield* TestClawFixture;
        const db = yield* Database;

        // The fixture already created GRANT audits for all members
        const audits = yield* db.organizations.claws.memberships.audits.findAll(
          {
            clawId: claw.id,
            memberId: clawDeveloper.id,
          },
        );

        expect(audits).toHaveLength(1);
        expect(audits[0].action).toBe("GRANT");
        expect(audits[0].newRole).toBe("DEVELOPER");

        // Now update the role to create another audit entry
        yield* db.organizations.claws.memberships.update({
          userId: owner.id,
          organizationId: org.id,
          clawId: claw.id,
          memberId: clawDeveloper.id,
          data: { role: "ADMIN" },
        });

        const updatedAudits =
          yield* db.organizations.claws.memberships.audits.findAll({
            clawId: claw.id,
            memberId: clawDeveloper.id,
          });

        expect(updatedAudits).toHaveLength(2);
        const changeAudit = updatedAudits.find((a) => a.action === "CHANGE");
        expect(changeAudit).toBeDefined();
      }),
    );

    it.effect("returns `DatabaseError` when audit query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.claws.memberships.audits
          .findAll({
            clawId: "claw-id",
            memberId: "member-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find audit entries");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Connection failed")).build(),
        ),
      ),
    );
  });
});
