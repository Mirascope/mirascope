import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import { withTestClientDb } from "@/tests/api";

describe("Projects API", () => {
  it(
    "GET /projects - list projects",
    withTestClientDb(async (client) => {
      // Initially should return empty array
      const projects = await Effect.runPromise(client.projects.list());
      expect(Array.isArray(projects)).toBe(true);
    }),
  );

  it(
    "POST /projects - create user-owned project",
    withTestClientDb(async (client, { user }) => {
      const project = await Effect.runPromise(
        client.projects.create({
          payload: { name: "My Personal Project", userOwnerId: user.id },
        }),
      );

      expect(project.name).toBe("My Personal Project");
      expect(project.userOwnerId).toBe(user.id);
      expect(project.orgOwnerId).toBeNull();
      expect(project.id).toBeDefined();
    }),
  );

  it(
    "POST /projects - create organization-owned project",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({
          payload: { name: "Test Org for Projects" },
        }),
      );

      const project = await Effect.runPromise(
        client.projects.create({
          payload: { name: "Org Project", orgOwnerId: org.id },
        }),
      );

      expect(project.name).toBe("Org Project");
      expect(project.userOwnerId).toBeNull();
      expect(project.orgOwnerId).toBe(org.id);
      expect(project.id).toBeDefined();
    }),
  );

  it(
    "GET /projects/:projectId - get project",
    withTestClientDb(async (client, { user }) => {
      const created = await Effect.runPromise(
        client.projects.create({
          payload: { name: "Get Test Project", userOwnerId: user.id },
        }),
      );

      const project = await Effect.runPromise(
        client.projects.get({
          path: { projectId: created.id },
        }),
      );

      expect(project.id).toBe(created.id);
      expect(project.name).toBe("Get Test Project");
      expect(project.userOwnerId).toBe(user.id);
    }),
  );

  it(
    "PUT /projects/:projectId - update project",
    withTestClientDb(async (client, { user }) => {
      const created = await Effect.runPromise(
        client.projects.create({
          payload: { name: "Original Project Name", userOwnerId: user.id },
        }),
      );

      const updated = await Effect.runPromise(
        client.projects.update({
          path: { projectId: created.id },
          payload: { name: "Updated Project Name" },
        }),
      );

      expect(updated.id).toBe(created.id);
      expect(updated.name).toBe("Updated Project Name");
      expect(updated.userOwnerId).toBe(user.id);
    }),
  );

  it(
    "DELETE /projects/:projectId - delete project",
    withTestClientDb(async (client, { user }) => {
      const created = await Effect.runPromise(
        client.projects.create({
          payload: { name: "Delete Test Project", userOwnerId: user.id },
        }),
      );

      await Effect.runPromise(
        client.projects.delete({
          path: { projectId: created.id },
        }),
      );

      // Verify it's gone by listing and checking it's not there
      const projects = await Effect.runPromise(client.projects.list());
      const found = projects.find((p) => p.id === created.id);
      expect(found).toBeUndefined();
    }),
  );

  it(
    "GET /projects - lists all user's projects",
    withTestClientDb(async (client, { user }) => {
      // Create a user-owned project
      const userProject = await Effect.runPromise(
        client.projects.create({
          payload: { name: "User Project", userOwnerId: user.id },
        }),
      );

      // Create an org and an org-owned project
      const org = await Effect.runPromise(
        client.organizations.create({
          payload: { name: "Test Org" },
        }),
      );

      const orgProject = await Effect.runPromise(
        client.projects.create({
          payload: { name: "Org Project", orgOwnerId: org.id },
        }),
      );

      // List should include both projects
      const projects = await Effect.runPromise(client.projects.list());

      expect(projects).toHaveLength(2);
      expect(projects.find((p) => p.id === userProject.id)).toBeDefined();
      expect(projects.find((p) => p.id === orgProject.id)).toBeDefined();
    }),
  );
});
