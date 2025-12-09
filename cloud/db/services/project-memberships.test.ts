import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";
import { DatabaseService } from "@/db/services";
import { MockDatabase, TestDatabase, TestProjectFixture } from "@/tests/db";
import type {
  PublicProjectMembership,
  PublicProjectMembershipAudit,
} from "@/db/schema";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";

describe("ProjectMembershipService", () => {
  // ===========================================================================
  // getRole
  // ===========================================================================

  describe("getRole", () => {
    it.effect("returns ADMIN for org OWNER (implicit project admin)", () =>
      Effect.gen(function* () {
        const { project, org, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        expect(
          yield* db.organizations.projects.memberships.getRole({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
          }),
        ).toBe("ADMIN");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns ADMIN for org ADMIN (implicit project admin)", () =>
      Effect.gen(function* () {
        const { project, org, admin } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        expect(
          yield* db.organizations.projects.memberships.getRole({
            userId: admin.id,
            organizationId: org.id,
            projectId: project.id,
          }),
        ).toBe("ADMIN");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns explicit project membership role", () =>
      Effect.gen(function* () {
        const { project, org, projectDeveloper } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        expect(
          yield* db.organizations.projects.memberships.getRole({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
          }),
        ).toBe("DEVELOPER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when project does not exist (implicit access path)",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations.projects.memberships
            .getRole({
              userId: owner.id,
              organizationId: org.id,
              projectId: "00000000-0000-0000-0000-000000000000",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Project not found");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when org member has no project access",
      () =>
        Effect.gen(function* () {
          const { project, org, member } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations.projects.memberships
            .getRole({
              userId: member.id,
              organizationId: org.id,
              projectId: project.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Project not found");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when membership lookup fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // organizations.getRole: org membership lookup returns empty → NotFoundError (caught)
          .select([])
          // project membership lookup: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations.projects.memberships
          .getRole({
            userId: "user-id",
            organizationId: "org-id",
            projectId: "project-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get project membership");
      }),
    );

    it.effect(
      "returns `DatabaseError` when verifyProjectExists fails (implicit access path)",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // organizations.getRole: membership role resolves to OWNER
            .select([{ role: "OWNER" }])
            // verifyProjectExists: fails
            .select(new Error("Database connection failed"))
            .build();

          const result = yield* db.organizations.projects.memberships
            .getRole({
              userId: "user-id",
              organizationId: "org-id",
              projectId: "project-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to verify project");
        }),
    );
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("retrieves all memberships for a project", () =>
      Effect.gen(function* () {
        const { project, org, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const memberships =
          yield* db.organizations.projects.memberships.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
          });

        // Fixture creates 4 explicit project members + the creator (auto project ADMIN)
        expect(memberships).toHaveLength(5);
        expect(memberships.map((m) => m.role).sort()).toEqual([
          "ADMIN",
          "ADMIN",
          "ANNOTATOR",
          "DEVELOPER",
          "VIEWER",
        ]);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when org member has no project access",
      () =>
        Effect.gen(function* () {
          const { project, org, member } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.organizations.projects.memberships
            .findAll({
              userId: member.id,
              organizationId: org.id,
              projectId: project.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Project not found");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // organizations.getRole: OWNER
          .select([{ role: "OWNER" }])
          // verifyProjectExists: exists
          .select([{ id: "project-id" }])
          // baseService.findAll: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.organizations.projects.memberships
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all project memberships");
      }),
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
        const db = yield* DatabaseService;

        const membership =
          yield* db.organizations.projects.memberships.findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            memberId: projectDeveloper.id,
          });

        expect(membership.role).toBe("DEVELOPER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when membership doesn't exist", () =>
      Effect.gen(function* () {
        const { project, org, owner, member } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

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
          `project membership with memberId ${member.id} not found`,
        );
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user has no project access", () =>
      Effect.gen(function* () {
        const { project, org, member, projectDeveloper } =
          yield* TestProjectFixture;
        const db = yield* DatabaseService;

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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // organizations.getRole: OWNER
          .select([{ role: "OWNER" }])
          // verifyProjectExists: exists
          .select([{ id: "project-id" }])
          // baseService.findById: fails
          .select(new Error("Database connection failed"))
          .build();

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
      }),
    );
  });

  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect(
      "creates a project membership (ADMIN actor) and writes audit",
      () =>
        Effect.gen(function* () {
          const { project, org, owner } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

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

          const membership =
            yield* db.organizations.projects.memberships.create({
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

          const audits =
            yield* db.organizations.projects.memberships.audits.findAll({
              organizationId: org.id,
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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when target is not an org member (TODO external collaborators)",
      () =>
        Effect.gen(function* () {
          const { project, org, owner } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when actor is not ADMIN (read-only role)",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, projectDeveloper } =
            yield* TestProjectFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `AlreadyExistsError` when user is already a member",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, projectDeveloper } =
            yield* TestProjectFixture;
          const db = yield* DatabaseService;

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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when project does not exist", () =>
      Effect.gen(function* () {
        const { org, owner, projectDeveloper } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.organizations.projects.memberships
          .create({
            userId: owner.id,
            organizationId: org.id,
            projectId: "00000000-0000-0000-0000-000000000000",
            data: { memberId: projectDeveloper.id, role: "VIEWER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // authorize(create): organizations.getRole => OWNER
          .select([{ role: "OWNER" }])
          // verifyProjectExists: exists
          .select([{ id: "project-id" }])
          // target org membership exists (organizations.memberships.getMembership)
          .select([{ role: "MEMBER" }])
          // transaction insert fails
          .insert(new Error("Database connection failed"))
          .build();

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
      }),
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
        const db = yield* DatabaseService;

        const updated = yield* db.projects.memberships.update({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          memberId: projectDeveloper.id,
          data: { role: "ANNOTATOR" },
        });

        expect(updated.role).toBe("ANNOTATOR");

        const audits = yield* db.projects.memberships.audits.findAll({
          organizationId: org.id,
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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to modify your own membership",
      () =>
        Effect.gen(function* () {
          const { project, org, projectAdmin } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.projects.memberships
            .update({
              userId: projectAdmin.id,
              organizationId: org.id,
              projectId: project.id,
              memberId: projectAdmin.id,
              data: { role: "DEVELOPER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot modify your own membership");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when actor is not ADMIN (read-only role)",
      () =>
        Effect.gen(function* () {
          const { project, org, projectDeveloper, projectViewer } =
            yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.projects.memberships
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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when target is not a project member",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, member } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.projects.memberships
            .update({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              memberId: member.id, // org member, no project membership
              data: { role: "VIEWER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            `User with id ${member.id} is not a member of this project`,
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when transaction fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // authorize(update): organizations.getRole => OWNER
          .select([{ role: "OWNER" }])
          // verifyProjectExists: exists
          .select([{ id: "project-id" }])
          // getMembership(existing): returns DEVELOPER
          .select([{ role: "DEVELOPER" }])
          // transaction update fails
          .update(new Error("Database connection failed"))
          .build();

        const result = yield* db.projects.memberships
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
      }),
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
        const db = yield* DatabaseService;

        yield* db.projects.memberships.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          memberId: projectDeveloper.id,
        });

        const audits = yield* db.projects.memberships.audits.findAll({
          organizationId: org.id,
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
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when trying to remove yourself",
      () =>
        Effect.gen(function* () {
          const { project, org, projectAdmin } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.projects.memberships
            .delete({
              userId: projectAdmin.id,
              organizationId: org.id,
              projectId: project.id,
              memberId: projectAdmin.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot remove yourself from a project");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when actor is not ADMIN (read-only role)",
      () =>
        Effect.gen(function* () {
          const { project, org, projectDeveloper, projectViewer } =
            yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.projects.memberships
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
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when target is not a project member",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, member } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.projects.memberships
            .delete({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              memberId: member.id, // org member, no project membership
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            `User with id ${member.id} is not a member of this project`,
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when transaction fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // authorize(delete): organizations.getRole => OWNER
          .select([{ role: "OWNER" }])
          // verifyProjectExists: exists
          .select([{ id: "project-id" }])
          // getMembership(existing): returns DEVELOPER
          .select([{ role: "DEVELOPER" }])
          // transaction delete fails
          .delete(new Error("Database connection failed"))
          .build();

        const result = yield* db.projects.memberships
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            memberId: "target-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete project membership");
      }),
    );
  });

  // ===========================================================================
  // audits
  // ===========================================================================

  describe("audits", () => {
    it.effect("findById retrieves a specific audit entry", () =>
      Effect.gen(function* () {
        const { project, org, owner, projectDeveloper } =
          yield* TestProjectFixture;
        const db = yield* DatabaseService;

        // Trigger a CHANGE audit entry
        yield* db.projects.memberships.update({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          memberId: projectDeveloper.id,
          data: { role: "ANNOTATOR" },
        });

        const audits = yield* db.projects.memberships.audits.findAll({
          organizationId: org.id,
          projectId: project.id,
          memberId: projectDeveloper.id,
        });
        const change = audits.find((a) => a.action === "CHANGE");
        expect(change).toBeDefined();

        const byId = yield* db.projects.memberships.audits.findById({
          organizationId: org.id,
          projectId: project.id,
          memberId: projectDeveloper.id,
          id: change!.id,
        });

        expect(byId.id).toBe(change!.id);
        expect(byId.action).toBe("CHANGE");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("findById returns `NotFoundError` when audit doesn't exist", () =>
      Effect.gen(function* () {
        const { project, org, projectDeveloper } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const missingId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.projects.memberships.audits
          .findById({
            organizationId: org.id,
            projectId: project.id,
            memberId: projectDeveloper.id,
            id: missingId,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          `project membership audit with id ${missingId} not found`,
        );
      }).pipe(Effect.provide(TestDatabase)),
    );
  });
});
