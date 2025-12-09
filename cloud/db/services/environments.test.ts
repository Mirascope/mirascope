import { describe, it, expect } from "@effect/vitest";
import {
  MockDatabase,
  TestDatabase,
  TestProjectFixture,
  TestEnvironmentFixture,
} from "@/tests/db";
import { Effect } from "effect";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { DatabaseService } from "@/db/services";

describe("EnvironmentService", () => {
  describe("create", () => {
    it.effect("creates an environment in a project", () =>
      Effect.gen(function* () {
        const { project, owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const name = "staging";
        const environment = yield* db.environments.create({
          data: { name, projectId: project.id },
          userId: owner.id,
        });

        expect(environment).toBeDefined();
        expect(environment.id).toBeDefined();
        expect(environment.name).toBe(name);
        expect(environment.projectId).toBe(project.id);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows same environment name in different projects", () =>
      Effect.gen(function* () {
        const { environment, org, owner } = yield* TestEnvironmentFixture;
        const db = yield* DatabaseService;

        const project2 = yield* db.projects.create({
          data: { name: "Project 2", organizationId: org.id },
          userId: owner.id,
        });

        const env2 = yield* db.environments.create({
          data: { name: environment.name, projectId: project2.id },
          userId: owner.id,
        });

        expect(env2.name).toBe(environment.name);
        expect(env2.id).not.toBe(environment.id);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when project lookup fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // projectService.getRole -> baseService.findById: fails
          .select(new Error("Database connection error"))
          .build();

        const result = yield* db.environments
          .create({
            data: { name: "staging", projectId: "project-id" },
            userId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find project");
      }),
    );

    it.effect("returns `NotFoundError` when project does not exist", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // projectService.getRole -> baseService.findById: project not found
          .select([])
          .build();

        const result = yield* db.environments
          .create({
            data: { name: "staging", projectId: "nonexistent-project" },
            userId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "project with id nonexistent-project not found",
        );
      }),
    );

    it.effect("returns `DatabaseError` when membership lookup fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // projectService.getRole -> projectBaseService.findById: project found
          .select([
            { id: "project-id", name: "Test", organizationId: "org-id" },
          ])
          // organizationService.getRole: fails
          .select(new Error("Database connection error"))
          .build();

        const result = yield* db.environments
          .create({
            data: { name: "staging", projectId: "project-id" },
            userId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { project, nonMember } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.environments
          .create({
            data: { name: "staging", projectId: project.id },
            userId: nonMember.id,
          })
          .pipe(Effect.flip);

        // getRole returns NotFoundError with "Organization not found" to hide org existence
        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when user has insufficient role",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // projectService.getRole -> projectBaseService.findById: project found
            .select([
              { id: "project-id", name: "Test", organizationId: "org-id" },
            ])
            // organizationService.getRole: ANNOTATOR role (too low for create)
            .select([{ role: "ANNOTATOR" }])
            .build();

          const result = yield* db.environments
            .create({
              data: { name: "staging", projectId: "project-id" },
              userId: "user-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to create this environment",
          );
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when environment name is taken",
      () =>
        Effect.gen(function* () {
          const { environment, project, owner } = yield* TestEnvironmentFixture;
          const db = yield* DatabaseService;

          const result = yield* db.environments
            .create({
              data: { name: environment.name, projectId: project.id },
              userId: owner.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            `An environment with name "${environment.name}" already exists in this project`,
          );
        }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // projectService.getRole -> projectBaseService.findById: project found
          .select([
            { id: "project-id", name: "Test", organizationId: "org-id" },
          ])
          // organizationService.getRole: pass
          .select([{ role: "OWNER" }])
          // insert: fails
          .insert(new Error("Insert failed"))
          .build();

        const result = yield* db.environments
          .create({
            data: { name: "staging", projectId: "project-id" },
            userId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create environment");
      }),
    );
  });

  describe("findAll", () => {
    it.effect("retrieves all environments for a user across projects", () =>
      Effect.gen(function* () {
        const { environment, org, owner } = yield* TestEnvironmentFixture;
        const db = yield* DatabaseService;

        const project2 = yield* db.projects.create({
          data: { name: "Project 2", organizationId: org.id },
          userId: owner.id,
        });
        const env2 = yield* db.environments.create({
          data: { name: "production", projectId: project2.id },
          userId: owner.id,
        });

        const environments = yield* db.environments.findAll({
          userId: owner.id,
        });

        expect(environments.length).toBeGreaterThanOrEqual(2);
        expect(
          environments.find((e) => e.name === environment.name),
        ).toBeDefined();
        expect(environments.find((e) => e.name === env2.name)).toBeDefined();
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns empty array when user has no environments", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        // Delete all environments in the project first (there may be auto-created ones)
        const envs = yield* db.environments.findAll({ userId: owner.id });
        for (const env of envs) {
          yield* db.environments.delete({ id: env.id, userId: owner.id });
        }

        const environments = yield* db.environments.findAll({
          userId: owner.id,
        });

        expect(environments).toHaveLength(0);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // findAll: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.environments
          .findAll({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get user environments");
      }),
    );
  });

  describe("findById", () => {
    it.effect("retrieves environment when user is a member", () =>
      Effect.gen(function* () {
        const { environment, owner } = yield* TestEnvironmentFixture;
        const db = yield* DatabaseService;

        const result = yield* db.environments.findById({
          id: environment.id,
          userId: owner.id,
        });

        expect(result).toBeDefined();
        expect(result.id).toBe(environment.id);
        expect(result.name).toBe(environment.name);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when findById fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // baseService.findById: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.environments
          .findById({ id: "env-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find environment");
      }),
    );

    it.effect("returns `NotFoundError` when environment not found", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // baseService.findById: not found
          .select([])
          .build();

        const result = yield* db.environments
          .findById({ id: "nonexistent-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "environment with id nonexistent-id not found",
        );
      }),
    );

    it.effect("returns `DatabaseError` when project lookup fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // environmentBaseService.findById: found
          .select([{ id: "env-id", name: "staging", projectId: "project-id" }])
          // getRole -> environmentBaseService.findById: found
          .select([{ id: "env-id", name: "staging", projectId: "project-id" }])
          // projectService.getRole -> projectBaseService.findById: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.environments
          .findById({ id: "env-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find project");
      }),
    );

    it.effect("returns `DatabaseError` when membership lookup fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // environmentBaseService.findById: found
          .select([{ id: "env-id", name: "staging", projectId: "project-id" }])
          // getRole -> environmentBaseService.findById: found
          .select([{ id: "env-id", name: "staging", projectId: "project-id" }])
          // projectService.getRole -> projectBaseService.findById: found
          .select([
            { id: "project-id", name: "Test", organizationId: "org-id" },
          ])
          // organizationService.getRole: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.environments
          .findById({ id: "env-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { environment, nonMember } = yield* TestEnvironmentFixture;
        const db = yield* DatabaseService;

        const result = yield* db.environments
          .findById({ id: environment.id, userId: nonMember.id })
          .pipe(Effect.flip);

        // getRole returns NotFoundError with "Organization not found" to hide org existence
        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("allows read with ANNOTATOR role", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // findById -> environmentBaseService.findById: found
          .select([{ id: "env-id", name: "staging", projectId: "project-id" }])
          // getRole -> environmentBaseService.findById: found
          .select([{ id: "env-id", name: "staging", projectId: "project-id" }])
          // projectService.getRole -> projectBaseService.findById: found
          .select([
            { id: "project-id", name: "Test", organizationId: "org-id" },
          ])
          // organizationService.getRole: ANNOTATOR can read
          .select([{ role: "ANNOTATOR" }])
          .build();

        const result = yield* db.environments.findById({
          id: "env-id",
          userId: "user-id",
        });

        expect(result).toBeDefined();
        expect(result.id).toBe("env-id");
      }),
    );
  });

  describe("update", () => {
    it.effect("updates an environment", () =>
      Effect.gen(function* () {
        const { environment, owner } = yield* TestEnvironmentFixture;
        const db = yield* DatabaseService;

        const updated = yield* db.environments.update({
          id: environment.id,
          data: { name: "Updated Name" },
          userId: owner.id,
        });

        expect(updated.name).toBe("Updated Name");
        expect(updated.id).toBe(environment.id);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when environment not found", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.environments
          .update({
            id: badId,
            data: { name: "New Name" },
            userId: owner.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(`environment with id ${badId} not found`);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { environment, nonMember } = yield* TestEnvironmentFixture;
        const db = yield* DatabaseService;

        const result = yield* db.environments
          .update({
            id: environment.id,
            data: { name: "New Name" },
            userId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when user has insufficient role",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // getRole -> environmentBaseService.findById: found
            .select([
              { id: "env-id", name: "staging", projectId: "project-id" },
            ])
            // projectService.getRole -> projectBaseService.findById: found
            .select([
              { id: "project-id", name: "Test", organizationId: "org-id" },
            ])
            // organizationService.getRole: ANNOTATOR role (too low for update)
            .select([{ role: "ANNOTATOR" }])
            .build();

          const result = yield* db.environments
            .update({
              id: "env-id",
              data: { name: "New Name" },
              userId: "user-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this environment",
          );
        }),
    );

    it.effect("returns `DatabaseError` when update operation fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole -> environmentBaseService.findById: found
          .select([{ id: "env-id", name: "staging", projectId: "project-id" }])
          // projectService.getRole -> projectBaseService.findById: found
          .select([
            { id: "project-id", name: "Test", organizationId: "org-id" },
          ])
          // organizationService.getRole: pass
          .select([{ role: "OWNER" }])
          // baseService.update: fails
          .update(new Error("Update failed"))
          .build();

        const result = yield* db.environments
          .update({
            id: "env-id",
            data: { name: "New Name" },
            userId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update environment");
      }),
    );
  });

  describe("delete", () => {
    it.effect("deletes an environment", () =>
      Effect.gen(function* () {
        const { environment, owner } = yield* TestEnvironmentFixture;
        const db = yield* DatabaseService;

        yield* db.environments.delete({ id: environment.id, userId: owner.id });

        // Verify it's gone
        const result = yield* db.environments
          .findById({ id: environment.id, userId: owner.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when findById fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // baseService.findById: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.environments
          .delete({ id: "env-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find environment");
      }),
    );

    it.effect("returns `NotFoundError` when environment does not exist", () =>
      Effect.gen(function* () {
        const { owner } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const badId = "00000000-0000-0000-0000-000000000000";
        const result = yield* db.environments
          .delete({ id: badId, userId: owner.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(`environment with id ${badId} not found`);
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when membership lookup fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole -> environmentBaseService.findById: found
          .select([{ id: "env-id", name: "staging", projectId: "project-id" }])
          // projectService.getRole -> projectBaseService.findById: found
          .select([
            { id: "project-id", name: "Test", organizationId: "org-id" },
          ])
          // organizationService.getRole: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.environments
          .delete({ id: "env-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { environment, nonMember } = yield* TestEnvironmentFixture;
        const db = yield* DatabaseService;

        const result = yield* db.environments
          .delete({ id: environment.id, userId: nonMember.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect(
      "returns `PermissionDeniedError` when user has insufficient role",
      () =>
        Effect.gen(function* () {
          const db = new MockDatabase()
            // getRole -> environmentBaseService.findById: found
            .select([
              { id: "env-id", name: "staging", projectId: "project-id" },
            ])
            // projectService.getRole -> projectBaseService.findById: found
            .select([
              { id: "project-id", name: "Test", organizationId: "org-id" },
            ])
            // organizationService.getRole: DEVELOPER role (too low for delete)
            .select([{ role: "DEVELOPER" }])
            .build();

          const result = yield* db.environments
            .delete({ id: "env-id", userId: "user-id" })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this environment",
          );
        }),
    );

    it.effect("returns `DatabaseError` when delete operation fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // getRole -> environmentBaseService.findById: found
          .select([{ id: "env-id", name: "staging", projectId: "project-id" }])
          // projectService.getRole -> projectBaseService.findById: found
          .select([
            { id: "project-id", name: "Test", organizationId: "org-id" },
          ])
          // organizationService.getRole: pass
          .select([{ role: "OWNER" }])
          // baseService.delete: fails
          .delete(new Error("Delete failed"))
          .build();

        const result = yield* db.environments
          .delete({ id: "env-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete environment");
      }),
    );
  });

  describe("findByProject", () => {
    it.effect("retrieves all environments in a project", () =>
      Effect.gen(function* () {
        const { environment, project, owner } = yield* TestEnvironmentFixture;
        const db = yield* DatabaseService;

        const env2 = yield* db.environments.create({
          data: { name: "production", projectId: project.id },
          userId: owner.id,
        });

        const environments = yield* db.environments.findByProject({
          projectId: project.id,
          userId: owner.id,
        });

        expect(environments).toHaveLength(2);
        expect(
          environments.find((e) => e.name === environment.name),
        ).toBeDefined();
        expect(environments.find((e) => e.name === env2.name)).toBeDefined();
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when project lookup fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // projectService.getRole -> baseService.findById: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.environments
          .findByProject({ projectId: "project-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find project");
      }),
    );

    it.effect("returns `NotFoundError` when project not found", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // projectService.getRole -> baseService.findById: project not found
          .select([])
          .build();

        const result = yield* db.environments
          .findByProject({ projectId: "nonexistent", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("project with id nonexistent not found");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { project, nonMember } = yield* TestProjectFixture;
        const db = yield* DatabaseService;

        const result = yield* db.environments
          .findByProject({ projectId: project.id, userId: nonMember.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }).pipe(Effect.provide(TestDatabase)),
    );

    it.effect("returns `DatabaseError` when fetching environments fails", () =>
      Effect.gen(function* () {
        const db = new MockDatabase()
          // projectService.getRole -> projectBaseService.findById: project found
          .select([
            { id: "project-id", name: "Test", organizationId: "org-id" },
          ])
          // organizationService.getRole: pass
          .select([{ role: "OWNER" }])
          // findByProject query: fails
          .select(new Error("Database connection failed"))
          .build();

        const result = yield* db.environments
          .findByProject({ projectId: "project-id", userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get project environments");
      }),
    );
  });
});
