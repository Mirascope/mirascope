import {
  describe,
  it,
  expect,
  MockDrizzleORM,
  TestProjectFixture,
} from "@/tests/db";
import { Effect } from "effect";
import { Database } from "@/db/database";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import type {
  PublicProjectMembership,
  PublicProjectMembershipAudit,
} from "@/db/schema";

describe("ProjectMemberships", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect(
      "creates a project membership (ADMIN actor) and writes audit",
      () =>
        Effect.gen(function* () {
          const { project, org, owner } = yield* TestProjectFixture;
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

          const membership = yield* db.organizations.projects.memberships.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { memberId: newOrgMember.id, role: "VIEWER" },
          });

          expect(membership).toMatchObject({
            projectId: project.id,
            memberId: newOrgMember.id,
            role: "VIEWER",
          } satisfies Partial<PublicProjectMembership>);

          const audits = yield* db.organizations.projects.memberships.audits.findAll({
            projectId: project.id,
            memberId: newOrgMember.id,
          });
          const grants = audits.filter((a) => a.action === "GRANT");
          expect(grants).toHaveLength(1);
          expect(grants[0]).toMatchObject({
            actorId: owner.id,
            targetId: newOrgMember.id,
            action: "GRANT",
            previousRole: null,
            newRole: "VIEWER",
          } satisfies Partial<PublicProjectMembershipAudit>);
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when target is not an org member",
      () =>
        Effect.gen(function* () {
          const { project, org, owner } = yield* TestProjectFixture;
          const db = yield* Database;

          const outsider = yield* db.users.create({
            data: { email: "outsider@example.com", name: "Outsider" },
          });

          const result = yield* db.organizations.projects.memberships
            .create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              data: { memberId: outsider.id, role: "DEVELOPER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "User must be a member of the organization before being added to a project",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when actor is not ADMIN (read-only role)",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, projectDeveloper } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const anotherOrgMember = yield* db.users.create({
            data: {
              email: "another-org-member@example.com",
              name: "Another Org Member",
            },
          });
          yield* db.organizations.memberships.create({
            userId: owner.id,
            organizationId: org.id,
            data: { memberId: anotherOrgMember.id, role: "MEMBER" },
          });

          const result = yield* db.organizations.projects.memberships
            .create({
              userId: projectDeveloper.id, // DEVELOPER role (read-only)
              organizationId: org.id,
              projectId: project.id,
              data: { memberId: anotherOrgMember.id, role: "DEVELOPER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to create this project membership",
          );
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when user is already a member",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, projectDeveloper } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              data: { memberId: projectDeveloper.id, role: "VIEWER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "User is already a member of this project",
          );
        }),
    );

    it.effect("returns `NotFoundError` when project does not exist", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestProjectFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .create({
            userId: owner.id,
            organizationId: org.id,
            projectId: "00000000-0000-0000-0000-000000000000",
            data: { memberId: member.id, role: "VIEWER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            data: { memberId: "target-id", role: "VIEWER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create project membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize(create) -> getRole -> organizationMemberships.findById (actor)
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists: exists
            .select([{ id: "project-id" }])
            // transaction insert fails
            .insert(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `PermissionDeniedError` when FK constraint fails (target not org member)",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, nonMember } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              data: { memberId: nonMember.id, role: "VIEWER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "User must be a member of the organization before being added to a project",
          );
        }),
    );

    it.effect("returns `DatabaseError` when audit log insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            data: { memberId: "target-id", role: "VIEWER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize(create) -> getRole -> organizationMemberships.findById (actor)
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists: exists
            .select([{ id: "project-id" }])
            // transaction membership insert succeeds
            .insert([
              {
                projectId: "project-id",
                memberId: "target-id",
                role: "VIEWER",
                createdAt: new Date(),
              },
            ])
            // audit log insert fails
            .insert(new Error("Audit log insert failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("retrieves all memberships for a project", () =>
      Effect.gen(function* () {
        const { project, org, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const memberships = yield* db.organizations.projects.memberships.findAll({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
        });

        // Fixture creates 5 explicit project members:
        // - owner (ADMIN, from db.organizations.projects.create)
        // - projectAdmin (ADMIN)
        // - projectDeveloper (DEVELOPER)
        // - projectViewer (VIEWER)
        // - projectAnnotator (ANNOTATOR)
        expect(memberships).toHaveLength(5);
        expect(memberships.map((m) => m.role).sort()).toEqual([
          "ADMIN",
          "ADMIN",
          "ANNOTATOR",
          "DEVELOPER",
          "VIEWER",
        ]);
      }),
    );

    it.effect(
      "returns `NotFoundError` when org member has no project access",
      () =>
        Effect.gen(function* () {
          const { project, org, member } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .findAll({
              userId: member.id,
              organizationId: org.id,
              projectId: project.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Project not found");
        }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all project memberships");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.findById -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists: exists
            .select([{ id: "project-id" }])
            // findAll: fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `DatabaseError` when membership lookup fails during authorization",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .findAll({
              userId: "member-id",
              organizationId: "org-id",
              projectId: "project-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to get project membership");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize -> getRole -> organizationMemberships.findById (MEMBER role)
              .select([
                {
                  role: "MEMBER",
                  organizationId: "org-id",
                  memberId: "member-id",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "MEMBER",
                  organizationId: "org-id",
                  memberId: "member-id",
                  createdAt: new Date(),
                },
              ])
              // getMembership: DB query fails (covers lines 255-258)
              .select(new Error("Database connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when project verification fails during authorization",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .findAll({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to verify project");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // authorize -> getRole -> organizationMemberships.findById (OWNER role)
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // verifyProjectExists: DB query fails (covers lines 359-362)
              .select(new Error("Database connection failed"))
              .build(),
          ),
        ),
    );
  });

  // ===========================================================================
  // findById
  // ===========================================================================

  describe("findById", () => {
    it.effect("retrieves a specific membership", () =>
      Effect.gen(function* () {
        const { project, org, owner, projectDeveloper } =
          yield* TestProjectFixture;
        const db = yield* Database;

        const membership = yield* db.organizations.projects.memberships.findById({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          memberId: projectDeveloper.id,
        });

        expect(membership.role).toBe("DEVELOPER");
      }),
    );

    it.effect("returns `NotFoundError` when membership doesn't exist", () =>
      Effect.gen(function* () {
        const { project, org, owner, member } = yield* TestProjectFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            memberId: member.id, // org member, but not a project member
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `Membership for member ${member.id} not found`,
        );
      }),
    );

    it.effect("returns `NotFoundError` when user has no project access", () =>
      Effect.gen(function* () {
        const { project, org, member, projectDeveloper } =
          yield* TestProjectFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .findById({
            userId: member.id, // no project access
            organizationId: org.id,
            projectId: project.id,
            memberId: projectDeveloper.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            memberId: "target-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find project membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.findById -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // organizationMemberships.findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists: exists
            .select([{ id: "project-id" }])
            // findById: fails
            .select(new Error("Database connection failed"))
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
        const { project, org, owner, projectDeveloper } =
          yield* TestProjectFixture;
        const db = yield* Database;

        const updated = yield* db.organizations.projects.memberships.update({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          memberId: projectDeveloper.id,
          data: { role: "ANNOTATOR" },
        });

        expect(updated.role).toBe("ANNOTATOR");

        const audits = yield* db.organizations.projects.memberships.audits.findAll({
          projectId: project.id,
          memberId: projectDeveloper.id,
        });
        const changes = audits.filter((a) => a.action === "CHANGE");
        expect(changes).toHaveLength(1);
        expect(changes[0]).toMatchObject({
          actorId: owner.id,
          targetId: projectDeveloper.id,
          action: "CHANGE",
          previousRole: "DEVELOPER",
          newRole: "ANNOTATOR",
        } satisfies Partial<PublicProjectMembershipAudit>);
      }),
    );

    it.effect("allows ADMIN to modify their own membership", () =>
      Effect.gen(function* () {
        const { project, org, projectAdmin } = yield* TestProjectFixture;
        const db = yield* Database;

        const updated = yield* db.organizations.projects.memberships.update({
          userId: projectAdmin.id,
          organizationId: org.id,
          projectId: project.id,
          memberId: projectAdmin.id,
          data: { role: "DEVELOPER" },
        });

        expect(updated.role).toBe("DEVELOPER");
        expect(updated.memberId).toBe(projectAdmin.id);
      }),
    );

    it.effect(
      "allows org ADMIN (implicit project ADMIN) to add and modify their own project membership",
      () =>
        Effect.gen(function* () {
          const { project, org, admin } = yield* TestProjectFixture;
          const db = yield* Database;

          // Admin is not an explicit project member, but has implicit ADMIN access
          // Add themselves as a DEVELOPER
          const created = yield* db.organizations.projects.memberships.create({
            userId: admin.id,
            organizationId: org.id,
            projectId: project.id,
            data: { memberId: admin.id, role: "DEVELOPER" },
          });

          expect(created.role).toBe("DEVELOPER");
          expect(created.memberId).toBe(admin.id);

          // Now modify their own membership to VIEWER
          const updated = yield* db.organizations.projects.memberships.update({
            userId: admin.id,
            organizationId: org.id,
            projectId: project.id,
            memberId: admin.id,
            data: { role: "VIEWER" },
          });

          expect(updated.role).toBe("VIEWER");
          expect(updated.memberId).toBe(admin.id);
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when non-ADMIN tries to modify their own membership",
      () =>
        Effect.gen(function* () {
          const { project, org, projectDeveloper } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .update({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              memberId: projectDeveloper.id,
              data: { role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this project membership",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when actor is not ADMIN (read-only role)",
      () =>
        Effect.gen(function* () {
          const { project, org, projectDeveloper, projectViewer } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .update({
              userId: projectDeveloper.id, // read-only role
              organizationId: org.id,
              projectId: project.id,
              memberId: projectViewer.id,
              data: { role: "ANNOTATOR" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this project membership",
          );
        }),
    );

    it.effect(
      "returns `NotFoundError` when target is not a project member",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, member } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .update({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              memberId: member.id, // org member, no project membership
              data: { role: "VIEWER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("User is not a member of this project");
        }),
    );

    it.effect("returns `DatabaseError` when transaction fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            memberId: "target-id",
            data: { role: "ANNOTATOR" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update project membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize(update) -> getRole -> organizationMemberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists: exists
            .select([{ id: "project-id" }])
            // getMembership(existing): returns DEVELOPER
            .select([{ role: "DEVELOPER" }])
            // transaction update fails
            .update(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit log insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            memberId: "target-id",
            data: { role: "ANNOTATOR" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize(update) -> getRole -> organizationMemberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists: exists
            .select([{ id: "project-id" }])
            // getMembership(existing): returns DEVELOPER
            .select([{ role: "DEVELOPER" }])
            // transaction update succeeds
            .update([
              {
                projectId: "project-id",
                memberId: "target-id",
                role: "ANNOTATOR",
                createdAt: new Date(),
              },
            ])
            // audit log insert fails
            .insert(new Error("Audit log insert failed"))
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
        const { project, org, owner, projectDeveloper } =
          yield* TestProjectFixture;
        const db = yield* Database;

        yield* db.organizations.projects.memberships.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          memberId: projectDeveloper.id,
        });

        const audits = yield* db.organizations.projects.memberships.audits.findAll({
          projectId: project.id,
          memberId: projectDeveloper.id,
        });
        const revokes = audits.filter((a) => a.action === "REVOKE");
        expect(revokes).toHaveLength(1);
        expect(revokes[0]).toMatchObject({
          actorId: owner.id,
          targetId: projectDeveloper.id,
          action: "REVOKE",
          previousRole: "DEVELOPER",
          newRole: null,
        } satisfies Partial<PublicProjectMembershipAudit>);
      }),
    );

    it.effect("allows ADMIN to remove themselves from a project", () =>
      Effect.gen(function* () {
        const { project, org, projectAdmin } = yield* TestProjectFixture;
        const db = yield* Database;

        yield* db.organizations.projects.memberships.delete({
          userId: projectAdmin.id,
          organizationId: org.id,
          projectId: project.id,
          memberId: projectAdmin.id,
        });

        const audits = yield* db.organizations.projects.memberships.audits.findAll({
          projectId: project.id,
          memberId: projectAdmin.id,
        });
        const revokes = audits.filter((a) => a.action === "REVOKE");
        expect(revokes).toHaveLength(1);
        expect(revokes[0]).toMatchObject({
          actorId: projectAdmin.id,
          targetId: projectAdmin.id,
          action: "REVOKE",
          previousRole: "ADMIN",
          newRole: null,
        } satisfies Partial<PublicProjectMembershipAudit>);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when actor is not ADMIN (read-only role)",
      () =>
        Effect.gen(function* () {
          const { project, org, projectDeveloper, projectViewer } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .delete({
              userId: projectDeveloper.id, // read-only role
              organizationId: org.id,
              projectId: project.id,
              memberId: projectViewer.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this project membership",
          );
        }),
    );

    it.effect(
      "returns `NotFoundError` when target is not a project member",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, member } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.memberships
            .delete({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              memberId: member.id, // org member, no project membership
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("User is not a member of this project");
        }),
    );

    it.effect("returns `DatabaseError` when transaction fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            memberId: "target-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete project membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize(delete) -> getRole -> organizationMemberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists: exists
            .select([{ id: "project-id" }])
            // getMembership(existing): returns DEVELOPER
            .select([{ role: "DEVELOPER" }])
            // transaction delete fails
            .delete(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit log insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            memberId: "target-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize(delete) -> getRole -> organizationMemberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // verifyProjectExists: exists
            .select([{ id: "project-id" }])
            // getMembership(existing): returns DEVELOPER
            .select([{ role: "DEVELOPER" }])
            // transaction delete succeeds
            .delete([])
            // audit log insert fails
            .insert(new Error("Audit log insert failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // audits
  // ===========================================================================

  describe("audits", () => {
    it.effect("findAll retrieves all audit entries for a member", () =>
      Effect.gen(function* () {
        const { project, org, owner, projectDeveloper } =
          yield* TestProjectFixture;
        const db = yield* Database;

        // Perform an update to create a CHANGE audit entry
        yield* db.organizations.projects.memberships.update({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          memberId: projectDeveloper.id,
          data: { role: "ANNOTATOR" },
        });

        const audits = yield* db.organizations.projects.memberships.audits.findAll({
          projectId: project.id,
          memberId: projectDeveloper.id,
        });

        // Should have GRANT (from fixture) + CHANGE (from update)
        expect(audits.length).toBeGreaterThanOrEqual(2);

        const grant = audits.find((a) => a.action === "GRANT");
        const change = audits.find((a) => a.action === "CHANGE");

        expect(grant).toBeDefined();
        expect(change).toBeDefined();
        expect(change).toMatchObject({
          actorId: owner.id,
          targetId: projectDeveloper.id,
          action: "CHANGE",
          previousRole: "DEVELOPER",
          newRole: "ANNOTATOR",
        });
      }),
    );

    it.effect("returns `DatabaseError` when findAll query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.memberships.audits
          .findAll({
            projectId: "project-id",
            memberId: "member-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find audit entries");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });
});
