import {
  describe,
  it,
  expect,
  MockDrizzleORM,
  TestOrganizationFixture,
} from "@/tests/db";
import { Effect } from "effect";
import { Database } from "@/db/database";
import {
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import type { PublicProject } from "@/db/schema";

describe("Projects", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates a project (org OWNER) and adds creator as ADMIN", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const project = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "New Project" },
        });

        expect(project).toMatchObject({
          name: "New Project",
          organizationId: org.id,
          createdByUserId: owner.id,
        } satisfies Partial<PublicProject>);

        // Verify creator was added as project ADMIN
        const membership =
          yield* db.organizations.projects.memberships.findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            memberId: owner.id,
          });
        expect(membership.role).toBe("ADMIN");

        // Verify audit log was created
        const audits =
          yield* db.organizations.projects.memberships.audits.findAll({
            projectId: project.id,
            memberId: owner.id,
          });
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

    it.effect("creates a project (org ADMIN)", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const project = yield* db.organizations.projects.create({
          userId: admin.id,
          organizationId: org.id,
          data: { name: "Admin Created Project" },
        });

        expect(project.name).toBe("Admin Created Project");
        expect(project.createdByUserId).toBe(admin.id);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when org MEMBER tries to create",
      () =>
        Effect.gen(function* () {
          const { org, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects
            .create({
              userId: member.id,
              organizationId: org.id,
              data: { name: "Unauthorized Project" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to create projects in this organization",
          );
        }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to create (hides org)",
      () =>
        Effect.gen(function* () {
          const { org, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects
            .create({
              userId: nonMember.id,
              organizationId: org.id,
              data: { name: "Unauthorized Project" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Organization not found");
        }),
    );

    it.effect("returns `DatabaseError` when project insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { name: "Test Project" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create project");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.findById (authorize + actual)
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
            // project insert fails
            .insert(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("allows multiple projects with the same name", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Create two projects with the same name
        const project1 = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Duplicate Name" },
        });

        const project2 = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Duplicate Name" },
        });

        // Both should succeed with different IDs
        expect(project1.name).toBe("Duplicate Name");
        expect(project2.name).toBe("Duplicate Name");
        expect(project1.id).not.toBe(project2.id);

        // Both should appear in findAll
        const allProjects = yield* db.organizations.projects.findAll({
          userId: owner.id,
          organizationId: org.id,
        });
        const duplicateNameProjects = allProjects.filter(
          (p) => p.name === "Duplicate Name",
        );
        expect(duplicateNameProjects).toHaveLength(2);
      }),
    );
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("org OWNER sees all projects in the organization", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Create projects
        yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Project 1" },
        });
        yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Project 2" },
        });

        // Owner sees all projects
        const ownerProjects = yield* db.organizations.projects.findAll({
          userId: owner.id,
          organizationId: org.id,
        });
        expect(ownerProjects).toHaveLength(2);

        // Member sees none (no project membership)
        const memberProjects = yield* db.organizations.projects.findAll({
          userId: member.id,
          organizationId: org.id,
        });
        expect(memberProjects).toHaveLength(0);
      }),
    );

    it.effect("org MEMBER only sees projects they are members of", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Create projects
        const project1 = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Project 1" },
        });
        yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Project 2" },
        });

        // Add member to project1 only
        yield* db.organizations.projects.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project1.id,
          data: { memberId: member.id, role: "DEVELOPER" },
        });

        // Member only sees project1
        const memberProjects = yield* db.organizations.projects.findAll({
          userId: member.id,
          organizationId: org.id,
        });
        expect(memberProjects).toHaveLength(1);
        expect(memberProjects[0].id).toBe(project1.id);
      }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to list (hides org)",
      () =>
        Effect.gen(function* () {
          const { org, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects
            .findAll({
              userId: nonMember.id,
              organizationId: org.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns `DatabaseError` when query fails (org privileged)", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all projects");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.findById (authorize + actual)
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
            // findAll query fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when query fails (org member)", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .findAll({
            userId: "member-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all projects");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // organizationMemberships.findById (authorize + actual)
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
            // findAll query fails (member path)
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
    it.effect("retrieves a project by ID", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Test Project" },
        });

        const project = yield* db.organizations.projects.findById({
          userId: owner.id,
          organizationId: org.id,
          projectId: created.id,
        });

        expect(project.id).toBe(created.id);
        expect(project.name).toBe("Test Project");
      }),
    );

    it.effect("returns `NotFoundError` when project doesn't exist", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }),
    );

    it.effect("returns `NotFoundError` when user has no access", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Test Project" },
        });

        const result = yield* db.organizations.projects
          .findById({
            userId: member.id,
            organizationId: org.id,
            projectId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find project");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projects.getRole -> projectMemberships.findById authorization
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
            // verifyProjectExists
            .select([{ id: "project-id" }])
            // projectMemberships.findById actual query
            .select([
              {
                role: "ADMIN",
                projectId: "project-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projects.findById query fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `NotFoundError` when findById returns empty (defensive)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects
            .findById({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "Project with projectId project-id not found",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // projects.getRole -> projectMemberships.findById authorization
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
              // verifyProjectExists
              .select([{ id: "project-id" }])
              // projectMemberships.findById actual query
              .select([
                {
                  role: "ADMIN",
                  projectId: "project-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // projects.findById returns empty array (defensive case)
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
    it.effect("updates a project name", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Original Name" },
        });

        const updated = yield* db.organizations.projects.update({
          userId: owner.id,
          organizationId: org.id,
          projectId: created.id,
          data: { name: "Updated Name" },
        });

        expect(updated.name).toBe("Updated Name");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when DEVELOPER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "Test Project" },
          });

          // Add member as DEVELOPER
          yield* db.organizations.projects.memberships.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: created.id,
            data: { memberId: member.id, role: "DEVELOPER" },
          });

          const result = yield* db.organizations.projects
            .update({
              userId: member.id,
              organizationId: org.id,
              projectId: created.id,
              data: { name: "Updated" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this project",
          );
        }),
    );

    it.effect("returns `NotFoundError` when project doesn't exist", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: "00000000-0000-0000-0000-000000000000",
            data: { name: "Updated" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns `DatabaseError` when update fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            data: { name: "Updated" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update project");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projects.getRole -> projectMemberships.findById authorization
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
            // verifyProjectExists
            .select([{ id: "project-id" }])
            // projectMemberships.findById actual query
            .select([
              {
                role: "ADMIN",
                projectId: "project-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // update fails
            .update(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `NotFoundError` when update returns empty (defensive)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              data: { name: "Updated" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "Project with projectId project-id not found",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // projects.getRole -> projectMemberships.findById authorization
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
              // verifyProjectExists
              .select([{ id: "project-id" }])
              // projectMemberships.findById actual query
              .select([
                {
                  role: "ADMIN",
                  projectId: "project-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // update returns empty array (defensive case)
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
    it.effect("deletes a project", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Test Project" },
        });

        yield* db.organizations.projects.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: created.id,
        });

        // Verify project is deleted
        const result = yield* db.organizations.projects
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when DEVELOPER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "Test Project" },
          });

          // Add member as DEVELOPER
          yield* db.organizations.projects.memberships.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: created.id,
            data: { memberId: member.id, role: "DEVELOPER" },
          });

          const result = yield* db.organizations.projects
            .delete({
              userId: member.id,
              organizationId: org.id,
              projectId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this project",
          );
        }),
    );

    it.effect("returns `NotFoundError` when project doesn't exist", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .delete({
            userId: owner.id,
            organizationId: org.id,
            projectId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete project");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projects.getRole -> projectMemberships.findById authorization
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
            // verifyProjectExists
            .select([{ id: "project-id" }])
            // projectMemberships.findById actual query
            .select([
              {
                role: "ADMIN",
                projectId: "project-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // delete fails
            .delete(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `NotFoundError` when delete returns empty (defensive)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects
            .delete({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "Project with projectId project-id not found",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // projects.getRole -> projectMemberships.findById authorization
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
              // verifyProjectExists
              .select([{ id: "project-id" }])
              // projectMemberships.findById actual query
              .select([
                {
                  role: "ADMIN",
                  projectId: "project-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // delete returns empty array (defensive case)
              .delete([])
              .build(),
          ),
        ),
    );
  });

  // ===========================================================================
  // getRole (delegation to memberships)
  // ===========================================================================

  describe("getRole", () => {
    it.effect("delegates to memberships.getRole", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Test Project" },
        });

        // getRole should work (owner has implicit ADMIN)
        const role = yield* db.organizations.projects.getRole({
          userId: owner.id,
          organizationId: org.id,
          projectId: created.id,
        });

        expect(role).toBe("ADMIN");
      }),
    );
  });
});
