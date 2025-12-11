import { describe, it, expect } from "@effect/vitest";
import {
  MockDatabase,
  TestOrganizationFixture,
  TestOrganizationProjectFixture,
  TestProjectFixture,
  TestDatabase,
} from "@/tests/db";
import { Effect } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { DatabaseService } from "@/db/services";

describe("ProjectService", () => {
  describe("create", () => {
    it.effect("creates a user-owned project", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const project = yield* db.projects.create({
          data: { name: "My Project", userOwnerId: user.id },
          userId: user.id,
        });

        expect(project).toBeDefined();
        expect(project.id).toBeDefined();
        expect(project.name).toBe("My Project");
        expect(project.userOwnerId).toBe(user.id);
        expect(project.orgOwnerId).toBeNull();
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("creates an organization-owned project", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const project = yield* db.projects.create({
          data: {
            name: "Org Project",
            orgOwnerId: org.id,
          },
          userId: owner.id,
        });

        expect(project).toBeDefined();
        expect(project.userOwnerId).toBeNull();
        expect(project.orgOwnerId).toBe(org.id);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("adds creator to project_memberships as OWNER", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        // Verify the creator can access the project (has membership)
        const role = yield* db.projects.getRole({
          id: project.id,
          userId: owner.id,
        });

        expect(role).toBe("OWNER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows same project name for different owners", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user1 = yield* db.users.create({
          email: "user1@example.com",
          name: "User 1",
        });

        const user2 = yield* db.users.create({
          email: "user2@example.com",
          name: "User 2",
        });

        const project1 = yield* db.projects.create({
          data: { name: "Same Name", userOwnerId: user1.id },
          userId: user1.id,
        });

        const project2 = yield* db.projects.create({
          data: { name: "Same Name", userOwnerId: user2.id },
          userId: user2.id,
        });

        expect(project1.name).toBe(project2.name);
        expect(project1.id).not.toBe(project2.id);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("fails with `DatabaseError` for non-existent user owner", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        // Try to create a project with a non-existent user owner
        const result = yield* db.projects
          .create({
            data: {
              name: "Test Project",
              userOwnerId: "00000000-0000-0000-0000-000000000000",
            },
            userId: user.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create project");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("fails with `DatabaseError` for non-existent org owner", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        // Try to create a project with a non-existent org owner
        const result = yield* db.projects
          .create({
            data: {
              name: "Test Project",
              orgOwnerId: "00000000-0000-0000-0000-000000000000",
            },
            userId: user.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create project");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when create fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // transaction fails
          .insert(new Error("Insert failed"))
          .build();

        const result = yield* db.projects
          .create({
            data: {
              name: "Test Project",
              userOwnerId: "user-id",
            },
            userId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create project");
      }),
    );
  });

  describe("findAll", () => {
    it.effect("retrieves all projects the user has access to", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        // Create another project
        const project2 = yield* db.projects.create({
          data: { name: "Project 2", userOwnerId: owner.id },
          userId: owner.id,
        });

        const projects = yield* db.projects.findAll({ userId: owner.id });

        expect(projects).toHaveLength(2);
        expect(projects.find((p) => p.name === project.name)).toBeDefined();
        expect(projects.find((p) => p.name === project2.name)).toBeDefined();
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns empty array when user has no projects", () =>
      Effect.gen(function* () {
        const db = yield* DatabaseService;

        const user = yield* db.users.create({
          email: "lonely@example.com",
          name: "Lonely User",
        });

        const projects = yield* db.projects.findAll({ userId: user.id });

        expect(projects).toHaveLength(0);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.projects
          .findAll({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get user projects");
      }),
    );
  });

  describe("findById", () => {
    it.effect("retrieves project when user is a member", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.projects.findById({
          id: project.id,
          userId: owner.id,
        });

        expect(result).toBeDefined();
        expect(result.id).toBe(project.id);
        expect(result.name).toBe(project.name);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when project not found", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: no membership found
          .select([])
          .build();

        const result = yield* db.projects
          .findById({ id: "nonexistent-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { project, nonMember } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.projects
          .findById({ id: project.id, userId: nonMember.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows read with ANNOTATOR role", () =>
      Effect.gen(function* () {
        const { project, annotator } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.projects.findById({
          id: project.id,
          userId: annotator.id,
        });

        expect(result).toBeDefined();
        expect(result.id).toBe(project.id);
      }).pipe(Effect.provide(TestDatabase)),
    );
  });

  describe("update", () => {
    it.effect("updates a project", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const updated = yield* db.projects.update({
          id: project.id,
          data: { name: "Updated Name" },
          userId: owner.id,
        });

        expect(updated.name).toBe("Updated Name");
        expect(updated.id).toBe(project.id);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when project not found", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.projects
          .update({ id: badId, data: { name: "New Name" }, userId: owner.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { project, nonMember } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.projects
          .update({
            id: project.id,
            data: { name: "New Name" },
            userId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when user has insufficient role",
      () =>
        Effect.gen(function* () {
          const { project, annotator } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          const result = yield* db.projects
            .update({
              id: project.id,
              data: { name: "New Name" },
              userId: annotator.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this project",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );
  });

  describe("delete", () => {
    it.effect("deletes a project", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        yield* db.projects.delete({ id: project.id, userId: owner.id });

        // Verify it's gone
        const result = yield* db.projects
          .findById({ id: project.id, userId: owner.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when project does not exist", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.projects
          .delete({ id: badId, userId: owner.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { project, nonMember } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.projects
          .delete({ id: project.id, userId: nonMember.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when user has insufficient role",
      () =>
        Effect.gen(function* () {
          const { project, admin } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          // Admin can't delete - only OWNER can
          const result = yield* db.projects
            .delete({ id: project.id, userId: admin.id })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this project",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when delete operation fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: OWNER role
          .select([{ role: "OWNER" }])
          // baseService.findById for permission check in base delete
          .select([
            {
              id: "project-id",
              name: "Test",
              userOwnerId: "user-id",
              orgOwnerId: null,
            },
          ])
          // baseService.delete: fails
          .delete(new Error("Delete failed"))
          .build();

        const result = yield* db.projects
          .delete({ id: "project-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete project");
      }),
    );
  });

  describe("findByOrganization", () => {
    it.effect("retrieves all projects owned by an organization", () =>
      Effect.gen(function* () {
        const { project, org, owner } = yield* TestOrganizationProjectFixture;
        const db = yield* DatabaseService;

        const project2 = yield* db.projects.create({
          data: {
            name: "Project 2",
            orgOwnerId: org.id,
          },
          userId: owner.id,
        });

        const projects = yield* db.projects.findByOrganization({
          organizationId: org.id,
          userId: owner.id,
        });

        expect(projects).toHaveLength(2);
        expect(projects.find((p) => p.name === project.name)).toBeDefined();
        expect(projects.find((p) => p.name === project2.name)).toBeDefined();
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns empty array when no projects for organization", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const projects = yield* db.projects.findByOrganization({
          organizationId: org.id,
          userId: owner.id,
        });

        expect(projects).toHaveLength(0);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.projects
          .findByOrganization({ organizationId: "org-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get organization projects");
      }),
    );
  });

  describe("getRole", () => {
    it.effect("returns user's role in project", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const role = yield* db.projects.getRole({
          id: project.id,
          userId: owner.id,
        });

        expect(role).toBe("OWNER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { project, nonMember } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.projects
          .getRole({ id: project.id, userId: nonMember.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.projects
          .getRole({ id: "project-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get project membership");
      }),
    );
  });

  describe("addMember", () => {
    it.effect("adds a member to a project", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        // Create a new user to add as member
        const newMember = yield* db.users.create({
          email: "newmember@example.com",
          name: "New Member",
        });

        const membership = yield* db.projects.addMember({
          id: project.id,
          memberUserId: newMember.id,
          role: "DEVELOPER",
          userId: owner.id,
        });

        expect(membership).toBeDefined();
        expect(membership.projectId).toBe(project.id);
        expect(membership.userId).toBe(newMember.id);
        expect(membership.role).toBe("DEVELOPER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows added member to access project", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const newMember = yield* db.users.create({
          email: "newmember@example.com",
          name: "New Member",
        });

        yield* db.projects.addMember({
          id: project.id,
          memberUserId: newMember.id,
          role: "ANNOTATOR",
          userId: owner.id,
        });

        // Verify the new member can access the project
        const foundProject = yield* db.projects.findById({
          id: project.id,
          userId: newMember.id,
        });

        expect(foundProject.id).toBe(project.id);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when project not found", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.projects
          .addMember({
            id: badId,
            memberUserId: owner.id,
            role: "DEVELOPER",
            userId: owner.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when caller is not a member", () =>
      Effect.gen(function* () {
        const { project, nonMember } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.projects
          .addMember({
            id: project.id,
            memberUserId: nonMember.id,
            role: "DEVELOPER",
            userId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when caller has insufficient role",
      () =>
        Effect.gen(function* () {
          const { project, developer, nonMember } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          // Developer tries to add a member (needs ADMIN or OWNER)
          const result = yield* db.projects
            .addMember({
              id: project.id,
              memberUserId: nonMember.id,
              role: "ANNOTATOR",
              userId: developer.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this project",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `AlreadyExistsError` when user is already a member",
      () =>
        Effect.gen(function* () {
          const { project, owner } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          // Try to add the owner again (they're already a member)
          const result = yield* db.projects
            .addMember({
              id: project.id,
              memberUserId: owner.id,
              role: "ADMIN",
              userId: owner.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "User is already a member of this project",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: OWNER role (has permission)
          .select([{ role: "OWNER" }])
          // insert: fails
          .insert(new Error("Insert failed"))
          .build();

        const result = yield* db.projects
          .addMember({
            id: "project-id",
            memberUserId: "new-user-id",
            role: "DEVELOPER",
            userId: "caller-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to add project member");
      }),
    );
  });

  describe("terminateMember", () => {
    it.effect("removes a member from a project", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        // Add a member first
        const member = yield* db.users.create({
          email: "member@example.com",
          name: "Member",
        });

        yield* db.projects.addMember({
          id: project.id,
          memberUserId: member.id,
          role: "DEVELOPER",
          userId: owner.id,
        });

        // Now remove them
        yield* db.projects.terminateMember({
          id: project.id,
          memberUserId: member.id,
          userId: owner.id,
        });

        // Verify they can no longer access the project
        const result = yield* db.projects
          .findById({ id: project.id, userId: member.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when project not found", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.projects
          .terminateMember({
            id: badId,
            memberUserId: owner.id,
            userId: owner.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when caller is not a member", () =>
      Effect.gen(function* () {
        const { project, nonMember } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.projects
          .terminateMember({
            id: project.id,
            memberUserId: nonMember.id,
            userId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Project not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when caller has insufficient role",
      () =>
        Effect.gen(function* () {
          const { project, developer, annotator } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          // Developer tries to remove annotator (needs ADMIN or OWNER)
          const result = yield* db.projects
            .terminateMember({
              id: project.id,
              memberUserId: annotator.id,
              userId: developer.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this project",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when user is not a member of the project",
      () =>
        Effect.gen(function* () {
          const { project, owner, nonMember } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          // Try to remove someone who isn't a member
          const result = yield* db.projects
            .terminateMember({
              id: project.id,
              memberUserId: nonMember.id,
              userId: owner.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("User is not a member of this project");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole: OWNER role (has permission)
          .select([{ role: "OWNER" }])
          // delete: fails
          .delete(new Error("Delete failed"))
          .build();

        const result = yield* db.projects
          .terminateMember({
            id: "project-id",
            memberUserId: "member-id",
            userId: "caller-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to remove project member");
      }),
    );
  });
});
