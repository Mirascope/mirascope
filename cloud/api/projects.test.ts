import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";
import { TestClient } from "@/tests/api";
import { TestDatabase, TestOrganizationFixture } from "@/tests/db";

describe("Projects API", () => {
  it.effect("GET /organizations/:organizationId/projects - list projects", () =>
    Effect.gen(function* () {
      const { owner, org } = yield* TestOrganizationFixture;
      const client = yield* TestClient.authenticate(owner);

      // Initially should return empty array
      const projects = yield* client.projects.list({
        path: { organizationId: org.id },
      });
      expect(Array.isArray(projects)).toBe(true);
      expect(projects).toHaveLength(0);
    }).pipe(Effect.provide(TestDatabase)),
  );

  it.effect(
    "POST /organizations/:organizationId/projects - create project",
    () =>
      Effect.gen(function* () {
        const { owner, org } = yield* TestOrganizationFixture;
        const client = yield* TestClient.authenticate(owner);

        const project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Org Project" },
        });

        expect(project.name).toBe("Org Project");
        expect(project.organizationId).toBe(org.id);
        expect(project.createdByUserId).toBeDefined();
        expect(project.id).toBeDefined();
      }).pipe(Effect.provide(TestDatabase)),
  );

  it.effect(
    "GET /organizations/:organizationId/projects/:projectId - get project",
    () =>
      Effect.gen(function* () {
        const { owner, org } = yield* TestOrganizationFixture;
        const client = yield* TestClient.authenticate(owner);

        const created = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Get Test Project" },
        });

        const project = yield* client.projects.get({
          path: { organizationId: org.id, projectId: created.id },
        });

        expect(project.id).toBe(created.id);
        expect(project.name).toBe("Get Test Project");
        expect(project.organizationId).toBe(org.id);
      }).pipe(Effect.provide(TestDatabase)),
  );

  it.effect(
    "PUT /organizations/:organizationId/projects/:projectId - update project",
    () =>
      Effect.gen(function* () {
        const { owner, org } = yield* TestOrganizationFixture;
        const client = yield* TestClient.authenticate(owner);

        const created = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Original Project Name" },
        });

        const updated = yield* client.projects.update({
          path: { organizationId: org.id, projectId: created.id },
          payload: { name: "Updated Project Name" },
        });

        expect(updated.id).toBe(created.id);
        expect(updated.name).toBe("Updated Project Name");
        expect(updated.organizationId).toBe(org.id);
      }).pipe(Effect.provide(TestDatabase)),
  );

  it.effect(
    "DELETE /organizations/:organizationId/projects/:projectId - delete project",
    () =>
      Effect.gen(function* () {
        const { owner, org } = yield* TestOrganizationFixture;
        const client = yield* TestClient.authenticate(owner);

        const created = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Delete Test Project" },
        });

        yield* client.projects.delete({
          path: { organizationId: org.id, projectId: created.id },
        });

        // Verify it's gone by listing and checking it's not there
        const projects = yield* client.projects.list({
          path: { organizationId: org.id },
        });
        const found = projects.find((p) => p.id === created.id);
        expect(found).toBeUndefined();
      }).pipe(Effect.provide(TestDatabase)),
  );
});
