/**
 * Tests for the Effect-native Annotations service.
 */

import { Effect } from "effect";
import {
  describe,
  it,
  expect,
  TestEnvironmentFixture,
  MockDrizzleORM,
} from "@/tests/db";
import { Database } from "@/db/database";
import {
  NotFoundError,
  AlreadyExistsError,
  DatabaseError,
  PermissionDeniedError,
} from "@/errors";
import type {
  CreateAnnotationInput,
  UpdateAnnotationInput,
} from "@/db/annotations";

// =============================================================================
// Helper to create a span for testing
// =============================================================================

const createTestSpan = (
  userId: string,
  environmentId: string,
  projectId: string,
  organizationId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;

    // Create a trace and span using the Traces service
    const traceId = "0123456789abcdef0123456789abcdef";
    const spanId = "0123456789abcdef";

    const result = yield* db.organizations.projects.environments.traces.create({
      userId,
      organizationId,
      projectId,
      environmentId,
      data: {
        resourceSpans: [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test-service" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test-scope" },
                spans: [
                  {
                    traceId,
                    spanId,
                    name: "test-span",
                    kind: 1,
                    startTimeUnixNano: "1700000000000000000",
                    endTimeUnixNano: "1700000001000000000",
                    attributes: [],
                    status: {},
                  },
                ],
              },
            ],
          },
        ],
      },
    });

    expect(result.acceptedSpans).toBe(1);

    return { traceId, spanId };
  });

// =============================================================================
// Annotations Tests
// =============================================================================

