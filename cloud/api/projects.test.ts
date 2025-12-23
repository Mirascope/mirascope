import { Effect } from "effect";
import { describe, expect, TestApiContext } from "@/tests/api";
import type { PublicProject } from "@/db/schema";

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
          payload: { name: "Test Project" },
        });

        expect(project.name).toBe("Test Project");
        expect(project.organizationId).toBe(org.id);
        expect(project.createdByUserId).toBeDefined();
        expect(project.id).toBeDefined();
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
