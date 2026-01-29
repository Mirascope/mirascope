import { Effect } from "effect";

import type { PublicTag } from "@/db/schema";

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
  TestProjectFixture,
} from "@/tests/db";

describe("Tags", () => {
  // ==========================================================================
  // create
  // ==========================================================================

  describe("create", () => {
    it.effect("creates a tag (org OWNER)", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const tag = yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });

        expect(tag).toMatchObject({
          name: "Bug",
          projectId: project.id,
          organizationId: org.id,
          createdBy: owner.id,
        } satisfies Partial<PublicTag>);
        expect(tag.id).toBeDefined();
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project DEVELOPER tries to create",
      () =>
        Effect.gen(function* () {
          const { org, project, projectDeveloper } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.tags
            .create({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              data: { name: "Feature" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project ANNOTATOR tries to create",
      () =>
        Effect.gen(function* () {
          const { org, project, projectAnnotator } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.tags
            .create({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              data: { name: "Annotation" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project VIEWER tries to create",
      () =>
        Effect.gen(function* () {
          const { org, project, projectViewer } = yield* TestProjectFixture;
          const db = yield* Database;

          const result = yield* db.organizations.projects.tags
            .create({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              data: { name: "Unauthorized" },
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

          const result = yield* db.organizations.projects.tags
            .create({
              userId: nonMember.id,
              organizationId: org.id,
              projectId: project.id,
              data: { name: "Unauthorized" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when tag name is taken in same project",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.tags
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              data: { name: "Bug" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
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
              // insert fails with unique constraint
              .insert(
                Object.assign(new Error("Duplicate tag"), { code: "23505" }),
              )
              .build(),
          ),
        ),
    );

    it.effect("allows case-sensitive tag names", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const first = yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });

        const second = yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "bug" },
        });

        expect(first.name).toBe("Bug");
        expect(second.name).toBe("bug");
        expect(first.id).not.toBe(second.id);
      }),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.tags
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            data: { name: "Bug" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create tag");
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
            // insert fails
            .insert(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ==========================================================================
  // findAll
  // ==========================================================================

  describe("findAll", () => {
    it.effect("retrieves all tags in a project", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });
        yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Feature" },
        });

        const tags = yield* db.organizations.projects.tags.findAll({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
        });

        expect(tags).toHaveLength(2);
        expect(tags.map((tag) => tag.name).sort()).toEqual(["Bug", "Feature"]);
      }),
    );

    it.effect("allows project VIEWER to list tags", () =>
      Effect.gen(function* () {
        const { org, project, owner, projectViewer } =
          yield* TestProjectFixture;
        const db = yield* Database;

        yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });

        const tags = yield* db.organizations.projects.tags.findAll({
          userId: projectViewer.id,
          organizationId: org.id,
          projectId: project.id,
        });

        expect(tags).toHaveLength(1);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.tags
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to list tags");
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
            // findAll query fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ==========================================================================
  // findById
  // ==========================================================================

  describe("findById", () => {
    it.effect("retrieves a tag by ID", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });

        const tag = yield* db.organizations.projects.tags.findById({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          tagId: created.id,
        });

        expect(tag.id).toBe(created.id);
        expect(tag.name).toBe("Bug");
      }),
    );

    it.effect("returns `NotFoundError` when tag does not exist", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.tags
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            tagId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "Tag with id 00000000-0000-0000-0000-000000000000 not found",
        );
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.tags
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            tagId: "tag-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get tag");
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
            // findById query fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });

  // ==========================================================================
  // update
  // ==========================================================================

  describe("update", () => {
    it.effect("updates a tag name", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });

        const updated = yield* db.organizations.projects.tags.update({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          tagId: created.id,
          data: { name: "Bugfix" },
        });

        expect(updated.id).toBe(created.id);
        expect(updated.name).toBe("Bugfix");
      }),
    );

    it.effect("updates a tag without changing name", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });

        const updated = yield* db.organizations.projects.tags.update({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          tagId: created.id,
          data: {},
        });

        expect(updated.id).toBe(created.id);
        expect(updated.name).toBe("Bug");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project VIEWER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, projectViewer } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.tags.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "Bug" },
          });

          const result = yield* db.organizations.projects.tags
            .update({
              userId: projectViewer.id,
              organizationId: org.id,
              projectId: project.id,
              tagId: created.id,
              data: { name: "Bugfix" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project DEVELOPER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, projectDeveloper } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.tags.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "Bug" },
          });

          const result = yield* db.organizations.projects.tags
            .update({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              tagId: created.id,
              data: { name: "Bugfix" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project ANNOTATOR tries to update",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, projectAnnotator } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.tags.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "Bug" },
          });

          const result = yield* db.organizations.projects.tags
            .update({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              tagId: created.id,
              data: { name: "Bugfix" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when name is taken in the same project",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.tags
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              tagId: "tag-id",
              data: { name: "Feature" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
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
              // update fails with unique constraint
              .update(
                Object.assign(new Error("Duplicate tag"), { code: "23505" }),
              )
              .build(),
          ),
        ),
    );

    it.effect("returns `NotFoundError` when tag does not exist", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.tags
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            tagId: "00000000-0000-0000-0000-000000000000",
            data: { name: "Missing" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns `DatabaseError` when update fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.tags
          .update({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            tagId: "tag-id",
            data: { name: "Bug" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update tag");
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
            // update fails
            .update(new Error("Update failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `AlreadyExistsError` when update fails with missing name",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.projects.tags
            .update({
              userId: "owner-id",
              organizationId: "org-id",
              projectId: "project-id",
              tagId: "tag-id",
              data: {},
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
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
              // update fails with unique constraint
              .update(
                Object.assign(new Error("Duplicate tag"), { code: "23505" }),
              )
              .build(),
          ),
        ),
    );
  });

  // ==========================================================================
  // delete
  // ==========================================================================

  describe("delete", () => {
    it.effect("deletes a tag", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const created = yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });

        yield* db.organizations.projects.tags.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          tagId: created.id,
        });

        const result = yield* db.organizations.projects.tags
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            tagId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project DEVELOPER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, projectDeveloper } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.tags.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "Bug" },
          });

          const result = yield* db.organizations.projects.tags
            .delete({
              userId: projectDeveloper.id,
              organizationId: org.id,
              projectId: project.id,
              tagId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when project ANNOTATOR tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, project, owner, projectAnnotator } =
            yield* TestProjectFixture;
          const db = yield* Database;

          const created = yield* db.organizations.projects.tags.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            data: { name: "Bug" },
          });

          const result = yield* db.organizations.projects.tags
            .delete({
              userId: projectAnnotator.id,
              organizationId: org.id,
              projectId: project.id,
              tagId: created.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect("returns `NotFoundError` when tag does not exist", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.tags
          .delete({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            tagId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.tags
          .delete({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            tagId: "tag-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete tag");
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
            // delete fails
            .delete(new Error("Delete failed"))
            .build(),
        ),
      ),
    );
  });

  // ==========================================================================
  // findByNames
  // ==========================================================================

  describe("findByNames", () => {
    it.effect("returns tags for matching names", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });
        yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Feature" },
        });

        const tags = yield* db.organizations.projects.tags.findByNames({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          names: ["Bug", "Feature"],
        });

        expect(tags).toHaveLength(2);
      }),
    );

    it.effect("returns empty list when no names provided", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        const tags = yield* db.organizations.projects.tags.findByNames({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          names: [],
        });

        expect(tags).toEqual([]);
      }),
    );

    it.effect("returns `NotFoundError` when names are missing", () =>
      Effect.gen(function* () {
        const { org, project, owner } = yield* TestProjectFixture;
        const db = yield* Database;

        yield* db.organizations.projects.tags.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          data: { name: "Bug" },
        });

        const result = yield* db.organizations.projects.tags
          .findByNames({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            names: ["Bug", "Missing"],
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toContain("Missing");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.tags
          .findByNames({
            userId: "owner-id",
            organizationId: "org-id",
            projectId: "project-id",
            names: ["Bug"],
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to validate tags");
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
            // findByNames query fails
            .select(new Error("Database connection failed"))
            .build(),
        ),
      ),
    );
  });
});