describe("Annotations", () => {
  describe("create", () => {
    it.effect("creates an annotation for a span", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create a span first
        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        // Create an annotation
        const input: CreateAnnotationInput = {
          spanId,
          traceId,
          label: "positive",
          reasoning: "This span completed successfully",
          data: { score: 0.95 },
        };

        const annotation =
          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          });

        expect(annotation).toBeDefined();
        expect(annotation.spanId).toBe(spanId);
        expect(annotation.traceId).toBe(traceId);
        expect(annotation.label).toBe("positive");
        expect(annotation.reasoning).toBe("This span completed successfully");
        expect(annotation.data).toEqual({ score: 0.95 });
        expect(annotation.environmentId).toBe(environment.id);
        expect(annotation.projectId).toBe(project.id);
        expect(annotation.organizationId).toBe(org.id);
      }),
    );

    it.effect("creates an annotation with createdBy set to userId", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        const input: CreateAnnotationInput = {
          spanId,
          traceId,
          label: "negative",
        };

        const annotation =
          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          });

        expect(annotation.createdBy).toBe(owner.id);
      }),
    );

    it.effect("returns NotFoundError when span does not exist", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const input: CreateAnnotationInput = {
          spanId: "nonexistentspanid",
          traceId: "nonexistenttraceid0123456789ab",
          label: "test",
        };

        const result = yield* db.organizations.projects.environments.annotations
          .create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect((result as NotFoundError).resource).toBe("span");
      }),
    );

    // TODO: Fix stack overflow issue in Effect error handling
    it.effect.skip("returns AlreadyExistsError for duplicate annotation", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        const input: CreateAnnotationInput = {
          spanId,
          traceId,
          label: "first",
        };

        // First annotation should succeed
        yield* db.organizations.projects.environments.annotations.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: input,
        });

        // Second annotation for same span should fail
        const result = yield* db.organizations.projects.environments.annotations
          .create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect((result as AlreadyExistsError).resource).toBe("annotation");
      }),
    );

    it.effect("returns PermissionDeniedError when user lacks permission", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectViewer } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const input: CreateAnnotationInput = {
          spanId: "0123456789abcdef",
          traceId: "0123456789abcdef0123456789abcdef",
          label: "test",
        };

        const result = yield* db.organizations.projects.environments.annotations
          .create({
            userId: projectViewer.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );

    it.effect("allows ANNOTATOR role to create annotations", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, projectAnnotator } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        const input: CreateAnnotationInput = {
          spanId,
          traceId,
          label: "annotator-created",
        };

        const annotation =
          yield* db.organizations.projects.environments.annotations.create({
            userId: projectAnnotator.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: input,
          });

        expect(annotation.label).toBe("annotator-created");
        expect(annotation.createdBy).toBe(projectAnnotator.id);
      }),
    );

    // TODO: Fix stack overflow issue in Effect error handling
    it.effect.skip("returns DatabaseError on insert failure", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const input: CreateAnnotationInput = {
          spanId: "0123456789abcdef",
          traceId: "0123456789abcdef0123456789abcdef",
          label: "test",
        };

        // Mock select to return a valid span, but insert to fail
        const result = yield* db.organizations.projects.environments.annotations
          .create({
            userId: "00000000-0000-0000-0000-000000000000",
            organizationId: "00000000-0000-0000-0000-000000000003",
            projectId: "00000000-0000-0000-0000-000000000002",
            environmentId: "00000000-0000-0000-0000-000000000001",
            data: input,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([
              {
                id: "span-id",
                traceDbId: "trace-id",
                spanId: "0123456789abcdef",
                traceId: "0123456789abcdef0123456789abcdef",
              },
            ])
            .insert(new Error("Insert failed"))
            .build(),
        ),
      ),
    );
  });

  describe("getById", () => {
    it.effect("returns annotation by ID", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        const created =
          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { spanId, traceId, label: "test" },
          });

        const found =
          yield* db.organizations.projects.environments.annotations.getById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: created.id,
          });

        expect(found.id).toBe(created.id);
        expect(found.label).toBe("test");
      }),
    );

    it.effect("returns NotFoundError when annotation does not exist", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.annotations
          .getById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect((result as NotFoundError).resource).toBe("annotation");
      }),
    );

    it.effect("returns PermissionDeniedError when user lacks permission", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const db = yield* Database;

        // User with no access
        const result = yield* db.organizations.projects.environments.annotations
          .getById({
            userId: "00000000-0000-0000-0000-000000000099",
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError); // NotFoundError for non-members
      }),
    );

    it.effect("returns DatabaseError on query failure", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.annotations
          .getById({
            userId: "00000000-0000-0000-0000-000000000000",
            organizationId: "00000000-0000-0000-0000-000000000003",
            projectId: "00000000-0000-0000-0000-000000000002",
            environmentId: "00000000-0000-0000-0000-000000000001",
            annotationId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Query failed")).build(),
        ),
      ),
    );
  });

  describe("update", () => {
    it.effect("updates annotation label", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        const created =
          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { spanId, traceId, label: "original" },
          });

        const updateData: UpdateAnnotationInput = { label: "updated" };
        const updated =
          yield* db.organizations.projects.environments.annotations.update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: created.id,
            data: updateData,
          });

        expect(updated.label).toBe("updated");
        expect(updated.id).toBe(created.id);
      }),
    );

    it.effect("updates annotation reasoning", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        const created =
          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { spanId, traceId, reasoning: "original reasoning" },
          });

        const updated =
          yield* db.organizations.projects.environments.annotations.update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: created.id,
            data: { reasoning: "updated reasoning" },
          });

        expect(updated.reasoning).toBe("updated reasoning");
      }),
    );

    it.effect("updates annotation data", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        const created =
          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { spanId, traceId, data: { key: "original" } },
          });

        const updated =
          yield* db.organizations.projects.environments.annotations.update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: created.id,
            data: { data: { key: "updated", extra: true } },
          });

        expect(updated.data).toEqual({ key: "updated", extra: true });
      }),
    );

    it.effect("returns NotFoundError when annotation does not exist", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.annotations
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: "00000000-0000-0000-0000-000000000000",
            data: { label: "test" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns PermissionDeniedError when user lacks permission", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectViewer } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.annotations
          .update({
            userId: projectViewer.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: "00000000-0000-0000-0000-000000000000",
            data: { label: "test" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );

    it.effect("allows ANNOTATOR role to update annotations", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, projectAnnotator } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        // Owner creates the annotation
        const created =
          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { spanId, traceId, label: "original" },
          });

        // Annotator updates it
        const updated =
          yield* db.organizations.projects.environments.annotations.update({
            userId: projectAnnotator.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: created.id,
            data: { label: "annotator-updated" },
          });

        expect(updated.label).toBe("annotator-updated");
      }),
    );

    it.effect("returns DatabaseError on update failure", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.annotations
          .update({
            userId: "00000000-0000-0000-0000-000000000000",
            organizationId: "00000000-0000-0000-0000-000000000003",
            projectId: "00000000-0000-0000-0000-000000000002",
            environmentId: "00000000-0000-0000-0000-000000000001",
            annotationId: "00000000-0000-0000-0000-000000000000",
            data: { label: "test" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().update(new Error("Update failed")).build(),
        ),
      ),
    );
  });

  describe("delete", () => {
    it.effect("deletes an annotation", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        const created =
          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { spanId, traceId, label: "to-delete" },
          });

        // Delete should succeed
        yield* db.organizations.projects.environments.annotations.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          annotationId: created.id,
        });

        // Should not be findable anymore
        const result = yield* db.organizations.projects.environments.annotations
          .getById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns NotFoundError when annotation does not exist", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.annotations
          .delete({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns PermissionDeniedError for DEVELOPER role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectDeveloper } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Developer cannot delete (only ADMIN can)
        const result = yield* db.organizations.projects.environments.annotations
          .delete({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );

    it.effect("returns PermissionDeniedError for ANNOTATOR role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectAnnotator } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Annotator cannot delete (only ADMIN can)
        const result = yield* db.organizations.projects.environments.annotations
          .delete({
            userId: projectAnnotator.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            annotationId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );

    it.effect("returns DatabaseError on delete failure", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.annotations
          .delete({
            userId: "00000000-0000-0000-0000-000000000000",
            organizationId: "00000000-0000-0000-0000-000000000003",
            projectId: "00000000-0000-0000-0000-000000000002",
            environmentId: "00000000-0000-0000-0000-000000000001",
            annotationId: "00000000-0000-0000-0000-000000000000",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().delete(new Error("Delete failed")).build(),
        ),
      ),
    );
  });

  describe("list", () => {
    it.effect("lists all annotations in environment", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        // Create two annotations for two different spans
        yield* db.organizations.projects.environments.annotations.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { spanId, traceId, label: "first" },
        });

        // Create another span for second annotation
        const result2 =
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: {
              resourceSpans: [
                {
                  resource: { attributes: [] },
                  scopeSpans: [
                    {
                      scope: { name: "test-scope" },
                      spans: [
                        {
                          traceId,
                          spanId: "abcdef0123456789",
                          name: "test-span-2",
                          kind: 1,
                          startTimeUnixNano: "1700000002000000000",
                          endTimeUnixNano: "1700000003000000000",
                          attributes: [],
                          status: {},
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          });
        expect(result2.acceptedSpans).toBe(1);

        yield* db.organizations.projects.environments.annotations.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { spanId: "abcdef0123456789", traceId, label: "second" },
        });

        const listResult =
          yield* db.organizations.projects.environments.annotations.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(listResult.total).toBe(2);
        expect(listResult.annotations.length).toBe(2);
      }),
    );

    it.effect("returns empty list when no annotations", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result =
          yield* db.organizations.projects.environments.annotations.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          });

        expect(result.total).toBe(0);
        expect(result.annotations).toEqual([]);
      }),
    );

    it.effect("filters by traceId", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        yield* db.organizations.projects.environments.annotations.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { spanId, traceId, label: "matching" },
        });

        const result =
          yield* db.organizations.projects.environments.annotations.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { traceId },
          });

        expect(result.total).toBe(1);
        expect(result.annotations[0].label).toBe("matching");
      }),
    );

    it.effect("filters by spanId", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        yield* db.organizations.projects.environments.annotations.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { spanId, traceId, label: "matching" },
        });

        const result =
          yield* db.organizations.projects.environments.annotations.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { spanId },
          });

        expect(result.total).toBe(1);
        expect(result.annotations[0].spanId).toBe(spanId);
      }),
    );

    it.effect("filters by label", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const { traceId, spanId } = yield* createTestSpan(
          owner.id,
          environment.id,
          project.id,
          org.id,
        );

        yield* db.organizations.projects.environments.annotations.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { spanId, traceId, label: "positive" },
        });

        const positiveResult =
          yield* db.organizations.projects.environments.annotations.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { label: "positive" },
          });
        expect(positiveResult.total).toBe(1);

        const negativeResult =
          yield* db.organizations.projects.environments.annotations.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { label: "negative" },
          });
        expect(negativeResult.total).toBe(0);
      }),
    );

    it.effect("paginates with limit", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create 3 spans with annotations
        const traceId = "0123456789abcdef0123456789abcdef";
        const spanIds = [
          "span000000000001",
          "span000000000002",
          "span000000000003",
        ];

        for (const spanId of spanIds) {
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: {
              resourceSpans: [
                {
                  resource: { attributes: [] },
                  scopeSpans: [
                    {
                      scope: { name: "test-scope" },
                      spans: [
                        {
                          traceId,
                          spanId,
                          name: `span-${spanId}`,
                          kind: 1,
                          startTimeUnixNano: "1700000000000000000",
                          endTimeUnixNano: "1700000001000000000",
                          attributes: [],
                          status: {},
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          });

          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { spanId, traceId, label: `label-${spanId}` },
          });
        }

        const result =
          yield* db.organizations.projects.environments.annotations.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { limit: 2 },
          });

        expect(result.total).toBe(3);
        expect(result.annotations.length).toBe(2);
      }),
    );

    it.effect("paginates with offset", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // Create 3 spans with annotations
        const traceId = "0123456789abcdef0123456789abcdef";
        const spanIds = [
          "span000000000001",
          "span000000000002",
          "span000000000003",
        ];

        for (const spanId of spanIds) {
          yield* db.organizations.projects.environments.traces.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: {
              resourceSpans: [
                {
                  resource: { attributes: [] },
                  scopeSpans: [
                    {
                      scope: { name: "test-scope" },
                      spans: [
                        {
                          traceId,
                          spanId,
                          name: `span-${spanId}`,
                          kind: 1,
                          startTimeUnixNano: "1700000000000000000",
                          endTimeUnixNano: "1700000001000000000",
                          attributes: [],
                          status: {},
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          });

          yield* db.organizations.projects.environments.annotations.create({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { spanId, traceId, label: `label-${spanId}` },
          });
        }

        const result =
          yield* db.organizations.projects.environments.annotations.list({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            filters: { limit: 10, offset: 2 },
          });

        expect(result.total).toBe(3);
        expect(result.annotations.length).toBe(1);
      }),
    );

    it.effect("returns PermissionDeniedError when user lacks permission", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const db = yield* Database;

        // User with no access
        const result = yield* db.organizations.projects.environments.annotations
          .list({
            userId: "00000000-0000-0000-0000-000000000099",
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError); // NotFoundError for non-members
      }),
    );

    it.effect("returns DatabaseError on query failure", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.projects.environments.annotations
          .list({
            userId: "00000000-0000-0000-0000-000000000000",
            organizationId: "00000000-0000-0000-0000-000000000003",
            projectId: "00000000-0000-0000-0000-000000000002",
            environmentId: "00000000-0000-0000-0000-000000000001",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Query failed")).build(),
        ),
      ),
    );
  });
});
