import { Effect, Schema } from "effect";
import { ParseError } from "effect/ParseResult";

import type { PublicProject } from "@/db/schema";

import { CreateProjectRequestSchema } from "@/api/projects.schemas";
import { describe, it, expect, TestApiContext } from "@/tests/api";

describe("CreateProjectRequestSchema validation", () => {
  it("rejects empty name", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreateProjectRequestSchema)({
        name: "",
        slug: "test-project",
      }),
    ).toThrow("Project name is required");
  });

  it("rejects name > 100 chars", () => {
    const longName = "a".repeat(101);
    expect(() =>
      Schema.decodeUnknownSync(CreateProjectRequestSchema)({
        name: longName,
        slug: "test-project",
      }),
    ).toThrow("Project name must be at most 100 characters");
  });

  it("accepts valid name", () => {
    const result = Schema.decodeUnknownSync(CreateProjectRequestSchema)({
      name: "Valid Project Name",
      slug: "valid-project",
    });
    expect(result.name).toBe("Valid Project Name");
  });
});

describe.sequential("Projects API", (it) => {
  let project: PublicProject;

  it.effect(
    "GET /organizations/:organizationId/projects - list projects (initially empty)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const projects = yield* client.projects.list({
          path: { organizationId: org.id },
        });
        expect(Array.isArray(projects)).toBe(true);
        // Initially should be empty (no projects created yet)
        expect(projects).toHaveLength(0);
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects - create project",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Test Project", slug: "test-project" },
        });

        expect(project.name).toBe("Test Project");
        expect(project.organizationId).toBe(org.id);
        expect(project.createdByUserId).toBeDefined();
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects - rejects invalid slug pattern",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.projects
          .create({
            path: { organizationId: org.id },
            payload: { name: "Test Project", slug: "Invalid Slug!" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(ParseError);
        expect(result.message).toContain(
          "Project slug must start and end with a letter or number, and only contain lowercase letters, numbers, hyphens, and underscores",
        );
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects - rejects empty name",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.projects
          .create({
            path: { organizationId: org.id },
            payload: { name: "", slug: "test-project" },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("ParseError");
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects - rejects name > 100 chars",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const longName = "a".repeat(101);
        const result = yield* client.projects
          .create({
            path: { organizationId: org.id },
            payload: { name: longName, slug: "test-project" },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("ParseError");
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/projects - list projects (after create)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const projects = yield* client.projects.list({
          path: { organizationId: org.id },
        });
        expect(projects).toHaveLength(1);
        expect(projects[0].id).toBe(project.id);
        expect(projects[0].name).toBe("Test Project");
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/projects/:projectId - get project",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const fetched = yield* client.projects.get({
          path: { organizationId: org.id, projectId: project.id },
        });

        expect(fetched.id).toBe(project.id);
        expect(fetched.name).toBe("Test Project");
        expect(fetched.organizationId).toBe(org.id);
      }),
  );

  it.effect(
    "PUT /organizations/:organizationId/projects/:projectId - update project",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const updated = yield* client.projects.update({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "Updated Project Name" },
        });

        expect(updated.id).toBe(project.id);
        expect(updated.name).toBe("Updated Project Name");
        expect(updated.organizationId).toBe(org.id);
      }),
  );

  it.effect(
    "DELETE /organizations/:organizationId/projects/:projectId - delete project",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client.projects.delete({
          path: { organizationId: org.id, projectId: project.id },
        });

        // Verify it's gone by listing and checking it's not there
        const projects = yield* client.projects.list({
          path: { organizationId: org.id },
        });
        const found = projects.find((p) => p.id === project.id);
        expect(found).toBeUndefined();
      }),
  );
});
