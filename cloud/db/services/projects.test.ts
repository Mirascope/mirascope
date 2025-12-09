import { describe, it, expect } from "@effect/vitest";
import {
  TestDatabase,
  TestOrganizationFixture,
  TestProjectFixture,
  MockDatabase,
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
    it.effect("creates an organization-owned project", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const project = yield* db.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "My Project" },
        });

        expect(project.id).toBeDefined();
        expect(project.name).toBe("My Project");
        expect(project.organizationId).toBe(org.id);
        expect(project.createdByUserId).toBe(owner.id);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("adds creator to project_memberships as ADMIN", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const project = yield* db.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Owned Project" },
        });

        expect(
          yield* db.projects.getRole({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
          }),
        ).toBe("ADMIN");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when org member lacks create permission",
      () =>
        Effect.gen(function* () {
          const { org, member } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const result = yield* db.projects
            .create({
              userId: member.id,
              organizationId: org.id,
              data: { name: "Should Fail" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to create projects in this organization",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not an org member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const result = yield* db.projects
          .create({
            userId: nonMember.id,
            organizationId: org.id,
            data: { name: "Should Fail" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `AlreadyExistsError` when a unique constraint is violated",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // org role resolves to OWNER
            .select([{ role: "OWNER" }])
            .build();

          // Simulate a PostgreSQL unique constraint violation inside the transaction.
          // (The real DB schema may not currently enforce uniqueness on project names.)
          const uniqueErr = Object.assign(new Error("unique_violation"), {
            code: "23505",
          });
          // Provide a typed `transaction` method on the mock client so ProjectService.create()
          // can catch and map the unique violation.
          const client = db.client as unknown as {
            transaction: () => Promise<never>;
          };
          client.transaction = () => Promise.reject(uniqueErr);

          const result = yield* db.projects
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { name: "Dup" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "A project with this name already exists",
          );
        }),
    );

    it.effect("returns `DatabaseError` when transaction fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // org role resolves to OWNER
          .select([{ role: "OWNER" }])
          .build();

        const result = yield* db.projects
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { name: "X" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create project");
      }),
    );
  });

  describe("getRole", () => {
    it.effect("treats org ADMIN as project ADMIN (implicit access)", () =>
      Effect.gen(function* () {
        const { org, owner, admin } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const project = yield* db.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Admin Access Project" },
        });

        expect(
          yield* db.projects.getRole({
            userId: admin.id,
            organizationId: org.id,
            projectId: project.id,
          }),
        ).toBe("ADMIN");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `NotFoundError` when org member is not a project member",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const project = yield* db.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "Restricted Project" },
          });

          const result = yield* db.projects
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
  });

  describe("findAll", () => {
    it.effect("returns all org projects for OWNER", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const p1 = yield* db.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "P1" },
        });
        const p2 = yield* db.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "P2" },
        });

        const projects = yield* db.projects.findAll({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(projects.map((p) => p.id).sort()).toEqual([p1.id, p2.id].sort());
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns empty array for DEVELOPER without project membership",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          yield* db.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "Hidden" },
          });

          const projects = yield* db.projects.findAll({
            userId: member.id,
            organizationId: org.id,
          });

          expect(projects).toEqual([]);
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // org role resolves to OWNER
          .select([{ role: "OWNER" }])
          // projects select fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.projects
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all projects");
      }),
    );

    it.effect("returns `DatabaseError` when non-privileged query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // org role resolves to MEMBER (not privileged)
          .select([{ role: "MEMBER" }])
          // join query fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.projects
          .findAll({
            userId: "member-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all projects");
      }),
    );
  });

  describe("findById", () => {
    it.effect("returns project when user has explicit project membership", () =>
      Effect.gen(function* () {
        const { project, org, projectViewer } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        // projectViewer is an explicit project member via the fixture
        const found = yield* db.projects.findById({
          userId: projectViewer.id,
          organizationId: org.id,
          projectId: project.id,
        });

        expect(found.id).toBe(project.id);
        expect(found.organizationId).toBe(org.id);
      }).pipe(Effect.provide(TestDatabase)),
    );
  });

  describe("memberships", () => {
    it.effect("adds a member via memberships.create and grants access", () =>
      Effect.gen(function* () {
        const { project, org, owner, member } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        yield* db.projects.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { memberId: member.id, role: "DEVELOPER" },
        });

        expect(
          yield* db.projects.getRole({
            userId: member.id,
            organizationId: org.id,
            projectId: project.id,
          }),
        ).toBe("DEVELOPER");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `AlreadyExistsError` when adding an existing member",
      () =>
        Effect.gen(function* () {
          const { project, org, owner, projectDeveloper } =
            yield* TestProjectFixture;
          const db = yield* DatabaseService;

          // projectDeveloper is already a project member
          const result = yield* db.projects.memberships
            .create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              data: { memberId: projectDeveloper.id, role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "User is already a member of this project",
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "prevents removing the project OWNER via memberships.delete",
      () =>
        Effect.gen(function* () {
          const { project, org, owner } = yield* TestProjectFixture;
          const db = yield* DatabaseService;

          // Cannot remove yourself (which is the owner)
          const result = yield* db.projects.memberships
            .delete({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              memberId: owner.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot remove yourself from a project");
        }).pipe(Effect.provide(TestDatabase)),
    );
  });

  describe("findById / update / delete", () => {
    it.effect(
      "returns `NotFoundError` for org member without project membership",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* DatabaseService;

          const project = yield* db.projects.create({
            userId: owner.id,
            organizationId: org.id,
            data: { name: "Private" },
          });

          const result = yield* db.projects
            .findById({
              userId: member.id,
              organizationId: org.id,
              projectId: project.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Project not found");
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("updates when ADMIN is a project member", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const project = yield* db.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Updatable" },
        });

        yield* db.projects.memberships.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { memberId: member.id, role: "ADMIN" },
        });

        const updated = yield* db.projects.update({
          userId: member.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Updated" },
        });

        expect(updated.name).toBe("Updated");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("deletes when org ADMIN performs the action", () =>
      Effect.gen(function* () {
        const { org, owner, admin } = yield* TestOrganizationFixture;
        const db = yield* DatabaseService;

        const project = yield* db.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Deletable" },
        });

        yield* db.projects.delete({
          userId: admin.id,
          organizationId: org.id,
          projectId: project.id,
        });

        const result = yield* db.projects
          .findById({
            userId: admin.id,
            organizationId: org.id,
            projectId: project.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );
  });
});
