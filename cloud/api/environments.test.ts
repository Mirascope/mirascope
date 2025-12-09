import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import { withTestClientDb } from "@/tests/api";

describe("Environments API", () => {
  it(
    "GET /organizations/:organizationId/projects/:projectId/environments - list environments",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({ payload: { name: "List Env Test Org" } }),
      );

      const project = await Effect.runPromise(
        client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Test Project" },
        }),
      );

      const environments = await Effect.runPromise(
        client.environments.list({
          path: { organizationId: org.id, projectId: project.id },
        }),
      );

      // Should have the default "development" environment
      expect(Array.isArray(environments)).toBe(true);
      expect(environments).toHaveLength(1);
      expect(environments[0].name).toBe("development");
    }),
  );

  it(
    "POST /organizations/:organizationId/projects/:projectId/environments - create environment",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({
          payload: { name: "Create Env Test Org" },
        }),
      );

      const project = await Effect.runPromise(
        client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Test Project" },
        }),
      );

      const env = await Effect.runPromise(
        client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "staging" },
        }),
      );

      expect(env.name).toBe("staging");
      expect(env.projectId).toBe(project.id);
      expect(env.id).toBeDefined();
    }),
  );

  it(
    "GET /organizations/:organizationId/projects/:projectId/environments/:environmentId - get environment",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({ payload: { name: "Get Env Test Org" } }),
      );

      const project = await Effect.runPromise(
        client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Test Project" },
        }),
      );

      const created = await Effect.runPromise(
        client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "staging" },
        }),
      );

      const env = await Effect.runPromise(
        client.environments.get({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: created.id,
          },
        }),
      );

      expect(env.id).toBe(created.id);
      expect(env.name).toBe("staging");
      expect(env.projectId).toBe(project.id);
    }),
  );

  it(
    "DELETE /organizations/:organizationId/projects/:projectId/environments/:environmentId - delete environment",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({
          payload: { name: "Delete Env Test Org" },
        }),
      );

      const project = await Effect.runPromise(
        client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Test Project" },
        }),
      );

      const created = await Effect.runPromise(
        client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "staging" },
        }),
      );

      await Effect.runPromise(
        client.environments.delete({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: created.id,
          },
        }),
      );

      // Verify it's gone by listing
      const environments = await Effect.runPromise(
        client.environments.list({
          path: { organizationId: org.id, projectId: project.id },
        }),
      );
      const found = environments.find((e) => e.id === created.id);
      expect(found).toBeUndefined();
    }),
  );
});
