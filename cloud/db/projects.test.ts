import { eq } from "drizzle-orm";
import { Effect, Layer } from "effect";

import type { PublicProject } from "@/db/schema";

import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { projects } from "@/db/schema";
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
          data: { name: "New Project", slug: "new-project" },
        });

        expect(project).toMatchObject({
          name: "New Project",
          slug: "new-project",
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
          data: {
            name: "Admin Created Project",
            slug: "admin-created-project",
          },
        });

        expect(project.name).toBe("Admin Created Project");
        expect(project.slug).toBe("admin-created-project");
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
              data: {
                name: "Unauthorized Project",
                slug: "unauthorized-project",
              },
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
              data: {
                name: "Unauthorized Project",
                slug: "unauthorized-project-2",
              },
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
            data: { name: "Test Project", slug: "test-project" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create project");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize: getRole
            .select([{ role: "OWNER" }])
            // findById: get membership
            .select([
              { memberId: "owner-id", role: "OWNER", createdAt: new Date() },
            ])
            // checkProjectLimit: getPlan -> fetch organization
            .select([{ stripeCustomerId: "cus_test" }])
            // checkProjectLimit: count projects (under limit)
            .select([{ count: 0 }])
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

        // Create two projects with the same name but different slugs
        const project1 = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Duplicate Name", slug: "duplicate-name-1" },
        });

        const project2 = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Duplicate Name", slug: "duplicate-name-2" },
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

    it.effect(
      "returns `AlreadyExistsError` when slug is taken in the same organization",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* Database;

          // Create first project
          yield* db.organizations.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "First Project", slug: "shared-slug" },
          });

          // Try to create second project with same slug
          const result = yield* db.organizations.projects
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { name: "Second Project", slug: "shared-slug" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "A project with this slug already exists in this organization",
          );
        }),
    );

    it.effect(
      "allows projects with the same slug across different organizations",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          // Create first organization and project
          const user1 = yield* db.users.create({
            data: { email: "user1@example.com", name: "User 1" },
          });
          const org1 = yield* db.organizations.create({
            userId: user1.id,
            data: { name: "Org 1", slug: "org-1" },
          });
          const project1 = yield* db.organizations.projects.create({
            userId: user1.id,
            organizationId: org1.id,
            data: { name: "Project", slug: "shared-slug" },
          });

          // Create second organization and project with same slug
          const user2 = yield* db.users.create({
            data: { email: "user2@example.com", name: "User 2" },
          });
          const org2 = yield* db.organizations.create({
            userId: user2.id,
            data: { name: "Org 2", slug: "org-2" },
          });
          const project2 = yield* db.organizations.projects.create({
            userId: user2.id,
            organizationId: org2.id,
            data: { name: "Project", slug: "shared-slug" },
          });

          // Both should succeed
          expect(project1.slug).toBe("shared-slug");
          expect(project2.slug).toBe("shared-slug");
          expect(project1.id).not.toBe(project2.id);
          expect(project1.organizationId).not.toBe(project2.organizationId);
        }),
    );

    it.effect("returns non-SqlError from getPlan in checkProjectLimit", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { name: "Test Project", slug: "test-project" },
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
            .select([]) // checkProjectLimit: getPlan -> org not found
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `DatabaseError` when counting projects fails in checkProjectLimit",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { name: "Test Project", slug: "test-project" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to count projects");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([{ role: "OWNER" }]) // authorize: getRole
              .select([
                { memberId: "owner-id", role: "OWNER", createdAt: new Date() },
              ]) // findById
              .select([{ stripeCustomerId: "cus_test" }]) // checkProjectLimit: getPlan
              .select(new Error("Connection failed")) // checkProjectLimit: count fails
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `PlanLimitExceededError` when project limit is exceeded",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestFreePlanOrganizationFixture;
          const db = yield* Database;

          // Create first project (FREE plan allows 1)
          yield* db.organizations.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "First Project", slug: "first-project" },
          });

          // Try to create second project - should fail
          const result = yield* db.organizations.projects
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { name: "Second Project", slug: "second-project" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PlanLimitExceededError);
          if (result instanceof PlanLimitExceededError) {
            expect(result.message).toContain("free plan limit is 1 project(s)");
            expect(result.limitType).toBe("projects");
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

    it.effect("created project has type standard by default", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;
        const client = yield* DrizzleORM;

        const project = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Test Standard Project", slug: "test-standard" },
        });

        // Verify the project has standard type
        const [dbProject] = yield* client
          .select()
          .from(projects)
          .where(eq(projects.id, project.id));
        expect(dbProject.type).toBe("standard");
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
          data: { name: "Project 1", slug: "project-1" },
        });
        yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Project 2", slug: "project-2" },
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
          data: { name: "Project 1", slug: "project-1" },
        });
        yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Project 2", slug: "project-2" },
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
          data: { name: "Test Project", slug: "test-project" },
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
          data: { name: "Test Project", slug: "test-project" },
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
          data: { name: "Original Name", slug: "original-name" },
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
            data: { name: "Test Project", slug: "test-project" },
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

    it.effect(
      "returns `AlreadyExistsError` when slug is taken in the same organization",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* Database;

          // Create first project
          yield* db.organizations.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "Existing Project", slug: "existing-project" },
          });

          // Create second project
          const project2 = yield* db.organizations.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "Second Project", slug: "second-project" },
          });

          // Try to update second project with existing slug
          const result = yield* db.organizations.projects
            .update({
              userId: owner.id,
              organizationId: org.id,
              projectId: project2.id,
              data: { slug: "existing-project" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "A project with this slug already exists in this organization",
          );
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
          data: { name: "Test Project", slug: "test-project" },
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
            data: { name: "Test Project", slug: "test-project" },
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
            // fetch project type
            .select([{ id: "project-id", type: "standard" }])
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
              // fetch project type
              .select([{ id: "project-id", type: "standard" }])
              // delete returns empty array (defensive case)
              .delete([])
              .build(),
          ),
        ),
    );

    it.effect("blocks deletion of claw_home project with active claw", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "home-project-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toBe(
          "Cannot delete a claw home project directly. Delete the claw instead.",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projects.getRole -> org membership check
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
            .select([{ id: "home-project-id" }])
            // projectMemberships.findById
            .select([
              {
                role: "ADMIN",
                projectId: "home-project-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // fetch project type - claw_home
            .select([{ id: "home-project-id", type: "claw_home" }])
            // check if claw still references this project - found one
            .select([{ id: "claw-id" }])
            .build(),
        ),
      ),
    );

    it.effect(
      "allows deletion of orphaned claw_home project (no active claw)",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          // Should succeed (no error thrown)
          yield* db.organizations.projects.delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "orphan-project-id",
          });
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // projects.getRole -> org membership check
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
              .select([{ id: "orphan-project-id" }])
              // projectMemberships.findById
              .select([
                {
                  role: "ADMIN",
                  projectId: "orphan-project-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // fetch project type - claw_home
              .select([{ id: "orphan-project-id", type: "claw_home" }])
              // check if claw references this project - none found
              .select([])
              // actual delete
              .delete([{ id: "orphan-project-id" }])
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
          data: { name: "Test Project", slug: "test-project" },
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
