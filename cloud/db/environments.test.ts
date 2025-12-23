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
import type { PublicEnvironment } from "@/db/schema";

describe("Environments", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates an environment (org OWNER)", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const environment =
          yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "production", slug: "production" },
          });

        expect(environment).toMatchObject({
          name: "production",
          slug: "production",
          projectId: project.id,
        } satisfies Partial<PublicEnvironment>);
        expect(environment.id).toBeDefined();
      }),
    );

    it.effect("creates an environment (org ADMIN)", () =>
      Effect.gen(function* () {
        const { org, project, admin } = yield* TestProjectFixture;
        const db = yield* Database;

        const environment =
          yield* db.organizations.projects.environments.create({
            userId: admin.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "staging", slug: "staging" },
          });

        expect(environment.name).toBe("staging");
        expect(environment.slug).toBe("staging");
      }),
    );

    it.effect("creates an environment (project ADMIN)", () =>
      Effect.gen(function* () {
        const { org, project, projectAdmin } = yield* TestProjectFixture;
        const db = yield* Database;

        const environment =
          yield* db.organizations.projects.environments.create({
            userId: projectAdmin.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "dev", slug: "dev" },
          });

        expect(environment.name).toBe("dev");
      }),
    );

    it.effect("creates an environment (project DEVELOPER)", () =>
      Effect.gen(function* () {
        const { org, project, projectDeveloper } = yield* TestProjectFixture;
        const db = yield* Database;

        const environment =
          yield* db.organizations.projects.environments.create({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "testing", slug: "testing" },
          });

        expect(environment.name).toBe("testing");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project VIEWER tries to create",
      () =>
        Effect.gen(function* () {
          const { org, project, projectViewer } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments
            .create({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              data: { name: "unauthorized", slug: "unauthorized" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to create this environment",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project ANNOTATOR tries to create",
      () =>
        Effect.gen(function* () {
          const { org, project, projectAnnotator } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments
            .create({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              data: { name: "unauthorized", slug: "unauthorized" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to create (hides project)",
      () =>
        Effect.gen(function* () {
          const { org, project, nonMember } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments
            .create({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              data: { name: "unauthorized", slug: "unauthorized" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when environment name is taken in same project",
      () =>
        Effect.gen(function* () {
          const { org, project, owner } = yield* TestProjectFixture;
          const db = yield* Database;

          yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "production", slug: "production" },
          });

          const result = yield* db.organizations.projects.environments
            .create({
              userId: owner.id,
              organizationId: org.id,
              projectId: project.id,
              data: { name: "production", slug: "production" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "An environment with this slug already exists in this project",
          );
        }),
    );

    it.effect("allows same environment name in different projects", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        // Create environment in first project
        const env1 = yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "production", slug: "production" },
        });

        // Create second project
        const project2 = yield* db.organizations.projects.create({
          userId: owner.id,
          organizationId: org.id,
          data: { name: "Second Project", slug: "second-project" },
        });

        // Create environment with same name in second project
        const env2 = yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project2.id,
          data: { name: "production", slug: "production" },
        });

        expect(env1.name).toBe(env2.name);
        expect(env1.id).not.toBe(env2.id);
        expect(env1.projectId).toBe(project.id);
        expect(env2.projectId).toBe(project2.id);
      }),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            data: { name: "production", slug: "production" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create environment");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById authorization
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // projectMemberships.getRole -> getMembership (returns empty, so uses org role)
            .select([])
            // environment insert fails
            .insert(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("retrieves all environments in a project", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        // Create environments
        yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "production", slug: "production" },
        });
        yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "staging", slug: "staging" },
        });

        const environments =
          yield* db.organizations.projects.environments.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
          });

        expect(environments).toHaveLength(2);
        expect(environments.map((e) => e.name).sort()).toEqual([
          "production",
          "staging",
        ]);
      }),
    );

    it.effect("allows project VIEWER to list environments", () =>
      Effect.gen(function* () {
        const { org, project, owner, projectViewer } =
          yield* TestProjectFixture;
        const db = yield* Database;

        yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "production", slug: "production" },
        });

        const environments =
          yield* db.organizations.projects.environments.findAll({
            userId: projectViewer.id,
            organizationId: org.id,
            projectId: project.id,
          });

        expect(environments).toHaveLength(1);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ANNOTATOR tries to list",
      () =>
        Effect.gen(function* () {
          const { org, project, projectAnnotator } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments
            .findAll({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to list (hides project)",
      () =>
        Effect.gen(function* () {
          const { org, project, nonMember } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.environments
            .findAll({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns empty array when project has no environments", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const environments =
          yield* db.organizations.projects.environments.findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
          });

        expect(environments).toHaveLength(0);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find all environments");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById authorization
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // When org OWNER/ADMIN found, skips getMembership and returns ADMIN directly
            // findAll query fails
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
    it.effect("retrieves an environment by ID", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "production", slug: "production" },
        });

        const environment =
          yield* db.organizations.projects.environments.findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: created.id,
          });

        expect(environment.id).toBe(created.id);
        expect(environment.name).toBe("production");
      }),
    );

    it.effect("allows project VIEWER to get environment", () =>
      Effect.gen(function* () {
        const { org, project, owner, projectViewer } =
          yield* TestProjectFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "production", slug: "production" },
        });

        const environment =
          yield* db.organizations.projects.environments.findById({
            userId: projectViewer.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: created.id,
          });

        expect(environment.id).toBe(created.id);
      }),
    );

    it.effect("returns `NotFoundError` when environment doesn't exist", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "Environment with environmentId 00000000-0000-0000-0000-000000000000 not found",
        );
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ANNOTATOR tries to get",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, projectAnnotator } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "production", slug: "production" },
          });

          const result = yield* db.organizations.projects.environments
            .findById({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to get (hides project)",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, nonMember } = yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "production", slug: "production" },
          });

          const result = yield* db.organizations.projects.environments
            .findById({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find environment");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById authorization
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // When org OWNER/ADMIN found, skips getMembership and returns ADMIN directly
            // findById query fails
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
    it.effect("updates an environment name", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "original", slug: "original" },
        });

        const updated = yield* db.organizations.projects.environments.update({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: created.id,
          data: { name: "updated", slug: "updated" },
        });

        expect(updated.name).toBe("updated");
        expect(updated.id).toBe(created.id);
      }),
    );

    it.effect("allows project DEVELOPER to update", () =>
      Effect.gen(function* () {
        const { org, project, owner, projectDeveloper } =
          yield* TestProjectFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "original", slug: "original" },
        });

        const updated = yield* db.organizations.projects.environments.update({
          userId: projectDeveloper.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: created.id,
          data: { name: "updated-by-dev", slug: "updated-by-dev" },
        });

        expect(updated.name).toBe("updated-by-dev");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when VIEWER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, projectViewer } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "original", slug: "original" },
          });

          const result = yield* db.organizations.projects.environments
            .update({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: created.id,
              data: { name: "unauthorized", slug: "unauthorized" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this environment",
          );
        }),
    );

    it.effect("returns `NotFoundError` when environment doesn't exist", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: "00000000-0000-0000-0000-000000000000",
            data: { name: "updated", slug: "updated" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns `AlreadyExistsError` when new name conflicts", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "production", slug: "production" },
        });

        const staging = yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "staging", slug: "staging" },
        });

        const result = yield* db.organizations.projects.environments
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: staging.id,
            data: { name: "production", slug: "production" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect(result.message).toBe(
          "An environment with this slug already exists in this project",
        );
      }),
    );

    it.effect("returns `DatabaseError` when update fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
            data: { name: "updated", slug: "updated" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update environment");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById authorization
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // projectMemberships.getRole -> getMembership (returns empty, so uses org role)
            .select([])
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

          const result = yield* db.organizations.projects.environments
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
              data: { name: "updated", slug: "updated" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "Environment with environmentId env-id not found",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // projectMemberships.getRole -> organizationMemberships.findById authorization
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // projectMemberships.getRole -> organizationMemberships.findById actual query
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // projectMemberships.getRole -> verifyProjectExists
              .select([{ id: "project-id" }])
              // projectMemberships.getRole -> getMembership (returns empty, so uses org role)
              .select([])
              // update returns empty array
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
    it.effect("deletes an environment", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.environments.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "to-delete", slug: "to-delete" },
        });

        yield* db.organizations.projects.environments.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: created.id,
        });

        // Verify it's deleted
        const result = yield* db.organizations.projects.environments
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when DEVELOPER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, projectDeveloper } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "production", slug: "production" },
          });

          const result = yield* db.organizations.projects.environments
            .delete({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this environment",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when VIEWER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, projectViewer } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "production", slug: "production" },
          });

          const result = yield* db.organizations.projects.environments
            .delete({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect("returns `NotFoundError` when environment doesn't exist", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments
          .delete({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect(
      "returns `NotFoundError` when non-member tries to delete (hides project)",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, nonMember } = yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.environments.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "production", slug: "production" },
          });

          const result = yield* db.organizations.projects.environments
            .delete({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              environmentId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            environmentId: "env-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete environment");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // projectMemberships.getRole -> organizationMemberships.findById authorization
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> organizationMemberships.findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "owner-id",
                createdAt: new Date(),
              },
            ])
            // projectMemberships.getRole -> verifyProjectExists
            .select([{ id: "project-id" }])
            // projectMemberships.getRole -> getMembership (returns empty, so uses org role)
            .select([])
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

          const result = yield* db.organizations.projects.environments
            .delete({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              environmentId: "env-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe(
            "Environment with environmentId env-id not found",
          );
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // projectMemberships.getRole -> organizationMemberships.findById authorization
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // projectMemberships.getRole -> organizationMemberships.findById actual query
              .select([
                {
                  role: "OWNER",
                  organizationId: "org-id",
                  memberId: "owner-id",
                  createdAt: new Date(),
                },
              ])
              // projectMemberships.getRole -> verifyProjectExists
              .select([{ id: "project-id" }])
              // projectMemberships.getRole -> getMembership (returns empty, so uses org role)
              .select([])
              // delete returns empty array
              .delete([])
              .build(),
          ),
        ),
    );
  });

  // ===========================================================================
  // getRole (delegation to project memberships)
  // ===========================================================================

  describe("getRole", () => {
    it.effect("delegates to projectMemberships.getRole", () =>
      Effect.gen(function* () {
        const { org, project, owner, projectDeveloper } =
          yield* TestProjectFixture;
        const db = yield* Database;

        // Owner has implicit ADMIN
        const ownerRole = yield* db.organizations.projects.environments.getRole(
          {
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
          },
        );
        expect(ownerRole).toBe("ADMIN");

        // Developer has explicit DEVELOPER role
        const devRole = yield* db.organizations.projects.environments.getRole({
          userId: projectDeveloper.id,
          organizationId: org.id,
          projectId: project.id,
        });
        expect(devRole).toBe("DEVELOPER");
      }),
    );
  });
});
